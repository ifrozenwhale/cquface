from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# Create your views here.
from rest_framework import generics, viewsets, mixins

from account import serializers
from account.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_all(self, request):
        users = User.objects.all()
        s = serializers.UserSerializer(instance=users, many=True)
        return JsonResponse(s.data, safe=False)

    def get_by_account(self, request, account):
        user = User.objects.get(account=account)
        s = serializers.UserSerializer(instance=user)
        return JsonResponse(s.data)

    def add_one(self, request):
        account = request.data.get('account')
        username = request.data.get('username')
        password = request.data.get('password')
        major = request.data.get('major')
        email = request.data.get('email')
        user = User(account=account, password=password, username=username, major=major, email=email)
        user.save()
        return HttpResponse('OK')

    def login(self, request):
        account = request.data.get('account')
        password = request.data.get('password')
        res = {'status': 0, 'msg': ''}
        print(account)
        try:
            ua = User.objects.get(account=account)
        except User.DoesNotExist:
            ua = None
        if not ua:
            res['status'] = 401
            res['msg'] = '账号不存在'
            return JsonResponse(res)
        try:
            up = User.objects.get(account=account, password=password)
        except User.DoesNotExist:
            up = None
        if not up:
            res['status'] = 402
            res['msg'] = '密码错误'
            return JsonResponse(res)
        res['status'] = 200
        res['msg'] = 'OK'
        request.session['account'] = account
        # request.session['login'] = True
        request.session.set_expiry(24 * 60 * 60)
        return JsonResponse(res)

    def logout(self, request):
        res = {'status': 200}
        if request.session.get('account', None) is not None:
            print(request.session.get('account'))
            del request.session['account']
            # request.session.flush()
            return JsonResponse(res)
        return JsonResponse(res)

    def check_login_status(self, request):
        res = {'status': 0, 'msg': ''}
        if request.session.get('account', None) is not None:
            print(request.session.get('account'))
            res['status'] = 200
            res['msg'] = 'login before'
            return JsonResponse(res)
        else:
            res['status'] = 400
            res['msg'] = 'not login'
            return JsonResponse(res)




