"""Modbus RTU over TCP client for Vevor EML3500-24L inverter.

This module loads register definitions from a CSV file and provides
an asynchronous client using pymodbus to poll and write registers.
"""

from __future__ import annotations

import asyncio
import contextlib
import csv
from dataclasses import dataclass
from decimal import Decimal
import inspect
import logging
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.framer import FramerType

logger = logging.getLogger(__name__)


@dataclass
class RegisterDefinition:
    """Describes a single modbus register."""

    name: str
    unit: str
    data_format: str
    address: int
    count: int
    access: str
    remark: str
    scale: float = 1.0


def _parse_scale(unit: str) -> float:
    """Extract numeric scale from the unit string.

    Examples
    --------
    "0.1v" -> 0.1
    "1w" -> 1.0
    "" -> 1.0
    """

    if not unit:
        return 1.0
    numeric = ""
    for ch in unit:
        if ch.isdigit() or ch in {".", "-"}:
            numeric += ch
        else:
            break
    try:
        return float(numeric) if numeric else 1.0
    except ValueError:
        return 1.0


def load_register_definitions(csv_path: Path) -> Dict[str, RegisterDefinition]:
    """Load register definitions from a CSV file."""

    registers: Dict[str, RegisterDefinition] = {}
    with csv_path.open(newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Skip blank lines
            if not row.get("Data name"):
                continue
            name = row["Data name"].strip()
            unit = (row.get("Unit") or "").strip()
            data_format = (row.get("Data format") or "").strip()
            try:
                address = int(row.get("Start address") or 0)
            except ValueError:
                continue
            try:
                count = int(row.get("Number of registers") or 1)
            except ValueError:
                count = 1
            access = (row.get("Read/Write") or "").strip()
            remark = (row.get("Remark") or "").replace("\n", " ").strip()
            scale = _parse_scale(unit)
            registers[name] = RegisterDefinition(
                name=name,
                unit=unit,
                data_format=data_format,
                address=address,
                count=count,
                access=access,
                remark=remark,
                scale=scale,
            )
    return registers


DEFAULT_REGISTER_CSV = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "vevor_eml3500_24l_registers.csv"
)


