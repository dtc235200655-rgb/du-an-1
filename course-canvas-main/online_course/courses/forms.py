from django import forms
from django.contrib import admin
from .models import Course, Category, Enrollment, Review
from .utils import ImageValidator, validate_image_file


class CourseAdminForm(forms.ModelForm):
    """Form tùy chỉnh cho Course Admin với validation file"""
    
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'vTextField'}),
            'description': forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'vIntegerField'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm help text cho trường image
        self.fields['image'].help_text = 'Định dạng: JPG, PNG, GIF, WEBP. Kích thước tối đa: 5MB. Tỷ lệ đề xuất: 16:9'
    
    def clean_image(self):
        """Kiểm tra file ảnh trước khi lưu"""
        image = self.cleaned_data.get('image')
        
        if image:
            # Validate file
            errors = validate_image_file(image)
            if errors:
                raise forms.ValidationError(errors)
            
            # Kiểm tra thêm với ImageValidator
            validator = ImageValidator(max_size_mb=5)
            try:
                validator(image)
            except Exception as e:
                raise forms.ValidationError(str(e))
        
        return image
    
    def clean_price(self):
        """Kiểm tra giá phải >= 0"""
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Giá không được nhỏ hơn 0')
        return price
    
    def clean(self):
        """Kiểm tra tổng thể"""
        cleaned_data = super().clean()
        
        # Kiểm tra nếu trạng thái là approved thì phải có ảnh
        status = cleaned_data.get('status')
        image = cleaned_data.get('image')
        
        if status == 'approved' and not image:
            raise forms.ValidationError('Khóa học được duyệt phải có ảnh minh họa')
        
        return cleaned_data


class EnrollmentAdminForm(forms.ModelForm):
    """Form tùy chỉnh cho Enrollment Admin"""
    
    class Meta:
        model = Enrollment
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        course = cleaned_data.get('course')
        
        # Kiểm tra không cho đăng ký khóa học của chính mình
        if user and course and course.created_by == user:
            raise forms.ValidationError('Không thể đăng ký khóa học do chính bạn tạo')
        
        return cleaned_data


class ReviewAdminForm(forms.ModelForm):
    """Form tùy chỉnh cho Review Admin"""
    
    class Meta:
        model = Review
        fields = '__all__'
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
            'admin_reply': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm help text cho trường image
        if 'image' in self.fields:
            self.fields['image'].help_text = 'Định dạng: JPG, PNG, GIF, WEBP. Tối đa 3MB. Kích thước đề xuất: 50x50 đến 2000x2000 pixels'
    
    def clean_rating(self):
        """Kiểm tra rating từ 1-5"""
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError('Đánh giá phải từ 1 đến 5 sao')
        return rating
    
    def clean_image(self):
        """Kiểm tra ảnh đính kèm đánh giá"""
        image = self.cleaned_data.get('image')
        if image:
            from .utils import validate_review_image
            errors = validate_review_image(image)
            if errors:
                raise forms.ValidationError(errors)
        return image


# =========== FORM CHO USER SUBMISSIONS ===========

class CourseCreateForm(forms.ModelForm):
    """Form cho người dùng tạo khóa học mới"""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'price', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tên khóa học'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Mô tả chi tiết khóa học'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'step': '1000'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Set status mặc định là draft
        self.fields['status'].initial = 'draft'
        # Set category optional
        self.fields['category'].required = False
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError('Vui lòng chọn ảnh minh họa cho khóa học')
        
        errors = validate_image_file(image)
        if errors:
            raise forms.ValidationError(errors)
        return image
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None:
            if price < 0:
                raise forms.ValidationError('Giá không được nhỏ hơn 0')
            if price > 100000000:  # 100 triệu
                raise forms.ValidationError('Giá không được vượt quá 100,000,000 VNĐ')
        return price
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance


class CourseUpdateForm(CourseCreateForm):
    """Form cập nhật khóa học (cho phép không bắt buộc ảnh)"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False
        self.fields['image'].help_text = 'Chọn ảnh mới nếu muốn thay đổi. Để trống để giữ ảnh cũ.'
