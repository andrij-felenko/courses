# ⚙️ Драйвер критичних секцій та RAII-вартові для Cortex-M

У складних вбудованих системах керування даними одночасно обмінюються десятки апаратних переривань, таймерних подій і фонових завдань операційної системи реального часу. Якщо функція оновлює кільцевий буфер зв'язку, калібрувальні коефіцієнти чи стан кінцевого автомата приводу, вона мусить тимчасово заблокувати асинхронне виконання переривань для збереження узгодженості пам'яті. 

Проте ручне керування прапорцями переривань через функції `__disable_irq()` та `__enable_irq()` неминуче призводить до двох типових фатальних відмов:
1. **Порушення вкладеності:** виклик допоміжної функції знімає глобальне блокування завчасно, залишаючи решту зовнішньої критичної секції повністю незахищеною.
2. **Витік блокування:** достроковий вихід із функції через `return` у разі виявлення помилки залишає переривання вимкненими назавжди, що призводить до мертвого зависання мікроконтролера.

Нижче наведено закінчений, виробничий модульний драйвер критичних секцій для процесорів ARM Cortex-M із повною підтримкою довільної глибини вкладеності, селективного маскування за пріоритетом (BASEPRI), діагностики контексту виконання, профілювання тривалості, врахування кеш-пам'яті Cortex-M7 та ідіоматичними C++20 RAII-вартовими нульової вартості.

## Архітектурний контракт драйвера

Драйвер спроєктовано за принципом абстракції нульової вартості (англ. *Zero-Cost Abstraction*): усі функції та методи є інлайновими, без динамічного виділення пам'яті чи віртуальних таблиць викликів, і транслюються компілятором у 3–4 асемблерні інструкції.

Драйвер надає два альтернативні механізми захисту:

1. **Глобальне маскування (PRIMASK):** блокує всі масковані апаратні переривання мікроконтролера. Цей механізм є універсальним і підтримується абсолютно всіма ядрами архітектури ARM Cortex-M (Cortex-M0, M0+, M3, M4, M7, M23, M33).
2. **Селективне маскування за пріоритетом (BASEPRI):** блокує лише переривання з пріоритетом, чисельно більшим або рівним за встановлений поріг (наприклад, переривання системних драйверів і планувальника FreeRTOS). Швидкі переривання прямого керування апаратурою (Zero-Latency ISR) продовжують виконуватися без жодних затримок. Підтримується на ядрах Cortex-M3, M4, M7 та M33.

Для обох механізмів реалізовано збереження попереднього стану регістра маски при вході та точне відновлення при виході, що усуває взаємний вплив вкладених блоків коду.

## Реалізація модуля мовами C та C++

