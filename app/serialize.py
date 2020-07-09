from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'account',
            'username',
            'password',
            'gender',
            'cities',
            'age',
            'qq',
            'sig',
            'email',
            'head'
        )
        model = models.User


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'photo_id',
            'account',
            'age',
            'glasses',
            'public',
            'emotion',
            'date',
            'face_shape',
            'expression',
            'base64',
            'gender',
            'beauty',
            'share_info'
        )
        model = models.Photo


class FavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'account',
            'photo_id'
        )
        model = models.Favorites


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'account',
            'photo_id',
            'comment'
        )
        model = models.Comments


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'followed_account',
            'follower_account'
        )
        model = models.Follow

