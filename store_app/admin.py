from django.contrib import admin
from .models import *


class tagTabularInline(admin.TabularInline):
    model = tag

class ProductAdmin(admin.ModelAdmin):

    list_display = ('name', 'price', 'stock',  'added_date')
    list_filter = ('stock', 'added_date')
    search_fields = ('name', 'description')

class OrderItemInline(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'get_total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username')
    inlines = [OrderItemInline]

    def get_total_price(self, obj):
        # Calculate total price based on order items
        total_price = sum(float(item.total) for item in obj.orderitem_set.all())
        return total_price

    get_total_price.short_description = 'Total Price'

    def delete_order(self, request, queryset):
        for order in queryset:
            order.delete()
    delete_order.short_description = "Delete selected orders"
    actions = [delete_order]

class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order')
    search_fields = ('order__id',)

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    search_fields = ('user__username',)

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'created_at')
    search_fields = ('user__username', 'product__name')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('amount', 'payment_method', 'payment_date')
    search_fields = ('payment_method',)

# Register models with their respective admin classes
admin.site.register(Categorie)
admin.site.register(Color)
admin.site.register(Product, ProductAdmin)

admin.site.register(tag)
admin.site.register(Filter_Price)
admin.site.register(Order, OrderAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Payment, PaymentAdmin)
