ARG BUILD_FROM=ghcr.io/home-assistant/${BUILD_ARCH}-base:2025.8.0
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# Install Python for the polling script
# hadolint ignore=DL3018
RUN apk add --no-cache python3 py3-pip

# Copy run script
COPY run.sh /run.sh
RUN chmod +x /run.sh

COPY . /app/vevor_eml3500_rs232_wifi
WORKDIR /app

CMD [ "/run.sh" ]
