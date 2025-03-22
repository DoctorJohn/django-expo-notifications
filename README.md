# Django Expo Notifications

[![PyPI][pypi-image]][pypi-url]
![PyPI - Python Version][python-image]
![PyPI - Django Version][django-image]
[![Codecov][codecov-image]][codecov-url]
[![License][license-image]][license-url]

[pypi-image]: https://img.shields.io/pypi/v/django-expo-notifications
[pypi-url]: https://pypi.org/project/django-expo-notifications/
[python-image]: https://img.shields.io/pypi/pyversions/django-expo-notifications
[django-image]: https://img.shields.io/pypi/djversions/django-expo-notifications
[codecov-image]: https://codecov.io/gh/DoctorJohn/django-expo-notifications/branch/main/graph/badge.svg
[codecov-url]: https://codecov.io/gh/DoctorJohn/django-expo-notifications
[license-image]: https://img.shields.io/pypi/l/django-expo-notifications
[license-url]: https://github.com/DoctorJohn/django-expo-notifications/blob/main/LICENSE

A Django app that allows you to keep track of devices, send Expo push notifications, and check their tickets for receipts.
This project makes use of the [Expo Server SDK for Python](https://github.com/expo-community/expo-server-sdk-python) for sending push messages and checking push receipts.

## Installation

```sh
pip install django-expo-notifications
```

After installing the Django app, add it to your project's `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = [
    "expo_notifications",  # <-- Add this line
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
```

The `expo_notifications` app comes with a set of models.
To make them available in your database, run Django's `migrate` management command:

```sh
python manage.py migrate
```

## Settings

You may optionally set the following settings in your Django project's settings module.
The code snippet bellow shows the default values for each setting.

```python
from datetime import timedelta


EXPO_NOTIFICATIONS_TOKEN = None

EXPO_NOTIFICATIONS_RECEIPT_CHECK_DELAY = timedelta(minutes=30)

EXPO_NOTIFICATIONS_SENDING_TASK_MAX_RETRIES = 5

EXPO_NOTIFICATIONS_SENDING_TASK_RETRY_DELAY = timedelta(seconds=30)

EXPO_NOTIFICATIONS_CHECKING_TASK_MAX_RETRIES = 3

EXPO_NOTIFICATIONS_CHECKING_TASK_RETRY_DELAY = timedelta(minutes=1)
```

### Enhanced Security for Push Notifications

At some point you most likely want to enable `Enhanced Security for Push Notifications` in your Expo account.
This will require you to provide an Expo access token in your Django project's settings module like this:

```python
EXPO_NOTIFICATIONS_TOKEN = "your-expo-viewer-access-token-here"
```

Check out the [Expo documentation](https://docs.expo.dev/push-notifications/sending-notifications/#additional-security) for more information.

### Receipt Check Delay

Expo recommends to check the receipts of push notifications after some delay.
This gives Expo time to process the push notifications and generate receipts.
By default, the delay is set to 30 minutes, based on the value used in the official [Expo Server SDK for Node](https://github.com/expo/expo-server-sdk-node).
If needed, you can adjust the delay setting like this:

```python
EXPO_NOTIFICATIONS_RECEIPT_CHECK_DELAY = timedelta(hours=1)
```

However, note that Expo only keeps ticket receipts for around a day and Celery generally prefers if tasks are not scheduled too far in the future.

## Usage

The most basic usage of this app involves creating `Device` and `Message` model instances.

### Quickstart

```python
from django.contrib.auth import get_user_model
from expo_notifications.models import Device, Message


some_user = get_user_model().objects.first()

device = Device.objects.create(
    user=some_user,
    push_token="ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]",
)

device.messages.send(
    title="Hello, World!",
    body="This is a test message.",
)
```

### Keeping track of user devices

The `Device` model represents a user device that can receive push notifications as long as it's `is_active` flag is `True`.
A user may have multiple devices, however, each device must have an Expo token that is unique to that device and user.

```python
from django.contrib.auth import get_user_model
from expo_notifications.models import Device


some_user = get_user_model().objects.first()

Device.objects.update_or_create(
    user=some_user,
    push_token="ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]",
    defaults={"is_active": True},
)
```

We recommend using `update_or_create` to avoid duplicate devices and to automatically reactivate existing devices if necessary.

#### Keeping track of device language

The `Device` model has an optional `lang` field that can be used to store the language/region code of the device.g. as per ISO 639-1).
This can be useful if you want to send localized push notifications to your users.

```python
from django.contrib.auth import get_user_model
from expo_notifications.models import Device


some_user = get_user_model().objects.first()

Device.objects.update_or_create(
    user=some_user,
    push_token="ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]",
    defaults={"is_active": True, "lang": "en"},
)
```

We recommend using [ISO 639-1](https://en.wikipedia.org/wiki/ISO_639-1) and, if needed, [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) codes.

### Sending push notifications

The recommended way to send messages is to create and send them in bulk like this:

```python
from expo_notifications.models import Device, Message


messages = [
    Message(device=device, title="Hello, World!")
    for device in Device.objects.all()
]

Message.objects.bulk_send(messages)
```

Similar to `bulk_send`, we provide a `send` method that can be used to send a single message:

```python
from expo_notifications.models import Device, Message


device = Device.objects.first()

Message.objects.send(device=device, title="Hello, World!")
```

Both `bulk_send` and `send` methods use Django's `bulk_create` and `create` under the hood and are also available on related managers:

```python
from expo_notifications.models import Device


device = Device.objects.first()
device.messages.send(title="Hello, World!")
```

#### Manually resending messages

This feature is mainly meant for debugging purposes, since Celery will automatically retry sending messages in case of a failure.

```python
from expo_notifications.models import Message


# Resending a single message (i.e. a model instance)
single_message = Message.objects.first()
single_message.send()

# Resending multiple messages (i.e. a queryset)
multiple_messages = Message.objects.all()
multiple_messages.send()
```

## Example Project

Take a look at our Django example project under `tests/project`.
It can be run by executing these commands:

1. `poetry install`
2. `poetry run tests/project/manage.py migrate`
3. `poetry run tests/project/manage.py createsuperuser`
4. `poetry run tests/project/manage.py runserver`

### Live testing

Sending push notifications and checking their receipts can be done by using the "Send selected messages" action in the Django admin interface.
In order for this to work, you need to run a Celery worker and make sure the Celery worker is authorized to communicate with Expo.

Unless the default Celery broker setup works for you (i.e. RabbitMQ on localhost), you need to provide a Celery broker url:

```sh
export CELERY_BROKER_URL="redis://localhost:6379/0"
```

In case you enabled `Enhanced Security for Push Notifications` in your Expo account, you also need to provide an Expo access token.

```sh
export EXPO_NOTIFICATIONS_TOKEN="your-expo-viewer-access-token-here"
```

Now you can run a Celery worker and the Django dev server in parallel to test sending push notifications and checking their receipts:

- `poetry run celery --workdir tests/project --app project worker -l INFO`
- `poetry run tests/project/manage.py runserver`
