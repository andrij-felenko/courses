#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <mutex>
#include <shared_mutex>
#include <atomic>
#include <chrono>
#include <optional>
#include <algorithm>
#include <thread>
#include <stdexcept>
#include <sstream>
#include <iomanip>

// 64-бітне представлення LSN (Log Sequence Number) у форматі PostgreSQL
using Lsn = uint64_t;

// Парсинг рядка формату "X/Y" (наприклад, "1/4A8B3C10") у 64-бітне ціле число
Lsn parse_lsn(std::string_view lsn_str) {
    if (lsn_str.empty()) return 0;
    size_t slash_pos = lsn_str.find('/');
    if (slash_pos == std::string_view::npos) return 0;

    std::string high_str(lsn_str.substr(0, slash_pos));
    std::string low_str(lsn_str.substr(slash_pos + 1));

    uint32_t high = static_cast<uint32_t>(std::stoul(high_str, nullptr, 16));
    uint32_t low = static_cast<uint32_t>(std::stoul(low_str, nullptr, 16));

    return (static_cast<uint64_t>(high) << 32) | low;
}

// Форматування 64-бітного LSN у стандартний рядок PostgreSQL
std::string format_lsn(Lsn lsn) {
    std::ostringstream oss;
    uint32_t high = static_cast<uint32_t>(lsn >> 32);
    uint32_t low = static_cast<uint32_t>(lsn & 0xFFFFFFFF);
    oss << std::hex << std::uppercase << high << "/" << low;
    return oss.str();
}

// Стан окремої репліки читання з атомарними лічильниками
struct ReplicaNode {
    std::string endpoint;
    std::atomic<bool> is_alive{true};
    std::atomic<Lsn> applied_lsn{0};
    std::atomic<uint32_t> lag_ms{0};
    std::atomic<uint64_t> active_queries{0};

    explicit ReplicaNode(std::string ep) : endpoint(std::move(ep)) {}
};

enum class QueryType { READ, WRITE };

// Головний клас маршрутизатора
class LagAwareReadRouter {
public:
    LagAwareReadRouter(std::string primary_endpoint,
                       const std::vector<std::string>& replica_endpoints,
                       uint32_t max_allowed_lag_ms = 2000,
                       uint32_t max_primary_fallback_rps = 1000)
        : primary_endpoint_(std::move(primary_endpoint)),
          max_allowed_lag_ms_(max_allowed_lag_ms),
          max_primary_fallback_rps_(max_primary_fallback_rps),
          running_(true) {
        
        for (const auto& ep : replica_endpoints) {
            replicas_.push_back(std::make_shared<ReplicaNode>(ep));
        }

        // Запуск фонового потоку опитування стану реплік
        health_check_thread_ = std::thread(&LagAwareReadRouter::health_check_loop, this);
    }

    ~LagAwareReadRouter() {
        running_.store(false, std::memory_order_relaxed);
        if (health_check_thread_.joinable()) {
            health_check_thread_.join();
        }
    }

    // Класифікація запиту за текстом SQL
    static QueryType classify_query(std::string_view sql) {
        // Пропускаємо початкові пробіли
        size_t start = sql.find_first_not_of(" \t\n\r");
        if (start == std::string_view::npos) return QueryType::WRITE;

        std::string_view head = sql.substr(start, std::min<size_t>(sql.size() - start, 10));
        
        // Порівняння без урахування регістру для першого ключового слова
        if (head.size() >= 6) {
            std::string prefix(head.substr(0, 6));
            std::transform(prefix.begin(), prefix.end(), prefix.begin(), ::toupper);
            if (prefix == "SELECT") {
                // Перевірка наявності блокуючих конструкцій FOR UPDATE / FOR SHARE
                std::string full_upper(sql);
                std::transform(full_upper.begin(), full_upper.end(), full_upper.begin(), ::toupper);
                if (full_upper.find("FOR UPDATE") != std::string::npos ||
                    full_upper.find("FOR SHARE") != std::string::npos) {
                    return QueryType::WRITE;
                }
                return QueryType::READ;
            }
        }
        return QueryType::WRITE;
    }

