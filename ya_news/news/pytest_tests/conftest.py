import pytest
from django.test import Client
from news.models import Comment, News
from django.conf import settings
from django.urls import reverse


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username="Автор")


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create(username="Администратор")


@pytest.fixture
def admin_client(admin):
    client = Client()
    client.force_login(admin)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title="Заголовок",
        text="Текст",
    )


@pytest.fixture
def news_batch():
    """Создает batch новостей для тестов"""
    return News.objects.bulk_create([
        News(title=f"Заголовок {i}", text=f"Текст {i}")
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ])


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(news=news, text="Комментарий", author=author)


@pytest.fixture
def comment_batch(news, author):
    """Создает batch комментариев для тестов"""
    return Comment.objects.bulk_create([
        Comment(news=news, text=f"Комментарий {i}", author=author)
        for i in range(2)
    ])


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def auth_urls():
    return [
        reverse('users:signup'),
        reverse('users:login'),
        reverse('users:logout')
    ]
