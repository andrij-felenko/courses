   -- Типовий підхід 1990-х років у нічному вікні
   DECLARE
       CURSOR c_orders IS SELECT id, total_amount FROM orders FOR UPDATE;
   BEGIN
       FOR r IN c_orders LOOP
           UPDATE orders 
           SET tax_v2 = r.total_amount * 0.20 
           WHERE CURRENT OF c_orders;
       END LOOP;
       COMMIT;
   END;
