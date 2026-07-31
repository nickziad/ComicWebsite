CREATE TABLE IF NOT EXISTS user_profile (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT(255),
    bio TEXT(255) DEFAULT '',
    profile_picture TEXT DEFAULT ''
);