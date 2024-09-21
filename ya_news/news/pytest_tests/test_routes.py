import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError
from news.models import Comment
from news.forms import BAD_WORDS, WARNING

NEW_COMMENT_TEXT = {'text': 'Новый текст'}

@pytest.mark.parametrize(
    'url_name, client_type, expected_status',
    [
        ('news:home', 'client', HTTPStatus.OK),
        ('news:detail', 'client', HTTPStatus.OK),
        ('users:signup', 'client', HTTPStatus.OK),
        ('users:login', 'client', HTTPStatus.OK),
        ('users:logout', 'client', HTTPStatus.OK),
        ('news:edit', 'client', HTTPStatus.FOUND),
        ('news:delete', 'client', HTTPStatus.FOUND),
    ]
)
@pytest.mark.django_db
def test_page_statuses(url_name, client_type, expected_status, client, author_client, news, comment):
    """
    Проверка статусов страниц для анонимного и авторизованного пользователя.
    """
    clients = {'client': client, 'author_client': author_client}
    url_map = {
        'news:home': reverse('news:home'),
        'news:detail': reverse('news:detail', args=(news.id,)),
        'news:edit': reverse('news:edit', args=(comment.id,)),
        'news:delete': reverse('news:delete', args=(comment.id,)),
        'users:signup': reverse('users:signup'),
        'users:login': reverse('users:login'),
        'users:logout': reverse('users:logout')
    }
    
    response = clients[client_type].get(url_map[url_name])
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_name, expected_redirect_url',
    [
        ('news:edit', 'users:login'),
        ('news:delete', 'users:login'),
    ]
)
@pytest.mark.django_db
def test_anonymous_redirect(url_name, expected_redirect_url, client, news, comment):
    """
    Анонимный пользователь перенаправляется на страницу логина при попытке
    редактирования или удаления комментария.
    """
    url_map = {
        'news:edit': reverse('news:edit', args=(comment.id,)),
        'news:delete': reverse('news:delete', args=(comment.id,)),
    }
    login_url = reverse('users:login')
    response = client.get(url_map[url_name])
    assertRedirects(response, f'{login_url}?next={url_map[url_name]}')
