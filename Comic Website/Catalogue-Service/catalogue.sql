CREATE TABLE IF NOT EXISTS comic_series ( --Batman Dark Knight
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    front_page TEXT, -- default: path to first issue's first page
    is_active INTEGER NOT NULL, 
    publisher_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    owner_id INTEGER NOT NULL,
    path_to_series TEXT NOT NULL, --/Desktop/comics/series
    issues_count INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(publisher_id) REFERENCES publishers(id),
    FOREIGN KEY(category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS publishers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publisher_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS categories(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL
);

-- 3. Comic Issues

-- | id | series_id | title | 

CREATE TABLE IF NOT EXISTS comic_issues ( --Batman Dark Knight #1
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    issue_number INTEGER NOT NULL DEFAULT 0,
    file_path TEXT NOT NULL, --/Desktop/comics/series/issues
    owner_id INTEGER NOT NULL,
    FOREIGN KEY(owner_id) REFERENCES comic_series(owner_id) ON DELETE CASCADE,
    FOREIGN KEY(series_id) REFERENCES comic_series(id) ON DELETE CASCADE,
    UNIQUE(series_id, issue_number)
);

INSERT INTO publishers(publisher_name) VALUES('DC Comics');
INSERT INTO publishers(publisher_name) VALUES('Marvel');
INSERT INTO publishers(publisher_name) VALUES('Other');

INSERT INTO categories(category_name) VALUES('Action');
INSERT INTO categories(category_name) VALUES('Comedy');
INSERT INTO categories(category_name) VALUES('Drama');
INSERT INTO categories(category_name) VALUES('Horror');
