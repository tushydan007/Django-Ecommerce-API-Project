from rest_framework import serializers
from django.db import transaction

from store.models import (
    Address,
    Cart,
    CartItem,
    Collection,
    Customer,
    Order,
    OrderItem,
    Product,
    ProductImage,
    ProductReview,
)


class CollectionSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ["id", "title", "product_count", "image_url"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        return ProductImage.objects.create(product_id=product_id, **validated_data)


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ["id", "customer_name", "description", "date_created"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        return ProductReview.objects.create(product_id=product_id, **validated_data)


class PatchProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["in_cart"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "inventory",
            "collection",
            "in_cart",
            "images",
            "reviews",
            "manufacturer",
        ]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "phone", "birth_date", "membership", "user"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "placed_at", "payment_status", "customer"]


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]
            user_id = self.context["user_id"]
            customer = Customer.objects.get(user_id=user_id)

            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects.filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    quantity=item.quantity,
                    unit_price=item.product.price,
                    order=order,
                    product=item.product,
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()
            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["payment_status"]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "quantity", "unit_price", "order", "product"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "street", "city", "customer"]


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "price"]


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name="item_total_price")

    def item_total_price(self, item):
        return item.quantity * item.product.price

    class Meta:
        model = CartItem
        fields = ["id", "quantity", "product", "total_price"]


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item

        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )

        return self.instance

    class Meta:
        model = CartItem
        fields = ["id", "quantity", "product_id"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class CartSerializer(serializers.ModelSerializer):
    cart_total_price = serializers.SerializerMethodField(method_name="get_total_price")
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ["id", "items", "cart_total_price"]
