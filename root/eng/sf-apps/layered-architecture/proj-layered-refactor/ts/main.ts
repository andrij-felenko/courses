// main.ts — ЄДИНЕ місце, де конкретні класи названо на ім'я
import express from "express";
import Database from "better-sqlite3";
import { SqlProductRepo, SqlOrderRepo } from "./infra/sqlRepos";
import { PlaceOrder } from "./application/placeOrder";
import { makeRoutes } from "./web/routes";

export function buildApp() {
  const db = new Database("shop.db");
  const products = new SqlProductRepo(db);   // обіцянку виконує SQL —
  const orders = new SqlOrderRepo(db);       //   але знає про це лише тут
  const place = new PlaceOrder(products, orders);
  const app = express();
  app.use(express.json());
  app.use(makeRoutes(place));
  return app;
}

buildApp().listen(3000);
