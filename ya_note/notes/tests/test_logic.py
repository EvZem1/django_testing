from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .base_test_case import BaseTestCase

User = get_user_model()


class TestNoteCreation(BaseTestCase):

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создавать заметку."""
        Note.objects.all().delete()
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_notes)
        self.assertGreater(Note.objects.count(), notes_count_before)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data["title"])
        self.assertEqual(new_note.text, self.form_data["text"])
        if "slug" in self.form_data:
            self.assertEqual(new_note.slug, self.form_data["slug"])
        else:
            expected_slug = slugify(self.form_data["title"])
            self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь НЕ может создавать заметки."""
        notes_count_before = Note.objects.count()
        response = self.client.post(self.add_url, data=self.form_data)
        expected_url = f"{self.login_url}?next={self.add_url}"
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_not_unique_slug(self):
        """Проверка, что повторяющийся slug вызывает ошибку формы."""
        notes_count_before = Note.objects.count()
        self.form_data["slug"] = self.note.slug
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count_before)
        self.assertFormError(
            response,
            form="form",
            field="slug",
            errors=self.form_data["slug"] + WARNING
        )

    def test_empty_slug(self):
        """
        Проверка создания заметки с пустым slug,
        чтобы он был автоматически сгенерирован.
        """
        Note.objects.all().delete()
        notes_count_before = Note.objects.count()
        self.form_data.pop("slug")
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_notes)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_before + 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data["title"])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(BaseTestCase):

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
