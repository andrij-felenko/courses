#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <mutex>
#include <chrono>
#include <algorithm>
#include <cstdint>
#include <cctype>
#include <optional>

namespace db_router {

using Lsn = uint64_t;
using Timestamp = std::chrono::steady_clock::time_point;

enum class QueryType {
    Unknown,
    Read,             // Звичайний SELECT
    ReadLocking,      // SELECT ... FOR UPDATE / FOR SHARE
    Write,            // INSERT, UPDATE, DELETE, DDL, Write-CTE
    TxBegin,          // BEGIN, START TRANSACTION
    TxCommit,         // COMMIT
    TxRollback,       // ROLLBACK
    SessionMutation   // SET @var, CREATE TEMPORARY TABLE
};

enum class NodeRole {
    Primary,
    Replica
};

struct DbNode {
    int id;
    std::string host;
    int port;
    NodeRole role;
    bool is_healthy{true};
    Lsn last_applied_lsn{1000};
    uint32_t lag_ms{0};
    uint64_t active_connections{0};

    DbNode(int node_id, std::string node_host, int node_port, NodeRole node_role)
        : id(node_id), host(std::move(node_host)), port(node_port), role(node_role) {}
};

class ClientSession {
public:
    int client_id;
    bool in_transaction{false};
    bool session_polluted{false};
    Lsn last_write_lsn{0};
    std::optional<Timestamp> last_write_time{std::nullopt};
    int pinned_node_id{-1};

    explicit ClientSession(int id) : client_id(id) {}

    void record_write(Lsn lsn) {
        last_write_lsn = lsn;
        last_write_time = std::chrono::steady_clock::now();
    }

    [[nodiscard]] bool is_in_sticky_window(std::chrono::seconds window_duration) const {
        if (!last_write_time.has_value()) return false;
        auto now = std::chrono::steady_clock::now();
        return (now - *last_write_time) < window_duration;
    }
};

class SqlClassifier {
public:
    static QueryType classify(std::string_view sql) {
        auto p = trim_leading_whitespace(sql);
        if (p.empty()) return QueryType::Unknown;

        // Пропуск C-подібних коментарів /* ... */
        while (p.starts_with("/*")) {
            auto end_idx = p.find("*/");
            if (end_idx == std::string_view::npos) return QueryType::Unknown;
            p = trim_leading_whitespace(p.substr(end_idx + 2));
        }

        if (starts_with_ci(p, "BEGIN") || starts_with_ci(p, "START TRANSACTION")) {
            return QueryType::TxBegin;
        }
        if (starts_with_ci(p, "COMMIT")) {
            return QueryType::TxCommit;
        }
        if (starts_with_ci(p, "ROLLBACK")) {
            return QueryType::TxRollback;
        }
        if (starts_with_ci(p, "INSERT") || starts_with_ci(p, "UPDATE") ||
            starts_with_ci(p, "DELETE") || starts_with_ci(p, "REPLACE") ||
            starts_with_ci(p, "ALTER")  || starts_with_ci(p, "DROP") ||
            starts_with_ci(p, "CREATE TABLE") || starts_with_ci(p, "TRUNCATE") ||
            starts_with_ci(p, "WITH ")) {
            return QueryType::Write;
        }
        if (starts_with_ci(p, "SET ") || starts_with_ci(p, "CREATE TEMPORARY")) {
            return QueryType::SessionMutation;
        }
        if (starts_with_ci(p, "SELECT")) {
            if (contains_ci(p, "FOR UPDATE") ||
                contains_ci(p, "LOCK IN SHARE MODE") ||
                contains_ci(p, "FOR SHARE")) {
                return QueryType::ReadLocking;
            }
            return QueryType::Read;
        }

        return QueryType::Write; // Безпечний дефолт
    }

private:
    static std::string_view trim_leading_whitespace(std::string_view s) {
        while (!s.empty() && std::isspace(static_cast<unsigned char>(s.front()))) {
            s.remove_prefix(1);
        }
        return s;
    }

