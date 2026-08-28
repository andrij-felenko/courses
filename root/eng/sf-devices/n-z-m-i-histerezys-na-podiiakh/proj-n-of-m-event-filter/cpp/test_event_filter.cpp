/**
 * @file test_event_filter.cpp
 * @brief Верифікаційний стенд на C++20
 */

#include <iostream>
#include <random>
#include <cassert>
#include "event_filter_modern.hpp"

using namespace embedded::filter;

int main() {
    std::cout << "=== C++20 Тестовий стенд фільтра подій N-з-M ===\n";

    // Створення екземпляра фільтра 12 з 16 з порогом залипання 500 тактів
    ModernEventFilter<16, 12, 4, 500> filter(false);

    std::mt19937 rng(1337);
    std::bernoulli_distribution noise(0.05); // 5% шум

    // 1. Тест спокою
    for (int i = 0; i < 1000; ++i) {
        bool sample = noise(rng);
        bool state = filter.Update(sample);
        assert(!state && "Помилка: хибне спрацьовування в тиші!");
    }

    // 2. Тест появи сигналу
    for (int i = 0; i < 16; ++i) {
        filter.Update(true);
    }
    assert(filter.GetState() && "Помилка: фільтр не активувався!");

    // 3. Тест діагностики залипання
    for (int i = 0; i < 600; ++i) {
        filter.Update(true);
    }
    assert(filter.IsStuck() && "Помилка: залипання не виявлено!");

    std::cout << "Усі тести на C++20 виконано без помилок.\n";
    return 0;
}
