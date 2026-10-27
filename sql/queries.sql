-- 1. Выборка: список всех тренировок с сортировкой по дате
SELECT id, title, city, date, capacity
FROM events
ORDER BY date ASC;

-- 2. Выборка: список всех видов спорта
SELECT id, name
FROM sports
ORDER BY name;

-- 3. Фильтрация WHERE: тренировки со свободными местами
SELECT id, title, capacity
FROM events
WHERE capacity > 0
ORDER BY capacity DESC;

-- 4. Фильтрация WHERE: активные заявки
SELECT id, athlete_id, event_id, status
FROM requests
WHERE is_cancelled = 0;

-- 5. Соединение JOIN: карточка тренировки с видом спорта
SELECT events.id, events.title, sports.name AS sport_name, events.city, events.location, events.date, events.capacity
FROM events
JOIN sports ON events.sport_id = sports.id
ORDER BY events.id;

-- 6. Соединение JOIN: заявки со спортсменами и тренировками
SELECT requests.id, athletes.name AS athlete_name, events.title AS event_title, requests.status
FROM requests
JOIN athletes ON requests.athlete_id = athletes.id
JOIN events ON requests.event_id = events.id
WHERE requests.is_cancelled = 0;

-- 7. Поиск по дате (подзапрос NOT IN): свободные события без заявок на дату
SELECT events.id, events.title, events.date
FROM events
WHERE events.date = '2026-10-20'
  AND events.id NOT IN (
      SELECT requests.event_id FROM requests WHERE requests.is_cancelled = 0
  );

-- 8. Агрегация COUNT: количество активных заявок
SELECT COUNT(*) AS active_requests_count
FROM requests
WHERE is_cancelled = 0;

-- 9. Агрегация: средняя вместимость событий
SELECT AVG(capacity) AS avg_capacity, MAX(capacity) AS max_capacity
FROM events;

-- 10. Группировка GROUP BY + LEFT JOIN: число заявок по событиям
SELECT events.title AS event_title, COUNT(requests.id) AS requests_count
FROM events
LEFT JOIN requests ON events.id = requests.event_id AND requests.is_cancelled = 0
GROUP BY events.id, events.title
ORDER BY requests_count DESC;

-- 11. Фильтрация групп HAVING: популярные события с числом заявок >= 1
SELECT events.title AS event_title, COUNT(requests.id) AS requests_count
FROM events
JOIN requests ON events.id = requests.event_id
WHERE requests.is_cancelled = 0
GROUP BY events.id, events.title
HAVING COUNT(requests.id) >= 1;
