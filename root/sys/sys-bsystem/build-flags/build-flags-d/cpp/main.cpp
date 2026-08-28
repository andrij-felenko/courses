#include <cstddef>
#include <span>
#include <numeric>

long long sum_array(std::span<const int> data, int factor) {
    long long total = 0;
    for (const int value : data) {
        // Множення на незмінний factor всередині циклу
        total += static_cast<long long>(value) * factor;
    }
    return total;
}
