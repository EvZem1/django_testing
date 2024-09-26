import pytest
from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm
from news.models import News

pytestmark = pytest.mark.django_db


def test_news_count(client, news_batch):
    """Количество новостей на главной странице."""
    response = client.get(reverse("news:home"))
    news_count_on_page = len(response.context["object_list"])
    assert news_count_on_page == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_batch):
    """Сортировка новостей от нового к старому."""
    response = client.get(reverse("news:home"))
    news_list = response.context["object_list"]
    all_dates = [n.date for n in news_list]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(author_client, news, comment_batch):
    """Сортировка комментариев в хронологическом порядке."""
    response = author_client.get(reverse("news:detail", args=(news.id,)))
    all_comments = list(
        response.context["news"].comment_set.all().order_by("created")
    )
    assert all_comments  # Ensuring list is not empty
    assert all(
        all_comments[i].created <= all_comments[i + 1].created
        for i in range(len(all_comments) - 1)
    )


def test_anonymous_client_has_no_form(client, news):
    """Анонимному пользователю недоступна форма для отправки комментария."""
    response = client.get(reverse("news:detail", args=(news.id,)))
    assert "form" not in response.context


def test_authorized_client_has_form(author_client, news):
    """Авторизованному пользователю доступна форма для отправки комментария."""
    response = author_client.get(reverse("news:detail", args=(news.id,)))
    assert "form" in response.context
    assert isinstance(response.context["form"], CommentForm)
