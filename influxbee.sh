#!/bin/sh

echo $MIRUBEE_USER
echo $MIRUBEE_PASSWORD

source venv/bin/activate
echo $MIRUBEE_USER
echo $MIRUBEE_PASSWORD

python influxbee.py -u $MIRUBEE_USER -p ${MIRUBEE_PASSWORD} --config-file /config/mirubee.toml --influxdb_host ${INFLUXDB_HOST} --influxdb_port ${INFLUXDB_PORT} --influxdb_database ${INFLUXDB_DATABASE} --influxdb_user ${INFLUXDB_USER} --influxdb_password ${INFLUXDB_PASSWORD} --requests_per_day ${REQUESTS_PER_DAY}