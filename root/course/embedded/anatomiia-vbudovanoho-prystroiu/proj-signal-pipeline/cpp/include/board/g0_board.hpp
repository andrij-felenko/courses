#pragma once

#include <cstdint>
#include <expected>

/// Апаратний шар для STM32G071 (Cortex-M0+, 48 МГц):
/// TIM2 задає період квантування й сам запускає АЦП, DMA кладе результат
/// у пам'ять і піднімає переривання, TIM3_CH1 віддає ШІМ.
namespace board {

inline constexpr std::uint32_t kSamplePeriodHz = 100; ///< 10 мс — той самий dt, що в коефіцієнтах

enum class Error : std::uint8_t {
    PllTimeout,
    AdcCalibrationTimeout,
    AdcNotReady,
};

/// Помилку налаштування нема кому повернути кодом і нема кому кинути винятком
/// (прошивка збирається без винятків), тож результат — std::expected.
[[nodiscard]] std::expected<void, Error> init() noexcept;

/// Запис у регістр порівняння TIM3->CCR1 із попереднім завантаженням:
/// нове значення береться цілком на наступному оновленні таймера.
void set_duty(std::uint16_t duty) noexcept;

/// Аварійне зупинення: навантаження знеструмлено, переривання вимкнено.
[[noreturn]] void panic(Error error) noexcept;

/// Гачок застосунку: викликається з переривання завершення передачі DMA,
/// рівно раз на період квантування. Визначає його main.cpp.
void on_sample(std::uint16_t raw_code) noexcept;

} // namespace board
