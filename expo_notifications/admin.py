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
    autocomplete_fields = ["user"]

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
        "tickets_link",
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
    autocomplete_fields = ["device"]
    actions = ["send_messages"]

    def get_ordering(self, request):
        return ["-id"]

    @admin.display(description="Device")
    @admin_anchor("device")
    def device_link(self, instance):
        return str(instance.device)

    @admin.display(description="Tickets")
    @admin_anchor("tickets")
    def tickets_link(self, instance):
        return str(instance.tickets.count())

    @admin.action(description="Send selected messages")
    def send_messages(modeladmin, request, queryset):
        queryset.send()

        modeladmin.message_user(
            request,
            ngettext(
                "%d message will be send.",
                "%d messages will be send.",
                queryset.count(),
            )
            % queryset.count(),
        )


class ReceiptAdmin(admin.ModelAdmin):
    list_display = ["__str__", "is_success", "date_checked", "ticket_link"]
    list_filter = ["is_success", "date_checked"]
    autocomplete_fields = ["ticket"]

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
        "receipts_link",
    ]
    list_filter = ["is_success", "date_received"]
    search_fields = ["external_id"]
    autocomplete_fields = ["message"]
    actions = ["check_tickets"]

    def get_ordering(self, request):
        return ["-id"]

    @admin.display(description="Message")
    @admin_anchor("message")
    def message_link(self, instance):
        return str(instance.message)

    @admin.display(description="Receipts")
    @admin_anchor("receipts")
    def receipts_link(self, instance):
        return str(instance.receipts.count())

    @admin.action(description="Check selected tickets")
    def check_tickets(modeladmin, request, queryset):
        queryset.check_receipts()

        modeladmin.message_user(
            request,
            ngettext(
                "%d ticket receipt will be checked.",
                "%d ticket receipts will be checked.",
                queryset.count(),
            )
            % queryset.count(),
        )


admin.site.register(Device, DeviceAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(Ticket, TicketAdmin)
