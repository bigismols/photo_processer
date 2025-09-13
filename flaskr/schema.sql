DROP TABLE IF EXISTS image;

CREATE TABLE image (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_data BLOB,
    filename TEXT,
    mimetype TEXT,
    length INTEGER,
    width INTEGER,
    thumbnail_small BLOB,
    thumbnail_medium BLOB,
    caption TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)