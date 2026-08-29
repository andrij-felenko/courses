// Плата стенда: STM32F411 на HSI 16 МГц.
//
//   PA5 — затвор MOSFET світлодіода збудження;
//   PA0 — вихід компаратора фотоприймача, вхід EXTI0 по фронту наростання;
//   PA2 — USART2_TX, 115200 8N1.
//
// Часова база — TIM2, 32 біти, ціна поділки рівно 1 мкс. Тип часу тут
// std::chrono::duration, а не «голий» uint32_t: інтервал і мітку часу
// переплутати неможливо навіть випадково.
#pragma once

#include <chrono>
#include <cstdint>
#include <string_view>

namespace board {

using Microseconds = std::chrono::duration<std::uint32_t, std::micro>;

void init() noexcept;

// Показ часової бази. Різниці беззнакові, тому перехід лічильника через нуль
// (раз на 71.6 хвилини) не ламає жодного виміру.
[[nodiscard]] Microseconds now() noexcept;

void wait(Microseconds duration) noexcept;

// Спалах живе рівно стільки, скільки живе об'єкт. Хоч би як вийшли з області
// видимості — по таймауту, по відгуку, по винятку — світлодіод буде погашено.
class LedFlash {
public:
    LedFlash() noexcept;
    ~LedFlash() noexcept;
    LedFlash(const LedFlash &) = delete;
    LedFlash &operator=(const LedFlash &) = delete;
};

// Вікно чутливості фотоприймача. Поза вікном переривання замасковане: інакше
// пульсації ламп на 100 Гц сипали б хибні спрацювання між випробуваннями.
class OpticalWindow {
public:
    OpticalWindow() noexcept;
    ~OpticalWindow() noexcept;
    OpticalWindow(const OpticalWindow &) = delete;
    OpticalWindow &operator=(const OpticalWindow &) = delete;

    void close() noexcept; // ідемпотентно; кличеться і з обробника переривання

private:
    bool open_{true};
};

// Скидання прапорця EXTI — єдине, що обробник робить із контролером переривань.
void clear_optical_flag() noexcept;

void print(std::string_view text) noexcept;
void print(std::uint32_t value) noexcept;
// Друкує тривалість як мілісекунди з трьома знаками: 16340 мкс -> "16.340".
void print(Microseconds value) noexcept;

[[noreturn]] void halt() noexcept;

} // namespace board
