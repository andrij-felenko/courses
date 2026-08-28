-- рядок 42: був status='paid', total=1200.00 → став status='review'
UPDATE orders
   SET status = @status
 WHERE id     = @id
   AND status = @orig_status
   AND total  = @orig_total;
-- @status='review', @id=42, @orig_status='paid', @orig_total=1200.00

-- рядок 45: доданий у наборі
INSERT INTO orders (customer_id, total, status) VALUES (@customer_id, @total, @status);

-- рядок 43: позначений вилученим
DELETE FROM orders
 WHERE id     = @id
   AND status = @orig_status
   AND total  = @orig_total;
