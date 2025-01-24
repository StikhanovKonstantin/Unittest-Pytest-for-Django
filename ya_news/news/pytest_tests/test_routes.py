from http import HTTPStatus

import pytest

from django.urls import reverse

from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        (pytest.lazy_fixture('home_url'), 1),
        (pytest.lazy_fixture('news_detail_url'), 1),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability_for_anon_users(client, name, args):
    """Проверяет доступ к страницам для неавторизованных пользователей."""
    if args is None:
        url = reverse(name, args=args)
    else:
        url = name
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('comment_edit_url')),
        (pytest.lazy_fixture('comment_delete_url')),
    ),
)
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
def test_availability_for_comment_edit_and_delete(
    url, parametrized_client, expected_status, comment
):
    """Проверяет доступ к изменению/удалению комментариев."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('comment_edit_url')),
        (pytest.lazy_fixture('comment_delete_url')),
    )
)
def test_redirect_for_anonymous_client(client, url):
    """Проверяет редирект неавторизованного пользователя."""
    login_url = reverse('users:login')
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
