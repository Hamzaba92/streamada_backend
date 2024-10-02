from django.test import TestCase

from django.test import TestCase
from django.core.cache import cache

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
