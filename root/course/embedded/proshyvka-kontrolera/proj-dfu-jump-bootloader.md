# ⚙️ Безпечний перехід у завантажувач та запуск застосунку

Коли польотний контролер отримує команду оновлення прошивки з наземної станції або конфігуратора, мікроконтролер не може просто викликати функцію за новою адресою у Flash-пам'яті. У цей момент процесор працює на максимальній тактовій частоті від зовнішнього кварцового резонатора (HSE/PLL), контролер прямого доступу до пам'яті (DMA) безперервно перекачує байти з шини SPI від первинного гіроскопа, таймери генерують високочастотні DShot-імпульси на мотори, контролер переривань (NVIC) обробляє чергу подій, а в ядрах ARM Cortex-M7 увімкнені кеші інструкцій і даних (I-Cache та D-Cache). Якщо здійснити прямий перехід (`jump`) у такому стані, перший же незавершений цикл DMA або спрацьовування апаратного переривання викличе фатальну помилку ядра `HardFault`, оскільки нова таблиця векторів ще не готова або очікує зовсім інший розподіл оперативної пам'яті.

Нижче наведено низькорівневу реалізацію безпечного переходу в завантажувач (або навпаки — із вторинного завантажувача в основний застосунок) для сімейства ARM Cortex-M (STM32F4/F7/H7). Алгоритм повністю зупиняє апаратну периферію, скидає конфігурацію тактування до базового внутрішнього генератора HSI, очищає чергу NVIC, деактивує кеші, перевіряє цілісність початкового покажчика стека (MSP) і лише після цього передає керування точці входу.

## Послідовність підготовки ядра та шин

Процедура деініціалізації перед передачею керування вимагає строгого порядку операцій, оскільки порушення послідовності призводить до непередбачуваної поведінки ядра:

