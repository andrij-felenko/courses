// C++20: Атомарне оформлення замовлення у моноліті (із застосуванням RAII для транзакції)
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>

class DatabaseTransaction {
public:
    explicit DatabaseTransaction(void* db_conn) : conn_(db_conn), committed_(false) {}
    
    ~DatabaseTransaction() {
        if (!committed_) {
            try {
                rollback();
            } catch (...) {}
        }
    }
    
    void commit() {
        // Запит до СУБД: COMMIT TRANSACTION
        committed_ = true;
    }
    
    void rollback() {
        // Запит до СУБД: ROLLBACK TRANSACTION
    }
    
    void execute(const std::string& query) {
        // Виконання SQL-запиту в межах транзакційного контексту
    }

private:
    void* conn_;
    bool committed_;
};

class OrderService {
public:
    void createOrderMonolith(const std::string& user_id, const std::string& item_id, int64_t amount) {
        DatabaseTransaction tx(db_conn_);

        // 1. Перевірка та списання балансу
        tx.execute("UPDATE accounts SET balance = balance - " + std::to_string(amount) + 
                   " WHERE id = '" + user_id + "' AND balance >= " + std::to_string(amount));

        // 2. Резервування товару
        tx.execute("UPDATE inventory SET stock = stock - 1 WHERE item_id = '" + item_id + "' AND stock >= 1");

        // 3. Створення запису замовлення
        tx.execute("INSERT INTO orders (user_id, item_id, amount, status) VALUES ('" + 
                   user_id + "', '" + item_id + "', " + std::to_string(amount) + ", 'COMPLETED')");

        // Атомарна фіксація. Якщо виникне виняток вище, деструктор tx виконає rollback()
        tx.commit();
    }
private:
    void* db_conn_{nullptr};
};
