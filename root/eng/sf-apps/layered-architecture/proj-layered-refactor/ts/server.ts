// server.ts — усе в одному обробнику: HTTP + правило + SQL
import express from "express";
import Database from "better-sqlite3";

const app = express();
app.use(express.json());
const db = new Database("shop.db");

app.post("/orders", (req, res) => {
  const body = req.body as {
    items: { sku: string; qty: number }[];
    promo?: string;
  };

  let total = 0;
  for (const line of body.items) {
    const row = db.prepare(
      "SELECT price, stock FROM products WHERE sku = ?").get(line.sku) as
      { price: number; stock: number } | undefined;
    if (!row) return res.status(404).json({ error: `немає товару ${line.sku}` });
    if (row.stock < line.qty)
      return res.status(409).json({ error: `замало ${line.sku}` });
    total += row.price * line.qty;
  }

  // знижка за промокодом — правило бізнесу, вписане просто тут
  if (body.promo === "SPRING") total *= 0.9;
  else if (body.promo === "VIP") total *= 0.8;

  const info = db.prepare("INSERT INTO orders(total) VALUES (?)").run(total);
  const orderId = info.lastInsertRowid;
  for (const line of body.items)
    db.prepare("UPDATE products SET stock = stock - ? WHERE sku = ?")
      .run(line.qty, line.sku);

  res.status(201).json({ orderId, total });
});
