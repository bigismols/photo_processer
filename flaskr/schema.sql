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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    status TEXT DEFAULT 'processing'
)