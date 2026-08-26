# ⚙️ Модуль мікросекундного профілювальника задач та функцій для систем реального часу

Розробка систем жорсткого реального часу на базі мікроконтролерів ARM Cortex-M вимагає постійного інструментального контролю за тривалістю виконання функцій, часом відгуку задач та накладними витратами планувальника RTOS. Стандартні програмні таймери (наприклад `SysTick`) із роздільною здатністю 1 мс не підходять для профілювання швидких обчислювальних контурів (10–500 мкс), оскільки ціла сотня ітерацій поміщається всередині одного системного кванту часу.

Цей модуль реалізує легкий, неінвазивний профілювальник на базі 32-розрядного апаратного лічильника циклів `DWT->CYCCNT`, що забезпечує однотактову точність вимірювання (5.95 нс на частоті 168 МГц) з автоматичною компенсацією власного оверхеду та розрахунком джиттера періодичності.

## Апаратний фундамент: регістри підсистеми DWT у Cortex-M

Блок DWT (англ. *Data Watchpoint and Trace*) розташований на внутрішній шині приватних периферійних пристроїв процесора (англ. *Private Peripheral Bus*, PPB) з базовою адресою `0xE0001000`. Окрім базового лічильника тактових циклів `CYCCNT`, блок містить додаткові лічильники подій конвеєра:

* `DWT->CTRL` (зсув `0x000`): регістр конфігурації та керування. Біт 0 (`CYCCNTENA`) вмикає лічильник тактових циклів `CYCCNT`. Біти 16–21 дозволяють роботу лічильників додаткових апаратних подій.
* `DWT->CYCCNT` (зсув `0x004`): безперервний 32-розрядний лічильник тактових імпульсів процесорного ядра `HCLK`. Інкрементується щотакту під час активної роботи ядра.
* `DWT->CPICNT` (зсув `0x008`): 8-розрядний лічильник додаткових циклів на інструкцію (англ. *Cycles Per Instruction*), що рахує такти простою конвеєра під час виконання мультитактових інструкцій.
* `DWT->EXCCNT` (зсув `0x00C`): 8-розрядний лічильник накладних витрат переривань (рахує такти стекінгу, анстекінгу та виконання коду обробників ISR).
* `DWT->SLEEPCNT` (зсув `0x010`): 8-розрядний лічильник циклів, проведених процесором у стані низького енергоспоживання після виклику інструкції `WFI` або `WFE`.
* `DWT->LSUCNT` (зсув `0x014`): 8-розрядний лічильник затримок блоку завантаження/збереження (англ. *Load-Store Unit*), що фіксує цикли очікування повільної пам'яті.
* `DWT->FOLDCNT` (зсув `0x018`): 8-розрядний лічильник «згорнутих» інструкцій (інструкції переходу, виконані паралельно з основними інструкціями без витрати тактів).

Для активації доступу до блоку DWT необхідно попередньо подати живлення на логіку трасування, встановивши біт 24 (`TRCENA`) у глобальному регістрі керування відладкою `CoreDebug->DEMCR` (адреса `0xE000EDFC`).

## Архітектура та структури даних профілювальника

Профілювальник відстежує фіксований масив контрольних точок (ідентифікаторів задач або функцій), що виключає динамічне виділення пам'яті (`malloc`/`new`) у критичних секціях. Для кожного зареєстрованого ідентифікатора модуль підтримує структуру агрегованої статистики:

* `name` — людиночитаний ідентифікатор задачі або функції для звітів;
* `expected_period_cyc` — номінальний період виклику в тактах процесора (для періодичних задач) або 0 (для спорадичних функцій);
* `min_cyc` — найкращий зафіксований час виконання (BCET);
* `max_cyc` — найгірший зафіксований час виконання (WCET);
* `total_cyc` — 64-розрядний накопичувач сумарного часу для точного розрахунку середнього часу (ACET);
* `call_count` — лічильник кількості успішних викликів функції;
* `max_jitter_cyc` — максимальне абсолютне відхилення між двома послідовними запусками від номінального періоду;
* `last_start_cyc` — мітка часу останнього входу в досліджувану ділянку коду;
* `last_duration_cyc` — тривалість останньої завершеної ітерації.

