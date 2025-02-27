from .models import Product
from django.contrib import admin
from .models import *

# Inline class for tags


class TagTabularInline(admin.TabularInline):
    model = tag


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'quantity',
                    'added_date')  # ✅ Display quantity field
    list_filter = ('stock', 'added_date')
    search_fields = ('name', 'description')
    inlines = [TagTabularInline]
    # ✅ Add delete action
    actions = ['restock_products', 'delete_selected_products']

    def restock_products(self, request, queryset):
        """✅ Restock selected products by 10 units."""
        for product in queryset:
            product.restock(amount=10)
        self.message_user(request, "Selected products have been restocked.")

    restock_products.short_description = "Restock selected products by 10 units"

    def delete_selected_products(self, request, queryset):
        """✅ Delete selected products from the database."""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} products have been deleted.")

    delete_selected_products.short_description = "Delete selected products"


# Inline class for OrderItem
class OrderItemInline(admin.TabularInline):
    model = OrderItem

# Order admin customization


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_first_name', 'user_last_name',
                    'product_names', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username',
                     'user__first_name', 'user__last_name')
    inlines = [OrderItemInline]

    # Custom action to delete selected orders
    def delete_order(self, request, queryset):
        queryset.delete()
    delete_order.short_description = "Delete selected orders"
    actions = [delete_order]

    # Custom method to display the user's first name
    def user_first_name(self, obj):
        return obj.user.first_name
    user_first_name.short_description = "First Name"

    # Custom method to display the user's last name
    def user_last_name(self, obj):
        return obj.user.last_name
    user_last_name.short_description = "Last Name"

    # Custom method to display the product names
    def product_names(self, obj):
        return ", ".join(
            [order_item.product.name for order_item in obj.order_items.all()]
        )
    product_names.short_description = "Product Names"

# Delivery admin customization


class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order')
    search_fields = ('order__id',)

# Wishlist admin customization


class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    search_fields = ('user__username',)

# Cart admin customization


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'created_at')
    search_fields = ('user__username', 'product__name')

# Payment admin customization


class ESEWATransactionAdmin(admin.ModelAdmin):
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
admin.site.register(ESEWATransaction, ESEWATransactionAdmin)
