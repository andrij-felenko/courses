#include <vector>
#include <random>
#include <algorithm>
#include <cassert>

struct ItemCpp {
    int key;
    int original_order;

    auto operator<=>(const ItemCpp& other) const {
        return key <=> other.key;
    }
};

/* Верифікація стійкості сортування */
bool verify_stability(const std::vector<ItemCpp>& data) {
    for (std::size_t i = 1; i < data.size(); ++i) {
        if (data[i].key < data[i - 1].key) {
            return false;
        }
        if (data[i].key == data[i - 1].key && data[i].original_order < data[i - 1].original_order) {
            return false;
        }
    }
    return true;
}

void run_cpp_tests() {
    std::vector<ItemCpp> items;
    items.reserve(1000);

    std::mt19937 rng(42);
    std::uniform_int_distribution<int> dist(0, 15);

    for (int i = 0; i < 1000; ++i) {
        items.push_back({dist(rng), i});
    }

    insertion_sort(std::span<ItemCpp>(items), [](const ItemCpp& a, const ItemCpp& b) {
        return a.key < b.key;
    });

    assert(verify_stability(items));
}
