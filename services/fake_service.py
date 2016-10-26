from services.classes import *


class FakeService(BaseACService, ACServiceAuthMixin):
    NAME = 'Fake service'


fake_service = FakeService()