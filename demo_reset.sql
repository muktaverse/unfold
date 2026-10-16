-- Clear the demo user's old data (order matters because of foreign keys)
DELETE FROM referrals WHERE user_id = (SELECT user_id FROM users WHERE email = 'demo@unfold.com');
DELETE FROM journal_entries WHERE entry_id IN
  (SELECT entry_id FROM mood_entries WHERE user_id = (SELECT user_id FROM users WHERE email = 'demo@unfold.com'));
DELETE FROM mood_entries WHERE user_id = (SELECT user_id FROM users WHERE email = 'demo@unfold.com');

-- One calm-ish week of history
INSERT INTO mood_entries (user_id, mood_score, tags, entry_date) SELECT user_id, 4, 'Calm',             CURRENT_DATE - 6 FROM users WHERE email = 'demo@unfold.com';
INSERT INTO mood_entries (user_id, mood_score, tags, entry_date) SELECT user_id, 3, 'Tired',            CURRENT_DATE - 5 FROM users WHERE email = 'demo@unfold.com';
INSERT INTO mood_entries (user_id, mood_score, tags, entry_date) SELECT user_id, 4, 'Productive, Calm', CURRENT_DATE - 4 FROM users WHERE email = 'demo@unfold.com';
INSERT INTO mood_entries (user_id, mood_score, tags, entry_date) SELECT user_id, 3, 'Stressed',         CURRENT_DATE - 3 FROM users WHERE email = 'demo@unfold.com';
INSERT INTO mood_entries (user_id, mood_score, tags, entry_date) SELECT user_id, 4, 'Grateful',         CURRENT_DATE - 2 FROM users WHERE email = 'demo@unfold.com';
INSERT INTO mood_entries (user_id, mood_score, tags, entry_date) SELECT user_id, 3, 'Tired',            CURRENT_DATE - 1 FROM users WHERE email = 'demo@unfold.com';

COMMIT;