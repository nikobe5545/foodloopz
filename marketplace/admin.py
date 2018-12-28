from django.contrib import admin

from marketplace.models import Organization, Category, Account, Ad


class AccountInline(admin.TabularInline):
    model = Account


class AdInline(admin.TabularInline):
    model = Ad


class OrganizationAdmin(admin.ModelAdmin):
    inlines = [
        AccountInline,
        AdInline,
    ]


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Category)
admin.site.register(Account)
admin.site.register(Ad)
