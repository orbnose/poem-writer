# Generated by Django 4.1.2 on 2022-10-20 08:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BookFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=200)),
                ('hash', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=45)),
                ('pos_tag', models.CharField(max_length=13)),
                ('dependency_label', models.CharField(blank=True, max_length=13)),
                ('count', models.IntegerField(default=1)),
                ('ancestor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='db.word')),
            ],
        ),
    ]