:::tabs
```c
#ifndef CRITICAL_SECTION_H
#define CRITICAL_SECTION_H

#include <stdint.h>
#include <stdbool.h>

#if defined(__ARMCC_VERSION) || defined(__GNUC__)
    #include "cmsis_compiler.h"
#else
    #error "Непідтримуваний компілятор: потрібна підтримка CMSIS intrinsics"
#endif

/*
 * Бар'єр оптимізації компілятора:
 * Забороняє компілятору переставляти операції читання/запису пам'яті
 * через межі критичної секції під час оптимізації (-O2, -O3, -Os).
 */
#define CRITICAL_MEMORY_BARRIER() __asm volatile("" ::: "memory")

/* ========================================================================= */
/* 1. Глобальна критична секція на основі PRIMASK (Cortex-M0/M0+/M3/M4/M7/M33) */
/* ========================================================================= */

typedef struct {
    uint32_t primask_state;
} critical_section_t;

static inline critical_section_t critical_section_enter(void) {
    critical_section_t cs;
    cs.primask_state = __get_PRIMASK();
    __disable_irq();
    CRITICAL_MEMORY_BARRIER();
    return cs;
}

static inline void critical_section_exit(critical_section_t cs) {
    CRITICAL_MEMORY_BARRIER();
    __set_PRIMASK(cs.primask_state);
}

/* ========================================================================= */
/* 2. Пріоритетна критична секція на основі BASEPRI (Cortex-M3/M4/M7/M33)   */
/* ========================================================================= */

#if (__CORTEX_M >= 3U) || defined(__ARM_ARCH_7M__) || defined(__ARM_ARCH_7EM__) || defined(__ARM_ARCH_8M_MAIN__)

typedef struct {
    uint32_t basepri_state;
} priority_critical_section_t;

/*
 * Вхід у критичну секцію із маскуванням переривань з пріоритетом >= max_syscall_prio.
 * max_syscall_prio має бути попередньо зміщеним у старші біти (наприклад, 0x50 для пріоритету 5 при 4 бітах NVIC).
 */
static inline priority_critical_section_t priority_critical_section_enter(uint8_t max_syscall_prio) {
    priority_critical_section_t pcs;
    pcs.basepri_state = __get_BASEPRI();
    /*
     * __set_BASEPRI_MAX встановлює нове значення лише якщо воно підвищує рівень маскування
     * (тобто задає суворіший поріг, ніж поточний), що запобігає випадковому розмаскуванню.
     */
    __set_BASEPRI_MAX(max_syscall_prio);
    CRITICAL_MEMORY_BARRIER();
    return pcs;
}

static inline void priority_critical_section_exit(priority_critical_section_t pcs) {
    CRITICAL_MEMORY_BARRIER();
    __set_BASEPRI(pcs.basepri_state);
}

#endif /* Cortex-M3+ */

/* ========================================================================= */
/* 3. Діагностика контексту виконання (Thread чи ISR)                        */
/* ========================================================================= */

static inline bool in_interrupt_context(void) {
    return (__get_IPSR() != 0U);
}

#endif /* CRITICAL_SECTION_H */
```
```cpp
#pragma once

#include <cstdint>
#include <concepts>
#include <type_traits>

#if defined(__ARMCC_VERSION) || defined(__GNUC__)
    #include "cmsis_compiler.h"
#else
    #error "Непідтримуваний компілятор: потрібна підтримка CMSIS intrinsics"
#endif

namespace embedded::sync {

// Бар'єр оптимізації компілятора
inline void memory_barrier() noexcept {
    __asm volatile("" ::: "memory");
}

// Діагностика контексту: перевірка, чи код виконується в обробнику переривання
[[nodiscard]] inline bool in_interrupt_context() noexcept {
    return (__get_IPSR() != 0U);
}

/* ========================================================================= */
/* 1. Політика блокування через PRIMASK (Глобальне вимкнення IRQ)           */
/* ========================================================================= */

class PrimaskLockPolicy {
public:
    using StateType = std::uint32_t;

    [[nodiscard]] static StateType enter() noexcept {
        const StateType state = __get_PRIMASK();
        __disable_irq();
        memory_barrier();
        return state;
    }

    static void exit(StateType state) noexcept {
        memory_barrier();
        __set_PRIMASK(state);
    }
};

/* ========================================================================= */
/* 2. Політика блокування через BASEPRI (Маскування за порогом пріоритету)   */
/* ========================================================================= */

#if (__CORTEX_M >= 3U) || defined(__ARM_ARCH_7M__) || defined(__ARM_ARCH_7EM__) || defined(__ARM_ARCH_8M_MAIN__)

template <std::uint8_t MaxSyscallPriority>
class BasepriLockPolicy {
public:
    using StateType = std::uint32_t;

    [[nodiscard]] static StateType enter() noexcept {
        const StateType state = __get_BASEPRI();
        __set_BASEPRI_MAX(MaxSyscallPriority);
        memory_barrier();
        return state;
    }

    static void exit(StateType state) noexcept {
        memory_barrier();
        __set_BASEPRI(state);
    }
};

#endif

/* ========================================================================= */
/* 3. Універсальний RAII-вартовий критичної секції (Critical Section Guard) */
/* ========================================================================= */

template <typename Policy = PrimaskLockPolicy>
class [[nodiscard]] CriticalSectionGuard {
public:
    CriticalSectionGuard() noexcept 
        : saved_state_(Policy::enter()) {}

    ~CriticalSectionGuard() noexcept {
        Policy::exit(saved_state_);
    }

    // Заборона копіювання та переміщення: вартовий жорстко прив'язаний до поточного стекового фрейму
    CriticalSectionGuard(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard(CriticalSectionGuard&&) = delete;
    CriticalSectionGuard& operator=(CriticalSectionGuard&&) = delete;

private:
    typename Policy::StateType saved_state_;
};

// Зручний псевдонім для стандартного глобального захисту
using IrqGuard = CriticalSectionGuard<PrimaskLockPolicy>;

#if (__CORTEX_M >= 3U) || defined(__ARM_ARCH_7M__) || defined(__ARM_ARCH_7EM__) || defined(__ARM_ARCH_8M_MAIN__)
template <std::uint8_t PriorityThreshold>
using PriorityGuard = CriticalSectionGuard<BasepriLockPolicy<PriorityThreshold>>;
#endif

/* ========================================================================= */
/* 4. Адаптер під стандартний концепт BasicLockable (std::lock_guard)        */
/* ========================================================================= */

class InterruptSpinLock {
public:
    void lock() noexcept {
        saved_state_ = PrimaskLockPolicy::enter();
    }

    void unlock() noexcept {
        PrimaskLockPolicy::exit(saved_state_);
    }

private:
    std::uint32_t saved_state_{0};
};

} // namespace embedded::sync
```
:::

