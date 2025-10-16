from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class OrderCart(models.Model):
    customer_name = models.CharField(max_length=255)
    customer_address = models.TextField()

class CartItem(models.Model):
    cart = models.ForeignKey(OrderCart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
