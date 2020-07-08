import base64
import os
import random
import uuid
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as au

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from aip import AipFace

from app import models, serialize

from rest_framework import viewsets



# 登录百度api的账号
from app.models import Photo, User, Favorites, Comments, Follow

APP_ID = '20710958'
API_KEY = 'l3lZkbn9qtIihUcnLZT1XYO3'
SECRET_KEY = '6ouePthZFFPAD9ctBuVHHlHilKkaHNcg'

client = AipFace(APP_ID, API_KEY, SECRET_KEY)

# Create your views here.



class AppViewSet(viewsets.ModelViewSet):
    serializer_class = serialize.UserSerializer

    # 人脸识别功能模块
    def recognition(self, request):
        BASE64 = request.data.get("image")
        imageType = "BASE64"
        account = request.data.get("account")
        imageName = uuid.uuid1()


        #
        # # 根据不同的imageType得到BASE64
        # if imageType.equals("FILE"):
        #
        #     # 写入本地文件夹
        #     imageAbsPath = "/static/files/images/local" + os.sep + str(imageName)
        #     try:
        #         with open(imageAbsPath, "wb+") as fp:
        #             for chunk in image.chunk():
        #                 fp.write(chunk)
        #     except:
        #         return HttpResponse("人脸识别功能模块失败")
        #
        #     # 转成base64
        #     with open(imageAbsPath, 'rb') as f:
        #         base64_data = base64.b64encode(f.read())
        #         BASE64 = base64_data.decode()
        # else:
        # BASE64 = image

        # 将BASE64写入本地文件夹
        base64LocalAbsPath = "app/static/files/base64TXT/local" + os.sep + str(imageName) + ".txt"
        file = open(base64LocalAbsPath, 'w')
        file.write(BASE64)
        file.close()

        # 配置识别要求信息
        options = {}
        options["face_field"] = "age,beauty,expression,gender,face_shape,glasses,eye_status,emotion,race"
        options["max_face_num"] = 1
        options["face_type"] = "LIVE"
        options["liveness_control"] = "LOW"

        # 进行图像识别
        dict = client.detect(BASE64, "BASE64", options)['result']

        # 提取信息
        result = {}
        result["age"] = dict["face_list"][0]["age"]
        result["beauty"] = dict["face_list"][0]["beauty"] * 0.4 + 60
        result["expression"] = dict["face_list"][0]["expression"]["type"]
        result["gender"] = dict["face_list"][0]["gender"]["type"]
        result["face_shape"] = dict["face_list"][0]["face_shape"]["type"]
        if dict["face_list"][0]["glasses"]["type"]=='none':
            result["glasses"] = False
        else:
            result["glasses"] = True
        result["emotion"] = dict["face_list"][0]["emotion"]["type"]
        result["race"] = dict["face_list"][0]["race"]["type"]
        result["face_width"] = dict["face_list"][0]["location"]["width"]
        result["face_height"] = dict["face_list"][0]["location"]["height"]
        result["image_name"] = imageName
        # 打印测试
        for key in result.keys():
            print(key, ":", result[key])
        user = User.objects.get(account=account)

        # 将识别信息写入数据库
        # Photo = models.Photo()
        # Photo.age = result["age"]
        # Photo.beauty = result["beauty"]
        # Photo.expression = result["expression"]
        # Photo.gender = result["gender"]
        # Photo.face_shape = result["face_shape"]
        # Photo.glasses = result["glasses"]
        # Photo.emotion = result["emotion"]
        # Photo.race = result["race"]
        # Photo.face_height = result["face_height"]
        # Photo.face_width = result["face_width"]
        # Photo.image_name = imageName

        Photo = models.Photo()

        Photo.age = result["age"]
        Photo.beauty = result["beauty"]
        Photo.expression = result["expression"]
        Photo.gender = result["gender"]
        Photo.face_shape = result["face_shape"]
        Photo.glasses = result["glasses"]
        Photo.emotion = result["emotion"]
        Photo.race = result["race"]
        Photo.face_height = result["face_height"]
        Photo.face_width = result["face_width"]
        Photo.image_name = imageName
        Photo.public = True

        # Photo.save()

        # 反过来将数据库中生成的photo_id提取出来写进result
        # p = Photo.objects.get()




        # 将其他信息写入数据库
        Photo.base64 = base64LocalAbsPath

        Photo.date = str(datetime.now())
        # user = User.objects.get(account=account)
        Photo.account = user


        # Photo.account_id = user.user_id

        Photo.save()

        photo_id = Photo.photo_id
        result["photo_id"] = photo_id

        return JsonResponse(result)

    # 分享照片
    def share(self, request):
        # account = request.data.get("user_id")
        photo_id = request.data.get("photo_id")
        public = request.data.get("public")
        share_info = request.data.get("content")

        res = {'status': 200, 'msg': ''}
        Photo = models.Photo
        # 失败：返回错误码
        try:
            photo = Photo.objects.filter(photo_id=photo_id)
        except User.DoesNotExist:
            photo = None
        if not photo:
            res['status'] = 401
            res['msg'] = '照片不存在'
            return JsonResponse(res)
        # if len(Photo.objects.get(photo_id = photo_id)) == 0:
        #     res['status'] = 404
        #     res['msg'] = "照片不存在"
        #     return JsonResponse(res)

        # 成功：将数据写进数据库
        Photo.objects.filter(photo_id=photo_id).update(public = public, share_info = share_info)
        return JsonResponse(res)

    # 返回粉丝信息列表
    def showFans(self, request, account):
        account = account
        Follow = models.Follow
        User = models.User
        objs = Follow.objects.filter(followed_account = account)

        # 粉丝列表
        fans = []
        for obj in objs:
            fan = {}
            fan["signature"] = User.objects.get(account = obj.follower_account.account).sig
            fan["nickname"] = User.objects.get(account = obj.follower_account.account).username
            headAbsPath = User.objects.get(account = obj.follower_account.account).head
            f = open(headAbsPath)
            BASE64 = f.read()
            f.close()
            fan["portrait"] = BASE64
            fans.append(fan)

        return JsonResponse(fans, safe=False)

    # 返回关注列表
    def showFollows(self, request, account):
        account = account
        Follow = models.Follow
        User = models.User
        objs = Follow.objects.filter(follower_account = account)

        # 关注列表
        follows = []
        for obj in objs:
            follow = {}
            follow["signature"] = User.objects.get(account = obj.followed_account.account).sig
            follow["nickname"] = User.objects.get(account = obj.followed_account.account).username
            headAbsPath = User.objects.get(account = obj.followed_account.account).head
            f = open(headAbsPath)
            BASE64 = f.read()
            f.close()
            follow["portrait"] = BASE64
            follows.append(follow)

        return JsonResponse(follows, safe=False)

    # 查看他人分享
    def showOthersShared(self, request, account):
        account = account
        Photo = models.Photo
        photos = Photo.objects.filter(account = account, public = True)

        data = []
        for photo in photos:
            dict = {}
            photo_path = photo.base64
            f = open(photo_path)
            BASE64 = f.read()
            f.close()

            dict["base64"] = BASE64
            dict['content'] = photo.share_info
            dict['photo_id'] = photo.photo_id
            dict['age'] = photo.age
            dict['gender'] = photo.gender
            dict['expression'] = photo.expression
            dict['glasses'] = photo.glasses
            dict['beauty'] = photo.beauty
            dict['emotion'] = photo.emotion
            dict['race'] = photo.race
            dict['face_form'] = photo.face_shape
            dict['face_height'] = photo.face_height
            dict['face_width'] = photo.face_width
            dict['photo_id'] = photo.photo_id
            data.append(dict)
        return JsonResponse(data, safe=False)

    # 关注|取关
    def followAndUnfollow(self, request):
        account = request.data.get("account")
        account_other = request.data.get("account_other")


        relation = models.Follow.objects.filter(follower_account=account, followed_account=account_other)
        Follow = models.Follow()
        if len(relation) == 0:
            Follow.follower_account = User.objects.get(account = account)
            Follow.followed_account = User.objects.get(account = account_other)
            Follow.save()
            return JsonResponse({"status": 1})    # 状态码为1，表示关注成功
        elif len(relation) == 1:
            relation.delete()
            return JsonResponse({"status": 0})    # 状态码为0，表示取关成功
        else:
            return JsonResponse({"status": -1}) # 状态码为-1，表示异常


    """
    qyCode
    """

    # 随机推送
    def get_shares(self, request, share_num):
        # 读取数据库
        shares = Photo.objects.all()
        # 生成随机序列
        index = [i for i in range(len(shares))]
        random.shuffle(index)
        index = index[:(share_num if len(shares) > share_num else len(shares))]
        share_data = []
        # 获取数据
        for i in index:
            dict = {}
            photo_path = shares[i].base64
            with open(photo_path, "r+") as f:
                dict['report_picture'] = f.read()
            user = User.objects.get(account=shares[i].account.account)
            dict['photo_id'] = shares[i].photo_id
            dict['report_name'] = user.username
            dict['report_time'] = shares[i].date
            dict['report_text'] = shares[i].share_info
            share_data.append(dict)
        return JsonResponse(share_data, safe=False)

    # 得到收藏信息
    def get_favorites(self, request, user_id):
        # 读取数据库
        user = User.objects.get(account=user_id)
        favorites = Favorites.objects.filter(account=user)
        # 获取数据
        favorites_data = []
        for i in favorites:
            photo = Photo.objects.get(photo_id=i.photo_id.photo_id)
            dict = {}
            photo_path = photo.base64
            with open(photo_path, "r") as f:
                dict['report_picture'] = f.read()
            user = User.objects.get(account=photo.account.account)
            dict['photo_id'] = photo.photo_id
            dict['report_name'] = user.username
            dict['report_time'] = photo.date
            dict['report_text'] = photo.share_info
            favorites_data.append(dict)
        return JsonResponse(favorites_data, safe=False)

    # 得到详情页
    def get_share_info(self, request, user_id, photo_id):
        # 读取数据库
        user = User.objects.get(account=user_id)
        photo = Photo.objects.get(photo_id=photo_id)
        # 获取数据
        dict = {}
        photo_path = photo.base64
        with open(photo_path, "r") as f:
            dict['report_picture'] = f.read()
        dict['report_text'] = photo.share_info
        dict['photo_id'] = photo.photo_id
        dict['age'] = photo.age
        dict['gender'] = photo.gender
        dict['expression'] = photo.expression
        dict['glass'] = photo.glasses
        dict['score'] = photo.beauty
        dict['emotion'] = photo.emotion
        dict['race'] = photo.race
        dict['face_form'] = photo.face_shape
        dict['face_height'] = photo.face_height
        dict['face_width'] = photo.face_width
        head_path = user.head
        with open(head_path, "r") as f:
            dict['portrait'] = f.read()
        dict['nickname'] = user.username
        dict['signature'] = user.sig
        return JsonResponse(dict)

    # 收藏
    def star(self, request):
        # 读取请求
        user_id = request.data.get('user_id')
        photo_id = request.data.get('photo_id')
        # 查询数据库
        res = {'status': 0, 'msg': ''}
        try:
            user = User.objects.get(account=user_id)
        except User.DoesNotExist:
            user = None
        if not user:
            res['status'] = 401
            res['msg'] = '账号不存在'
            return JsonResponse(res)
        try:
            photo = Photo.objects.get(photo_id=photo_id)
        except Photo.DoesNotExist:
            photo = None
        if not photo:
            res['status'] = 401
            res['msg'] = '图片不存在'
            return JsonResponse(res)
        # 存入数据库
        favorite = Favorites()
        favorite.account = user
        favorite.photo_id = photo
        favorite.save()
        return JsonResponse(res)

    def comment(self, request):
        # 读取请求
        user_id = request.data.get('user_id')
        photo_id = request.data.get('photo_id')
        comment_text = request.data.get('comment_text')
        # 查询数据库
        res = {'status': 0, 'msg': ''}
        try:
            user = User.objects.get(account=user_id)
        except User.DoesNotExist:
            user = None
        if not user:
            res['status'] = 401
            res['msg'] = '账号不存在'
            return JsonResponse(res)
        try:
            photo = Photo.objects.get(photo_id=photo_id)
        except Photo.DoesNotExist:
            photo = None
        if not photo:
            res['status'] = 401
            res['msg'] = '图片不存在'
            return JsonResponse(res)
        # 存入数据库
        comment = Comments(comment=comment_text)
        comment.account = user
        comment.photo_id = photo
        comment.save()
        return JsonResponse(res)

    """
    lqpCode
    """

    # 添加一个新的用户
    def add_one(self, request):
        account = request.data.get('account')  # 获取账号
        # 判断账号是否已经存在
        users = User.objects.filter(account=account)
        if len(users) > 0:
            return JsonResponse({'status': 401, 'msg': '账号已存在！'})
        username = request.data.get('username')  # 获取用户名（昵称）
        password = request.data.get('password')  # 获取密码
        gender = request.data.get('gender')  # 获取性别
        cities = request.data.get('cities')  # 获取城市
        age = request.data.get('age')  # 获取年龄
        qq = request.data.get('qq')  # 获取qq
        # sig = request.data.get('signature')  # 获取个性签名
        sig = request.data.get('sig')  # 获取个性签名
        email = request.data.get('email')  # 获取邮箱
        # head64 = request.data.get('portrait')  # 获取头像的base64编码
        head64 = request.data.get('head')  # 获取头像的base64编码

        # 接下来将编码写入一个txt文件中
        # basepath = os.path.join(            # 文件保存目录
        #     os.getcwd(),
        #     'static/files/base64TXT/head'
        # )
        basepath = 'app/static/files/base64TXT/head'
        if not os.path.exists(basepath):  # 如果目录不存在则创建
            os.mkdir(basepath)
        uname = str(uuid.uuid1()) + '.txt'  # 产生唯一的文件名
        # 文件的路径
        baseapath = basepath + os.sep + uname
        # 写txt文件
        with open(baseapath, 'w+') as ff:
            ff.write(head64)
        # 生成一个新的user
        auu = au.objects.create_user(username=account, password=password)
        user = User(
            user_id=auu.id,
            account=account,
            username=username,
            password=password,
            gender=gender,
            cities=cities,
            age=age,
            qq=qq,
            sig=sig,
            email=email,
            head=baseapath
        )
        # 将新的user保存到User表中
        user.save()
        # 响应到前台
        return JsonResponse({'status': 200, 'msg': '注册成功'})

    # 登录
    def login(self, request):
        # 先获取前台传来的登录信息
        account = request.data.get('account')
        password = request.data.get('password')
        res = {'status': 0, 'msg': ''}
        # 去数据库进行用户的验证
        user = authenticate(username=account, password=password)
        # 如果认证成功，即用户名和密码都正确，则进行登录
        if user is not None:
            login(request, user)
            res['status'] = 200
            res['msg'] = '登陆成功'
            return JsonResponse(res)
        # 如果登录失败，返回错误提示信息
        else:
            res['status'] = 401
            res['msg'] = '用户名或密码错误，请重试'
            return JsonResponse(res)

    # 安全退出
    def logout(self, request):
        res = {'status': 200}
        # 清除session中的登录信息
        logout(request)
        return JsonResponse(res)

    # 获取我的个人信息
    def get_my_info(self, request):
        account = request.data.get('account')  # 首先获取当前登录用户的账号
        me = User.objects.get(account=account)  # 在数据库中查询该用户
        data = dict()  # 存放个人信息用于返回

        data['nickname'] = me.username
        data['signature'] = me.sig
        data['gender'] = me.gender
        data['email'] = me.email
        data['QQ'] = me.qq
        data['city'] = me.cities
        data['age'] = me.age

        # 获取头像的base64编码
        with open(me.head, 'r+') as f:
            portrait = f.read()
        data['portrait'] = portrait

        # 查询所有关注了该用户的记录并统计数量

        fans = Follow.objects.filter(followed_account=me)
        fan_num = len(fans)
        data['fan_num'] = fan_num

        # 查询该用户所有的关注记录并统计数量
        follows = Follow.objects.filter(follower_account=me)
        follow_num = len(follows)
        data['follow_num'] = follow_num

        # 查询该用户所有的收藏并统计数量
        favs = Favorites.objects.filter(account=me)
        collect_num = len(favs)
        data['collect_num'] = collect_num

        return JsonResponse(data)  # 响应到前台

    # 更新我的个人信息
    def update_my_info(self, request):
        account = request.data.get('account')  # 获取当前登录用户的账号
        nickname = request.data.get('nickname')  # 获取昵称（用户名）
        signature = request.data.get('signature')  # 获取个性签名
        gender = request.data.get('gender')  # 获取性别
        email = request.data.get('email')  # 获取email
        QQ = request.data.get('QQ')  # 获取qq
        city = request.data.get('city')  # 获取城市
        age = request.data.get('age')
        b64 = request.data.get('portrait')  # 获取头像文件的base64编码

        # 接下来将编码写入一个txt文件中
        # basepath = os.path.join(            # 文件保存目录
        #     os.getcwd(),
        #     'static/files/base64TXT/head'
        # )
        basepath = 'app/static/files/base64TXT/head'
        if not os.path.exists(basepath):  # 如果目录不存在则创建
            os.mkdir(basepath)
        uname = str(uuid.uuid1()) + '.txt'  # 产生唯一的文件名
        # 文件的绝对路径
        baseapath = basepath + os.sep + uname
        # 写txt文件
        with open(baseapath, 'w+') as ff:
            ff.write(b64)

        # 更新该用户的信息
        User.objects.filter(account=account).update(
            head=baseapath,
            username=nickname,
            sig=signature,
            gender=gender,
            email=email,
            qq=QQ,
            cities=city,
            age=age
        )
        return JsonResponse({'status': 200})

