:::tabs
```c
/* task_profiler.h - C API профілювальника */
#ifndef TASK_PROFILER_H
#define TASK_PROFILER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PROFILER_MAX_TASKS 8

typedef struct {
    const char* name;
    uint32_t expected_period_cyc; /* 0 якщо спорадична */
    uint32_t min_cyc;
    uint32_t max_cyc;
    uint64_t total_cyc;
    uint32_t call_count;
    uint32_t max_jitter_cyc;
    uint32_t last_start_cyc;
    uint32_t last_duration_cyc;
} TaskStats;

void task_profiler_init(uint32_t cpu_freq_hz);
void task_profiler_register_task(uint8_t id, const char* name, uint32_t expected_period_us);
void task_profiler_enter(uint8_t id);
void task_profiler_exit(uint8_t id);
void task_profiler_get_stats(uint8_t id, TaskStats* out_stats);
void task_profiler_print_report(void (*print_fn)(const char* str));

#ifdef __cplusplus
}
#endif

#endif /* TASK_PROFILER_H */
```
```cpp
// task_profiler.hpp - C++20 API профілювальника з RAII Scope
#pragma once

#include <cstdint>
#include <array>
#include <string_view>
#include <span>
#include <algorithm>

namespace RealTime {

struct TaskStats {
    std::string_view name{"Unnamed"};
    uint32_t expected_period_cyc{0};
    uint32_t min_cyc{UINT32_MAX};
    uint32_t max_cyc{0};
    uint64_t total_cyc{0};
    uint32_t call_count{0};
    uint32_t max_jitter_cyc{0};
    uint32_t last_start_cyc{0};
    uint32_t last_duration_cyc{0};
};

template <size_t MaxTasks = 8>
class TaskProfiler {
public:
    explicit TaskProfiler(uint32_t cpu_freq_hz) noexcept : cpu_freq_hz_(cpu_freq_hz) {
        init_hardware();
    }

    void register_task(uint8_t id, std::string_view name, uint32_t expected_period_us) noexcept {
        if (id >= MaxTasks) return;
        tasks_[id].name = name;
        tasks_[id].expected_period_cyc = (expected_period_us * (cpu_freq_hz_ / 1'000'000U));
        tasks_[id].min_cyc = UINT32_MAX;
        tasks_[id].max_cyc = 0;
        tasks_[id].total_cyc = 0;
        tasks_[id].call_count = 0;
        tasks_[id].max_jitter_cyc = 0;
        tasks_[id].last_start_cyc = 0;
    }

    void enter(uint8_t id) noexcept {
        if (id >= MaxTasks) return;
        const uint32_t now = read_cyccnt();
        auto& t = tasks_[id];

        if (t.expected_period_cyc > 0 && t.last_start_cyc > 0) {
            const uint32_t actual_period = now - t.last_start_cyc;
            const uint32_t jitter = (actual_period > t.expected_period_cyc)
                ? (actual_period - t.expected_period_cyc)
                : (t.expected_period_cyc - actual_period);
            if (jitter > t.max_jitter_cyc) {
                t.max_jitter_cyc = jitter;
            }
        }
        t.last_start_cyc = now;
    }

    void exit(uint8_t id) noexcept {
        const uint32_t stop = read_cyccnt();
        if (id >= MaxTasks) return;
        auto& t = tasks_[id];
        
        uint32_t elapsed = stop - t.last_start_cyc;
        if (elapsed >= overhead_cyc_) {
            elapsed -= overhead_cyc_;
        }

        t.last_duration_cyc = elapsed;
        t.total_cyc += elapsed;
        t.call_count++;

        if (elapsed < t.min_cyc) t.min_cyc = elapsed;
        if (elapsed > t.max_cyc) t.max_cyc = elapsed;
    }

    [[nodiscard]] const TaskStats& get_stats(uint8_t id) const noexcept {
        static constexpr TaskStats empty_stats{};
        return (id < MaxTasks) ? tasks_[id] : empty_stats;
    }

    [[nodiscard]] uint32_t cyc_to_us(uint32_t cyc) const noexcept {
        return static_cast<uint32_t>((static_cast<uint64_t>(cyc) * 1'000'000ULL) / cpu_freq_hz_);
    }

    // RAII Guard для автоматичного вимірювання області видимості
    class ScopeGuard {
    public:
        ScopeGuard(TaskProfiler& profiler, uint8_t id) noexcept
            : profiler_(profiler), id_(id) {
            profiler_.enter(id_);
        }
        ~ScopeGuard() noexcept {
            profiler_.exit(id_);
        }
        ScopeGuard(const ScopeGuard&) = delete;
        ScopeGuard& operator=(const ScopeGuard&) = delete;
    private:
        TaskProfiler& profiler_;
        uint8_t id_;
    };

    [[nodiscard]] ScopeGuard make_scope(uint8_t id) noexcept {
        return ScopeGuard(*this, id);
    }

private:
    void init_hardware() noexcept;
    static inline uint32_t read_cyccnt() noexcept;

    uint32_t cpu_freq_hz_{168'000'000U};
    uint32_t overhead_cyc_{0};
    std::array<TaskStats, MaxTasks> tasks_{};
};

} // namespace RealTime
```
:::

