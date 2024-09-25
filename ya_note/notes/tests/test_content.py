from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from .base_test_case import BaseTestCase

User = get_user_model()


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
        """
        На странице создания заметки передаются формы.
        Проверка, что форма является экземпляром NoteForm.
        """
        response = self.author_client.get(self.add_url)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], NoteForm)

    def test_edit_page_have_form(self):
        """
        На странице редактирования заметки передаются формы.
        Проверка, что форма является экземпляром NoteForm.
        """
        response = self.author_client.get(self.edit_url)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], NoteForm)
