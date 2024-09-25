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

    def test_availability_for_note_autorized_user(self):
        """Доступность страниц для залогиненных пользователей."""
        users_statuses = ((self.reader, HTTPStatus.OK),)
        for user, status in users_statuses:
            self.client.force_login(user)
            urls = (
                self.list_url,
                self.url_to_notes,
                self.add_url,
            )
            for url in urls:
                with self.subTest(user=user, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_for_note_edit_and_delete(self):
        """Доступность страниц авторам."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            urls = (
                self.edit_url,
                self.delete_url,
                self.detail_url,
            )
            for url in urls:
                with self.subTest(user=user, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Редирект для анонимов."""
        urls = (
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f"{self.login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

        additional_urls = (
            self.list_url,
            self.url_to_notes,
            self.add_url,
        )
        for url in additional_urls:
            with self.subTest(url=url):
                redirect_url = f"{self.login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
