from django.test import TestCase
from django.core.cache import cache
from django.urls import reverse
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.authtoken.models import Token



class CacheTestCase(TestCase):
    """Test if Redis works well with Django"""
    
    def test_cache_set_and_get(self):
        cache.set('my_key', 'my_value', timeout=60)
        
        cached_value = cache.get('my_key')
        self.assertEqual(cached_value, 'my_value')

    def test_cache_timeout(self):
        cache.set('temporary_key', 'temp_value', timeout=1)
        
        cached_value = cache.get('temporary_key')
        self.assertEqual(cached_value, 'temp_value')
        
        import time
        time.sleep(2)
        
        cached_value = cache.get('temporary_key')
        self.assertIsNone(cached_value)

    def tearDown(self):
        cache.clear()


class RegisterUserTest(APITestCase):
    def test_register_user_success(self):
        url = reverse('register_user')
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User successfully registered')
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(email='testuser@example.com')
        self.assertFalse(user.is_active)



class ActivateUserTest(APITestCase):
    
    def setUp(self):
        # Set up a user for testing, but initially inactive
        self.user = User.objects.create_user(
            username='testuser', 
            email='testuser@example.com', 
            password='testpass123',
            is_active=False
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
    
    def test_activate_user_success(self):
        """
        Test that a user is successfully activated with a valid token and UID.
        """
        # Generate activation URL with valid token and UID
        url = reverse('activate', kwargs={'uidb64': self.uidb64, 'token': self.token})
        
        response = self.client.get(url)
        
        # Check that the response redirects to the login page (user successfully activated)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, 'http://localhost:4200/login')
        
        # Reload the user from the database and check if they are active now
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activate_user_invalid_token(self):
        """
        Test that activation fails with an invalid token.
        """
        # Generate activation URL with an invalid token
        url = reverse('activate', kwargs={'uidb64': self.uidb64, 'token': 'invalid-token'})
        
        response = self.client.get(url)
        
        # Check that the response returns a 400 Bad Request status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid activation link')
        
        # Ensure the user is still inactive
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
    
    def test_activate_user_invalid_uid(self):
        """
        Test that activation fails with an invalid UID.
        """
        # Generate activation URL with an invalid UID
        url = reverse('activate', kwargs={'uidb64': 'invalid-uid', 'token': self.token})
        
        response = self.client.get(url)
        
        # Check that the response returns a 400 Bad Request status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid activation link')
        
        # Ensure the user is still inactive
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)



class LoginUserTest(APITestCase):
    
    def setUp(self):
        # Erstelle einen aktiven Benutzer mit E-Mail-Login
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',  # Verwende das Feld 'email'
            password='testpass123',
            is_active=True
        )



