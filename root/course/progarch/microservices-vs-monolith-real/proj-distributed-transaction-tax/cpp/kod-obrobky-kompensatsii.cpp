// C++20: Ідемпотентна обробка компенсуючого списання
#include <string>

class PaymentConsumer {
public:
    bool handleRefundCompensation(const std::string& event_id, const std::string& user_id, int64_t amount) {
        DatabaseTransaction tx(db_conn_);

        // 1. Перевірка таблиці прослуханих подій на дублікати
        if (isEventProcessed(tx, event_id)) {
            return true; // Пропускаємо дубльоване повідомлення z Kafka
        }

        // 2. Повернення балансу користувачу (компенсація)
        tx.execute("UPDATE accounts SET balance = balance + " + std::to_string(amount) +
                   " WHERE id = '" + user_id + "'");

        // 3. Збереження ідемпотентного ключа
        tx.execute("INSERT INTO processed_events (event_id) VALUES ('" + event_id + "')");

        tx.commit();
        return true;
    }
private:
    bool isEventProcessed(DatabaseTransaction& tx, const std::string& event_id) {
        // SQL запит до processed_events
        return false;
    }
    void* db_conn_{nullptr};
};
