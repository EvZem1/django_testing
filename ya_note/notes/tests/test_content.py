from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.another_user = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )
        cls.add_url = reverse('notes:add')
        cls.list_url = reverse('notes:list')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.author_client = cls.client_class()
        cls.another_user_client = cls.client_class()
        cls.author_client.force_login(cls.author)
        cls.another_user_client.force_login(cls.another_user)


class TestContentPage(BaseTestCase):

    def test_note_in_list_for_author(self):
        """Отдельная заметка передаётся на страницу со списком заметок."""
        response = self.author_client.get(self.list_url)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

    def test_note_not_in_list_for_another_user(self):
        """В список одного пользователя не попадают заметки других юзеров."""
        response = self.another_user_client.get(self.list_url)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_add_page_have_form(self):
        """На странице создания заметки передаются формы."""
        response = self.author_client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_have_form(self):
        """На странице редактирования заметки передаются формы."""
        response = self.author_client.get(self.edit_url)
        self.assertIn('form', response.context)
