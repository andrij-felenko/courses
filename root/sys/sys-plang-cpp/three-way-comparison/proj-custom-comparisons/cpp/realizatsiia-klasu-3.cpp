#include <iostream>
#include <vector>
#include <string>
#include <compare>
#include <algorithm>
#include <cstdint>

class ImmutableDocument {
    uint64_t                 content_hash{0};
    std::vector<std::string> lines;

    static uint64_t compute_hash(const std::vector<std::string>& lns) noexcept {
        uint64_t h = 14695981039346656037ULL; // FNV-1a offset basis
        for (const auto& line : lns) {
            for (char c : line) {
                h ^= static_cast<unsigned char>(c);
                h *= 1099511628211ULL; // FNV-1a prime
            }
        }
        return h;
    }

public:
    ImmutableDocument(std::vector<std::string> lns)
        : content_hash(compute_hash(lns)), lines(std::move(lns)) {}

    // 1. Оптимізована рівність: адреса -> хеш -> повний вміст
    bool operator==(const ImmutableDocument& other) const noexcept {
        // Рівень 1: Тотожність адреси в пам'яті (O(1))
        if (this == &other) {
            return true;
        }
        // Рівень 2: Збіг предобчисленого 64-бітного хешу (O(1))
        if (content_hash != other.content_hash) {
            return false;
        }
        // Рівень 3: Повний захист від колізій хешу (O(N))
        return lines == other.lines;
    }

    // 2. Лексикографічний порядок: винятково через вміст
    std::strong_ordering operator<=>(const ImmutableDocument& other) const noexcept {
        if (this == &other) {
            return std::strong_ordering::equal;
        }
        return std::lexicographical_compare_three_way(
            lines.begin(), lines.end(),
            other.lines.begin(), other.lines.end()
        );
    }
};
