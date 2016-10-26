from services.freesound import freesound
from services.fake_service import fake_service


def get_available_services():
    return [freesound, fake_service]
