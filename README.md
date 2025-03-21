# Django Expo Notifications

## Example Project

Take a look at our Django example project under `tests/project`.
It can be run by executing these commands:

1. `poetry install`
2. `poetry run tests/project/manage.py migrate`
3. `poetry run tests/project/manage.py createsuperuser`
4. `poetry run tests/project/manage.py runserver`

### Live testing

Test sending push notifications and checking their receipts involves running a Celery worker and making sure the Celery worker is authorized to communicate with Expo.

Unless the default Celery broker setup works for you (i.e. RabbitMQ on localhost), you need to provide a Celery broker url:

```sh
export CELERY_BROKER_URL="redis://localhost:6379/0"
```

In case you enabled `Enhanced Security for Push Notifications` in your Expo account, you also need to provide an Expo access token.

```sh
export EXPO_NOTIFICATIONS_TOKEN="your-expo-viewer-access-token-here"
```

Now you can run a Celery worker and a Django shell in parallel to test sending push notifications and checking their receipts:

- `poetry run celery --workdir tests/project --app project worker -l INFO`
- `poetry run tests/project/manage.py shell`

The following snipped shows how to send a push notification from the Django shell, which will be send and later checked by the Celery worker:

```python
from django.utils import timezone
from expo_notifications.models import Device

device = Device.objects.create(
    token='ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]',
    date_registered=timezone.now(),
)

device.messages.send(
    title='Hello, World!',
    body='This is a test message.',
    date_scheduled=timezone.now(),
)
```
