import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.models import Comment


# 1. Главная страница доступна анонимному пользователю
@pytest.mark.django_db
def test_home_page_accessible_anonymous(client):
    """Главная страница доступна анонимному пользователю."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# 2. Страница отдельной новости доступна анонимному пользователю
@pytest.mark.django_db
def test_news_detail_page_accessible_anonymous(client, news):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# 3. Страницы удаления и редактирования комментария доступны автору комментария
@pytest.mark.django_db
def test_author_can_access_edit_and_delete_pages(author_client, comment):
    """Автор комментария может зайти на страницы редактирования и удаления."""
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))

    response_edit = author_client.get(edit_url)
    response_delete = author_client.get(delete_url)

    assert response_edit.status_code == HTTPStatus.OK
    assert response_delete.status_code == HTTPStatus.OK


# 4. Анонимный пользователь перенаправляется на страницу авторизации
@pytest.mark.parametrize(
    'url_name',
    ['news:edit', 'news:delete']
)
@pytest.mark.django_db
def test_anonymous_redirects_to_login(client, comment, url_name):
    """
    Анонимный пользователь перенаправляется на страницу авторизации
    при попытке редактировать или удалить комментарий.
    """
    url = reverse(url_name, args=(comment.id,))
    login_url = reverse('users:login')
    response = client.get(url)
    assertRedirects(response, f'{login_url}?next={url}')


# 5. Авторизованный пользователь не может зайти на страницы чужих комментариев (404)
@pytest.mark.parametrize(
    'url_name',
    ['news:edit', 'news:delete']
)
@pytest.mark.django_db
def test_user_cant_edit_or_delete_another_users_comment(admin_client, comment, url_name):
    """
    Авторизованный пользователь не может зайти на страницы редактирования или
    удаления чужих комментариев (404).
    """
    url = reverse(url_name, args=(comment.id,))
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


# 6. Страницы регистрации, входа и выхода доступны анонимным пользователям
@pytest.mark.parametrize(
    'url_name',
    ['users:signup', 'users:login', 'users:logout']
)
@pytest.mark.django_db
def test_auth_pages_accessible_anonymous(client, url_name):
    """Страницы регистрации, входа и выхода доступны анонимным пользователям."""
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
