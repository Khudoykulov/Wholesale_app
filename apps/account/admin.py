from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserToken
from .forms import UserCreationForm, UserChangeForm


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('id', 'phone', 'name', 'is_superuser', 'is_staff', 'is_active', 'created_date')
    readonly_fields = ('last_login', 'modified_date', 'created_date')
    list_filter = ('is_superuser', 'is_staff', 'is_active')
    date_hierarchy = 'created_date'
    fieldsets = (
        (None, {'fields': ('name', 'phone', 'password', 'avatar')}),
        (_('Permissions'), {'fields': ('is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'modified_date', 'created_date')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('name', 'password1', 'password2')}),
    )
    search_fields = ('name', 'phone')
    ordering = ('name',)
    filter_horizontal = ()


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_used', 'token', 'created_date')
    date_hierarchy = 'created_date'
    list_filter = ('is_used',)
    search_fields = ('user__username', 'user_full_name', 'token')


admin.site.register(User, UserAdmin)

admin.site.index_title = _('Optom_app administration')
admin.site.site_header = _('Optom_app')
