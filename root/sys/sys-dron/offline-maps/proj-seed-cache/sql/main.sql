PRAGMA user_version;                              -- має бути 1

SELECT setID, name, typeStr, type, defaultSet, minZoom, maxZoom, numTiles
FROM TileSets;                                    -- рівно один рядок, defaultSet = 0

SELECT (SELECT COUNT(*) FROM Tiles)                            AS tiles,
       (SELECT COUNT(*) FROM SetTiles)                         AS links,
       (SELECT COUNT(*) FROM Tiles t WHERE NOT EXISTS
           (SELECT 1 FROM SetTiles s WHERE s.tileID = t.tileID)) AS orphans,
       (SELECT MIN(length(hash)) FROM Tiles)                   AS hash_min,
       (SELECT MAX(length(hash)) FROM Tiles)                   AS hash_max;
