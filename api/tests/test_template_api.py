from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from api.serializers import TemplateSerializer
from rest_framework.test import APIClient
from rest_framework import status
from journal.models import Template


TEMPLATE_URL = reverse('api:template-list')

def detail_url(uuid):
    """Return template detail URL"""
    return reverse('api:template-detail', args=[uuid])


class PublicTemplateApiTests(TestCase):
    """Test the publicly available template API"""

    def setUp(self):
        self.client = APIClient()


class PrivateTemplateApiTests(TestCase):
    """Test the authorized user Template API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@action.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    
    def test_create_template_successful(self):
        """Test creating a new template"""
        payload = {
            'title': 'Test template',
            'slug': 'test-template',
            'description': 'Test description'
        }
        res = self.client.post(TEMPLATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


    def test_create_template_invalid(self):
        """Test creating a new template with invalid payload"""
        payload = {'title': ''}
        res = self.client.post(TEMPLATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_delete_template(self):
        """Test deleting a template"""
        template = Template.objects.create(
            title='Test template',
            slug='test-template',
            description='Test description',
            created_by=self.user
        )
        url = detail_url(template.uuid)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


    def test_update_template(self):
        """Test updating a template"""
        template = Template.objects.create(
            title='Test template',
            slug='test-template',
            description='Test description',
            created_by=self.user
        )
        payload = {'title': 'Updated template'}
        url = detail_url(template.uuid)
        self.client.patch(url, payload)
        template.refresh_from_db()
        self.assertEqual(template.title, payload['title'])
