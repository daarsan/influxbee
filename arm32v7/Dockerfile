FROM arm32v7/python:3.7-slim

# Define variables
ENV MIRUBEE_USER=user \
    MIRUBEE_PASSWORD=password \
    INFLUXDB_HOST=localhost \
    INFLUXDB_DATABASE=mirubee \
    INFLUXDB_PORT=8086 \
    INFLUXDB_USER=root \
    INFLUXDB_PASSWORD=root \
    REQUESTS_PER_DAY=100

# Copy in your requirements file
ADD requirements.txt /requirements.txt

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step. Correct the path to
# your production requirements file, if needed.
RUN set -ex \
    && apt-get update \
    && python3 -m venv /influxbee/venv \
    && /influxbee/venv/bin/pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/influxbee/venv/bin/pip install --no-cache-dir -r /requirements.txt"

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
COPY / /influxbee/
RUN mkdir /config && \
    chmod +x /influxbee/influxbee.sh
WORKDIR /influxbee

VOLUME /config

ENTRYPOINT ["/influxbee/influxbee.sh"]
