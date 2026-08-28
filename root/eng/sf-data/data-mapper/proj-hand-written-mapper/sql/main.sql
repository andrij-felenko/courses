CREATE TABLE orders (
  id          INTEGER PRIMARY KEY,
  placed_at   TEXT    NOT NULL,
  total_cents INTEGER NOT NULL,
  currency    TEXT    NOT NULL CHECK (length(currency) = 3),
  status      TEXT    NOT NULL CHECK (status IN ('new', 'shipped', 'cancelled'))
);

CREATE TABLE order_lines (
  id          INTEGER PRIMARY KEY,
  order_id    INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  position    INTEGER NOT NULL,
  sku         TEXT    NOT NULL,
  qty         INTEGER NOT NULL CHECK (qty > 0),
  price_cents INTEGER NOT NULL,
  UNIQUE (order_id, position)
);
