from django.contrib.auth.models import User
from django.urls import reverse
from .forms import EventForm
from unittest.mock import Mock, patch
from django.test import TestCase
from .models import Event, Player


class UserSignupTestCase(TestCase):

    def test_signup_form(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        response = self.client.post(reverse('account_signup'), data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='testuser')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')


class EventFormTests(TestCase):

    @patch('mainapp.models.Event')
    def test_event_form_valid_data(self, MockEvent):
        form = EventForm(data={
            'name': 'Test Event',
            'start_date': '2023-01-01',
            'end_date': '2023-01-10',
            'privacy': 'U',
            'description': 'Test Description',
        })
        self.assertTrue(form.is_valid())

    def test_event_form_no_data(self):
        form = EventForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 5)

    def setUp(self):
        self.user = User.objects.create_user('testuserjalen', 'testuser@example.com', 'testpassword123')

    def test_create_event(self):
        self.client.login(username='testuserjalen', password='testpassword123')
        data = {
            'name': 'Test Event',
            'start_date': '2023-11-01',
            'end_date': '2023-11-10',
            'privacy': 'U',
            'description': 'A test scavenger hunt event.'
        }
        response = self.client.post(reverse('create_event'), data)
        self.assertEqual(response.status_code, 302)
        event = Event.objects.get(name='Test Event')
        self.assertEqual(event.creator, self.user)
        self.assertEqual(event.status, 'pending')


class JoinEventTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuserjalen', 'testuser@example.com', 'testpassword123')
        self.event = Event.objects.create(
            name='Test Event',
            start_date='2023-11-01',
            end_date='2023-11-10',
            creator=self.user,
            status='approved',
            privacy='U',
            description='A test event'
        )

    def test_join_event(self):
        self.client.login(username='testuserjalen', password='testpassword123')
        data = {
            'team': 'Team A',
        }
        response = self.client.post(reverse('join_event', args=[self.event.id]), data)
        self.assertEqual(response.status_code, 302)
        player = Player.objects.get(user=self.user)
        self.assertEqual(player.event, self.event)
        self.assertEqual(player.team, 'Team A')


class ManageEventsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('adminuser', 'adminuser@example.com', 'adminpassword123')
        self.user.is_staff = True
        self.user.save()
        self.event = Event.objects.create(
            name='Test Event to Approve',
            start_date='2023-11-01',
            end_date='2023-11-10',
            creator=self.user,
            status='pending',
            privacy='U',
            description='A test event'
        )

    def test_approve_event(self):
        self.client.login(username='adminuser', password='adminpassword123')
        response = self.client.post(reverse('approve_event', args=[self.event.id]))
        self.assertEqual(response.status_code, 302)
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, 'approved')

    def test_reject_event(self):
        self.client.login(username='adminuser', password='adminpassword123')
        response = self.client.post(reverse('deny_event', args=[self.event.id]))
        self.assertEqual(response.status_code, 302)
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, 'denied')