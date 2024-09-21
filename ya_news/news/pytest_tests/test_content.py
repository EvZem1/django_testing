from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment
from news.forms import CommentForm

pytestmark = pytest.mark.django_db
User = get_user_model()


def test_news_count(client, news):
    """Количество новостей на главной странице не больше заданного в настройках."""
    response = client.get(reverse('news:home'))
    news_count = News.objects.count()
    assert news_count <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news):
    """Сортировка новостей от нового к старому."""
    today = timezone.now()
    response = client.get(reverse('news:home'))
    news_list = response.context['object_list']
    all_dates = [n.date for n in news_list]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(author_client, news, comment):
    """Сортировка комментариев в хронологическом порядке."""
    response = author_client.get(reverse('news:detail', args=(news.id,)))
    news = response.context['news']
    all_comments = list(news.comment_set.all().order_by('created'))
    assert all(all_comments[i].created <= all_comments[i+1].created for i in range(len(all_comments) - 1))


def test_anonymous_client_has_no_form(client, news):
    """Анонимному пользователю недоступна форма для отправки комментария."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news):
    """Авторизованному пользователю доступна форма для отправки комментария."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
