// ЗАДУМАНО: логіка залежить від порту, не від бази.
struct OrderRepository {                     // порт: контракт без бази
    virtual Order load(int id) = 0;
    virtual ~OrderRepository() = default;
};

int order_total(OrderRepository& repo, int id) {
    Order o = repo.load(id);                 // жодного сліду бази
    return o.total();
}
