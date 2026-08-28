#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <memory>
#include <thread>
#include <expected>
#include <sqlite3.h>

namespace embedded_db {

/* RAII-обгортка для безпечного керування дескриптором sqlite3 */
class DatabaseConnection {
public:
    static std::expected<DatabaseConnection, std::string> open(std::string_view path, int flags) {
        sqlite3* raw_db = nullptr;
        int rc = sqlite3_open_v2(path.data(), &raw_db, flags, nullptr);
        if (rc != SQLITE_OK) {
            std::string err = raw_db ? sqlite3_errmsg(raw_db) : "Невідома помилка";
            if (raw_db) sqlite3_close(raw_db);
            return std::unexpected(err);
        }

        DatabaseConnection conn(raw_db);
        conn.configure();
        return conn;
    }

    ~DatabaseConnection() {
        if (db_) {
            sqlite3_close_v2(db_);
        }
    }

    DatabaseConnection(DatabaseConnection&& other) noexcept : db_(other.db_) {
        other.db_ = nullptr;
    }

    DatabaseConnection& operator=(DatabaseConnection&& other) noexcept {
        if (this != &other) {
            if (db_) sqlite3_close_v2(db_);
            db_ = other.db_;
            other.db_ = nullptr;
        }
        return *this;
    }

    DatabaseConnection(const DatabaseConnection&) = delete;
    DatabaseConnection& operator=(const DatabaseConnection&) = delete;

    sqlite3* handle() const noexcept { return db_; }

private:
    explicit DatabaseConnection(sqlite3* db) noexcept : db_(db) {}

    void configure() {
        sqlite3_busy_timeout(db_, 5000);
        char* err_msg = nullptr;
        sqlite3_exec(db_, "PRAGMA journal_mode=WAL;", nullptr, nullptr, &err_msg);
        if (err_msg) sqlite3_free(err_msg);
        sqlite3_exec(db_, "PRAGMA synchronous=NORMAL;", nullptr, nullptr, nullptr);
    }

    sqlite3* db_{nullptr};
};

/* Обробник запитів із Zero-Copy доступом через безпечні типи std::span */
class QueryEngine {
public:
    explicit QueryEngine(sqlite3* db) : db_(db) {}

    void process_payloads() {
        constexpr std::string_view sql = "SELECT id, device_id, payload FROM sensor_payloads ORDER BY id DESC LIMIT 5;";
        sqlite3_stmt* raw_stmt = nullptr;
        
        if (sqlite3_prepare_v3(db_, sql.data(), -1, 0, &raw_stmt, nullptr) != SQLITE_OK) {
            return;
        }

        /* Автоматичне звільнення компільованого виразу через кастомний делетер */
        std::unique_ptr<sqlite3_stmt, decltype(&sqlite3_finalize)> stmt(raw_stmt, sqlite3_finalize);

        while (sqlite3_step(stmt.get()) == SQLITE_ROW) {
            int64_t id = sqlite3_column_int64(stmt.get(), 0);
            int32_t device_id = sqlite3_column_int(stmt.get(), 1);

            /* Отримання прямого константного покажчика на комірку пам'яті */
            const auto* data = static_cast<const uint8_t*>(sqlite3_column_blob(stmt.get(), 2));
            int size = sqlite3_column_bytes(stmt.get(), 2);

            /* Представлення як std::span без додаткового виділення динамічної пам'яті */
            std::span<const uint8_t> payload_view(data, static_cast<size_t>(size));

            if (!payload_view.empty()) {
                volatile uint8_t marker = payload_view[0];
                (void)marker;
            }
            (void)id;
            (void)device_id;
        }
    }

private:
    sqlite3* db_;
};

} // namespace embedded_db
