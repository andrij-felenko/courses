// domain/ports.ts ── ДВІ обіцянки домену, його поняттями. Ні SQL, ні SMTP.
import { Order } from "./order";

// вихідний порт №1: КУДИ складати замовлення
export interface Orders {
  save(order: Order): Promise<void>;
  byId(id: string): Promise<Order | null>;
}

// вихідний порт №2: ЯК сповістити клієнта
export interface Notifier {
  orderPlaced(order: Order): Promise<void>;   // «підтвердь клієнтові замовлення»
}
