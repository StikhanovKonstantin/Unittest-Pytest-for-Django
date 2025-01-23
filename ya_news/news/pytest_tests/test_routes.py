from http import HTTPStatus

import pytest

from django.urls import reverse

from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('id_for_news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability_for_anon_users(client, name, args):
    """Проверяет доступ к страницам для неавторизованных пользователей."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_comment')),
        ('news:delete', pytest.lazy_fixture('id_for_comment')),
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
    name, parametrized_client, expected_status, comment, args
):
    """Проверяет доступ к изменению/удалению комментариев."""
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_comment')),
        ('news:delete', pytest.lazy_fixture('id_for_comment')),
    )
)
def test_redirect_for_anonymous_client(client, name, args):
    """Проверяет редирект неавторизованного пользователя."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
