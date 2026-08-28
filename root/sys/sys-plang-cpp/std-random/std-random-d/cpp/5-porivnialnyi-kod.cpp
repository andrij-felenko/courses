#include <iostream>
#include <random>

// Сучасний C++11/C++20 підхід (Беззсувний, об'єктно-орієнтований, потокобезпечний)
class DiceRoller {
public:
    DiceRoller() 
        // 1. Ініціалізація апаратною ентропією
        : rng_(rd_())
        // 2. Діапазон [1, 6] без модульного зміщення
        , dist_(1, 6) {}

    int roll() {
        return dist_(rng_);
    }

private:
    std::random_device rd_;
    std::mt19937 rng_;
    std::uniform_int_distribution<int> dist_;
};

int main() {
    DiceRoller roller;

    for (int i = 0; i < 5; ++i) {
        std::cout << "C++ Dice Roll: " << roller.roll() << "\n";
    }
    return 0;
}
