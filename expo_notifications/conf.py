from datetime import timedelta

from django.conf import settings as django_settings


class Settings:
    @property
    def token(self) -> str | None:
        return getattr(
            django_settings,
            "EXPO_NOTIFICATIONS_TOKEN",
            None,
        )

    @property
    def receipt_check_delay(self) -> timedelta:
        return getattr(
            django_settings,
            "EXPO_NOTIFICATIONS_RECEIPT_CHECK_DELAY",
            timedelta(minutes=30),
        )

    @property
    def sending_task_max_retries(self) -> int:
        return getattr(
            django_settings,
            "EXPO_NOTIFICATIONS_SENDING_TASK_MAX_RETRIES",
            5,
        )

    @property
    def sending_task_retry_delay(self) -> timedelta:
        return getattr(
            django_settings,
            "EXPO_NOTIFICATIONS_SENDING_TASK_RETRY_DELAY",
            timedelta(seconds=30),
        )

    @property
    def checking_task_max_retries(self) -> int:
        return getattr(
            django_settings,
            "EXPO_NOTIFICATIONS_CHECKING_TASK_MAX_RETRIES",
            3,
        )

    @property
    def checking_task_retry_delay(self) -> timedelta:
        return getattr(
            django_settings,
            "EXPO_NOTIFICATIONS_CHECKING_TASK_RETRY_DELAY",
            timedelta(minutes=1),
        )


settings = Settings()