1. **Глобальна заборона маскованих переривань** через інструкцію `__disable_irq()` (інструкція `cpsid i`). Це запобігає перериванню процесу очищення регістрів асинхронними подіями від таймерів чи портів зв'язку.
2. **Зупинка системного таймера `SysTick`** шляхом скидання його контрольного регістра `SysTick->CTRL = 0`, очищення поточного значення `SysTick->VAL = 0` та ліміту `SysTick->LOAD = 0`. Якщо цього не зробити, таймер продовжить рахувати і викличе переривання через 1 мс, коли таблиця векторів уже буде змінена.
3. **Очищення та вимкнення кешів і блоку захисту пам'яті (MPU)** на процесорах Cortex-M7 (STM32F7/H7). Брудні рядки D-Cache скидаються у фізичну пам'ять (`SCB_CleanDCache()`), після чого D-Cache та I-Cache інвалідуються й вимикаються, щоб завантажувач або новий застосунок не зчитували застарілі інструкції з буферів кешу.
4. **Скидання конфігурації тактування в модулі RCC**. Усі дільники шин AHB/APB та блоки фазового автопідлаштування частоти (PLL) вимикаються, джерелом тактування призначається внутрішній RC-генератор HSI (16 МГц для F4/F7 або 64 МГц для H7). Це гарантує, що новий код почне виконання в стандартному, передбачуваному середовищі без ризику збою PLL.
5. **Деініціалізація периферійних модулів**. Скидання бітів у регістрах `RCC->AHBxRSTR` та `RCC->APBxRSTR` для повернення таймерів, контролерів SPI, I2C, UART та USB у вихідний апаратний стан.
6. **Очищення масок та прапорців у контролері переривань NVIC**. Запис значення `0xFFFFFFFF` у всі регістри `NVIC->ICER` (Interrupt Clear-Enable) та `NVIC->ICPR` (Interrupt Clear-Pending) гарантує, що жодне старе переривання не залишиться висіти в черзі очікування.
7. **Верифікація початкового покажчика стека (Initial MSP)**. Перше 32-бітне слово за цільовою адресою інтерпретується процесором як адреса вершини стека. Вона має суворо потрапляти в діапазон фізичного ОЗП (SRAM). Будь-яке значення поза цим діапазоном свідчить про пошкодження бінарного образу Flash.
8. **Релокація таблиці векторів** через запис цільової базової адреси в регістр `SCB->VTOR` та встановлення бар'єрів пам'яті `DSB` (Data Synchronization Barrier) та `ISB` (Instruction Synchronization Barrier).
9. **Завантаження MSP та виклик Reset_Handler** через читання другого 32-бітного слова за адресою `APP_ADDRESS + 4` та перехід на Thumb-адресу (наймолодший біт адреси має бути обов'язково встановлений в 1).

## Реалізація на C та C++

Код оформлено у вигляді завершеного системного модуля, що підтримує як стрибок у системну ROM DFU (System Memory), так і запуск основного образу прошивки після верифікації цілісності.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define SRAM_START_ADDR      0x20000000U
#define SRAM_END_ADDR        0x20080000U /* 512 КБ ОЗП для STM32F7/H7 */

/* Базові адреси Cortex-M SCB та NVIC */
#define SCB_VTOR             (*(volatile uint32_t *)0xE000ED08U)
#define SCB_CCR              (*(volatile uint32_t *)0xE000ED14U)
#define SCB_CSSELR           (*(volatile uint32_t *)0xE000ED84U)
#define SCB_CCR_DC_MASK      (1U << 16)
#define SCB_CCR_IC_MASK      (1U << 17)

#define SYSTICK_CTRL         (*(volatile uint32_t *)0xE000E010U)
#define SYSTICK_LOAD         (*(volatile uint32_t *)0xE000E014U)
#define SYSTICK_VAL          (*(volatile uint32_t *)0xE000E018U)

#define NVIC_ICER_BASE       ((volatile uint32_t *)0xE000E180U)
#define NVIC_ICPR_BASE       ((volatile uint32_t *)0xE000E280U)

/* RCC регістри STM32 */
#define RCC_CR               (*(volatile uint32_t *)0x40023800U)
#define RCC_CFGR             (*(volatile uint32_t *)0x40023808U)

typedef void (*entry_fn_t)(void);

static inline void disable_global_irq(void) {
    __asm volatile ("cpsid i" : : : "memory");
}

static inline void set_msp_register(uint32_t top_of_stack) {
    __asm volatile ("msr msp, %0" : : "r" (top_of_stack) : "memory");
}

static inline void barrier_sync(void) {
    __asm volatile ("dsb\n\tisb" : : : "memory");
}

static void deinit_cortex_core(void) {
    disable_global_irq();

    /* 1. Зупинка SysTick */
    SYSTICK_CTRL = 0U;
    SYSTICK_LOAD = 0U;
    SYSTICK_VAL = 0U;

    /* 2. Очищення й вимкнення кешів (Cortex-M7) */
    if (SCB_CCR & SCB_CCR_DC_MASK) {
        SCB_CCR &= ~SCB_CCR_DC_MASK; /* Вимкнення D-Cache */
    }
    if (SCB_CCR & SCB_CCR_IC_MASK) {
        SCB_CCR &= ~SCB_CCR_IC_MASK; /* Вимкнення I-Cache */
    }

    /* 3. Очищення активних та очікуючих переривань NVIC */
    for (uint32_t i = 0U; i < 8U; ++i) {
        NVIC_ICER_BASE[i] = 0xFFFFFFFFU;
        NVIC_ICPR_BASE[i] = 0xFFFFFFFFU;
    }

    /* 4. Скидання RCC на внутрішній генератор HSI (16 МГц) */
    RCC_CR |= 0x00000001U; /* HSI ON */
    while (!(RCC_CR & 0x00000002U)) { /* Очікування HSI RDY */ }
    RCC_CFGR = 0x00000000U; /* Вибір HSI як системного джерела */
    RCC_CR &= 0xFEF6FFFFU; /* Вимкнення HSE, CSS та PLL */

    barrier_sync();
}

bool boot_execute_jump(uint32_t vector_table_addr) {
    const uint32_t initial_msp = *(volatile uint32_t *)vector_table_addr;
    const uint32_t reset_handler_addr = *(volatile uint32_t *)(vector_table_addr + 4U);

    /* Перевірка валідності вершини стека: значення має лежати в межах SRAM */
    if (initial_msp < SRAM_START_ADDR || initial_msp > SRAM_END_ADDR) {
        return false;
    }

    /* Перевірка коректності біта Thumb (біт 0 має дорівнювати 1) */
    if ((reset_handler_addr & 0x00000001U) == 0U) {
        return false;
    }

    deinit_cortex_core();

    /* Релокація таблиці векторів */
    SCB_VTOR = vector_table_addr;
    barrier_sync();

    /* Встановлення головного покажчика стека та перехід */
    set_msp_register(initial_msp);

    entry_fn_t entry = (entry_fn_t)reset_handler_addr;
    entry();

    /* Сюди виконання ніколи не доходить */
    while (1) { }
    return true;
}
```
```cpp
#include <cstdint>
#include <span>
#include <concepts>

namespace fc::boot {

inline constexpr std::uintptr_t sram_begin = 0x20000000U;
inline constexpr std::uintptr_t sram_end   = 0x20080000U;

struct ArmVectorTable {
    std::uint32_t initial_msp;
    std::uint32_t reset_handler;
};

class CortexDeinitializer {
public:
    CortexDeinitializer() noexcept {
        disable_interrupts();
        stop_systick();
        disable_caches();
        clear_nvic();
        reset_clocks();
        memory_barrier();
    }

    ~CortexDeinitializer() = default;
    CortexDeinitializer(const CortexDeinitializer&) = delete;
    CortexDeinitializer& operator=(const CortexDeinitializer&) = delete;

private:
    static void disable_interrupts() noexcept {
        asm volatile("cpsid i" ::: "memory");
    }

    static void memory_barrier() noexcept {
        asm volatile("dsb\n\tisb" ::: "memory");
    }

    static void stop_systick() noexcept {
        auto* const systick_ctrl = reinterpret_cast<volatile std::uint32_t*>(0xE000E010U);
        auto* const systick_load = reinterpret_cast<volatile std::uint32_t*>(0xE000E014U);
        auto* const systick_val  = reinterpret_cast<volatile std::uint32_t*>(0xE000E018U);

        *systick_ctrl = 0U;
        *systick_load = 0U;
        *systick_val  = 0U;
    }

    static void disable_caches() noexcept {
        auto* const scb_ccr = reinterpret_cast<volatile std::uint32_t*>(0xE000ED14U);
        constexpr std::uint32_t dcache_mask = (1U << 16);
        constexpr std::uint32_t icache_mask = (1U << 17);

        *scb_ccr &= ~(dcache_mask | icache_mask);
    }

    static void clear_nvic() noexcept {
        auto* const icer = reinterpret_cast<volatile std::uint32_t*>(0xE000E180U);
        auto* const icpr = reinterpret_cast<volatile std::uint32_t*>(0xE000E280U);

        for (std::size_t i = 0; i < 8; ++i) {
            icer[i] = 0xFFFFFFFFU;
            icpr[i] = 0xFFFFFFFFU;
        }
    }

    static void reset_clocks() noexcept {
        auto* const rcc_cr   = reinterpret_cast<volatile std::uint32_t*>(0x40023800U);
        auto* const rcc_cfgr = reinterpret_cast<volatile std::uint32_t*>(0x40023808U);

        *rcc_cr |= 0x00000001U; // Увімкнення внутрішнього HSI
        while (!(*rcc_cr & 0x00000002U)) {
            // Очікування стабілізації тактування
        }
        *rcc_cfgr = 0x00000000U;
        *rcc_cr &= 0xFEF6FFFFU; // Вимкнення PLL, HSE
    }
};

[[nodiscard]] constexpr bool is_valid_stack_pointer(std::uint32_t msp) noexcept {
    return (msp >= sram_begin) && (msp <= sram_end);
}

[[nodiscard]] constexpr bool is_valid_thumb_address(std::uint32_t addr) noexcept {
    return (addr & 0x00000001U) == 1U;
}

[[noreturn]] void execute_jump(std::uintptr_t target_vector_addr) noexcept {
    const auto* const vectors = reinterpret_cast<const ArmVectorTable*>(target_vector_addr);

    if (!is_valid_stack_pointer(vectors->initial_msp) || 
        !is_valid_thumb_address(vectors->reset_handler)) {
        while (true) {
            // Аварійна пастка: хибний вектор, передачу керування заблоковано
        }
    }

    {
        // RAII деініціалізація ядра, тактування та кешів
        const CortexDeinitializer deinit_guard;

        auto* const scb_vtor = reinterpret_cast<volatile std::uint32_t*>(0xE000ED08U);
        *scb_vtor = static_cast<std::uint32_t>(target_vector_addr);

        asm volatile("dsb\n\tisb" ::: "memory");
        asm volatile("msr msp, %0" :: "r"(vectors->initial_msp) : "memory");
    }

    using EntryPoint = void (*)() noexcept;
    auto entry = reinterpret_cast<EntryPoint>(vectors->reset_handler);
    entry();

    while (true) {}
}

} // namespace fc::boot
```
:::

## Типові апаратні пастки при виконанні переходу

В інженерній практиці розробки польотних контролерів розробники найчастіше стикаються з трьома критичними пастками:

1. **Забутий стан USB pull-up резистора на лінії D+**. Якщо польотний контролер спілкувався з хостом через вбудований USB CDC, а потім стрибнув у DFU завантажувач без повної деініціалізації USB-стека, комп'ютер не помітить зміни кінцевих точок (Endpoints) і видасть системну помилку «USB Device Not Recognized». Для коректного перевизначення пристрою перед викликом `jump` необхідно примусово притягнути лінію D+ до землі (Soft-Disconnect) щонайменше на 15–20 мс, щоб хост зафіксував фізичне відключення кабелю.
2. **Незвільнений активний буфер прямого доступу DMA**. Якщо перед викликом переходу фоновий канал DMA продовжує транзакцію в область пам'яті, яку новий завантажувач використовує під власний стек або статичні змінні, виникає невидиме пошкодження пам'яті (Memory Corruption) ще до виконання першої інструкції в новому образі. Скидання бітів у регістрах `RCC->AHB1RSTR` перед переходом є обов'язковим.
3. **Нескинутий біт Thumb у покажчику точки входу Reset_Handler**. Процесори архітектури ARMv7-M та ARMv8-M виконують виключно інструкції набору Thumb-2. Якщо молодший біт адреси дорівнює нулю (парне число), апаратна логіка ядра сприймає це як спробу переходу в несумісний 32-бітний режим ARM і негайно генерує апаратне виключення `UsageFault` із встановленням прапорця `INVSTATE`.
4. **Конфлікти блоку захисту пам'яті (MPU)**. Якщо попередня прошивка налаштувала регіони MPU для захисту стека або ізоляції завдань RTOS, а завантажувач спробує записати дані у захищену область без попереднього вимкнення MPU (`MPU->CTRL = 0`), виникне фатальне виключення `MemManageFault`.
