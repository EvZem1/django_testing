from http import HTTPStatus
from .base_test_case import BaseTestCase


class TestRoutes(BaseTestCase):

    def test_pages_availability(self):
        """Доступность страниц для анонимов."""
        urls = (
            self.home_url,
            self.login_url,
            self.logout_url,
            self.signup_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_authorized_user(self):
        """Доступность страниц для залогиненных пользователей."""
        urls = (
            self.list_url,
            self.url_to_notes,
            self.add_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """Доступность страниц авторам."""
        users_clients = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for client, status in users_clients:
            urls = (
                self.edit_url,
                self.delete_url,
                self.detail_url,
            )
            for url in urls:
                with self.subTest(client=client, url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Редирект для анонимов."""
        urls = (
            self.detail_url,
            self.edit_url,
            self.delete_url,
            self.list_url,
            self.url_to_notes,
            self.add_url,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f"{self.login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
