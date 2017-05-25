from django.conf import settings
import hashlib


def create_hash(data, add_secret=True, limit=16):
    m = hashlib.sha256()
    if add_secret:
        m.update((str(data) + settings.SECRET_KEY).encode('utf-8'))
    else:
        m.update(str(data).encode('utf-8'))
    return m.hexdigest()[0:limit]
