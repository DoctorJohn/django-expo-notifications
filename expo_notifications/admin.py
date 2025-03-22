from admin_anchors import admin_anchor
from django.contrib import admin
from django.utils.translation import ngettext

from expo_notifications.models import Device, Message, Receipt, Ticket


class DeviceAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "is_active",
        "date_registered",
        "lang",
        "user_link",
        "messages_link",
    ]
    list_filter = ["is_active", "lang", "date_registered"]
    search_fields = ["user__username", "push_token"]

    def get_ordering(self, request):
        return ["-id"]

    @admin.display(description="User")
    @admin_anchor("user")
    def user_link(self, instance):
        return str(instance.user)

    @admin.display(description="Messages")
    @admin_anchor("messages")
    def messages_link(self, instance):
        return str(instance.messages.count())


class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "title",
        "body",
        "date_created",
        "device_link",
        "ticket_link",
    ]
    list_filter = [
        "date_created",
        "expiration",
        "priority",
        "channel_id",
        "category_id",
        "mutable_content",
    ]
    search_fields = ["title", "body", "subtitle"]
    actions = ["send_messages"]

    def get_ordering(self, request):
        return ["-id"]

    @admin.display(description="Device")
    @admin_anchor("device")
    def device_link(self, instance):
        return str(instance.device)

    @admin.display(description="Ticket")
    @admin_anchor("ticket")
    def ticket_link(self, instance):
        return str(instance.ticket)

    @admin.action(description="Send selected messages")
    def send_messages(modeladmin, request, queryset):
        from expo_notifications.tasks import send_messages

        message_pks = list(queryset.values_list("pk", flat=True))
        send_messages.delay_on_commit(message_pks)

        modeladmin.message_user(
            request,
            ngettext("%d message was sent.", "%d messages were sent.", queryset.count())
            % queryset.count(),
        )


class ReceiptAdmin(admin.ModelAdmin):
    list_display = ["__str__", "is_success", "date_checked", "ticket_link"]
    list_filter = ["is_success", "date_checked"]

    def get_ordering(self, request):
        return ["-id"]

    @admin.display(description="Ticket")
    @admin_anchor("ticket")
    def ticket_link(self, instance):
        return str(instance.ticket)


class TicketAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "is_success",
        "date_received",
        "external_id",
        "message_link",
        "receipt_link",
    ]
    list_filter = ["is_success", "date_received"]
    search_fields = ["external_id"]

    def get_ordering(self, request):
        return ["-id"]

    @admin.display(description="Message")
    @admin_anchor("message")
    def message_link(self, instance):
        return str(instance.message)

    @admin.display(description="Receipt")
    @admin_anchor("receipt")
    def receipt_link(self, instance):
        return str(instance.receipt)


admin.site.register(Device, DeviceAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(Ticket, TicketAdmin)
