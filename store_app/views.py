

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from store_app.models import Product, Categorie
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from cart.cart import Cart
from store_app.models import Order, Delivery, Wishlist, OrderItem
from django.contrib.auth import login
from django.http import HttpResponse


def index(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'main/index.html', context)


class AuthView(View):
    def get(self, request):
        return render(request, 'register/auth.html')


def BASE(request):
    return render(request, 'main/base.html')


def HOME(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'main/index.html', context)


def product(request):
    products = Product.objects.all()
    categories = Categorie.objects.all()
    CATID = request.GET.get('category')
    if CATID:
        products = Product.objects.filter(categorie=CATID)
    else:
        products = Product.objects.all()

    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'main/product.html', context)


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if User.objects.filter(email=email).exists():
            return render(request, 'register/auth.html', {'error_message': 'Email address is already in use'})

        # Check if passwords match
        if pass1 != pass2:
            return render(request, 'register/auth.html', {'error_message': 'Passwords do not match'})

        # Set a default yedi not provided
        if not username:
            username = email.split('@')[0]

        # Create a new user
        customer = User.objects.create_user(username, email, pass1)
        customer.first_name = first_name
        customer.last_name = last_name
        customer.save()

        return redirect('register')

    return render(request, 'register/auth.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'register/auth.html', {'error_message': 'Invalid login credentials'})


def help_page(request):
    return render(request, 'main/help.html')


def user_logout(request):
    logout(request)
    return redirect('home')


def detail_page(request):
    return render(request, 'main/detail.html')


def about_page(request):
    return render(request, 'main/about.html')


def search(request):
    query = request.GET.get('search')
    products = Product.objects.filter(name__icontains=query)

    context = {
        'products': products,
    }

    return render(request, 'main/search.html', context)


@login_required(login_url="/main/register/auth/")
def cart_add(request, product_id):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        cart = Cart(request)
        product = Product.objects.get(id=product_id)
        cart.add(product=product)

        # Return JSON response indicating success
        return JsonResponse({'success': True})
    else:
        return redirect("home")


@login_required(login_url="/main/register/auth/")
@login_required(login_url="/main/register/auth/")
def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)

    # Calculate total price after removing the item
    total_price = calculate_total_price(cart)

    # Return JSON response with updated total price
    return JsonResponse({'total_price': total_price})


@login_required(login_url="/main/register/auth/")
def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="/main/register/auth/")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")


@login_required(login_url="/main/register/auth/")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


@login_required(login_url="/main/register/auth/")
def cart_detail(request):
    cart = Cart(request)
    total_price = calculate_total_price(cart)  # Calculate total price
    return render(request, 'cart/cart_detail.html', {'cart': cart, 'total_price': total_price})


# Calculate total price based on items in the cart
def calculate_total_price(cart):
    total_price = 0
    for product_id, item in cart.cart.items():
        product = Product.objects.get(id=product_id)
        total_price += product.price * item['quantity']
    return total_price


@login_required
def userprofile(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    deliveries = Delivery.objects.filter(order__user=user)
    wishlist, created = Wishlist.objects.get_or_create(user=user)

    context = {
        'user': user,
        'orders': orders,
        'deliveries': deliveries,
        'wishlist': wishlist,
    }

    return render(request, 'main/userprofile.html', context)


def update_total_price(request):
    # Check if the request is a POST request and has the 'HTTP_X_REQUESTED_WITH' header set to 'XMLHttpRequest'
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        # Calculate total price here
        cart = Cart(request)
        total_price = calculate_total_price(cart)

        return JsonResponse({'total_price': total_price})
    else:
        # Handle non-AJAX requests appropriately
        # For example, return a 404 Not Found response
        return JsonResponse({'error': 'Not Found'}, status=404)


from django.shortcuts import render


def remove_from_cart(request, product_id):
    if request.method == "POST" and request.user.is_authenticated:
        cart = Cart(request)
        product = Product.objects.get(id=product_id)  # Assuming you have a Product model
        cart.remove(product)
        return render(request, 'cart/cart_detail.html', {'cart': cart})


def about(request):
    return render(request, 'main/about.html')


@login_required
def place_order(request):
    # Retrieve cart from the session
    cart = request.session.get('cart', {})

    if not cart:
        return HttpResponse("Your cart is empty.", status=400)

    total_price = 0
    cart_items = []

    for product_id, details in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = details['quantity']
            price = product.price
            total_price += price * quantity
            cart_items.append({'product': product, 'quantity': quantity, 'price': price})
        except Product.DoesNotExist:
            continue  # Skip any invalid product IDs in the cart

    # Create an order
    order = Order.objects.create(
        user=request.user,
        total_price=total_price,
        status='Pending'
    )

    # Create OrderItems for each product
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            price=item['price']
        )

    # Clear the cart
    request.session['cart'] = {}
    request.session.modified = True

    return HttpResponse("Order placed successfully!")


