# Generated by Django 3.1.14 on 2023-07-15 22:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usa_jobs', '0003_auto_20230715_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=255)),
                ('org_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='relatedorgs',
            name='org_name',
        ),
        migrations.AddField(
            model_name='relatedorgs',
            name='code',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='usa_jobs.organization'),
            preserve_default=False,
        ),
    ]
