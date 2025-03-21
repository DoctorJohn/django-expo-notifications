# Generated by Django 5.1.7 on 2025-03-19 19:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Device",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("lang", models.CharField(max_length=5)),
                ("push_token", models.CharField(max_length=4096)),
                ("date_registered", models.DateTimeField()),
                ("is_active", models.BooleanField(default=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="devices",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "push_token")},
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data", models.JSONField(blank=True, null=True)),
                ("title", models.CharField(blank=True, max_length=64)),
                ("body", models.CharField(blank=True, max_length=256)),
                ("ttl", models.DurationField(blank=True, null=True)),
                ("expiration", models.DateTimeField(blank=True, null=True)),
                (
                    "priority",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("default", "Default"),
                            ("normal", "Normal"),
                            ("high", "High"),
                        ],
                        max_length=7,
                        null=True,
                    ),
                ),
                ("subtitle", models.CharField(blank=True, max_length=64)),
                ("sound", models.CharField(blank=True, max_length=64)),
                ("badge", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("channel_id", models.CharField(blank=True, max_length=32)),
                ("category_id", models.CharField(blank=True, max_length=64)),
                ("mutable_content", models.BooleanField(default=False)),
                ("date_created", models.DateTimeField()),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="expo_notifications.device",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Ticket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_success", models.BooleanField()),
                ("external_id", models.CharField(blank=True, max_length=64)),
                ("error_message", models.TextField(blank=True)),
                ("date_received", models.DateTimeField()),
                (
                    "message",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ticket",
                        to="expo_notifications.message",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Receipt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_success", models.BooleanField()),
                ("error_message", models.TextField(blank=True)),
                ("date_checked", models.DateTimeField()),
                (
                    "ticket",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="receipt",
                        to="expo_notifications.ticket",
                    ),
                ),
            ],
        ),
    ]
