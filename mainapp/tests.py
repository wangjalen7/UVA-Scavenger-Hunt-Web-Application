import json
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import EventForm
from unittest.mock import Mock, patch
from django.test import TestCase
from .models import Event, Player, Theme, Team, Task


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


class TaskCreationTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            'admin_task_creator', 'admin@example.com', 'adminpassword')
        self.theme = Theme.objects.create(
            title='Adventure Theme', description='Exciting adventure tasks')

    def test_create_task(self):
        self.client.login(username='admin_task_creator',
                          password='adminpassword')
        data = {
            'name': 'Find a Historic Landmark',
            'task': 'Locate and take a photo with a well-known historic landmark in your city.',
            'hint': 'Some hint',  # Add a hint here
            'theme': self.theme.id
        }

        response = self.client.post(
            reverse('create_task', args=[self.theme.id]), data)
        if response.status_code != 302:
            print("Form errors:", response.context['form'].errors)

        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(name='Find a Historic Landmark')
        self.assertEqual(task.theme, self.theme)
        self.assertEqual(task.task, 'Locate and take a photo with a well-known historic landmark in your city.')


class ThemeCreationTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            'admin_theme_creator', 'admin@example.com', 'adminpassword')

        self.tasks = [
            {
                'name': 'Find a Historic Landmark',
                'task': 'Locate and take a photo with a well-known historic landmark in your city.',
                'hint': 'Look for famous structures or monuments.',
                'latitude': 40.748817,
                'longitude': -73.985428
            },
            {
                'name': 'Nature Trail Exploration',
                'task': 'Explore a nature trail and mark three different types of trees.',
                'hint': 'Pay attention to the shape of leaves and bark patterns.',
                'latitude': 37.769420,
                'longitude': -122.486213
            }
        ]

    def test_create_theme_with_tasks(self):
        self.client.login(username='admin_theme_creator',
                          password='adminpassword')
        theme_data = {
            'title': 'Adventure Theme',
            'description': 'Exciting adventure tasks',
            'tasks_json': json.dumps(self.tasks)
        }

        response = self.client.post(reverse('create_theme'), theme_data)

        if response.status_code != 302:
            print("Theme Form Errors:", response.context['form'].errors)

        self.assertEqual(response.status_code, 302)
        theme = Theme.objects.get(title='Adventure Theme')
        for task in self.tasks:
            self.assertTrue(theme.tasks.filter(name=task['name']).exists())


class EventFormTests(TestCase):

    @patch('mainapp.models.Event')
    def test_event_form_valid_data(self, MockEvent):
        theme = Theme.objects.create(
            title='Test Theme', description='Test Theme Description')
        form = EventForm(data={
            'name': 'Test Event',
            'start_date': '2023-01-01',
            'end_date': '2023-01-10',
            'privacy': 'U',
            'description': 'Test Description',
            'theme': theme.id,
        })
        self.assertTrue(form.is_valid())

    def test_event_form_no_data(self):
        form = EventForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 6)

    def setUp(self):
        self.user = User.objects.create_user(
            'testuserjalen', 'testuser@example.com', 'testpassword123')

    def test_create_event(self):
        self.client.login(username='testuserjalen', password='testpassword123')
        theme = Theme.objects.create(
            title='Test Theme', description='Test Theme Description')
        data = {
            'name': 'Test Event',
            'start_date': '2023-11-01',
            'end_date': '2023-11-10',
            'privacy': 'U',
            'description': 'A test scavenger hunt event.',
            'theme': theme.id
        }
        response = self.client.post(reverse('create_event'), data)
        self.assertEqual(response.status_code, 302)
        event = Event.objects.get(name='Test Event')
        self.assertEqual(event.creator, self.user)
        self.assertEqual(event.status, 'pending')
        self.assertEqual(event.theme, theme)


class EventParticipationTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'participant', 'participant@example.com', 'participant123')
        self.event = Event.objects.create(
            name='Participation Event',
            start_date='2023-12-01',
            end_date='2023-12-10',
            creator=self.user,
            status='approved',
            privacy='U',
            description='Event for participation test'
        )
        self.team = Team.objects.create(name='Test Team', event=self.event)

    def test_join_event(self):
        self.client.login(username='participant', password='participant123')

        # User joins a team
        response = self.client.post(
            reverse('join_team', args=[self.event.id, self.team.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.team.members.filter(id=self.user.id).exists())

        # Create a second team and try to join it
        another_team = Team.objects.create(
            name='Another Team', event=self.event)
        response = self.client.post(
            reverse('join_team', args=[self.event.id, another_team.id]))
        # Assuming it redirects to an error page or similar
        self.assertNotEqual(response.status_code, 302)
        self.assertFalse(another_team.members.filter(id=self.user.id).exists())


class EventParticipationTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'participant', 'participant@example.com', 'participant123')
        self.event = Event.objects.create(
            name='Participation Event',
            start_date='2023-12-01',
            end_date='2023-12-10',
            creator=self.user,
            status='approved',
            privacy='U',
            description='Event for participation test'
        )

    def test_view_event(self):
        self.client.login(username='participant', password='participant123')

        # User views event details
        response = self.client.get(
            reverse('event_details', args=[self.event.id]))
        self.assertEqual(response.status_code, 200)


class ManageEventsTestCase(TestCase):

    def setUp(self):
        self.adminuser = User.objects.create_user(
            'adminuser', 'adminuser@example.com', 'adminpassword123', is_staff=True)
        self.event = Event.objects.create(
            name='Test Event to Approve',
            start_date='2023-11-01',
            end_date='2023-11-10',
            creator=self.adminuser,
            status='pending',
            privacy='U',
            description='A test event'
        )

    def test_approve_event(self):
        self.client.login(username='adminuser', password='adminpassword123')
        response = self.client.post(
            reverse('approve_event', args=[self.event.id]))
        self.assertEqual(response.status_code, 302)
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, 'approved')

    def test_reject_event(self):
        self.client.login(username='adminuser', password='adminpassword123')
        response = self.client.post(
            reverse('deny_event', args=[self.event.id]))
        self.assertEqual(response.status_code, 302)
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, 'denied')
