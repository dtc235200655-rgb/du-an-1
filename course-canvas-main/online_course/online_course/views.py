from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout  # ← THIẾU DÒNG NÀY
from django.contrib.auth.models import User
from django.contrib import messages


def home(request):
    return render(request, 'index.html')


def login_view(request):
    from courses.models import UserRole  # Import at the beginning
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_role = request.POST.get('role', 'customer')  # Mặc định là customer
        
        # Xác thực user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Kiểm tra vai trò người dùng
            if hasattr(user, 'user_role'):
                user_role = user.user_role.role
                
                # Kiểm tra xem vai trò được chọn có khớp với vai trò thực tế không
                if selected_role != user_role:
                    messages.error(request, f'Tài khoản này không có vai trò {dict(UserRole.ROLE_CHOICES)[selected_role]}. Vai trò thực tế của bạn là {user.user_role.get_role_display()}.')
                    return render(request, 'login.html', {
                        'selected_role': selected_role,
                        'role_choices': UserRole.ROLE_CHOICES
                    })
                
                # Đăng nhập thành công
                login(request, user)
                messages.success(request, f'Xin chào {username}! Đăng nhập thành công với vai trò {user.user_role.get_role_display()}.')
                
                # Redirect theo vai trò
                redirect_url = user.user_role.get_role_redirect_url()
                return redirect(redirect_url)
            else:
                # User chưa có UserRole, gán mặc định là customer
                UserRole.objects.create(user=user, role='customer')
                login(request, user)
                messages.success(request, f'Xin chào {username}! Đăng nhập thành công.')
                return redirect('courses:dashboard')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
            return render(request, 'login.html', {
                'selected_role': selected_role,
                'role_choices': UserRole.ROLE_CHOICES
            })
    
    # GET request - hiển thị form
    return render(request, 'login.html', {
        'role_choices': UserRole.ROLE_CHOICES,
        'selected_role': 'customer'  # Mặc định chọn customer
    })


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
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Gán vai trò customer mặc định
            from courses.models import UserRole
            UserRole.objects.create(user=user, role='customer')
            
            messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return redirect('register')
    
    return render(request, 'register.html')