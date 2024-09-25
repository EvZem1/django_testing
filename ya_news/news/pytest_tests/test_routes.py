from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("url_name", ["news:home"])
def test_home_page_accessible_anonymous(client, url_name):
    """Главная страница доступна анонимному пользователю."""
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("url_name", ["news:edit", "news:delete"])
def test_author_can_access_edit_and_delete_pages(
    author_client,
    comment,
    url_name
):
    """Автор комментария может зайти на страницы редактирования и удаления."""
    url = reverse(url_name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("url_name", ["news:edit", "news:delete"])
def test_anonymous_redirects_to_login(client, comment, url_name):
    """Анонимный пользователь перенаправляется на страницу авторизации."""
    url = reverse(url_name, args=(comment.id,))
    login_url = reverse('users:login')
    response = client.get(url)
    assertRedirects(response, f'{login_url}?next={url}')


@pytest.mark.django_db
def test_news_detail_page_accessible_anonymous(client, news):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("url_name", ["news:edit", "news:delete"])
def test_user_cant_edit_or_delete_another_users_comment(
    admin_client, comment, url_name
):
    """
    Авторизованный пользователь не может зайти
    на страницы редактирования или удаления чужих комментариев (404).
    """
    url = reverse(url_name, args=(comment.id,))
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    "url_name",
    [
        "users:signup",
        "users:login",
        "users:logout"
    ]
)
def test_auth_pages_accessible_anonymous(client, url_name):
    """
    Страницы регистрации, входа и выхода
    доступны анонимным пользователям.
    """
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
