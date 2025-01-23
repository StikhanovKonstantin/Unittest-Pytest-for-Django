from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, comment_data, news_detail_url
):
    """
    Проверяет то, что неавторизованный пользователь
    не может добавить комментарии.
    """
    client.post(news_detail_url, data=comment_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
    author_client, news_detail_url, comment_data, news, author
):
    """
    Проверяет, что авторизованный пользователь
    может оставлять комментарии.
    """
    response = author_client.post(news_detail_url, data=comment_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    comment_count = Comment.objects.count()
    assert comment_count == 1
    comment = Comment.objects.get()
    assert comment.news == news
    assert comment.author == author
    assert comment.text == comment_data['text']


def test_user_cant_use_bad_words(
    author_client, news_detail_url
):
    """
    Проверяет, что в форму комментария попадают
    только валидные данные.
    """
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(news_detail_url, bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comment_count = Comment.objects.count()
    assert comment_count == 0


def test_author_can_delete_comment(
    author_client, comment_delete_url, url_to_comments
):
    """Проверяет, что автор комментария может его удалить."""
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comments_of_others(
    not_author_client, comment_delete_url, url_to_comments
):
    """Проверяет, что пользователь не может удалить чужой комментарий."""
    response = not_author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    author_client, url_to_comments,
    comment_edit_url, comment_edit_data, comment
):
    """Проверяет, что автор может редактировать свои комментарии."""
    response = author_client.post(comment_edit_url, comment_edit_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == comment_edit_data['text']


def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment_edit_data,
    comment_edit_url, comment, comment_data
):
    """Проверяет, что пользователь не можеть редактировать чужие комменты."""
    response = not_author_client.post(comment_edit_url, comment_edit_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_data['text']
