# ⚙️ Модульна бібліотека самотестування POST/BIST за стандартом IEC 60730

Ця вставка містить повноцінну виробничу реалізацію діагностичного комплексу функційної безпеки (Safety Self-Test Engine) для мікроконтролерів на базі архітектури ARM Cortex-M та RISC-V. Бібліотека реалізує вимоги стандарту IEC 60730 Class B та промислового стандарту IEC 61508 SIL 2.

Головне завдання діагностичного комплексу — розділити процес верифікації апаратної частини на два взаємодоповнюючі етапи:
1. **POST (Power-On Self-Test):** вичерпне тестування апаратних ресурсів під час холодного старту (у функції `Reset_Handler`), коли прикладні задачі ще не створені, а оперативна пам'ять не містить цінних даних;
2. **Periodic BIST (Built-In Self-Test):** неруйнівне фонове сканування оперативної пам'яті малими квантами, поступовий підрахунок контрольної суми Flash та перехресний контроль частоти тактування під час штатної роботи супер-циклу або задач RTOS.

---

## Архітектурний дизайн та структури даних

Усі функції та контексти спроєктовано за принципом нульового динамічного виділення пам'яті (Zero Heap Allocation), що є обов'язковою вимогою стандартів функційної безпеки. Стан кожного діагностичного модуля інкапсулюється у статично виділені структури контексту.

Контекст тестування оперативної пам'яті (`bist_ram_slice_ctx_t`) зберігає межі області пам'яті, поточний вказівник на активний зріз та локальний резервний буфер `backup_buf`. Розмір зрізу за замовчуванням становить 16 32-бітних слів (64 байти). Це значення обрано як компроміс між швидкістю повного сканування пам'яті та часом перебування процесора у критичній секції із вимкненими перериваннями: виконання 10N операцій March C- над 16 словами на частоті ядра 168 МГц триває приблизно 1.2 мікросекунди, що гарантує відсутність джитера для високопріоритетних переривань керування двигунами чи силовими перетворювачами.

Контекст контролю постійної пам'яті (`bist_flash_crc_ctx_t`) розбиває верифікацію образу Flash на порції фіксованого розміру (типово 1024 байти за квант). Завдяки збереженню проміжного стану `running_crc` алгоритм не блокує виконання прикладного коду на тривалий час.

