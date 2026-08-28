// router.cpp - Високопродуктивний шардинг-маршрутизатор мовою C++20
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <queue>
#include <memory>
#include <algorithm>
#include <optional>
#include <expected>
#include <cstdint>

namespace dist {

struct Row {
    std::string key;
    std::string value;

    auto operator<=>(const Row &other) const = default;
};

// 64-бітний хеш FNV-1a для constexpr та string_view
constexpr uint64_t fnv1a_hash(std::string_view key) noexcept {
    uint64_t hash = 14695981039346656037ULL;
    for (char c : key) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 1099511628211ULL;
    }
    return hash;
}

class ShardNode {
public:
    ShardNode(int id, std::string addr, std::string r_start, std::string r_end)
        : id_(id), address_(std::move(addr)),
          range_start_(std::move(r_start)), range_end_(std::move(r_end)) {}

    [[nodiscard]] int id() const noexcept { return id_; }
    [[nodiscard]] std::string_view address() const noexcept { return address_; }
    [[nodiscard]] std::string_view range_start() const noexcept { return range_start_; }
    [[nodiscard]] std::string_view range_end() const noexcept { return range_end_; }

    void put(std::string key, std::string val) {
        auto it = std::lower_bound(rows_.begin(), rows_.end(), key,
            [](const Row &r, const std::string &k) { return r.key < k; });
        if (it != rows_.end() && it->key == key) {
            it->value = std::move(val);
        } else {
            rows_.insert(it, Row{std::move(key), std::move(val)});
        }
    }

    [[nodiscard]] std::vector<Row> scan_range(std::string_view start, std::string_view end) const {
        std::vector<Row> res;
        for (const auto &row : rows_) {
            if (row.key >= start && row.key <= end) {
                res.push_back(row);
            }
        }
        return res;
    }

private:
    int id_;
    std::string address_;
    std::string range_start_;
    std::string range_end_;
    std::vector<Row> rows_;
};

enum class RoutingStrategy {
    KeyRange,
    KeyHash
};

enum class RouterError {
    NoAvailableShards,
    KeyOutOfRange,
    Timeout
};

class PartitionRouter {
public:
    explicit PartitionRouter(RoutingStrategy strategy) : strategy_(strategy) {}

    void add_shard(int id, std::string addr, std::string start, std::string end) {
        shards_.push_back(std::make_unique<ShardNode>(id, std::move(addr), std::move(start), std::move(end)));
    }

    [[nodiscard]] std::expected<int, RouterError> route_key(std::string_view key) const noexcept {
        if (shards_.empty()) return std::unexpected(RouterError::NoAvailableShards);

        if (strategy_ == RoutingStrategy::KeyHash) {
            return static_cast<int>(fnv1a_hash(key) % shards_.size());
        }

        for (size_t i = 0; i < shards_.size(); ++i) {
            if (key >= shards_[i]->range_start() && key <= shards_[i]->range_end()) {
                return static_cast<int>(i);
            }
        }
        return std::unexpected(RouterError::KeyOutOfRange);
    }

    void put(std::string key, std::string val) {
        auto shard_idx = route_key(key);
        if (shard_idx.has_value()) {
            shards_[*shard_idx]->put(std::move(key), std::move(val));
        }
    }

    // Потоковий Scatter-Gather з K-канальним злиттям через std::priority_queue
    struct Cursor {
        std::vector<Row> buffer;
        size_t pos{0};
        int shard_id{0};

        [[nodiscard]] bool has_next() const noexcept { return pos < buffer.size(); }
        [[nodiscard]] const Row& current() const noexcept { return buffer[pos]; }
        void advance() noexcept { ++pos; }
    };

    struct HeapComparator {
        bool operator()(const Cursor *a, const Cursor *b) const noexcept {
            return a->current().key > b->current().key; // Мін-купа за ключем
        }
    };

    [[nodiscard]] std::vector<Row> scatter_gather_scan(std::string_view key_start,
                                                       std::string_view key_end,
                                                       size_t limit,
                                                       size_t offset = 0) const {
        std::vector<std::unique_ptr<Cursor>> active_cursors;

        // Фаза Scatter: надсилаємо запити релевантним шардам
        for (const auto &shard : shards_) {
            if (strategy_ == RoutingStrategy::KeyRange) {
                if (key_start > shard->range_end() || key_end < shard->range_start()) {
                    continue;
                }
            }
            auto data = shard->scan_range(key_start, key_end);
            if (!data.empty()) {
                auto cur = std::make_unique<Cursor>(Cursor{std::move(data), 0, shard->id()});
                active_cursors.push_back(std::move(cur));
            }
        }

        std::priority_queue<Cursor*, std::vector<Cursor*>, HeapComparator> min_heap;
        for (const auto &cur : active_cursors) {
            if (cur->has_next()) min_heap.push(cur.get());
        }

        // Фаза Gather & K-Way Merge
        std::vector<Row> result;
        result.reserve(limit);
        size_t skipped = 0;

        while (!min_heap.empty() && result.size() < limit) {
            Cursor *top = min_heap.top();
            min_heap.pop();

            if (skipped >= offset) {
                result.push_back(top->current());
            } else {
                ++skipped;
            }

            top->advance();
            if (top->has_next()) {
                min_heap.push(top);
            }
        }

        return result;
    }

private:
    RoutingStrategy strategy_;
    std::vector<std::unique_ptr<ShardNode>> shards_;
};

} // namespace dist

int main() {
    using namespace dist;

    PartitionRouter router(RoutingStrategy::KeyRange);
    router.add_shard(0, "10.0.0.1:9042", "A", "H");
    router.add_shard(1, "10.0.0.2:9042", "I", "P");
    router.add_shard(2, "10.0.0.3:9042", "Q", "Z");

    router.put("Alice", "role:admin");
    router.put("Bob", "role:user");
    router.put("Charlie", "role:manager");
    router.put("Denys", "role:developer");
    router.put("Ivan", "role:qa");
    router.put("Maria", "role:designer");
    router.put("Orest", "role:devops");
    router.put("Roman", "role:architect");
    router.put("Taras", "role:lead");
    router.put("Zenon", "role:intern");

    std::cout << "--- Точкова маршрутизація ---\n";
    if (auto idx = router.route_key("Maria"); idx) {
        std::cout << "Ключ 'Maria' закріплено за шардом: " << *idx << '\n';
    }

    std::cout << "\n--- Scatter-Gather вибірка ['B' .. 'T'], LIMIT 4, OFFSET 2 ---\n";
    auto page = router.scatter_gather_scan("B", "T", 4, 2);
    for (const auto &r : page) {
        std::cout << "  [Результат] " << r.key << " => " << r.value << '\n';
    }

    return 0;
}
