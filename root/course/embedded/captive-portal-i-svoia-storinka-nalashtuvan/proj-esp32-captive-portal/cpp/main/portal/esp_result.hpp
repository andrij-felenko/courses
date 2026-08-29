#pragma once

#include <expected>
#include <utility>

#include "esp_err.h"

namespace portal {

/*
 * Замість пари «код повернення + вихідний параметр» тут скрізь ходить
 * std::expected: значення та помилка мешкають в одному об'єкті, і
 * прочитати значення, не перевіривши помилки, компілятор не дасть.
 */
template <typename T>
using Result = std::expected<T, esp_err_t>;

/* Операція без результату — лише успіх або код помилки. */
using Status = std::expected<void, esp_err_t>;

/* Перекладає код ESP-IDF у Status. */
[[nodiscard]] inline Status check(esp_err_t err) noexcept
{
    if (err == ESP_OK) {
        return {};
    }
    return std::unexpected(err);
}

/*
 * Пропускає помилку далі, міняючи тип очікуваного значення.
 * Знадобиться там, де Status із глибини треба віддати як Result<T>.
 */
template <typename T, typename E>
[[nodiscard]] inline auto forwardError(const std::expected<T, E> &source) noexcept
{
    return std::unexpected(source.error());
}

}  // namespace portal
