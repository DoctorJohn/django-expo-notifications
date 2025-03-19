import factory
from django.conf import settings
from django.utils import timezone

from expo_notifications.models import Device, Message, Receipt, Ticket


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.Sequence(lambda n: f"username{n}")


class DeviceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Device

    user = factory.SubFactory(UserFactory)
    lang = factory.Faker("random_element", elements=["en", "en-US", "en-GB"])
    push_token = factory.Sequence(lambda n: f"ExponentPushToken[{n}]")
    date_registered = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    is_active = factory.Faker("boolean")


class ActiveDeviceFactory(DeviceFactory):
    is_active = True


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    device = factory.SubFactory(DeviceFactory)
    data = factory.Faker("pydict", value_types=(str,))
    title = factory.Faker("text", max_nb_chars=64)
    body = factory.Faker("text", max_nb_chars=256)
    ttl = factory.Faker("time_delta")
    expiration = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    priority = factory.Faker(
        "random_element", elements=[p for p, _ in Message.PRIORITY_CHOICES]
    )
    subtitle = factory.Faker("text", max_nb_chars=64)
    sound = factory.Faker("text", max_nb_chars=64)
    badge = factory.Faker("random_int", min=0, max=100)
    channel_id = factory.Faker("word")
    category_id = factory.Faker("word")
    mutable_content = factory.Faker("boolean")
    date_scheduled = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())


class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    message = factory.SubFactory(MessageFactory)
    is_success = factory.Faker("boolean")
    external_id = factory.Faker("uuid4")
    error_message = factory.Faker("text", max_nb_chars=256)
    date_received = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())


class ReceiptFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Receipt

    ticket = factory.SubFactory(TicketFactory)
    is_success = factory.Faker("boolean")
    error_message = factory.Faker("text", max_nb_chars=256)
    date_checked = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
