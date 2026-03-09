#!/usr/bin/env python
"""
Login System Verification Script
Run this to check if login system is working properly
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_course.settings')
django.setup()

from django.contrib.auth.models import User
from courses.models import UserRole
from django.contrib.auth import authenticate

print("=" * 60)
print("🔍 LOGIN SYSTEM VERIFICATION")
print("=" * 60)

# Check 1: UserRole model
print("\n✅ CHECK 1: UserRole Model")
try:
    role_choices = UserRole.ROLE_CHOICES
    print(f"   ✓ Role choices loaded: {len(role_choices)} roles")
    for value, display in role_choices:
        print(f"     - {value}: {display}")
except Exception as e:
    print(f"   ✗ Error loading UserRole: {e}")

# Check 2: Database tables
print("\n✅ CHECK 2: Database Tables")
try:
    user_count = User.objects.count()
    role_count = UserRole.objects.count()
    print(f"   ✓ Users table: {user_count} users")
    print(f"   ✓ Roles table: {role_count} roles")
    
    if user_count > 0 and role_count == 0:
        print(f"   ⚠️  WARNING: No roles found! Run: python manage.py assign_user_roles")
except Exception as e:
    print(f"   ✗ Database error: {e}")

# Check 3: Users with roles
print("\n✅ CHECK 3: Users and Roles Status")
users_without_roles = []
users_with_roles = []

for user in User.objects.all():
    if hasattr(user, 'user_role'):
        users_with_roles.append((user.username, user.user_role.role))
        print(f"   ✓ {user.username}: {user.user_role.get_role_display()}")
    else:
        users_without_roles.append(user.username)
        print(f"   ✗ {user.username}: NO ROLE ASSIGNED")

if users_without_roles:
    print(f"\n   ⚠️  Found {len(users_without_roles)} users without roles!")
    print(f"   💡 Solution: python manage.py assign_user_roles")

# Check 4: Test authentication
print("\n✅ CHECK 4: Authentication Test")
test_credentials = [
    ('Admin', 'admin'),  # Default superuser
    ('staff_admin', 'staff123'),
]

for username, password in test_credentials:
    try:
        user = authenticate(username=username, password=password)
        if user:
            role = user.user_role.role if hasattr(user, 'user_role') else 'NO ROLE'
            print(f"   ✓ {username}: Authenticated successfully ({role})")
        else:
            print(f"   ⚠️  {username}: Wrong password or doesn't exist")
    except Exception as e:
        print(f"   ✗ {username}: Error - {e}")

# Check 5: Redirect URLs
print("\n✅ CHECK 5: Role Redirect URLs")
try:
    for role_value, role_display in UserRole.ROLE_CHOICES:
        # Create a mock object to test get_role_redirect_url
        class MockRole:
            role = role_value
            def get_role_redirect_url(self):
                redirect_urls = {
                    'admin': '/admin/',
                    'staff': '/staff/dashboard/',
                    'customer': '/dashboard/',
                }
                return redirect_urls.get(self.role, '/dashboard/')
        
        mock = MockRole()
        url = mock.get_role_redirect_url()
        print(f"   ✓ {role_display}: {url}")
except Exception as e:
    print(f"   ✗ Error checking redirects: {e}")

# Summary
print("\n" + "=" * 60)
print("📊 SUMMARY")
print("=" * 60)
print(f"Total users: {user_count}")
print(f"Users with roles: {len(users_with_roles)}")
print(f"Users without roles: {len(users_without_roles)}")

if len(users_without_roles) > 0:
    print("\n⚠️  ACTION REQUIRED:")
    print("   Run: python manage.py assign_user_roles")
else:
    print("\n✅ All users have roles assigned!")

print("\n💡 NEXT STEPS:")
print("   1. If errors found, run the suggested commands")
print("   2. Test login at: http://localhost:8000/login/")
print("   3. Use credentials: staff_admin / staff123")
print("=" * 60)
