from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Order, Payment
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django_daraja.mpesa.core import MpesaClient
from django.http import HttpResponse

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
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("signup_view")

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("signup_view")

        # Check if email is already in use
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("signup_view")

        # Create user with separate username and email
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Log the user in
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

#all orders
def orders(request):
    orders = Order.objects.filter(order_customer=request.user).order_by('-created_at')  # Fetch user's orders
    return render(request, "webapp/orders.html", {"orders": orders})



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

from django.contrib.auth.decorators import login_required
@login_required
def update_profile(request):
    if request.method == "POST":
        user = request.user
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")

        # Update Name
        if first_name and last_name:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # Update Phone Number
        if phone_number:
            user.profile.phone_number = phone_number
            user.profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("account")  # Change to your actual profile page name

    return redirect("account")





#view for stk push

@csrf_exempt  # Allow external requests (disable CSRF for API)
def initiate_stk_push(request, order_id):
    cl = MpesaClient()
    # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
    phone_number = request.user.profile.phone_number
    if not phone_number:
        messages.error(request, 'Please update your phone number in your account settings')
        return redirect('account')

    order = Order.objects.filter(order_id=order_id).first()
   
    print(order.payment.payment_status)  # Debugging

    if not order:
        messages.error(request, "Order not found!")
        return redirect("orders")
    amount = int(order.order_total)

    account_reference = 'reference'
    transaction_desc = 'Description'
    print("Initiating STK Push...")  # Debugging
    callback_url = f"https://74720cfbcda114885399f5f9e6d21a60.serveo.net/callback/{order_id}/"
    print(callback_url)  # Debugging
    response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
    print(response)  # Debugging
    if response:
        print(response)
        messages.success(request, 'Payment initiated successfully')
    return redirect('order', order_id=order_id)


@csrf_exempt 
def mpesa_callback(request, order_id):
    print("M-Pesa Callback Received")  # Debugging
    if request.method == "POST":
        try:
            callback_data = json.loads(request.body)
            print("M-Pesa Callback Data:", callback_data)  # Debugging

            # Extract necessary details
            body = callback_data.get("Body", {})
            stk_callback = body.get("stkCallback", {})
            result_code = stk_callback.get("ResultCode", -1)  # -1 default for safety
            merchant_request_id = stk_callback.get("MerchantRequestID", "")
            checkout_request_id = stk_callback.get("CheckoutRequestID", "")
            callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])

            if result_code != 0:
                messages.error(request, "payment failed")

            # Check if payment was successful
            if result_code == 0:
                messages.success(request, "Payment successful")
                amount = None
                mpesa_receipt = None
                phone_number = None

                # Extract metadata values
                for item in callback_metadata:
                    if item["Name"] == "Amount":
                        amount = item["Value"]
                    elif item["Name"] == "MpesaReceiptNumber":
                        mpesa_receipt = item["Value"]
                    elif item["Name"] == "PhoneNumber":
                        phone_number = item["Value"]

                # Find order by amount and phone number (assuming match exists)
                order = Order.objects.filter(order_total=amount, order_id=order_id).first()
                print("Order found:", order)  # Debugging
                if order:
                    order.payment.payment_status = "True"  # Set payment status to False
                    order.save()
                    print("Order updated successfully")
                    print("M-Pesa Receipt:", mpesa_receipt)
                    print(order.payment.payment_status)

                    return JsonResponse({"message": "Payment successful", "receipt": mpesa_receipt}, status=200)
                else:
                    return JsonResponse({"error": "Order not found for payment"}, status=404)
            else:
                messages.error(request, "Payment failed")
                return redirect('order', order_id=order_id)

        except Exception as e:
            print("Error in callback:", str(e))
            return JsonResponse({"error": "Invalid data"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)
