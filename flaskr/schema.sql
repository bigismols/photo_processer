DROP TABLE IF EXISTS image;

CREATE TABLE image (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_data BLOB,
    thumbnail_small BLOB,
    thumbnail_medium BLOB,
    metadata TEXT,
    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processing_status TEXT NOT NULL
)