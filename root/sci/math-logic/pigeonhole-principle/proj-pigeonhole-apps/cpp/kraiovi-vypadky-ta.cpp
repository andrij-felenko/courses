#include <iostream>
#include <vector>
#include <optional>
#include <span >

struct SubarrayRange {
    size_t start_index; // Включно (0-indexed)
    size_t end_index;   // Включно (0-indexed)
    long long sum;      // Сума підмасиву
};

std::optional<SubarrayRange> find_zero_sum_mod_n(std::span<const int> arr) {
    const size_t n = arr.size();
    if (n == 0) return std::nullopt;

    // Масив для збереження індексу префіксу (-1 означає "остача ще не зустрічалася")
    std::vector<int> first_seen_prefix(n, -1);
    first_seen_prefix[0] = 0; // S₀ = 0 дає остачу 0 на префіксі довжини 0

    long long current_prefix_sum = 0;
    for (size_t j = 1; j <= n; ++j) {
        current_prefix_sum += arr[j - 1];

        // Математичний модуль для довільних від'ємних і додатних сум
        long long mod_raw = current_prefix_sum % static_cast<long long>(n);
        size_t rem = static_cast<size_t>((mod_raw + static_cast<long long>(n)) % static_cast<long long>(n));

        if (first_seen_prefix[rem] != -1) {
            size_t i = static_cast<size_t>(first_seen_prefix[rem]);
            return SubarrayRange{
                .start_index = i,
                .end_index = j - 1,
                .sum = current_prefix_sum
            };
        }

        first_seen_prefix[rem] = static_cast<int>(j);
    }

    return std::nullopt;
}

int main() {
    const std::vector<int> data = { 4, -7, 2, 9, -5 };

    if (auto res = find_zero_sum_mod_n(data)) {
        std::cout << "Знайдено підмасив [індекси " << res->start_index 
                  << ".." << res->end_index << "]: ";
        long long sum = 0;
        for (size_t k = res->start_index; k <= res->end_index; ++k) {
            std::cout << data[k] << " ";
            sum += data[k];
        }
        std::cout << "\nСума = " << sum << " (кратно " << data.size() << ")\n";
    }
    return 0;
}
