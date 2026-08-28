// main.prod.ts ── ТОЧКА ЗБІРКИ (прод). ЄДИНЕ місце, де звучить слово "Postgres".
import { randomUUID } from "crypto";
import { ЗамовленняСервіс } from "./order/service";
import { PgСховище } from "./adapters/pg";
import { ЗамовленняHttp } from "./adapters/http";

const db = new PgPool(process.env.DATABASE_URL);

const сервіс = new ЗамовленняСервіс(new PgСховище(db), randomUUID); // ← база сюди
const http = new ЗамовленняHttp(сервіс);                            // ← ядро сюди

router.post("/orders", (req, res) => http.post(req, res));
