import pytest

from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, ten_news_homepage, home_url):
    """Проверяет, что на главной странице отображается 10 новостей."""
    response = client.get(home_url)
    news_list = response.context['news_list']
    news_count = news_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_ordering(client, ten_news_homepage, home_url):
    """Сортировка на главной странице, от новых к старым записям."""
    response = client.get(home_url)
    news_list = response.context['news_list']
    all_dates = [news.date for news in news_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comment_ordering(client, news, ten_comments, news_detail_url):
    """
    Сортировка комментариев на странице отдельной новости.

    От старых к новым комментариям.
    """
    response = client.get(news_detail_url)
    assert 'news' in response.context
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_detail_url):
    """
    Проверяет, что на странице новости у неавторизованного
    пользователя нет формы для создания комментария.
    """
    response = client.get(news_detail_url)
    assert 'form' not in response.context


def authorized_client_has_form(author_client, news_detail_url):
    """
    Проверяет, что на странице новости у авторизованного
    пользователя есть форма для создания комментария.
    """
    response = author_client.get(news_detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
