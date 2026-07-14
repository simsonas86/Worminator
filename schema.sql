-- Worminator database schema template.
-- Ensure a database exists with a name matching DB_DATABASE in .env.

BEGIN;

CREATE TABLE IF NOT EXISTS users
(
    user_id       BIGINT PRIMARY KEY,
    username      VARCHAR(50) NOT NULL,
    ticket_count  INTEGER     NOT NULL DEFAULT 0,
    times_coached INTEGER     NOT NULL DEFAULT 0
);

COMMIT;