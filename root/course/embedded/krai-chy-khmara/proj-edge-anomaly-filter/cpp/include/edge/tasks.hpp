#pragma once

#include <cstddef>
#include <cstdint>

/*
 * Контракт плати. Ці функції реалізує BSP конкретного виробу — драйвер АЦП
 * і драйвер радіомодема. Мова зв'язування C: BSP майже завжди зібраний
 * компілятором C, і спотворене ім'я C++ до нього не долинуло б.
 */
extern "C" {

/// Блокується до готовності чергової вибірки (переривання DMA АЦП).
/// false — перетворення не завершилося у відведений час.
bool adc_read_sample(float* out, std::uint32_t timeout_ms);

void radio_wake();                                       ///< Sleep -> активний режим
void radio_sleep();                                      ///< вимкнути PA, глибокий сон
bool radio_send(const std::uint8_t* frame, std::size_t len);
bool radio_wait_ack(std::uint32_t timeout_ms);

}  // extern "C"

namespace edge {

/// Створює чергу й обидві задачі. Кличеться з main() до vTaskStartScheduler().
/// Уся пам'ять статична, тож false означає лише невідповідність конфігурації
/// FreeRTOS (немає configSUPPORT_STATIC_ALLOCATION).
bool telemetry_start();

/// Черга переповнюється, коли радіо не встигає за давачем. Втрачені звіти
/// треба бачити, а не здогадуватися про них.
[[nodiscard]] std::uint32_t dropped_reports() noexcept;
[[nodiscard]] std::uint32_t failed_transmissions() noexcept;

}  // namespace edge
