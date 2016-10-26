from services.classes import *


class FreesoundService(BaseACService, ACServiceAuthMixin):
    NAME = 'Freesound'
    URL = 'http://www.freesound.org'
    API_BASE_URL = "https://www.freesound.org/apiv2/"
    BASE_AUTHORIZE_URL = API_BASE_URL + 'oauth2/authorize/?client_id={client_id}&response_type=code'


freesound = FreesoundService()