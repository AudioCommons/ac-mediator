from services.classes import *


class JamendoService(BaseACService, ACServiceAuthMixin):
    NAME = 'Jamendo'
    URL = 'http://www.jamendo.com'
    API_BASE_URL = 'https://api.jamendo.com/v3.0/'
    SUPPORTED_AUTH_METHODS = [APIKEY_AUTH_METHOD, ENDUSER_AUTH_METHOD]
    BASE_AUTHORIZE_URL = API_BASE_URL + 'oauth/authorize/?client_id={0}'
    ACCESS_TOKEN_URL = API_BASE_URL + 'oauth/grant/'
    REFRESH_TOKEN_URL = API_BASE_URL + 'oauth/grant/'

    def get_authorize_url(self):
        # Jamendo needs to include 'redirect_uri' in the authorize url
        return self.BASE_AUTHORIZE_URL.format(self.service_client_id) \
               + '&redirect_uri={0}'.format(self.get_redirect_uri())

    def access_token_request_data(self, authorization_code):
        # Jamendo needs to include 'redirect_uri' in the access token request
        data = super(JamendoService, self).access_token_request_data(authorization_code)
        data.update({'redirect_uri': self.get_redirect_uri()})
        return data
