-- SportPartner Finder: схема базы данных SQLite
CREATE TABLE IF NOT EXISTS sports (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS athletes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    level INTEGER NOT NULL,
    city TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    sport_id INTEGER NOT NULL,
    city TEXT NOT NULL,
    location TEXT NOT NULL,
    date TEXT NOT NULL,
    min_level INTEGER NOT NULL DEFAULT 1,
    max_level INTEGER NOT NULL DEFAULT 5,
    capacity INTEGER NOT NULL DEFAULT 2,
    FOREIGN KEY (sport_id) REFERENCES sports (id)
);

CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY,
    athlete_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    is_cancelled INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (athlete_id) REFERENCES athletes (id),
    FOREIGN KEY (event_id) REFERENCES events (id)
);
