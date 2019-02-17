from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from marketplace.models import Organization, AdCategory, Account, Ad, Address, OrganizationCategory, \
    OrganizationCertification, AdCertification, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


class AccountInline(admin.TabularInline):
    model = Account


class AdInline(admin.TabularInline):
    model = Ad


class AddressInline(admin.TabularInline):
    model = Address


class OrganizationAdmin(admin.ModelAdmin):
    inlines = [
        AccountInline,
        AdInline
    ]
    search_fields = ('name', 'organization_number')


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationCategory)
admin.site.register(OrganizationCertification)
admin.site.register(AdCategory)
admin.site.register(AdCertification)
admin.site.register(Account)
admin.site.register(Ad)
admin.site.register(Address)
