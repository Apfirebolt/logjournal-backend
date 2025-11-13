from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from api.serializers import CategorySerializer
from rest_framework.test import APIClient
from rest_framework import status
from journal.models import Category


CATEGORY_URL = reverse('api:category-list')

def detail_url(uuid):
    """Return category detail URL"""
    return reverse('api:category-detail', args=[uuid])


class PublicCategoryApiTests(TestCase):
    """Test the publicly available category API"""

    def setUp(self):
        self.client = APIClient()


class PrivateCategoryApiTests(TestCase):
    """Test the authorized user Category API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@action.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    
    def test_create_category_successful(self):
        """Test creating a new category"""
        payload = {
            'name': 'Test category',
            'description': 'Test description'
        }
        res = self.client.post(CATEGORY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


    def test_create_category_invalid(self):
        """Test creating a new category with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_delete_category(self):
        """Test deleting a category"""
        category = Category.objects.create(
            name='Test category',
            description='Test description',
            created_by=self.user
        )
        url = detail_url(category.uuid)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


    def test_update_category(self):
        """Test updating a category"""
        category = Category.objects.create(
            name='Test category',
            description='Test description',
            created_by=self.user
        )
        payload = {'name': 'Updated category'}
        url = detail_url(category.uuid)
        self.client.patch(url, payload)
        category.refresh_from_db()
        self.assertEqual(category.name, payload['name'])
