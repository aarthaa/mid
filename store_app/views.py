

import hmac
import json
from django.conf import settings
from .models import Order, ESEWATransaction
import uuid
import base64
import hashlib
from .models import Order, Product, OrderItem
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
from store_app.models import Order, Delivery, Wishlist, OrderItem
from django.contrib.auth import login
from rapidfuzz import process
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Product, images, tag
from cart.cart import Cart
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


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
    products = Product.objects.filter(
        stock='IN STOCK')  # showing instock product
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


def calback(request):
    try:
        print("k xa mero chali rako xa ")
        pass
    except Exception as e:
        return f"{e}"


def user_logout(request):
    logout(request)
    return redirect('home')


def detail_page(request):
    return render(request, 'main/detail.html')


def about_page(request):
    return render(request, 'main/about.html')


# used fuzzy algo for search
def search(request):
    query = request.GET.get('search', '')
    products = Product.objects.all()

    if query:
        product_names = list(products.values_list('name', flat=True))
        matched_names = process.extract(query, product_names, limit=10)
        matched_names = [name[0] for name in matched_names if name[1] > 50]

        products = products.filter(name__in=matched_names)
    else:
        return

    return render(request, 'main/search.html', {'products': products})


@login_required(login_url="/main/register/auth/")
def cart_add(request, product_id):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        cart = Cart(request)
        product = Product.objects.get(id=product_id)
        if product.stock == "OUT OF STOCK":
            return JsonResponse({"message": "Out of stock"})
        cart.add(product=product)
        return JsonResponse({"message": "Added To Cart.", 'success': True})

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


# total price calculation based on items in the cart
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


def remove_from_cart(request, product_id):
    if request.method == "POST" and request.user.is_authenticated:
        cart = Cart(request)
        # Assuming you have a Product model
        product = Product.objects.get(id=product_id)
        cart.remove(product)
        return render(request, 'cart/cart_detail.html', {'cart': cart})


def about(request):
    return render(request, 'main/about.html')


@login_required
def place_order(request):
    if request.method == "POST":
        # Get the order data from the request
        order_data_json = request.POST.get('order_data')

        # If order data is empty, return an error message
        if not order_data_json:
            return JsonResponse({"error": "No items selected for the order."}, status=400)

        # Deserialize the order data from JSON
        order_data = json.loads(order_data_json)

        total_price = 0
        cart_items = []

        # Loop through the order data to calculate the total price and prepare order items
        for item in order_data:
            try:
                product = Product.objects.get(id=item['id'])
                quantity = item['quantity']
                # Use product.price, not item['price'] from the frontend!
                price = product.price
                total_price += price * quantity
                cart_items.append(
                    {'product': product, 'quantity': quantity, 'price': price})
            except Product.DoesNotExist:
                return JsonResponse({"error": f"Product with id {item['id']} not found."}, status=400)

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

        # Return the order_id in the response
        return JsonResponse({
            "success": True,
            "order_id": order.id,
            "total_price": total_price
        }, status=200)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)


def product_detail(request, product_id):
    # Fetch the product by its ID
    product = get_object_or_404(Product, id=product_id)

    # Fetch the related images and tags
    product_images = images.objects.filter(product=product)
    product_tags = tag.objects.filter(product=product)

    # Fetch similar products from the same category
    similar_products = Product.objects.filter(
        categorie=product.categorie).exclude(id=product_id)[:4]

    context = {
        'product': product,
        'product_images': product_images,
        'product_tags': product_tags,
        'similar_products': similar_products
    }

    return render(request, 'main/detail.html', context)


@login_required
def checkout(request):
    if request.method == "POST":
        try:
            # Get the cart from session
            cart = request.session.get('cart', {})
            if not cart:
                # Redirect to cart page if no items in cart
                return redirect('cart_detail')
            # Prepare cart items data
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
            # Calculate total price
            total_price = sum(item['price'] * item['quantity']
                              for item in cart_items)

            # Create a new order
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                status='Pending'
            )
            print("test", order)
            # Create order items for each product in the cart
            for item in cart_items:
                product = Product.objects.get(id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price']
                )
                # Redirect to payment page or checkout confirmation page
            return render(request, 'register/checkout.html', {
                'order': order,
                'cart_items': cart_items,
                'total_price': total_price
            })

        except Exception as e:
            print(f"error hai:{e}")
            return render(request, 'register/checkout.html', {'error_message': str(e)})

    return render(request, 'register/checkout.html')


class SecureDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Secure data accessed successfully"}, status=status.HTTP_200_OK)

    def post(self, request):
        # Process the incoming data
        data = request.data
        # Your logic here

        return Response({"message": "Data received and processed"}, status=status.HTTP_201_CREATED)


def generate_esewa_signature(total_amount, transaction_uuid, product_code):
    """
    Generate a signature for eSewa sandbox testing using HMAC-SHA256.
    """
    secret_key = "8gBm/:&EnhH.1/q"  # Replace with actual eSewa merchant secret key

    # Correct concatenation format (match `signed_field_names`)
    data_string = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"

    # Generate HMAC signature
    signature = hmac.new(
        secret_key.encode(),
        data_string.encode(),
        hashlib.sha256
    ).digest()

    # Return base64 encoded signature
    return base64.b64encode(signature).decode('utf-8')


# Example usage
print(generate_esewa_signature("100", "123456789", "TEST_PRODUCT"))


@login_required
def esewa_payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)

        # Generate transaction UUID
        # Match 6-digit format like "241028"
        transaction_uuid = str(uuid.uuid4())[:6]

        # Convert total price to integer (eSewa requires integer, hence rounding it)
        # Ensure it's in the smallest unit (e.g., paise for Nepal)
        total_amount = int(float(order.total_price))

        # Tax amount and other charges (if any)
        tax_amount = 0  # Example tax
        final_amount = total_amount + tax_amount  # Final amount to be paid

        # Product code for sandbox (example)
        product_code = "EPAYTEST"

        # Generate signature
        signature = generate_esewa_signature(
            total_amount=str(final_amount),
            transaction_uuid=transaction_uuid,
            product_code=product_code
        )

        # Prepare eSewa payment data
        payment_data = {
            # Total amount, converted to smallest unit (integer)
            "total_amount": str(final_amount),
            "transaction_uuid": transaction_uuid,  # Unique Transaction ID
            "product_code": product_code,  # Product code for the test
            # Base amount (this might be same as total_amount, without tax)
            "amount": str(total_amount),
            "tax_amount": "0",  # Tax Amount (if any)
            # Service charge (if any)
            "product_service_charge": "0",
            # Delivery charge (if any)
            "product_delivery_charge": "0",
            "success_url": "https://developer.esewa.com.np/success",  # Redirect URL
            "failure_url": "https://developer.esewa.com.np/failure",  # Redirect URL
            "signed_field_names": "total_amount,transaction_uuid,product_code",  # Signed fields
            "signature": signature  # HMAC-SHA256 Signature
        }

        # eSewa sandbox API URL
        sandbox_url = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"

        # Render the payment form
        return render(request, 'register/esewa_payment.html', {
            'payment_data': payment_data,
            'sandbox_url': sandbox_url
        })

    except Order.DoesNotExist:
        return redirect('cart_detail')

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def esewa_success(request):
    if request.method == 'GET':
        try:
            transaction_uuid = request.GET.get('transaction_uuid')
            transaction = ESEWATransaction.objects.get(
                transaction_id=transaction_uuid)

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
                'username': transaction.user.username if transaction.user else "Guest"
            })

        except ESEWATransaction.DoesNotExist:
            return redirect('cart_detail')

    return redirect('cart_detail')


@csrf_exempt
def esewa_failure(request):
    if request.method == 'GET':
        try:
            transaction_uuid = request.GET.get('transaction_uuid')
            transaction = ESEWATransaction.objects.get(
                transaction_id=transaction_uuid)
            transaction.status = 'FAILED'
            transaction.save()

            return render(request, 'register/payment_failed.html', {
                'order': transaction.order,
                'transaction': transaction
            })
        except ESEWATransaction.DoesNotExist:
            pass

    return redirect('cart_detail')
