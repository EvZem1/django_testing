from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "url_fixture, client_fixture, expected_status",
    [
        ("home_url", "client", HTTPStatus.OK),
        ("detail_url", "client", HTTPStatus.OK),
        ("edit_url", "author_client", HTTPStatus.OK),
        ("delete_url", "author_client", HTTPStatus.OK),
        ("edit_url", "admin_client", HTTPStatus.NOT_FOUND),
        ("delete_url", "admin_client", HTTPStatus.NOT_FOUND),
        ("signup_url", "client", HTTPStatus.OK),
        ("login_url", "client", HTTPStatus.OK),
        ("logout_url", "client", HTTPStatus.OK),
    ]
)
def test_accessible_pages(
    request, url_fixture, client_fixture, expected_status
):
    """Тестирование доступности страниц для различных клиентов."""
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "url_fixture, client_fixture",
    [
        ("edit_url", "client"),
        ("delete_url", "client"),
    ]
)
def test_anonymous_redirects_to_login(
    request, url_fixture, client_fixture, login_url
):
    """Анонимный пользователь перенаправляется на страницу авторизации."""
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assertRedirects(response, f"{login_url}?next={url}")
