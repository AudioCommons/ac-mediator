from services.classes import *


class JamendoService(BaseACService, ACServiceAuthMixin):
    NAME = 'Jamendo'
    URL = 'http://www.jamendo.com'
    API_BASE_URL = "https://api.jamendo.com/v3.0/"
    BASE_AUTHORIZE_URL = API_BASE_URL + 'oauth/authorize/?client_id={0}'
    ACCESS_TOKEN_URL = API_BASE_URL + 'oauth/grant/'
    REFRESH_TOKEN_URL = API_BASE_URL + 'oauth/grant/'
