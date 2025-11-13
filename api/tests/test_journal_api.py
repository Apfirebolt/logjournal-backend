from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from api.serializers import JournalEntrySerializer
from rest_framework.test import APIClient
from rest_framework import status
from journal.models import JournalEntry, Template


JOURNAL_ENTRY_URL = reverse('api:journalentry-list')


class PrivateJournalEntryApiTests(TestCase):
    """Test the authorized user Journal Entry API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@action.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.template = Template.objects.create(
            title='Daily Journal',
            slug='daily-journal',
            description='Daily journal template',
            created_by=self.user
        )

    def test_create_journal_entry_successful(self):
        """Test creating a new journal entry"""
        payload = {
            'title': 'Test entry',
            'template': self.template.uuid,
            'quote_of_the_day': 'Test quote',
            'rate_your_day': 5
        }
        res = self.client.post(JOURNAL_ENTRY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_journal_entry_without_template(self):
        """Test creating a journal entry without template"""
        payload = {
            'title': 'Test entry',
            'quote_of_the_day': 'Test quote',
            'rate_your_day': 5
        }
        res = self.client.post(JOURNAL_ENTRY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_journal_entry_minimal(self):
        """Test creating a journal entry with minimal data"""
        payload = {}
        res = self.client.post(JOURNAL_ENTRY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_retrieve_journal_entries(self):
        """Test retrieving a list of journal entries"""
        JournalEntry.objects.create(
            title='Entry 1',
            created_by=self.user
        )
        JournalEntry.objects.create(
            title='Entry 2',
            created_by=self.user
        )
        res = self.client.get(JOURNAL_ENTRY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_journal_entry_detail(self):
        """Test retrieving a journal entry detail"""
        entry = JournalEntry.objects.create(
            title='Test entry',
            created_by=self.user,
            quote_of_the_day='Test quote'
        )
        url = journal_entry_detail_url(entry.uuid)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], entry.title)

    def test_update_journal_entry(self):
        """Test updating a journal entry"""
        entry = JournalEntry.objects.create(
            title='Original title',
            created_by=self.user
        )
        payload = {'title': 'Updated title', 'rate_your_day': 8}
        url = journal_entry_detail_url(entry.uuid)
        res = self.client.patch(url, payload)
        entry.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(entry.title, payload['title'])
        self.assertEqual(entry.rate_your_day, payload['rate_your_day'])

    def test_delete_journal_entry(self):
        """Test deleting a journal entry"""
        entry = JournalEntry.objects.create(
            title='Test entry',
            created_by=self.user
        )
        url = journal_entry_detail_url(entry.uuid)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(JournalEntry.objects.filter(uuid=entry.uuid).exists())

    def test_user_can_only_see_own_entries(self):
        """Test that users can only see their own journal entries"""
        other_user = get_user_model().objects.create_user(
            'other@action.com',
            'password123'
        )
        JournalEntry.objects.create(title='My entry', created_by=self.user)
        JournalEntry.objects.create(title='Other entry', created_by=other_user)
        
        res = self.client.get(JOURNAL_ENTRY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], 'My entry')


class PublicJournalEntryApiTests(TestCase):
    """Test the publicly available journal entry API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(JOURNAL_ENTRY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


def journal_entry_detail_url(uuid):
    """Return journal entry detail URL"""
    return reverse('api:journalentry-detail', args=[uuid])
