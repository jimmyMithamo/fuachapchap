from django.contrib import admin
from .models import Order, Profile, Payment, Service

# Register your models here.
admin.site.register(Order)
admin.site.register(Profile)
admin.site.register(Payment)
admin.site.register(Service)