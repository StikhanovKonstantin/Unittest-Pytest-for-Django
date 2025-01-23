from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class TestRoute(TestCase):
    """Проверка доступа к страницам проекта."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Предустанавливает все нужные объекты перед тестами."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Простой читатель')
        cls.note = Note.objects.create(
            title='Название',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        cls.SLUG_ARGUMENT = (cls.note.slug,)

    def test_pages_availability(self):
        """Проверяет доступ к страницам для неавторизованных пользователей."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None)
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """
        Проверяет доступ к редакту/удалению записей.
        Доступно только для автора.
        """
        user_statuses: tuple[tuple] = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=self.SLUG_ARGUMENT)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_for_pages_required_authorisation(self):
        """
        Проверяет доступ для страниц, доступ к которым
        есть только у авторизованного пользователя/автора(страница новости).
        """
        urls: tuple[tuple] = (
            ('notes:list', None),
            ('notes:detail', self.SLUG_ARGUMENT),
            ('notes:add', None),
            ('notes:success', None),
        )
        self.client.force_login(self.author)

        # Проверка доступа для авторизованного пользователя.
        for name, args in urls:
            with self.subTest(user=self.author, name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        self.client.logout()

        # Проверка доступа для неавторизованного пользователя.
        for name, args in urls:
            with self.subTest(user=self.author, name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
