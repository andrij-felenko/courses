#include <iostream>
#include <string>
#include <stdexcept>
#include <system_error>

namespace db {

class Connection {
public:
    void execute(std::string_view sql) {
        // Відправка SQL-команди до рушія СУБД
    }
};

// RAII-обгортка для гарантованого закриття транзакційного контексту
class TransactionGuard {
public:
    explicit TransactionGuard(Connection& conn) : conn_(conn) {
        conn_.execute("BEGIN TRANSACTION;");
    }

    ~TransactionGuard() noexcept {
        if (!committed_) {
            try {
                conn_.execute("ROLLBACK;");
            } catch (...) {
                // Поглинання помилок у деструкторі
            }
        }
    }

    TransactionGuard(const TransactionGuard&) = delete;
    TransactionGuard& operator=(const TransactionGuard&) = delete;

    void commit() {
        conn_.execute("COMMIT;");
        committed_ = true;
    }

private:
    Connection& conn_;
    bool committed_{false};
};

void execute_money_transfer(Connection& conn, int from_id, int to_id, int64_t amount) {
    TransactionGuard txn(conn);

    conn.execute("UPDATE accounts SET balance = balance - " + std::to_string(amount) +
                 " WHERE id = " + std::to_string(from_id) + ";");

    conn.execute("UPDATE accounts SET balance = balance + " + std::to_string(amount) +
                 " WHERE id = " + std::to_string(to_id) + ";");

    // Якщо до цього рядка виникне виняток, деструктор txn автоматично виконає ROLLBACK
    txn.commit();
}

} // namespace db
