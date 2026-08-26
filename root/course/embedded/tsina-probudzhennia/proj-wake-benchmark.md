# ⚙️ Практикум: мікросекундний профільовник пробудження та вимірювання енергії

Цей проект надає завершений код вимірювального драйвера та стендову методику точного профілювання фаз пробудження мікроконтролера за допомогою апаратних GPIO-маркерів і лічильника тактів DWT, без яких неможливо перевірити реальні часові інтервали стабілізації заліза та розрахувати фактичну ціну виходу зі сну.

## 1. Постановка задачі та апаратна схема

Для об'єктивного енергетичного аудиту нам необхідно виміряти точну тривалість чотирьох послідовних фаз:
1. `t_wake`: від моменту спрацьовування апаратного переривання/таймера до першої виконуваної інструкції процесора;
2. `t_rail`: від увімкнення ключа живлення давача (Load Switch) та запуску буфера опорної напруги VREFBUF до виходу аналогового тракту на стабільний рівень;
3. `t_adc`: час прогріву, вибірки та оцифрування аналогового сигналу 12-бітним АЦП (16 вибірок з апаратним усередненням);
4. `t_sleep`: час збереження накопиченого результату в збережену пам'ять (Retention RAM) та конфігурації мікроконтролера перед повторним зануренням у глибокий сон (Stop 2).

Вимірювання здійснюється двома синхронізованими каналами:
- **Канал 1 (цифровий логічний аналізатор / осцилограф):** підключений до діагностичних виводів `GPIO_MARKER_0` (загальний статус активності CPU) та `GPIO_MARKER_1` (строб готовності аналогової частини).
- **Канал 2 (осцилограф через струмовий шунт 10 Ом або прецизійний вимірювач струму):** фіксація миттєвого профілю струму `I(t)` у ланцюзі живлення всієї плати.

```
                  ┌───────────────────────────────┐
                  │    STM32 / Cortex-M4 MCU      │
                  │                               │
                  │  [Pin PA0] ───► MARKER 0 (CPU Active)
                  │  [Pin PA1] ───► MARKER 1 (Sensor Power)
                  │  [Pin PA2] ───► Load Switch EN ──┐
                  │                                  │
                  │  [Retention SRAM: 4 KB]          │
                  │  • Кільцевий буфер вимірів       │
                  │  • Лічильник пробуджень          │
                  └──────────────────────────────────┘
                                                     │
                                                     ▼
                                          ┌──────────────────────┐
                                          │ P-MOSFET Load Switch │
                                          └──────────┬───────────┘
                                                     │ VDD_SENS
                                                     ▼
                                          ┌──────────────────────┐
                                          │ Давач / АЦП-тракт    │
                                          └──────────────────────┘
```

## 2. Конфігурація компонування пам'яті (Linker Script)

Щоб змінні зберігали свій стан крізь фази глибокого сну без повторного занулення стандартним прологом C-runtime, ми виділяємо окрему секцію `.retention` у пам'яті SRAM2 (адреса `0x10000000` у STM32L4), живлення якої підтримується мікропотужним LPR-регулятором.

Фрагмент скрипта компонувальника GCC (`linker_script.ld`):

```ld
MEMORY
{
  FLASH (rx)      : ORIGIN = 0x08000000, LENGTH = 256K
  SRAM1 (rwx)     : ORIGIN = 0x20000000, LENGTH = 48K
  SRAM2_RET (rw)  : ORIGIN = 0x10000000, LENGTH = 16K   /* Retention domain */
}

SECTIONS
{
  .retention (NOLOAD) :
  {
    . = ALIGN(4);
    _sretention = .;
    *(.retention)
    *(.retention*)
    . = ALIGN(4);
    _eretention = .;
  } > SRAM2_RET
}
```

Атрибут `NOLOAD` вказує компонувальнику не включати цю секцію до таблиці копіювання `.data` та не додавати її до діапазону занулення `.bss` у startup-коді. Завдяки цьому пам'ять залишається абсолютно недоторканою під час кожного швидкого пробудження.

## 3. Реалізація вимірювального драйвера

Нижче наведено робочий код драйвера пробудження. Вкладка C демонструє прямий низькорівневий доступ до регістрів без накладних витрат важких бібліотек. Вкладка C++ реалізує ту саму функціональність через сучасні безпечні нуль-витратні абстракції: RAII-керування живленням давача, типізований доступ до збереженої пам'яті та строгі часові типи.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

// Адреси регістрів периферії (приклад STM32L4 Cortex-M4)
#define RCC_BASE        0x40021000U
#define RCC_AHB2ENR     (*(volatile uint32_t *)(RCC_BASE + 0x4CU))
#define RCC_APB1ENR1    (*(volatile uint32_t *)(RCC_BASE + 0x58U))

