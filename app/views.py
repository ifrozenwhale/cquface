import os
import random
import uuid
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as au
from django.core.paginator import Paginator
from django.http import JsonResponse

from rest_framework import viewsets
from rest_framework.authtoken.models import Token

from app import models, serialize
from app.models import Photo, User, Favorites, Comments, Follow

from aip import AipFace

# 登录百度api的账号
APP_ID = '20710958'
API_KEY = 'l3lZkbn9qtIihUcnLZT1XYO3'
SECRET_KEY = '6ouePthZFFPAD9ctBuVHHlHilKkaHNcg'

client = AipFace(APP_ID, API_KEY, SECRET_KEY)


class AppViewSet(viewsets.ModelViewSet):
    serializer_class = serialize.UserSerializer

    # 人脸识别功能模块
    def recognition(self, request):
        # 读取请求
        BASE64 = request.data.get("image")
        account = request.data.get("account")
        imageName = uuid.uuid1()
        # token认证
        getToken = request.META.get("HTTP_AUTHORIZATION")
        user = User.objects.get(account=account)
        user_id = user.user_id
        key = Token.objects.get(user_id=user_id).key
        if getToken != key:
            return JsonResponse({'status': 405, 'msg': "token验证失败"})
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
        # 存入数据库
        user = User.objects.get(account=account)
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
        Photo.base64 = base64LocalAbsPath
        Photo.date = str(datetime.now())
        Photo.account = user
        Photo.save()
        #  得到数据库生成的图片id
        photo_id = Photo.photo_id
        result["photo_id"] = photo_id
        return JsonResponse(result)

    # 分享照片
    def share(self, request):
        # 读取请求
        account = request.data.get("account")
        photo_id = request.data.get("photo_id")
        public = request.data.get("public")
        share_info = request.data.get("content")
        # token认证
        getToken = request.META.get("HTTP_AUTHORIZATION")
        user = User.objects.get(account=account)
        user_id = user.user_id
        key = Token.objects.get(user_id=user_id).key
        if getToken != key:
            return JsonResponse({'status': 405, 'msg': "token验证失败"})
        res = {'status': 200, 'msg': ''}
        # 图片查找失败：返回错误码
        Photo = models.Photo
        try:
            photo = Photo.objects.filter(photo_id=photo_id)
        except User.DoesNotExist:
            photo = None
        if not photo:
            res['status'] = 401
            res['msg'] = '照片不存在'
            return JsonResponse(res)
        # 成功：将数据写进数据库
        Photo.objects.filter(photo_id=photo_id).update(public=public, share_info=share_info)
        return JsonResponse(res)

    # 返回粉丝信息列表
    def showFans(self, request, account):
        # 读取请求
        account = account
        Follow = models.Follow
        User = models.User
        objs = Follow.objects.filter(followed_account = account)
        # token认证
        getToken = request.META.get("HTTP_AUTHORIZATION")
        user = User.objects.get(account=account)
        user_id = user.user_id
        key = Token.objects.get(user_id=user_id).key
        if getToken != key:
            return JsonResponse({'status': 405, 'msg': "token验证失败"})
        # 返回粉丝列表
        fans = []
        for obj in objs:
            fan = {}
            fan["signature"] = User.objects.get(account=obj.follower_account.account).sig
            fan["nickname"] = User.objects.get(account=obj.follower_account.account).username
            headAbsPath = User.objects.get(account=obj.follower_account.account).head
            BASE64 = ""
            if headAbsPath != "":
                f = open(headAbsPath)
                BASE64 = f.read()
                f.close()
            fan["portrait"] = BASE64
            fan["account"] = obj.follower_account.account
            fans.append(fan)
        return JsonResponse(fans, safe=False)

    # 返回关注列表
    def showFollows(self, request, account):
        # 读取请求
        account = account
        Follow = models.Follow
        User = models.User
        objs = Follow.objects.filter(follower_account = account)
        # token认证
        getToken = request.META.get("HTTP_AUTHORIZATION")
        user = User.objects.get(account=account)
        user_id = user.user_id
        key = Token.objects.get(user_id=user_id).key
        if getToken != key:
            return JsonResponse({'status': 405, 'msg': "token验证失败"})
        # 关注列表
        follows = []
        for obj in objs:
            follow = {}
            follow["signature"] = User.objects.get(account = obj.followed_account.account).sig
            follow["nickname"] = User.objects.get(account = obj.followed_account.account).username
            headAbsPath = User.objects.get(account = obj.followed_account.account).head
            BASE64 = ""
            if headAbsPath != "":
                f = open(headAbsPath)
                BASE64 = f.read()
                f.close()
            follow["portrait"] = BASE64
            follow["account"] = obj.followed_account.account
            follows.append(follow)
        return JsonResponse(follows, safe=False)

    # 查看他人分享
    # 别人主页不用登录token
    def showOthersShared(self, request, account):
        # 查询数据库
        Photo = models.Photo
        photos = Photo.objects.filter(account=account, public=True)
        # 返回分享信息
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
        # 读取请求
        account = request.data.get("account")
        account_other = request.data.get("account_other")
        # token认证
        getToken = request.META.get("HTTP_AUTHORIZATION")
        user = User.objects.get(account=account)
        user_id = user.user_id
        key = Token.objects.get(user_id=user_id).key
        if getToken != key:
            return JsonResponse({'status': 405, 'msg': "token验证失败"})
        # 查询数据库
        relation = models.Follow.objects.filter(follower_account=account, followed_account=account_other)
        # 关注与取关
        Follow = models.Follow()
        if len(relation) == 0:
            Follow.follower_account = User.objects.get(account=account)
            Follow.followed_account = User.objects.get(account=account_other)
            Follow.save()
            return JsonResponse({"status": 1})    # 状态码为1，表示关注成功
        elif len(relation) == 1:
            relation.delete()
            return JsonResponse({"status": 0})    # 状态码为0，表示取关成功
        else:
            return JsonResponse({"status": -1})  # 状态码为-1，表示异常

    """
    qyCode
    """

    # 随机推送
    def get_shares(self, request, user_id, share_num):
        # 读取数据库
        user_now = User.objects.get(account=user_id)
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
            dict['comment_num'] = len(Comments.objects.filter(photo_id=shares[i]))
            dict['favorite_num'] = len(Favorites.objects.filter(photo_id=shares[i]))
            head_path = user.head
            dict['portrait'] = ""
            if head_path != "":
                with open(head_path, "r") as f:
                    dict['portrait'] = f.read()
            dict['nickname'] = user.username
            dict['signature'] = user.sig
            dict['age'] = shares[i].age
            dict['gender'] = shares[i].gender
            dict['expression'] = shares[i].expression
            dict['emotion'] = shares[i].emotion
            dict['score'] = shares[i].beauty
            dict['user_id'] = user.user_id
            if len(Favorites.objects.filter(account=user_now, photo_id=shares[i])) != 0:
                dict['is_favorites'] = True
            else:
                dict['is_favorites'] = False
            share_data.append(dict)
        return JsonResponse(share_data, safe=False)

    # 得到收藏信息
    def get_favorites(self, request, user_id):
        # 读取数据库
        user = User.objects.get(account=user_id)
        favorites = Favorites.objects.filter(account=user)
        # token认证
        getToken = request.META.get("HTTP_AUTHORIZATION")
        user_id = user.user_id
        key = Token.objects.get(user_id=user_id).key
        if getToken != key:
            return JsonResponse({'status': 405, 'msg': "token验证失败"})
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
            dict['age'] = photo.age
            dict['report_name'] = user.username
            dict['report_time'] = photo.date
            dict['report_text'] = photo.share_info
            dict['account'] = photo.account.account
            favorites_data.append(dict)
        return JsonResponse(favorites_data, safe=False)

        # 得到详情页
        # 不用登录token

    def get_share_info(self, request, user_id, photo_id, user_now):
        # 读取数据库
        user = User.objects.get(user_id=user_id)
        photo = Photo.objects.get(photo_id=photo_id)
        # 获取数据
        dict = {}
        # 获取图片数据
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
        dict['comment_num'] = len(Comments.objects.filter(photo_id=photo_id))
        dict['favorite_num'] = len(Favorites.objects.filter(photo_id=photo_id))
        if len(Favorites.objects.filter(account=user_now, photo_id=photo_id)) != 0:
            dict['is_favorites'] = True
        else:
            dict['is_favorites'] = False
        # 获取用户数据
        head_path = user.head
        if head_path != "":
            with open(head_path, "r") as f:
                dict['portrait'] = f.read()
        dict['nickname'] = user.username
        dict['signature'] = user.sig
        # 获取评论信息
        comments_info = []
        for comment in Comments.objects.filter(photo_id=photo):
            comment_info = {}
            commenter = comment.account
            head_path = commenter.head
            if head_path != "":
                with open(head_path, "r") as f:
                    comment_info['portrait'] = f.read()
            comment_info['name'] = commenter.username
            comment_info['cont'] = comment.comment
            comment_info[
                'avator'] = 'https://avataaars.io/?avatarStyle=Transparent&topType=ShortHairShortCurly&accessoriesType=Prescription02&hairColor=Black&facialHairType=Blank&clotheType=Hoodie&clotheColor=White&eyeType=Default&eyebrowType=DefaultNatural&mouthType=Default&skinColor=Light'
            comments_info.append(comment_info)
        dict['comments_info'] = comments_info
        return JsonResponse(dict)




    # 收藏|取消收藏
    def star(self, request):
        # 读取请求
        account = request.data.get('account')
        photo_id = request.data.get('photo_id')
        # token认证
        getToken = request.META.get("HTTP_AUTHORIZATION")
        user = User.objects.get(account=account)
        user_id = user.user_id
        key = Token.objects.get(user_id=user_id).key
        if getToken != key:
            return JsonResponse({'status': 405, 'msg': "token验证失败"})
        # 查询数据库
        res = {'status': 0, 'msg': ''}
        try:
            user = User.objects.get(account=account)
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
        # 查询是否收藏
        if len(Favorites.objects.filter(account=user, photo_id=photo)) != 0:
            # 取消收藏
            Favorites.objects.filter(account=user, photo_id=photo).delete()
        else:
            # 收藏并存入数据库
            favorite = Favorites()
            favorite.account = user
            favorite.photo_id = photo
            favorite.save()
        return JsonResponse(res)

    # 评论
    def comment(self, request):
        # 读取请求
        account = request.data.get('user_id')
        photo_id = request.data.get('photo_id')
        comment_text = request.data.get('comment_text')
        # token认证
        getToken = request.META.get("HTTP_AUTHORIZATION")
        user = User.objects.get(account=account)
        user_id = user.user_id
        key = Token.objects.get(user_id=user_id).key
        if getToken != key:
            return JsonResponse({'status': 405, 'msg': "token验证失败"})
        # 查询数据库
        res = {'status': 0, 'msg': ''}
        try:
            user = User.objects.get(account=account)
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
        sig = request.data.get('sig')  # 获取个性签名
        email = request.data.get('email')  # 获取邮箱
        # head64 = request.data.get('head')  # 获取头像的base64编码
        head64 = ""
        # 写入编码
        # basepath = 'app/static/files/base64TXT/head'
        # if not os.path.exists(basepath):  # 如果目录不存在则创建
        #     os.mkdir(basepath)
        # uname = str(uuid.uuid1()) + '.txt'  # 产生唯一的文件名
        # # 文件的路径
        # baseapath = basepath + os.sep + uname
        # if head64 is not None and head64 != "":
        #     # 写txt文件
        #     with open(baseapath, 'w+') as ff:
        #         ff.write(head64)
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
        # 如果登录失败，返回错误提示信息
        else:
            res['status'] = 401
            res['msg'] = '用户名或密码错误，请重试'
        # 创建新的Token
        token = Token.objects.create(user=user)
        res['token'] = token.key
        return JsonResponse(res)

    def logout(self, request):
        account = request.data.get('account')
        res = {'status': 200}
        # 清除session中的登录信息
        logout(request)
        # 删除token
        user = User.objects.get(account=account)
        old_token = Token.objects.filter(user_id=user.user_id)
        old_token.delete()
        return JsonResponse(res)

    # 获取我的个人信息
    def get_my_info(self, request):
        # 读取请求
        account = request.data.get('account')  # 首先获取当前登录用户的账号
        me = User.objects.get(account=account)  # 在数据库中查询该用户
        data = dict()  # 存放个人信息用于返回
        # token认证
        getToken = request.META.get("HTTP_AUTHORIZATION")
        print(getToken)
        user = User.objects.get(account=account)
        user_id = user.user_id
        key = Token.objects.get(user_id=user_id).key
        if getToken != key:
            return JsonResponse({'status': 405, 'msg': "token验证失败"})
        # 返回数据
        data['nickname'] = me.username
        data['signature'] = me.sig
        data['gender'] = me.gender
        data['email'] = me.email
        data['QQ'] = me.qq
        data['city'] = me.cities
        data['age'] = me.age
        # 获取头像的base64编码
        data['portrait'] = ""
        if me.head != "":
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
        # 读取请求
        account = request.data.get('account')  # 获取当前登录用户的账号
        nickname = request.data.get('nickname')  # 获取昵称（用户名）
        signature = request.data.get('signature')  # 获取个性签名
        email = request.data.get('email')  # 获取email
        QQ = request.data.get('QQ')  # 获取qq
        city = request.data.get('city')  # 获取城市

        # token认证
        getToken = request.META.get("HTTP_AUTHORIZATION")
        user = User.objects.get(account=account)
        user_id = user.user_id
        key = Token.objects.get(user_id=user_id).key
        if getToken != key:
            return JsonResponse({'status': 405, 'msg': "token验证失败"})

        # 更新该用户的信息
        User.objects.filter(account=account).update(
            username=nickname,
            sig=signature,
            email=email,
            qq=QQ,
            cities=city,
        )
        return JsonResponse({'status': 200})



    def get_my_portrait(self, request, account):
        me = User.objects.get(account=account)  # 在数据库中查询该用户
        data = dict()  # 存放个人信息用于返
        # 获取头像的base64编码

        # 获取头像的base64编码
        print(me.head)
        if me.head is not None and me.head != '':
            with open(me.head, 'r+') as f:
                portrait = f.read()
        else:
            portrait = None
        data['portrait'] = portrait
        return JsonResponse(data)

    def update_my_portrait(self, request):
        account = request.data.get("account")
        print(account)
        b64 = request.data.get('portrait')  # 获取头像文件的base64编码
        basepath = self.update_head_help(b64)
        # 更新该用户的信息
        print(b64)
        User.objects.filter(account=account).update(
            head=basepath
        )
        res = {"status": 200}
        return JsonResponse(res)


    def update_head_help(self, b64):
        # b64 = request.data.get('portrait')  # 获取头像文件的base64编码
        basepath = 'app/static/files/base64TXT/head'
        if not os.path.exists(basepath):  # 如果目录不存在则创建
            os.mkdir(basepath)
        uname = str(uuid.uuid1()) + '.txt'  # 产生唯一的文件名
        # 文件的绝对路径
        baseapath = basepath + os.sep + uname
        # 写txt文件
        with open(baseapath, 'w+') as ff:
            ff.write(b64)
        return baseapath

    def get_shared_by_account(self, request, account):
        share_data = []
        photo_list = Photo.objects.filter(account_id=account).order_by('-date')
        single_num = int(request.GET.get("each"))
        page_num = int(request.GET.get("page"))
        paginator = Paginator(photo_list, single_num)
        photos = paginator.page(page_num)


        # 获取数据
        for i in range(single_num):
            if i >= len(photos):
                break
            dict = {}
            photo_path = photos[i].base64
            with open(photo_path, "r+") as f:
                dict['report_picture'] = f.read()
            user = User.objects.get(account=photos[i].account.account)
            dict['photo_id'] = photos[i].photo_id
            dict['report_name'] = user.username
            dict['report_time'] = photos[i].date
            dict['report_text'] = photos[i].share_info
            dict['total_num'] = paginator.num_pages

            share_data.append(dict)
        return JsonResponse(share_data, safe=False)


    def delete_photo(self, request, photo_id):
        Photo.objects.filter(photo_id=photo_id).delete()
        res = dict()
        res['status'] = 200
        res['msg'] = 'ok'
        return JsonResponse(res)


    def get_fan_follow_collect(self, request, account):
        me = User.objects.get(account=account)  # 在数据库中查询该用户
        data = dict()  # 存放个人信息用于返回

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

