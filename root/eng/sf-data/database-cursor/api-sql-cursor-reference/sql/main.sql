DO $$
DECLARE
    cur_trans CURSOR FOR SELECT id, amount FROM transactions WHERE status = 'PENDING';
    rec_trans RECORD;
BEGIN
    OPEN cur_trans;
    LOOP
        FETCH NEXT FROM cur_trans INTO rec_trans;
        EXIT WHEN NOT FOUND; -- Перевірка стану %NOTFOUND
        
        -- Логіка обробки окремого рядка
        PERFORM process_single_transaction(rec_trans.id, rec_trans.amount);
    END LOOP;
    CLOSE cur_trans;
END $$;
