# Generated by Django 5.2.4 on 2025-07-24 16:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_report_followup_notes_report_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Políticas y Condiciones', max_length=100)),
                ('content', models.TextField(help_text='Texto completo de las políticas y condiciones para bonos y referidos')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('bonus_amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('min_invited_users', models.PositiveIntegerField(default=0, help_text='Cantidad mínima de usuarios invitados')),
                ('min_trips', models.PositiveIntegerField(default=0, help_text='Cantidad mínima de viajes realizados')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='UserPromotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('awarded_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('promotion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_promotions', to='users.promotion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_promotions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
