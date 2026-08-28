// package warehouse — межа = сам пакет; лише public видно ззовні
package shop.warehouse;

public interface Warehouse {                 // ← фасад: єдине, що бачать сусіди
    Reservation reserve(OrderId id, int qty);
}

// клас реалізації — package-private (немає public), поза пакетом невидимий
class WarehouseService implements Warehouse {
    private final StockTable stock;          // ← приватна нутрощі, чужим зась
    public Reservation reserve(OrderId id, int qty) {
        return stock.hold(id, qty);          // логіка резервування
    }
}
