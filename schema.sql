-- ─────────────────────────────────────────────────────────────
-- FitAvatar — Database Schema
-- Run this in Supabase SQL Editor to create all tables.
-- ─────────────────────────────────────────────────────────────

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           TEXT UNIQUE NOT NULL,
    -- Supabase Auth owns passwords; keep a non-sensitive placeholder default
    -- for backward compatibility with older app versions/tests.
    password        TEXT NOT NULL DEFAULT '__managed_by_supabase__',
    supabase_uid    UUID UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    age             INTEGER NOT NULL CHECK (age BETWEEN 10 AND 100),
    weight_kg       FLOAT NOT NULL CHECK (weight_kg BETWEEN 20 AND 300),
    height_cm       FLOAT NOT NULL CHECK (height_cm BETWEEN 100 AND 250),
    gender          TEXT NOT NULL CHECK (gender IN ('male', 'female')),
    goal            TEXT NOT NULL CHECK (goal IN ('Weight Loss', 'Muscle Gain', 'Maintenance')),
    activity_level  TEXT NOT NULL,
    country         TEXT NOT NULL CHECK (country IN (
                        'Brazil', 'China', 'France', 'Greece', 'India', 'Italy',
                        'Japan', 'Lebanon', 'Mexico', 'Pakistan', 'Saudi Arabia',
                        'Spain', 'Thailand', 'Turkey', 'USA'
                    )),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Workout sessions table
