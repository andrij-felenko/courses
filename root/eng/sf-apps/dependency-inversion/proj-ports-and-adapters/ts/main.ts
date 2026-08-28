// main.ts ── КОРІНЬ ЗБІРКИ. ЄДИНЕ місце, де сходяться "Postgres" і "SMTP".
import { randomUUID } from "crypto";
import { PlaceOrder } from "./domain/place-order";
import { PgOrders } from "./infra/pg-orders";
import { SmtpNotifier } from "./infra/smtp-notifier";

const db = new Pg(process.env.DATABASE_URL);
const smtp = new Smtp(process.env.SMTP_URL);

// обидва адаптери сходяться ТУТ і подаються сценарію ззовні
const placeOrder = new PlaceOrder(
  new PgOrders(db),                        // порт Orders   ← Postgres
  new SmtpNotifier(smtp, "shop@acme.io"),  // порт Notifier ← SMTP
  randomUUID,
);
// далі placeOrder.run(...) не знає ні слова "Postgres", ні слова "SMTP"
