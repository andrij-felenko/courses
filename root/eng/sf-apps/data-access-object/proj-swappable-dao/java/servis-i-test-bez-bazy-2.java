class DigestServiceTest {
    @Test
    void digestPairsPaidOrdersWithOwnerEmail() {
        UserDao users = new InMemoryUserDao();
        OrderDao orders = new InMemoryOrderDao();
        users.insert(new UserRow(1, "ann@co", "approver", true));
        users.insert(new UserRow(2, "bob@co", "buyer", true));
        orders.insert(new OrderRow(10, 1, "paid",  1500));
        orders.insert(new OrderRow(11, 2, "paid",   900));
        orders.insert(new OrderRow(12, 1, "draft",  400));   // не оплачене — поза дайджестом

        List<String> digest = new DigestService(users, orders).digest();

        assertEquals(List.of("ann@co → 15.00", "bob@co → 9.00"), digest);
    }
}