## Практичний приклад застосування: багатопотоковий модуль навігації

Розглянемо практичний приклад: безпечне оновлення телеметричного пакету даних навігаційного контролера безпілотного апарата. 

Структура містить широту, довготу, висоту та 64-бітну часову мітку з точністю до мікросекунд. Дані вичитуються для радіопередачі у фоновому потоці головного циклу й оновлюються в обробнику переривання GNSS-модуля або таймера з частотою 100 Гц.

:::tabs
```c
#include "critical_section.h"
#include <string.h>

typedef struct {
    int32_t  latitude;
    int32_t  longitude;
    int32_t  altitude_mm;
    uint64_t timestamp_us;
} navigation_data_t;

static navigation_data_t g_nav_data;

/* Оновлення даних: може викликатися з будь-якого контексту */
void navigation_update(int32_t lat, int32_t lon, int32_t alt, uint64_t ts) {
    critical_section_t cs = critical_section_enter();
    
    g_nav_data.latitude = lat;
    g_nav_data.longitude = lon;
    g_nav_data.altitude_mm = alt;
    g_nav_data.timestamp_us = ts;
    
    critical_section_exit(cs);
}

/* Безпечне копіювання узгодженого знімка структури */
bool navigation_get_snapshot(navigation_data_t *out_data) {
    if (out_data == NULL) {
        return false;
    }
    
    critical_section_t cs = critical_section_enter();
    *out_data = g_nav_data; // Атомарне копіювання всіх полів без ризику розриву
    critical_section_exit(cs);
    
    return true;
}
```
```cpp
#include "critical_section.hpp"
#include <optional>

struct NavigationData {
    std::int32_t  latitude{0};
    std::int32_t  longitude{0};
    std::int32_t  altitude_mm{0};
    std::uint64_t timestamp_us{0};
};

class NavigationManager {
public:
    void update(std::int32_t lat, std::int32_t lon, std::int32_t alt, std::uint64_t ts) noexcept {
        // RAII-вартовий: автоматично знімає блокування при виході з методу
        const embedded::sync::IrqGuard lock;
        
        data_.latitude = lat;
        data_.longitude = lon;
        data_.altitude_mm = alt;
        data_.timestamp_us = ts;
    }

    [[nodiscard]] NavigationData get_snapshot() const noexcept {
        const embedded::sync::IrqGuard lock;
        return data_; // Повернення захищеної копії об'єкта
    }

private:
    NavigationData data_{};
};
```
:::

## Інтеграція з FreeRTOS: безпечні критичні секції в задачах та ISR

У проектах під керуванням FreeRTOS виклик критичної секції залежить від контексту, у якому виконується код. Якщо викликати стандартний макрос `taskENTER_CRITICAL()` зсередини обробника переривання, операційна система викличе аварійне спрацювання асерту `configASSERT()`. 

Для обробників переривань FreeRTOS вимагає використання пари `taskENTER_CRITICAL_FROM_ISR()` та `taskEXIT_CRITICAL_FROM_ISR()`.

За допомогою C++20 та функції `in_interrupt_context()` ми можемо побудувати універсального контекстно-незалежного вартового:

