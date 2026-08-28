#include <iostream>
#include <memory>
#include <string_view>
#include <expected>
#include <stdexcept>
#include <libpq-fe.h>

// RAII обгортка для управління з'єднанням PostgreSQL
class PGConnWrapper {
    PGconn* conn_;
public:
    explicit PGConnWrapper(PGconn* conn) : conn_(conn) {}
    ~PGConnWrapper() {
        if (conn_) PQfinish(conn_);
    }
    PGConnWrapper(const PGConnWrapper&) = delete;
    PGConnWrapper& operator=(const PGConnWrapper&) = delete;
    PGConnWrapper(PGConnWrapper&& o) noexcept : conn_(o.conn_) { o.conn_ = nullptr; }

    [[nodiscard]] PGconn* get() const noexcept { return conn_; }
};

// RAII Guard для ізоляції сесії орендаря у транзакції
class TenantSessionGuard {
    PGconn* conn_;
    bool committed_ = false;
public:
    static std::expected<TenantSessionGuard, std::string> create(PGconn* conn, std::string_view tenant_id) {
        if (tenant_id.empty()) {
            return std::unexpected("Security violation: tenant_id cannot be empty");
        }

        PGresult* res = PQexec(conn, "BEGIN");
        if (PQresultStatus(res) != PGRES_COMMAND_OK) {
            PQclear(res);
            return std::unexpected("Failed to start transaction");
        }
        PQclear(res);

        // Встановлюємо змінну сесії з is_local = true
        const char* paramValues[1] = { tenant_id.data() };
        res = PQexecParams(conn,
                           "SELECT set_config('app.current_tenant', $1, true)",
                           1, nullptr, paramValues, nullptr, nullptr, 0);

        if (PQresultStatus(res) != PGRES_TUPLES_OK) {
            PQclear(res);
            PQexec(conn, "ROLLBACK");
            return std::unexpected("Failed to set app.current_tenant setting");
        }
        PQclear(res);

        return TenantSessionGuard(conn);
    }

    ~TenantSessionGuard() {
        if (!committed_ && conn_) {
            PGresult* res = PQexec(conn_, "ROLLBACK");
            PQclear(res);
        }
    }

    std::expected<void, std::string> commit() {
        PGresult* res = PQexec(conn_, "COMMIT");
        if (PQresultStatus(res) != PGRES_COMMAND_OK) {
            PQclear(res);
            return std::unexpected("Failed to commit transaction");
        }
        PQclear(res);
        committed_ = true;
        return {};
    }

private:
    explicit TenantSessionGuard(PGconn* conn) : conn_(conn) {}
};
