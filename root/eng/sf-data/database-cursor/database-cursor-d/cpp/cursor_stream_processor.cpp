// cursor_stream_processor.cpp — Ідіоматичний RAII-конвеєр на C++20
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <format>
#include <stdexcept>
#include <libpq-fe.h>

struct PgConnDeleter {
    void operator()(PGconn* c) const noexcept { if (c) PQfinish(c); }
};

struct PgResultDeleter {
    void operator()(PGresult* r) const noexcept { if (r) PQclear(r); }
};

using UniquePgConn = std::unique_ptr<PGconn, PgConnDeleter>;
using UniquePgResult = std::unique_ptr<PGresult, PgResultDeleter>;

struct StreamStats {
    uint64_t total_rows = 0;
    double total_sum = 0.0;
};

/* Безпечна RAII-обгортка над життєвим циклом транзакції та серверного курсора */
class ScopedDatabaseCursor {
public:
    ScopedDatabaseCursor(PGconn* conn, std::string_view cursor_name, std::string_view sql_query, size_t chunk_size = 1000)
        : conn_(conn), name_(cursor_name), chunk_size_(chunk_size) {
        
        execute_command("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;");
        
        std::string decl_sql = std::format("DECLARE {} NO SCROLL CURSOR FOR {};", name_, sql_query);
        execute_command(decl_sql);
        
        fetch_sql_ = std::format("FETCH {} FROM {};", chunk_size_, name_);
    }

    ~ScopedDatabaseCursor() noexcept {
        try {
            if (active_) {
                execute_command(std::format("CLOSE {};", name_));
                execute_command("COMMIT;");
            }
        } catch (...) {
            // Деструктори не повинні викидати винятків
        }
    }

    ScopedDatabaseCursor(const ScopedDatabaseCursor&) = delete;
    ScopedDatabaseCursor& operator=(const ScopedDatabaseCursor&) = delete;
    ScopedDatabaseCursor(ScopedDatabaseCursor&&) noexcept = default;

    UniquePgResult fetch_chunk() {
        if (!active_) return nullptr;

        auto res = UniquePgResult(PQexec(conn_, fetch_sql_.c_str()));
        if (PQresultStatus(res.get()) != PGRES_TUPLES_OK) {
            throw std::runtime_error(std::format("Помилка виконання FETCH: {}", PQerrorMessage(conn_)));
        }

        if (PQntuples(res.get()) == 0) {
            active_ = false;
            return nullptr;
        }
        return res;
    }

private:
    void execute_command(std::string_view sql) {
        auto res = UniquePgResult(PQexec(conn_, sql.data()));
        if (PQresultStatus(res.get()) != PGRES_COMMAND_OK) {
            throw std::runtime_error(std::format("Помилка SQL [{}]: {}", sql, PQerrorMessage(conn_)));
        }
    }

    PGconn* conn_;
    std::string name_;
    size_t chunk_size_;
    std::string fetch_sql_;
    bool active_ = true;
};

StreamStats process_large_dataset_cpp(std::string_view conninfo) {
    UniquePgConn conn(PQconnectdb(conninfo.data()));
    if (PQstatus(conn.get()) != CONNECTION_OK) {
        throw std::runtime_error(std::format("Збій з'єднання з базою даних: {}", PQerrorMessage(conn.get())));
    }

    StreamStats stats;
    constexpr size_t BATCH_SIZE = 1000;
    std::string_view query = "SELECT amount FROM transactions WHERE status = 'SUCCESS'";

    ScopedDatabaseCursor cursor(conn.get(), "trans_cur", query, BATCH_SIZE);

    while (auto chunk = cursor.fetch_chunk()) {
        int rows = PQntuples(chunk.get());
        for (int i = 0; i < rows; ++i) {
            if (!PQgetisnull(chunk.get(), i, 0)) {
                std::string_view val = PQgetvalue(chunk.get(), i, 0);
                stats.total_sum += std::stod(std::string(val));
                stats.total_rows++;
            }
        }
    }

    return stats;
}
