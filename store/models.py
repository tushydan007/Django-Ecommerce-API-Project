from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator, MinValueValidator
from uuid import uuid4

from store.validators import validate_file_size

# Create your models here.


class Collection(models.Model):
    title = models.CharField(max_length=255, validators=[MinLengthValidator(3)])
    image_url = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255, validators=[MinLengthValidator(3)])
    description = models.TextField(max_length=500, validators=[MinLengthValidator(8)])
    price = models.IntegerField(validators=[MinValueValidator(1)])
    inventory = models.IntegerField(validators=[MinValueValidator(1)])
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name="products"
    )
    manufacturer = models.CharField(max_length=255, default="Apple")
    in_cart = models.BooleanField(default=False)
    quantity_incart = models.PositiveSmallIntegerField()


class ProductReview(models.Model):
    description = models.TextField()
    customer_name = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )


class ProductImage(models.Model):
    image = models.ImageField(upload_to="store/images", validators=[validate_file_size])
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )


class Customer(models.Model):
    MEMBERSHIP_BRONZE = "B"
    MEMBERSHIP_SILVER = "S"
    MEMBERSHIP_GOLD = "G"

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, "Bronze"),
        (MEMBERSHIP_SILVER, "Silver"),
        (MEMBERSHIP_GOLD, "Gold"),
    ]
    phone = models.CharField(max_length=30, validators=[MinLengthValidator(7)])
    birth_date = models.DateField(auto_now_add=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Order(models.Model):
    PAYMENT_STATUS_PENDING = "P"
    PAYMENT_STATUS_COMPLETE = "C"
    PAYMENT_STATUS_FAILED = "F"
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, "Pending"),
        (PAYMENT_STATUS_COMPLETE, "Complete"),
        (PAYMENT_STATUS_FAILED, "Failed"),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING
    )

    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="orders"
    )


class OrderItem(models.Model):
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.IntegerField(validators=[MinValueValidator(1)])
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items"
    )


class Address(models.Model):
    street = models.CharField(max_length=255, validators=[MinLengthValidator(3)])
    city = models.CharField(max_length=255, validators=[MinLengthValidator(3)])
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="addresses"
    )


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )

    class Meta:
        unique_together = [["product", "cart"]]
