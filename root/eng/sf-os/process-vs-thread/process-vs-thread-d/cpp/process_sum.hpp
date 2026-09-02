#pragma once

#include <cstddef>
#include <expected>
#include <span>
#include <system_error>

// Сума елементів силами workers окремих процесів: кожна дитина дістає масив
// копією-при-записі й повертає часткову суму через канал.
// Помилку віддає значенням, а не через errno.
std::expected<long long, std::error_code> sumWithProcesses(std::span<const int> data,
                                                           std::size_t workers);
