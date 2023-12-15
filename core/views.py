from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
#from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse


def home(request):
    return render(request, 'home.html')

#def admins(request):
 #   admins = admin.objects.all()  # fetch the moderators from db
  #  response = AdminSerializer(admins, many=True)  # turning all of them into json
   # return JsonResponse({"admins": response.data})







