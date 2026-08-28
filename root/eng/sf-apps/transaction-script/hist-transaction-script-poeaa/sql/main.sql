-- Oracle PL/SQL, ~1992: збережена процедура — це вже сценарій транзакції,
-- лише названий «procedure», а не «pattern»
CREATE PROCEDURE place_order(p_customer IN NUMBER, p_product IN NUMBER, p_qty IN NUMBER) AS
  v_price  products.price%TYPE;
  v_stock  products.stock%TYPE;
  v_total  NUMBER;
  v_order  NUMBER;
BEGIN
  SELECT price, stock INTO v_price, v_stock          -- прочитати
    FROM products WHERE id = p_product FOR UPDATE;
  IF v_stock < p_qty THEN
    RAISE_APPLICATION_ERROR(-20001, 'недостатньо на складі');
  END IF;

  v_total := v_price * p_qty * (1 - loyalty_discount(p_customer));   -- порахувати

  INSERT INTO orders(customer_id, total, status)                     -- записати
    VALUES (p_customer, v_total, 'new') RETURNING id INTO v_order;
  INSERT INTO order_lines(order_id, product_id, qty, price)
    VALUES (v_order, p_product, p_qty, v_price);
  UPDATE products SET stock = stock - p_qty WHERE id = p_product;

  COMMIT;                                             -- усе або нічого
END;
