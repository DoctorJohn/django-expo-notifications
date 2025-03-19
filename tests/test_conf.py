from datetime import timedelta

from expo_notifications.conf import settings as expo_notifications_settings


def test_token(settings):
    settings.EXPO_NOTIFICATIONS_TOKEN = "test-token"
    assert expo_notifications_settings.token == "test-token"


def test_token_default(settings):
    del settings.EXPO_NOTIFICATIONS_TOKEN
    assert expo_notifications_settings.token is None


def test_receipt_check_delay(settings):
    settings.EXPO_NOTIFICATIONS_RECEIPT_CHECK_DELAY = timedelta(minutes=45)
    assert expo_notifications_settings.receipt_check_delay == timedelta(minutes=45)


def test_receipt_check_delay_default(settings):
    del settings.EXPO_NOTIFICATIONS_RECEIPT_CHECK_DELAY
    assert expo_notifications_settings.receipt_check_delay == timedelta(minutes=30)


def test_sending_task_max_retries(settings):
    settings.EXPO_NOTIFICATIONS_SENDING_TASK_MAX_RETRIES = 10
    assert expo_notifications_settings.sending_task_max_retries == 10


def test_sending_task_max_retries_default(settings):
    del settings.EXPO_NOTIFICATIONS_SENDING_TASK_MAX_RETRIES
    assert expo_notifications_settings.sending_task_max_retries == 5


def test_sending_task_retry_delay(settings):
    settings.EXPO_NOTIFICATIONS_SENDING_TASK_RETRY_DELAY = timedelta(seconds=45)
    assert expo_notifications_settings.sending_task_retry_delay == timedelta(seconds=45)


def test_sending_task_retry_delay_default(settings):
    del settings.EXPO_NOTIFICATIONS_SENDING_TASK_RETRY_DELAY
    assert expo_notifications_settings.sending_task_retry_delay == timedelta(seconds=30)


def test_checking_task_max_retries(settings):
    settings.EXPO_NOTIFICATIONS_CHECKING_TASK_MAX_RETRIES = 6
    assert expo_notifications_settings.checking_task_max_retries == 6


def test_checking_task_max_retries_default(settings):
    del settings.EXPO_NOTIFICATIONS_CHECKING_TASK_MAX_RETRIES
    assert expo_notifications_settings.checking_task_max_retries == 3


def test_checking_task_retry_delay(settings):
    settings.EXPO_NOTIFICATIONS_CHECKING_TASK_RETRY_DELAY = timedelta(minutes=2)
    assert expo_notifications_settings.checking_task_retry_delay == timedelta(minutes=2)


def test_checking_task_retry_delay_default(settings):
    del settings.EXPO_NOTIFICATIONS_CHECKING_TASK_RETRY_DELAY
    assert expo_notifications_settings.checking_task_retry_delay == timedelta(minutes=1)
