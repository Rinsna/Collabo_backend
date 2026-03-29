# Generated migration to add location field to CompanyProfile

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_influencerprofile_latest_product_review_likes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyprofile',
            name='location',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
