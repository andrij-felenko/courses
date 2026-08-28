// warehouse/warehouse.ts — реалізація ховається у теці
class WarehouseService {
  constructor(private stock: StockTable) {}  // приватна нутрощі
  reserve(id: OrderId, qty: number): Reservation {
    return this.stock.hold(id, qty);
  }
}

// warehouse/index.ts — ЄДИНІ двері модуля: реекспортуємо лише фасад
export type { Reservation, OrderId };
export interface Warehouse {                 // сусіди імпортують тільки це
  reserve(id: OrderId, qty: number): Reservation;
}
export const makeWarehouse = (s: StockTable): Warehouse => new WarehouseService(s);
// StockTable назовні НЕ експортовано — його не існує для сусідів
