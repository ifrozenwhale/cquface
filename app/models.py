from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser


# 用户信息
class User(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    account = models.CharField(max_length=40, primary_key=True)  # 用户ID
    username = models.CharField(max_length=100)  # 用户名
    password = models.CharField(max_length=40)  # 密码
    gender = models.CharField(max_length=10, null=True)  # 性别
    cities = models.CharField(max_length=40, null=True)  # 城市
    age = models.CharField(max_length=40, null=True)  # 年龄
    qq = models.CharField(max_length=40, null=True)  # QQ
    sig = models.CharField(max_length=150, null=True)  # 个性签名
    email = models.CharField(max_length=40)  # 邮箱
    head = models.CharField(max_length=100, null=True)  # 头像的base64的txt文件的路径




# 照片信息
class Photo(models.Model):
    photo_id = models.AutoField(primary_key=True)  # 图片ID
    account = models.ForeignKey('User', on_delete=models.CASCADE)  # 用户ID

    age = models.CharField(max_length=3)  # 年龄
    glasses = models.BooleanField()  # 是否戴眼镜
    public = models.BooleanField()  # 是否公开
    emotion = models.CharField(max_length=20)  # 情绪
    date = models.CharField(max_length=50)  # 日期
    face_shape = models.CharField(max_length=20)  # 脸型
    expression = models.CharField(max_length=20)  # 表情
    base64 = models.CharField(max_length=100)  # base64的txt文件路径
    gender = models.CharField(max_length=10)  # 男：male   女：female
    beauty = models.FloatField()  # 颜值
    face_width = models.CharField(max_length=20)  # 面宽
    face_height = models.CharField(max_length=20)  # 面高
    race = models.CharField(max_length=20)  # 人种
    share_info = models.CharField(max_length=300)  # 分享评论
    image_name = models.CharField(max_length=100)


# 收藏夹
class Favorites(models.Model):
    account = models.ForeignKey('User', on_delete=models.CASCADE)  # 收藏者的用户ID
    photo_id = models.ForeignKey('Photo', on_delete=models.CASCADE)  # 被收藏的照片ID


# 他人对照片的评论
class Comments(models.Model):
    account = models.ForeignKey('User', on_delete=models.CASCADE)  # 评论者的用户ID
    photo_id = models.ForeignKey('Photo', on_delete=models.CASCADE)  # 被评论的照片ID
    comment = models.CharField(max_length=300)  # 评论语


# 关注列表
class Follow(models.Model):
    followed_account = models.ForeignKey('User', on_delete=models.CASCADE, related_name="fd")  # 被关注者的用户ID
    follower_account = models.ForeignKey('User', on_delete=models.CASCADE, related_name="fr")  # 关注者的用户ID
