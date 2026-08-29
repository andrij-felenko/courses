#pragma once

#include <cstddef>
#include <string>
#include <string_view>

#include "portal/esp_result.hpp"

namespace portal::credentials {

/* SSID — до 32 октетів, пароль WPA2 — до 63 символів. */
inline constexpr std::size_t kSsidMax = 32;
inline constexpr std::size_t kPasswordMax = 63;

struct Credentials {
    std::string ssid;
    std::string password;
};

/* Чи лежить у NVS повний, доведений до кінця запис конфігурації. */
[[nodiscard]] bool isConfigured() noexcept;

/* ESP_ERR_NVS_NOT_FOUND у помилці означає «пристрій ще не налаштовано». */
[[nodiscard]] Result<Credentials> load() noexcept;

/*
 * Записує облікові дані транзакційно: спершу знімає ознаку `configured`,
 * потім кладе поля, і лише останнім кроком ставить ознаку назад.
 * Знеструмлення на будь-якому кроці лишає запис без ознаки — а такий
 * при наступному старті не буде прийнято за валідний.
 */
[[nodiscard]] Status save(std::string_view ssid, std::string_view password) noexcept;

/* Забуває конфігурацію: пристрій наступного разу підніме портал. */
[[nodiscard]] Status erase() noexcept;

}  // namespace portal::credentials
