-- успіх: рядок просто зникає
DELETE FROM jobs WHERE id = $1 AND locked_by = $2;

-- невдача, спроби ще є: відсунути час і записати причину
UPDATE jobs SET run_at = now() + make_interval(secs => $2), last_error = $3
 WHERE id = $1 AND locked_by = $4;

-- невдача, спроби вичерпано: відкласти вбік
UPDATE jobs SET status = 'dead', last_error = $2, run_at = now()
 WHERE id = $1 AND locked_by = $3;
