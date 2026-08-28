#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <random>
#include <algorithm>
#include <cstdint>
#include <optional>

enum class ErrorCode {
    Timeout,
    QuorumFailed,
    NotFound
};

struct Record {
    std::string key;
    std::string value;
    uint64_t    version{0};
};

class StorageNode {
public:
    explicit StorageNode(int id, double failure_rate = 0.05)
        : id_(id), failure_rate_(failure_rate), rng_(std::random_device{}()) {}

    int id() const noexcept { return id_; }

    std::expected<void, ErrorCode> write(std::string_view key, std::string_view value, uint64_t version) {
        if (simulate_failure()) {
            return std::unexpected(ErrorCode::Timeout);
        }
        if (!data_.has_value() || version >= data_->version) {
            data_ = Record{std::string(key), std::string(value), version};
        }
        return {};
    }

    std::expected<Record, ErrorCode> read(std::string_view key) {
        if (simulate_failure()) {
            return std::unexpected(ErrorCode::Timeout);
        }
        if (!data_.has_value() || data_->key != key) {
            return std::unexpected(ErrorCode::NotFound);
        }
        return *data_;
    }

    void force_corrupt_for_testing(std::string_view stale_val, uint64_t stale_ver) {
        if (data_.has_value()) {
            data_->value = std::string(stale_val);
            data_->version = stale_ver;
        }
    }

private:
    bool simulate_failure() {
        std::uniform_real_distribution<double> dist(0.0, 1.0);
        return dist(rng_) < failure_rate_;
    }

    int id_;
    double failure_rate_;
    std::mt19937 rng_;
    std::optional<Record> data_;
};

class QuorumCoordinator {
public:
    explicit QuorumCoordinator(std::vector<StorageNode>& cluster)
        : cluster_(cluster) {}

    std::expected<void, ErrorCode> write(std::string_view key, std::string_view value, 
                                         uint64_t version, size_t w_quorum) {
        std::cout << "[Coordinator] Запис key='" << key << "', val='" << value 
                  << "', ver=" << version << " (потрібно W=" << w_quorum << ")...\n";

        size_t acks = 0;
        for (auto& node : cluster_) {
            if (auto res = node.write(key, value, version); res.has_value()) {
                std::cout << "  -> Вузол " << node.id() << ": Запис OK\n";
                ++acks;
            } else {
                std::cout << "  -> Вузол " << node.id() << ": Таймаут/Відмова\n";
            }
        }

        if (acks >= w_quorum) {
            std::cout << "[Coordinator] Запис успішний: зібрано " << acks << " acks з " << w_quorum << "\n\n";
            return {};
        }

        std::cout << "[Coordinator] ПОМИЛКА: Кворум запису не зібрано!\n\n";
        return std::unexpected(ErrorCode::QuorumFailed);
    }

    std::expected<Record, ErrorCode> read(std::string_view key, size_t r_quorum) {
        std::cout << "[Coordinator] Читання key='" << key << "' (потрібно R=" << r_quorum << ")...\n";

        struct ReadResult {
            int node_id;
            Record record;
        };
        std::vector<ReadResult> successful_reads;

        for (auto& node : cluster_) {
            if (auto res = node.read(key); res.has_value()) {
                std::cout << "  <- Вузол " << node.id() << ": val='" << res->value 
                          << "', ver=" << res->version << "\n";
                successful_reads.push_back({node.id(), *res});
            } else {
                std::cout << "  <- Вузол " << node.id() << ": Недоступний\n";
            }
        }

        if (successful_reads.size() < r_quorum) {
            std::cout << "[Coordinator] ПОМИЛКА: Недостатньо відповідей для кворуму читання!\n\n";
            return std::unexpected(ErrorCode::QuorumFailed);
        }

        // Знаходження свіжої версії
        auto latest_it = std::max_element(
            successful_reads.begin(), successful_reads.end(),
            [](const ReadResult& a, const ReadResult& b) {
                return a.record.version < b.record.version;
            });

        const Record fresh_record = latest_it->record;
        std::cout << "[Coordinator] Свіже значення: val='" << fresh_record.value 
                  << "', ver=" << fresh_record.version << "\n";

        // Асинхронний Read Repair для застарілих вузлів
        std::cout << "[Coordinator] Read Repair перевірка:\n";
        for (const auto& [node_id, record] : successful_reads) {
            if (record.version < fresh_record.version) {
                std::cout << "  -> [Read Repair] Вузол " << node_id << " відстає (ver " 
                          << record.version << " < " << fresh_record.version << "). Оновлюємо...\n";
                cluster_[node_id].write(fresh_record.key, fresh_record.value, fresh_record.version);
            }
        }

        std::cout << "[Coordinator] Читання завершено успішно.\n\n";
        return fresh_record;
    }

private:
    std::vector<StorageNode>& cluster_;
};

int main() {
    std::vector<StorageNode> cluster;
    for (int i = 0; i < 5; ++i) {
        cluster.emplace_back(i, (i == 3) ? 0.35 : 0.05);
    }

    QuorumCoordinator coordinator(cluster);

    // Крок 1: Запис балансу з кворумом W=3
    auto w_res = coordinator.write("user:99", "balance:500", 1, 3);

    // Крок 2: Емуляція застарівання одного вузла
    cluster[2].force_corrupt_for_testing("balance:200", 0);

    // Крок 3: Читання з R=3 та автоматичним Read Repair
    auto r_res = coordinator.read("user:99", 3);
    if (r_res.has_value()) {
        std::cout << "Клієнт успішно прочитав: " << r_res->value 
                  << " (версія " << r_res->version << ")\n";
    }

    return 0;
}