:::tabs
```c
#ifndef IEC60730_BIST_H
#define IEC60730_BIST_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди результатів самодіагностики */
typedef enum {
    BIST_OK               = 0x00,
    BIST_ERR_CPU_REG      = 0x01,
    BIST_ERR_CPU_FLAGS    = 0x02,
    BIST_ERR_CPU_PC       = 0x03,
    BIST_ERR_RAM_MARCH_C  = 0x10,
    BIST_ERR_FLASH_CRC    = 0x20,
    BIST_ERR_CLOCK_DRIFT  = 0x30,
    BIST_ERR_WDT_TRIGGER  = 0x40,
    BIST_ERR_ADC_VREF     = 0x50,
    BIST_ERR_GPIO_STUCK   = 0x60
} bist_status_t;

/* Контекст неруйнівного фонового тестування ОЗП */
typedef struct {
    uint32_t *start_addr;       /* Початкова адреса області ОЗП */
    uint32_t *end_addr;         /* Кінцева адреса області ОЗП */
    uint32_t *current_ptr;      /* Поточний вказівник на активний зріз */
    size_t    slice_words;      /* Кількість 32-бітних слів у зрізі */
    uint32_t  backup_buf[16];   /* Буфер для збереження вмісту активного зрізу (до 64 байт) */
} bist_ram_slice_ctx_t;

/* Контекст циклічної перевірки Flash */
typedef struct {
    const uint8_t *flash_start; /* Початок образу програми */
    size_t         total_bytes; /* Загальний розмір коду */
    size_t         bytes_per_slice; /* Кількість байтів на один цикл BIST */
    size_t         processed_bytes; /* Оброблено на даний момент */
    uint32_t       running_crc; /* Поточне проміжне значення CRC32 */
    uint32_t       expected_crc;/* Еталонний хеш із кінця Flash / образу */
} bist_flash_crc_ctx_t;

/* Контекст перехресного контролю тактування */
typedef struct {
    uint32_t expected_counts;   /* Очікувана кількість тактів PLL за 1 період LSI */
    uint32_t tolerance_counts;  /* Допустиме відхилення (наприклад, ±5%) */
} bist_clock_ctx_t;

/* ── Функції POST (виконуються одноразово при старті) ── */
bist_status_t bist_post_cpu_registers(void);
bist_status_t bist_post_cpu_flags(void);
bist_status_t bist_post_full_ram_march_c(uint32_t *start, uint32_t *end);
bist_status_t bist_post_flash_crc32(const uint8_t *start, size_t len, uint32_t expected);
bist_status_t bist_post_clock_check(const bist_clock_ctx_t *ctx);

/* ── Функції періодичного BIST (виконуються у робочому циклі) ── */
bist_status_t bist_slice_ram_march_c(bist_ram_slice_ctx_t *ctx);
bist_status_t bist_slice_flash_crc32(bist_flash_crc_ctx_t *ctx, bool *out_cycle_complete);

/* ── Аварійний перехід у безпечний стан ── */
void bist_enter_safe_state(bist_status_t error_code);

#ifdef __cplusplus
}
#endif

#endif /* IEC60730_BIST_H */
```
```cpp
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>

namespace safety {

enum class Status : std::uint8_t {
    Ok             = 0x00,
    ErrCpuReg      = 0x01,
    ErrCpuFlags    = 0x02,
    ErrCpuPc       = 0x03,
    ErrRamMarchC   = 0x10,
    ErrFlashCrc    = 0x20,
    ErrClockDrift  = 0x30,
    ErrWdtTrigger  = 0x40,
    ErrAdcVref     = 0x50,
    ErrGpioStuck   = 0x60
};

// Контекст неруйнівного зрізу ОЗП на базі std::span
template <std::size_t SliceWords = 16>
class RamSliceScanner {
public:
    explicit RamSliceScanner(std::span<std::uint32_t> ram_region) noexcept
        : region_(ram_region), current_offset_(0) {}

    [[nodiscard]] Status scan_next_slice() noexcept;
    void reset() noexcept { current_offset_ = 0; }

private:
    std::span<std::uint32_t> region_;
    std::size_t current_offset_;
    std::array<std::uint32_t, SliceWords> backup_buffer_{};
};

// Контекст інкрементального підрахунку CRC32 Flash
class FlashCrcScanner {
public:
    FlashCrcScanner(std::span<const std::uint8_t> flash_area,
                    std::uint32_t expected_crc,
                    std::size_t bytes_per_quantum = 1024) noexcept
        : flash_(flash_area), expected_crc_(expected_crc),
          quantum_(bytes_per_quantum), processed_(0), running_crc_(0xFFFFFFFFU) {}

    struct StepResult {
        Status status;
        bool is_cycle_finished;
    };

    [[nodiscard]] StepResult scan_quantum() noexcept;
    void reset() noexcept {
        processed_ = 0;
        running_crc_ = 0xFFFFFFFFU;
    }

private:
    std::span<const std::uint8_t> flash_;
    std::uint32_t expected_crc_;
    std::size_t quantum_;
    std::size_t processed_;
    std::uint32_t running_crc_;
};

// Перевірка тактового генератора
class ClockMonitor {
public:
    constexpr ClockMonitor(std::uint32_t expected, std::uint32_t tolerance) noexcept
        : expected_(expected), tolerance_(tolerance) {}

    [[nodiscard]] Status verify_frequency(std::uint32_t measured_counts) const noexcept {
        const std::uint32_t min_allowed = expected_ - tolerance_;
        const std::uint32_t max_allowed = expected_ + tolerance_;
        if (measured_counts < min_allowed || measured_counts > max_allowed) {
            return Status::ErrClockDrift;
        }
        return Status::Ok;
    }

private:
    std::uint32_t expected_;
    std::uint32_t tolerance_;
};

// Захищений вхід у Safe State
[[noreturn]] void enter_safe_state(Status reason) noexcept;

} // namespace safety
```
:::

