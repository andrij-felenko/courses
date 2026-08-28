#include <iostream>
#include <memory>
#include <optional>
#include <array>
#include <cstdint>
#include <string_view>

struct RouteEntry {
    uint32_t next_hop{0};
    uint32_t prefix_len{0};
};

class RadixTrie {
public:
    RadixTrie() = default;

    /* Додавання префікса в дерево пересилання */
    void insert(uint32_t network_ip, uint32_t prefix_len, uint32_t next_hop) {
        if (prefix_len > 32) return;

        Node* curr = &root_;
        for (uint32_t i = 0; i < prefix_len; ++i) {
            const uint32_t bit = get_bit(network_ip, i);
            if (!curr->children[bit]) {
                curr->children[bit] = std::make_unique<Node>();
            }
            curr = curr->children[bit].get();
        }

        curr->route = RouteEntry{next_hop, prefix_len};
    }

    /* Пошук за алгоритмом Longest Prefix Match */
    [[nodiscard]] std::optional<RouteEntry> lookup(uint32_t target_ip) const noexcept {
        const Node* curr = &root_;
        const RouteEntry* best_match = curr->route ? &curr->route.value() : nullptr;

        for (uint32_t i = 0; i < 32; ++i) {
            const uint32_t bit = get_bit(target_ip, i);
            if (!curr->children[bit]) {
                break;
            }
            curr = curr->children[bit].get();
            if (curr->route) {
                best_match = &curr->route.value();
            }
        }

        if (best_match) {
            return *best_match;
        }
        return std::nullopt;
    }

    /* Видалення маршруту з підрізанням */
    void remove(uint32_t network_ip, uint32_t prefix_len) {
        if (prefix_len <= 32) {
            remove_helper(&root_, network_ip, prefix_len, 0);
        }
    }

    /* Допоміжне перетворення октетів у 32-бітне число */
    static constexpr uint32_t make_ip(uint8_t a, uint8_t b, uint8_t c, uint8_t d) noexcept {
        return (static_cast<uint32_t>(a) << 24) |
               (static_cast<uint32_t>(b) << 16) |
               (static_cast<uint32_t>(c) << 8)  |
                static_cast<uint32_t>(d);
    }

private:
    struct Node {
        std::array<std::unique_ptr<Node>, 2> children{};
        std::optional<RouteEntry> route{std::nullopt};
    };

    Node root_{};

    static constexpr uint32_t get_bit(uint32_t ip, uint32_t bit_index) noexcept {
        return (ip >> (31 - bit_index)) & 1U;
    }

    bool remove_helper(Node* node, uint32_t ip, uint32_t prefix_len, uint32_t depth) {
        if (!node) return false;

        if (depth == prefix_len) {
            node->route = std::nullopt;
            return (!node->children[0] && !node->children[1]);
        }

        const uint32_t bit = get_bit(ip, depth);
        if (node->children[bit] && remove_helper(node->children[bit].get(), ip, prefix_len, depth + 1)) {
            node->children[bit].reset();
            return (!node->route && !node->children[0] && !node->children[1]);
        }
        return false;
    }
};

int main() {
    RadixTrie fib;

    /* Заповнюємо таблицю пересилання */
    fib.insert(RadixTrie::make_ip(0, 0, 0, 0), 0, RadixTrie::make_ip(192, 0, 2, 1));
    fib.insert(RadixTrie::make_ip(198, 51, 0, 0), 16, RadixTrie::make_ip(10, 0, 0, 1));
    fib.insert(RadixTrie::make_ip(198, 51, 100, 0), 22, RadixTrie::make_ip(10, 0, 1, 1));
    fib.insert(RadixTrie::make_ip(198, 51, 100, 32), 27, RadixTrie::make_ip(10, 0, 2, 1));

    /* Виконуємо пошук для IP-адреси 198.51.100.45 */
    const uint32_t dst_ip = RadixTrie::make_ip(198, 51, 100, 45);
    const auto result = fib.lookup(dst_ip);

    if (result) {
        const uint32_t nh = result->next_hop;
        std::cout << "Знайдено маршрут LPM: префікс /" << result->prefix_len
                  << ", Next-Hop: "
                  << ((nh >> 24) & 0xFF) << "."
                  << ((nh >> 16) & 0xFF) << "."
                  << ((nh >> 8) & 0xFF)  << "."
                  << (nh & 0xFF) << "\n";
    } else {
        std::cout << "Маршрут не знайдено: пакет скинуто\n";
    }

    fib.remove(RadixTrie::make_ip(198, 51, 100, 32), 27);
    return 0;
}
