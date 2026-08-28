// C++20: Атомарне збереження бізнес-сутності та Outbox-події
#include <string>
#include <stdexcept>

class OutboxPublisher {
public:
    void createOrderWithOutbox(const std::string& order_id, const std::string& user_id, 
                               const std::string& item_id, int64_t amount) {
        DatabaseTransaction tx(db_conn_);

        // 1. Запис замовлення зі статусом PENDING
        tx.execute("INSERT INTO orders (id, user_id, item_id, amount, status) VALUES ('" +
                   order_id + "', '" + user_id + "', '" + item_id + "', " + std::to_string(amount) + ", 'PENDING')");

        // 2. Гарантований запис події в Outbox-таблицю
        std::string payload = "{\"order_id\":\"" + order_id + "\",\"user_id\":\"" + user_id + 
                              "\",\"amount\":" + std::to_string(amount) + "}";
        tx.execute("INSERT INTO outbox (aggregate_type, aggregate_id, type, payload) VALUES ('Order', '" +
                   order_id + "', 'OrderCreated', '" + payload + "')");

        tx.commit(); // Обидва записи комітяться атомарно
    }
private:
    void* db_conn_{nullptr};
};
