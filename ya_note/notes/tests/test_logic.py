from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestLogicSlug(TestCase):
    """Проверяет логику приложения."""

    # Макс. разрешенная длина поля slug модели Note.
    SLUG_LENGTH: int = 100

    @classmethod
    def setUpTestData(cls):
        """Предустанавливает все нужные объекты перед началом тестирования."""
        cls.author = User.objects.create(username='test_user')
        cls.note = Note.objects.create(
            title='titletest',
            text='text_test',
            author=cls.author
        )

    def test_is_empty_slug_equal_to_title(self):
        """
        Проверяет, что если slug в форме создания или редакта заметки не
        указан, то вместо него будет записан title поста.
        """
        expected_slug = slugify(self.note.title)[:self.SLUG_LENGTH]
        self.assertEqual(self.note.slug, expected_slug)


class TestNoteCreation(TestCase):
    """Проверка логики на создание заметок."""

    NOTE_TEXT: str = 'note_text'
    NOTE_TITLE: str = 'note-title'

    @classmethod
    def setUpTestData(cls):
        """Предустанавливает все нужные объекты перед тестированием."""
        cls.user = User.objects.create(username='Чубзик')
        cls.url = reverse('notes:add')
        cls.redirect_url = reverse('notes:success')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'text': cls.NOTE_TEXT, 'title': cls.NOTE_TITLE}

    def test_anonymous_user_cant_create_note(self):
        """
        Проверяет, что неавторизованный пользователь
        не может создавать заметки.
        """
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_auth_user_can_create_notes(self):
        """
        Проверяет, что авторизованный пользователь
        может создавать заметки.
        """
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что после пост-запроса пользователя
        # переводят на страницу успешного выполнения.
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        # Сверяем отправленные данные для заметки с текущей заметкой.
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.slug, self.NOTE_TITLE)

    def test_slug_is_not_exists(self):
        """
        Проверяет, что при создании заметки, указав в поле slug
        уже существующий slug, заметка не будет создана и вызовется ошибка.
        """
        data_1 = {
            'text': self.NOTE_TEXT,
            'title': self.NOTE_TITLE,
            'slug': 'similar_slug'
        }
        data_2 = {
            'text': self.NOTE_TEXT + '_2',
            'title': self.NOTE_TITLE + '_2',
            'slug': 'similar_slug'
        }
        self.auth_client.post(self.url, data_1)
        # Создаем 2-ю заметку с одинаковым слагом.
        response_2 = self.auth_client.post(self.url, data_2)
        self.assertFormError(
            response_2,
            form='form',
            field='slug',
            errors=data_2['slug'] + WARNING
        )
        # Убедимся, что комментарий не будет создан.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditDelete(TestCase):
    """Проверяет логику выполнения редакта/удаления заметок."""

    NOTE_TEXT: str = 'Начальный текст заметки'
    NOTE_TITLE: str = 'Начальный заголовок заметки'
    NEW_NOTES_TEXT: str = 'Измененный текст'
    NEW_NOTES_TITLE: str = 'Измененный заголовок'

    @classmethod
    def setUpTestData(cls):
        # Создаем автора заметок, он может
        # редактировать и удалять свои заметки.
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        # Создаем авторизованного "читателя", он не может
        # редактировать и удалять заметки.
        cls.reader = User.objects.create(username='Не автор')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Создаем заметку, автором которой будет username=Автор.
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.SLUG_ARG = (cls.note.slug,)
        # Страничка успешного выполнения операций.
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=cls.SLUG_ARG)
        cls.delete_url = reverse('notes:delete', args=cls.SLUG_ARG)
        cls.form_data = {
            'text': cls.NEW_NOTES_TEXT,
            'title': cls.NEW_NOTES_TITLE
        }

    def test_author_can_delete_notes(self):
        """Проверяет, что автор может удалять свои заметки."""
        response = self.author_client.delete(self.delete_url)
        # Проверим, что редирект привел на страницу успешного выполнения.
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        # Проверяем, что после удаления в БД не осталось объектов.
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_notes_of_another_user(self):
        """Проверяет, что простой читатель не может удалять чужие заметки."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что заметки остались на месте.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_notes(self):
        """Проверяет, что автор может редактировать свои заметки."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        # Проверим, что редирект привел на страницу успешного выполнения.
        self.assertRedirects(response, self.success_url)
        # Обновляем старую заметку.
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTES_TEXT)
        self.assertEqual(self.note.title, self.NEW_NOTES_TITLE)

    def test_user_cant_edit_another_user_notes(self):
        """Проверяет, что пользователь не может редактировать чужие заметки."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)


class TestAnonymousRedirects(TestCase):
    """Проверяет редиректы неавторизованного пользователя."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            author=cls.user
        )
        cls.SLUG_ARGUMENT = (cls.note.slug,)

    def test_redirect_for_anonymous(self):
        """
        Проверяет редирект неавторизованного
        пользователя на страницу логина.
        """
        login_url = reverse('users:login')
        name_args: tuple[tuple] = (
            ('notes:add', None),
            ('notes:edit', self.SLUG_ARGUMENT),
            ('notes:delete', self.SLUG_ARGUMENT),
            ('notes:list', None),
            ('notes:detail', self.SLUG_ARGUMENT),
        )
        for name, args in name_args:
            url = reverse(name, args=args)
            redirect_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, redirect_url)
