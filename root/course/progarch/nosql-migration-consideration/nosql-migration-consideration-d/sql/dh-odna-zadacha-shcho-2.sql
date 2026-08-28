BEGIN;
  SELECT h.id, p.tier, count(d.id)
    FROM homes h
    JOIN plans   p ON p.id = h.plan_id
    JOIN devices d ON d.home_id = h.id
   WHERE h.id = $1
   GROUP BY h.id, p.tier;
  INSERT INTO invoices(home_id, amount, period) VALUES (...);
  UPDATE homes SET billed_through = $2 WHERE id = $1;
COMMIT;
