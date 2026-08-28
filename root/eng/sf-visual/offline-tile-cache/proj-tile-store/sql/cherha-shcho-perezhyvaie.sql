-- поставити тайл у чергу, якщо його ще нема або він застарів
INSERT OR IGNORE INTO download_queue(key, set_id)
SELECT ?1, ?2
 WHERE NOT EXISTS (SELECT 1 FROM tiles
                    WHERE key = ?1 AND body IS NOT NULL AND fetched > ?3);

-- взяти наступну порцію (індекс queue_ready покриває і пошук, і порядок)
SELECT key FROM download_queue WHERE state = 0 AND set_id = ?1 ORDER BY key LIMIT 64;

-- позначити зроблене; помилку — з лічильником спроб
UPDATE download_queue SET state = 2 WHERE set_id = ?1 AND key = ?2;
UPDATE download_queue SET state = 3, tries = tries + 1 WHERE set_id = ?1 AND key = ?2;

-- чесний відсоток для смужки прогресу
SELECT SUM(state = 2), COUNT(*) FROM download_queue WHERE set_id = ?1;
