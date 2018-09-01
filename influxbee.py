# import the standard JSON parser
import json
# import the REST library
import requests
import argparse

MIRUBEE_API_URL = "https://app.mirubee.com/api/v2"

def login(email, password):
    data = '''{
        "language": "ES",
        "client_type_id": "api",
        "client_id": "influxdb",
        "timezone": "Europe/Madrid",
        "password": "{}",
        "email": "{}"
    }'''.format(password, email)
    url = "{}/login".format(MIRUBEE_API_URL)
    response = requests.post(url, data=data)

    print(response.text)
    print("----------")
    print(response.json())
    print("----------")
    print(response.status_code)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Pull data from mirubee.')
    parser.add_argument('-u', '--user', help='Username', required=True)
    parser.add_argument('-p', '--password', help='Password', required=True)
    args = parser.parse_args()

    login(args.user, args.password)