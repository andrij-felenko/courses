// ── порти: інтерфейси сховища, названі мовою предмета, не мовою SQL ──
struct OrderRepository {
    virtual ~OrderRepository() = default;
    virtual Order* byId(const std::string& id) = 0;      // nullptr, якщо нема
    virtual void   save(const Order& order)   = 0;
};

struct CustomerRepository {
    virtual ~CustomerRepository() = default;
    virtual const Customer* byId(const std::string& id) = 0;
};

// ── сервіс: тонка оркестрація — дістати, сказати одне слово, зберегти ──
class PlaceOrderService {
public:
    PlaceOrderService(OrderRepository& orders, CustomerRepository& customers)
        : orders_(orders), customers_(customers) {}

    void place(const std::string& orderId, const std::string& customerId) {
        Order* order = orders_.byId(orderId);
        if (!order) throw DomainError("немає замовлення " + orderId);
        const Customer* customer = customers_.byId(customerId);
        if (!customer) throw DomainError("немає клієнта " + customerId);

        order->place(*customer);          // домен вирішує все — сервіс лише передав слово
        orders_.save(*order);             // збереження живе ЗЗОВНІ моделі
    }
private:
    OrderRepository&    orders_;
    CustomerRepository& customers_;
};
