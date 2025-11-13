from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from journal.models import Template


class PrivateTemplateFieldApiTests(TestCase):
    """Test the authorized user Template Field API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "test@action.com", "password123"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.template = Template.objects.create(
            title="Daily Journal",
            slug="daily-journal",
            description="Daily journal template",
            created_by=self.user,
        )

    def test_create_template_field_successful(self):
        """Test creating a new template field"""
        payload = {
            "template": self.template.uuid,
            "name": "Daily Mood",
            "field_type": "text",
            "order": 1,
            "is_required": True,
        }
        url = reverse("api:templatefield-list")
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], payload["name"])
        self.assertEqual(res.data["field_type"], payload["field_type"])

    def test_create_template_field_with_category(self):
        """Test creating a template field with category"""
        from journal.models import Category

        category = Category.objects.create(name="Health", created_by=self.user)
        payload = {
            "template": self.template.uuid,
            "name": "Exercise Duration",
            "field_type": "number",
            "category": category.id,
            "order": 2,
        }
        url = reverse("api:templatefield-list")
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["category"], category.id)

    def test_create_template_field_minimal(self):
        """Test creating a template field with minimal data"""
        payload = {
            "template": self.template.uuid,
            "name": "Notes",
            "field_type": "text",
        }
        url = reverse("api:templatefield-list")
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["order"], 0)
        self.assertEqual(res.data["is_required"], False)

    def test_create_template_field_all_types(self):
        """Test creating template fields with all field types"""
        field_types = ["text", "number", "date", "boolean"]
        url = reverse("api:templatefield-list")

        for field_type in field_types:
            payload = {
                "template": self.template.uuid,
                "name": f"Test {field_type}",
                "field_type": field_type,
            }
            res = self.client.post(url, payload)
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            self.assertEqual(res.data["field_type"], field_type)

    def test_retrieve_template_fields(self):
        """Test retrieving a list of template fields"""
        from journal.models import TemplateField

        TemplateField.objects.create(
            template=self.template, name="Field 1", field_type="text"
        )
        TemplateField.objects.create(
            template=self.template, name="Field 2", field_type="number"
        )
        url = reverse("api:templatefield-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_template_field_detail(self):
        """Test retrieving a template field detail"""
        from journal.models import TemplateField

        field = TemplateField.objects.create(
            template=self.template, name="Mood Rating", field_type="number"
        )
        url = reverse("api:templatefield-detail", args=[field.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], field.name)

    def test_update_template_field(self):
        """Test updating a template field"""
        from journal.models import TemplateField

        field = TemplateField.objects.create(
            template=self.template, name="Original Name", field_type="text"
        )
        payload = {"name": "Updated Name", "field_type": "number", "is_required": True}
        url = reverse("api:templatefield-detail", args=[field.id])
        res = self.client.patch(url, payload)
        field.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(field.name, payload["name"])
        self.assertEqual(field.field_type, payload["field_type"])
        self.assertEqual(field.is_required, payload["is_required"])

    def test_delete_template_field(self):
        """Test deleting a template field"""
        from journal.models import TemplateField

        field = TemplateField.objects.create(
            template=self.template, name="Test Field", field_type="text"
        )
        url = reverse("api:templatefield-detail", args=[field.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TemplateField.objects.filter(id=field.id).exists())

    def test_filter_template_fields_by_template(self):
        """Test filtering template fields by template"""
        from journal.models import TemplateField

        other_template = Template.objects.create(
            title="Other Template", slug="other-template", created_by=self.user
        )
        TemplateField.objects.create(
            template=self.template, name="My Field", field_type="text"
        )
        TemplateField.objects.create(
            template=other_template, name="Other Field", field_type="text"
        )
        url = reverse("api:templatefield-list")
        res = self.client.get(url, {"template": self.template.uuid})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], "My Field")

    def test_template_field_ordering(self):
        """Test that template fields are ordered correctly"""
        from journal.models import TemplateField

        TemplateField.objects.create(
            template=self.template, name="Field 3", field_type="text", order=3
        )
        TemplateField.objects.create(
            template=self.template, name="Field 1", field_type="text", order=1
        )
        TemplateField.objects.create(
            template=self.template, name="Field 2", field_type="text", order=2
        )
        url = reverse("api:templatefield-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]["name"], "Field 1")
        self.assertEqual(res.data[1]["name"], "Field 2")
        self.assertEqual(res.data[2]["name"], "Field 3")


class PublicTemplateFieldApiTests(TestCase):
    """Test the publicly available template field API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        url = reverse("api:templatefield-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
