from django.db import models

# Create your models here.
class User(models.Model):
    account = models.CharField(max_length=40, primary_key=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=40)
    email = models.CharField(max_length=40)
    major = models.CharField(max_length=40)

