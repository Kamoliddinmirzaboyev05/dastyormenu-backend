"""User admin."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ['organization', 'full_name', 'role', 'is_active']
    
    def get_fields(self, request, obj=None):
        """Hide organization field for super_admin."""
        fields = super().get_fields(request, obj)
        if obj and hasattr(obj, 'userprofile') and obj.userprofile.role == 'super_admin':
            return ['full_name', 'role', 'is_active']
        return fields


class UserAdmin(BaseUserAdmin):
    """Extended User admin with profile inline."""
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role']
    
    def get_role(self, obj):
        """Get user role from profile."""
        if hasattr(obj, 'userprofile'):
            return obj.userprofile.role
        return '-'
    get_role.short_description = 'Role'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model."""
    list_display = ['full_name', 'get_username', 'get_email', 'role', 'organization', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'organization']
    search_fields = ['full_name', 'user__username', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_username(self, obj):
        """Get username from user."""
        return obj.user.username
    get_username.short_description = 'Username'
    
    def get_email(self, obj):
        """Get email from user."""
        return obj.user.email
    get_email.short_description = 'Email'


# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
