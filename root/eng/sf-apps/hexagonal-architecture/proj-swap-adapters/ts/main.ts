// main.ts ── ОДНА збірка на всі середовища. Вибір адаптера — тут, і тільки тут.
import { randomUUID } from "crypto";
import { ЗамовленняСервіс } from "./order/service";
import { ЗамовленняСховище } from "./order/core";
import { PgСховище } from "./adapters/pg";
import { ПамятьСховище } from "./adapters/memory";
import { ЗамовленняHttp } from "./adapters/http";

// ↓ ЄДИНА розвилка на весь застосунок
function зібратиСховище(): ЗамовленняСховище {
  if (process.env.STORE === "memory") return new ПамятьСховище();
  return new PgСховище(new PgPool(process.env.DATABASE_URL));
}

const сервіс = new ЗамовленняСервіс(зібратиСховище(), randomUUID);
const http = new ЗамовленняHttp(сервіс);
router.post("/orders", (req, res) => http.post(req, res));
// STORE=memory node main.js  → пам'ять
// (без STORE)                → Postgres
