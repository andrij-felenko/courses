#include <iostream>
#include <string_view>
#include <optional>
#include <expected>
#include <memory>
#include <span>
#include <sqlite3.h>

// Автоматичне керування життєвим циклом sqlite3_stmt через RAII
struct StmtDeleter {
    void operator()(sqlite3_stmt* stmt) const noexcept {
        if (stmt) {
            sqlite3_finalize(stmt);
        }
    }
};

using ScopedStmt = std::unique_ptr<sqlite3_stmt, StmtDeleter>;

class AccountRepository {
private:
    sqlite3* db_{nullptr};

public:
    explicit AccountRepository(sqlite3* db) noexcept : db_(db) {}

    enum class DbError {
        PrepareFailed,
        BindFailed,
        StepFailed,
        NotFound
    };

    // Безпечне виконання з типізованою обробкою результатів (C++23 std::expected)
    std::expected<double, DbError> get_balance(int64_t user_id) const noexcept {
        constexpr std::string_view query = "SELECT balance FROM accounts WHERE id = ?;";
        sqlite3_stmt* raw_stmt = nullptr;

        // 1. Компіляція виразу
        int rc = sqlite3_prepare_v2(db_, query.data(), static_cast<int>(query.size()), &raw_stmt, nullptr);
        if (rc != SQLITE_OK) {
            return std::unexpected(DbError::PrepareFailed);
        }

        ScopedStmt stmt(raw_stmt); // Гарантія виклику sqlite3_finalize при виході

        // 2. Зв'язування параметра
        if (sqlite3_bind_int64(stmt.get(), 1, user_id) != SQLITE_OK) {
            return std::unexpected(DbError::BindFailed);
        }

        // 3. Отримання результату
        rc = sqlite3_step(stmt.get());
        if (rc == SQLITE_ROW) {
            return sqlite3_column_double(stmt.get(), 0);
        } else if (rc == SQLITE_DONE) {
            return std::unexpected(DbError::NotFound);
        }

        return std::unexpected(DbError::StepFailed);
    }
};
