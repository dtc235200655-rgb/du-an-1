import os
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.conf import settings


# =========== VALIDATORS CHO FILE UPLOAD ===========

@deconstructible
class FileSizeValidator:
    """Kiểm tra kích thước file"""
    
    def __init__(self, max_size_mb=5):
        self.max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
        self.max_size_mb = max_size_mb
    
    def __call__(self, value):
        if value.size > self.max_size_bytes:
            raise ValidationError(
                f'Kích thước file không được vượt quá {self.max_size_mb}MB. '
                f'File hiện tại có kích thước {value.size / (1024*1024):.1f}MB'
            )


@deconstructible
class FileExtensionValidator:
    """Kiểm tra định dạng file được phép"""
    
    def __init__(self, allowed_extensions=None):
        if allowed_extensions is None:
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
    
    def __call__(self, value):
        # Lấy extension từ filename
        ext = os.path.splitext(value.name)[1].lower().lstrip('.')
        
        if ext not in self.allowed_extensions:
            allowed = ', '.join(self.allowed_extensions)
            raise ValidationError(
                f'Định dạng file không được phép. '
                f'Được phép: {allowed}. '
                f'File của bạn: {ext}'
            )


@deconstructible
class ImageValidator:
    """Kết hợp nhiều kiểm tra cho ảnh"""
    
    def __init__(self, max_size_mb=5, min_width=100, min_height=100, max_width=3000, max_height=3000):
        self.max_size_validator = FileSizeValidator(max_size_mb)
        self.extension_validator = FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp'])
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height
    
    def __call__(self, value):
        # Kiểm tra định dạng và kích thước
        self.extension_validator(value)
        self.max_size_validator(value)
        
        # Kiểm tra dimensions (nếu có PIL)
        try:
            from PIL import Image
            img = Image.open(value)
            width, height = img.size
            
            if width < self.min_width:
                raise ValidationError(f'Chiều rộng ảnh phải >= {self.min_width}px (hiện tại: {width}px)')
            
            if height < self.min_height:
                raise ValidationError(f'Chiều cao ảnh phải >= {self.min_height}px (hiện tại: {height}px)')
            
            if width > self.max_width:
                raise ValidationError(f'Chiều rộng ảnh phải <= {self.max_width}px (hiện tại: {width}px)')
            
            if height > self.max_height:
                raise ValidationError(f'Chiều cao ảnh phải <= {self.max_height}px (hiện tại: {height}px)')
                
        except ImportError:
            # PIL không được cài đặt, bỏ qua kiểm tra dimensions
            pass
        except Exception:
            # Không đọc được ảnh, cho phép qua
            pass


# =========== HÀM TIỆNÍ XỬ LÝ FILE ===========

def validate_image_file(uploaded_file):
    """Hàm kiểm tra ảnh (trả về dict chứa lỗi)"""
    errors = []
    
    # Kiểm tra định dạng
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in valid_extensions:
        errors.append(f'Định dạng không được hỗ trợ: {ext}. Chỉ chấp nhận: {", ".join(valid_extensions)}')
    
    # Kiểm tra kích thước (max 5MB)
    max_size = 5 * 1024 * 1024
    if uploaded_file.size > max_size:
        size_mb = uploaded_file.size / (1024 * 1024)
        errors.append(f'File quá lớn: {size_mb:.1f}MB. Giới hạn: 5MB')
    
    # Kiểm tra có thể đọc ảnh hay không
    if not errors:
        try:
            from PIL import Image
            Image.open(uploaded_file)
            uploaded_file.seek(0)  # Reset lại position
        except ImportError:
            # Bỏ qua kiểm tra Pillow
            pass
        except Exception:
            errors.append('Không thể đọc file ảnh. Vui lòng kiểm tra lại định dạng.')
    
    return errors


