from django.db import models

# Create your models here.

class Anime(models.Model):
    mal_id = models.IntegerField(null=True, blank=True)  # Nullable ve blank olarak belirledik
    english_name = models.CharField(max_length=255)
    genres = models.CharField(max_length=255)
    score = models.FloatField()
    popularity = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.english_name