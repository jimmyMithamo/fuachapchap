from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login_view/', views.login_view, name='login_view'),
    path('signup_view/', views.signup_view, name='signup_view'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('account/', views.account, name='account'),

    path('services/', views.services, name='services'),

    path('place_pickup/', views.place_pickup, name='place_pickup'),
    path('pickup_order/', views.pickup_order, name='pickup_order'),
    path('order/<int:order_id>/', views.order, name='order'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name = 'cancel_order'),
    path('make_payment/<int:order_id>/', views.make_payment, name='make_payment'),

    path('custom-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('custom-admin/active_orders/', views.active_orders, name='active_orders'),
    path('custom-admin/completed_orders/', views.completed_orders, name='completed_orders'),
    path('custom-admin/order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('custom-admin/all-orders/', views.all_orders, name='all_orders'),



]
