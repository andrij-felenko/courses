#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <chrono>
#include <random>
#include <thread>
#include <expected>
#include <system_error>
#include <poll.h>
#include <sys/socket.h>
#include <libpq-fe.h>

class DatabaseConnectionException : public std::runtime_error {
public:
    explicit DatabaseConnectionException(const std::string& message)
        : std::runtime_error(message) {}
};

/* RAII-делетери для безпечного управління структурами C-бібліотеки libpq */
struct PgConnCleanup { 
    void operator()(PGconn* conn) const noexcept { 
        if (conn) PQfinish(conn); 
    } 
};

struct PgResultCleanup { 
    void operator()(PGresult* res) const noexcept { 
        if (res) PQclear(res); 
    } 
};

using ScopedPgConn = std::unique_ptr<PGconn, PgConnCleanup>;
using ScopedPgResult = std::unique_ptr<PGresult, PgResultCleanup>;

class ResilientDatabaseClient {
public:
    explicit ResilientDatabaseClient(std::string conninfo)
        : conninfo_(std::move(conninfo)), rng_(std::random_device{}()) {
        if (!reconnect()) {
            throw DatabaseConnectionException("Не вдалося встановити первинний зв'язок із пулером");
        }
    }

    /* Виконання лямбда-функції в межах строгої транзакції з RAII-відкатом */
    template <typename TransactionCallback>
    auto executeTransaction(TransactionCallback&& callback) -> std::expected<void, std::string> {
        ensureConnectionAlive();

        auto beginRes = executeRaw("BEGIN");
        if (!beginRes || PQresultStatus(beginRes.get()) != PGRES_COMMAND_OK) {
            return std::unexpected("Помилка ініціалізації транзакції (BEGIN): " + getErrorString());
        }

        try {
            callback(conn_.get());
        } catch (...) {
            executeRaw("ROLLBACK");
            throw;
        }

        auto commitRes = executeRaw("COMMIT");
        if (!commitRes || PQresultStatus(commitRes.get()) != PGRES_COMMAND_OK) {
            executeRaw("ROLLBACK");
            return std::unexpected("Помилка фіксації транзакції (COMMIT): " + getErrorString());
        }

        return {};
    }

    ScopedPgResult executeRaw(std::string_view sql) {
        return ScopedPgResult(PQexec(conn_.get(), sql.data()));
    }

private:
    std::string conninfo_;
    ScopedPgConn conn_;
    std::mt19937 rng_;

    static constexpr int kInitialBackoffMs = 50;
    static constexpr int kMaxBackoffMs = 2000;
    static constexpr int kMaxRetries = 5;

    bool isSocketHealthy() const noexcept {
        if (!conn_ || PQstatus(conn_.get()) != CONNECTION_OK) return false;
        int fd = PQsocket(conn_.get());
        if (fd < 0) return false;

        pollfd pfd{ .fd = fd, .events = POLLIN | POLLRDHUP | POLLERR | POLLHUP, .revents = 0 };
        int pollStatus = poll(&pfd, 1, 0);
        if (pollStatus < 0) return false;
        if (pollStatus > 0) {
            if (pfd.revents & (POLLERR | POLLHUP | POLLRDHUP)) return false;
            if (pfd.revents & POLLIN) {
                char buffer[1];
                ssize_t bytes = recv(fd, buffer, sizeof(buffer), MSG_PEEK | MSG_DONTWAIT);
                if (bytes == 0) return false; // FIN-пакет від пулера
                if (bytes < 0 && errno != EAGAIN && errno != EWOULDBLOCK) return false;
            }
        }
        return true;
    }

    void ensureConnectionAlive() {
        if (!isSocketHealthy()) {
            if (!reconnect()) {
                throw DatabaseConnectionException("Втрачено зв'язок із пулером, повторні спроби вичерпано");
            }
        }
    }

    bool reconnect() {
        conn_.reset();
        int backoffWindow = kInitialBackoffMs;

        for (int attempt = 1; attempt <= kMaxRetries; ++attempt) {
            conn_.reset(PQconnectdb(conninfo_.c_str()));
            if (PQstatus(conn_.get()) == CONNECTION_OK) {
                return true;
            }

            conn_.reset();
            std::uniform_int_distribution<int> dist(0, backoffWindow);
            int jitteredDelay = dist(rng_);
            std::this_thread::sleep_for(std::chrono::milliseconds(jitteredDelay));

            backoffWindow = std::min(backoffWindow * 2, kMaxBackoffMs);
        }
        return false;
    }

    std::string getErrorString() const {
        return conn_ ? PQerrorMessage(conn_.get()) : "З'єднання відсутнє";
    }
};
