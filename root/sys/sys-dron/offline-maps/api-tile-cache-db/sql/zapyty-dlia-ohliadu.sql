SELECT ts.setID, ts.name, ts.defaultSet, ts.typeStr,
       ts.minZoom || '–' || ts.maxZoom          AS zoom,
       ts.numTiles                              AS planned,
       COUNT(t.tileID)                          AS have,
       COALESCE(SUM(t.size), 0) / 1048576.0     AS MiB
FROM TileSets ts
LEFT JOIN SetTiles st ON st.setID = ts.setID
LEFT JOIN Tiles    t  ON t.tileID = st.tileID
GROUP BY ts.setID
ORDER BY MiB DESC;