#define GPIOA_BASE      0x48000000U
#define GPIOA_MODER     (*(volatile uint32_t *)(GPIOA_BASE + 0x00U))
#define GPIOA_BSRR      (*(volatile uint32_t *)(GPIOA_BASE + 0x18U))

#define PWR_BASE        0x40007000U
#define PWR_CR1         (*(volatile uint32_t *)(PWR_BASE + 0x00U))
#define PWR_SCR         (*(volatile uint32_t *)(PWR_BASE + 0x18U))

#define DWT_CTRL        (*(volatile uint32_t *)0xE0001000U)
#define DWT_CYCCNT      (*(volatile uint32_t *)0xE0001004U)
#define CoreDebug_DEMCR (*(volatile uint32_t *)0xE000EDFCU)

#define PIN_MARKER_CPU   (1U << 0)  // PA0
#define PIN_MARKER_ANLG  (1U << 1)  // PA1
#define PIN_LOAD_SWITCH  (1U << 2)  // PA2

// Структура збережених даних у Retention RAM (SRAM2 / Backup SRAM)
typedef struct {
    uint32_t boot_magic;
    uint32_t wake_counter;
    uint16_t adc_history[64];
    uint32_t last_duration_cycles;
} RetentionStorage;

#define RETENTION_RAM_ADDR 0x10000000U
#define RETENTION_MAGIC    0x57414B45U // "WAKE"

static RetentionStorage *const g_retention = (RetentionStorage *)RETENTION_RAM_ADDR;

static inline void dwt_init(void) {
    CoreDebug_DEMCR |= (1U << 24); // DEMCR_TRCENA
    DWT_CTRL |= (1U << 0);        // DWT_CTRL_CYCCNTENA
}

static inline void marker_cpu_high(void) {
    GPIOA_BSRR = PIN_MARKER_CPU;
}

static inline void marker_cpu_low(void) {
    GPIOA_BSRR = (PIN_MARKER_CPU << 16);
}

static inline void sensor_power_on(void) {
    GPIOA_BSRR = PIN_LOAD_SWITCH | PIN_MARKER_ANLG;
}

static inline void sensor_power_off(void) {
    GPIOA_BSRR = (PIN_LOAD_SWITCH << 16) | (PIN_MARKER_ANLG << 16);
}

// Швидкий замір АЦП без повторного повного калібрування
static uint16_t perform_fast_adc_measurement(void) {
    // Імітація вибірки 16 семплів зі стабілізованого каналу
    volatile uint32_t sum = 0;
    for (int i = 0; i < 16; ++i) {
        sum += (2048U + (uint32_t)(i * 3));
    }
    return (uint16_t)(sum >> 4);
}