    static bool starts_with_ci(std::string_view s, std::string_view prefix) {
        if (s.size() < prefix.size()) return false;
        return std::equal(prefix.begin(), prefix.end(), s.begin(),
            [](char a, char b) {
                return std::tolower(static_cast<unsigned char>(a)) ==
                       std::tolower(static_cast<unsigned char>(b));
            });
    }

    static bool contains_ci(std::string_view hay, std::string_view needle) {
        auto it = std::search(hay.begin(), hay.end(), needle.begin(), needle.end(),
            [](char a, char b) {
                return std::tolower(static_cast<unsigned char>(a)) ==
                       std::tolower(static_cast<unsigned char>(b));
            });
        return it != hay.end();
    }
};

class CausalDatabaseRouter {
public:
    static constexpr uint32_t MAX_ALLOWED_LAG_MS = 2000;
    static constexpr std::chrono::seconds STICKY_WINDOW{3};

    CausalDatabaseRouter(std::string p_host, int p_port)
        : primary_(std::make_shared<DbNode>(0, std::move(p_host), p_port, NodeRole::Primary)) {}

    void add_replica(std::string host, int port) {
        std::lock_guard<std::mutex> lock(mutex_);
        int next_id = static_cast<int>(replicas_.size() + 1);
        replicas_.push_back(std::make_shared<DbNode>(next_id, std::move(host), port, NodeRole::Replica));
    }

    void update_replica_status(int replica_id, bool healthy, uint32_t lag_ms, Lsn lsn) {
        std::lock_guard<std::mutex> lock(mutex_);
        for (auto& rep : replicas_) {
            if (rep->id == replica_id) {
                rep->is_healthy = healthy;
                rep->lag_ms = lag_ms;
                rep->last_applied_lsn = lsn;
                break;
            }
        }
    }

    std::shared_ptr<DbNode> route(ClientSession& session, std::string_view sql) {
        QueryType qtype = SqlClassifier::classify(sql);
        std::lock_guard<std::mutex> lock(mutex_);

        // 1. Керування транзакційними межами
        if (qtype == QueryType::TxBegin) {
            session.in_transaction = true;
            session.pinned_node_id = primary_->id;
            return primary_;
        }
        if (qtype == QueryType::TxCommit || qtype == QueryType::TxRollback) {
            session.in_transaction = false;
            session.pinned_node_id = -1;
            return primary_;
        }

        // 2. Якщо сесія в транзакції — жорстка прив'язка до Primary
        if (session.in_transaction) {
            return primary_;
        }

        // 3. Записи та блокуючі читання
        if (qtype == QueryType::Write || qtype == QueryType::ReadLocking) {
            primary_->last_applied_lsn += 10;
            session.record_write(primary_->last_applied_lsn);
            return primary_;
        }

        // 4. Мутація стану сесії (SET @var)
        if (qtype == QueryType::SessionMutation) {
            session.session_polluted = true;
            return primary_;
        }

        // 5. Чисті читання
        if (qtype == QueryType::Read) {
            Lsn required_lsn = 0;
            if (session.is_in_sticky_window(STICKY_WINDOW)) {
                required_lsn = session.last_write_lsn;
            }
            return select_healthy_replica_unlocked(required_lsn);
        }

        return primary_;
    }

private:
    std::shared_ptr<DbNode> select_healthy_replica_unlocked(Lsn required_lsn) {
        if (replicas_.empty()) {
            return primary_;
        }

        size_t attempts = replicas_.size();
        while (attempts-- > 0) {
            size_t idx = rr_index_++ % replicas_.size();
            auto& rep = replicas_[idx];

            if (rep->is_healthy && rep->lag_ms <= MAX_ALLOWED_LAG_MS) {
                if (required_lsn == 0 || rep->last_applied_lsn >= required_lsn) {
                    return rep;
                }
            }
        }

        // Безпечний fallback на Primary
        return primary_;
    }

    std::shared_ptr<DbNode> primary_;
    std::vector<std::shared_ptr<DbNode>> replicas_;
    size_t rr_index_{0};
    std::mutex mutex_;
};

} // namespace db_router
