# ⚙️ Практичний модуль профілювання: DWT-таймінг та GPIO-стробування на C і C++

Точний вимір тривалості виконання критичних ділянок коду та функцій фільтрації у тактах процесора без підключення зовнішнього відлагоджувача вимагає автономного програмного інструменту, що напряму взаємодіє з апаратним лічильником DWT ядра ARM Cortex-M і віднімає накладні витрати на власні виклики. Цей модуль надає готовий інструментарій для вимірювання часу виконання функцій у тактах і наносекундах, статистичного аналізу розкиду значень (мінімум, максимум, середнє) та швидкого апаратного стробування виводів GPIO для спостереження затримки на цифровому осцилографі.

## Архітектура та принцип роботи апаратного лічильника

Лічильник `DWT->CYCCNT` (англ. *Data Watchpoint and Trace Cycle Count*) — це 32-бітний монотонно зростаючий регістр у просторі пам'яті налагодження процесорів ARM Cortex-M3/M4/M7/M33 (базова адреса блоку DWT `0xE0001000`). Він інкрементується на кожному такті системної частоти процесорного ядра `HCLK`. Наприклад, для мікроконтролера STM32F7 на частоті 216 МГц період одного кроку лічильника становить `1 / (216 · 10^6) ≈ 4.6296 нс`.

Робота модуля профілювання спирається на три фундаментальні апаратні властивості:

1. **Апаратне розблокування трасування (CoreDebug):** Доступ до блоку DWT заблоковано за замовчуванням після скидання процесора для мінімізації паразитного енергоспоживання. Для активації лічильника необхідно спочатку виставити біт `TRCENA` (біт 24) у регістрі контролю відлагодження `CoreDebug->DEMCR`, після чого записати одиницю в біт `CYCCNTENA` (біт 0) у регістрі керування `DWT->CTRL`.
2. **Калібрування та компенсація витрат (Overhead Compensation):** Процес зчитування лічильника, збереження числа у локальний регістр процесора та виклик завершального читання вимагає від 2 до 8 тактів виконання інструкцій конвеєра. Модуль під час ініціалізації виконує серію калібрувальних «холостих» вимірювань і фіксує базове зміщення `s_overhead`. При кожному обчисленні тривалості це калібрувальне значення автоматично віднімається від різниці показів лічильника.
3. **Безпечна арифметика переповнення (Modulo-2³² Subtraction):** Оскільки регістр 32-бітний беззнаковий (`uint32_t`), операція віднімання `(end_cycles - start_cycles)` у беззнаковій арифметиці мов C і C++ повертає абсолютно коректну кількість тактів навіть тоді, коли лічильник переповнився (перейшов через максимальне значення `0xFFFFFFFF` у нуль) під час виконання вимірюваного блоку. Єдина фізична межа — тривалість одного вимірювання не повинна перевищувати період повного оберту лічильника. На частоті ядра 168 МГц лічильник переповнюється кожні 25.56 секунди, а на 216 МГц — кожні 19.88 секунди, що перекриває будь-які практичні потреби профілювання коротких функцій.

## Програмна реалізація для вбудованих систем

Нижче наведено модульну реалізацію profiler на чистому C (призначену для C99-прошивок, драйверів і модулів ядра) та об'єктно-орієнтовану реалізацію на сучасному C++20 із застосуванням RAII-обгорток (англ. *Resource Acquisition Is Initialization*), що гарантує коректне завершення вимірювання та збір статистики навіть за наявності ранніх виходів `return` чи виключень.