class ModbusRTUOverTCPClient:
    """Asynchronous Modbus client with periodic polling and retry logic."""

    def __init__(
        self,
        host: str,
        port: int = 502,
        unit: int = 1,
        poll_interval: float = 5.0,
        read_timeout: float = 5.0,
        registers: Optional[Dict[str, RegisterDefinition]] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.unit = unit
        self.poll_interval = poll_interval
        self.read_timeout = read_timeout
        self.client = AsyncModbusTcpClient(host, port=port, framer=FramerType.RTU)
        params = inspect.signature(
            self.client.read_holding_registers
        ).parameters
        if "unit" in params:
            self._slave_kwarg = "unit"
        elif "slave" in params:
            self._slave_kwarg = "slave"
        else:
            self._slave_kwarg = None
        self.registers = registers or load_register_definitions(DEFAULT_REGISTER_CSV)
        self.values: Dict[str, float | str] = {}
        self._poll_task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        """Connect the underlying pymodbus client if not connected."""
        if not self.client.connected:
            result = self.client.connect()
            if asyncio.iscoroutine(result):
                await result

    async def close(self) -> None:
        """Close the underlying pymodbus client."""
        result = self.client.close()
        if asyncio.iscoroutine(result):
            await result

    async def read_register(self, name: str, retries: int = 3) -> float | str:
        """Read a register by name and return the scaled value."""
        reg = self.registers[name]
        kwargs = {self._slave_kwarg: self.unit} if self._slave_kwarg else {}
        for attempt in range(retries):
            try:
                await self.connect()
                response = await asyncio.wait_for(
                    self.client.read_holding_registers(
                        reg.address, count=reg.count, **kwargs
                    ),
                    timeout=self.read_timeout,
                )
                if response.isError():
                    raise RuntimeError(f"Read failed for {name}: {response}")

                if reg.data_format == "ULong":
                    value = (response.registers[0] << 16) + response.registers[1]
                    scaled = Decimal(value) * Decimal(str(reg.scale))
                    return float(scaled)
                if reg.data_format == "UInt":
                    value = response.registers[0]
                    scaled = Decimal(value) * Decimal(str(reg.scale))
                    return float(scaled)
                if reg.data_format == "Int":
                    raw = response.registers[0]
                    value = raw - 0x10000 if raw & 0x8000 else raw
                    scaled = Decimal(value) * Decimal(str(reg.scale))
                    return float(scaled)
                if reg.data_format in {"ASC", "ASCII"}:
                    data = b"".join(r.to_bytes(2, "big") for r in response.registers)
                    return data.decode(errors="ignore").rstrip("\x00")
                if reg.count > 1:
                    scale = Decimal(str(reg.scale))
                    return [float(Decimal(val) * scale) for val in response.registers]
                scaled = Decimal(response.registers[0]) * Decimal(str(reg.scale))
                return float(scaled)
            except asyncio.TimeoutError:
                logger.warning("Timeout reading %s, retry %d", name, attempt + 1)
                await self.close()
                await asyncio.sleep(1)
        raise RuntimeError(f"Failed to read register {name}")

    async def write_register(
        self, name: str, value: float | str, retries: int = 3
    ) -> None:
        """Write a scaled value to a register with retry and reconnect logic."""
        reg = self.registers[name]
        if "W" not in reg.access:
            raise PermissionError(f"Register {name} is not writable")
        for attempt in range(retries):
            try:
                await self.connect()
                kwargs = {self._slave_kwarg: self.unit} if self._slave_kwarg else {}
                if reg.data_format in {"ASC", "ASCII"} and isinstance(value, str):
                    data = value.encode()
                    data = data.ljust(reg.count * 2, b"\x00")[: reg.count * 2]
                    regs = [
                        int.from_bytes(data[i : i + 2], "big")
                        for i in range(0, len(data), 2)
                    ]
                    response = await self.client.write_registers(
                        reg.address, regs, **kwargs
                    )
                else:
                    raw = int(float(value) / reg.scale)
                    if reg.data_format == "ULong" or reg.count > 1:
                        hi = (raw >> 16) & 0xFFFF
                        lo = raw & 0xFFFF
                        response = await self.client.write_registers(
                            reg.address, [hi, lo], **kwargs
                        )
                    else:
                        response = await self.client.write_register(
                            reg.address, value=raw, **kwargs
                        )
                if not response.isError():
                    return
            except Exception:
                pass
            await self.close()
            await asyncio.sleep(1)
        raise RuntimeError(f"Failed to write register {name}")

    async def _poll_once(self, regs: Iterable[str]) -> None:
        for name in regs:
            try:
                self.values[name] = await self.read_register(name)
            except Exception:
                await self.close()
                raise

    async def poll_forever(
        self,
        regs: Optional[Iterable[str]] = None,
        callback: Optional[Callable[[str, float | str], None]] = None,
    ) -> None:
        """Continuously poll registers, invoking callback for new values."""
        regs = list(regs or self.registers.keys())
        while True:
            try:
                await self._poll_once(regs)
                if callback:
                    for name in regs:
                        callback(name, self.values[name])
            except Exception:
                await asyncio.sleep(1)
                continue
            await asyncio.sleep(self.poll_interval)

    def start_polling(
        self,
        regs: Optional[Iterable[str]] = None,
        callback: Optional[Callable[[str, float | str], None]] = None,
    ) -> None:
        """Start background polling task."""
        if self._poll_task is None or self._poll_task.done():
            self._poll_task = asyncio.create_task(self.poll_forever(regs, callback))

    async def stop_polling(self) -> None:
        """Stop background polling."""
        if self._poll_task:
            self._poll_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._poll_task
            self._poll_task = None
            await self.close()
