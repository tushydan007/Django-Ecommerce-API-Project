from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)
from rest_framework.viewsets import GenericViewSet

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
)
from store.serializers import (
    AddCartItemSerializer,
    AddressSerializer,
    CartItemSerializer,
    CartSerializer,
    CollectionSerializer,
    CustomerSerializer,
    OrderItemSerializer,
    OrderSerializer,
    ProductImageSerializer,
    ProductSerializer,
    UpdateCartItemSerializer,
)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.prefetch_related("products").all()
    serializer_class = CollectionSerializer


class ProductViewSet(ModelViewSet):
    queryset = (
        Product.objects.select_related("collection").prefetch_related("images").all()
    )
    serializer_class = ProductSerializer


class ProductImageViewSet(ModelViewSet):
    def get_queryset(self):
        return ProductImage.objects.select_related("product").filter(
            product_id=self.kwargs["product_pk"]
        )

    serializer_class = ProductImageSerializer


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.select_related("user").all()
    serializer_class = CustomerSerializer


class OrderViewSet(ModelViewSet):
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.select_related("customer").all()
        customer = Customer.objects.only("id").get(user_id=self.request.user.id)
        return Order.objects.filter(customer_id=customer)

    serializer_class = OrderSerializer


class OrderItemViewSet(ModelViewSet):
    def get_queryset(self):
        return (
            OrderItem.objects.select_related("order")
            .select_related("product")
            .filter(order_id=self.kwargs["order_pk"])
        )

    serializer_class = OrderItemSerializer


class AddressViewSet(ModelViewSet):
    def get_queryset(self):
        return Address.objects.select_related("customer").filter(
            customer_id=self.kwargs["customer_pk"]
        )

    serializer_class = AddressSerializer


class CartViewSet(
    CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = Cart.objects.prefetch_related("items").all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return (
            CartItem.objects.select_related("cart")
            .select_related("product")
            .filter(cart_id=self.kwargs["cart_pk"])
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        if self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}