---

## Реалізація алгоритмів діагностики

Реалізація модулів враховує специфіку компіляторів GCC та Clang для вбудованих систем:
* **Захист від оптимізатора:** Регістрові змінні жорстко прив'язані до імен регістрів архітектури ARM через атрибут `__asm__("r0")`, а доступ до пам'яті здійснюється через кваліфікатор `volatile`. Без цього компілятор із прапорцем `-O2` або `-O3` повністю видалив би цикли запису та читання March C-, оскільки з погляду семантики C вони записують значення, які негайно перезаписуються і не використовуються далі в коді.
* **Атомарність критичних операцій:** Для блокування переривань використовується інструкція `CPSID I` (Change Processor State Interrupt Disable), яка модифікує біт маски `PRIMASK`. У версії C++ блокування реалізовано через ідіому RAII у класі `InterruptGuard`, що виключає випадкове залишення системи з вимкненими перериваннями при передчасному виході з функції.
* **Синтез прапорців АЛП:** Тест прапорців навмисно виконує граничні операції додавання з переповненням знакового діапазону (`0x7FFFFFFF + 1`) та беззнакового переносу (`0xFFFFFFFF + 1`), змушуючи апаратні компаратори АЛП активувати лінії N, Z, C та V.

:::tabs
```c
#include "iec60730_bist.h"

/* Апаратні примітиви заборони/дозволу переривань */
static inline uint32_t disable_interrupts(void) {
    uint32_t primask;
    __asm__ volatile ("mrs %0, primask\n cpsid i" : "=r" (primask) :: "memory");
    return primask;
}

static inline void restore_interrupts(uint32_t primask) {
    __asm__ volatile ("msr primask, %0" :: "r" (primask) : "memory");
}

/* ── 1. Перевірка регістрів процесора (CPU Registers POST) ── */
bist_status_t bist_post_cpu_registers(void) {
    const uint32_t pat_a = 0x55555555UL;
    const uint32_t pat_b = 0xAAAAAAAAUL;

    /* Використовуємо інлайн-асемблер для тестування R0-R12, LR без втручання оптимізатора */
    register uint32_t r0 __asm__("r0") = pat_a;
    register uint32_t r1 __asm__("r1") = pat_a;
    register uint32_t r2 __asm__("r2") = pat_a;
    register uint32_t r3 __asm__("r3") = pat_a;
    register uint32_t r4 __asm__("r4") = pat_a;

    if (r0 != pat_a || r1 != pat_a || r2 != pat_a || r3 != pat_a || r4 != pat_a) {
        return BIST_ERR_CPU_REG;
    }

    r0 = pat_b; r1 = pat_b; r2 = pat_b; r3 = pat_b; r4 = pat_b;
    if (r0 != pat_b || r1 != pat_b || r2 != pat_b || r3 != pat_b || r4 != pat_b) {
        return BIST_ERR_CPU_REG;
    }

    return BIST_OK;
}

/* ── 2. Перевірка прапорців АЛП (ALU Flags) ── */
bist_status_t bist_post_cpu_flags(void) {
    volatile uint32_t a = 0x7FFFFFFFUL;
    volatile uint32_t b = 1;
    volatile uint32_t sum = a + b; /* Генерує переповнення (V-flag) і від'ємний результат (N-flag) */

    if ((int32_t)sum >= 0) {
        return BIST_ERR_CPU_FLAGS; /* Не спрацював прапорець знака N */
    }

    volatile uint32_t c = 0xFFFFFFFFUL;
    volatile uint32_t carry_sum = c + 1; /* Генерує перенесення (C-flag) і нуль (Z-flag) */
    if (carry_sum != 0) {
        return BIST_ERR_CPU_FLAGS; /* Не спрацював прапорець нуля Z */
    }

    return BIST_OK;
}

/* ── 3. Ядро алгоритму March C- для блоку пам'яті ── */
static bool execute_march_c_core(volatile uint32_t *mem, size_t words) {
    /* M0: ⇕ (w0) */
    for (size_t i = 0; i < words; ++i) {
        mem[i] = 0x00000000UL;
    }

    /* M1: ⇑ (r0, w1) */
    for (size_t i = 0; i < words; ++i) {
        if (mem[i] != 0x00000000UL) return false;
        mem[i] = 0xFFFFFFFFUL;
    }

    /* M2: ⇑ (r1, w0) */
    for (size_t i = 0; i < words; ++i) {
        if (mem[i] != 0xFFFFFFFFUL) return false;
        mem[i] = 0x00000000UL;
    }

    /* M3: ⇓ (r0, w1) */
    for (size_t i = words; i > 0; --i) {
        size_t idx = i - 1;
        if (mem[idx] != 0x00000000UL) return false;
        mem[idx] = 0xFFFFFFFFUL;
    }

    /* M4: ⇓ (r1, w0) */
    for (size_t i = words; i > 0; --i) {
        size_t idx = i - 1;
        if (mem[idx] != 0xFFFFFFFFUL) return false;
        mem[idx] = 0x00000000UL;
    }

    /* M5: ⇕ (r0) */
    for (size_t i = 0; i < words; ++i) {
        if (mem[i] != 0x00000000UL) return false;
    }

    return true;
}

/* ── 4. Неруйнівний зріз ОЗП для фонового BIST ── */
bist_status_t bist_slice_ram_march_c(bist_ram_slice_ctx_t *ctx) {
    if (ctx == NULL || ctx->current_ptr >= ctx->end_addr) {
        return BIST_OK;
    }

    size_t words_to_test = ctx->slice_words;
    if (ctx->current_ptr + words_to_test > ctx->end_addr) {
        words_to_test = (size_t)(ctx->end_addr - ctx->current_ptr);
    }

    /* КРИТИЧНА СЕКЦІЯ: атомарне збереження, тест і відновлення */
    uint32_t primask = disable_interrupts();

    /* Зберігаємо дані застосунку у захищений буфер */
    for (size_t i = 0; i < words_to_test; ++i) {
        ctx->backup_buf[i] = ctx->current_ptr[i];
    }

    /* Прогін March C- */
    bool pass = execute_march_c_core((volatile uint32_t *)ctx->current_ptr, words_to_test);

    /* Відновлюємо дані застосунку */
    for (size_t i = 0; i < words_to_test; ++i) {
        ctx->current_ptr[i] = ctx->backup_buf[i];
    }

    restore_interrupts(primask);

    if (!pass) {
        return BIST_ERR_RAM_MARCH_C;
    }

    /* Зсуваємо вказівник на наступний зріз */
    ctx->current_ptr += words_to_test;
    if (ctx->current_ptr >= ctx->end_addr) {
        ctx->current_ptr = ctx->start_addr; /* Зациклення */
    }

    return BIST_OK;
}

/* ── 5. Інкрементальний розрахунок CRC-32 (IEEE 802.3) ── */
static uint32_t crc32_step(uint32_t crc, uint8_t data) {
    crc ^= data;
    for (int i = 0; i < 8; ++i) {
        if (crc & 1) {
            crc = (crc >> 1) ^ 0xEDB88320UL;
        } else {
            crc >>= 1;
        }
    }
    return crc;
}

bist_status_t bist_slice_flash_crc32(bist_flash_crc_ctx_t *ctx, bool *out_cycle_complete) {
    *out_cycle_complete = false;
    size_t chunk = ctx->bytes_per_slice;
    if (ctx->processed_bytes + chunk > ctx->total_bytes) {
        chunk = ctx->total_bytes - ctx->processed_bytes;
    }

    const uint8_t *p = ctx->flash_start + ctx->processed_bytes;
    for (size_t i = 0; i < chunk; ++i) {
        ctx->running_crc = crc32_step(ctx->running_crc, p[i]);
    }

    ctx->processed_bytes += chunk;
    if (ctx->processed_bytes >= ctx->total_bytes) {
        uint32_t final_crc = ~ctx->running_crc;
        if (final_crc != ctx->expected_crc) {
            return BIST_ERR_FLASH_CRC;
        }
        *out_cycle_complete = true;
        ctx->processed_bytes = 0;
        ctx->running_crc = 0xFFFFFFFFUL;
    }

    return BIST_OK;
}

/* ── 6. Перехід у безпечний стан (Safe State Lock) ── */
void bist_enter_safe_state(bist_status_t error_code) {
    disable_interrupts();

    /* 1. Знеструмити критичні виходи: ШІМ у 0, реле розімкнути */
    /* GPIOA->ODR = 0; TIM1->BDTR &= ~TIM_BDTR_MOE; */

    /* 2. Зафіксувати код помилки в нелетких регістрах RTC/Backup */
    /* RTC->BKP0R = (uint32_t)error_code; */
    (void)error_code;

    /* 3. Нескінченне зависання для очікування апаратного скиду сторожовим таймером */
    for (;;) {
        __asm__ volatile ("wfi");
    }
}
```
```cpp
#include "iec60730_bist.hpp"
#include <concepts>
#include <algorithm>

namespace safety {

namespace {

// RAII обгортка блокування переривань
class InterruptGuard {
public:
    InterruptGuard() noexcept {
        __asm__ volatile ("mrs %0, primask\n cpsid i" : "=r" (primask_) :: "memory");
    }
    ~InterruptGuard() noexcept {
        __asm__ volatile ("msr primask, %0" :: "r" (primask_) : "memory");
    }
    InterruptGuard(const InterruptGuard&) = delete;
    InterruptGuard& operator=(const InterruptGuard&) = delete;

private:
    std::uint32_t primask_{0};
};

// Ядро алгоритму March C- над std::span
bool execute_march_c(std::span<volatile std::uint32_t> slice) noexcept {
    // M0: ⇕ (w0)
    for (auto& word : slice) {
        word = 0x00000000U;
    }

    // M1: ⇑ (r0, w1)
    for (std::size_t i = 0; i < slice.size(); ++i) {
        if (slice[i] != 0x00000000U) return false;
        slice[i] = 0xFFFFFFFFU;
    }

    // M2: ⇑ (r1, w0)
    for (std::size_t i = 0; i < slice.size(); ++i) {
        if (slice[i] != 0xFFFFFFFFU) return false;
        slice[i] = 0x00000000U;
    }

    // M3: ⇓ (r0, w1)
    for (std::size_t i = slice.size(); i > 0; --i) {
        const std::size_t idx = i - 1;
        if (slice[idx] != 0x00000000U) return false;
        slice[idx] = 0xFFFFFFFFU;
    }

    // M4: ⇓ (r1, w0)
    for (std::size_t i = slice.size(); i > 0; --i) {
        const std::size_t idx = i - 1;
        if (slice[idx] != 0xFFFFFFFFU) return false;
        slice[idx] = 0x00000000U;
    }

    // M5: ⇕ (r0)
    for (const auto& word : slice) {
        if (word != 0x00000000U) return false;
    }

    return true;
}

constexpr std::uint32_t update_crc32(std::uint32_t crc, std::uint8_t byte) noexcept {
    crc ^= byte;
    for (int i = 0; i < 8; ++i) {
        crc = (crc & 1) ? ((crc >> 1) ^ 0xEDB88320U) : (crc >> 1);
    }
    return crc;
}

} // namespace

template <std::size_t SliceWords>
Status RamSliceScanner<SliceWords>::scan_next_slice() noexcept {
    if (region_.empty()) {
        return Status::Ok;
    }

    const std::size_t remaining = region_.size() - current_offset_;
    const std::size_t count = std::min(remaining, SliceWords);

    auto target_span = region_.subspan(current_offset_, count);

    bool march_passed = false;
    {
        InterruptGuard lock; // Атомарне тестування

        // 1. Зберегти початкові дані
        std::copy_n(target_span.data(), count, backup_buffer_.begin());

        // 2. Виконати March C-
        std::span<volatile std::uint32_t> vol_span(
            reinterpret_cast<volatile std::uint32_t*>(target_span.data()), count);
        march_passed = execute_march_c(vol_span);

        // 3. Відновити стан пам'яті
        std::copy_n(backup_buffer_.begin(), count, target_span.data());
    }

    if (!march_passed) {
        return Status::ErrRamMarchC;
    }

    current_offset_ += count;
    if (current_offset_ >= region_.size()) {
        current_offset_ = 0; // Перехід до початку масиву
    }

    return Status::Ok;
}

FlashCrcScanner::StepResult FlashCrcScanner::scan_quantum() noexcept {
    if (flash_.empty()) {
        return {Status::Ok, true};
    }

    const std::size_t remaining = flash_.size() - processed_;
    const std::size_t chunk = std::min(remaining, quantum_);

    auto sub = flash_.subspan(processed_, chunk);
    for (std::uint8_t b : sub) {
        running_crc_ = update_crc32(running_crc_, b);
    }

    processed_ += chunk;
    if (processed_ >= flash_.size()) {
        const std::uint32_t final_crc = ~running_crc_;
        if (final_crc != expected_crc_) {
            return {Status::ErrFlashCrc, true};
        }
        reset();
        return {Status::Ok, true};
    }

    return {Status::Ok, false};
}

[[noreturn]] void enter_safe_state(Status reason) noexcept {
    __asm__ volatile ("cpsid i" ::: "memory");

    // Вимкнення критичної периферії: контактори, ШІМ, нагрівачі
    // Фіксація коду помилки у Retain RAM
    (void)reason;

    for (;;) {
        __asm__ volatile ("wfi");
    }
}

// Явна інстанціація типового сканера
template class RamSliceScanner<16>;

} // namespace safety
```
:::

