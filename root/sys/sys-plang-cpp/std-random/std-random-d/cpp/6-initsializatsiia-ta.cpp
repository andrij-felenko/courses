#include <random>
#include <array>
#include <iostream>

std::mt19937 create_robust_engine() {
    std::random_device rd;

    // Збираємо 8 32-бітних слів апаратної ентропії (256 бітів)
    std::array<std::uint32_t, 8> seeds;
    for (auto& s : seeds) {
        s = rd();
    }

    // seed_seq розширює 256 бітів ентропії на всі 624 елементи стану MT19937
    std::seed_seq seq(seeds.begin(), seeds.end());
    return std::mt19937(seq);
}

int main() {
    std::mt19937 rng = create_robust_engine();
    std::cout << "Якісно ініціалізоване число: " << rng() << "\n";
    return 0;
}
