from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_user_can_create_comment(author_client, author, news, detail_url):
    """Авторизованный пользователь может отправить комментарий."""
    Comment.objects.all().delete()
    comments_count_before = Comment.objects.count()
    comment_text = "Новый текст"
    response = author_client.post(detail_url, data={"text": comment_text})
    assertRedirects(response, f"{detail_url}#comments")
    assert Comment.objects.count() == comments_count_before + 1
    comment = Comment.objects.get(author=author, news=news)
    assert comment.text == comment_text
    assert comment.author == author
    assert comment.news == news


def test_anonymous_user_cant_create_comment(client, news, detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    Comment.objects.all().delete()
    comments_count_before = Comment.objects.count()
    client.post(detail_url, data={"text": "Новый текст"})
    assert Comment.objects.count() == comments_count_before


def test_user_cant_use_bad_words(author_client, news, detail_url):
    """Проверка содержания запрещенных слов."""
    bad_word_comment = f"Какой-то текст, {BAD_WORDS[0]}, еще текст"
    response = author_client.post(detail_url, data={"text": bad_word_comment})
    assertFormError(response, form="form", field="text", errors=WARNING)


def test_author_can_edit_comment(
    author_client, news, comment, edit_url, detail_url
):
    """Автор может редактировать свой комментарий."""
    new_text = "Обновленный текст"
    response = author_client.post(edit_url, data={"text": new_text})
    assertRedirects(response, f"{detail_url}#comments")
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == new_text
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_user_cant_edit_comment_of_another_user(
    admin_client, comment, edit_url
):
    """Пользователь не может редактировать чужой комментарий."""
    response = admin_client.post(edit_url, data={"text": "Обновленный текст"})
    assert response.status_code == HTTPStatus.NOT_FOUND
    original_comment = Comment.objects.get(id=comment.id)
    assert original_comment.text == comment.text
    assert original_comment.author == comment.author
    assert original_comment.news == comment.news


def test_author_can_delete_comment(
    author_client, comment, delete_url, detail_url
):
    """Автор может удалять свой комментарий."""
    comments_count_before = Comment.objects.count()
    url_to_comments = f"{detail_url}#comments"
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == comments_count_before - 1


def test_other_user_cant_delete_comment(admin_client, comment, delete_url):
    """Пользователь не может удалять чужой комментарий."""
    comments_count_before = Comment.objects.count()
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count_before
