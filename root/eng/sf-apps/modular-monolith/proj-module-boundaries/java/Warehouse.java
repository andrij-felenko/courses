// ── warehouse/api/Warehouse.java — фасад: public, його бачать усі ──
package shop.warehouse.api;

public interface Warehouse {
    Reservation reserve(OrderId id, int qty);   // єдине, що видно ззовні
}

// ── warehouse/internal/WarehouseServiceImpl.java — НЕ public ──
package shop.warehouse.internal;

import shop.warehouse.api.Warehouse;

// зверни увагу: НЕ "public class" — клас package-private.
// Поза пакетом shop.warehouse.internal його не видно взагалі.
class WarehouseServiceImpl implements Warehouse {
    private final StockTable stock;             // StockTable теж НЕ public

    WarehouseServiceImpl(StockTable stock) { this.stock = stock; }

    @Override public Reservation reserve(OrderId id, int qty) {
        return stock.hold(id, qty);
    }
}

// ── orders намагається зрадити межу ──
package shop.orders.internal;

import shop.warehouse.api.Warehouse;                       // ✅ фасад — можна
// import shop.warehouse.internal.WarehouseServiceImpl;    // ❌ НЕ КОМПІЛЮЄТЬСЯ:
//   "WarehouseServiceImpl is not public in shop.warehouse.internal;
//    cannot be accessed from outside package"
