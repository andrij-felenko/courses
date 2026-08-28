class LoggingCachingOrderService implements OrderService {
    private final Map<String, Order> cache = new HashMap<>();   // id → замовлення
    private final OrderService real;
    LoggingCachingOrderService(OrderService real) { this.real = real; }

    public Order getOrder(String id) {
        Order hit = cache.get(id);
        if (hit != null) {
            log("getOrder(" + id + ") — з кешу");
            return hit;                         // база не чіпається взагалі
        }
        log("getOrder(" + id + ") — промах, іду в базу");
        Order order = real.getOrder(id);
        cache.put(id, order);                   // запам'ятали на майбутнє
        return order;
    }

    public String placeOrder(Order order) {
        log("placeOrder(...)");
        String id = real.placeOrder(order);
        cache.put(id, order);                   // свіже замовлення одразу відоме
        return id;
    }

    public void cancelOrder(String id) {
        log("cancelOrder(" + id + ")");
        real.cancelOrder(id);
        cache.remove(id);   // ← ІНВАЛІДАЦІЯ: кеш більше не відповідає базі
    }
}
