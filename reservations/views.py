from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from .models import Ticket, Offer
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404


def home(request):
    offers = Offer.objects.all()  # Récupère toutes les offres disponibles
    return render(request, 'home.html', {'offers': offers})

# Vue pour l'inscription d'un utilisateur
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')  # Redirection vers la page d'accueil ou autre
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Connexion réussie !')
            return redirect('home')  # Redirige vers l'accueil après la connexion
        else:
            messages.error(request, 'Identifiants incorrects.')
            return redirect('login')
    return render(request, 'login.html')

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0  # Initialiser le total

    # Récupérer les détails de chaque offre dans le panier
    for offer_id, quantity in cart.items():
        offer = Offer.objects.get(id=offer_id)
        items.append({'offer': offer, 'quantity': quantity})
        total += offer.price * quantity  # Calculez le prix total ici

    return render(request, 'cart.html', {'items': items, 'total': total})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre compte a été créé. Vous pouvez maintenant vous connecter.')
            return redirect('login')  # Redirige vers la page de connexion après l'inscription
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def finalize_order(request, offer_id):
    offer = Offer.objects.get(id=offer_id)

    if request.method == 'POST':
        ticket = Ticket(user=request.user, offer=offer)
        ticket.save()  # Cela génère aussi le QR code
        return redirect('confirmation', ticket_id=ticket.id)  # Passer l'ID du ticket

    return render(request, 'finalize_order.html', {'offer': offer})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Si l'utilisateur est authentifié, on le connecte
            login(request, user)
            return redirect('home')  # Redirige vers la page d'accueil ou une autre vue après la connexion
        else:
            # Si l'authentification échoue, on affiche un message d'erreur
            return render(request, 'login.html', {'error': 'Nom d\'utilisateur ou mot de passe incorrect'})

    return render(request, 'login.html')

######
@login_required
def add_to_cart(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)

    # Si l'utilisateur a déjà un panier dans la session, on l'utilise
    cart = request.session.get('cart', {})

    if offer_id in cart:
        cart[offer_id] += 1  # Augmenter la quantité si l'offre est déjà dans le panier
    else:
        cart[offer_id] = 1  # Ajouter l'offre au panier avec une quantité de 1

    request.session['cart'] = cart  # Enregistrer le panier dans la session

    messages.success(request, f"L'offre '{offer.name}' a été ajoutée à votre panier.")
    return redirect('home')  # Redirige vers la page d'accueil ou vers une autre page

@login_required
def remove_from_cart(request, offer_id):
    cart = request.session.get('cart', {})

    if offer_id in cart:
        del cart[offer_id]  # Retirer l'offre du panier
        request.session['cart'] = cart  # Enregistrer les modifications dans la session
        messages.success(request, "L'offre a été retirée du panier.")

    return redirect('view_cart')  # Rediriger vers la vue du panier

@login_required
def clear_cart(request):
    """
    Cette vue permet de vider le panier.
    """
    # Vider le panier dans la session
    request.session['cart'] = {}

    # Ajouter un message de succès
    messages.success(request, "Votre panier a été vidé avec succès.")

    # Rediriger vers la vue du panier
    return redirect('view_cart')

@login_required
def checkout(request, offer_id):
    offer = Offer.objects.get(id=offer_id)

    if request.method == 'POST':
        # Simule le processus de paiement
        card_number = request.POST.get('card_number')
        expiry_date = request.POST.get('expiry_date')
        cvv = request.POST.get('cvv')

        # Logique fictive de traitement de paiement
        if card_number and expiry_date and cvv:
            # Si le paiement est validé, rediriger vers la finalisation de la commande
            return redirect('finalize_order', offer_id=offer.id)
        else:
            return render(request, 'checkout.html', {'offer': offer, 'error': 'Informations de paiement invalides.'})

    return render(request, 'checkout.html', {'offer': offer})

@login_required
def confirmation(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)  # Récupérer le ticket généré

    return render(request, 'confirmation.html', {'ticket': ticket})



