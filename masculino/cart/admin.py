from django.contrib import admin
from .models import *
# Register your models here.
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id','date_added',)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('get_product','cart','quantity','is_active',)
    def get_product(self, obj) :
        return obj.product.product_name

admin.site.register(Cart,CartAdmin)
admin.site.register(CartItem,CartItemAdmin)