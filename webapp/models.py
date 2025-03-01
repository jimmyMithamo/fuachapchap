from django.contrib.auth.models import User
from django.db import models


#profile model extends user model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
       

# Order model
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    order_id = models.AutoField(primary_key=True)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    service = models.TextField()
    order_customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_address = models.TextField()
    payment = models.OneToOneField('Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='order')

    def __str__(self):
        return f"Order #{self.order_id}"
    
    def create_payment(self):
        if not self.payment:
            payment = Payment.objects.create(
                payment_amount=self.order_total,
                payment_order=self
            )
            self.payment = payment
            self.save()

    def delete_with_payment(self):
        if self.payment:
            self.payment.delete()
        self.delete()


# Payment model
class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    payment_order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment_info')

    def __str__(self):
        return f"Payment #{self.payment_id}"


#model for services
class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=100)
    service_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.service


