#include <iostream>
#include <vector>
#include <cstdint>
#include <span>

#include "xor_filter.hpp"

int main() {
    const std::vector<uint64_t> dataset = {
        0x1000ULL, 0x2000ULL, 0x3000ULL, 0x4000ULL, 0x5000ULL
    };

    auto filter_result = algorithms::XorFilter<uint8_t>::build(dataset);
    if (!filter_result.has_value()) {
        std::cerr << "Помилка конструювання Xor-фільтра\n";
        return 1;
    }

    const auto& filter = *filter_result;

    /* Перевірка збережених ключів */
    for (uint64_t key : dataset) {
        std::cout << "Ключ 0x" << std::hex << key << ": "
                  << (filter.contains(key) ? "ТАК" : "НІ") << " (очікується ТАК)\n";
    }

    /* Перевірка стороннього ключа */
    const uint64_t missing_key = 0x9999ULL;
    std::cout << "Відсутній ключ 0x" << std::hex << missing_key << ": "
              << (filter.contains(missing_key) ? "ХИБНИЙ СПАЛАХ" : "НІ (відсутній)\n");

    std::cout << std::dec << "Розмір структури в RAM: " << filter.size_in_bytes() << " байтів\n";
    return 0;
}