:::tabs
```c
#include "critical_section.h"
#include "FreeRTOS.h"
#include "task.h"

/* Контекстно-незалежний вхід у критичну секцію FreeRTOS */
typedef struct {
    bool is_isr;
    UBaseType_t isr_state;
} rtos_critical_t;

static inline rtos_critical_t rtos_critical_enter(void) {
    rtos_critical_t rc;
    rc.is_isr = in_interrupt_context();
    if (rc.is_isr) {
        rc.isr_state = taskENTER_CRITICAL_FROM_ISR();
    } else {
        taskENTER_CRITICAL();
        rc.isr_state = 0;
    }
    return rc;
}

static inline void rtos_critical_exit(rtos_critical_t rc) {
    if (rc.is_isr) {
        taskEXIT_CRITICAL_FROM_ISR(rc.isr_state);
    } else {
        taskEXIT_CRITICAL();
    }
}
```
```cpp
#include "critical_section.hpp"
#include "FreeRTOS.h"
#include "task.h"

namespace embedded::rtos {

class [[nodiscard]] FreeRtosGuard {
public:
    FreeRtosGuard() noexcept : is_isr_(sync::in_interrupt_context()) {
        if (is_isr_) {
            isr_saved_state_ = taskENTER_CRITICAL_FROM_ISR();
        } else {
            taskENTER_CRITICAL();
        }
    }

    ~FreeRtosGuard() noexcept {
        if (is_isr_) {
            taskEXIT_CRITICAL_FROM_ISR(isr_saved_state_);
        } else {
            taskEXIT_CRITICAL();
        }
    }

    FreeRtosGuard(const FreeRtosGuard&) = delete;
    FreeRtosGuard& operator=(const FreeRtosGuard&) = delete;

private:
    bool is_isr_{false};
    UBaseType_t isr_saved_state_{0};
};

} // namespace embedded::rtos
```
:::

## Профілювання тривалості критичної секції через DWT

Найважливіша вимога до критичної секції в системах реального часу — детермінований і мінімальний час блокування. Якщо критична секція триває довше, ніж дозволяє бюджет латентності найшвидшого переривання, це призводить до зриву часових параметрів.

Для діагностики тривалості критичних секцій на мікроконтролерах Cortex-M3/M4/M7/M33 застосовують апаратний лічильник тактів підсистеми зневадження DWT (англ. *Data Watchpoint and Trace*, регістр `DWT->CYCCNT`).

:::tabs
```c
#include "critical_section.h"
#include "core_cm4.h"

/* Максимально допустима тривалість критичної секції (у тактах ядра) */
#define MAX_ALLOWED_CRITICAL_CYCLES  50U

static inline void profile_critical_section(void) {
    /* 1. Ініціалізація DWT лічильника тактів (виконується один раз при старті) */
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    uint32_t start_cycles = DWT->CYCCNT;
    
    critical_section_t cs = critical_section_enter();
    
    /* Робота зі спільним ресурсом */
    g_nav_data.latitude += 10;
    
    critical_section_exit(cs);
    
    uint32_t elapsed = DWT->CYCCNT - start_cycles;
    
    if (elapsed > MAX_ALLOWED_CRITICAL_CYCLES) {
        /* Фіксація перевищення бюджету латентності: запис у журнал або breakpoint */
        __BKPT(0);
    }
}
```
```cpp
#include "critical_section.hpp"
#include "core_cm4.h"
#include <concepts>

namespace embedded::debug {

class CriticalSectionProfiler {
public:
    static void init() noexcept {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    }

    template <std::uint32_t MaxCycles, typename Callable>
    static void run_monitored(Callable&& action) noexcept {
        const std::uint32_t start_cycles = DWT->CYCCNT;
        
        {
            const sync::IrqGuard lock;
            action();
        }
        
        const std::uint32_t elapsed = DWT->CYCCNT - start_cycles;
        if (elapsed > MaxCycles) {
            __BKPT(0); // Зупинка зневаджувача при перевищенні ліміту
        }
    }
};

} // namespace embedded::debug
```
:::

## Особливості роботи з кеш-пам'яттю на Cortex-M7

На високопродуктивних ядрах Cortex-M7 мікроконтролер має апаратний кеш інструкцій (I-Cache) та кеш даних (D-Cache). Якщо критична секція виконує оновлення буфера, який одночасно передається периферійним контролером прямого доступу до пам'яті (DMA), простого вимкнення переривань недостатньо.

