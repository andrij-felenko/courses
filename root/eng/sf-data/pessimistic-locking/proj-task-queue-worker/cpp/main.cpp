#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <memory>
#include <chrono>
#include <thread>
#include <stdexcept>
#include <libpq-fe.h>

struct TaskItem {
    int64_t id;
    std::string payload;
    int attempts;
};

// RAII обгортка для результатів запитів PostgreSQL
class PgResult {
public:
    explicit PgResult(PGresult* res) : res_(res) {}
    ~PgResult() { if (res_) PQclear(res_); }

    PgResult(const PgResult&) = delete;
    PgResult& operator=(const PgResult&) = delete;

    PgResult(PgResult&& other) noexcept : res_(other.res_) { other.res_ = nullptr; }
    PgResult& operator=(PgResult&& other) noexcept {
        if (this != &other) {
            if (res_) PQclear(res_);
            res_ = other.res_;
            other.res_ = nullptr;
        }
        return *this;
    }

    [[nodiscard]] PGresult* get() const noexcept { return res_; }
    [[nodiscard]] ExecStatusType status() const noexcept { return PQresultStatus(res_); }
    [[nodiscard]] int rowCount() const noexcept { return PQntuples(res_); }
    [[nodiscard]] const char* getValue(int row, int col) const { return PQgetvalue(res_, row, col); }

private:
    PGresult* res_{nullptr};
};

// RAII обгортка для керування життєвим циклом з'єднання СУБД
class DatabaseConnection {
public:
    explicit DatabaseConnection(std::string_view conninfo) {
        conn_ = PQconnectdb(conninfo.data());
        if (PQstatus(conn_) != CONNECTION_OK) {
            std::string err = PQerrorMessage(conn_);
            PQfinish(conn_);
            throw std::runtime_error("Database connection failed: " + err);
        }
    }

    ~DatabaseConnection() {
        if (conn_) {
            PQfinish(conn_);
        }
    }

    DatabaseConnection(const DatabaseConnection&) = delete;
    DatabaseConnection& operator=(const DatabaseConnection&) = delete;

    PgResult execute(std::string_view sql) {
        return PgResult(PQexec(conn_, sql.data()));
    }

private:
    PGconn* conn_{nullptr};
};

class TaskQueueWorker {
public:
    explicit TaskQueueWorker(std::string_view conninfo)
        : db_(std::make_unique<DatabaseConnection>(conninfo)) {}

    std::optional<TaskItem> fetchAndLockNextTask() {
        auto beginRes = db_->execute("BEGIN;");
        if (beginRes.status() != PGRES_COMMAND_OK) {
            return std::nullopt;
        }

        constexpr std::string_view fetchSql = 
            "SELECT id, payload, attempts "
            "FROM task_queue "
            "WHERE status = 'pending' "
            "ORDER BY id ASC "
            "LIMIT 1 "
            "FOR UPDATE SKIP LOCKED;";

        auto res = db_->execute(fetchSql);
        if (res.status() != PGRES_TUPLES_OK) {
            db_->execute("ROLLBACK;");
            return std::nullopt;
        }

        if (res.rowCount() == 0) {
            db_->execute("COMMIT;");
            return std::nullopt;
        }

        TaskItem item{
            .id = std::stoll(res.getValue(0, 0)),
            .payload = res.getValue(0, 1),
            .attempts = std::stoi(res.getValue(0, 2))
        };

        return item;
    }

    void completeTask(int64_t taskId) {
        std::string updateSql = 
            "UPDATE task_queue SET status = 'completed', updated_at = NOW() WHERE id = " 
            + std::to_string(taskId) + ";";

        auto res = db_->execute(updateSql);
        if (res.status() != PGRES_COMMAND_OK) {
            db_->execute("ROLLBACK;");
            throw std::runtime_error("Failed to complete task");
        }

        db_->execute("COMMIT;");
    }

    void run() {
        while (running_) {
            try {
                auto task = fetchAndLockNextTask();
                if (task) {
                    // Обробка бізнес-логіки
                    completeTask(task->id);
                } else {
                    std::this_thread::sleep_for(std::chrono::milliseconds(100));
                }
            } catch (const std::exception& ex) {
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
            }
        }
    }

    void stop() noexcept {
        running_ = false;
    }

private:
    std::unique_ptr<DatabaseConnection> db_;
    bool running_{true};
};
