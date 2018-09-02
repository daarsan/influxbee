FROM python:3.6.4-alpine

# Define variables
ENV APP_PATH=/influxbee \
    MIRUBEE_USER=user
    MIRUBEE_PASSWORD=password

# Copy in your requirements file
ADD requirements.txt /requirements.txt

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step. Correct the path to
# your production requirements file, if needed.
RUN set -ex \
    && apk update \
    && python3 -m venv $APP_PATH/venv \
    && $APP_PATH/venv/bin/pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "$APP_PATH/venv/bin/pip install --no-cache-dir -r /requirements.txt" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive $APP_PATH/venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    ) nginx" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir $APP_PATH
RUN mkdir /config
COPY / $APP_PATH/
WORKDIR $APP_PATH
#RUN chmod +x $APP_PATH/influxbee.sh

VOLUME /config

RUN echo '0-59  *  *  *  *    $APP_PATH/venv/bin/python $APP_PATH/influxbee.py -u $MIRUBEE_USER -p $MIRUBEE_PASSWORD --config-file /config/mirubee.toml' > /etc/crontabs/root

CMD ['crond', '-l 2', '-f']


