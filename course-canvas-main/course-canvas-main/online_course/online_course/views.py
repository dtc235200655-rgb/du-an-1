from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout  # ← THIẾU DÒNG NÀY
from django.contrib.auth.models import User
from django.contrib import messages


def home(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Xác thực user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Xin chào {username}! Đăng nhập thành công.')
            return redirect('courses:dashboard')    
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
            return redirect('login')
    
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate
        if password != confirm_password:
            messages.error(request, 'Mật khẩu không khớp!')
            return redirect('register')
        
        if len(password) < 8:
            messages.error(request, 'Mật khẩu phải có ít nhất 8 ký tự!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại!')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã được sử dụng!')
            return redirect('register')
        
        # Tạo user mới
        try:
            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return redirect('register')
    
    return render(request, 'register.html')