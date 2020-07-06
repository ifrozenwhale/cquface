import base64
import os
import random
import uuid
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from aip import AipFace

from app import models


from rest_framework import viewsets



# 登录百度api的账号
from app.models import Photo, User, Favorites, Comments

APP_ID = '20710958'
API_KEY = 'l3lZkbn9qtIihUcnLZT1XYO3'
SECRET_KEY = '6ouePthZFFPAD9ctBuVHHlHilKkaHNcg'

client = AipFace(APP_ID, API_KEY, SECRET_KEY)

# Create your views here.



class AppViewSet(viewsets.ModelViewSet):
            # 人脸识别功能模块
            @login_required
            def recongnition(self, request):
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
                base64LocalAbsPath = "static/files/base64TXT/local" + os.sep + str(imageName) + ".txt"
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
                result["beauty"] = dict["face_list"][0]["beauty"]
                result["expression"] = dict["face_list"][0]["expression"]
                result["gender"] = dict["face_list"][0]["gender"]
                result["face_shape"] = dict["face_list"][0]["face_shape"]
                result["glasses"] = dict["face_list"][0]["glasses"]
                result["emotion"] = dict["face_list"][0]["emotion"]
                result["race"] = dict["face_list"][0]["race"]
                result["face_width"] = dict["face_list"][0]["location"]["width"]
                result["face_height"] = dict["face_list"][0]["location"]["height"]

                # 将识别信息写入数据库
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

                Photo.save()

                # 反过来将数据库中生成的photo_id提取出来作为result
                photo_id = Photo.photo_id
                result["photo_id"] = photo_id

                # 打印测试
                for key in result.keys():
                    print(key, ":", result[key])

                # 将其他信息写入数据库
                Photo.base64 = base64LocalAbsPath
                Photo.date = datetime.now()
                Photo.account = account

                return JsonResponse(result)

            @login_required
            def share(self, request):
                account = request.data.get["user_id"]
                photo_id = request.data.get["photo_id"]
                public = request.data.get["public"]
                share_info = request.data.get["content"]

                res = {'status': 0, 'msg': ''}

                Photo = models.Photo()
                # 失败：返回错误码
                if len(Photo.objects.filter(photo_id = photo_id)) == 0:
                    res['status'] = 404
                    res['msg'] = "照片不存在"
                    return JsonResponse(res)

                # 成功：将数据写进数据库
                Photo.objects.filter(photo_id = photo_id).update(public = public, share_info = share_info)

            @login_required
            def showFans(self, request, user_id):
                account = user_id
                Follow = models.Follow()
                User = models.User()
                objs = Follow.objects.filter(followed_account = account)

                # 粉丝列表
                fans = []
                for obj in objs:
                    fan = {}
                    fan["signature"] = User.objects.get(obj["account"]).sig
                    fan["nickname"] = User.objects.get(obj["account"]).username
                    headAbsPath = User.objects.get(obj["account"]).head
                    f = open(headAbsPath)
                    BASE64 = f.read()
                    fan["portrait"] = BASE64
                    fans.append(fan)

                return JsonResponse(fans, safe=False)

            @login_required
            def showFollows(self, request, user_id):
                account = user_id
                Follow = models.Follow()
                User = models.User()
                objs = Follow.objects.filter(followerer_account = account)

                # 关注列表
                follows = []
                for obj in objs:
                    follow = {}
                    follow["signature"] = User.objects.get(obj["account"]).sig
                    follow["nickname"] = User.objects.get(obj["account"]).username
                    headAbsPath = User.objects.get(obj["account"]).head
                    f = open(headAbsPath)
                    BASE64 = f.read()
                    follow["portrait"] = BASE64
                    follows.append(follow)

                return JsonResponse(follows, safe=False)

            @login_required
            def showOthersShared(self, request, user_id):
                account = user_id
                Photo = models.Photo()
                photos = Photo.objects.get(account = account, public = True)

                dict = {}
                for photo in photos:

                    photo_path = photo.base64
                    f = open(photo_path)
                    BASE64 = f.read()

                    dict["base64"] = BASE64
                    dict['report_txt'] = photo.share_info
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
                    dict['photo_id'] = photo.photo_id
                return JsonResponse(dict, safe=False)

            @login_required
            def followAndUnfollow(self, request):
                user_id = request.data.get("user_id")
                user_id_other = request.data.get("user_id_other")

                Follow = models.Follow()

                relation = Follow.objects.filter(followed_account=user_id, follower_account=user_id_other)

                if len(relation) == 0:
                    Follow.objects.create   (followed_account=user_id, follower_account=user_id_other)
                    return JsonResponse({"status": 1})    # 状态码为1，表示关注成功
                elif len(relation) == 1:
                    relation.delete()
                    return JsonResponse({"status": 0})    # 状态码为0，表示取关成功
                else:
                    return JsonResponse({"status": -1}) # 状态码为-1，表示异常


            """
            qyCode
            """

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
                    with open(photo_path, "rb") as f:
                        dict['report_picture'] = f.read()
                    user = User.objects.get(account=shares[i].account)
                    dict['report_name'] = user.username
                    dict['report_time'] = shares[i].date
                    dict['report_text'] = shares[i].share_info
                    share_data.append(dict)
                return JsonResponse(share_data, safe=False)

            @login_required
            def get_favorites(self, request, user_id):
                # 读取数据库
                favorites = Favorites.objects.filter(account=user_id)
                # 获取数据
                favorites_data = []
                for i in favorites:
                    photo = Photo.objects.get(photo_id=i.photo_id)
                    dict = {}
                    photo_path = photo.base64
                    with open(photo_path, "rb") as f:
                        dict['report_picture'] = f.read()
                    user = User.objects.get(account=photo.account)
                    dict['report_name'] = user.username
                    dict['report_time'] = photo.date
                    dict['report_text'] = photo.share_info
                    favorites_data.append(dict)
                return JsonResponse(favorites_data, safe=False)

            def get_share_info(self, request, user_id, photo_id):
                # 读取数据库
                user = User.objects.get(account=user_id)
                photo = Photo.objects.get(photo_id=photo_id)
                # 获取数据
                dict = {}
                photo_path = photo.base64
                with open(photo_path, "rb") as f:
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
                with open(head_path, "rb") as f:
                    dict['portrait'] = f.read()
                dict['nickname'] = user.username
                dict['signature'] = user.sig
                return JsonResponse(dict)

            @login_required
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

            @login_required
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


























