ARG BUILD_FROM=ghcr.io/home-assistant/${BUILD_ARCH}-base:2025.8.0
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# Install Python for the polling script
# hadolint ignore=DL3018
RUN apk add --no-cache python3 py3-pip

# Install required Python packages
RUN pip install --no-cache-dir pymodbus paho-mqtt

# Copy run script
COPY vevor_eml3500_rs232_wifi/run.sh /run.sh
RUN chmod +x /run.sh

# Copy application files and CSV documentation
COPY vevor_eml3500_rs232_wifi /app/vevor_eml3500_rs232_wifi
COPY docs/*.csv /app/docs/
WORKDIR /app

CMD [ "/run.sh" ]
