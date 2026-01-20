# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from import_export.admin import ImportExportMixin, ImportExportModelAdmin
from .models import UserProfile
from .models import Address

# Thêm profile vào trang User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserAdmin(ImportExportMixin, BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'first_name', 'last_name', 'email')


@admin.register(UserProfile)
class UserProfileAdmin(ImportExportModelAdmin):
    list_display = ("user", "phone", "date_of_birth", "created_at")
    search_fields = ("user__username", "user__email", "phone")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Address)
class AddressAdmin(ImportExportModelAdmin):
    list_display = ("full_name", "phone", "city", "district", "ward", "is_default")
    list_filter = ("is_default", "city")
    search_fields = ("full_name", "phone", "city", "district", "address_line")
# Ghi đè UserAdmin mặc định
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
