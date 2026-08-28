#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <map>
#include <algorithm>
#include <memory>
#include <shared_mutex>
#include <future>
#include <chrono>
#include <stdexcept>
#include <sstream>
#include <cstdint>

// 64-бітний хеш FNV-1a для детермінованого розсіювання ключів
class HashUtil {
public:
    static uint64_t fnv1a64(std::string_view key) noexcept {
        uint64_t hash = 0xcbf29ce484222325ULL;
        for (char c : key) {
            hash ^= static_cast<uint8_t>(c);
            hash *= 0x100000001b3ULL;
        }
        return hash;
    }
};

// Модель запису бази даних
struct Record {
    std::string key;
    std::string value;
    int64_t timestamp;
};

// Абстракція фізичного шарду
class ShardClient {
public:
    explicit ShardClient(std::string shardId, std::string endpoint)
        : shardId_(std::move(shardId)), endpoint_(std::move(endpoint)) {}

    [[nodiscard]] const std::string& getId() const noexcept { return shardId_; }
    [[nodiscard]] const std::string& getEndpoint() const noexcept { return endpoint_; }

    // Точковий запис
    bool put(const std::string& key, const std::string& value) {
        // Емуляція виконання запиту до вузла
        return !key.empty() && !value.empty();
    }

    // Точкове читання
    [[nodiscard]] std::string get(const std::string& key) const {
        return "val_from_" + shardId_ + "_for_" + key;
    }

    // Сканування даних для Scatter-Gather
    [[nodiscard]] std::vector<Record> scan(std::string_view queryFilter, std::chrono::milliseconds timeout) const {
        // Емуляція тривалості запиту
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        
        std::vector<Record> results;
        results.push_back({ "k1_" + shardId_, "payload_match", 100 + static_cast<int64_t>(shardId_.size()) });
        results.push_back({ "k2_" + shardId_, "payload_match", 200 + static_cast<int64_t>(shardId_.size()) });
        return results;
    }

private:
    std::string shardId_;
    std::string endpoint_;
};

// Кільце консистентного хешування
class ConsistentHashRing {
public:
    explicit ConsistentHashRing(size_t virtualNodesPerShard = 128)
        : virtualNodes_(virtualNodesPerShard) {}

    void addShard(const std::string& shardId) {
        for (size_t i = 0; i < virtualNodes_; ++i) {
            std::string vnodeKey = shardId + "#vnode_" + std::to_string(i);
            uint64_t token = HashUtil::fnv1a64(vnodeKey);
            ring_[token] = shardId;
        }
    }

    void removeShard(const std::string& shardId) {
        for (auto it = ring_.begin(); it != ring_.end(); ) {
            if (it->second == shardId) {
                it = ring_.erase(it);
            } else {
                ++it;
            }
        }
    }

    [[nodiscard]] std::string getShard(std::string_view key) const {
        if (ring_.empty()) {
            throw std::runtime_error("Consistent hash ring is empty: no shards available");
        }
        uint64_t token = HashUtil::fnv1a64(key);
        // Пошук першого вузла, токен якого >= токену ключа
        auto it = ring_.lower_bound(token);
        if (it == ring_.end()) {
            // Замикання кільця (Wrap-around)
            it = ring_.begin();
        }
        return it->second;
    }

private:
    size_t virtualNodes_;
    std::map<uint64_t, std::string> ring_;
};

// Топологія кластера (незмінна структура під захистом Shared Pointer)
struct ClusterTopology {
    uint64_t version{ 0 };
    std::shared_ptr<ConsistentHashRing> ring;
    std::map<std::string, std::shared_ptr<ShardClient>> shards;
};

// Розподілений маршрутизатор
class ShardRouter {
public:
    ShardRouter() {
        auto initialTopology = std::make_shared<ClusterTopology>();
        initialTopology->version = 1;
        initialTopology->ring = std::make_shared<ConsistentHashRing>(128);
        std::atomic_store(&currentTopology_, initialTopology);
    }

