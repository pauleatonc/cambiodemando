# Fix NOT NULL violation: x_tweet_id must have default so get_or_create(publication_date=...) works

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0006_add_x_tweet_id_x_published_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailypublication',
            name='x_tweet_id',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
