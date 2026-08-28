class InMemoryUserDao implements UserDao {
    private final Map<Long, UserRow> store = new HashMap<>();

    public Optional<UserRow> findById(long id) {
        return Optional.ofNullable(store.get(id));
    }
    public List<UserRow> findByRole(String role) {
        return store.values().stream()
            .filter(u -> u.role().equals(role))
            .sorted(comparingLong(UserRow::id)).toList();   // той самий порядок, що ORDER BY id
    }
    public List<UserRow> findByIds(Collection<Long> ids) {
        return ids.stream().map(store::get).filter(Objects::nonNull)
            .sorted(comparingLong(UserRow::id)).toList();
    }
    public void insert(UserRow u) { store.put(u.id(), u); }
    public void update(UserRow u) { store.put(u.id(), u); }
    public void delete(long id)   { store.remove(id); }
}

class InMemoryOrderDao implements OrderDao {
    private final Map<Long, OrderRow> store = new HashMap<>();

    public List<OrderRow> findByStatus(String status) {
        return store.values().stream()
            .filter(o -> o.status().equals(status))
            .sorted(comparingLong(OrderRow::id)).toList();
    }
    public void insert(OrderRow o) { store.put(o.id(), o); }
}
