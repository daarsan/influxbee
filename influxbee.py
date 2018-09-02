# import the standard JSON parser
import json

# import logger
import logging

# import the REST library
import requests

import argparse
import os

class MirubeeUserInfo():
    def init(self):
        pass


class MirubeeApi():
    MIRUBEE_API_URL = "https://app.mirubee.com/api/v2/"

    def setToken(self, token):
        self.MIRUBEE_API_TOKEN = token

        return self.MIRUBEE_API_TOKEN

    def login(self, email, password):
        data = {
            "language": "ES",
            "client_type_id": "api",
            "client_id": "influxdb",
            "timezone": "Europe/Madrid",
            "password": password,
            "email": email
        }
        _url = "{}{}".format(self.MIRUBEE_API_URL, "login")
        logger.debug("Getting info from {}".format(_url))
        response = requests.post(_url, data=data)
        logger.debug("Response Code: {}".format(response.status_code))

        if response.status_code == 201:
            logger.debug(response.text)
            self.MIRUBEE_API_TOKEN = response.json()['token']
        else:
            raise ConnectionError()

        return self.MIRUBEE_API_TOKEN

    def _get(self, url):
        _headers = {'Authorization': self.MIRUBEE_API_TOKEN}
        _url = "{}{}".format(self.MIRUBEE_API_URL, url)

        logger.debug("Getting info from {}".format(_url))
        response = requests.get(_url, headers=_headers)
        logger.debug("Response Code: {}".format(response.status_code))

        if response.status_code == 200:
            logger.debug("\n" + json.dumps(response.json(), indent=2))
        else:
            raise ConnectionError()

        return response.json()

    def getInfo(self):
        url = "me"

        return self._get(url)

    def getBuildings(self, user_id):
        url = "users/{}/buildings".format(user_id)

        return self._get(url)

    def getBuildingInfo(self, building_id):
        url = "buildings/{}".format(building_id)

        return self._get(url)

    def getBuildingMeters(self, building_id):
        url = "buildings/{}/meters".format(building_id)

        return self._get(url)

    def getMeterInfo(self, building_id, meter_id):
        url = "buildings/{}/meters/{}".format(building_id, meter_id)

        return self._get(url)

    def getChannelLast(self, building_id, meter_id, channel_id):
        url = "buildings/{}/meters/{}/channels/{}/last".format(building_id, meter_id, channel_id)

        return self._get(url)

    def scan(self):
        user_data = {
            "MIRUBEE_API_TOKEN": self.MIRUBEE_API_TOKEN
        }

        MIRUBEE_USER_INFO = self.getInfo()
        # logger.debug(MIRUBEE_USER_INFO)
        user_data["MIRUBEE_USER_ID"] = MIRUBEE_USER_INFO['id']

        MIRUBEE_USER_BUILDINGS = mirubee.getBuildings(MIRUBEE_USER_INFO['id'])
        # logger.debug(MIRUBEE_USER_BUILDINGS)
        # user_data["MIRUBEE_USER_BUILDINGS"] = [MIRUBEE_USER_BUILDING['id'] for MIRUBEE_USER_BUILDING in MIRUBEE_USER_BUILDINGS]
        user_data["MIRUBEE_USER_BUILDINGS"] = [
        {
            "MIRUBEE_BUILDING_ID": MIRUBEE_BUILDING['id'],
            "MIRUBEE_BUILDING_METERS": [
                {
                    "MIRUBEE_METER_ID": MIRUBEE_METER['meter_id'],
                    "MIRUBEE_METER_CHANNELS": [
                        {
                            "MIRUBEE_CHANNEL_ID": MIRUBEE_CHANNEL['channel_id'],
                            "MIRUBEE_CHANNEL_MAIN": MIRUBEE_CHANNEL['main_connection']
                        } for MIRUBEE_CHANNEL in MIRUBEE_METER['channels']]
                } for MIRUBEE_METER in mirubee.getBuildingMeters(MIRUBEE_BUILDING['id'])
            ]
        } for MIRUBEE_BUILDING in MIRUBEE_USER_BUILDINGS]

        return user_data


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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Pull data from mirubee.')
    parser.add_argument('--user', '-u', help='Username')
    parser.add_argument('--password', '-p', help='Password')
    parser.add_argument('--verbose_mode', help='Increase output verbosity', action="store_true")
    parser.add_argument('--config_file', help='Path of the file with the information of user')
    args = parser.parse_args()

    logger = _setup_logger(args.verbose_mode)

    mirubee = MirubeeApi()

    config_file = os.path.abspath(args.config_file if args.config_file else "mirubee.toml")

    if os.path.exists(config_file):
        logger.debug("Opening user data file on {}".format(config_file))
        with open(config_file) as f:
            user_data = json.load(f)
        mirubee.setToken(user_data['MIRUBEE_API_TOKEN'])
    else:
        logger.info("Generating user data file on {}".format(config_file))

        username = os.environ.get("MIRUBEE_USER", args.user)
        password = os.environ.get("MIRUBEE_PASSWORD", args.password)

        if not username or not password:
            raise RuntimeError("Since there is no configuration file, username AND password are required.")

        MIRUBEE_API_TOKEN = mirubee.login(username, password)

        user_data = mirubee.scan()
        logger.debug(user_data)

        with open(config_file, 'w') as f:
            json.dump(user_data, f, indent=2)

    for MIRUBEE_USER_BUILDING in user_data['MIRUBEE_USER_BUILDINGS']:
        for MIRUBEE_BUILDING_METER in MIRUBEE_USER_BUILDING['MIRUBEE_BUILDING_METERS']:
            for MIRUBEE_METER_CHANNEL in MIRUBEE_BUILDING_METER['MIRUBEE_METER_CHANNELS']:
                if MIRUBEE_METER_CHANNEL['MIRUBEE_CHANNEL_MAIN']:
                    measure = mirubee.getChannelLast(MIRUBEE_USER_BUILDING['MIRUBEE_BUILDING_ID'],
                                                     MIRUBEE_BUILDING_METER['MIRUBEE_METER_ID'],
                                                     MIRUBEE_METER_CHANNEL['MIRUBEE_CHANNEL_ID'])
                    logger.info(measure)

    # MIRUBEE_API_TOKEN = os.environ.get("MIRUBEE_API_TOKEN", mirubee.login(args.user, args.password))
    # logger.debug(MIRUBEE_API_TOKEN)
    #
    # MIRUBEE_USER_INFO = mirubee.getInfo()
    # logger.debug(MIRUBEE_USER_INFO)
    #
    # MIRUBEE_USER_BUILDINGS = mirubee.getBuildings(MIRUBEE_USER_INFO['id'])
    #
    # for MIRUBEE_USER_BUILDING in MIRUBEE_USER_BUILDINGS:
    #     logger.debug(MIRUBEE_USER_BUILDING)
    #
    #     MIRUBEE_BUILDING_INFO = mirubee.getBuildingInfo(MIRUBEE_USER_BUILDING['id'])
    #     logger.debug(MIRUBEE_BUILDING_INFO)
    #
    #     MIRUBEE_BUILDING_METERS = mirubee.getBuildingMeters(MIRUBEE_USER_BUILDING['id'])
    #     for MIRUBEE_BUILDING_METER in MIRUBEE_BUILDING_METERS:
    #         logger.debug(MIRUBEE_BUILDING_METER)
    #
    #         MIRUBEE_METER_INFO = mirubee.getMeterInfo(MIRUBEE_USER_BUILDING['id'], MIRUBEE_BUILDING_METER['meter']['id'])
    #         logger.debug(MIRUBEE_METER_INFO)
    #
    #         for MIRUBEE_METER_CHANNEL in MIRUBEE_METER_INFO['channels']:
    #             if MIRUBEE_METER_CHANNEL['main_connection']:
    #                 measure = mirubee.getChannelLast(MIRUBEE_USER_BUILDING['id'], MIRUBEE_BUILDING_METER['meter']['id'],
    #                                       MIRUBEE_METER_CHANNEL['channel_id'])
    #                 logger.info(measure)