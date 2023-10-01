from django.db.models import Count
from django.contrib import admin
from django.utils.html import format_html, urlencode
from django.urls import reverse

from .models import (
    Collection,
    Product,
    Customer,
    Order,
    OrderItem,
    Address,
    Cart,
    CartItem,
    ProductImage,
)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "product_count"]
    list_editable = ["title"]
    search_fields = ["title"]

    @admin.display(ordering="product_count")
    def product_count(self, collection: Collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection_id": collection.id})
        )
        return format_html(
            "<a href='{}' target='_blank'>{}</a>",
            url,
            collection.product_count,
        )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(product_count=Count("products"))


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "description",
        "price",
        "inventory",
        "last_update",
        "collection",
    ]
    list_editable = ["price", "description", "inventory"]
    search_fields = ["title", "price", "last_update"]
    inlines = [ProductImageInline]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "phone", "birth_date", "membership"]
    list_editable = ["membership"]
    search_fields = ["user__name"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "placed_at",
        "payment_status",
        "customer",
    ]
    list_editable = ["payment_status"]
    search_fields = ["placed_at"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "quantity", "unit_price", "order", "product"]
    list_editable = ["quantity"]
    search_fields = ["order__id"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["id", "street", "city", "customer"]
    list_editable = ["street", "city"]
    search_fields = ["street", "city"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    search_fields = ["id"]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["id", "quantity", "cart", "product"]
    search_fields = ["cart__id"]
