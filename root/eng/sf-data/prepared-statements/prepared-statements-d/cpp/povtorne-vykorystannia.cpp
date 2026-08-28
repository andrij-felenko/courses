#include <vector>
#include <span>
#include <string_view>
#include <sqlite3.h>

struct BalanceAdjustment {
    int64_t account_id;
    double delta;
};

// Пакетне оновлення з використанням std::span та RAII
bool batch_adjust_balances(sqlite3* db, std::span<const BalanceAdjustment> adjustments) noexcept {
    constexpr std::string_view sql = "UPDATE accounts SET balance = balance + ? WHERE id = ?;";
    sqlite3_stmt* raw_stmt = nullptr;

    if (sqlite3_prepare_v2(db, sql.data(), static_cast<int>(sql.size()), &raw_stmt, nullptr) != SQLITE_OK) {
        return false;
    }

    ScopedStmt stmt(raw_stmt);

    sqlite3_exec(db, "BEGIN TRANSACTION;", nullptr, nullptr, nullptr);

    for (const auto& item : adjustments) {
        sqlite3_bind_double(stmt.get(), 1, item.delta);
        sqlite3_bind_int64(stmt.get(), 2, item.account_id);

        if (sqlite3_step(stmt.get()) != SQLITE_DONE) {
            sqlite3_exec(db, "ROLLBACK;", nullptr, nullptr, nullptr);
            return false;
        }

        // Скидання ітератора виконання без втрати скомпільованого байт-коду
        sqlite3_reset(stmt.get());
        sqlite3_clear_bindings(stmt.get());
    }

    sqlite3_exec(db, "COMMIT;", nullptr, nullptr, nullptr);
    return true;
}
