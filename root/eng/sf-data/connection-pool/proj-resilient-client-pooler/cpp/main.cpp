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

class DatabaseError : public std::runtime_error {
public:
    explicit DatabaseError(const std::string& msg) : std::runtime_error(msg) {}
};

/* RAII-керування життєвим циклом низькорівневих C-структур libpq */
struct PgConnDeleter { 
    void operator()(PGconn* p) const noexcept { 
        if (p) PQfinish(p); 
    } 
};

struct PgResultDeleter { 
    void operator()(PGresult* p) const noexcept { 
        if (p) PQclear(p); 
    } 
};

using UniquePgConn = std::unique_ptr<PGconn, PgConnDeleter>;
using UniquePgResult = std::unique_ptr<PGresult, PgResultDeleter>;

class ResilientDbClient {
public:
    explicit ResilientDbClient(std::string conninfo)
        : conninfo_(std::move(conninfo)), rng_(std::random_device{}()) {
        if (!reconnect()) {
            throw DatabaseError("Не вдалося встановити початкове з'єднання з пулером");
        }
    }

    /* Виконання функції всередині безпечної транзакції з RAII-відкатом */
    template <typename Func>
    auto withTransaction(Func&& action) -> std::expected<void, std::string> {
        ensureHealthyConnection();

        auto resBegin = execQuery("BEGIN");
        if (!resBegin || PQresultStatus(resBegin.get()) != PGRES_COMMAND_OK) {
            return std::unexpected("Помилка старту транзакції (BEGIN): " + getLastError());
        }

        try {
            action(conn_.get());
        } catch (...) {
            execQuery("ROLLBACK");
            throw;
        }

        auto resCommit = execQuery("COMMIT");
        if (!resCommit || PQresultStatus(resCommit.get()) != PGRES_COMMAND_OK) {
            execQuery("ROLLBACK");
            return std::unexpected("Помилка фіксації транзакції (COMMIT): " + getLastError());
        }

        return {};
    }

    UniquePgResult execQuery(std::string_view sql) {
        return UniquePgResult(PQexec(conn_.get(), sql.data()));
    }

private:
    std::string conninfo_;
    UniquePgConn conn_;
    std::mt19937 rng_;

    static constexpr int kBaseBackoffMs = 50;
    static constexpr int kMaxBackoffMs = 2000;
    static constexpr int kMaxRetries = 5;

    bool isSocketAlive() const noexcept {
        if (!conn_ || PQstatus(conn_.get()) != CONNECTION_OK) return false;
        int fd = PQsocket(conn_.get());
        if (fd < 0) return false;

        pollfd pfd{ .fd = fd, .events = POLLIN | POLLRDHUP | POLLERR | POLLHUP, .revents = 0 };
        int ret = poll(&pfd, 1, 0);
        if (ret < 0) return false;
        if (ret > 0) {
            if (pfd.revents & (POLLERR | POLLHUP | POLLRDHUP)) return false;
            if (pfd.revents & POLLIN) {
                char buf[1];
                ssize_t n = recv(fd, buf, sizeof(buf), MSG_PEEK | MSG_DONTWAIT);
                if (n == 0) return false;
                if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK) return false;
            }
        }
        return true;
    }

    void ensureHealthyConnection() {
        if (!isSocketAlive()) {
            if (!reconnect()) {
                throw DatabaseError("Втрата з'єднання з пулером, повторні спроби вичерпано");
            }
        }
    }

    bool reconnect() {
        conn_.reset();
        int currentBackoff = kBaseBackoffMs;

        for (int attempt = 1; attempt <= kMaxRetries; ++attempt) {
            conn_.reset(PQconnectdb(conninfo_.c_str()));
            if (PQstatus(conn_.get()) == CONNECTION_OK) {
                return true;
            }

            conn_.reset();
            std::uniform_int_distribution<int> dist(0, currentBackoff);
            int sleepTime = dist(rng_);
            std::this_thread::sleep_for(std::chrono::milliseconds(sleepTime));

            currentBackoff = std::min(currentBackoff * 2, kMaxBackoffMs);
        }
        return false;
    }

    std::string getLastError() const {
        return conn_ ? PQerrorMessage(conn_.get()) : "Немає активного сокета";
    }
};