    // Маршрутизація SQL-запиту
    std::string route_query(std::string_view sql, std::optional<Lsn> required_lsn = std::nullopt) {
        QueryType qtype = classify_query(sql);

        // Усі мутації направляються на Primary
        if (qtype == QueryType::WRITE) {
            return primary_endpoint_;
        }

        // Відбір здорових та актуальних реплік читання
        std::vector<std::shared_ptr<ReplicaNode>> eligible_replicas;
        {
            std::shared_lock<std::shared_mutex> lock(nodes_mutex_);
            for (const auto& rep : replicas_) {
                if (!rep->is_alive.load(std::memory_order_relaxed)) {
                    continue;
                }
                // Перевірка 1: лаг репліки не перевищує ліміт SLA
                if (rep->lag_ms.load(std::memory_order_relaxed) > max_allowed_lag_ms_) {
                    continue;
                }
                // Перевірка 2: сесійний інваріант LSN (Read-Your-Own-Writes)
                if (required_lsn.has_value() &&
                    rep->applied_lsn.load(std::memory_order_relaxed) < required_lsn.value()) {
                    continue;
                }
                eligible_replicas.push_back(rep);
            }
        }

        // Балансування Round-Robin серед придатних реплік
        if (!eligible_replicas.empty()) {
            size_t idx = rr_counter_.fetch_add(1, std::memory_order_relaxed) % eligible_replicas.size();
            return eligible_replicas[idx]->endpoint;
        }

        // Fallback на Primary із захистом лімітером запитів
        uint64_t now_sec = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::steady_clock::now().time_since_epoch()).count();

        if (now_sec != fallback_window_sec_.load(std::memory_order_relaxed)) {
            fallback_window_sec_.store(now_sec, std::memory_order_relaxed);
            fallback_counter_.store(0, std::memory_order_relaxed);
        }

        if (fallback_counter_.fetch_add(1, std::memory_order_relaxed) < max_primary_fallback_rps_) {
            std::cerr << "[WARN] Репліки відстають. Fallback запиту читання на Primary.\n";
            return primary_endpoint_;
        }

        throw std::runtime_error("Усі репліки відстають, а ліміт Fallback на Primary вичерпано!");
    }

    // Метод для ручного встановлення метрик вузла під час тестів
    void update_replica_state(size_t index, bool is_alive, Lsn applied_lsn, uint32_t lag_ms) {
        std::shared_lock<std::shared_mutex> lock(nodes_mutex_);
        if (index < replicas_.size()) {
            replicas_[index]->is_alive.store(is_alive, std::memory_order_relaxed);
            replicas_[index]->applied_lsn.store(applied_lsn, std::memory_order_relaxed);
            replicas_[index]->lag_ms.store(lag_ms, std::memory_order_relaxed);
        }
    }

private:
    void health_check_loop() {
        while (running_.load(std::memory_order_relaxed)) {
            // У реальному продакшн-коді тут виконується асинхронний виклик:
            // SELECT pg_last_wal_replay_lsn(), EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
        }
    }

    std::string primary_endpoint_;
    std::vector<std::shared_ptr<ReplicaNode>> replicas_;
    std::shared_mutex nodes_mutex_;

    uint32_t max_allowed_lag_ms_;
    uint32_t max_primary_fallback_rps_;

    std::atomic<bool> running_{false};
    std::thread health_check_thread_;

    std::atomic<size_t> rr_counter_{0};
    std::atomic<uint64_t> fallback_window_sec_{0};
    std::atomic<uint32_t> fallback_counter_{0};
};

int main() {
    std::vector<std::string> replicas = {
        "postgres-replica-1.internal:5432",
        "postgres-replica-2.internal:5432"
    };

    LagAwareReadRouter router("postgres-primary.internal:5432", replicas, 2000, 500);

    // Імітація початкового стану: Репліка 1 наздогнала стан, Репліка 2 відстає
    router.update_replica_state(0, true, parse_lsn("0/16B3C00"), 10);
    router.update_replica_state(1, true, parse_lsn("0/16B3800"), 500);

    // Тест 1: Операція запису завжди йде на Primary
    std::string write_sql = "INSERT INTO orders (user_id, total) VALUES (101, 450.00);";
    std::cout << "Запит: " << write_sql << "\n"
              << "-> Скеровано на: " << router.route_query(write_sql) << "\n\n";

    // Тест 2: Запит читання з сесійним LSN маркером клієнта
    Lsn user_session_lsn = parse_lsn("0/16B3A40");
    std::string read_sql = "SELECT * FROM orders WHERE user_id = 101;";
    
    std::cout << "Запит читання з сесійним LSN (" << format_lsn(user_session_lsn) << "):\n"
              << "-> Скеровано на: " << router.route_query(read_sql, user_session_lsn) << "\n\n";

    return 0;
}
