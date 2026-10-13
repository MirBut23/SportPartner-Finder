from django.http import HttpResponse


def page(title, content):
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
    )
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="{bootstrap}">
</head>
<body>
    <nav class="nav bg-light p-3 mb-4">
        <a class="nav-link" href="/">Главная</a>
        <a class="nav-link" href="/events/">Тренировки</a>
        <a class="nav-link" href="/requests/">Заявки</a>
    </nav>
    <main class="container">{content}</main>
</body>
</html>'''


def index(request):
    content = '''
    <h1 class="display-4">SportPartner Finder</h1>
    <p class="lead">Система поиска спортивных партнеров и тренировок.</p>
    <p>Основные разделы платформы:</p>
    <a href="/events/" class="btn btn-primary me-2">Тренировки</a>
    <a href="/requests/" class="btn btn-secondary">Заявки на матчи</a>
    '''
    return HttpResponse(page("SportPartner Finder — Главная", content))


def page_not_found(request, exception):
    content = '''
    <h1 class="text-danger">404 — Страница не найдена</h1>
    <p>Запрошенный ресурс не найден. Проверьте адрес или вернитесь на главную.</p>
    <a href="/" class="btn btn-primary">На главную</a>
    '''
    return HttpResponse(page("404 — Не найдено", content), status=404)
