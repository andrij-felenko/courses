#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <stdexcept>
#include <cstdint>
#include <sqlite3.h>

struct Account {
    std::int64_t id{0};
    std::string name;
    std::int64_t balance_cents{0};
};

/* RAII-обгортка над дескриптором підготовленого виразу */
class PreparedStatement {
public:
    explicit PreparedStatement(sqlite3* db, std::string_view sql) {
        sqlite3_stmt* raw_stmt = nullptr;
        int rc = sqlite3_prepare_v2(db, sql.data(), static_cast<int>(sql.size()), &raw_stmt, nullptr);
        if (rc != SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(db));
        }
        stmt_.reset(raw_stmt);
    }

    void bind_int64(int index, std::int64_t value) {
        if (sqlite3_bind_int64(stmt_.get(), index, value) != SQLITE_OK) {
            throw std::runtime_error("Помилка прив'язки int64");
        }
    }

    void bind_text(int index, std::string_view text) {
        if (sqlite3_bind_text(stmt_.get(), index, text.data(), static_cast<int>(text.size()), SQLITE_TRANSIENT) != SQLITE_OK) {
            throw std::runtime_error("Помилка прив'язки text");
        }
    }

    bool step() {
        int rc = sqlite3_step(stmt_.get());
        if (rc == SQLITE_ROW) return true;
        if (rc == SQLITE_DONE) return false;
        throw std::runtime_error("Помилка під час ітерації курсора");
    }

    void reset() {
        sqlite3_reset(stmt_.get());
        sqlite3_clear_bindings(stmt_.get());
    }

    [[nodiscard]] sqlite3_stmt* get() const noexcept { return stmt_.get(); }

private:
    struct StmtDeleter {
        void operator()(sqlite3_stmt* s) const noexcept {
            if (s) sqlite3_finalize(s);
        }
    };
    std::unique_ptr<sqlite3_stmt, StmtDeleter> stmt_;
};

/* RAII-обгортка для автоматичного керування життєвим циклом транзакцій */
class ScopedTransaction {
public:
    explicit ScopedTransaction(sqlite3* db) : db_(db), committed_(false) {
        char* err_msg = nullptr;
        if (sqlite3_exec(db_, "BEGIN IMMEDIATE TRANSACTION;", nullptr, nullptr, &err_msg) != SQLITE_OK) {
            std::string err = err_msg ? err_msg : "Невідома помилка BEGIN";
            sqlite3_free(err_msg);
            throw std::runtime_error(err);
        }
    }

    void commit() {
        char* err_msg = nullptr;
        if (sqlite3_exec(db_, "COMMIT TRANSACTION;", nullptr, nullptr, &err_msg) != SQLITE_OK) {
            std::string err = err_msg ? err_msg : "Невідома помилка COMMIT";
            sqlite3_free(err_msg);
            throw std::runtime_error(err);
        }
        committed_ = true;
    }

    ~ScopedTransaction() noexcept {
        if (!committed_ && db_) {
            sqlite3_exec(db_, "ROLLBACK TRANSACTION;", nullptr, nullptr, nullptr);
        }
    }

    ScopedTransaction(const ScopedTransaction&) = delete;
    ScopedTransaction& operator=(const ScopedTransaction&) = delete;

private:
    sqlite3* db_;
    bool committed_;
};

/* Керування переказом коштів з автоматичним відкатом при винятках */
void transfer_funds(sqlite3* db, std::int64_t from_id, std::int64_t to_id, std::int64_t amount_cents) {
    ScopedTransaction tx(db);

    PreparedStatement stmt_debit(db, "UPDATE accounts SET balance_cents = balance_cents - ? "
                                     "WHERE id = ? AND balance_cents >= ?;");
    stmt_debit.bind_int64(1, amount_cents);
    stmt_debit.bind_int64(2, from_id);
    stmt_debit.bind_int64(3, amount_cents);

    stmt_debit.step();
    if (sqlite3_changes(db) == 0) {
        throw std::runtime_error("Недостатньо коштів або рахунок платника не знайдено");
    }

    PreparedStatement stmt_credit(db, "UPDATE accounts SET balance_cents = balance_cents + ? WHERE id = ?;");
    stmt_credit.bind_int64(1, amount_cents);
    stmt_credit.bind_int64(2, to_id);

    stmt_credit.step();
    if (sqlite3_changes(db) == 0) {
        throw std::runtime_error("Рахунок отримувача не знайдено");
    }

    tx.commit();
}
