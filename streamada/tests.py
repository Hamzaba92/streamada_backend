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
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from streamada.models import Video
from streamada.serializers import VideoSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
import uuid
from unittest import mock
from streamada.tasks import delete_original_file
import os
import subprocess
from streamada.tasks import convert_video
from streamada.signals import auto_delete_file_on_delete



User = get_user_model()

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
        url = reverse('activate', kwargs={'uidb64': self.uidb64, 'token': self.token})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, 'http://localhost:4200/login')
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activate_user_invalid_token(self):
        """
        Test that activation fails with an invalid token.
        """
        url = reverse('activate', kwargs={'uidb64': self.uidb64, 'token': 'invalid-token'})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid activation link')
        
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
    
    def test_activate_user_invalid_uid(self):
        """
        Test that activation fails with an invalid UID.
        """
        url = reverse('activate', kwargs={'uidb64': 'invalid-uid', 'token': self.token})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid activation link')
        
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)



class LoginUserTest(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com', 
            password='testpass123',
            is_active=True
        )



class PasswordResetViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('password_reset')

def test_password_reset_valid_email(self):
    valid_email = {'email': 'valid@example.com'}
    user = User.objects.create_user(username=valid_email['email'], email=valid_email['email'], password='password123')

    response = self.client.post(self.url, data=valid_email, format='json')

    print(response.status_code)
    print(response.json())

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.json()['detail'], 'Password reset link has been sent.')



class PasswordResetConfirmViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('confirm-new-pw')

        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='old_password123')

        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = PasswordResetTokenGenerator().make_token(self.user)

    def test_password_reset_confirm_valid(self):
        valid_data = {
            'uid': self.uid,
            'token': self.token,
            'new_password': 'new_password123',
            'confirm_password': 'new_password123'
        }

        response = self.client.post(self.url, data=valid_data, format='json')

        print(response.status_code)
        print(response.json())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['detail'], 'Password has been reset successfully.')

    def test_password_reset_confirm_invalid(self):
        invalid_data = {
            'uid': self.uid,
            'token': self.token,
            'new_password': 'new_password123',
            'confirm_password': 'different_password123'
        }

        response = self.client.post(self.url, data=invalid_data, format='json')

        print(response.status_code)
        print(response.json())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['detail'], 'Password has been reset successfully.')



class VideoListAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('video-list')

        video_file1 = SimpleUploadedFile(f"{uuid.uuid4()}_file1.mp4", b"file_content", content_type="video/mp4")
        video_file2 = SimpleUploadedFile(f"{uuid.uuid4()}_file2.mp4", b"file_content", content_type="video/mp4")

        self.video1 = Video.objects.create(
            title="Video 1", 
            description="Beschreibung 1", 
            genre="Abstract", 
            video_file=video_file1
        )
        self.video2 = Video.objects.create(
            title="Video 2", 
            description="Beschreibung 2", 
            genre="Abstract",
            video_file=video_file2
        )

    def test_video_list(self):
        response = self.client.get(self.url)

        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)

        print(response.status_code)
        print(response.json())

        for response_video, expected_video in zip(response.json(), serializer.data):
            self.assertEqual(response_video['title'], expected_video['title'])
            self.assertEqual(response_video['description'], expected_video['description'])
            self.assertEqual(response_video['genre'], expected_video['genre'])



class DeleteOriginalFileTest(TestCase):
    @mock.patch('os.remove') 
    @mock.patch('os.path.isfile')
    def test_delete_existing_file(self, mock_isfile, mock_remove):
        mock_isfile.return_value = True
        file_path = "/path/to/existing/file.mp4"

        delete_original_file(file_path)

        mock_remove.assert_called_once_with(file_path)
        print("Test: Existing file - passed")

    @mock.patch('os.remove')
    @mock.patch('os.path.isfile')
    def test_file_does_not_exist(self, mock_isfile, mock_remove):
        mock_isfile.return_value = False
        file_path = "/path/to/nonexistent/file.mp4"

        delete_original_file(file_path)

        mock_remove.assert_not_called()
        print("Test: Non-existent file - passed")

    @mock.patch('os.remove')
    @mock.patch('os.path.isfile')
    def test_delete_file_with_exception(self, mock_isfile, mock_remove):
        mock_isfile.return_value = True
        file_path = "/path/to/file_with_error.mp4"

        mock_remove.side_effect = Exception("Test exception")

        delete_original_file(file_path)

        mock_remove.assert_called_once_with(file_path)
        print("Test: File deletion with exception - passed")



