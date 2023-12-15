# Generated by Django 4.2 on 2023-12-15 18:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_remove_comment_user_email_remove_comment_user_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cartoon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('excerpt', models.CharField(blank=True, max_length=200, null=True)),
                ('slug', models.SlugField(unique=True)),
                ('date', models.DateField(auto_now=True)),
                ('tags', models.ManyToManyField(blank=True, to='blog.tag')),
            ],
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.CreateModel(
            name='CartoonPanel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='cartoons')),
                ('caption', models.TextField()),
                ('order', models.PositiveIntegerField(default=0)),
                ('cartoon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='panels', to='blog.cartoon')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
