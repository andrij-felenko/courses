interface OrderService {
    Order getOrder(String id);            // читання: часте, безпечне, кешується
    String placeOrder(Order order);       // запис: треба право
    void cancelOrder(String id);          // запис: треба право (вище)
}

// Справжній сервіс: ходить у базу, нічого не знає про права й кеш.
class RealOrderService implements OrderService {
    public Order getOrder(String id) {
        return db.query("SELECT ... WHERE id = ?", id);   // дорогий похід у базу
    }
    public String placeOrder(Order order) {
        return db.insert(order);
    }
    public void cancelOrder(String id) {
        db.update("UPDATE orders SET state='cancelled' WHERE id = ?", id);
    }
}
