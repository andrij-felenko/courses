#pragma once

#include <cstddef>
#include <span>

// Сума елементів силами workers потоків одного процесу.
// Потоки дістають лише span — вікно в ту саму пам'ять, без копіювання.
// Кидає std::invalid_argument, якщо workers == 0.
long long sumWithThreads(std::span<const int> data, std::size_t workers);
