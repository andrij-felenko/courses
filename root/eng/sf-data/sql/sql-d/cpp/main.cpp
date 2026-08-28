#include <iostream>
#include <string_view>
#include <memory>
#include <stdexcept>
#include <optional>
#include <sqlite3.h>

/* Ідіоматична обгортка мовою C++ з RAII-керуванням ресурсами */
class StatementHandle {
public:
    explicit StatementHandle(sqlite3* db, std::string_view sql) {
        sqlite3_stmt* raw_stmt = nullptr;
        if (sqlite3_prepare_v2(db, sql.data(), static_cast<int>(sql.size()), &raw_stmt, nullptr) != SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(db));
        }
        stmt_.reset(raw_stmt);
    }

    [[nodiscard]] sqlite3_stmt* get() const noexcept { return stmt_.get(); }

private:
    struct Deleter {
        void operator()(sqlite3_stmt* s) const noexcept {
            if (s) sqlite3_finalize(s);
        }
    };
    std::unique_ptr<sqlite3_stmt, Deleter> stmt_;
};

std::optional<double> get_user_balance(sqlite3* db, int user_id) {
    StatementHandle stmt(db, "SELECT balance FROM accounts WHERE user_id = ?;");

    if (sqlite3_bind_int(stmt.get(), 1, user_id) != SQLITE_OK) {
        throw std::runtime_error("Помилка прив'язки цілочислового параметра");
    }

    int rc = sqlite3_step(stmt.get());
    if (rc == SQLITE_ROW) {
        return sqlite3_column_double(stmt.get(), 0);
    }
    if (rc == SQLITE_DONE) {
        return std::nullopt;
    }

    throw std::runtime_error("Помилка під час зчитування кортежу");
}