:::tabs
```c
/* dwt_profiler.h — Модуль апаратного профілювання на C */
#ifndef DWT_PROFILER_H
#define DWT_PROFILER_H

#include <stdint.h>
#include <stdbool.h>

#if defined(STM32F407xx) || defined(STM32F746xx) || defined(STM32H743xx)
  #include "stm32f4xx.h" /* CMSIS-заголовок вашого чипа */
#else
  /* Базові адреси CoreDebug та DWT за стандартом ARM Cortex-M3/M4/M7 */
  #define CORE_DEBUG_DEMCR  (*(volatile uint32_t *)0xE000EDFCU)
  #define DWT_CTRL          (*(volatile uint32_t *)0xE0001000U)
  #define DWT_CYCCNT        (*(volatile uint32_t *)0xE0001004U)
  #define DEMCR_TRCENA_BIT  (1UL << 24)
  #define DWT_CYCCNTENA_BIT (1UL << 0)
#endif

typedef struct {
    uint32_t min_cycles;
    uint32_t max_cycles;
    uint64_t total_cycles;
    uint32_t samples_count;
} profiler_stats_t;

/**
 * @brief Ініціалізація DWT лічильника та калібрування накладних витрат.
 * @return true, якщо апаратний лічильник успішно запущено.
 */
bool dwt_profiler_init(void);

/**
 * @brief Отримання поточного значення лічильника тактів.
 */
static inline uint32_t dwt_get_cycles(void) {
#if defined(DWT)
    return DWT->CYCCNT;
#else
    return DWT_CYCCNT;
#endif
}

/**
 * @brief Розрахунок витрачених тактів із вирахуванням накладних витрат.
 */
uint32_t dwt_elapsed_cycles(uint32_t start_cycles);

/**
 * @brief Перерахунок тактів у наносекунди за поточною частотою ядра CPU.
 */
uint64_t dwt_cycles_to_ns(uint32_t cycles, uint32_t cpu_freq_hz);

/**
 * @brief Оновлення структури статистики новим заміром.
 */
void profiler_stats_update(profiler_stats_t *stats, uint32_t cycles);

/**
 * @brief Скидання накопиченої статистики.
 */
void profiler_stats_reset(profiler_stats_t *stats);

#endif /* DWT_PROFILER_H */
```
```cpp
// dwt_profiler.hpp — Модуль апаратного профілювання на C++20
#pragma once

#include <cstdint>
#include <concepts>
#include <algorithm>
#include <limits>

namespace embedded::profiler {

#if defined(STM32F407xx) || defined(STM32F746xx) || defined(STM32H743xx)
  #include "stm32f4xx.h"
#else
  inline volatile uint32_t& core_debug_demcr = *reinterpret_cast<volatile uint32_t*>(0xE000EDFCU);
  inline volatile uint32_t& dwt_ctrl         = *reinterpret_cast<volatile uint32_t*>(0xE0001000U);
  inline volatile uint32_t& dwt_cyccnt       = *reinterpret_cast<volatile uint32_t*>(0xE0001004U);
  constexpr uint32_t demcr_trcena_bit  = (1UL << 24);
  constexpr uint32_t dwt_cyccntena_bit = (1UL << 0);
#endif

struct ExecutionStats {
    uint32_t min_cycles{std::numeric_limits<uint32_t>::max()};
    uint32_t max_cycles{0};
    uint64_t total_cycles{0};
    uint32_t samples_count{0};

    constexpr void update(uint32_t cycles) noexcept {
        min_cycles = std::min(min_cycles, cycles);
        max_cycles = std::max(max_cycles, cycles);
        total_cycles += cycles;
        ++samples_count;
    }

    [[nodiscard]] constexpr uint32_t average_cycles() const noexcept {
        return (samples_count > 0) ? static_cast<uint32_t>(total_cycles / samples_count) : 0;
    }

    constexpr void reset() noexcept {
        min_cycles = std::numeric_limits<uint32_t>::max();
        max_cycles = 0;
        total_cycles = 0;
        samples_count = 0;
    }
};

class DwtProfiler {
public:
    static bool init() noexcept {
#if defined(CoreDebug) && defined(DWT)
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
        DWT->CYCCNT = 0;
#else
        core_debug_demcr |= demcr_trcena_bit;
        dwt_ctrl |= dwt_cyccntena_bit;
        dwt_cyccnt = 0;
#endif
        calibrate();
        return is_running();
    }

    [[nodiscard]] static inline uint32_t get_cycles() noexcept {
#if defined(DWT)
        return DWT->CYCCNT;
#else
        return dwt_cyccnt;
#endif
    }

    [[nodiscard]] static uint32_t elapsed_cycles(uint32_t start_cycles) noexcept {
        const uint32_t now = get_cycles();
        const uint32_t raw_delta = now - start_cycles;
        return (raw_delta > s_overhead) ? (raw_delta - s_overhead) : 0;
    }

    [[nodiscard]] static constexpr uint64_t to_nanoseconds(uint32_t cycles, uint32_t cpu_freq_hz) noexcept {
        if (cpu_freq_hz == 0) return 0;
        return (static_cast<uint64_t>(cycles) * 1'000'000'000ULL) / cpu_freq_hz;
    }

    [[nodiscard]] static uint32_t get_overhead() noexcept {
        return s_overhead;
    }

private:
    static inline uint32_t s_overhead{0};

    static bool is_running() noexcept {
#if defined(DWT)
        return (DWT->CTRL & DWT_CTRL_CYCCNTENA_Msk) != 0;
#else
        return (dwt_ctrl & dwt_cyccntena_bit) != 0;
#endif
    }

    static void calibrate() noexcept {
        s_overhead = 0;
        uint32_t accumulated = 0;
        constexpr uint32_t iterations = 16;

        for (uint32_t i = 0; i < iterations; ++i) {
            __asm__ volatile("" ::: "memory"); // Бар'єр компілятора
            const uint32_t t0 = get_cycles();
            __asm__ volatile("" ::: "memory");
            const uint32_t t1 = get_cycles();
            accumulated += (t1 - t0);
        }
        s_overhead = accumulated / iterations;
    }
};

/**
 * @brief RAII-обгортка для автоматичного вимірювання тривалості блоку коду.
 */
class [[nodiscard]] ScopedTimer {
public:
    explicit ScopedTimer(ExecutionStats& stats) noexcept
        : m_stats(stats), m_start_cycles(DwtProfiler::get_cycles()) {}

    ~ScopedTimer() noexcept {
        const uint32_t elapsed = DwtProfiler::elapsed_cycles(m_start_cycles);
        m_stats.update(elapsed);
    }

    ScopedTimer(const ScopedTimer&) = delete;
    ScopedTimer& operator=(const ScopedTimer&) = delete;
    ScopedTimer(ScopedTimer&&) = delete;
    ScopedTimer& operator=(ScopedTimer&&) = delete;

private:
    ExecutionStats& m_stats;
    const uint32_t m_start_cycles;
};

} // namespace embedded::profiler
```
:::

