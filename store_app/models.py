from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError


class Categorie(models.Model):
    model_name = models.CharField(max_length=200)

    def __str__(self):
        return self.model_name

class Color(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Filter_Price(models.Model):
    Filter_Price_Choices = (
        ('100 TO 1000', '1000 TO 2000'),
        ('200 TO 3000', '3000 TO 4000'),
        ('4000 TO 10000', '10000 To 30000'),
    )
    price = models.CharField(choices=Filter_Price_Choices, max_length=90)

class Product(models.Model):
    STOCK_CHOICES = (('IN STOCK', 'IN STOCK'), ('OUT OF STOCK', 'OUT OF STOCK'))

    unique_id = models.CharField(unique=True, max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='Product_images/img')
    name = models.CharField(max_length=60)
    price = models.FloatField()
    description = models.CharField(max_length=500)
    stock = models.CharField(choices=STOCK_CHOICES, max_length=200)

    added_date = models.DateTimeField(default=timezone.now)

    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    filter_price = models.ForeignKey(Filter_Price, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.unique_id and self.added_date:
            if not self.id:
                super().save(*args, **kwargs)
            self.unique_id = self.added_date.strftime('75%Y%m%d23') + str(self.id)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class images(models.Model):
    image = models.ImageField(upload_to='Product_images/img')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    def __str__(self):
        return self.image

class tag(models.Model):
    name = models.CharField(max_length=200)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class CustomUser(models.Model):
    email = models.EmailField(unique=True, validators=[EmailValidator(message="Enter a valid email address.")])

    def clean(self):
        email_exists = CustomUser.objects.exclude(pk=self.pk).filter(email=self.email).exists()
        if email_exists:
            raise ValidationError({'email': 'This email address is already in use.'})

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),

        ('Cash on Delivery', 'Cash on Delivery'),
        # Add more payment methods as needed
    )

    product = models.ForeignKey(Product, related_name='orders', on_delete=models.CASCADE, default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=100, default='')
    lastname = models.CharField(max_length=100,default='')
    address = models.TextField(max_length=100, null=True, blank=True)

    city = models.CharField(max_length=100, null=True, blank=True)
    phone = models.IntegerField(default='0')

    email = models.EmailField(max_length=100,default='')
    amount = models.CharField(max_length=20, default=(0.0))   # Add max_length attribute here


    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)  # Field to indicate deletion status
    payment_done = models.BooleanField(default=False)  # Field to indicate whether payment is done
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='Cash on Delivery')  # Field for payment method

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    images = models.ImageField(upload_to="Product_images/Order_Img",default='')
    quantity = models.CharField(max_length=20, default=0)
    price = models.CharField(max_length=20, default='0')
    total = models.CharField(max_length=10000, default='0')


    def __str__(self):
       return self.order.user.username

class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    # Add other fields related to deliveries

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add other fields related to wishlist

class CartManager(models.Manager):
    pass

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CartManager()


class Payment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100)
    payment_date = models.DateTimeField(auto_now_add=True)



class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
