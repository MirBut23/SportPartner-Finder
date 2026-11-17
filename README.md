# SportPartner Finder

Веб-приложение на Django для поиска партнёров по совместным тренировкам, управления спортивными событиями и подачи заявок на участие.

## Технологии
- Python 3.14
- Django 5.2
- SQLite (слой данных реализован через Django ORM)
- Bootstrap 5, Django Debug Toolbar, Pillow

## Модели данных
- `Sport` (`events/models.py`) — справочник видов спорта.
- `Event` (`events/models.py`) — тренировки и спортивные события (связь `ForeignKey` со `Sport`, дата, локация, допустимый диапазон уровней, вместимость, фото локации `ImageField`).
- `Athlete` (`requests/models.py`) — спортсмены с уровнем подготовки и городом.
- `Request` (`requests/models.py`) — заявки на участие (связи `ForeignKey` с `Athlete` и `Event` с `on_delete=models.PROTECT`, кастомный менеджер `Request.objects.active()`, метод отмены `cancel()`).

## Запуск проекта
1. Клонируйте репозиторий и перейдите в каталог проекта:
   git clone <адрес репозитория> && cd SportPartner-Finder
2. Создайте и активируйте виртуальное окружение:
   python3 -m venv venv && source venv/bin/activate
3. Установите зависимости:
   pip install -r requirements.txt
4. Примените миграции:
   python manage.py migrate
5. (Опционально) Перенесите исходные данные из БД ПР7:
   python db/import_sqlite_to_orm.py
6. Запустите сервер разработки:
   python manage.py runserver

## Проверка качества и тесты
- Проверка конфигурации: `python manage.py check`
- Запуск автотестов: `python manage.py test -v 2`
