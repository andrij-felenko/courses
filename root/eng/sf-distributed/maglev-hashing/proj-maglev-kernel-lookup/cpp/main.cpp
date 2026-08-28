#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <array>
#include <atomic>
#include <memory>
#include <cstdint>
#include <span>
#include <stdexcept>

class MaglevConsistentRouter {
public:
    static constexpr uint32_t TABLE_SIZE = 65537u; // Просте число Ферма M
    static constexpr size_t MAX_BACKENDS = 64;

    struct Backend {
        std::string name;
        uint32_t offset{0};
        uint32_t skip{0};
        uint32_t weight{1};
        bool is_alive{true};
    };

    struct LookupTable {
        std::array<int32_t, TABLE_SIZE> lookup;
        uint32_t generation{0};

        LookupTable() {
            lookup.fill(-1);
        }
    };

    MaglevConsistentRouter() {
        tables_[0] = std::make_unique<LookupTable>();
        tables_[1] = std::make_unique<LookupTable>();
        active_table_.store(tables_[0].get(), std::memory_order_release);
    }

    void add_backend(std::string_view name, uint32_t weight = 1) {
        if (backends_.size() >= MAX_BACKENDS) {
            throw std::runtime_error("Перевищено ліміт кількості бекендів");
        }

        Backend b;
        b.name = std::string(name);
        b.weight = (weight == 0) ? 1 : weight;
        b.is_alive = true;
        b.offset = fnv1a_32(name, 0x9e3779b9u) % TABLE_SIZE;
        b.skip = (fnv1a_32(name, 0x85ebca6bu) % (TABLE_SIZE - 1)) + 1;

        backends_.push_back(std::move(b));
    }

    void set_backend_status(size_t index, bool alive) {
        if (index >= backends_.size()) {
            throw std::out_of_range("Некоректний індекс бекенда");
        }
        backends_[index].is_alive = alive;
    }

    void rebuild_table() {
        uint32_t next_idx = 1 - current_table_idx_;
        LookupTable& target = *tables_[next_idx];
        target.lookup.fill(-1);

        std::array<uint32_t, MAX_BACKENDS> next{};
        uint32_t filled = 0;

        while (filled < TABLE_SIZE) {
            bool any_progress = false;

            for (size_t i = 0; i < backends_.size(); ++i) {
                if (!backends_[i].is_alive) continue;

                for (uint32_t w = 0; w < backends_[i].weight; ++w) {
                    while (true) {
                        uint32_t c = (backends_[i].offset + next[i] * backends_[i].skip) % TABLE_SIZE;
                        next[i]++;

                        if (target.lookup[c] == -1) {
                            target.lookup[c] = static_cast<int32_t>(i);
                            filled++;
                            any_progress = true;
                            break;
                        }
                    }
                    if (filled == TABLE_SIZE) break;
                }
                if (filled == TABLE_SIZE) break;
            }

            if (!any_progress && filled < TABLE_SIZE) break;
        }

        target.generation++;
        current_table_idx_ = next_idx;
        active_table_.store(&target, std::memory_order_release);
    }

    [[nodiscard]] const Backend& dispatch(uint32_t src_ip, uint32_t dst_ip,
                                          uint16_t src_port, uint16_t dst_port,
                                          uint8_t proto) const {
        const LookupTable* tbl = active_table_.load(std::memory_order_acquire);
        if (!tbl) {
            throw std::runtime_error("Таблиця Maglev не ініціалізована");
        }

        uint32_t h = hash_5tuple(src_ip, dst_ip, src_port, dst_port, proto);
        int32_t backend_id = tbl->lookup[h % TABLE_SIZE];

        if (backend_id < 0 || static_cast<size_t>(backend_id) >= backends_.size()) {
            throw std::runtime_error("Усі бекенди недоступні");
        }

        return backends_[static_cast<size_t>(backend_id)];
    }

    [[nodiscard]] std::span<const Backend> backends() const noexcept {
        return backends_;
    }

private:
    static constexpr uint32_t fnv1a_32(std::string_view data, uint32_t seed) noexcept {
        uint32_t hash = 2166136261u ^ seed;
        for (char c : data) {
            hash ^= static_cast<uint8_t>(c);
            hash *= 16777619u;
        }
        return hash;
    }

    static constexpr uint32_t hash_5tuple(uint32_t src_ip, uint32_t dst_ip,
                                          uint16_t src_port, uint16_t dst_port,
                                          uint8_t proto) noexcept {
        uint32_t h = src_ip;
        h ^= (dst_ip << 1) | (dst_ip >> 31);
        h ^= (static_cast<uint32_t>(src_port) << 16) | dst_port;
        h ^= static_cast<uint32_t>(proto) * 0x5bd1e995u;
        h ^= h >> 13;
        h *= 0x5bd1e995u;
        h ^= h >> 15;
        return h;
    }

    std::vector<Backend> backends_;
    std::array<std::unique_ptr<LookupTable>, 2> tables_;
    uint32_t current_table_idx_{0};
    std::atomic<const LookupTable*> active_table_{nullptr};
};

int main() {
    MaglevConsistentRouter router;
    router.add_backend("srv-app-01.dc1", 1);
    router.add_backend("srv-app-02.dc1", 1);
    router.add_backend("srv-app-03.dc1", 2); // Подвійна вага
    router.add_backend("srv-app-04.dc1", 1);

    router.rebuild_table();

    std::cout << "Таблицю Maglev згенеровано на " << MaglevConsistentRouter::TABLE_SIZE << " комірок.\n";

    uint32_t client_ip = 0xC0000205; // 192.0.2.5
    uint32_t vip = 0xC6336401;       // 198.51.100.1
    uint16_t client_port = 49152;
    uint16_t vip_port = 443;
    uint8_t proto = 6; // TCP

    const auto& target = router.dispatch(client_ip, vip, client_port, vip_port, proto);
    std::cout << "Клієнтський потік спрямовано на: " << target.name
              << " (вага: " << target.weight << ")\n";

    return 0;
}