## Фізика обробки переповнення 32-розрядного лічильника

Лічильник `DWT->CYCCNT` є стандартним апаратним 32-розрядним регістром зі значеннями від `0` до `2^32 - 1` (`0xFFFFFFFF`). За частоти ядра 168 МГц він переповнюється кожні 25.565 секунди.

Чому беззнакова різниця `stop - start` залишається строго коректною навіть за умови переповнення лічильника через нуль? Розглянемо приклад:

1. Нехай задача стартує в момент `start = 0xFFFFFFF0` (за 16 тактів до переповнення).
2. Завершення відбувається в момент `stop = 0x00000020` (32 такти після переповнення).
3. Істинна тривалість виконання: `16 + 32 = 48` тактів.
4. Обчислення за правилами C/C++ для типу `uint32_t`:
   `0x00000020 - 0xFFFFFFF0 = 0x00000020 + (~0xFFFFFFF0 + 1) = 0x00000020 + 0x00000010 = 0x00000030 = 48` тактів.

Завдяки властивостям додаткового коду (англ. *Two's Complement Arithmetic*) операція віднімання цілих без знаку в межах розрядності `2^32` дає математично точний результат для будь-якого інтервалу, меншого за період переповнення.

## Калібрування власного оверхеду зчитування

Будь-яка вимірювальна функція вносить затримку через виконання власних інструкцій. Зчитування регістра `DWT_CYCCNT` через шину PPB займає від 1 до 3 тактів шини AHB/PPB, а виклик функції `task_profiler_enter()` потребує додаткових інструкцій збереження регістрів та оновлення полів структури.

Щоб виключити вплив самого інструменту на результати, модуль під час ініціалізації проводить автокалібрування: виконує два послідовні зчитування лічильника `DWT_CYCCNT` без корисного навантаження між ними та зберігає різницю `s_overhead_cyc`. Під час кожного виклику `task_profiler_exit()` ця величина автоматично віднімається від виміряного часу виконання.

## Повна реалізація ядра профілювальника на C та C++

Нижче наведено робочу реалізацію функцій модуля:

:::tabs
```c
/* task_profiler.c - Реалізація на чистому C для Cortex-M */
#include "task_profiler.h"
#include <stdio.h>

/* Апаратні адреси CoreDebug та DWT */
#define CORE_DEBUG_DEMCR        (*(volatile uint32_t*)0xE000EDFCU)
#define CORE_DEBUG_DEMCR_TRCENA (1U << 24)

#define DWT_CTRL                (*(volatile uint32_t*)0xE0001000U)
#define DWT_CTRL_CYCCNTENA      (1U << 0)
#define DWT_CYCCNT              (*(volatile uint32_t*)0xE0001004U)

static TaskStats s_tasks[PROFILER_MAX_TASKS];
static uint32_t s_cpu_freq_hz = 168000000U;
static uint32_t s_overhead_cyc = 0;

static inline uint32_t read_dwt_cycles(void) {
    return DWT_CYCCNT;
}

static void calibrate_overhead(void) {
    uint32_t start, stop;
    /* Вимірюємо тривалість двох послідовних читань */
    start = read_dwt_cycles();
    stop = read_dwt_cycles();
    s_overhead_cyc = stop - start;
}

void task_profiler_init(uint32_t cpu_freq_hz) {
    s_cpu_freq_hz = cpu_freq_hz;
    
    /* 1. Активація блоку трасування в CoreDebug */
    CORE_DEBUG_DEMCR |= CORE_DEBUG_DEMCR_TRCENA;
    
    /* 2. Скидання та активація лічильника CYCCNT у DWT */
    DWT_CYCCNT = 0U;
    DWT_CTRL |= DWT_CTRL_CYCCNTENA;
    
    /* 3. Очищення структур статистики */
    for (int i = 0; i < PROFILER_MAX_TASKS; ++i) {
        s_tasks[i].name = "Unused";
        s_tasks[i].min_cyc = 0xFFFFFFFFU;
        s_tasks[i].max_cyc = 0U;
        s_tasks[i].total_cyc = 0ULL;
        s_tasks[i].call_count = 0U;
        s_tasks[i].max_jitter_cyc = 0U;
        s_tasks[i].last_start_cyc = 0U;
    }
    
    calibrate_overhead();
}

void task_profiler_register_task(uint8_t id, const char* name, uint32_t expected_period_us) {
    if (id >= PROFILER_MAX_TASKS) return;
    s_tasks[id].name = name;
    s_tasks[id].expected_period_cyc = (uint32_t)(((uint64_t)expected_period_us * s_cpu_freq_hz) / 1000000ULL);
    s_tasks[id].min_cyc = 0xFFFFFFFFU;
    s_tasks[id].max_cyc = 0U;
    s_tasks[id].total_cyc = 0ULL;
    s_tasks[id].call_count = 0U;
    s_tasks[id].max_jitter_cyc = 0U;
    s_tasks[id].last_start_cyc = 0U;
}

void task_profiler_enter(uint8_t id) {
    if (id >= PROFILER_MAX_TASKS) return;
    uint32_t now = read_dwt_cycles();
    TaskStats* t = &s_tasks[id];
    
    if (t->expected_period_cyc > 0 && t->last_start_cyc > 0) {
        uint32_t actual_period = now - t->last_start_cyc;
        uint32_t jitter = (actual_period > t->expected_period_cyc) 
            ? (actual_period - t->expected_period_cyc) 
            : (t->expected_period_cyc - actual_period);
        if (jitter > t->max_jitter_cyc) {
            t->max_jitter_cyc = jitter;
        }
    }
    t->last_start_cyc = now;
}

void task_profiler_exit(uint8_t id) {
    uint32_t stop = read_dwt_cycles();
    if (id >= PROFILER_MAX_TASKS) return;
    TaskStats* t = &s_tasks[id];
    
    uint32_t elapsed = stop - t->last_start_cyc;
    if (elapsed >= s_overhead_cyc) {
        elapsed -= s_overhead_cyc;
    }
    
    t->last_duration_cyc = elapsed;
    t->total_cyc += elapsed;
    t->call_count++;
    
    if (elapsed < t->min_cyc) t->min_cyc = elapsed;
    if (elapsed > t->max_cyc) t->max_cyc = elapsed;
}

void task_profiler_get_stats(uint8_t id, TaskStats* out_stats) {
    if (id < PROFILER_MAX_TASKS && out_stats != NULL) {
        *out_stats = s_tasks[id];
    }
}

void task_profiler_print_report(void (*print_fn)(const char* str)) {
    char buf[128];
    print_fn("\r\n+---------------- REAL-TIME EXECUTION PROFILE ----------------+\r\n");
    print_fn("ID  Name            Calls    Min(us)  Avg(us)  Max(us)  Jitter(us)\r\n");
    print_fn("--------------------------------------------------------------\r\n");
    
    for (uint8_t i = 0; i < PROFILER_MAX_TASKS; ++i) {
        TaskStats* t = &s_tasks[i];
        if (t->call_count == 0) continue;
        
        uint32_t min_us = (uint32_t)(((uint64_t)t->min_cyc * 1000000ULL) / s_cpu_freq_hz);
        uint32_t max_us = (uint32_t)(((uint64_t)t->max_cyc * 1000000ULL) / s_cpu_freq_hz);
        uint32_t avg_us = (uint32_t)((t->total_cyc * 1000000ULL) / ((uint64_t)t->call_count * s_cpu_freq_hz));
        uint32_t jit_us = (uint32_t)(((uint64_t)t->max_jitter_cyc * 1000000ULL) / s_cpu_freq_hz);
        
        snprintf(buf, sizeof(buf), "%-3u %-15s %-8lu %-8lu %-8lu %-8lu %-8lu\r\n",
                 i, t->name, (unsigned long)t->call_count,
                 (unsigned long)min_us, (unsigned long)avg_us,
                 (unsigned long)max_us, (unsigned long)jit_us);
        print_fn(buf);
    }
    print_fn("+------------------------------------------------------------+\r\n");
}
```
```cpp
// task_profiler.cpp - Реалізація методів TaskProfiler для C++20
#include "task_profiler.hpp"
#include <cstdio>
#include <array>

namespace RealTime {

namespace Hardware {
    inline volatile uint32_t& DEMCR   = *reinterpret_cast<volatile uint32_t*>(0xE000EDFCU);
    inline volatile uint32_t& DWT_CTRL = *reinterpret_cast<volatile uint32_t*>(0xE0001000U);
    inline volatile uint32_t& DWT_CYCCNT = *reinterpret_cast<volatile uint32_t*>(0xE0001004U);

    constexpr uint32_t DEMCR_TRCENA = (1U << 24);
    constexpr uint32_t DWT_CYCCNTENA = (1U << 0);
}

template <size_t MaxTasks>
void TaskProfiler<MaxTasks>::init_hardware() noexcept {
    // 1. Активація блоку трасування
    Hardware::DEMCR |= Hardware::DEMCR_TRCENA;
    
    // 2. Активація лічильника
    Hardware::DWT_CYCCNT = 0U;
    Hardware::DWT_CTRL |= Hardware::DWT_CYCCNTENA;

    // 3. Калібрування власного оверхеду
    const uint32_t start = read_cyccnt();
    const uint32_t stop = read_cyccnt();
    overhead_cyc_ = stop - start;
}

template <size_t MaxTasks>
inline uint32_t TaskProfiler<MaxTasks>::read_cyccnt() noexcept {
    return Hardware::DWT_CYCCNT;
}

// Явна інстанціація шаблону для розміру 8
template class TaskProfiler<8>;

} // namespace RealTime
```
:::

## Інтеграція в FreeRTOS через трасувальні макроси

Для автоматичного профілювання перемикання контексту RTOS без ручного додавання викликів у код задачі, профілювальник підключають безпосередньо у заголовок конфігурації `FreeRTOSConfig.h`:

:::tabs
```c
/* Фрагмент FreeRTOSConfig.h */
#include "task_profiler.h"

/* Викликається щоразу, коли планувальник обирає нову задачу */
#define traceTASK_SWITCHED_IN() do {                                      \
    TaskHandle_t xTask = xTaskGetCurrentTaskHandle();                     \
    UBaseType_t uxId = uxTaskGetTaskNumber(xTask);                        \
    if (uxId < PROFILER_MAX_TASKS) {                                      \
        task_profiler_enter((uint8_t)uxId);                               \
    }                                                                     \
} while(0)

/* Викликається безпосередньо перед витісненням поточної задачі */
#define traceTASK_SWITCHED_OUT() do {                                     \
    TaskHandle_t xTask = xTaskGetCurrentTaskHandle();                     \
    UBaseType_t uxId = uxTaskGetTaskNumber(xTask);                        \
    if (uxId < PROFILER_MAX_TASKS) {                                      \
        task_profiler_exit((uint8_t)uxId);                                \
    }                                                                     \
} while(0)
```
```cpp
// Фрагмент RTOS хуків у стилі C++20
#include "task_profiler.hpp"

extern "C" void vApplicationTaskHookIn(void* task_handle, uint32_t task_id) noexcept;
extern "C" void vApplicationTaskHookOut(void* task_handle, uint32_t task_id) noexcept;

namespace {
    RealTime::TaskProfiler<8> g_system_profiler(168'000'000U);
}

extern "C" void vApplicationTaskHookIn(void* /*task_handle*/, uint32_t task_id) noexcept {
    g_system_profiler.enter(static_cast<uint8_t>(task_id));
}

extern "C" void vApplicationTaskHookOut(void* /*task_handle*/, uint32_t task_id) noexcept {
    g_system_profiler.exit(static_cast<uint8_t>(task_id));
}
```
:::

## Пастки та крайові випадки

### 1. Оптимізація та перевпорядкування інструкцій компілятором

Оптимізуючий компілятор (із прапорцями `-O2` або `-O3`) має право змінювати порядок інструкцій, якщо це не порушує послідовну семантику потоку. У результаті інструкція читання `DWT_CYCCNT` може бути перенесена через точку виклику функції, що досліджується.

Щоб запобігти цьому, застосовують програмні та апаратні бар'єри пам'яті:

:::tabs
```c
/* Бар'єри компілятора та ядра на C */
static inline uint32_t read_dwt_cycles_barrier(void) {
    __asm volatile ("" ::: "memory"); /* Заборона перестановки компілятором */
    __DSB();                          /* Data Synchronization Barrier */
    __ISB();                          /* Instruction Synchronization Barrier */
    uint32_t val = DWT_CYCCNT;
    __asm volatile ("" ::: "memory");
    return val;
}
```
```cpp
// Бар'єри компілятора та ядра на C++20
#include <atomic>

inline uint32_t read_dwt_cycles_barrier() noexcept {
    std::atomic_signal_fence(std::memory_order_seq_cst);
    asm volatile("dsb 0xF" ::: "memory");
    asm volatile("isb 0xF" ::: "memory");
    const uint32_t val = *reinterpret_cast<volatile uint32_t*>(0xE0001004U);
    std::atomic_signal_fence(std::memory_order_seq_cst);
    return val;
}
```
:::

### 2. Сплячі режими процесора (WFI / WFE)

Під час переходу процесора в енергозберігаючі режими `Sleep` або `Stop` (інструкція `WFI` — Wait For Interrupt) тактування ядра `HCLK` вимикається, і лічильник `DWT->CYCCNT` зупиняє лік. Якщо система використовує безтіковий режим очікування RTOS (Tickless Idle), час перебування у сні не додаватиметься до загального часу функцій, що призведе до занижених результатів загального часу. Для точного обліку тривалості сну використовують окремий апаратний лічильник `DWT->SLEEPCNT`.

### 3. Атомарність оновлення 64-бітних накопичувачів

Поле `total_cyc` має розрядність 64 біти. На 32-розрядному ядрі Cortex-M читання та запис такого поля виконується за дві окремі інструкції. Якщо високорівневий потік зчитує звіт статистики під час оновлення поля з переривання, він може прочитати частково оновлене значення. Усі операції зчитування агрегованих структур у мультизадачному середовищі мають виконуватися із захистом критичною секцією або через атомарні копії.
