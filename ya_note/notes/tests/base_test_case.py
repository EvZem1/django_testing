from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()

class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Автор")
        cls.another_user = User.objects.create(username="Другой пользователь")
        cls.note = Note.objects.create(
            title="Заголовок",
            text="Текст",
            author=cls.author,
        )
        cls.add_url = reverse("notes:add")
        cls.list_url = reverse("notes:list")
        cls.edit_url = reverse("notes:edit", args=(cls.note.slug,))
        cls.author_client = cls.client_class()
        cls.another_user_client = cls.client_class()
        cls.author_client.force_login(cls.author)
        cls.another_user_client.force_login(cls.another_user)
