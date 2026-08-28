#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <optional>
#include <chrono>
#include <thread>
#include <atomic>
#include <vector>

// Структура репліки бази даних
class DatabaseReplica {
private:
    std::string name_;
    std::unordered_map<std::string, std::pair<std::string, uint64_t>> storage_;
    std::atomic<uint64_t> current_lsn_{0};

public:
    explicit DatabaseReplica(std::string name) : name_(std::move(name)) {}

    const std::string& name() const { return name_; }
    uint64_t current_lsn() const { return current_lsn_.load(); }

    void apply_write(const std::string& key, const std::string& val, uint64_t lsn) {
        storage_[key] = {val, lsn};
        current_lsn_.store(lsn);
    }

    std::optional<std::string> read(const std::string& key, uint64_t min_lsn) const {
        // Якщо репліка відстає від вимог клієнта — читання відхиляється
        if (current_lsn_.load() < min_lsn) {
            return std::nullopt;
        }
        auto it = storage_.find(key);
        if (it != storage_.end()) {
            return it->second.first;
        }
        return std::nullopt;
    }
};

// Сесійний проксі-клієнт
class SessionConsistentClient {
private:
    std::vector<std::shared_ptr<DatabaseReplica>> replicas_;
    std::atomic<uint64_t>& global_lsn_gen_;
    uint64_t session_lsn_{0}; // Локальний токен причинності клієнта

public:
    SessionConsistentClient(std::vector<std::shared_ptr<DatabaseReplica>> replicas,
                            std::atomic<uint64_t>& lsn_gen)
        : replicas_(std::move(replicas)), global_lsn_gen_(lsn_gen) {}

    // Виконання запису: оновлюємо первинну репліку та фіксуємо LSN у сесії
    void write(const std::string& key, const std::string& val) {
        uint64_t new_lsn = ++global_lsn_gen_;
        // Пишемо на перший доступний вузол (імітація лідера)
        replicas_[0]->apply_write(key, val, new_lsn);
        session_lsn_ = new_lsn;
        std::cout << "[Client Write] Успішно записано '" << key << " = " << val
                  << "'. Сесійний токен LSN оновлено до " << session_lsn_ << "\n";
    }

    // Виконання читання: гарантуємо, що прочитаний вузол не старіший за session_lsn_
    std::string read(const std::string& key) {
        for (const auto& replica : replicas_) {
            auto res = replica->read(key, session_lsn_);
            if (res.has_value()) {
                std::cout << "[Client Read] Прочитано з " << replica->name()
                          << " (LSN " << replica->current_lsn() << "): " << *res << "\n";
                return *res;
            } else {
                std::cout << "[Client Read Bypass] Репліка " << replica->name()
                          << " відстає (LSN " << replica->current_lsn()
                          << " < " << session_lsn_ << "). Пропускаємо...\n";
            }
        }
        throw std::runtime_error("Усі доступні репліки відстають від сесії клієнта!");
    }
};

int main() {
    std::atomic<uint64_t> lsn_generator{0};

    auto primary = std::make_shared<DatabaseReplica>("Primary-EU");
    auto replica_fast = std::make_shared<DatabaseReplica>("Replica-Fast");
    auto replica_lagging = std::make_shared<DatabaseReplica>("Replica-Lagging");

    SessionConsistentClient client({primary, replica_fast, replica_lagging}, lsn_generator);

    std::cout << "=== 1. Клієнт виконує оновлення даних ===\n";
    client.write("user:101:status", "VIP-Tier");

    std::cout << "\n=== 2. Асинхронна реплікація з лагом ===\n";
    // Replica-Fast наздогнала Primary
    replica_fast->apply_write("user:101:status", "VIP-Tier", 1);
    // Replica-Lagging залишилася на LSN = 0

    std::cout << "\n=== 3. Клієнт читає свій запис із кластера ===\n";
    std::string value = client.read("user:101:status");
    std::cout << "Підсумковий прочитаний результат: " << value << "\n";

    return 0;
}
