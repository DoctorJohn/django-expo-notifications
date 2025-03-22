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
