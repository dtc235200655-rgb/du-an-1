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
                actual_role = user.user_role.role
                
                # ✅ YÊU CẦU: Chọn đúng role mới được đăng nhập
                if selected_role != actual_role:
                    # Hiển thị lỗi rõ ràng với hướng dẫn
                    role_names = dict(UserRole.ROLE_CHOICES)
                    messages.error(
                        request,
                        f'⚠️ Vai trò không khớp!\n\n'
                        f'Tài khoản <strong>{username}</strong> có vai trò thực tế là: '
                        f'<span class="badge bg-success">{role_names.get(actual_role)}</span>\n\n'
                        f'Bạn đã chọn: <span class="badge bg-danger">{role_names.get(selected_role)}</span>\n\n'
                        f'💡 Vui lòng chọn đúng <strong>"{role_names.get(actual_role)}"</strong> và thử lại.'
                    )
                    return render(request, 'login.html', {
                        'selected_role': selected_role,
                        'role_choices': UserRole.ROLE_CHOICES
                    })
                
                # ✅ Đăng nhập thành công khi chọn đúng role
                login(request, user)
                messages.success(request, f'✅ Xin chào {username}! Đăng nhập thành công với vai trò {user.user_role.get_role_display()}.')
                
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
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        terms_accepted = request.POST.get('terms') == 'on'
        
        # Lưu lại dữ liệu đã nhập để hiển thị lại
        form_data = {
            'username': username,
            'email': email,
        }
        
        # Validate chi tiết
        form_errors = {}
        
        # Kiểm tra username
        if not username:
            form_errors['username'] = ['Tên đăng nhập không được để trống.']
        elif len(username) < 4:
            form_errors['username'] = ['Tên đăng nhập phải có ít nhất 4 ký tự.']
        elif len(username) > 50:
            form_errors['username'] = ['Tên đăng nhập không được vượt quá 50 ký tự.']
        elif not all(c.isalnum() or c == '_' for c in username):
            form_errors['username'] = ['Tên đăng nhập chỉ được chứa chữ, số và dấu gạch dưới.']
        elif User.objects.filter(username=username).exists():
            form_errors['username'] = ['Tên đăng nhập này đã được sử dụng. Vui lòng chọn tên khác.']
        
        # Kiểm tra email
        if not email:
            form_errors['email'] = ['Email không được để trống.']
        elif '@' not in email or '.' not in email:
            form_errors['email'] = ['Email không hợp lệ. Ví dụ: name@example.com']
        elif len(email) > 254:
            form_errors['email'] = ['Email quá dài (tối đa 254 ký tự).']
        elif User.objects.filter(email=email).exists():
            form_errors['email'] = ['Email này đã được đăng ký. Vui lòng dùng email khác.']
        
        # Kiểm tra password
        if not password:
            form_errors['password'] = ['Mật khẩu không được để trống.']
        elif len(password) < 8:
            form_errors['password'] = ['Mật khẩu phải có ít nhất 8 ký tự.']
        elif len(password) > 128:
            form_errors['password'] = ['Mật khẩu không được vượt quá 128 ký tự.']
        
        # Kiểm tra confirm password
        if not confirm_password:
            form_errors['confirm_password'] = ['Vui lòng xác nhận mật khẩu.']
        elif password and confirm_password != password:
            form_errors['confirm_password'] = ['Mật khẩu xác nhận không khớp. Vui lòng nhập lại.']
        
        # Kiểm tra terms
        if not terms_accepted:
            form_errors['terms'] = ['Bạn phải đồng ý với Điều khoản dịch vụ và Chính sách bảo mật.']
        
        # Nếu có lỗi, hiển thị lại form
        if form_errors:
            messages.error(
                request,
                '<div class="fw-bold">⚠️ Đăng ký không thành công. Vui lòng kiểm tra lại thông tin!</div>'
            )
            return render(request, 'register.html', {
                'form_errors': form_errors,
                'form_data': form_data
            })
        
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
            
            messages.success(
                request,
                f'✅ <strong>Đăng ký thành công!</strong><br>'
                f'Tài khoản <strong>{username}</strong> đã được tạo.<br>'
                f'Vui lòng <a href="/login/" class="alert-link">đăng nhập</a> để tiếp tục.'
            )
            return redirect('login')
        except Exception as e:
            messages.error(
                request,
                f'❌ Có lỗi xảy ra: {str(e)}.<br>Vui lòng thử lại hoặc liên hệ hỗ trợ.'
            )
            return render(request, 'register.html', {
                'form_errors': {'__all__': [str(e)]},
                'form_data': form_data
            })
    
    # GET request - hiển thị form rỗng
    return render(request, 'register.html', {
        'form_errors': None,
        'form_data': None
    })