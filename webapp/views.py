from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Order, Payment
from django.db.models import Q
from django.contrib import messages

# home view - landing page
def home(request):
    return render(request, 'webapp/home.html')

# signup view
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login

def signup_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("signup_view")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("signup_view")

        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
        
        login(request, user)
        messages.success(request, "Signup successful! Welcome to Fua Chap Chap.")
        return redirect("home")  # Redirect to homepage after signup

    return render(request, "webapp/signup.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')  # ✅ Corrected syntax
        password = request.POST.get('password')

        print(email, password)  # Debugging (Remove in production)

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)  # Logs the user in
            messages.success(request, "Login successful!")
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('home')  # Redirect to dashboard (Change URL name)
        else:
            print("Invalid email or password")
            return render(request, 'webapp/login.html', {"error": "Invalid email or password"})

    return render(request, 'webapp/login.html')


# logout view
def logout_view(request):
    logout(request)
    messages.success(request, "Logout successful!")
    return redirect('home')

# account view
def account(request):
    user = request.user
    context = {
        "user": user
    }
    orders = Order.objects.filter(order_customer=user)
    context['orders'] = orders  
    return render(request, 'webapp/account.html', context)

# services view
def services(request):
    return render(request, 'webapp/services.html')


#place pick up view
def place_pickup(request):
    return render(request, 'webapp/place_pickup.html')

#place pickup order
def pickup_order(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login_view')
    
    address = request.POST.get('pickup_address')
    service = request.POST.get('service_type')

    if not address or not service:
        return render(request, 'webapp/place_pickup.html', {'error': 'Please fill in all fields '})
    
    #create new order
    order = Order.objects.create(order_customer=user, order_address=address, service=service)
    order.create_payment()  # Creates payment after order is saved
    messages.success(request, 'Pickup order placed successfully!')
    return redirect('account')

#view order
def order(request, order_id):
    user = request.user
    if not user.is_authenticated:
        return redirect('login_view')

    order = Order.objects.get(order_id=order_id)
    if order.order_customer != user:
        return redirect('home')

    context = {
        'order': order
    }
    return render(request, 'webapp/order.html', context)

#cancel order
def cancel_order(request, order_id):
    order = Order.objects.get(order_id = order_id)
    if order:
        order.delete_with_payment()  # Deletes both order and payment
        messages.success(request, 'Order cancelled successfully!')
        return redirect('account')
    return redirect('account')
 
#make payment
def make_payment(request, order_id):
    order = Order.objects.get(order_id=order_id)
    if order:
        order.payment.payment_status = True
        order.payment.save()

        payment = Payment.objects.get(payment_order=order)
        if payment:
            payment.payment_status = True
            payment.payment_amount = order.order_total
            messages.success(request, 'Payment made successfully!')
            return redirect('order', order_id=order_id)
    return redirect('order', order_id=order_id)




 #admin dashboard
def admin_dashboard(request):
    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(order_status='Completed').count()
    pending_or_inprogress_orders = Order.objects.filter(
        Q(order_status='Pending') | Q(order_status='In Progress')
    ).count()
    return render(request, 'administrator/admin_dashboard.html', {
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'in_progress_orders': pending_or_inprogress_orders,
    })  


#admin active orders
def active_orders(request):
    orders = Order.objects.filter(order_status__in=['Pending', 'In Progress']).order_by('order_date')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        price = request.POST.get('price')
        status = request.POST.get('status')

        order = get_object_or_404(Order, order_id=order_id)
        order.order_total = price
        order.order_status = status
        order.save()
        messages.success(request, 'Order updated successfully!')
        return redirect('active_orders')

    return render(request, 'administrator/active_orders.html', {'orders': orders}) 

#completed orders
def completed_orders(request):
    orders = Order.objects.filter(order_status='Completed').order_by('order_date')
    return render(request, 'administrator/completed_orders.html', {'orders': orders})


#order detail view
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        price = request.POST.get('price')

        order.order_status = status
        order.order_total = price
        order.save()

        messages.success(request, "Order updated successfully!")
        return redirect('order_detail', order_id=order_id)

    return render(request, 'administrator/order_detail.html', {'order': order})

#all orders
def all_orders(request):
    order_id = request.GET.get('order_id')
    orders = Order.objects.all().order_by('-order_date')

    if order_id:
        orders = orders.filter(order_id__icontains=order_id)

    return render(request, 'administrator/all_orders.html', {'orders': orders})
