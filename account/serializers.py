from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('account', 'username', 'password', 'email', 'major')
        model = models.User
