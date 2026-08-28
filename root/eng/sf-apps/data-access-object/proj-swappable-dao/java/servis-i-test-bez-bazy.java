public class DigestService {
    private final UserDao users;
    private final OrderDao orders;
    public DigestService(UserDao users, OrderDao orders) {
        this.users = users;
        this.orders = orders;
    }

    public List<String> digest() {
        List<OrderRow> paid = orders.findByStatus("paid");           // 1 запит
        Set<Long> ids = paid.stream().map(OrderRow::userId).collect(toSet());
        Map<Long, UserRow> byId = users.findByIds(ids).stream()      // 1 запит на ВСІХ
            .collect(toMap(UserRow::id, u -> u));
        return paid.stream()
            .map(o -> byId.get(o.userId()).email() + " → " + money(o.cents()))
            .toList();
    }

    private static String money(long cents) {
        return String.format("%d.%02d", cents / 100, cents % 100);   // 1500 → 15.00
    }
}
