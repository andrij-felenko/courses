#include "sram_puf_analyzer.hpp"
#include <iostream>
#include <array>
#include <random>

int main() {
    std::cout << "--- C++20 Analizator SRAM PUF (std::span & std::bitset) ---\n";

    puf::SramPufAnalyzer analyzer;

    std::array<std::uint8_t, puf::SramPufAnalyzer::BlockSize> base_sample;
    base_sample.fill(0xAA); /* Початковий базовий паттерн */

    std::mt19937 rng(42);
    std::uniform_int_distribution<int> dist(0, 500);

    /* Збір 10 вибірок із невеликим додатковим шумом */
    for (int cycle = 0; cycle < 10; ++cycle) {
        auto sample = base_sample;
        int noise_bit = dist(rng) % puf::SramPufAnalyzer::TotalBits;
        sample[noise_bit / 8] ^= (1 << (noise_bit % 8));

        analyzer.add_sample(sample);
    }

    auto stable_mask = analyzer.generate_stable_mask();
    double ber = analyzer.calculate_average_intra_ber();

    std::cout << "[Аналіз C++] Кількість стабільних бітів: " << stable_mask.count()
              << " з " << puf::SramPufAnalyzer::TotalBits << "\n";
    std::cout << "[Аналіз C++] Середній рівень бітових помилок (Intra-BER): " << ber << "%\n";

    return 0;
}
