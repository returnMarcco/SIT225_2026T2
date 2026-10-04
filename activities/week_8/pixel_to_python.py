import pandas as pd
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import iot_api_client as iot
from iot_api_client.configuration import Configuration
from iot_api_client.api import PropertiesV2Api

CLIENT_ID = "oUr7D0MqIqPKlUqfZfxYvco1Ix1Wly2s"
CLIENT_SECRET = "nCNPdJhYVoy9nCLZYFeXjBASO4kL7pNFJFHeDwp1g9wdCPzSY2icqm3VO20GQBe9"
THING_ID = "ec0dccb6-9475-43a0-baa2-bb3ad9e9ca73"

oauth_client = BackendApplicationClient(client_id=CLIENT_ID)
token_url = "https://api2.arduino.cc/iot/v1/clients/token"


oauth = OAuth2Session(client=oauth_client)

token = oauth.fetch_token(
    token_url=token_url,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    include_client_id=True,
    audience="https://api2.arduino.cc/iot"
)

access_token=token["access_token"]

configuration = Configuration(
    host="https://api2.arduino.cc"
)

configuration.access_token = access_token

api_client = iot.ApiClient(configuration)

properties_api = PropertiesV2Api(api_client)

properties = properties_api.properties_v2_list(THING_ID)

for prop in properties:
    print(prop.name, prop.id)