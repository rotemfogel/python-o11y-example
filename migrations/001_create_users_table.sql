CREATE TABLE IF NOT EXISTS users (
    id          SERIAL      PRIMARY KEY,
    user_name   VARCHAR(36) NOT NULL UNIQUE,
    created_at  TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP   NOT NULL DEFAULT NOW(),
    password    TEXT        NOT NULL
);
