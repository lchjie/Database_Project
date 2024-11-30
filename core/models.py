from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    operating_hours = models.CharField(max_length=200, default="9:00 AM - 9:00 PM")

    def __str__(self):
        return self.name

class Menu(models.Model):
    name = models.CharField(max_length=100)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.restaurant.name} - {self.name} (${self.price})"

class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='items', null=True, blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    computing_id = models.CharField(
        max_length=6,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9]{6}$',
                message='Computing ID must be exactly 6 alphanumeric characters'
            )
        ]
    )
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, editable=False)
    phone_number = models.CharField(max_length=15, blank=True)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def clean(self):
        self.email = f"{self.computing_id}@virginia.edu"
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.get_full_name()

class Order(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    items = models.ManyToManyField(Item, related_name='orders')

    def clean(self):
        # Check if all items are from the same restaurant
        if self.pk:  # Only check if order exists (has items)
            restaurants = set(item.menu.restaurant.id for item in self.items.all())
            if len(restaurants) > 1:
                raise ValidationError("All items in an order must be from the same restaurant")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} by {self.student.get_full_name()}"
