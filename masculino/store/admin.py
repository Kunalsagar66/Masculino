from django.contrib import admin
from .models import *
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('product_name',)}
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')

class VariationAdmin(admin.ModelAdmin):
    list_display = ('get_product', 'variation_category', 'variation_value', 'is_active', 'created_date',)
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active',)
    def get_product(self, obj) :
        return obj.product.product_name

admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)