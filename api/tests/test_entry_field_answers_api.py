from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from journal.models import Template


class PrivateEntryFieldAnswerApiTests(TestCase):
    """Test the authorized user Entry Field Answer API"""

    def setUp(self):
        from journal.models import TemplateField, JournalEntry

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

        self.field1 = TemplateField.objects.create(
            template=self.template,
            name="Mood",
            field_type="text",
            order=1,
            is_required=True,
        )

        self.field2 = TemplateField.objects.create(
            template=self.template,
            name="Energy Level",
            field_type="number",
            order=2,
        )

        self.entry = JournalEntry.objects.create(
            template=self.template,
            title="My Daily Entry",
            created_by=self.user,
        )

    def test_create_entry_field_answer_successful(self):
        """Test creating a new entry field answer"""
        payload = {
            "entry": self.entry.uuid,
            "field": self.field1.id,
            "value": "Happy",
        }
        url = reverse("api:entryfield_answer-list")
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["value"], payload["value"])
        self.assertEqual(res.data["field"], self.field1.id)

    def test_create_entry_field_answer_minimal(self):
        """Test creating an entry field answer with minimal data"""
        payload = {
            "entry": self.entry.uuid,
            "field": self.field2.id,
        }
        url = reverse("api:entryfield_answer-list")
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(res.data["value"])

    def test_create_duplicate_entry_field_answer_fails(self):
        """Test creating duplicate entry field answer fails"""
        from journal.models import EntryFieldAnswer

        EntryFieldAnswer.objects.create(
            entry=self.entry, field=self.field1, value="Happy"
        )

        payload = {
            "entry": self.entry.uuid,
            "field": self.field1.id,
            "value": "Sad",
        }
        url = reverse("api:entryfield_answer-list")
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_entry_field_answers(self):
        """Test retrieving a list of entry field answers"""
        from journal.models import EntryFieldAnswer

        EntryFieldAnswer.objects.create(
            entry=self.entry, field=self.field1, value="Happy"
        )
        EntryFieldAnswer.objects.create(entry=self.entry, field=self.field2, value="8")

        url = reverse("api:entryfield_answer-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_entry_field_answer_detail(self):
        """Test retrieving an entry field answer detail"""
        from journal.models import EntryFieldAnswer

        answer = EntryFieldAnswer.objects.create(
            entry=self.entry, field=self.field1, value="Excited"
        )

        url = reverse("api:entryfield_answer-detail", args=[answer.uuid])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["value"], "Excited")

    def test_update_entry_field_answer(self):
        """Test updating an entry field answer"""
        from journal.models import EntryFieldAnswer

        answer = EntryFieldAnswer.objects.create(
            entry=self.entry, field=self.field1, value="Happy"
        )

        payload = {"value": "Very Happy"}
        url = reverse("api:entryfield_answer-detail", args=[answer.uuid])
        res = self.client.patch(url, payload)
        answer.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(answer.value, payload["value"])

    def test_delete_entry_field_answer(self):
        """Test deleting an entry field answer"""
        from journal.models import EntryFieldAnswer

        answer = EntryFieldAnswer.objects.create(
            entry=self.entry, field=self.field1, value="Happy"
        )

        url = reverse("api:entryfield_answer-detail", args=[answer.uuid])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(EntryFieldAnswer.objects.filter(uuid=answer.uuid).exists())

    def test_filter_entry_field_answers_by_entry(self):
        """Test filtering entry field answers by entry"""
        from journal.models import EntryFieldAnswer, JournalEntry

        other_entry = JournalEntry.objects.create(
            template=self.template,
            title="Another Entry",
            created_by=self.user,
        )

        EntryFieldAnswer.objects.create(
            entry=self.entry, field=self.field1, value="Happy"
        )
        EntryFieldAnswer.objects.create(
            entry=other_entry, field=self.field1, value="Sad"
        )

        url = reverse("api:entryfield_answer-list")
        res = self.client.get(url, {"entry": self.entry.uuid})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["value"], "Happy")

    def test_filter_entry_field_answers_by_field(self):
        """Test filtering entry field answers by field"""
        from journal.models import EntryFieldAnswer

        EntryFieldAnswer.objects.create(
            entry=self.entry, field=self.field1, value="Happy"
        )
        EntryFieldAnswer.objects.create(entry=self.entry, field=self.field2, value="8")

        url = reverse("api:entryfield_answer-list")
        res = self.client.get(url, {"field": self.field1.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["field"], self.field1.id)

    def test_cannot_create_answer_for_other_user_entry(self):
        """Test that user cannot create answer for another user's entry"""
        from journal.models import JournalEntry

        other_user = get_user_model().objects.create_user(
            "other@action.com", "password123"
        )
        other_entry = JournalEntry.objects.create(
            template=self.template,
            title="Other User Entry",
            created_by=other_user,
        )

        payload = {
            "entry": other_entry.uuid,
            "field": self.field1.id,
            "value": "Happy",
        }
        url = reverse("api:entryfield_answer-list")
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PublicEntryFieldAnswerApiTests(TestCase):
    """Test the publicly available entry field answer API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        url = reverse("api:entryfield_answer-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
