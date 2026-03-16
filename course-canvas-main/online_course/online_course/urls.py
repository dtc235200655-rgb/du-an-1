from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from . import views
from courses import views as course_views
urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', include('courses.urls')),
    path('crypto/', include('crypto_bot.urls')),  # ✅ NEW: Crypto Bot feature
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', course_views.dashboard, name='dashboard'), 
    path('admin/', admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)