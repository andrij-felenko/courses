#include <array>
#include <algorithm>

constexpr auto generate_sorted_table() {
    std::array<int, 6> arr = {5, 2, 8, 1, 9, 3};
    std::sort(arr.begin(), arr.end());
    return arr;
}

// Таблиця обчислюється і сортується повністю на етапі компіляції!
constexpr auto sorted_data = generate_sorted_table();
static_assert(sorted_data[0] == 1);
static_assert(sorted_data[5] == 9);
