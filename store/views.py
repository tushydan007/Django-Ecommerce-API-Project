from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from django.db.models import Count
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import (
    IsAdminUser,
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)

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
from store.serializers import (
    AddCartItemSerializer,
    AddressSerializer,
    CartItemSerializer,
    CartSerializer,
    CollectionSerializer,
    CreateOrderSerializer,
    CustomerSerializer,
    OrderItemSerializer,
    OrderSerializer,
    ProductImageSerializer,
    ProductReviewSerializer,
    ProductSerializer,
    UpdateCartItemSerializer,
    UpdateOrderSerializer,
)


class CollectionViewSet(ModelViewSet):
    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [AllowAny()]
        return [IsAdminUser()]

    queryset = (
        Collection.objects.annotate(product_count=Count("products"))
        .prefetch_related("products")
        .all()
    )
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=self.kwargs["pk"]).count() > 0:
            return Response(
                {
                    "Error": "Collection cannot be deleted because it is associated with at least one product"
                }
            )
        return super().destroy(request, *args, **kwargs)


class CollectionProductViewSet(ModelViewSet):
    def get_queryset(self):
        return Product.objects.select_related("collection").filter(
            collection_id=self.kwargs["collection_pk"]
        )

    serializer_class = ProductSerializer


class ProductViewSet(ModelViewSet):
    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [AllowAny()]
        return [IsAdminUser()]

    queryset = (
        Product.objects.select_related("collection").prefetch_related("images").all()
    )
    serializer_class = ProductSerializer

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=self.kwargs["pk"]).count() > 0:
            return Response(
                {
                    "Error": "Product cannot be deleted because it is associated with at least one order item"
                }
            )
        return super().destroy(request, *args, **kwargs)


class ProductImageViewSet(ModelViewSet):
    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        return ProductImage.objects.select_related("product").filter(
            product_id=self.kwargs["product_pk"]
        )

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}

    serializer_class = ProductImageSerializer


class ProductReviewViewSet(ModelViewSet):
    def get_queryset(self):
        return ProductReview.objects.select_related("product").filter(
            product_id=self.kwargs["product_pk"]
        )

    serializer_class = ProductReviewSerializer


class CustomerViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.select_related("user").all()
    serializer_class = CustomerSerializer

    @action(detail=False, methods=["GET", "PUT"], permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        customer = Customer.objects.get(user_id=self.request.user)
        if request.method == "GET":
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if Order.objects.filter(customer_id=self.kwargs["pk"]).count() > 0:
            return Response(
                {
                    "Error": "Customer cannot be deleted because it is associated with at least one order"
                }
            )
        return super().destroy(request, *args, **kwargs)


class OrderViewSet(ModelViewSet):
    http_method_names = ["get", "patch", "post", "delete", "head", "options"]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.select_related("customer").all()
        customer = Customer.objects.only("id").get(user_id=self.request.user.id)
        return Order.objects.filter(customer_id=customer)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        if self.request.method == "PATCH":
            return UpdateOrderSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data, context={"user_id": self.request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)

        return Response(serializer.data)


class OrderItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

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
