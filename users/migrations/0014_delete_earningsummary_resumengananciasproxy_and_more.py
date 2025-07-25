# Generated by Django 5.2.4 on 2025-07-25 16:09

import django.contrib.auth.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_earningsummary_alter_earning_amount_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EarningSummary',
        ),
        migrations.CreateModel(
            name='ResumenGananciasProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Resumen de Ganancias',
                'verbose_name_plural': 'Resumen de Ganancias',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('users.customuser',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='earning',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
        migrations.AlterField(
            model_name='earning',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='earning',
            name='earning_type',
            field=models.CharField(choices=[('referido', 'Referido'), ('promocion', 'Promoción'), ('viaje', 'Viaje'), ('otro', 'Otro')], max_length=20),
        ),
        migrations.AlterField(
            model_name='earning',
            name='related_promotion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='earnings', to='users.promotion'),
        ),
        migrations.AlterField(
            model_name='earning',
            name='related_trip',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='earnings', to='users.trip'),
        ),
        migrations.AlterField(
            model_name='earning',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='earnings', to=settings.AUTH_USER_MODEL),
        ),
    ]