    // Атомне оновлення конфігурації
    void updateTopology(const std::vector<std::pair<std::string, std::string>>& shardList) {
        auto nextTopology = std::make_shared<ClusterTopology>();
        nextTopology->ring = std::make_shared<ConsistentHashRing>(128);

        for (const auto& [shardId, endpoint] : shardList) {
            nextTopology->shards[shardId] = std::make_shared<ShardClient>(shardId, endpoint);
            nextTopology->ring->addShard(shardId);
        }

        auto oldTopology = std::atomic_load(&currentTopology_);
        nextTopology->version = oldTopology ? oldTopology->version + 1 : 1;

        // Атомарна підміна покажчика топології (RCU патерн)
        std::atomic_store(&currentTopology_, nextTopology);
        std::cout << "[Router] Topology updated to version " << nextTopology->version 
                  << " with " << shardList.size() << " shards.\n";
    }

    // Точковий запис
    bool put(const std::string& key, const std::string& value) {
        auto topology = std::atomic_load(&currentTopology_);
        std::string targetShardId = topology->ring->getShard(key);
        
        auto it = topology->shards.find(targetShardId);
        if (it == topology->shards.end()) {
            throw std::runtime_error("Target shard not found in active topology: " + targetShardId);
        }
        return it->second->put(key, value);
    }

    // Точкове читання
    std::string get(const std::string& key) {
        auto topology = std::atomic_load(&currentTopology_);
        std::string targetShardId = topology->ring->getShard(key);

        auto it = topology->shards.find(targetShardId);
        if (it == topology->shards.end()) {
            throw std::runtime_error("Target shard not found in active topology: " + targetShardId);
        }
        return it->second->get(key);
    }

    // Паралельний Scatter-Gather запит
    std::vector<Record> scatterGatherScan(std::string_view queryFilter, std::chrono::milliseconds timeout) {
        auto topology = std::atomic_load(&currentTopology_);
        const auto& shards = topology->shards;

        if (shards.empty()) return {};

        // Запуск паралельних асинхронних завдань
        std::vector<std::future<std::vector<Record>>> futures;
        futures.reserve(shards.size());

        for (const auto& [id, client] : shards) {
            futures.push_back(std::async(std::launch::async, [client, queryFilter, timeout]() {
                return client->scan(queryFilter, timeout);
            }));
        }

        std::vector<Record> aggregatedResults;

        // Збір результатів із бар'єром синхронізації
        for (auto& fut : futures) {
            auto status = fut.wait_for(timeout);
            if (status == std::future_status::ready) {
                auto shardRows = fut.get();
                aggregatedResults.insert(aggregatedResults.end(), shardRows.begin(), shardRows.end());
            } else {
                std::cerr << "[Router] Warning: Shard query timed out during Scatter-Gather.\n";
            }
        }

        // Локальне сортування об'єднаного результату
        std::sort(aggregatedResults.begin(), aggregatedResults.end(), [](const Record& a, const Record& b) {
            return a.timestamp > b.timestamp; // Свіжі записи першими
        });

        return aggregatedResults;
    }

private:
    std::shared_ptr<ClusterTopology> currentTopology_;
};

int main() {
    ShardRouter router;

    // Ініціалізація кластера з трьох шардів
    router.updateTopology({
        { "shard-0", "10.0.1.10:3306" },
        { "shard-1", "10.0.1.11:3306" },
        { "shard-2", "10.0.1.12:3306" }
    });

    // Тест точкових операцій
    router.put("user_10842", "{ name: 'Alice', balance: 540 }");
    router.put("user_99214", "{ name: 'Bob', balance: 1280 }");

    std::cout << "[Client] Read user_10842: " << router.get("user_10842") << "\n";
    std::cout << "[Client] Read user_99214: " << router.get("user_99214") << "\n";

    // Тест Scatter-Gather
    std::cout << "[Client] Executing Scatter-Gather scan...\n";
    auto rows = router.scatterGatherScan("status = 'ACTIVE'", std::chrono::milliseconds(100));
    std::cout << "[Client] Total records returned across cluster: " << rows.size() << "\n";
    for (const auto& row : rows) {
        std::cout << "  - Key: " << row.key << " | TS: " << row.timestamp << "\n";
    }

    return 0;
}
