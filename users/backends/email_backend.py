from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http.request import HttpRequest

User=get_user_model()


class EmailAuthBackend(ModelBackend):
    
    def authenticate(self,request,username=None,password=None):
        try:
            user= User.objects.get(email=username)
            if user.check_password(password):
                return user
            return
        except User.DoesNotExist:
            return
    
    def get_user(self,user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None