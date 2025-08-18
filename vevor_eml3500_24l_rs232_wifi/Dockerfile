ARG BUILD_FROM
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# Install Python for the polling script
# hadolint ignore=DL3018
RUN apk add --no-cache python3 py3-pip

# Install required Python packages
RUN pip install --no-cache-dir --break-system-packages pymodbus paho-mqtt

# Copy run script
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Copy application files and CSV documentation
COPY . /app/vevor_eml3500_24l_rs232_wifi
COPY docs/*.csv /app/docs/
WORKDIR /app

CMD [ "/run.sh" ]
