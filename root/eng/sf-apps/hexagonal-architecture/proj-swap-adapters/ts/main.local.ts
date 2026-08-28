// main.local.ts ── ТОЧКА ЗБІРКИ (локально). Слова "Postgres" тут НЕМА зовсім.
import { randomUUID } from "crypto";
import { ЗамовленняСервіс } from "./order/service";
import { ПамятьСховище } from "./adapters/memory";      // ← єдина інша строка імпорту
import { ЗамовленняHttp } from "./adapters/http";

const сервіс = new ЗамовленняСервіс(new ПамятьСховище(), randomUUID); // ← пам'ять сюди
const http = new ЗамовленняHttp(сервіс);

router.post("/orders", (req, res) => http.post(req, res));
