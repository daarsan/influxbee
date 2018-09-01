# import the standard JSON parser
import json

# import logger
import logging

# import the REST library
import requests

import argparse
import os

MIRUBEE_API_URL = "https://app.mirubee.com/api/v2"

class MirubeeApi():
    pass

def _setup_logger(verbose_mode):
    # create logger with 'influxbee'
    logger = logging.getLogger('influxbee')
    logger.setLevel(logging.DEBUG)

    # create console handler with a lower log level
    ch = logging.StreamHandler()
    if verbose_mode:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)

    return logger

def login(email, password):
    data = {
        "language": "ES",
        "client_type_id": "api",
        "client_id": "influxdb",
        "timezone": "Europe/Madrid",
        "password": password,
        "email": email
    }
    url = "{}/login".format(MIRUBEE_API_URL)
    logger.debug("Connecting to {}".format(url))
    response = requests.post(url, data=data)
    logger.debug("Response: {}".format(response.status_code))

    if response.status_code == 201:
        MIRUBEE_API_TOKEN = response.json()['token']
        os.environ.setdefault("MIRUBEE_API_TOKEN", MIRUBEE_API_TOKEN)
        logger.debug("Connection successful")
    else:
        raise ConnectionError()

    return MIRUBEE_API_TOKEN

def getInfo(MIRUBEE_API_TOKEN):
    headers = {'Authorization': MIRUBEE_API_TOKEN}
    url = "{}/me".format(MIRUBEE_API_URL)

    logger.debug("Getting info from {}".format(url))
    response = requests.get(url, headers=headers)
    logger.debug("Response: {}".format(response.status_code))

    if response.status_code == 200:
        return response.json()
        logger.debug("Connection successful")
    else:
        raise ConnectionError()

def getBuildings(MIRUBEE_API_TOKEN, user_id):
    headers = {'Authorization': MIRUBEE_API_TOKEN}
    url = "{}/users/{}/buildings".format(MIRUBEE_API_URL, user_id)

    logger.debug("Getting info from {}".format(url))
    response = requests.get(url, headers=headers)
    logger.debug("Response: {}".format(response.status_code))

    if response.status_code == 200:
        return response.json()
        logger.debug("Connection successful")
    else:
        raise ConnectionError()

def getBuildingInfo(MIRUBEE_API_TOKEN, building_id):
    headers = {'Authorization': MIRUBEE_API_TOKEN}
    url = "{}/buildings/{}".format(MIRUBEE_API_URL, building_id)

    logger.debug("Getting info from {}".format(url))
    response = requests.get(url, headers=headers)
    logger.debug("Response: {}".format(response.status_code))

    if response.status_code == 200:
        return response.json()
        logger.debug("Connection successful")
    else:
        raise ConnectionError()

def getBuildingMeters(MIRUBEE_API_TOKEN, building_id):
    headers = {'Authorization': MIRUBEE_API_TOKEN}
    url = "{}/buildings/{}/meters".format(MIRUBEE_API_URL, building_id)

    logger.debug("Getting info from {}".format(url))
    response = requests.get(url, headers=headers)
    logger.debug("Response: {}".format(response.status_code))

    if response.status_code == 200:
        return response.json()
        logger.debug("Connection successful")
    else:
        raise ConnectionError()

def getMeterInfo(MIRUBEE_API_TOKEN, building_id, meter_id):
    headers = {'Authorization': MIRUBEE_API_TOKEN}
    url = "{}/buildings/{}/meters/{}".format(MIRUBEE_API_URL, building_id, meter_id)

    logger.debug("Getting info from {}".format(url))
    response = requests.get(url, headers=headers)
    logger.debug("Response: {}".format(response.status_code))

    if response.status_code == 200:
        return response.json()
        logger.debug("Connection successful")
    else:
        raise ConnectionError()

def getChannelLast(MIRUBEE_API_TOKEN, building_id, meter_id, channel_id):
    headers = {'Authorization': MIRUBEE_API_TOKEN}
    url = "{}/buildings/{}/meters/{}/channels/{}/last".format(MIRUBEE_API_URL, building_id, meter_id, channel_id)

    logger.debug("Getting info from {}".format(url))
    response = requests.get(url, headers=headers)
    logger.debug("Response: {}".format(response.status_code))

    if response.status_code == 200:
        return response.json()
        logger.debug("Connection successful")
    else:
        raise ConnectionError()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Pull data from mirubee.')
    parser.add_argument('user', help='Username')
    parser.add_argument('password', help='Password')
    parser.add_argument('--verbose_mode', help='Increase output verbosity', action="store_true")
    args = parser.parse_args()

    logger = _setup_logger(args.verbose_mode)

    MIRUBEE_API_TOKEN = os.environ.get("MIRUBEE_API_TOKEN", login(args.user, args.password))
    logger.debug(MIRUBEE_API_TOKEN)

    MIRUBEE_USER_INFO = getInfo(MIRUBEE_API_TOKEN)
    logger.debug(MIRUBEE_USER_INFO)

    MIRUBEE_USER_BUILDINGS = getBuildings(MIRUBEE_API_TOKEN, MIRUBEE_USER_INFO['id'])

    for MIRUBEE_USER_BUILDING in MIRUBEE_USER_BUILDINGS:
        logger.debug(MIRUBEE_USER_BUILDING)

        MIRUBEE_BUILDING_INFO = getBuildingInfo(MIRUBEE_API_TOKEN, MIRUBEE_USER_BUILDING['id'])
        logger.debug(MIRUBEE_BUILDING_INFO)

        MIRUBEE_BUILDING_METERS = getBuildingMeters(MIRUBEE_API_TOKEN, MIRUBEE_USER_BUILDING['id'])
        for MIRUBEE_BUILDING_METER in MIRUBEE_BUILDING_METERS:
            logger.debug(MIRUBEE_BUILDING_METER)

            MIRUBEE_METER_INFO = getMeterInfo(MIRUBEE_API_TOKEN, MIRUBEE_USER_BUILDING['id'], MIRUBEE_BUILDING_METER['meter']['id'])
            logger.debug(MIRUBEE_METER_INFO)

            for MIRUBEE_METER_CHANNEL in MIRUBEE_METER_INFO['channels']:
                if MIRUBEE_METER_CHANNEL['main_connection']:
                    measure = getChannelLast(MIRUBEE_API_TOKEN, MIRUBEE_USER_BUILDING['id'], MIRUBEE_BUILDING_METER['meter']['id'],
                                          MIRUBEE_METER_CHANNEL['channel_id'])
                    logger.info(measure)



