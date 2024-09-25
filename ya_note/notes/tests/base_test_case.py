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
        cls.reader = User.objects.create(username="Пользователь_1")
        cls.note = Note.objects.create(
            title="Заголовок",
            text="Текст",
            author=cls.author,
        )
        cls.url_to_notes = reverse("notes:success")
        cls.add_url = reverse("notes:add")
        cls.list_url = reverse("notes:list")
        cls.edit_url = reverse("notes:edit", args=(cls.note.slug,))
        cls.delete_url = reverse("notes:delete", args=(cls.note.slug,))
        cls.detail_url = reverse("notes:detail", args=(cls.note.slug,))
        cls.home_url = reverse("notes:home")
        cls.login_url = reverse("users:login")
        cls.logout_url = reverse("users:logout")
        cls.signup_url = reverse("users:signup")

        # Создаем клиента для каждого пользователя
        cls.author_client = cls.client_class()
        cls.another_user_client = cls.client_class()
        cls.reader_client = cls.client_class()

        # Логиним пользователей
        cls.author_client.force_login(cls.author)
        cls.another_user_client.force_login(cls.another_user)
        cls.reader_client.force_login(cls.reader)

        # Общие данные формы для всех тестов
        cls.form_data = {
            "title": "Новый заголовок",
            "text": "Новый текст",
            "slug": "new_slug",
        }
