import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_course.settings')
django.setup()

from django.contrib.auth.models import User
from courses.models import UserRole

print("=== USER ROLES CHECK ===\n")
for user in User.objects.all():
    has_role = hasattr(user, 'user_role')
    if has_role:
        role = user.user_role.role
        print(f"✓ {user.username}: Role = '{role}' ({user.user_role.get_role_display()})")
    else:
        print(f"✗ {user.username}: NO ROLE")

print("\n=== TESTING LOGIN SCENARIOS ===\n")

# Test scenario 1: User tries to login as staff but is actually customer
print("Scenario 1: Customer user (Manh) trying to login as STAFF")
manh = User.objects.filter(username='Manh').first()
if manh and hasattr(manh, 'user_role'):
    print(f"  Actual role: {manh.user_role.role}")
    print(f"  If selects 'staff' at login: ERROR will occur (role mismatch)")
    print(f"  Should select: 'customer'\n")

# Test scenario 2: Staff user trying to login as customer  
print("Scenario 2: Staff user (staff_admin) trying to login as CUSTOMER")
staff = User.objects.filter(username='staff_admin').first()
if staff and hasattr(staff, 'user_role'):
    print(f"  Actual role: {staff.user_role.role}")
    print(f"  If selects 'customer' at login: ERROR will occur (role mismatch)")
    print(f"  Should select: 'staff'\n")

print("\n=== SOLUTION ===")
print("Users must select their ACTUAL role when logging in!")
print("The system validates that selected role matches actual role.")
