// БУЛО: локальна реалізація за бар'єром warehouse/index.ts
export const makeWarehouse = (s: StockTable): Warehouse =>
  new WarehouseService(s);

// СТАЛО: за тим самим бар'єром — клієнт до винесеного сервісу.
// Жоден імпортер 'warehouse' не змінюється: тип Warehouse той самий.
class WarehouseHttpClient implements Warehouse {
  constructor(private baseUrl: string) {}
  async reserve(id: OrderId, qty: number): Promise<Reservation> {
    const r = await fetch(`${this.baseUrl}/reserve`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ orderId: id, qty }),
    });
    if (!r.ok) throw new WarehouseUnavailable(r.status);   // ← НОВЕ: мережа падає
    return (await r.json()) as Reservation;
  }
}
export const makeWarehouse = (base: string): Warehouse =>
  new WarehouseHttpClient(base);
