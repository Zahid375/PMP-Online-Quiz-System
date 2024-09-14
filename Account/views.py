from django.shortcuts import render, redirect
from .models import CustomUser
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
# Create your views here.


def logInPage(request):
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            messages.success(request, "Login succesfully !")
            return redirect('/')
        else:
            messages.warning(request, "Something wrong")
            return redirect('account:login')
    return render(request, 'login.html')


def signUpPage(request):
    if request.POST:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = CustomUser.objects.filter(email=email)
        if not user.exists():
            user = CustomUser.objects.create(
                first_name=first_name, last_name=last_name, email=email, password=password)
            user.set_password(password)
            user.save()
            messages.success(request, "User Account Create succesfully ")
            return redirect('account:login')
        else:
            messages.success(request, "Already you have a account ")
            return redirect('account:signup')
    return render(request, 'signup.html')


def log_out(request):
    logout(request)
    return redirect('account:login')
