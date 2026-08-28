#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <optional>
#include <algorithm>
#include <cstdint>

enum class ConsistencyLevel {
    ONE = 1,
    QUORUM = 2,
    ALL = 3
};

struct Record {
    std::string value;
    uint64_t version = 0;
};

class ClusterNode {
public:
    explicit ClusterNode(int id) : id_(id) {}

    int id() const { return id_; }

    void write_local(const std::string& key, const std::string& val, uint64_t ver) {
        store_[key] = Record{val, ver};
    }

    std::optional<Record> read_local(const std::string& key) const {
        auto it = store_.find(key);
        if (it != store_.end()) return it->second;
        return std::nullopt;
    }

private:
    int id_;
    std::unordered_map<std::string, Record> store_;
};

class DistributedCluster {
public:
    DistributedCluster(int node_count, int rtt_ms)
        : rtt_ms_(rtt_ms), partition_active_(false) {
        for (int i = 0; i < node_count; ++i) {
            nodes_.emplace_back(i);
        }
    }

    void set_partition(bool active) {
        partition_active_ = active;
    }

    // Запис із налаштовуваним рівнем узгодженості
    bool write(int coord_id, const std::string& key, const std::string& val,
               ConsistencyLevel level, int& elapsed_latency_ms) {
        elapsed_latency_ms = 0;
        uint64_t next_ver = ++global_version_counter_;
        int required = static_cast<int>(level);
        int acks = 0;

        // 1. Локальний запис на координаторі
        nodes_[coord_id].write_local(key, val, next_ver);
        acks++;

        // 2. Реплікація на віддалені вузли
        for (auto& node : nodes_) {
            if (node.id() == coord_id) continue;

            // Якщо є розділення і вузол відрізаний від координатора
            if (partition_active_ && is_isolated(coord_id, node.id())) {
                continue; // пакет губиться в мережі
            }

            node.write_local(key, val, next_ver);
            acks++;
        }

        // Розрахунок латентності за моделлю PACELC
        if (required == 1) {
            elapsed_latency_ms = 0; // локальний запис без очікування мережі
        } else {
            elapsed_latency_ms = rtt_ms_; // потрібен щонайменше 1 раунд RTT
        }

        return acks >= required;
    }

    // Читання з налаштовуваним рівнем узгодженості
    std::optional<std::string> read(int coord_id, const std::string& key,
                                    ConsistencyLevel level, int& elapsed_latency_ms) {
        elapsed_latency_ms = 0;
        int required = static_cast<int>(level);
        std::vector<Record> responses;

        // 1. Локальне читання
        auto loc = nodes_[coord_id].read_local(key);
        if (loc) responses.push_back(*loc);

        // 2. Опитування реплік
        for (const auto& node : nodes_) {
            if (node.id() == coord_id) continue;

            if (partition_active_ && is_isolated(coord_id, node.id())) {
                continue;
            }

            auto rem = node.read_local(key);
            if (rem) responses.push_back(*rem);
        }

        if (required == 1) {
            elapsed_latency_ms = 0;
        } else {
            elapsed_latency_ms = rtt_ms_;
        }

        if (static_cast<int>(responses.size()) < required) {
            return std::nullopt; // відмова за браком кворуму (CP)
        }

        // Пошук запису з найбільшою версією (Read Repair / Highest Timestamp)
        auto newest = std::max_element(responses.begin(), responses.end(),
            [](const Record& a, const Record& b) { return a.version < b.version; });

        return newest->value;
    }

private:
    bool is_isolated(int from, int to) const {
        // Вузол 2 ізольований від вузлів 0 і 1
        if ((from == 2 && to != 2) || (from != 2 && to == 2)) return true;
        return false;
    }

    int rtt_ms_;
    bool partition_active_;
    uint64_t global_version_counter_ = 0;
    std::vector<ClusterNode> nodes_;
};
