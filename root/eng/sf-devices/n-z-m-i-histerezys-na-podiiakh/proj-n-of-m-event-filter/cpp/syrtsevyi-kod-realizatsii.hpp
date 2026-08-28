/**
 * @file event_filter_impl.cpp
 * @brief C++20 реалізація допоміжних функцій
 */

#include "event_filter.hpp"
#include <bit>

namespace embedded::c_api {

// Перевірка коректності бітових операцій компілятором C++
static_assert(std::popcount(0xFFFFFFFFU) == 32);
static_assert(std::popcount(0x00000000U) == 0);
static_assert(std::popcount(0xAAAAAAAAU) == 16);

} // namespace embedded::c_api
