#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <expected>
#include <chrono>
#include <thread>
#include <csignal>
#include <libpq-fe.h>

namespace outbox {

struct Event {
    std::string id;
    std::string topic;
    std::string key;
    std::string payload;
};

// RAII обгортка для з'єднання з базою даних PostgreSQL
class DbConnection {
public:
    explicit DbConnection(std::string_view conninfo)
        : conn_(PQconnectdb(conninfo.data()), &PQfinish) {
        if (PQstatus(conn_.get()) != CONNECTION_OK) {
            throw std::runtime_error("DB Connection failed: " + std::string(PQerrorMessage(conn_.get())));
        }
    }

    PGconn* get() const noexcept { return conn_.get(); }

private:
    std::unique_ptr<PGconn, decltype(&PQfinish)> conn_;
};

// RAII обгортка для результату SQL-запиту
class DbResult {
public:
    explicit DbResult(PGresult* res) : res_(res, &PQclear) {}

    PGresult* get() const noexcept { return res_.get(); }
    ExecStatusType status() const noexcept { return PQresultStatus(res_.get()); }
    int rowCount() const noexcept { return PQntuples(res_.get()); }
    
    std::string_view get(int row, int col) const noexcept {
        return std::string_view(PQgetvalue(res_.get(), row, col));
    }

private:
    std::unique_ptr<PGresult, decltype(&PQclear)> res_;
};

class OutboxPublisher {
public:
    explicit OutboxPublisher(DbConnection& db, size_t batchSize = 50)
        : db_(db), batchSize_(batchSize) {}

    // Повертає кількість успішно оброблених подій або помилку
    std::expected<size_t, std::string> processBatch() {
        if (!execCommand("BEGIN;")) {
            return std::unexpected("Failed to begin transaction");
        }

        const std::string fetchSql = 
            "SELECT id, aggregate_type, aggregate_id, payload "
            "FROM outbox "
            "ORDER BY created_at ASC "
            "LIMIT $1 "
            "FOR UPDATE SKIP LOCKED;";

        std::string limitStr = std::to_string(batchSize_);
        const char* params[1] = { limitStr.c_str() };

        DbResult res(PQexecParams(db_.get(), fetchSql.c_str(), 1, nullptr, params, nullptr, nullptr, 0));
        if (res.status() != PGRES_TUPLES_OK) {
            execCommand("ROLLBACK;");
            return std::unexpected("Fetch outbox events failed: " + std::string(PQerrorMessage(db_.get())));
        }

        int count = res.rowCount();
        if (count == 0) {
            execCommand("COMMIT;");
            return 0;
        }

        std::vector<std::string> publishedIds;
        publishedIds.reserve(count);

        for (int i = 0; i < count; ++i) {
            Event ev{
                std::string(res.get(i, 0)),
                std::string(res.get(i, 1)),
                std::string(res.get(i, 2)),
                std::string(res.get(i, 3))
            };

            if (!sendToBroker(ev)) {
                execCommand("ROLLBACK;");
                return std::unexpected("Broker publish failed for event: " + ev.id);
            }

            publishedIds.push_back(ev.id);
        }

        // Видаляємо всі опубліковані події пачки
        for (const auto& id : publishedIds) {
            const char* delParams[1] = { id.c_str() };
            DbResult delRes(PQexecParams(db_.get(), "DELETE FROM outbox WHERE id = $1;", 1, nullptr, delParams, nullptr, nullptr, 0));
            if (delRes.status() != PGRES_COMMAND_OK) {
                execCommand("ROLLBACK;");
                return std::unexpected("Delete event failed: " + id);
            }
        }

        if (!execCommand("COMMIT;")) {
            return std::unexpected("Failed to commit transaction");
        }

        return publishedIds.size();
    }

private:
    DbConnection& db_;
    size_t batchSize_;

    bool execCommand(std::string_view sql) {
        DbResult res(PQexec(db_.get(), sql.data()));
        return res.status() == PGRES_COMMAND_OK;
    }

    bool sendToBroker(const Event& ev) const noexcept {
        // У продакшені: виклик librdkafka продюсера з перевіркою доставки
        return !ev.id.empty() && !ev.topic.empty();
    }
};

} // namespace outbox

static volatile std::sig_atomic_t g_stop = 0;

int main() {
    std::signal(SIGINT, [](int) { g_stop = 1; });
    std::signal(SIGTERM, [](int) { g_stop = 1; });

    try {
        outbox::DbConnection db("host=localhost port=5432 dbname=shop user=postgres password=secret");
        outbox::OutboxPublisher publisher(db, 50);

        while (!g_stop) {
            auto result = publisher.processBatch();
            if (result.has_value()) {
                if (result.value() == 0) {
                    std::this_thread::sleep_for(std::chrono::milliseconds(200));
                }
            } else {
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
            }
        }
    } catch (const std::exception& e) {
        return 1;
    }

    return 0;
}
