#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <mutex>
#include <shared_mutex>
#include <condition_variable>
#include <chrono>
#include <optional>
#include <expected>
#include <algorithm>
#include <atomic>

using namespace std::chrono_literals;

// Тип монотонного номера журналу транзакцій
using Lsn = uint64_t;

enum class RoutingError {
    AllReplicasUnavailable,
    TimeoutWaitingForLsn,
    PrimaryWriteFailed
};

// Абстракція вузла репліки бази даних
class DatabaseReplica {
public:
    DatabaseReplica(std::string id, std::string connection_str)
        : id_(std::move(id)), connection_str_(std::move(connection_str)), applied_lsn_(0) {}

    [[nodiscard]] const std::string& id() const noexcept { return id_; }
    [[nodiscard]] Lsn current_lsn() const noexcept { return applied_lsn_.load(std::memory_order_acquire); }

    // Викликається фоновим потоком реплікації при застосуванні нового блоку WAL
    void update_applied_lsn(Lsn new_lsn) noexcept {
        {
            std::lock_guard<std::mutex> lock(cv_mutex_);
            applied_lsn_.store(new_lsn, std::memory_order_release);
        }
        cv_.notify_all();
    }

    // Очікування, поки репліка наздожене цільовий LSN
    bool wait_for_lsn(Lsn target_lsn, std::chrono::milliseconds timeout) const {
        if (current_lsn() >= target_lsn) {
            return true;
        }
        std::unique_lock<std::mutex> lock(cv_mutex_);
        return cv_.wait_for(lock, timeout, [this, target_lsn]() {
            return applied_lsn_.load(std::memory_order_acquire) >= target_lsn;
        });
    }

    // Виконання запиту читання
    [[nodiscard]] std::string execute_read(std::string_view query) const {
        return "Результат читання [" + std::string(query) + "] з репліки " + id_ + " (LSN: " + std::to_string(current_lsn()) + ")";
    }

private:
    std::string id_;
    std::string connection_str_;
    std::atomic<Lsn> applied_lsn_;
    mutable std::mutex cv_mutex_;
    mutable std::condition_variable cv_;
};

// Вузол-лідер (Primary)
class DatabasePrimary {
public:
    explicit DatabasePrimary(std::string connection_str)
        : connection_str_(std::move(connection_str)), current_lsn_(1000) {}

    // Виконання запису: фіксація транзакції та повернення нового LSN
    [[nodiscard]] std::expected<Lsn, RoutingError> execute_write(std::string_view query) {
        // Симуляція запису у сховище та просування журналу WAL
        Lsn new_commit_lsn = ++current_lsn_;
        std::cout << "[Primary] Запис виконано: " << query << " -> Commit LSN: " << new_commit_lsn << "\n";
        return new_commit_lsn;
    }

    [[nodiscard]] std::string execute_read(std::string_view query) const {
        return "Результат читання [" + std::string(query) + "] з PRIMARY (LSN: " + std::to_string(current_lsn_.load()) + ")";
    }

    [[nodiscard]] Lsn current_lsn() const noexcept { return current_lsn_.load(std::memory_order_acquire); }

private:
    std::string connection_str_;
    std::atomic<Lsn> current_lsn_;
};

// Контекст клієнтської сесії
struct ClientSession {
    std::string session_id;
    Lsn min_lsn{0};

    void observe_lsn(Lsn lsn) noexcept {
        min_lsn = std::max(min_lsn, lsn);
    }
};

// Сесійний маршрутизатор
class SessionConsistentRouter {
public:
    SessionConsistentRouter(std::shared_ptr<DatabasePrimary> primary,
                            std::vector<std::shared_ptr<DatabaseReplica>> replicas,
                            std::chrono::milliseconds max_replica_wait = 50ms)
        : primary_(std::move(primary)),
          replicas_(std::move(replicas)),
          max_replica_wait_(max_replica_wait) {}

    // Виконання операції запису від клієнта
    std::expected<void, RoutingError> handle_write(ClientSession& session, std::string_view query) {
        auto result = primary_->execute_write(query);
        if (!result) {
            return std::unexpected(result.error());
        }
        session.observe_lsn(*result);
        return {};
    }

    // Виконання операції читання з гарантією RYW та Monotonic Reads
    std::expected<std::string, RoutingError> handle_read(ClientSession& session, std::string_view query) {
        Lsn required_lsn = session.min_lsn;

        // 1. Спроба знайти репліку, яка вже готова
        std::shared_ptr<DatabaseReplica> best_replica = nullptr;
        Lsn best_lsn = 0;

        for (const auto& rep : replicas_) {
            Lsn rep_lsn = rep->current_lsn();
            if (rep_lsn >= required_lsn) {
                session.observe_lsn(rep_lsn);
                return rep->execute_read(query);
            }
            if (rep_lsn > best_lsn) {
                best_lsn = rep_lsn;
                best_replica = rep;
            }
        }

        // 2. Якщо всі репліки відстають, чекаємо на найсвіжішій
        if (best_replica && best_replica->wait_for_lsn(required_lsn, max_replica_wait_)) {
            session.observe_lsn(best_replica->current_lsn());
            return best_replica->execute_read(query);
        }

        // 3. Якщо таймаут вичерпано, аварійний Fallback на Primary
        std::cout << "[Router] Всі репліки відстають (потрібен LSN " << required_lsn
                  << "). Перенаправлення читання на Primary!\n";
        session.observe_lsn(primary_->current_lsn());
        return primary_->execute_read(query);
    }

private:
    std::shared_ptr<DatabasePrimary> primary_;
    std::vector<std::shared_ptr<DatabaseReplica>> replicas_;
    std::chrono::milliseconds max_replica_wait_;
};
