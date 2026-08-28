#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <array>
#include <cstdint>
#include <stdexcept>

class MaglevRing {
public:
    static constexpr uint32_t TABLE_SIZE = 65537; // Просте число M

    struct Backend {
        std::string name;
        uint32_t offset{0};
        uint32_t skip{0};
        uint32_t next_idx{0};
        bool is_alive{true};
    };

    explicit MaglevRing(std::vector<std::string> names) {
        backends_.reserve(names.size());
        for (const auto& name : names) {
            add_backend(name);
        }
        rebuild_table();
    }

    void add_backend(std::string_view name) {
        Backend b;
        b.name = std::string(name);
        b.is_alive = true;
        b.offset = fnv1a(name, 0x12345678) % TABLE_SIZE;
        b.skip = (fnv1a(name, 0x87654321) % (TABLE_SIZE - 1)) + 1;
        backends_.push_back(std::move(b));
    }

    void set_backend_status(size_t index, bool alive) {
        if (index >= backends_.size()) throw std::out_of_range("Invalid backend index");
        backends_[index].is_alive = alive;
        rebuild_table();
    }

    void rebuild_table() {
        lookup_table_.fill(-1);
        for (auto& b : backends_) {
            b.next_idx = 0;
        }

        uint32_t filled = 0;
        while (filled < TABLE_SIZE) {
            for (size_t i = 0; i < backends_.size(); ++i) {
                if (!backends_[i].is_alive) continue;

                auto& b = backends_[i];
                while (true) {
                    uint32_t candidate = (b.offset + b.next_idx * b.skip) % TABLE_SIZE;
                    b.next_idx++;
                    if (lookup_table_[candidate] == -1) {
                        lookup_table_[candidate] = static_cast<int>(i);
                        filled++;
                        break;
                    }
                }
                if (filled == TABLE_SIZE) break;
            }
        }
    }

    [[nodiscard]] const Backend& dispatch(uint32_t src_ip, uint32_t dst_ip,
                                          uint16_t src_port, uint16_t dst_port,
                                          uint8_t proto) const {
        uint32_t h = hash_5tuple(src_ip, dst_ip, src_port, dst_port, proto);
        int backend_id = lookup_table_[h % TABLE_SIZE];
        if (backend_id < 0 || static_cast<size_t>(backend_id) >= backends_.size()) {
            throw std::runtime_error("Lookup table uninitialized or empty");
        }
        return backends_[static_cast<size_t>(backend_id)];
    }

private:
    static uint32_t fnv1a(std::string_view str, uint32_t seed) noexcept {
        uint32_t hash = 2166136261u ^ seed;
        for (char c : str) {
            hash ^= static_cast<uint8_t>(c);
            hash *= 16777619u;
        }
        return hash;
    }

    static uint32_t hash_5tuple(uint32_t src_ip, uint32_t dst_ip,
                                uint16_t src_port, uint16_t dst_port,
                                uint8_t proto) noexcept {
        uint32_t h = src_ip;
        h ^= (dst_ip << 1) | (dst_ip >> 31);
        h ^= (static_cast<uint32_t>(src_port) << 16) | dst_port;
        h ^= static_cast<uint32_t>(proto) * 0x5bd1e995;
        h ^= h >> 13;
        h *= 0x5bd1e995;
        h ^= h >> 15;
        return h;
    }

    std::vector<Backend> backends_;
    std::array<int, TABLE_SIZE> lookup_table_;
};

int main() {
    MaglevRing router({
        "srv-app-01.eu-central",
        "srv-app-02.eu-central",
        "srv-app-03.eu-central",
        "srv-app-04.eu-central"
    });

    std::cout << "Таблицю Maglev збудовано на " << MaglevRing::TABLE_SIZE << " комірок.\n";

    uint32_t client_ip = 0xC0000201; // 192.0.2.1
    uint32_t vip = 0xC6336401;       // 198.51.100.1
    uint16_t client_port = 54321;
    uint16_t svc_port = 443;
    uint8_t proto = 6; // TCP

    const auto& target = router.dispatch(client_ip, vip, client_port, svc_port, proto);
    std::cout << "Клієнтський потік спрямовано на: " << target.name << '\n';

    return 0;
}
