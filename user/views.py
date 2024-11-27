

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
# from rest_framework.permissions import AllowAny





@api_view(['GET'])
@permission_classes([IsAuthenticated])



def user_profile(request):
    user = request.user
    if user.is_staff:
        return Response({"role": "staff", "redirect": "/yonetici-dashboard"})
    
def yonetici_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Kullanıcı kimlik doğrulama
        user = authenticate(request, username=username, password=password)

        if user:  # Kullanıcı doğrulandı
            if user.role == "admin":  # Yönetici rol kontrolü
                login(request, user)
                # return redirect("/user/yonetici/dashboard/")
            else:
                return HttpResponse("Bu sayfaya yalnızca yöneticiler giriş yapabilir.", status=403)
        else:
            return HttpResponse("Giriş başarısız! Kullanıcı adı veya şifre yanlış.", status=401)
    
    return render(request, "yonetici-login.html")



def personel_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Kullanıcı kimlik doğrulama
        user = authenticate(request, username=username, password=password)

        if user:  # Kullanıcı doğrulandı
            if user.role == "personel":  # Personel rol kontrolü
                login(request, user)
                return redirect("/user/personel/dashboard/")
            else:
                return HttpResponse("Bu sayfaya yalnızca personeller giriş yapabilir.", status=403)
        else:
            return HttpResponse("Giriş başarısız! Kullanıcı adı veya şifre yanlış.", status=401)
    
    return render(request, "personel-login.html")


def yonetici_dashboard(request):
    return render(request, "yonetici-dashboard.html")


def personel_dashboard(request):
    return render(request, "personel-dashboard.html")

def ofise_giris(request):
    return render(request, 'ofis-giris.html')#not planned