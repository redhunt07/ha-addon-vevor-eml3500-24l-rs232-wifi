# Contributing

Hardware test reports, register-map corrections, decoder fixes and clearer setup instructions are welcome. Italian and English are both welcome.

## Before changing code

Read the [README](README.md) and [register map](docs/registers.md). Include the inverter model/firmware, bridge setup and a reproducible example in an issue. Remove credentials and device identifiers from public logs.

## Development checks

Use an isolated Python environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip install ruff
ruff check .
python -m pytest
```

The existing CI also installs `pymodbus` and `paho-mqtt`. Tests that skip without optional dependencies do not validate the full polling path. Report skipped tests and hardware limitations explicitly.

Keep runtime changes separate from documentation-only changes. For Modbus changes, include register references and test coverage for decoding, short responses and multi-word values where relevant. Only run write-command hardware tests on equipment you control, using settings appropriate for that device.

## Pull requests

Describe the trigger, before/after behavior and validation. Preserve existing copyright and licensing. Avoid unrelated formatting or generated files.

Contributions follow the existing [MIT license](LICENSE).
