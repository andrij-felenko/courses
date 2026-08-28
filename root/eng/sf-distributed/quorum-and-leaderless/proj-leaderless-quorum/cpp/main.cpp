#include <iostream>
#include <string>
#include <vector>
#include <optional>
#include <cstdint>
#include <algorithm>
#include <unordered_map>

struct Record {
    std::string key;
    std::string value;
    uint64_t    version{0};
    bool        is_deleted{false};
};

class ReplicaNode {
public:
    explicit ReplicaNode(uint32_t id) : id_(id), is_alive_(true) {}

    [[nodiscard]] uint32_t id() const noexcept { return id_; }
    [[nodiscard]] bool is_alive() const noexcept { return is_alive_; }
    void set_alive(bool state) noexcept { is_alive_ = state; }

    bool write(const std::string& key, const std::string& val, uint64_t ver) {
        if (!is_alive_) return false;

        auto it = storage_.find(key);
        if (it != storage_.end()) {
            if (ver >= it->second.version) {
                it->second = Record{key, val, ver, false};
            }
        } else {
            storage_[key] = Record{key, val, ver, false};
        }
        return true;
    }

    [[nodiscard]] std::optional<Record> read(const std::string& key) const {
        if (!is_alive_) return std::nullopt;

        auto it = storage_.find(key);
        if (it != storage_.end()) {
            return it->second;
        }
        /* Вузол живий, але ключа немає */
        return Record{key, "", 0, false};
    }

private:
    uint32_t id_;
    bool is_alive_;
    std::unordered_map<std::string, Record> storage_;
};

class LeaderlessCoordinator {
public:
    LeaderlessCoordinator(std::vector<ReplicaNode>& cluster, size_t w, size_t r)
        : cluster_(cluster), w_quorum_(w), r_quorum_(r) {}

    bool write(const std::string& key, const std::string& val, uint64_t ver) {
        size_t acks = 0;
        std::cout << "[Coordinator] Запис key='" << key << "', val='" << val
                  << "', ver=" << ver << " (потрібно W=" << w_quorum_
                  << " з N=" << cluster_.size() << ")...\n";

        for (auto& node : cluster_) {
            if (node.write(key, val, ver)) {
                ++acks;
                std::cout << "  -> Вузол " << node.id() << ": OK (підтверджено)\n";
            } else {
                std::cout << "  -> Вузол " << node.id() << ": ВІДМОВА (недоступний)\n";
            }
        }

        if (acks >= w_quorum_) {
            std::cout << "[Coordinator] УСПІХ: зібрано " << acks << " ACK >= W=" << w_quorum_ << "\n\n";
            return true;
        }
        std::cout << "[Coordinator] ПОМИЛКА КВОРУМУ: зібрано лише " << acks << " ACK\n\n";
        return false;
    }

    std::optional<Record> read(const std::string& key) {
        struct NodeResponse {
            uint32_t node_id;
            Record record;
        };

        std::vector<NodeResponse> responses;
        std::cout << "[Coordinator] Читання key='" << key
                  << "' (потрібно R=" << r_quorum_
                  << " з N=" << cluster_.size() << ")...\n";

        for (auto& node : cluster_) {
            if (responses.size() >= r_quorum_) break;

            if (auto rec = node.read(key)) {
                responses.push_back({node.id(), *rec});
                std::cout << "  <- Відповідь від вузла " << node.id()
                          << ": val='" << rec->value
                          << "', ver=" << rec->version << "\n";
            } else {
                std::cout << "  <- Вузол " << node.id() << " не відповів (таймаут)\n";
            }
        }

        if (responses.size() < r_quorum_) {
            std::cout << "[Coordinator] ПОМИЛКА КВОРУМУ ЧИТАННЯ: замало відповідей\n\n";
            return std::nullopt;
        }

        /* Пошук максимальної версії серед опитаного кворуму */
        auto best_it = std::max_element(responses.begin(), responses.end(),
            [](const NodeResponse& a, const NodeResponse& b) {
                return a.record.version < b.record.version;
            });

        Record newest = best_it->record;
        std::cout << "[Coordinator] Обрано найновіший стан: val='" << newest.value
                  << "', ver=" << newest.version << "\n";

        /* ФАЗА READ-REPAIR: асинхронне лікування відсталих вузлів */
        for (const auto& resp : responses) {
            if (resp.record.version < newest.version) {
                std::cout << "  [Read-Repair] Вузол " << resp.node_id
                          << " відстає (ver=" << resp.record.version
                          << " < " << newest.version << ") -> зцілення...\n";

                for (auto& node : cluster_) {
                    if (node.id() == resp.node_id) {
                        node.write(key, newest.value, newest.version);
                        std::cout << "  [Read-Repair] Вузол " << resp.node_id
                                  << " оновлено до ver=" << newest.version << "!\n";
                        break;
                    }
                }
            }
        }
        std::cout << "\n";
        return newest;
    }

private:
    std::vector<ReplicaNode>& cluster_;
    size_t w_quorum_;
    size_t r_quorum_;
};

int main() {
    std::vector<ReplicaNode> cluster;
    cluster.emplace_back(1);
    cluster.emplace_back(2);
    cluster.emplace_back(3);

    LeaderlessCoordinator coordinator(cluster, /*W=*/2, /*R=*/2);

    std::cout << "=== Сценарій 1: Звичайний запис (W=2) при всіх живих вузлах ===\n";
    coordinator.write("user:101", "Andriy", 1);

    std::cout << "=== Сценарій 2: Вузол 3 падає; оновлення записується на вузли 1 і 2 ===\n";
    cluster[2].set_alive(false);
    coordinator.write("user:101", "Andriy Felenko", 2);

    std::cout << "=== Сценарій 3: Вузол 3 оживає зі старим станом (ver=1) ===\n";
    cluster[2].set_alive(true);
    cluster[0].set_alive(false); // Вузол 1 стає тимчасово недоступним

    auto result = coordinator.read("user:101");

    std::cout << "=== Сценарій 4: Перевірка після Read-Repair (Вузол 3 має бути оновлений) ===\n";
    auto direct_check = cluster[2].read("user:101");
    if (direct_check) {
        std::cout << "Прямий погляд на сховище Вузла 3: val='"
                  << direct_check->value << "', ver=" << direct_check->version
                  << " (Зцілення підтверджено!)\n";
    }

    return 0;
}
