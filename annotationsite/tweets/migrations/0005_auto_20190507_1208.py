# Generated by Django 2.2.1 on 2019-05-07 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0004_auto_20190507_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweetmedia',
            name='is_meme',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='tweetuser',
            name='url',
            field=models.URLField(null=True),
        ),
    ]
