from rest_framework_nested import routers

from store.views import (
    AddressViewSet,
    CartItemViewSet,
    CartViewSet,
    CollectionViewSet,
    CustomerViewSet,
    OrderItemViewSet,
    OrderViewSet,
    ProductReviewViewSet,
    ProductViewSet,
    ProductImageViewSet,
    CollectionProductViewSet,
)


router = routers.DefaultRouter()
# main routes
router.register("collections", CollectionViewSet, basename="collections")
router.register("products", ProductViewSet, basename="products")
router.register("customers", CustomerViewSet, basename="customers")
router.register("orders", OrderViewSet, basename="orders")
router.register("carts", CartViewSet, basename="carts")

# Sub parent routes
order_router = routers.NestedDefaultRouter(router, "orders", lookup="order")
cart_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
customer_router = routers.NestedDefaultRouter(router, "customers", lookup="customer")
product_router = routers.NestedDefaultRouter(router, "products", lookup="product")
collection_router = routers.NestedDefaultRouter(
    router, "collections", lookup="collection"
)

# nested routes
order_router.register("items", OrderItemViewSet, basename="order_items")
cart_router.register("items", CartItemViewSet, basename="cart_items")
customer_router.register("addresses", AddressViewSet, basename="addresses")
product_router.register("images", ProductImageViewSet, basename="product_images")
product_router.register("reviews", ProductReviewViewSet, basename="product_reviews")
collection_router.register(
    "products", CollectionProductViewSet, basename="collection_products"
)


urlpatterns = (
    router.urls
    + order_router.urls
    + cart_router.urls
    + customer_router.urls
    + product_router.urls
    + collection_router.urls
)
