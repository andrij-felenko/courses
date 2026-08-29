#pragma once

#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

// Контракт нижнього рівня: усе, чого тестовий рушій вимагає від плати-виробу
// й від стенда. Реалізація — у BSP конкретного виробу. Те, що може не
// відповісти, повертає std::optional: «не знаю» тут окремий стан, а не -1.

namespace hal {

// --- Час, затримки, сторожовий таймер ---------------------------------------

// Читається прямо з регістра апаратного таймера (крок 100 мкс), а не з
// лічильника переривань: під час March C- переривання замасковані.
std::uint32_t time_us() noexcept;
void delay_us(std::uint32_t us) noexcept;
void watchdog_kick() noexcept;

std::uint32_t irq_disable() noexcept;                 // повертає старий PRIMASK
void irq_restore(std::uint32_t primask) noexcept;

// --- АЦП --------------------------------------------------------------------

enum class AdcChannel : std::uint8_t {
    Vrefint = 0,   // внутрішнє джерело опорної напруги
    Vcore = 1      // V_CORE через дільник 1:2 на технологічному купоні
};

std::optional<std::uint16_t> adc_read(AdcChannel ch, std::uint32_t timeout_us) noexcept;
std::uint16_t vrefint_cal() noexcept;   // фабричне значення, зняте при 3.000 В

// --- Тактування -------------------------------------------------------------

void pll_start() noexcept;
bool pll_locked() noexcept;
// Частота HSE проти опорного 32768 Гц; nullopt — кварц не збудився.
std::optional<std::uint32_t> measure_hse_hz(std::uint32_t gate_ms) noexcept;

// --- I2C --------------------------------------------------------------------

void i2c_pins_to_gpio() noexcept;
void i2c_pins_to_peripheral() noexcept;
void i2c_scl_write(bool level) noexcept;
void i2c_sda_write(bool level) noexcept;
bool i2c_sda_read() noexcept;
void i2c_reinit() noexcept;
std::optional<std::uint8_t> i2c_read_reg(std::uint8_t addr7, std::uint8_t reg,
                                         std::uint32_t timeout_us) noexcept;

// --- SPI --------------------------------------------------------------------

void spi_cs(bool active) noexcept;
bool spi_xfer(std::span<const std::uint8_t> tx, std::span<std::uint8_t> rx,
              std::uint32_t timeout_us) noexcept;

// --- Радіотракт -------------------------------------------------------------

inline constexpr std::uint8_t kXoTrimMax = 63;

bool radio_init() noexcept;
bool radio_cw_start(std::uint32_t freq_khz, std::int16_t power_ddbm) noexcept;
void radio_cw_stop() noexcept;
std::uint8_t radio_xo_trim() noexcept;
void radio_xo_trim_set(std::uint8_t trim) noexcept;

// --- OTP / eFuse ------------------------------------------------------------

inline constexpr std::uint8_t kOtpWordXoTrim = 4;

std::optional<std::uint32_t> otp_read(std::uint8_t word_index) noexcept;
// Пропалювання перемички: імпульс до 200 мА. Напругу сторожує тестер.
bool otp_write(std::uint8_t word_index, std::uint32_t value) noexcept;

// --- Канал до стенда --------------------------------------------------------

struct StandPowerLog {
    std::uint16_t inrush_peak_ma;
    std::uint16_t inrush_duration_us;
    std::uint16_t iq_ua;
};

struct RfMeasurement {
    std::int16_t power_ddbm;     // десяті частки dBm
    std::int32_t freq_error_hz;  // відхилення піку від замовленої частоти
};

std::optional<StandPowerLog> stand_power_log(std::uint32_t timeout_us) noexcept;
std::optional<RfMeasurement> stand_measure_rf(std::uint32_t freq_khz,
                                              std::uint32_t timeout_us) noexcept;

void uart_write(std::span<const char> data) noexcept;
void result_indicate(bool pass) noexcept;
void board_init() noexcept;

}  // namespace hal