CREATE TABLE IF NOT EXISTS workout_sessions (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_name     TEXT NOT NULL CHECK (exercise_name IN ('Squats', 'Push-ups', 'Bicep Curls')),
    total_reps        INTEGER NOT NULL DEFAULT 0,
    correct_reps      INTEGER NOT NULL DEFAULT 0,
    incorrect_reps    INTEGER NOT NULL DEFAULT 0,
    score_percent     FLOAT NOT NULL DEFAULT 0.0 CHECK (score_percent BETWEEN 0 AND 100),
    duration_seconds  INTEGER NOT NULL DEFAULT 0,
    recorded_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Diet logs table
CREATE TABLE IF NOT EXISTS diet_logs (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    calories_target  INTEGER NOT NULL,
    protein_target   INTEGER NOT NULL,
    bmi_value        FLOAT NOT NULL,
    bmi_category     TEXT NOT NULL,
    goal             TEXT NOT NULL,
    location         TEXT NOT NULL,
    meals_json       JSONB NOT NULL,
    generated_at     TIMESTAMPTZ DEFAULT NOW()
);

-- User Progress table (tracks complete physical profile over time)
CREATE TABLE IF NOT EXISTS user_progress (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    age        INTEGER NOT NULL CHECK (age BETWEEN 10 AND 100),
    weight_kg  FLOAT NOT NULL CHECK (weight_kg BETWEEN 20 AND 300),
    height_cm  FLOAT NOT NULL CHECK (height_cm BETWEEN 100 AND 250),
    goal       TEXT NOT NULL CHECK (goal IN ('Weight Loss', 'Muscle Gain', 'Maintenance')),
    location   TEXT NOT NULL CHECK (location IN (
                   'Brazil', 'China', 'France', 'Greece', 'India', 'Italy',
                   'Japan', 'Lebanon', 'Mexico', 'Pakistan', 'Saudi Arabia',
                   'Spain', 'Thailand', 'Turkey', 'USA'
               )),
    logged_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ── Indexes for query performance ─────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_sessions_user_id    ON workout_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_recorded   ON workout_sessions(recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_diet_logs_user_id   ON diet_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_diet_logs_generated ON diet_logs(generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_logged  ON user_progress(logged_at ASC);

-- ── NOTE ──────────────────────────────────────────────────────────────────────
-- Authentication is fully handled by Supabase Auth.
-- Run this entire script in Supabase SQL Editor as a clean setup.
-- supabase_uid links each row to the Supabase Auth user identity.












-- old

-- Users table
-- CREATE TABLE IF NOT EXISTS users (
--     id              SERIAL PRIMARY KEY,
--     email           TEXT UNIQUE NOT NULL,
--     supabase_uid    UUID UNIQUE NOT NULL,
--     name            TEXT NOT NULL,
--     age             INTEGER NOT NULL CHECK (age BETWEEN 10 AND 100),
--     weight_kg       FLOAT NOT NULL CHECK (weight_kg BETWEEN 20 AND 300),
--     height_cm       FLOAT NOT NULL CHECK (height_cm BETWEEN 100 AND 250),
--     gender          TEXT NOT NULL CHECK (gender IN ('male', 'female')),
--     goal            TEXT NOT NULL CHECK (goal IN ('Weight Loss', 'Muscle Gain', 'Maintenance')),
--     activity_level  TEXT NOT NULL,
--     country         TEXT NOT NULL CHECK (country IN (
--                         'Brazil', 'China', 'France', 'Greece', 'India', 'Italy',
--                         'Japan', 'Lebanon', 'Mexico', 'Pakistan', 'Saudi Arabia',
--                         'Spain', 'Thailand', 'Turkey', 'USA'
--                     )),
--     created_at      TIMESTAMPTZ DEFAULT NOW()
-- );

-- -- Workout sessions table
-- CREATE TABLE IF NOT EXISTS workout_sessions (
--     id                SERIAL PRIMARY KEY,
--     user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     exercise_name     TEXT NOT NULL CHECK (exercise_name IN ('Squats', 'Push-ups', 'Bicep Curls')),
--     total_reps        INTEGER NOT NULL DEFAULT 0,
--     correct_reps      INTEGER NOT NULL DEFAULT 0,
--     incorrect_reps    INTEGER NOT NULL DEFAULT 0,
--     score_percent     FLOAT NOT NULL DEFAULT 0.0 CHECK (score_percent BETWEEN 0 AND 100),
--     duration_seconds  INTEGER NOT NULL DEFAULT 0,
--     recorded_at       TIMESTAMPTZ DEFAULT NOW()
-- );

-- -- Diet logs table
-- CREATE TABLE IF NOT EXISTS diet_logs (
--     id               SERIAL PRIMARY KEY,
--     user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     calories_target  INTEGER NOT NULL,
--     protein_target   INTEGER NOT NULL,
--     bmi_value        FLOAT NOT NULL,
--     bmi_category     TEXT NOT NULL,
--     goal             TEXT NOT NULL,
--     location         TEXT NOT NULL,
--     meals_json       JSONB NOT NULL,
--     generated_at     TIMESTAMPTZ DEFAULT NOW()
-- );

-- -- User Progress table (tracks complete physical profile over time)
-- CREATE TABLE IF NOT EXISTS user_progress (
--     id         SERIAL PRIMARY KEY,
--     user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     age        INTEGER NOT NULL CHECK (age BETWEEN 10 AND 100),
--     weight_kg  FLOAT NOT NULL CHECK (weight_kg BETWEEN 20 AND 300),
--     height_cm  FLOAT NOT NULL CHECK (height_cm BETWEEN 100 AND 250),
--     goal       TEXT NOT NULL CHECK (goal IN ('Weight Loss', 'Muscle Gain', 'Maintenance')),
--     location   TEXT NOT NULL CHECK (location IN (
--                    'Brazil', 'China', 'France', 'Greece', 'India', 'Italy',
--                    'Japan', 'Lebanon', 'Mexico', 'Pakistan', 'Saudi Arabia',
--                    'Spain', 'Thailand', 'Turkey', 'USA'
--                )),
--     logged_at  TIMESTAMPTZ DEFAULT NOW()
-- );

-- -- ── Indexes for query performance ─────────────────────────────────────────────
-- CREATE INDEX IF NOT EXISTS idx_sessions_user_id    ON workout_sessions(user_id);
-- CREATE INDEX IF NOT EXISTS idx_sessions_recorded   ON workout_sessions(recorded_at DESC);
-- CREATE INDEX IF NOT EXISTS idx_diet_logs_user_id   ON diet_logs(user_id);
-- CREATE INDEX IF NOT EXISTS idx_diet_logs_generated ON diet_logs(generated_at DESC);
-- CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);
-- CREATE INDEX IF NOT EXISTS idx_user_progress_logged  ON user_progress(logged_at ASC);
