# Django Testing

Данный проект посвящен написанию тестов для двух простейших веб-приложений с использованием библиотек Unittest и Pytest. Тесты предназначены для проверки корректности работы приложений Ya News и Ya Note.

## Структура репозитория

Dev
└── django_testing
    ├── ya_news
    │   ├── news
    │   │   ├── fixtures/
    │   │   ├── migrations/
    │   │   ├── pytest_tests/   <- Директория с тестами pytest для проекта ya_news
    │   │   ├── __init__.py
    │   │   ├── admin.py
    │   │   ├── apps.py
    │   │   ├── forms.py
    │   │   ├── models.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   ├── templates/
    │   ├── yanews/
    │   ├── manage.py
    │   └── pytest.ini
    ├── ya_note
    │   ├── notes
    │   │   ├── migrations/
    │   │   ├── tests/          <- Директория с тестами unittest для проекта ya_note
    │   │   ├── __init__.py
    │   │   ├── admin.py
    │   │   ├── apps.py
    │   │   ├── forms.py
    │   │   ├── models.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   ├── templates/
    │   ├── yanote/
    │   ├── manage.py
    │   └── pytest.ini
    ├── .gitignore
    ├── README.md
    ├── requirements.txt
    └── structure_test.py

## Запуск тестов

1. Создание и активация виртуального окружения:

   
```
   python -m venv venv
   # Для Windows:
   venv\Scripts\activate
   # Для Unix/MacOS:
   source venv/bin/activate
```
   

2. Установка зависимостей:

   
```
   pip install -r requirements.txt
```

3. Запуск скрипта для тестов:

Перейдите в корневую директорию проекта и выполните:

   
```
   bash run_tests.sh
```
