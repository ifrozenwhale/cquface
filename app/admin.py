from django.contrib import admin

# Register your models here.
from app.models import Follow, Comments, Favorites, Photo, User

admin.site.register([User, Photo, Favorites, Comments, Follow])