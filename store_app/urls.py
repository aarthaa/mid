
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import AuthView
from .views import item_clear






urlpatterns = [


    path('', views.HOME, name='home'),
    path('index/', views.index, name="index"),
    path('base/', views.BASE, name='base'),
    path('product/', views.product, name='product'),
    path('register/', views.register, name='register'),
    path('main/register/auth/', AuthView.as_view(), name='auth'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('search/', views.search, name='search'),
    path('product/<int:category_id>/', views.product, name='product'),
    path('cart/cart_detail/', views.cart_detail, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('userprofile/', views.userprofile, name='userprofile'),
    path('checkout/', views.checkout, name='checkout'),
    path('about/', views.about, name='aboutus'),


    path('cart_clear/', views.cart_clear, name='cart_clear'),
    path('place_order/', views.place_order, name='place_order'),
    path('cart/item_clear/<int:id>/', item_clear, name='item-clear'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove-from-cart'),

    path('help/', views.help_page, name='help'),

    path('detail/', views.detail_page, name='detail'),
    path('about/', views.about_page, name='about'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