Оскільки процесор може записати нові дані у швидкий L1 D-Cache без негайного скидання на системну шину AXI, контролер DMA зчитає застарілі байти безпосередньо з фізичного ОЗП. У таких випадках перед виходом із критичної секції необхідно виконати операцію інвалідації або скидання кешу даних CMSIS-функцією `SCB_CleanDCache_by_Addr()` або розміщувати спільні буфери в некешованій ділянці пам'яті DTCM (Data Tightly-Coupled Memory).

## Тестування критичних секцій на комп'ютері розробника (Host Mocking)

Під час написання кросплатформних модульних тестів (Unit Tests) для виконання на робочій станції (x86_64 Linux або Windows) прямий виклик інструкцій ARM `CPSID`/`PRIMASK` неможливий.

Для тестування бізнес-логіки драйвера створюють заголовок-заглушку (Mock Policy), що емулює апаратне блокування за допомогою стандартних атоміків C++:

:::tabs
```c
#ifndef MOCK_CMSIS_COMPILER_H
#define MOCK_CMSIS_COMPILER_H

#include <stdint.h>
#include <stdbool.h>

/* Глобальні лічильники викликів для перевірки у тестах */
extern uint32_t g_mock_primask_state;
extern uint32_t g_mock_disable_irq_calls;
extern uint32_t g_mock_enable_irq_calls;

static inline uint32_t __get_PRIMASK(void) {
    return g_mock_primask_state;
}

static inline void __set_PRIMASK(uint32_t state) {
    g_mock_primask_state = state;
}

static inline void __disable_irq(void) {
    g_mock_disable_irq_calls++;
    g_mock_primask_state = 1U;
}

static inline void __enable_irq(void) {
    g_mock_enable_irq_calls++;
    g_mock_primask_state = 0U;
}

static inline uint32_t __get_IPSR(void) {
    return 0U; // Емуляція Thread Mode
}

#endif /* MOCK_CMSIS_COMPILER_H */
```
```cpp
#pragma once

#include <cstdint>
#include <atomic>

namespace embedded::mock {

class HostMockLockPolicy {
public:
    using StateType = std::uint32_t;

    static inline std::atomic<std::uint32_t> lock_count{0};
    static inline std::atomic<bool> is_locked{false};

    [[nodiscard]] static StateType enter() noexcept {
        const StateType prev = is_locked.exchange(true) ? 1U : 0U;
        ++lock_count;
        return prev;
    }

    static void exit(StateType state) noexcept {
        is_locked.store(state != 0U);
    }

    static void reset() noexcept {
        lock_count.store(0);
        is_locked.store(false);
    }
};

} // namespace embedded::mock
```
:::

Така модульна структура дозволяє перевірити коректність роботи алгоритмів кільцевих буферів та пакетних парсерів у середовищі безперервної інтеграції (CI/CD) на звичайних x86 серверах без підключення фізичної плати розробника.

## Інженерний аналіз згенерованого асемблерного коду

Компілятор GCC з рівнем оптимізації `-O2` транслює C++ метод `update` у наступну компактну послідовність машинних інструкцій Thumb-2:

```asm
navigation_update:
    MRS     r12, PRIMASK      ; r12 = зберегти поточний стан PRIMASK (1 такт)
    CPSID   i                 ; Глобально вимкнути масковані переривання (1 такт)
    
    ; --- Тіло критичної секції ---
    LDR     r3, =g_nav_data
    STR     r0, [r3, #0]      ; latitude
    STR     r1, [r3, #4]      ; longitude
    STR     r2, [r3, #8]      ; altitude_mm
    STRD    r4, r5, [r3, #16] ; timestamp_us (64-бітний запис)
    
    ; --- Вихід з критичної секції (деструктор RAII) ---
    MSR     PRIMASK, r12      ; Відновити попередній стан маски (1 такт)
    BX      LR                ; Повернення з функції
```

Згенерований лістинг демонструє ключову властивість RAII-вартого: накладні витрати на вхід і вихід становлять рівно **3 такти процесора** (`MRS`, `CPSID`, `MSR`). Усі конструктори та деструктори повністю заінлайнено, жоден байт пам'яті не виділяється на стеку динамічно, а компіляторний бар'єр пам'яті гарантує, що інструкції збереження `STR` виконуються строго між `CPSID` та `MSR`.
