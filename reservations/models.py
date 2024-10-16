import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import uuid


# Modèle pour les articles du panier
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer = models.ForeignKey('Offer', on_delete=models.CASCADE)  # Renommé de Offer à offer
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.offer.name} - {self.quantity}"

    class Meta:
        unique_together = ('user', 'offer')  # Assure qu'une offre peut être ajoutée une seule fois par utilisateur


# Vue pour ajouter une offre au panier
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


# Vue pour afficher le panier
@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    items = []

    # Récupérer les détails de chaque offre dans le panier
    for offer_id, quantity in cart.items():
        offer = get_object_or_404(Offer, id=offer_id)
        items.append({'offer': offer, 'quantity': quantity})

    return render(request, 'cart.html', {'items': items})


# Vue pour retirer un article du panier
@login_required
def remove_from_cart(request, offer_id):
    cart = request.session.get('cart', {})

    if offer_id in cart:
        del cart[offer_id]  # Retirer l'offre du panier
        request.session['cart'] = cart  # Enregistrer les modifications dans la session
        messages.success(request, "L'offre a été retirée du panier.")

    return redirect('view_cart')  # Rediriger vers la vue du panier


# Vue pour vider le panier
@login_required
def clear_cart(request):
    request.session['cart'] = {}  # Vider le panier
    messages.success(request, "Votre panier a été vidé.")
    return redirect('view_cart')  # Rediriger vers la vue du panier


# Modèle pour les offres
class Offer(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


# Modèle pour les tickets
class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    purchase_key = models.UUIDField(default=uuid.uuid4, editable=False)
    final_key = models.UUIDField(editable=False, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True)

    def save(self, *args, **kwargs):
        if not self.final_key:
            self.final_key = uuid.uuid4()  # clé unique pour le billet

        # Générer le QR code basé sur la final_key
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(self.final_key))
        qr.make(fit=True)

        # Créer l'image du QR code
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer)
        file_name = f'qr_code_{self.id}.png'
        self.qr_code.save(file_name, File(buffer), save=False)

        super(Ticket, self).save(*args, **kwargs)



