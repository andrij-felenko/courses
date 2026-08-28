// ── Підсистема: чотири служби, кожна робить одне й нічого не знає про сусідів ──

interface CartItem { sku: string; qty: number; price: number; }
interface Cart     { items: CartItem[]; total: number; email: string; }
interface Card     { token: string; }

class OutOfStockError extends Error {}
class PaymentDeclinedError extends Error {}

// 1. Склад: резервує товар і вміє резерв ЗНЯТИ (це стане ключем до відкоту)
class InventoryService {
  reserve(items: CartItem[]): ReservationId {
    for (const it of items) {
      if (!this.hasStock(it.sku, it.qty))
        throw new OutOfStockError(`Немає ${it.qty}× ${it.sku}`);
    }
    return this.hold(items);          // повертає розписку про резерв
  }
  release(id: ReservationId): void { /* повертає товар на полицю */ }

  private hasStock(sku: string, qty: number): boolean { /* ... */ return true; }
  private hold(items: CartItem[]): ReservationId { /* ... */ return "res_1" as ReservationId; }
}

// 2. Платіж: списує гроші; може відхилити картку
class PaymentGateway {
  charge(card: Card, amount: number): Charge {
    const ok = this.callProvider(card.token, amount);   // зовнішній API банку
    if (!ok) throw new PaymentDeclinedError("Картку відхилено");
    return { id: `chg_${Date.now()}`, amount };
  }
  refund(chargeId: string): void { /* повертає гроші, теж компенсація */ }

  private callProvider(token: string, amount: number): boolean { /* ... */ return true; }
}

// 3. Сховище замовлень: створює й зберігає запис замовлення
class OrderRepository {
  create(cart: Cart, chargeId: string): Order {
    return { id: `ord_${Date.now()}`, cart, chargeId, status: "paid" };
  }
}

// 4. Пошта: шле листи; НЕ критична — її збій не має валити замовлення
class EmailService {
  sendConfirmation(order: Order): void { /* SMTP, може бути недоступний */ }
}

type ReservationId = string & { readonly brand: unique symbol };
interface Charge { id: string; amount: number; }
interface Order  { id: string; cart: Cart; chargeId: string; status: string; }
