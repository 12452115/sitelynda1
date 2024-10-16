from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class UserSignupTest(TestCase):

    def test_signup(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password1': 'mypassword',
            'password2': 'mypassword'
        })
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
class UserLoginTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='mypassword')

    def test_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'mypassword'
        })
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        self.assertTrue(response.wsgi_request.user.is_authenticated)

from .models import Offer, Ticket

class FinalizeOrderTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='mypassword')
        self.offer = Offer.objects.create(name='Offer 1', price=50)

    def test_finalize_order_authenticated(self):
        self.client.login(username='testuser', password='mypassword')
        response = self.client.post(reverse('finalize-order', args=[self.offer.id]))
        self.assertEqual(response.status_code, 302)  # Redirection après commande
        self.assertTrue(Ticket.objects.filter(user=self.user, offer=self.offer).exists())
    
    def test_finalize_order_unauthenticated(self):
        response = self.client.get(reverse('finalize-order', args=[self.offer.id]))
        self.assertEqual(response.status_code, 302)  # Redirection vers login
        self.assertRedirects(response, f'/login/?next=/finalize-order/{self.offer.id}/')

class QRCodeTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='mypassword')
        self.offer = Offer.objects.create(name='Offer 1', price=50)

    def test_qr_code_generation(self):
        self.client.login(username='testuser', password='mypassword')
        response = self.client.post(reverse('finalize-order', args=[self.offer.id]))
        ticket = Ticket.objects.get(user=self.user, offer=self.offer)
        self.assertIsNotNone(ticket.qr_code)  # Vérifie que le QR code est généré


