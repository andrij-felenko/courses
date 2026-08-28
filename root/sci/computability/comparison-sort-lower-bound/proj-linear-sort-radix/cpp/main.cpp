#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdint>
#include <chrono>

// 1. Сортування підрахунком для невід'ємних цілих чисел
void counting_sort(std::vector<int>& arr) {
    if (arr.empty()) return;

    int max_val = *std::max_element(arr.begin(), arr.end());
    std::vector<int> count(max_val + 1, 0);
    std::vector<int> output(arr.size());

    // Підрахунок частот
    for (int x : arr) {
        count[x]++;
    }

    // Префіксні суми
    for (int i = 1; i <= max_val; ++i) {
        count[i] += count[i - 1];
    }

    // Запис у вихідний масив із кінця (для стабільності)
    for (int i = static_cast<int>(arr.size()) - 1; i >= 0; --i) {
        output[count[arr[i]] - 1] = arr[i];
        count[arr[i]]--;
    }

    arr = std::move(output);
}

// 2. Порозрядне сортування (LSD Radix Sort) для 32-бітних unsigned int
void radix_sort_u32(std::vector<uint32_t>& arr) {
    if (arr.size() <= 1) return;

    const size_t n = arr.size();
    std::vector<uint32_t> temp(n);

    // 4 проходи по 8 бітів (байт за байтом)
    for (int shift = 0; shift < 32; shift += 8) {
        uint32_t count[256] = {0};

        // Підрахунок частот поточного байта
        for (size_t i = 0; i < n; ++i) {
            uint8_t byte_val = (arr[i] >> shift) & 0xFF;
            count[byte_val]++;
        }

        // Префіксні суми
        uint32_t total = 0;
        for (int i = 0; i < 256; ++i) {
            uint32_t old_c = count[i];
            count[i] = total;
            total += old_c;
        }

        // Розподіл елементів по кошиках
        for (size_t i = 0; i < n; ++i) {
            uint8_t byte_val = (arr[i] >> shift) & 0xFF;
            temp[count[byte_val]++] = arr[i];
        }

        arr.swap(temp);
    }
}

int main() {
    std::vector<uint32_t> data = {0x00A1F012, 0x00000005, 0x12345678, 0x00A1E000, 0x00000001};
    
    std::cout << "Перед сортуванням:\n";
    for (auto x : data) std::cout << std::hex << "0x" << x << " ";
    std::cout << "\n\n";

    radix_sort_u32(data);

    std::cout << "Після Radix Sort (O(N)):\n";
    for (auto x : data) std::cout << std::hex << "0x" << x << " ";
    std::cout << std::dec << "\n";

    return 0;
}
