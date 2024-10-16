from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),  # Page d'accueil
    path('signup/', views.signup, name='signup'),
    path('finalize-order/<int:offer_id>/', views.finalize_order, name='finalize_order'),
    path('add-to-cart/<int:offer_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:offer_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'), # URL pour la page de connexion
    path('checkout/<int:offer_id>/', views.checkout, name='checkout'),
    path('confirmation/<int:ticket_id>/', views.confirmation, name='confirmation'),
    path('remove-from-cart/<int:offer_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'), 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

