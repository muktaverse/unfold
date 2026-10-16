-- USERS: one row per registered person
CREATE TABLE users (
    user_id        NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name      VARCHAR2(100) NOT NULL,
    email          VARCHAR2(150) NOT NULL UNIQUE,
    password_hash  VARCHAR2(255) NOT NULL,
    created_at     DATE DEFAULT CURRENT_DATE
);

-- MOOD_ENTRIES: one row per daily check-in
CREATE TABLE mood_entries (
    entry_id    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     NUMBER NOT NULL REFERENCES users(user_id),
    mood_score  NUMBER(1) NOT NULL CHECK (mood_score BETWEEN 1 AND 5),
    tags        VARCHAR2(200),
    entry_date  DATE DEFAULT CURRENT_DATE
);

-- JOURNAL_ENTRIES: optional private note attached to a check-in
CREATE TABLE journal_entries (
    journal_id  NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entry_id    NUMBER NOT NULL REFERENCES mood_entries(entry_id),
    content     CLOB NOT NULL
);

-- TIPS: self-help suggestions, linked to a mood level (1 to 5)
CREATE TABLE tips (
    tip_id       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    mood_level   NUMBER(1) NOT NULL CHECK (mood_level BETWEEN 1 AND 5),
    title        VARCHAR2(100) NOT NULL,
    description  VARCHAR2(400) NOT NULL
);

-- COUNSELORS: people a user can be referred to
CREATE TABLE counselors (
    counselor_id    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name            VARCHAR2(100) NOT NULL,
    specialization  VARCHAR2(100),
    email           VARCHAR2(150)
);

-- REFERRALS: a user's request to talk to a counselor
CREATE TABLE referrals (
    referral_id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id       NUMBER NOT NULL REFERENCES users(user_id),
    counselor_id  NUMBER REFERENCES counselors(counselor_id),
    reason        VARCHAR2(300),
    status        VARCHAR2(20) DEFAULT 'PENDING',
    created_at    DATE DEFAULT CURRENT_DATE
);

-- Starter tips
INSERT INTO tips (mood_level, title, description) VALUES (1, 'Reach out', 'Talk to someone you trust today, or consider speaking to a counselor.');
INSERT INTO tips (mood_level, title, description) VALUES (1, 'Slow breathing', 'Breathe in for 4 seconds, hold for 4, out for 6. Repeat for 2 minutes.');
INSERT INTO tips (mood_level, title, description) VALUES (2, 'Short walk', 'A 10-minute walk outside can lift your mood a little.');
INSERT INTO tips (mood_level, title, description) VALUES (2, 'Write it down', 'Spend 5 minutes writing what is on your mind in your journal.');
INSERT INTO tips (mood_level, title, description) VALUES (3, 'Small goal', 'Pick one small task and finish it today.');
INSERT INTO tips (mood_level, title, description) VALUES (4, 'Keep the streak', 'Do one thing you enjoyed this week again today.');
INSERT INTO tips (mood_level, title, description) VALUES (5, 'Share the good mood', 'Message a friend and tell them something you appreciate.');

-- Starter counselors (sample data for the demo)
INSERT INTO counselors (name, specialization, email) VALUES ('Dr. Asha Rao', 'Student stress', 'asha.rao@example.com');
INSERT INTO counselors (name, specialization, email) VALUES ('Dr. Kiran Mehta', 'Anxiety and mood', 'kiran.mehta@example.com');

COMMIT;