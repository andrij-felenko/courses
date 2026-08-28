interface UserDao {
    Optional<UserRow> findById(long id);
    List<UserRow> findByRole(String role);
    List<UserRow> findByIds(Collection<Long> ids);   // одразу пачку, не по одному
    void insert(UserRow u);
    void update(UserRow u);
    void delete(long id);
}

interface OrderDao {
    List<OrderRow> findByStatus(String status);
    void insert(OrderRow o);
}