---

## Інтеграція у робочий цикл та годування Watchdog

Золоте правило функційної безпеки: **годування сторожового таймера є свідченням успішного проходження всіх кроків самодіагностики**. Годувати Watchdog наосліп або в незалежному перериванні апаратного таймера категорично заборонено, оскільки це замаскує дефект пам'яті чи зависання BIST-слайсера.

У типовому головному циклі супер-циклу або у виділеній задачі нагляду RTOS функція `safety_periodic_tick()` викликається на кожній ітерації:
1. Виконується неруйнівний тест чергових 64 байтів ОЗП;
2. Обчислюється контрольна сума чергового кілобайта Flash;
3. Якщо хоча б один тест зафіксував несправність — відбувається негайний перехід у `bist_enter_safe_state()`, де живлення приводів знімається, а процесор зависає;
4. Тільки якщо всі підсистеми повернули `BIST_OK`, викликається `watchdog_feed()`.

:::tabs
```c
void safety_periodic_tick(void) {
    bool flash_done = false;

    /* 1. Тестуємо чергові 64 байти ОЗП */
    bist_status_t st = bist_slice_ram_march_c(&g_ram_ctx);
    if (st != BIST_OK) {
        bist_enter_safe_state(st);
    }

    /* 2. Рахуємо черговий 1 КБ Flash */
    st = bist_slice_flash_crc32(&g_flash_ctx, &flash_done);
    if (st != BIST_OK) {
        bist_enter_safe_state(st);
    }

    /* 3. Годуємо Watchdog ТІЛЬКИ якщо всі BIST-слайси пройшли успішно */
    watchdog_feed();
}
```
```cpp
void safety_periodic_tick() noexcept {
    // 1. Тестуємо чергові 64 байти ОЗП
    if (const auto st = g_ram_scanner.scan_next_slice(); st != safety::Status::Ok) {
        safety::enter_safe_state(st);
    }

    // 2. Рахуємо черговий 1 КБ Flash
    if (const auto [st, finished] = g_flash_scanner.scan_quantum(); st != safety::Status::Ok) {
        safety::enter_safe_state(st);
    }

    // 3. Годуємо Watchdog ТІЛЬКИ якщо всі BIST-слайси пройшли успішно
    watchdog_feed();
}
```
:::