## Реалізація функцій обчислення (C-файл)

Для C-модуля логіка калібрування та розрахунку наносекунд оформлюється в окремому `.c`-файлі:

:::tabs
```c
/* dwt_profiler.c — Реалізація функцій профілювання */
#include "dwt_profiler.h"

static uint32_t s_dwt_overhead = 0;

static void dwt_calibrate_overhead(void) {
    s_dwt_overhead = 0;
    uint32_t total = 0;
    const uint32_t runs = 16;

    for (uint32_t i = 0; i < runs; ++i) {
        __asm__ volatile("" ::: "memory");
        uint32_t t0 = dwt_get_cycles();
        __asm__ volatile("" ::: "memory");
        uint32_t t1 = dwt_get_cycles();
        total += (t1 - t0);
    }
    s_dwt_overhead = total / runs;
}

bool dwt_profiler_init(void) {
#if defined(CoreDebug) && defined(DWT)
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    DWT->CYCCNT = 0;
    dwt_calibrate_overhead();
    return (DWT->CTRL & DWT_CTRL_CYCCNTENA_Msk) != 0;
#else
    CORE_DEBUG_DEMCR |= DEMCR_TRCENA_BIT;
    DWT_CTRL |= DWT_CYCCNTENA_BIT;
    DWT_CYCCNT = 0;
    dwt_calibrate_overhead();
    return (DWT_CTRL & DWT_CYCCNTENA_BIT) != 0;
#endif
}

uint32_t dwt_elapsed_cycles(uint32_t start_cycles) {
    uint32_t now = dwt_get_cycles();
    uint32_t diff = now - start_cycles;
    return (diff > s_dwt_overhead) ? (diff - s_dwt_overhead) : 0;
}

uint64_t dwt_cycles_to_ns(uint32_t cycles, uint32_t cpu_freq_hz) {
    if (cpu_freq_hz == 0) return 0;
    return ((uint64_t)cycles * 1000000000ULL) / cpu_freq_hz;
}

void profiler_stats_update(profiler_stats_t *stats, uint32_t cycles) {
    if (stats->samples_count == 0) {
        stats->min_cycles = cycles;
        stats->max_cycles = cycles;
    } else {
        if (cycles < stats->min_cycles) stats->min_cycles = cycles;
        if (cycles > stats->max_cycles) stats->max_cycles = cycles;
    }
    stats->total_cycles += cycles;
    stats->samples_count++;
}

void profiler_stats_reset(profiler_stats_t *stats) {
    stats->min_cycles = 0xFFFFFFFFU;
    stats->max_cycles = 0;
    stats->total_cycles = 0;
    stats->samples_count = 0;
}
```
```cpp
// Приклад використання C++ RAII ScopedTimer у реальній задачі
#include "dwt_profiler.hpp"

namespace {
    embedded::profiler::ExecutionStats g_fir_filter_stats;
}

void process_audio_frame(float* buffer, size_t size) {
    // Автоматичний старт заміру при вході в область видимості
    embedded::profiler::ScopedTimer timer(g_fir_filter_stats);

    // Досліджуваний критичний код
    for (size_t i = 0; i < size; ++i) {
        buffer[i] = buffer[i] * 0.5f + 0.1f;
    }
    // Таймер зупиняється в деструкторі, статистика оновлюється автоматично
}
```
:::

