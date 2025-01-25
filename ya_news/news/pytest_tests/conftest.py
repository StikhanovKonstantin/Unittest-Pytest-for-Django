from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from news.models import News, Comment
from .constants import OBJECTS_FOR_TESTS


@pytest.fixture
def author(django_user_model):
    """Создает объект автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Создает объект читателя. Не автор комментариев."""
    return django_user_model.objects.create(username='Простой читатель')


@pytest.fixture
def author_client(author):
    """Создает клиент для автора комментариев."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Создает клиент для читателя комментариев."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Создает объект новости."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def comment(author, news):
    """Создает объект комментария."""
    return (
        Comment.objects.create(
            news=news,
            author=author,
            text='Текст комментария'
        )
    )


@pytest.fixture
def ten_news_homepage():
    """Создает 10 объектов новостей."""
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f"Новость {index}",
            text="Просто текст.",
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def ten_comments(news, author):
    """Создает 10 объектов комментариев."""
    now = timezone.now()
    for index in range(OBJECTS_FOR_TESTS):
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
            created=now + timedelta(days=index)
        )


@pytest.fixture
def start_comments_count():
    """Возвращает начальное кол-во комментариев в базе данных."""
    return Comment.objects.count()


@pytest.fixture
def home_url():
    """Подготавливает URL для главной страницы."""
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    """Подготавливает URL для страницы отдельной новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comment_edit_url(comment):
    """Подготавливает URL для страницы редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def comment_delete_url(comment):
    """Подготавливает URL для страницы удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def url_to_comments(news_detail_url):
    """Подготавливает URL-редирект с блоком комментариев."""
    return news_detail_url + '#comments'


@pytest.fixture
def comment_data():
    """Подготавливает данные для создания комментария."""
    return {
        'text': 'Текст комментария'
    }


@pytest.fixture
def comment_edit_data():
    """Подготавливает данные для редактирования комментария."""
    return {
        'text': 'Новый текст комментария'
    }
