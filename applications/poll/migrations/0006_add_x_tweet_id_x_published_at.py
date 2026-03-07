# Generated manually for X (Twitter) publication tracking

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0005_alter_vote_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailypublication',
            name='x_tweet_id',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='dailypublication',
            name='x_published_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
