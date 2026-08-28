-- Варіант А: Миттєва відмова при зайнятості ресурсу
SELECT seat_id, price 
FROM flight_seats 
WHERE flight_id = 501 AND seat_number = '12A' 
FOR UPDATE NOWAIT;

-- Варіант Б: Пропуск заблокованих записів (ідеально для черг)
SELECT id, payload 
FROM background_tasks 
WHERE status = 'pending' 
ORDER BY priority DESC, id ASC 
LIMIT 1 
FOR UPDATE SKIP LOCKED;