## Апаратне стробування виводів GPIO для осцилографа

Для вимірювання затримок обробників переривань без внесення будь-яких затримок пам'яті використовується маніпуляція бітами порту через регістр атомарного встановлення/скидання `BSRR` (англ. *Bit Set/Reset Register*). Запис у цей регістр виконується за 1-2 такти шини AHB і не потребує блокування переривань, на відміну від операцій читання-модифікації-запису `ODR ^= PIN`.

:::tabs
```c
/* Швидкі макроси стробування GPIO на C */
#define PROFILING_PORT       GPIOB
#define PROFILING_PIN_MASK   (1U << 5)

/* Встановлення високого рівня на початку ділянки */
#define PROFILING_PIN_HIGH() do { PROFILING_PORT->BSRR = PROFILING_PIN_MASK; } while(0)

/* Скидання у низький рівень наприкінці ділянки */
#define PROFILING_PIN_LOW()  do { PROFILING_PORT->BSRR = (PROFILING_PIN_MASK << 16); } while(0)

void EXTI0_IRQHandler(void) {
    PROFILING_PIN_HIGH(); // Підйом фронту для осцилографа

    /* Корисна робота обробника */
    process_urgent_sensor_event();

    PROFILING_PIN_LOW();  // Спад фронту
}
```
```cpp
// Type-Safe GPIO Strobe на C++20 з використанням RAII
#pragma once
#include <cstdint>

namespace embedded::profiler {

template <uintptr_t PortBase, uint8_t PinIndex>
struct FastGpioPin {
    static_assert(PinIndex < 16, "Pin index must be between 0 and 15");

    static inline void set_high() noexcept {
        auto* bsrr = reinterpret_cast<volatile uint32_t*>(PortBase + 0x18); // Зсув BSRR у STM32
        *bsrr = (1UL << PinIndex);
    }

    static inline void set_low() noexcept {
        auto* bsrr = reinterpret_cast<volatile uint32_t*>(PortBase + 0x18);
        *bsrr = (1UL << (PinIndex + 16));
    }
};

template <typename GpioPinType>
class [[nodiscard]] ScopedGpioStrobe {
public:
    ScopedGpioStrobe() noexcept {
        GpioPinType::set_high();
    }
    ~ScopedGpioStrobe() noexcept {
        GpioPinType::set_low();
    }

    ScopedGpioStrobe(const ScopedGpioStrobe&) = delete;
    ScopedGpioStrobe& operator=(const ScopedGpioStrobe&) = delete;
};

} // namespace embedded::profiler
```
:::

