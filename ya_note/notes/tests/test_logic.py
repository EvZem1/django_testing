import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

from .base_test_case import BaseTestCase  # надеюсь, тут ему и место

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


class TestNoteCreation(BaseTestCase):

    NEW_TITLE = "Новый заголовок"
    NEW_NOTE_TEXT = "Новый текст"
    NEW_SLUG = "new_slug"

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создавать заметку."""
        Note.objects.all().delete()
        form_data = {
            "title": self.NEW_TITLE,
            "text": self.NEW_NOTE_TEXT,
            "slug": self.NEW_SLUG,
        }
        response = self.author_client.post(self.add_url, data=form_data)
        self.assertRedirects(response, self.done_url)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, form_data["title"])
        self.assertEqual(new_note.text, form_data["text"])
        self.assertEqual(new_note.slug, form_data["slug"])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь НЕ может создавать заметки."""
        notes_count_before = Note.objects.count()
        form_data = {
            "title": self.NEW_TITLE,
            "text": self.NEW_NOTE_TEXT,
            "slug": self.NEW_SLUG,
        }
        response = self.client.post(self.add_url, data=form_data)
        expected_url = f"{self.login_url}?next={self.add_url}"
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_not_unique_slug(self):
        """Проверка, что повторяющийся slug вызывает ошибку формы."""
        notes_count_before = Note.objects.count()
        form_data = {
            "title": self.NEW_TITLE,
            "text": self.NEW_NOTE_TEXT,
            "slug": self.note.slug,
        }
        response = self.author_client.post(
            self.add_url, data=form_data
        )
        self.assertEqual(Note.objects.count(), notes_count_before)
        self.assertFormError(
            response,
            form="form",
            field="slug",
            errors=form_data["slug"] + WARNING,
        )

    def test_empty_slug(self):
        """Проверка создания заметки с пустым slug."""
        Note.objects.all().delete()
        form_data = {
            "title": self.NEW_TITLE,
            "text": self.NEW_NOTE_TEXT,
        }
        response = self.author_client.post(self.add_url, data=form_data)
        self.assertRedirects(response, self.done_url)
        new_note = Note.objects.get()
        expected_slug = slugify(form_data["title"])
        self.assertEqual(new_note.slug, expected_slug)
