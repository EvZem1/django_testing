
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, news):
    """Авторизованный пользователь может отправить комментарий."""
    comments_count_before = Comment.objects.count()
    url = reverse("news:detail", args=(news.id,))
    response = author_client.post(url, data={"text": "Новый текст"})
    assertRedirects(response, f"{url}#comments")
    assert Comment.objects.count() == comments_count_before + 1
    comment = Comment.objects.get(author=author, news=news)
    assert comment.text == "Новый текст"


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    """Анонимный пользователь не может отправить комментарий."""
    comments_count_before = Comment.objects.count()
    url = reverse("news:detail", args=(news.id,))
    client.post(url, data={"text": "Новый текст"})
    assert Comment.objects.count() == comments_count_before


def test_user_cant_use_bad_words(author_client, news):
    """Проверка содержания запрещенных слов."""
    url = reverse("news:detail", args=(news.id,))
    response = author_client.post(
        url,
        data={"text": f"Какой-то текст, {BAD_WORDS[0]}, еще текст"}
    )
    assertFormError(response, form="form", field="text", errors=WARNING)


def test_author_can_edit_comment(author_client, news, comment):
    """Автор может редактировать свой комментарий."""
    url = reverse("news:edit", args=(comment.id,))
    response = author_client.post(url, data={"text": "Обновленный текст"})
    assertRedirects(
        response,
        f"{reverse('news:detail', args=(news.id,))}#comments"
    )
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == "Обновленный текст"


def test_user_cant_edit_comment_of_another_user(admin_client, comment):
    """Пользователь не может редактировать чужой комментарий."""
    url = reverse("news:edit", args=(comment.id,))
    response = admin_client.post(url, data={"text": "Обновленный текст"})
    assert response.status_code == HTTPStatus.NOT_FOUND
