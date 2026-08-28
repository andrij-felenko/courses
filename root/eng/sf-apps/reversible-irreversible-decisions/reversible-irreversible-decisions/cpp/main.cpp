// ЗІ ШВОМ: логіка знає тільки інтерфейс, база — за адаптером
struct OrderRepo {                       // порт: контракт без бази
    virtual double total(int order_id) = 0;
    virtual ~OrderRepo() = default;
};

double order_total(OrderRepo& repo, int order_id) {
    return repo.total(order_id);         // жодного сліду конкретної бази
}

// Конкретна база живе в ОДНОМУ місці — в адаптері:
struct PgOrderRepo : OrderRepo {         // сьогодні PostgreSQL...
    double total(int order_id) override { /* pqxx-запит саме тут */ }
};
// Завтра інша база — новий адаптер, а order_total і виклики не міняються.
