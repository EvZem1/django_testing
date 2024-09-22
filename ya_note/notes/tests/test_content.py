
import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from notes.forms import NoteForm
from notes.models import Note

from .base_test_case import BaseTestCase  # Corrected relative import order

User = get_user_model()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username="Автор")


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username="Не автор")


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def note(author):
    note = Note.objects.create(
        title="Заголовок",
        text="Текст заметки",
        slug="note-slug",
        author=author,
    )
    return note


@pytest.fixture
def slug_for_args(note):
    return (note.slug,)


class TestContentPage(BaseTestCase):

    def test_note_in_list_for_author(self):
        """Отдельная заметка передаётся на страницу со списком заметок."""
        response = self.author_client.get(self.list_url)
        notes = response.context["object_list"]
        self.assertIn(self.note, notes)

    def test_note_not_in_list_for_another_user(self):
        """В список одного пользователя не попадают заметки других юзеров."""
        response = self.another_user_client.get(self.list_url)
        notes = response.context["object_list"]
        self.assertNotIn(self.note, notes)

    def test_add_page_have_form(self):
        """На странице создания заметки передаются формы."""
        response = self.author_client.get(self.add_url)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], NoteForm)

    def test_edit_page_have_form(self):
        """На странице редактирования заметки передаются формы."""
        response = self.author_client.get(self.edit_url)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], NoteForm)
