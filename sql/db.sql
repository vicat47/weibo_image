CREATE TABLE IF NOT EXISTS images
(
    url TEXT PRIMARY KEY,
    catch_id INTEGER NOT NULL,
    downloaded INT default 0,
    dl_time TEXT default NULL
);

CREATE TABLE IF NOT EXISTS catch_list
(
    com_id TEXT PRIMARY KEY,
    root_id TEXT NOT NULL,
    is_child INTEGER default 0,
    user TEXT NOT NULL,
    create_time TEXT NOT NULL,
    catch_time TEXT NOT NULL
);