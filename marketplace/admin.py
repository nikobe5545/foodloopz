from django.contrib import admin

from marketplace.models import Organization, Category, Account, Ad

admin.site.register(Organization)
admin.site.register(Category)
admin.site.register(Account)
admin.site.register(Ad)