from django.shortcuts import render, get_object_or_404
from .models import Product, images, tag


def product_detail(request, product_id):
    # Fetch the product by its ID
    product = get_object_or_404(Product, id=product_id)

    # Fetch the related images and tags
    product_images = images.objects.filter(product=product)
    product_tags = tag.objects.filter(product=product)

    # Fetch similar products from the same category
    similar_products = Product.objects.filter(categorie=product.categorie).exclude(id=product_id)[:4]

    context = {
        'product': product,
        'product_images': product_images,
        'product_tags': product_tags,
        'similar_products': similar_products
    }

    return render(request, 'main/detail.html', context)


import hmac
import hashlib
import base64
import uuid
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Order, ESEWATransaction
from django.conf import settings
import requests


def generate_esewa_signature(total_amount, transaction_uuid, product_code):
    """Simulate signature generation for local testing"""
    # Just return a static signature for testing
    return "test_signature_123"

@login_required
def esewa_payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)

        # Generate transaction UUID
        transaction_uuid = str(uuid.uuid4())

        # Convert total price to integer
        total_amount = int(float(order.total_price))

        # Generate signature
        signature = generate_esewa_signature(
            total_amount=str(total_amount),
            transaction_uuid=transaction_uuid,
            product_code="EPAYTEST"
        )

        # Save transaction details
        transaction = ESEWATransaction.objects.create(
            user=request.user,  # Store user
            order=order,
            transaction_id=transaction_uuid,
            amount=total_amount,
            status='PENDING'
        )

        # Prepare sandbox payment data
        esewa_payment_data = {
            'amount': str(total_amount),
            'tax_amount': "0",
            'total_amount': str(total_amount),
            'transaction_uuid': transaction_uuid,
            'product_code': "EPAYTEST",
            'product_service_charge': "0",
            'product_delivery_charge': "0",
            'success_url': request.build_absolute_uri('/esewa-success/'),
            'failure_url': request.build_absolute_uri('/esewa-failure/'),
            'signed_field_names': 'total_amount,transaction_uuid,product_code',
            'signature': signature,
            'username': request.user.username,  # Include username
        }

        return render(request, 'register/esewa_payment.html', {
            'payment_data': esewa_payment_data,
            'sandbox_mode': True
        })

    except Order.DoesNotExist:
        return redirect('cart_detail')
@csrf_exempt
def esewa_success(request):
    if request.method == 'GET':
        try:
            transaction_uuid = request.GET.get('transaction_uuid')
            transaction = ESEWATransaction.objects.get(transaction_id=transaction_uuid)

            # Mark transaction as successful
            transaction.status = 'SUCCESS'
            transaction.save()

            # Update order status
            order = transaction.order
            order.payment_done = True
            order.payment_method = 'eSewa'
            order.status = "Confirmed"
            order.save()

            # Clear Cart
            if 'cart' in request.session:
                del request.session['cart']
            request.session.modified = True

            return render(request, 'register/success.html', {
                'order': order,
                'transaction': transaction,
                'username': transaction.user.username if transaction.user else "Guest"  # Include username
            })

        except ESEWATransaction.DoesNotExist:
            return redirect('cart_detail')

    return redirect('cart_detail')

@csrf_exempt
def esewa_failure(request):
    if request.method == 'GET':
        try:
            transaction_uuid = request.GET.get('transaction_uuid')
            transaction = ESEWATransaction.objects.get(transaction_id=transaction_uuid)
            transaction.status = 'FAILED'
            transaction.save()

            return render(request, 'register/payment_failed.html', {
                'order': transaction.order,
                'transaction': transaction
            })
        except ESEWATransaction.DoesNotExist:
            pass

    return redirect('cart_detail')
@login_required
def checkout(request):
    if request.method == "POST":
        try:
            cart = request.session.get('cart', {})
            if not cart:
                return redirect('cart_detail')

            cart_items = [
                {
                    'product_id': key,
                    'name': value['name'],
                    'price': float(value['price']),
                    'quantity': int(value['quantity']),
                    'image': value.get('image', '')
                }
                for key, value in cart.items()
            ]

            total_price = sum(item['price'] * item['quantity'] for item in cart_items)

            # Create Order
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                status='Pending'
            )

            # Create Order Items
            for item in cart_items:
                product = Product.objects.get(id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price']
                )

            # After creating the order, redirect to checkout page
            return render(request, 'register/checkout.html', {'order': order, 'cart_items': cart_items, 'total_price': total_price})

        except Exception as e:
            return render(request, 'register/checkout.html', {'error_message': str(e)})

    return render(request, 'register/checkout.html')
