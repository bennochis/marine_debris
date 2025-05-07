-- Create the table for debris submissions
CREATE TABLE IF NOT EXISTS debris (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT,
    category TEXT,
    gps TEXT,       -- single field for "lat, lon"
    -- gps_lon REAL,
    country TEXT
);
