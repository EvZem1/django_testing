from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("notes:add")
        cls.done_url = reverse("notes:success")
        cls.login_url = reverse("users:login")
        cls.author = User.objects.create(username="Автор")
        cls.reader = User.objects.create(username="Пользователь")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)


class TestNoteCreation(BaseTestCase):
    NEW_TITLE = "Новый заголовок"
    NEW_NOTE_TEXT = "Новый текст"
    NEW_SLUG = "new_slug"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title="Заголовок",
            text="Текст",
            slug="note-slug",
            author=cls.author,
        )
        cls.form_data = {
            "title": cls.NEW_TITLE,
            "text": cls.NEW_NOTE_TEXT,
            "slug": cls.NEW_SLUG,
        }

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создавать заметку."""
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        self.assertGreater(Note.objects.count(), notes_count_before)
        new_note = Note.objects.get(slug=self.NEW_SLUG)
        self.assertEqual(new_note.title, self.form_data["title"])
        self.assertEqual(new_note.text, self.form_data["text"])
        self.assertEqual(new_note.slug, self.form_data["slug"])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь НЕ может создавать заметки."""
        notes_count_before = Note.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        expected_url = f"{self.login_url}?next={self.url}"
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_not_unique_slug(self):
        """Проверка, что повторяющийся slug вызывает ошибку формы."""
        notes_count_before = Note.objects.count()
        self.form_data["slug"] = self.note.slug
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count_before)
        self.assertFormError(
            response, form="form", field="slug", errors=self.note.slug + WARNING
        )

    def test_empty_slug(self):
        """
        Проверка создания заметки с пустым slug,
        чтобы он был автоматически сгенерирован.
        """
        Note.objects.all().delete()
        notes_count_before = Note.objects.count()
        self.form_data.pop("slug")
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        notes_count = Note.objects.count()
        self.assertGreater(notes_count, notes_count_before)
        new_note = Note.objects.get(title=self.NEW_TITLE)
        expected_slug = slugify(self.form_data["title"])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(BaseTestCase):
    NOTE_TEXT = "Текст заметки"
    NEW_NOTE_TEXT = "Обновлённая заметка"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title="Заголовок",
            text=cls.NOTE_TEXT,
            author=cls.author,
        )
        cls.edit_url = reverse("notes:edit", args=[cls.note.slug])
        cls.delete_url = reverse("notes:delete", args=[cls.note.slug])
        cls.url_to_notes = reverse("notes:success")
        cls.form_data = {
            "title": "Новый заголовок",
            "text": cls.NEW_NOTE_TEXT,
        }

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_notes)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.text, self.form_data["text"])
        self.assertEqual(updated_note.title, self.form_data["title"])
        self.assertEqual(updated_note.author, self.note.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать заметку другого пользователя."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.text, self.note.text)
        self.assertEqual(updated_note.title, self.note.title)
        self.assertEqual(updated_note.slug, self.note.slug)
        self.assertEqual(updated_note.author, self.note.author)

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_to_notes)
        self.assertEqual(Note.objects.count(), notes_count_before - 1)

    def test_user_cant_delete_note_of_another_user(self):
        notes_count_before = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count_before)