class ConvertVideoTest(TestCase):
    @mock.patch('subprocess.run') 
    def test_convert_video(self, mock_subprocess):
        source = "/path/to/source/file.mp4"
        resolution = "1280x720"
        label = "720p"
        
        expected_target = "/path/to/source/file_720p.mp4"

        result = convert_video(source, resolution, label)

        expected_cmd = f'ffmpeg -i "{source}" -s {resolution} -c:v libx264 -crf 23 -c:a aac -strict -2 "{expected_target}"'
        mock_subprocess.assert_called_once_with(expected_cmd, shell=True)

        self.assertEqual(result, expected_target)
        print("Test: Convert video - passed")



class AutoDeleteFileOnDeleteTest(TestCase):
    @mock.patch('os.remove')
    @mock.patch('os.path.isfile')
    def test_auto_delete_file_on_delete(self, mock_isfile, mock_remove):
        video = Video(video_file=mock.MagicMock(path="/path/to/video.mp4"), thumbnail=mock.MagicMock(path="/path/to/thumbnail.jpg"))

        mock_isfile.side_effect = lambda path: path in [
            "/path/to/video_480p.mp4",
            "/path/to/video_720p.mp4",
            "/path/to/video_1080p.mp4",
            "/path/to/thumbnail.jpg"
        ]
        auto_delete_file_on_delete(Video, video)
        mock_remove.assert_any_call("/path/to/video_480p.mp4")
        mock_remove.assert_any_call("/path/to/video_720p.mp4")
        mock_remove.assert_any_call("/path/to/video_1080p.mp4")
        mock_remove.assert_any_call("/path/to/thumbnail.jpg")

        self.assertEqual(mock_remove.call_count, 6)



class VideoModelTest(TestCase):
    def setUp(self):
        self.video = Video.objects.create(
            title="Test Video",
            description="This is a test video description.",
            genre="Abstract",
            video_file="videos/test_video.mp4",
            thumbnail="thumbnails/test_thumbnail.jpg",
            add_to_new_video_feed=True
        )

    def test_video_creation(self):
        self.assertEqual(self.video.title, "Test Video")
        self.assertEqual(self.video.description, "This is a test video description.")
        self.assertEqual(self.video.genre, "Abstract")
        self.assertEqual(self.video.video_file, "videos/test_video.mp4")
        self.assertEqual(self.video.thumbnail, "thumbnails/test_thumbnail.jpg")
        self.assertTrue(self.video.add_to_new_video_feed)

    def test_video_str_method(self):
        expected_str = "[Genre]: Abstract,  [Title]: Test Video"
        self.assertEqual(str(self.video), expected_str)



class APITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

        self.video = Video.objects.create(
            title="Test Video",
            description="Test Description",
            genre="Abstract",
            video_file="videos/test_video.mp4"
        )

def test_register_user(self):
    url = reverse('register_user')
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'newpassword',
        'password2': 'newpassword'
    }
    response = self.client.post(url, data, format='json')
    print(response.json()) 
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

def test_login_user(self):
    url = reverse('login')
    data = {
        'email': 'test@example.com',
        'password': 'testpassword'
    }
    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertIn('token', response.json())

def test_password_reset(self):
    url = reverse('password_reset')
    data = {
            'email': 'test@example.com'
        }
    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_200_OK)

def test_confirm_new_password(self):
    url = reverse('confirm-new-pw')
    data = {
            'uid': 'valid_uid',
            'token': 'valid_token',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_200_OK)

def test_video_list(self):
    url = reverse('video-list')
    response = self.client.get(url, format='json')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(len(response.json()), 1) 
    self.assertEqual(response.json()[0]['title'], "Test Video")