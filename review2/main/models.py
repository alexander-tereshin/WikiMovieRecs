from django.db import models


class Article(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.IntegerField()
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    summary = models.CharField(max_length=5000)

