#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <string_view>
#include <vector>

#include "esp_wifi.h"

#include "portal/esp_result.hpp"

namespace portal::wifi {

/* Адреса самої точки доступу; на неї ж указує DNS-перехоплювач. */
inline constexpr const char *kApAddress = "192.168.4.1";
inline constexpr const char *kApNetmask = "255.255.255.0";

/* Пул DHCP: .2–.10. Портал обслуговує одного користувача, решта
 * клієнтів — фонові служби його ж телефона, десяти адрес досить. */
inline constexpr const char *kDhcpPoolStart = "192.168.4.2";
inline constexpr const char *kDhcpPoolEnd = "192.168.4.10";

/* Скільки мереж максимум віддаємо веб-інтерфейсу. */
inline constexpr std::size_t kScanLimit = 16;

struct ScannedNetwork {
    std::string ssid;
    std::int8_t rssi{};
    std::uint8_t channel{};
    wifi_auth_mode_t auth{WIFI_AUTH_OPEN};

    [[nodiscard]] std::string_view authName() const noexcept;
};

/*
 * Піднімає мережевий стек: віртуальні інтерфейси AP і STA, драйвер,
 * режим AP+STA. Режим саме комбінований, бо сканувати ефір може лише
 * станційна частина радіотракту.
 */
[[nodiscard]] Status initStack() noexcept;

/*
 * Запускає точку доступу зі статичною адресою kApAddress і власним
 * налаштуванням DHCP (пул адрес + видача себе як DNS-сервера).
 * Порожній пароль — відкрита мережа.
 */
[[nodiscard]] Status startAccessPoint(std::string_view ssid,
                                      std::string_view password = {}) noexcept;

/* Підключення станційної частини до збереженої мережі. */
[[nodiscard]] Status connectStation(std::string_view ssid,
                                    std::string_view password) noexcept;

/* Синхронне сканування ефіру. */
[[nodiscard]] Result<std::vector<ScannedNetwork>> scan(
    std::size_t limit = kScanLimit) noexcept;

/* Ім'я точки доступу з хвостом апаратної адреси: ESP32-Setup-A1B2. */
[[nodiscard]] std::string accessPointName() noexcept;

/* Адреса точки доступу у мережевому порядку байтів — для DNS-відповіді. */
[[nodiscard]] std::uint32_t accessPointIp() noexcept;

}  // namespace portal::wifi
