CREATE TABLE IF NOT EXISTS TileSets (
    setID          INTEGER PRIMARY KEY NOT NULL,
    name           TEXT NOT NULL UNIQUE,
    typeStr        TEXT,
    topleftLat     REAL DEFAULT 0.0,
    topleftLon     REAL DEFAULT 0.0,
    bottomRightLat REAL DEFAULT 0.0,
    bottomRightLon REAL DEFAULT 0.0,
    minZoom        INTEGER DEFAULT 3,
    maxZoom        INTEGER DEFAULT 3,
    type           INTEGER DEFAULT -1,
    numTiles       INTEGER DEFAULT 0,
    defaultSet     INTEGER DEFAULT 0,
    date           INTEGER DEFAULT 0)
