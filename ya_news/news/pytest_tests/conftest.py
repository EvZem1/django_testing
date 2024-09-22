import pytest
from django.test import Client

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username="Автор")


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title="Заголовок",
        text="Текст",
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(news=news, text="Комментарий", author=author)
