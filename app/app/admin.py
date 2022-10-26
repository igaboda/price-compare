from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from price.models import Price
from product.models import Product
from shop.models import Shop
from user.models import User


class UserAdmin(BaseUserAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(Price)
admin.site.register(Product)
admin.site.register(Shop)

