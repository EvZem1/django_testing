import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError
from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_home_page_accessible_anonymous(client):
    """Главная страница доступна анонимному пользователю."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail_page_accessible_anonymous(client, news):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_redirect_for_anonymous_user(client, news, comment):
    """
    Анонимы перенаправляются на страницу авторизации
    при попытке редактирования или удаления комментария.
    """
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    login_url = reverse('users:login')

    response = client.get(edit_url)
    assertRedirects(response, f'{login_url}?next={edit_url}')

    response = client.get(delete_url)
    assertRedirects(response, f'{login_url}?next={delete_url}')


@pytest.mark.django_db
def test_registration_login_logout_pages_accessible_anonymous(client):
    """
    Страницы регистрации, входа и выхода из системы доступны
    анонимным пользователям.
    """
    urls = (
        reverse('users:signup'),
        reverse('users:login'),
        reverse('users:logout')
    )
    for url in urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, news, form_data):
    """Авторизованный пользователь может отправить комментарий."""
    comments_count_before = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() > comments_count_before
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    comments_count_before = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    assert Comment.objects.count() == comments_count_before


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    """Проверка содержания запрещенных слов."""
    comments_count_before = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'бла-бла-бла, {BAD_WORDS[0]}, бла-бла-бла'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == comments_count_before


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, form_data, news, comment):
    """Автор может редактировать свой комментарий."""
    edit_url = reverse('news:edit', args=(comment.id,))
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
                                                admin_client,
                                                form_data,
                                                comment):
    """Пользователь не может редактировать чужой комментарий."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Комментарий'


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, news, comment):
    """Автор может удалять свой комментарий."""
    comments_count_before = Comment.objects.count()
    delete_url = reverse('news:delete', args=(comment.id,))
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() < comments_count_before


@pytest.mark.django_db
def test_other_user_cant_delete_news(admin_client, comment):
    """Пользователь не может удалять чужой комментарий."""
    comments_count_before = Comment.objects.count()
    delete_url = reverse('news:delete', args=(comment.id,))
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count_before
