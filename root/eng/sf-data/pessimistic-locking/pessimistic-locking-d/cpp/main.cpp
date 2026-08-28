#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <chrono>
#include <thread>
#include <random>
#include <expected>
#include <stdexcept>
#include <libpq-fe.h>

enum class TransferError {
    ConnectionFailed,
    AccountNotFound,
    InsufficientFunds,
    LockTimeout,
    DeadlockExhausted,
    DatabaseError
};

class PgQueryResult {
public:
    explicit PgQueryResult(PGresult* res) : res_(res) {}
    ~PgQueryResult() { if (res_) PQclear(res_); }

    PgQueryResult(const PgQueryResult&) = delete;
    PgQueryResult& operator=(const PgQueryResult&) = delete;

    PgQueryResult(PgQueryResult&& other) noexcept : res_(other.res_) { other.res_ = nullptr; }
    PgQueryResult& operator=(PgQueryResult&& other) noexcept {
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
    [[nodiscard]] const char* errorField(int field) const { return PQresultErrorField(res_, field); }

private:
    PGresult* res_{nullptr};
};

class DatabaseClient {
public:
    explicit DatabaseClient(std::string_view conninfo) {
        conn_ = PQconnectdb(conninfo.data());
        if (PQstatus(conn_) != CONNECTION_OK) {
            std::string msg = PQerrorMessage(conn_);
            PQfinish(conn_);
            throw std::runtime_error("Database connection failure: " + msg);
        }
    }

    ~DatabaseClient() {
        if (conn_) {
            PQfinish(conn_);
        }
    }

    DatabaseClient(const DatabaseClient&) = delete;
    DatabaseClient& operator=(const DatabaseClient&) = delete;

    PgQueryResult execute(std::string_view sql) {
        return PgQueryResult(PQexec(conn_, sql.data()));
    }

private:
    PGconn* conn_{nullptr};
};

class BankTransferService {
public:
    explicit BankTransferService(std::string_view conninfo)
        : db_(std::make_unique<DatabaseClient>(conninfo)) {}

    std::expected<void, TransferError> transferFunds(int64_t fromId, int64_t toId, double amount) {
        db_->execute("SET lock_timeout = '2s';");

        // Канонічний порядок: спочатку блокуємо менший ідентифікатор
        const int64_t firstId = std::min(fromId, toId);
        const int64_t secondId = std::max(fromId, toId);

        constexpr int maxRetries = 3;
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<int> jitterDist(0, 20);

        for (int attempt = 0; attempt < maxRetries; ++attempt) {
            auto beginRes = db_->execute("BEGIN;");
            if (beginRes.status() != PGRES_COMMAND_OK) {
                return std::unexpected(TransferError::DatabaseError);
            }

            std::string lockSql = 
                "SELECT id, balance FROM accounts WHERE id IN (" 
                + std::to_string(firstId) + ", " + std::to_string(secondId) 
                + ") ORDER BY id ASC FOR UPDATE;";

            auto lockRes = db_->execute(lockSql);
            if (lockRes.status() != PGRES_TUPLES_OK) {
                const char* sqlstate = lockRes.errorField(PG_DIAG_SQLSTATE);
                db_->execute("ROLLBACK;");

                if (sqlstate) {
                    std::string_view state(sqlstate);
                    if (state == "40P01" || state == "55P03" || state == "57014") {
                        if (attempt < maxRetries - 1) {
                            auto backoff = std::chrono::milliseconds(50 * (1 << attempt) + jitterDist(gen));
                            std::this_thread::sleep_for(backoff);
                            continue;
                        }
                        return std::unexpected(TransferError::DeadlockExhausted);
                    }
                }
                return std::unexpected(TransferError::DatabaseError);
            }

            if (lockRes.rowCount() != 2) {
                db_->execute("ROLLBACK;");
                return std::unexpected(TransferError::AccountNotFound);
            }

            double sourceBalance = 0.0;
            for (int i = 0; i < 2; ++i) {
                int64_t id = std::stoll(lockRes.getValue(i, 0));
                if (id == fromId) {
                    sourceBalance = std::stod(lockRes.getValue(i, 1));
                }
            }

            if (sourceBalance < amount) {
                db_->execute("ROLLBACK;");
                return std::unexpected(TransferError::InsufficientFunds);
            }

            std::string updateSql = 
                "UPDATE accounts SET balance = balance - " + std::to_string(amount) 
                + " WHERE id = " + std::to_string(fromId) + "; "
                + "UPDATE accounts SET balance = balance + " + std::to_string(amount) 
                + " WHERE id = " + std::to_string(toId) + ";";

            auto updateRes = db_->execute(updateSql);
            if (updateRes.status() != PGRES_COMMAND_OK) {
                db_->execute("ROLLBACK;");
                return std::unexpected(TransferError::DatabaseError);
            }

            auto commitRes = db_->execute("COMMIT;");
            if (commitRes.status() == PGRES_COMMAND_OK) {
                return {}; // Успіх
            }
        }

        return std::unexpected(TransferError::DeadlockExhausted);
    }

private:
    std::unique_ptr<DatabaseClient> db_;
};
