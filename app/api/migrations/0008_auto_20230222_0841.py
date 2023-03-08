# Generated by Django 3.2.18 on 2023-02-22 08:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_chessopening_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChessPuzzle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('moves', models.TextField()),
                ('theme', models.TextField()),
                ('url', models.URLField()),
                ('opening_fam', models.TextField()),
                ('opening_variation', models.TextField()),
                ('fen', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='puzzle', to='api.chessprocess')),
            ],
        ),
        migrations.DeleteModel(
            name='ChessPuzzles',
        ),
    ]