def get_file_info(file_obj):
    """Lấy thông tin chi tiết của file"""
    if not file_obj:
        return None
    
    ext = os.path.splitext(file_obj.name)[1].lower()
    size_mb = file_obj.size / (1024 * 1024)
    
    info = {
        'name': file_obj.name,
        'extension': ext,
        'size_bytes': file_obj.size,
        'size_mb': round(size_mb, 2),
        'is_image': ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    }
    
    # Nếu là ảnh đánh giá, giới hạn kích thước nhỏ hơn
    if info['is_image']:
        try:
            from PIL import Image
            img = Image.open(file_obj)
            info['width'] = img.width
            info['height'] = img.height
            info['format'] = img.format
            file_obj.seek(0)
        except:
            info['width'] = None
            info['height'] = None
            info['format'] = None
    
    # Nếu là ảnh, thêm thông tin dimensions
    if info['is_image']:
        try:
            from PIL import Image
            img = Image.open(file_obj)
            info['width'] = img.width
            info['height'] = img.height
            info['format'] = img.format
            file_obj.seek(0)
        except:
            info['width'] = None
            info['height'] = None
            info['format'] = None
    
    return info


# =========== VALIDATORS CHO CÁC LOẠI FILE KHÁC ===========

def validate_document_file(uploaded_file):
    """Kiểm tra file tài liệu (PDF, DOC, DOCX)"""
    errors = []
    
    valid_extensions = ['.pdf', '.doc', '.docx']
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    if ext not in valid_extensions:
        errors.append(f'Định dạng không được hỗ trợ: {ext}. Chỉ chấp nhận: {", ".join(valid_extensions)}')
    
    # Max 10MB cho tài liệu
    max_size = 10 * 1024 * 1024
    if uploaded_file.size > max_size:
        size_mb = uploaded_file.size / (1024 * 1024)
        errors.append(f'File quá lớn: {size_mb:.1f}MB. Giới hạn: 10MB')
    
    return errors


def validate_video_file(uploaded_file):
    """Kiểm tra file video"""
    errors = []
    
    valid_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    if ext not in valid_extensions:
        errors.append(f'Định dạng không được hỗ trợ: {ext}. Chỉ chấp nhận: {", ".join(valid_extensions)}')
    
    # Max 100MB cho video
    max_size = 100 * 1024 * 1024
    if uploaded_file.size > max_size:
        size_mb = uploaded_file.size / (1024 * 1024)
        errors.append(f'File quá lớn: {size_mb:.1f}MB. Giới hạn: 100MB')
    
    return errors


def validate_review_image(uploaded_file):
    """Kiểm tra ảnh cho đánh giá (kích thước nhỏ hơn)"""
    errors = []
    
    # Kiểm tra định dạng
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    if ext not in valid_extensions:
        errors.append(f'Định dạng không được hỗ trợ: {ext}. Chỉ chấp nhận: {", ".join(valid_extensions)}')
    
    # Max 3MB cho ảnh đánh giá (nhỏ hơn ảnh khóa học)
    max_size = 3 * 1024 * 1024
    if uploaded_file.size > max_size:
        size_mb = uploaded_file.size / (1024 * 1024)
        errors.append(f'Ảnh quá lớn: {size_mb:.1f}MB. Giới hạn: 3MB')
    
    # Kiểm tra có thể đọc ảnh
    if not errors:
        try:
            from PIL import Image
            img = Image.open(uploaded_file)
            width, height = img.size
            
            # Giới hạn dimensions hợp lý cho ảnh đánh giá
            if width > 2000 or height > 2000:
                errors.append('Kích thước ảnh quá lớn. Tối đa: 2000x2000 pixels')
            
            if width < 50 or height < 50:
                errors.append('Kích thước ảnh quá nhỏ. Tối thiểu: 50x50 pixels')
                
            uploaded_file.seek(0)
        except ImportError:
            # Bỏ qua nếu không có PIL
            pass
        except Exception:
            errors.append('Không thể đọc file ảnh. Vui lòng kiểm tra lại định dạng.')
    
    return errors
