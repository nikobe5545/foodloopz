from django.contrib import admin

from marketplace.models import Organization, AdCategory, Account, Ad, Address, OrganizationCategory, \
    OrganizationCertification, AdCertification


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