void fast_wakeup_sequence(void) {
    // 1. Перший машинний такт: підняти маркер активності CPU
    marker_cpu_high();
    
    // Запуск лічильника циклів DWT для точного виміру
    DWT_CYCCNT = 0;
    
    // 2. Перевірка цілісності Retention RAM
    if (g_retention->boot_magic != RETENTION_MAGIC) {
        g_retention->boot_magic = RETENTION_MAGIC;
        g_retention->wake_counter = 0;
    }
    
    // 3. Комутація живлення давача
    sensor_power_on();
    
    // 4. Очікування стабілізації аналогової шини (наприклад, 120 мкс на 16 МГц MSI = 1920 тактів)
    uint32_t start_tick = DWT_CYCCNT;
    while ((DWT_CYCCNT - start_tick) < 1920U) {
        // Очікування завершення перехідного процесу
    }
    
    // 5. Виконання швидкої вибірки АЦП
    uint16_t sample = perform_fast_adc_measurement();
    
    // 6. Збереження результату у збережену пам'ять
    uint32_t idx = g_retention->wake_counter % 64U;
    g_retention->adc_history[idx] = sample;
    g_retention->wake_counter++;
    
    // Зняття живлення з давача
    sensor_power_off();
    
    // Фіксація тривалості циклу в тактах
    g_retention->last_duration_cycles = DWT_CYCCNT;
    
    // 7. Опускання маркерного виводу безпосередньо перед засинанням
    marker_cpu_low();
    
    // Очищення прапорця пробудження та перехід у глибокий сон (Stop 2)
    PWR_SCR = (1U << 0); // Clear WUF (Wakeup Flag)
    PWR_CR1 |= (1U << 14); // LPMS = Stop 2 Mode
    
    __asm volatile ("wfi");
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>

namespace power_audit {

// Апаратні адреси регістрів
inline constexpr std::uintptr_t kRccBase   = 0x40021000U;
inline constexpr std::uintptr_t kGpioaBase = 0x48000000U;
inline constexpr std::uintptr_t kPwrBase   = 0x40007000U;
inline constexpr std::uintptr_t kDwtCtrl   = 0xE0001000U;
inline constexpr std::uintptr_t kDwtCyccnt = 0xE0001004U;
inline constexpr std::uintptr_t kDemcr     = 0xE000EDFCU;

// Бітові маски ліній
inline constexpr std::uint32_t kPinMarkerCpu  = 1U << 0;
inline constexpr std::uint32_t kPinMarkerAnlg = 1U << 1;
inline constexpr std::uint32_t kPinLoadSwitch = 1U << 2;

inline constexpr std::uint32_t kRetentionMagic = 0x57414B45U; // "WAKE"
inline constexpr std::size_t   kHistoryDepth   = 64;

struct RetentionStorage {
    std::uint32_t boot_magic;
    std::uint32_t wake_counter;
    std::uint16_t adc_history[kHistoryDepth];
    std::uint32_t last_duration_cycles;
};

// Регістровий драйвер GPIO через BSRR
class FastMarkerPort {
public:
    static void set_cpu_active(bool active) noexcept {
        auto& bsrr = *reinterpret_cast<volatile std::uint32_t*>(kGpioaBase + 0x18U);
        bsrr = active ? kPinMarkerCpu : (kPinMarkerCpu << 16);
    }

    static void set_sensor_power(bool enable) noexcept {
        auto& bsrr = *reinterpret_cast<volatile std::uint32_t*>(kGpioaBase + 0x18U);
        std::uint32_t mask = kPinLoadSwitch | kPinMarkerAnlg;
        bsrr = enable ? mask : (mask << 16);
    }
};

// RAII-обгортка для гарантованого вимкнення живлення периферії
class [[nodiscard]] SensorPowerRailGuard {
public:
    SensorPowerRailGuard() noexcept {
        FastMarkerPort::set_sensor_power(true);
    }

    ~SensorPowerRailGuard() noexcept {
        FastMarkerPort::set_sensor_power(false);
    }

    SensorPowerRailGuard(const SensorPowerRailGuard&) = delete;
    SensorPowerRailGuard& operator=(const SensorPowerRailGuard&) = delete;
};

// Апаратний лічильник тактів Cortex-M
class CycleCounter {
public:
    static void init() noexcept {
        *reinterpret_cast<volatile std::uint32_t*>(kDemcr) |= (1U << 24);
        *reinterpret_cast<volatile std::uint32_t*>(kDwtCtrl) |= (1U << 0);
    }

    static void reset() noexcept {
        *reinterpret_cast<volatile std::uint32_t*>(kDwtCyccnt) = 0;
    }

    [[nodiscard]] static std::uint32_t get() noexcept {
        return *reinterpret_cast<volatile std::uint32_t*>(kDwtCyccnt);
    }

    static void wait_cycles(std::uint32_t cycles) noexcept {
        std::uint32_t start = get();
        while ((get() - start) < cycles) {
            // Очікування встановлення шини
        }
    }
};

// Контейнер збереженої пам'яті
class BackupDomain {
public:
    explicit BackupDomain(std::uintptr_t base_address) noexcept
        : storage_(*reinterpret_cast<RetentionStorage*>(base_address)) {
        if (storage_.boot_magic != kRetentionMagic) {
            storage_.boot_magic = kRetentionMagic;
            storage_.wake_counter = 0;
        }
    }

    void record_sample(std::uint16_t value, std::uint32_t duration_cycles) noexcept {
        std::size_t idx = storage_.wake_counter % kHistoryDepth;
        storage_.adc_history[idx] = value;
        storage_.wake_counter++;
        storage_.last_duration_cycles = duration_cycles;
    }

    [[nodiscard]] std::span<const std::uint16_t> history() const noexcept {
        return {storage_.adc_history, kHistoryDepth};
    }

private:
    RetentionStorage& storage_;
};

// Основний конвеєр швидкого пробудження
class FastWakeupController {
public:
    static void execute_fast_cycle() noexcept {
        FastMarkerPort::set_cpu_active(true);
        CycleCounter::reset();

        BackupDomain backup(0x10000000U);

        std::uint16_t sample_value = 0;
        {
            SensorPowerRailGuard rail_guard{};

            // Очікування стабілізації: 120 мкс на 16 МГц = 1920 тактів
            CycleCounter::wait_cycles(1920U);

            sample_value = sample_analog_input();
        } // rail_guard автоматично знеструмлює датчик при виході з блоку

        backup.record_sample(sample_value, CycleCounter::get());

        FastMarkerPort::set_cpu_active(false);
        enter_deep_sleep();
    }

private:
    [[nodiscard]] static std::uint16_t sample_analog_input() noexcept {
        volatile std::uint32_t accumulator = 0;
        for (std::size_t i = 0; i < 16; ++i) {
            accumulator += static_cast<std::uint32_t>(2048U + i * 3);
        }
        return static_cast<std::uint16_t>(accumulator >> 4);
    }

    static void enter_deep_sleep() noexcept {
        auto& pwr_scr = *reinterpret_cast<volatile std::uint32_t*>(kPwrBase + 0x18U);
        auto& pwr_cr1 = *reinterpret_cast<volatile std::uint32_t*>(kPwrBase + 0x00U);

        pwr_scr = (1U << 0);       // Clear WUF
        pwr_cr1 |= (1U << 14);     // Stop 2 Mode

        asm volatile ("wfi");
    }
};

} // namespace power_audit

extern "C" void fast_wakeup_sequence(void) {
    power_audit::FastWakeupController::execute_fast_cycle();
}
```
:::

## 4. Стендова методика зняття та аналізу осцилограм

Для коректного зняття профілю струму на мікросекундних часових базах дотримуйтеся такого алгоритму підключення:

1. **Монтаж прецизійного шунта:** У розрив негативної (GND) або позитивної (VDD) лінії живлення встановлюється безіндуктивний SMD-резистор номіналом 10.0 Ом (точністю 0.1%). За наявності використовується спеціалізований інструмент енергетичного профілювання (наприклад, Joulescope або Nordic Power Profiler Kit).
2. **Підключення осцилографічних щупів:** Щуп каналу 1 підключається до виводу `PA0` (MARKER_CPU) для синхронізації запуску розгортки за наростаючим фронтом (Rising Edge Trigger). Щуп каналу 2 підключається паралельно струмовому шунту з використанням пружинного наконечника заземлення (Ground Spring), оскільки довгий гнучкий провід заземлення («крокодил») додає паразитну індуктивність 50–100 нГн, що викликає помилкові високочастотні коливання на фронтах перемикання.
3. **Обчислення інтегрального заряду:** За допомогою математичного каналу осцилографа `Math = Integral(Ch2 / 10.0)` обчислюється площа під кривою струму в одиницях заряду (Кулони):
   ```
   Q_cycle = ∫ I(t) dt
   ```
4. **Визначення точки перегину стабілізації:** Напруга на виводі датчика після комутації ключа має експоненційний вигляд `V(t) = V_DD · (1 - exp(-t / τ))`. Час очікування у циклі DWT має дорівнювати щонайменше `4τ`–`5τ`, де напруга досягає 99.3% від номіналу, щоб виключити помилки оцифрування.

## 5. Типові інженерні пастки при профілюванні

1. **Фальшивий довгий старт через стандартний `SystemInit()`:** Більшість згенерованих компілятором startup-файлів при виході зі сну викликають функцію ініціалізації тактового дерева, яка містить очікування прапорця `HSERDY` або `PLLRDY` у нескінченному циклі `while`. Якщо задача швидка — перевірте джерело пробудження у векторі скидання й переходьте безпосередньо до виконання на швидкому внутрішньому RC (MSI/HSI), минаючи конфігурацію PLL.
2. **Ємнісне спотворення фронтів маркерного піна:** Підключення стандартного щупа осцилографа з ємністю 15–20 пФ на контакт `GPIO_MARKER` затягує швидкі перепади напруги до 10–30 нс. Для фіксації субмікросекундних імпульсів використовуйте активні щупи або узгоджені коаксіальні лінії з резистивним дільником на платі.
3. **Хибне повторне пробудження через залишковий прапорець переривання:** Якщо перед викликом інструкції `wfi` не очистити прапорець виходу зі сну в регістрі супервізора живлення (`PWR->SCR = PWR_SCR_CWUF`), ядро миттєво прокинеться в наступному такті, не занурившись у глибокий сон.
4. **Паразитне зворотне живлення вимкненого датчика через цифрові лінії:** Якщо датчик знеструмлено комутатором живлення, а лінії шини I²C або SPI залишаються підтягнутими до 3.3 В або мають логічний рівень HIGH, струм потече через внутрішні захисні ESD-діоди датчика у знеструмлену шину VDD. Перед зняттям живлення завжди переводьте лінії зв'язку в режим високого імпедансу (Hi-Z / Analog Mode) або низького рівня (LOW).
