#include <vector>
#include <span>
#include <array>
#include <cstdint>
#include <algorithm>

void radix_sort_edges(std::span<Edge> edges) {
    const size_t n = edges.size();
    if (n <= 1) return;

    std::vector<Edge> temp(n);

    for (int shift = 0; shift < 32; shift += 8) {
        std::array<size_t, 256> count{};

        for (const auto& edge : edges) {
            auto byte = static_cast<uint8_t>((edge.weight >> shift) & 0xFF);
            ++count[byte];
        }

        size_t total = 0;
        for (auto& cnt : count) {
            size_t old = cnt;
            cnt = total;
            total += old;
        }

        for (const auto& edge : edges) {
            auto byte = static_cast<uint8_t>((edge.weight >> shift) & 0xFF);
            temp[count[byte]++] = edge;
        }

        std::ranges::copy(temp, edges.begin());
    }
}
