/* silicon.hpp — ревізія кристала й матриця застосовності еррати.
 *
 * Errata Sheet — це таблиця «дефект × ревізія». Щоб обхід не коштував тактів
 * там, де дефекту вже немає, таблицю переносять у код і звіряють із власним
 * REV_ID, прочитаним з DBGMCU_IDCODE.
 */
#pragma once

#include <cstdint>
#include <expected>
#include <string_view>

namespace hw::silicon {

/* DEV_ID сімейства STM32F405/407/415/417 (RM0090 §38.6.1). */
inline constexpr std::uint16_t expected_dev_id = 0x413U;

enum class Revision : std::uint8_t {
    unknown = 0,
    rev_a,
    rev_z,
    rev_1,
    rev_2,
    rev_y,
    rev_3,
};

enum class Erratum : std::uint8_t {
    /* ES0182: перше звернення до щойно затактованого блоку може не пройти. */
    rcc_clock_enable_delay,
    /* ES0182: аналоговий фільтр I2C зависає з піднятим прапорцем BUSY. */
    i2c_busy_lock,
};

struct Device {
    std::uint16_t dev_id{};
    std::uint16_t rev_id{};
    Revision      revision{Revision::unknown};
};

enum class IdError {
    foreign_device,   // DEV_ID не наш — карта регістрів вказує в порожнечу
};

/* Читає IDCODE й розбирає його. Помилка тут не виняток, а очікуваний
 * результат: та сама прошивка може приїхати на плату з іншим чипом. */
[[nodiscard]] std::expected<Device, IdError> identify() noexcept;

/* Той самий результат, прочитаний один раз і закешований. */
[[nodiscard]] const Device& device() noexcept;

/* Головне питання до еррати. Нерозпізнаний кремній вважаємо ураженим:
 * зайвий обхід коштує тактів, пропущений — зупинки пристрою в полі. */
[[nodiscard]] bool affected(Erratum erratum) noexcept;

[[nodiscard]] std::string_view name(Revision revision) noexcept;

/* Заголовок дефекту — щоб у журналі стояла не цифра, а рядок, який можна
 * знайти пошуком у самому документі еррати. */
[[nodiscard]] std::string_view title(Erratum erratum) noexcept;

} // namespace hw::silicon
