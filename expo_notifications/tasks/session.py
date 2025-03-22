import requests

from expo_notifications.conf import settings

session = requests.Session()
session.headers.update(
    {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }
)

if settings.token is not None:
    session.headers.update({"Authorization": f"Bearer {settings.token}"})
