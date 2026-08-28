#include <iostream>
#include <cstdint>

void verify_compression_pigeonhole(uint32_t n_bits) {
    if (n_bits >= 62) return;

    const uint64_t input_count = 1ULL << n_bits;        // 2^N
    const uint64_t output_count = input_count - 1;      // 2^N - 1

    std::cout << "=== Перевірка принципу Діріхле для N = " << n_bits << " бітів ===\n";
    std::cout << "Вхідний простір (2^N):    " << input_count << " файлів\n";
    std::cout << "Вихідний простір (< N):   " << output_count << " слотів\n";

    if (input_count > output_count) {
        std::cout << "ВИСНОВОК: За принципом Діріхле (n > k), універсальне стиснення\n"
                  << "без втрат математично НЕДОСЯЖНЕ. Спроба стиснути всі "
                  << input_count << " файлів створить принаймні 1 колізію.\n";
    }
}

int main() {
    verify_compression_pigeonhole(4);
    std::cout << "\n";
    verify_compression_pigeonhole(16);
    return 0;
}