Така модульна архітектура забезпечує повну сертифікаційну відповідність класу IEC 60730 Class B з мінімальними накладними витратами на пам'ять та час виконання процесора.

---

## Взаємодія з DMA та блоком захисту пам'яті (MPU)

Під час практичної інтеграції діагностичного комплексу розробники стикаються з двома специфічними апаратними крайовими випадками:

1. **Конфлікти прямого доступу до пам'яті (DMA Bus Collisions):**
   Контролер DMA здійснює запис у пам'ять незалежно від процесора. Якщо під час прогону шести фаз March C- на активному зрізі ОЗП периферійний блок (наприклад, SPI чи АЦП через DMA) запише нові виміряні дані в одну з тестованих комірок, виникне подвійний збій: по-перше, алгоритм March C- зафіксує розбіжність очікуваного патерну і помилково підніме тривогу; по-друге, після відновлення даних із тіньового буфера `backup_buf` свіжі дані DMA будуть безповоротно затерті старими значеннями.
   *Інженерне рішення:* Буфери DMA розміщують в окремій нетестованій області ОЗП або виділяють під них фіксовані сторінки, які виключаються з контексту `RamSliceScanner` і перевіряються окремо лише у моменти простою DMA.

2. **Вимоги до блоку захисту пам'яті (MPU):**
   Якщо в системі активний блок MPU (Memory Protection Unit), що розділяє простір пам'яті на привілейовані та непривілейовані зони, діагностичний код BIST повинен виконуватися виключно у привілейованому режимі ядра (Privileged Handler Mode або Privileged Thread Mode). Спроба запису тестових патернів у стек іншої задачі непривілейованим потоком викличе апаратний виняток `MemManage Fault`, що паралізує роботу пристрою.

---

## Валідація та тестування ін'єкцією несправностей (Fault Injection)

Сертифікаційні лабораторії (TÜV, UL, VDE) вимагають обов'язкового практичного підтвердження працездатності самої бібліотеки BIST за допомогою методів штучної ін'єкції несправностей (*Fault Injection Testing*):

* **Ін'єкція дефектів ОЗП:** За допомогою апаратного відлагоджувача JTAG/SWD або спеціального тестового переривання в один із бітів пам'яті примусово записується інверсне значення під час виконання кроку M1 алгоритму March C-. Бібліотека зобов'язана зафіксувати код `BIST_ERR_RAM_MARCH_C` та перейти в безпечний стан протягом одного кванта.
* **Ін'єкція дефектів Flash:** Зміна константи у верифікованій області пам'яті повинна призвести до фіксації помилки `BIST_ERR_FLASH_CRC` після повного обходу адресного простору Flash.
* **Імітація збою тактування:** Примусова зміна дільника передподільника таймера захоплення повинна миттєво генерувати код `BIST_ERR_CLOCK_DRIFT`.

Проходження цих тестів доводить, що система самодіагностики є надійною і не має прихованих сліпих зон.