## Інженерні обмеження, крайові випадки та тонкощі профілювання

Практичне застосування лічильника DWT та GPIO-стробування у промислових прошивках пов'язане з кількома тонкощами фізичної поведінки апаратури мікроконтролера:

### 1. Відсутність блоку DWT в ядрах Cortex-M0 та Cortex-M0+

Архітектура базового набору команд ARMv6-M (наприклад, мікроконтролери родин STM32F0, STM32L0, Raspberry Pi RP2040) апаратно не містить блоку відлагодження DWT. У таких чипах регістри за адресою `0xE0001000` фізично відсутні, а спроба читання повертає нуль або викликає помилку апаратного виключення `HardFault`.

Для ядер Cortex-M0 альтернативними інструментами є:
- **Системний таймер SysTick:** 24-бітний лічильник `SysTick->VAL`, який рахує від значення `SysTick->LOAD` вниз до нуля. Тривалість у тактах обчислюється як `(start_val - end_val)`. Якщо за час вимірювання таймер переповнився (скинув прапорець `COUNTFLAG`), до результату додається значення `LOAD`.
- **Вільний 32-бітний таймер загального призначення:** налаштування таймера (наприклад, TIM2) у режимі рахунку без прескалера (`PSC = 0`) з тактуванням від повної частоти шини APB.

### 2. Заморозка лічильника в режимах низького споживання (Sleep / Standby)

Під час переходу процесора в режим очікування події чи переривання за інструкціями `WFI` (Wait For Interrupt) або `WFE` (Wait For Event) тактування ядра процесора вимикається на апаратному рівні (англ. *Clock Gating*). Разом із ядром зупиняється і лічильник `DWT->CYCCNT`.

Якщо вимірювана ділянка містить очікування переривання всередині RTOS або блокуючий сон, лічильник DWT зафіксує лише чистий час активності ядра без урахування періоду перебування у сні. Для повного наскрізного вимірювання часу із включенням періодів глибокого сну слід використовувати зовнішній апаратний таймер RTC із незалежним тактуванням від низькочастотного кварцового резонатора LSE (32.768 кГц).

### 3. Прогрів кешу (Cache Warmup) та «холодний старт»

Під час першого виклику будь-якої функції інструкції завантажуються з повільної Flash-пам'яті у Prefetch-буфер або кеш інструкцій (I-Cache). Перший замір завжди показує підвищену кількість тактів (Cold Run). Усі наступні виклики (Warm Runs) виконуються з кешу з нульовими затримками.

Для об'єктивного аналізу:
- Якщо вимірюється **середній час (ACET)**: перший замір відкидають, а статистику збирають після попереднього «прогріву» функції.
- Якщо визначається **найгірший час (WCET)**: кеш примусово інвалідують перед кожним тестовим прогоном (`SCB_InvalidateICache()`), щоб змоделювати найгірший випадок холодного старту обробника після витіснення іншим кодом.

### 4. Вплив ємнісного навантаження виводу GPIO на осцилограф

Під час вимірювання ультракоротких імпульсів (тривалістю менше 100 нс) за допомогою GPIO-виводу фізична ємність щупа осцилографа (зазвичай 10–15 пФ) та внутрішній опір вихідного каскаду піна утворюють RC-ланцюг. Це призводить до завалювання фронтів імпульсу (тривалість наростання `t_rise` може досягати 10–20 нс).

Для усунення похибки:
1. Завжди налаштовуйте швидкість наростання виводу GPIO на максимальне значення в регістрі `OSPEEDR` (Very High Speed).
2. Використовуйте якісні пасивні щупи з дільником 1:10 (вхідна ємність менше 10 пФ) або активні диференційні пробники, а земляний контакт підключайте якомога коротшим пружинним контактом безпосередньо біля виводу чипа.
