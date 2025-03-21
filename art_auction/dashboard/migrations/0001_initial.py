# Generated by Django 5.1.6 on 2025-03-04 10:56

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
            name='Catalogue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cat_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.CharField(blank=True, choices=[('Poor', 'Poor'), ('Fair', 'Fair'), ('Good', 'Good'), ('Very Good', 'Very Good'), ('Excellent', 'Excellent')], max_length=10, null=True)),
                ('feedback_text', models.TextField(blank=True, null=True)),
                ('sentiment', models.CharField(blank=True, choices=[('positive', 'Positive'), ('negative', 'Negative'), ('neutral', 'Neutral')], max_length=10, null=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('source', models.CharField(choices=[('frontend', 'Frontend'), ('backend', 'Backend')], default='frontend', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('query', models.TextField()),
                ('category', models.CharField(max_length=50)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Artwork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sale_type', models.CharField(choices=[('discount', 'Discount'), ('auction', 'Auction')], default='auction', max_length=50)),
                ('product_id', models.CharField(default='', max_length=255, null=True)),
                ('product_name', models.CharField(max_length=255, null=True)),
                ('product_price', models.IntegerField(default=0, null=True)),
                ('model_360', models.FileField(blank=True, null=True, upload_to='3d_models/')),
                ('opening_bid', models.IntegerField(blank=True, default=0, null=True)),
                ('product_qty', models.IntegerField(default=0, null=True)),
                ('product_image', models.ImageField(upload_to='arts/')),
                ('dimension_unit', models.CharField(choices=[('cm', 'Centimeters'), ('ft', 'Feet')], max_length=10)),
                ('length_in_centimeters', models.FloatField(blank=True, default=0, null=True)),
                ('width_in_centimeters', models.FloatField(blank=True, default=0, null=True)),
                ('foot', models.FloatField(blank=True, default=0, null=True)),
                ('inches', models.FloatField(blank=True, default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateField(blank=True, db_index=True, null=True)),
                ('is_sold', models.BooleanField(default=False)),
                ('is_purchased', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('active', 'Active'), ('closed', 'Closed'), ('waiting_for_response', 'Waiting for Response'), ('unsold', 'Unsold')], default='active', max_length=50)),
                ('response_deadline', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('buyer_response', models.CharField(choices=[('yes', 'Yes'), ('no', 'No'), ('no_response', 'No Response')], default='no_response', max_length=11)),
                ('discounted_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('favorited_by', models.ManyToManyField(blank=True, related_name='favorite_artworks', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product_cat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.catalogue')),
                ('purchase_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.purchasecategory')),
            ],
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid_date', models.DateField(auto_now_add=True)),
                ('bid_amt', models.IntegerField(default=1)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='dashboard.artwork')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.artwork')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateField(auto_now_add=True)),
                ('order_qty', models.IntegerField(default=0)),
                ('delivery_at', models.TextField(default=' ')),
                ('order_price', models.FloatField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.artwork')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('status', models.CharField(default='Pending', max_length=254, verbose_name='Payment Status')),
                ('provider_order_id', models.CharField(max_length=40, verbose_name='Order ID')),
                ('payment_id', models.CharField(max_length=36, verbose_name='Payment ID')),
                ('signature_id', models.CharField(max_length=128, verbose_name='Signature ID')),
                ('payment_method', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.ordermodel')),
            ],
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refunded_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processed', 'Processed')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.ordermodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Shipping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('processing', 'Processing'), ('shipped', 'Shipped'), ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='processing', max_length=20)),
                ('tracking_number', models.CharField(blank=True, max_length=100, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='shipping', to='dashboard.ordermodel')),
            ],
        ),
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction_type', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('artwork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.artwork')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('artwork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.artwork')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'artwork')},
            },
        ),
    ]
