#pragma once

#include <chrono>
#include <cstddef>
#include <cstdint>

namespace at {

/* Час рушія — це системний тік мікроконтролера, 32-бітний лічильник
   мілісекунд. Беззнакове віднімання обгортається саме так, як треба:
   переповнення через 49.7 доби не робить жоден таймаут ані вічним,
   ані миттєвим. */
using Millis = std::chrono::duration<std::uint32_t, std::milli>;

namespace config {

/* Ступінь двійки — обов'язково: тоді загортання індексу коштує одну
   побітову операцію І замість ділення за модулем. */
inline constexpr std::size_t kRxSize = 512;
inline constexpr std::uint16_t kRxMask = static_cast<std::uint16_t>(kRxSize - 1);
static_assert((kRxSize & (kRxSize - 1)) == 0, "kRxSize має бути ступенем двійки");
static_assert(kRxSize <= 0x8000, "індекси кільцевого буфера 16-бітові");

inline constexpr std::size_t kMaxLine = 128;
inline constexpr std::size_t kMaxCommand = 96;
inline constexpr std::size_t kMaxPrefix = 24;
inline constexpr std::size_t kQueueCapacity = 8;
inline constexpr std::size_t kMaxUrcHandlers = 8;

/* Скільки байтів замикання вміщує колбек. Динамічної пам'яті рушій не
   торкається взагалі, тож розмір мусить бути відомий наперед. */
inline constexpr std::size_t kCallbackStorage = 32;

inline constexpr Millis kRetryDelay{100};
inline constexpr char kPromptChar = '>';
inline constexpr std::uint8_t kTimeoutEscalationLimit = 3;

static_assert(kMaxCommand < kMaxLine, "луна команди мусить уміщатися в рядок");

}  // namespace config
}  // namespace at
