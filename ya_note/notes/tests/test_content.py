from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestListNotes(TestCase):
    """
    Проверяет, что на главной странице
    отображаются только собственные заметки.
    """

    # Ссылка на страницу списка заметок.
    NOTES_LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Предустанавливает все нужные объекты перед началом тестирования."""
        cls.author = User.objects.create(username='author_test')
        cls.reader = User.objects.create(username='reader_test')
        cls.note = Note.objects.create(
            title='test_title',
            text='test_text',
            slug='slug',
            author=cls.author
        )

    def test_only_author_notes_in_list(self):
        """Проверяет, что пользователю видны только его заметки, а не чужие."""
        user_and_amount_notes = (
            (self.author, 1),
            (self.reader, 0),
        )
        for user, notes_amount in user_and_amount_notes:
            self.client.force_login(user)
            response = self.client.get(self.NOTES_LIST_URL)
            object_list = response.context['object_list']
            notes_count = object_list.count()
            with self.subTest(user=user):
                self.assertEqual(notes_count, notes_amount)

    def test_pages_contains_form(self):
        """
        Проверяет, что на страницы создания и редактирования
        заметок в контексте существует форма,
        которая принадлежит к классу формы создания заметок.
        """
        self.client.force_login(self.author)
        name_args = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in name_args:
            url = reverse(name, args=args)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
