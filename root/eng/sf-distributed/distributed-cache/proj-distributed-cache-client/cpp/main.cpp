#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <format>
#include <cstdint>
#include <optional>
#include <span>

namespace cache {

// 32-бітний детермінований FNV-1a constexpr хеш
constexpr uint32_t fnv1a(std::string_view key) noexcept {
    uint32_t hash = 2166136261U;
    for (char c : key) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 16777619U;
    }
    return hash;
}

struct ServerEndpoint {
    std::string host;
    uint16_t port;

    auto operator<=>(const ServerEndpoint&) const = default;
};

class ConsistentHashRing {
public:
    struct VNode {
        uint32_t hash;
        size_t server_index;

        bool operator<(const VNode& other) const noexcept {
            return hash < other.hash;
        }
    };

    void add_server(std::string host, uint16_t port, size_t vnodes = 128) {
        size_t s_idx = servers_.size();
        servers_.push_back(ServerEndpoint{std::move(host), port});

        for (size_t v = 0; v < vnodes; ++v) {
            std::string vnode_label = std::format("{}:{}#{}", servers_[s_idx].host, servers_[s_idx].port, v);
            uint32_t h = fnv1a(vnode_label);
            ring_.push_back(VNode{h, s_idx});
        }

        std::sort(ring_.begin(), ring_.end());
    }

    [[nodiscard]] std::optional<ServerEndpoint> lookup(std::string_view key) const noexcept {
        if (ring_.empty()) {
            return std::nullopt;
        }

        uint32_t h = fnv1a(key);
        auto it = std::lower_bound(ring_.begin(), ring_.end(), VNode{h, 0});

        if (it == ring_.end()) {
            it = ring_.begin(); // Замикання кільця (wrap-around)
        }

        return servers_[it->server_index];
    }

    [[nodiscard]] std::span<const ServerEndpoint> servers() const noexcept {
        return servers_;
    }

private:
    std::vector<ServerEndpoint> servers_;
    std::vector<VNode> ring_;
};

// Форматувальник бінарно-безпечного протоколу Redis RESP2
class RespFormatter {
public:
    static std::string format_get(std::string_view key) {
        return std::format("*2\r\n$3\r\nGET\r\n${}\r\n{}\r\n", key.size(), key);
    }

    static std::string format_set(std::string_view key, std::string_view value, uint32_t ex_seconds) {
        return std::format("*4\r\n$3\r\nSET\r\n${}\r\n{}\r\n${}\r\n{}\r\n$2\r\nEX\r\n:{}\r\n",
                           key.size(), key, value.size(), value, ex_seconds);
    }
};

} // namespace cache

int main() {
    cache::ConsistentHashRing ring;
    ring.add_server("10.0.1.10", 6379, 128);
    ring.add_server("10.0.1.11", 6379, 128);
    ring.add_server("10.0.1.12", 6379, 128);

    std::vector<std::string_view> keys = {
        "user:101:profile",
        "session:token_abc",
        "cart:items_998"
    };

    for (auto key : keys) {
        if (auto node = ring.lookup(key)) {
            std::string cmd = cache::RespFormatter::format_get(key);
            std::cout << std::format("Ключ '{}' -> Вузол {}:{}\n", key, node->host, node->port);
        }
    }

    return 0;
}
