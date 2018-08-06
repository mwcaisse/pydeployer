import requests


class TokenFetcher:

    AUTH_TOKEN_HEADER = "MITCHELL_SESSION"

    def __init__(self, config):
        if "tokens" not in config:
            #TODO: Perform some better json validation
            raise AssertionError("No token configuration present")

        self.config = config["tokens"]

    def fetch_tokes(self, application_uuid):
        url = self.construct_url("application/{application_uuid}/environment/{environment_uuid}/token".format(
            application_uuid=application_uuid,
            environment_uuid=self.config["environment_uuid"]
        ))
        auth_token = self.login_for_token()
        resp = requests.get(url, headers={
            self.AUTH_TOKEN_HEADER:  auth_token
        })
        resp.raise_for_status()
        return self.parse_token_response(resp.json())

    def parse_token_response(self, tokens_list):
        return {t["name"]: t["value"] for t in tokens_list}

    def login_for_token(self):
        resp = requests.post(self.construct_url("user/login/token"), json={
            "username": self.config["service_username"],
            "authenticationToken": self.config["service_token"]
        })
        resp.raise_for_status()
        if bool(resp.text):
            return resp.headers[self.AUTH_TOKEN_HEADER]
        return None

    def construct_url(self, relative_url):
        api_url = self.config["service_url"]
        if not api_url.endswith("/"):
            api_url = api_url + "/"
        return api_url + relative_url
