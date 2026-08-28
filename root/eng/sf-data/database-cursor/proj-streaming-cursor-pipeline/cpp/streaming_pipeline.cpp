// streaming_pipeline.cpp — Потоковий конвеєр через RAII та C++20
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

using PgConnPtr = std::unique_ptr<PGconn, PgConnDeleter>;
using PgResultPtr = std::unique_ptr<PGresult, PgResultDeleter>;

struct AggregationStats {
    uint64_t total_records = 0;
    double total_amount = 0.0;
};

/* Безпечний RAII-клас керування життєвим циклом серверного курсора */
class CursorStream {
public:
    CursorStream(PGconn* conn, std::string_view cursor_name, std::string_view query, size_t batch_size = 1000)
        : conn_(conn), cursor_name_(cursor_name), batch_size_(batch_size) {
        
        exec_command("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;");
        
        std::string decl_sql = std::format(
            "DECLARE {} NO SCROLL CURSOR FOR {};", cursor_name_, query);
        exec_command(decl_sql);
        
        fetch_cmd_ = std::format("FETCH {} FROM {};", batch_size_, cursor_name_);
    }

    ~CursorStream() noexcept {
        try {
            if (is_active_) {
                std::string close_sql = std::format("CLOSE {};", cursor_name_);
                auto res = PgResultPtr(PQexec(conn_, close_sql.c_str()));
                auto commit_res = PgResultPtr(PQexec(conn_, "COMMIT;"));
            }
        } catch (...) {
            // Деструктор гарантує відсутність викидання винятків
        }
    }

    CursorStream(const CursorStream&) = delete;
    CursorStream& operator=(const CursorStream&) = delete;
    CursorStream(CursorStream&&) noexcept = default;

    /* Зчитування наступного пакета рядків */
    PgResultPtr fetch_next_batch() {
        if (!is_active_) return nullptr;

        auto res = PgResultPtr(PQexec(conn_, fetch_cmd_.c_str()));
        if (PQresultStatus(res.get()) != PGRES_TUPLES_OK) {
            throw std::runtime_error(std::format("Помилка FETCH: {}", PQerrorMessage(conn_)));
        }

        if (PQntuples(res.get()) == 0) {
            is_active_ = false;
            return nullptr;
        }
        return res;
    }

private:
    void exec_command(std::string_view sql) {
        auto res = PgResultPtr(PQexec(conn_, sql.data()));
        if (PQresultStatus(res.get()) != PGRES_COMMAND_OK) {
            throw std::runtime_error(std::format("SQL Error: {}", PQerrorMessage(conn_)));
        }
    }

    PGconn* conn_;
    std::string cursor_name_;
    size_t batch_size_;
    std::string fetch_cmd_;
    bool is_active_ = true;
};

void run_streaming_pipeline_cpp(std::string_view conninfo) {
    PgConnPtr conn(PQconnectdb(conninfo.data()));
    if (PQstatus(conn.get()) != CONNECTION_OK) {
        throw std::runtime_error(std::format("Помилка підключення: {}", PQerrorMessage(conn.get())));
    }

    AggregationStats stats;
    constexpr size_t BATCH_SIZE = 1000;
    
    std::string_view query = "SELECT id, user_id, amount FROM transactions WHERE status = 'COMPLETED'";
    CursorStream stream(conn.get(), "trans_cursor", query, BATCH_SIZE);

    while (auto batch = stream.fetch_next_batch()) {
        int rows = PQntuples(batch.get());
        int col_amount = PQfnumber(batch.get(), "amount");

        for (int i = 0; i < rows; ++i) {
            if (!PQgetisnull(batch.get(), i, col_amount)) {
                std::string_view val_sv = PQgetvalue(batch.get(), i, col_amount);
                double amount = std::stod(std::string(val_sv));
                stats.total_amount += amount;
                stats.total_records++;
            }
        }
    }

    std::cout << std::format("Опрацьовано: {} рядків, Загальна сума: {:.2f}\n", 
                             stats.total_records, stats.total_amount);
}
