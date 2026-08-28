# ⚙️ Автоматизований стенд power-cut тестування на базі мікроконтролера та керованого комутатора

Надійність вбудованої системи під час раптового знеструмлення неможливо довести теоретично або перевірити симуляцією на робочій станції розробника: тонкі напівпровідникові ефекти Flash-пам'яті, поведінка вбудованого завантажувача (bootloader) та стійкість журналу файлової системи проявляються виключно в реальному залізі під впливом апаратного знеструмлення у критичні мікросекунди.

Нижче реалізовано повний програмно-апаратний комплекс для автоматизованого Power-Cut тестування, побудований за принципом замкненого контуру:
1. **Прошивка контролера комутатора живлення (Harness Controller):** обробляє зовнішній апаратний тригер від цільового пристрою (DUT), відраховує прецизійну мікросекундну затримку через 32-бітний апаратний таймер, керує парою силових MOSFET (верхнє плече + активний розряд) і передає телеметрію на хост.
2. **Прошивка цільового мікроконтролера (DUT Target):** емулює циклічне оновлення секторів Flash-пам'яті та транзакційний запис файлової системи LittleFS із виставленням тригерного імпульсу синхронізації.
3. **Модуль валідації та аудиту цілісності (Host Oracle):** перевіряє стан розділів, детектує пошкоджені байти, відловлює цикли перезавантаження (bootloop) та веде статистику виживаності.

## Контролер комутатора: прецизійний апаратний таймінг

Головне завдання керуючого мікроконтролера стенда — мінімізувати часовий дрейф (фазовий джитер) між надходженням тригерного фронту від цільового пристрою та фізичним розривом силового кола. Якщо обробляти тригер у високорівневому циклі опитування або через повільну операційну систему, випадкові затримки планувальника (10–100 мкс) унеможливлять прицільний фаззинг коротких операцій (наприклад, запису сторінки за 250 мкс).

Тому контролер стенда реалізує повністю апаратний контур: вхідний пін тригера налаштований на лінію зовнішнього переривання (EXTI) з прямим запуском 32-бітного таймера (TIM2), що тактується безпосередньо від системної шини без попереднього поділу (1 такт = 1/72 або 1/84 мікросекунди). Таймер генерує переривання після відліку точної кількості мікросекунд, детерміновано переводячи вихідні піни в стан екстремального знеструмлення (джитер < 50 нс).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Базові константи та порти комутатора */
#define PIN_HS_GATE      (1U << 4)   /* P-MOSFET верхнього плеча (Active LOW) */
#define PIN_CROWBAR_GATE (1U << 5)   /* N-MOSFET активного розряду (Active HIGH) */
#define PIN_TRIG_INPUT   (1U << 0)   /* Вхід апаратного тригера з DUT */

typedef struct {
    volatile uint32_t delay_us;       /* Затримка від тригера до обриву (мкс) */
    volatile uint32_t cut_duration_ms;/* Тривалість фази знеструмлення (мс) */
    volatile bool     armed;          /* Прапорець готовності до перехоплення */
    volatile bool     cycle_completed;/* Прапорець завершення циклу */
    uint32_t          total_cycles;   /* Загальний лічильник виконаних циклів */
} harness_state_t;

static harness_state_t g_harness = {
    .delay_us = 100,
    .cut_duration_ms = 50,
    .armed = false,
    .cycle_completed = false,
    .total_cycles = 0
};

/* Апаратне вмикання живлення цільового пристрою */
static inline void power_rail_enable(void) {
    /* 1. Закриваємо розрядний N-MOSFET */
    /* GPIO_PORT->BSRR = (PIN_CROWBAR_GATE << 16); */
    
    /* Захисна пауза (dead-time) для запобігання наскрізного струму: 50 нс */
    __asm volatile("nop; nop; nop; nop;");
    
    /* 2. Відкриваємо силовий P-MOSFET верхнього плеча (подаємо LOW на затвор) */
    /* GPIO_PORT->BSRR = (PIN_HS_GATE << 16); */
}

/* Апаратне екстремальне знеструмлення шини живлення з активним розрядом */
static inline void power_rail_emergency_cut(void) {
    /* 1. Миттєво закриваємо P-MOSFET верхнього плеча (подаємо HIGH на затвор) */
    /* GPIO_PORT->BSRR = PIN_HS_GATE; */
    
    /* Захисний інтервал dead-time перед розрядом: 50 нс */
    __asm volatile("nop; nop; nop; nop;");
    
    /* 2. Відкриваємо активний N-MOSFET Crowbar (скидаємо заряд ємностей DUT на GND) */
    /* GPIO_PORT->BSRR = PIN_CROWBAR_GATE; */
}

/* Обробник переривання апаратного таймера точної затримки */
void TIM2_IRQHandler(void) {
    /* Очищення прапорця переривання таймера */
    /* TIM2->SR = ~TIM_SR_UIF; */

    if (g_harness.armed) {
        /* Фаза точного обриву живлення */
        power_rail_emergency_cut();
        g_harness.armed = false;
        g_harness.cycle_completed = true;
        g_harness.total_cycles++;
        
        /* Запуск таймера тривалості знеструмлення */
        /* timer_start_ms(g_harness.cut_duration_ms); */
    }
}

/* Обробник зовнішнього переривання від GPIO-тригера цільового пристрою */
void EXTI0_IRQHandler(void) {
    /* Очищення прапорця переривання EXTI */
    /* EXTI->PR = PIN_TRIG_INPUT; */

    if (g_harness.armed) {
        if (g_harness.delay_us == 0) {
            /* Миттєвий обрив без затримки */
            power_rail_emergency_cut();
            g_harness.armed = false;
            g_harness.cycle_completed = true;
            g_harness.total_cycles++;
        } else {
            /* Завантаження мікросекундного зміщення в лічильник таймера */
            /* TIM2->CNT = 0; */
            /* TIM2->ARR = g_harness.delay_us; */
            /* TIM2->CR1 |= TIM_CR1_CEN; */
        }
    }
}

/* Ініціалізація та армування нового циклу випробування */
void harness_arm_cycle(uint32_t target_delay_us, uint32_t power_off_ms) {
    g_harness.delay_us = target_delay_us;
    g_harness.cut_duration_ms = power_off_ms;
    g_harness.cycle_completed = false;
    
    /* Подаємо живлення на DUT перед очікуванням тригера */
    power_rail_enable();
    
    /* Дозволяємо перехоплення фронту сигналу */
    g_harness.armed = true;
}
```
```cpp
#include <cstdint>
#include <concepts>
#include <span>
#include <atomic>

namespace PowerCut {

/* Клас апаратного драйвера комутації живлення з RAII-гарантією dead-time */
class PowerSwitchController {
public:
    static constexpr std::uint32_t PinHighSide = (1U << 4);
    static constexpr std::uint32_t PinCrowbar  = (1U << 5);
    static constexpr std::uint32_t PinTrigger  = (1U << 0);

    PowerSwitchController() noexcept {
        initHardware();
        enablePower();
    }

    ~PowerSwitchController() noexcept {
        disablePowerSafe();
    }

    void enablePower() noexcept {
        // Закриваємо розрядний N-MOSFET
        setPinState(PinCrowbar, false);
        insertDeadTime();
        // Відкриваємо P-MOSFET верхнього плеча (Active LOW)
        setPinState(PinHighSide, false);
        isPowered_.store(true, std::memory_order_release);
    }

    void emergencyCut() noexcept {
        // Миттєво розмикаємо верхнє плече
        setPinState(PinHighSide, true);
        insertDeadTime();
        // Вмикаємо активний розряд шини на землю
        setPinState(PinCrowbar, true);
        isPowered_.store(false, std::memory_order_release);
    }

    void armTrigger(std::uint32_t delayMicroseconds, std::uint32_t cutDurationMs) noexcept {
        targetDelayUs_.store(delayMicroseconds, std::memory_order_relaxed);
        cutDurationMs_.store(cutDurationMs, std::memory_order_relaxed);
        cycleComplete_.store(false, std::memory_order_release);
        
        enablePower();
        isArmed_.store(true, std::memory_order_release);
    }

    void onTriggerReceived() noexcept {
        if (!isArmed_.load(std::memory_order_acquire)) {
            return;
        }

        const auto delay = targetDelayUs_.load(std::memory_order_relaxed);
        if (delay == 0) {
            emergencyCut();
            finalizeCycle();
        } else {
            startHardwareTimer(delay);
        }
    }

    void onTimerExpired() noexcept {
        if (isArmed_.load(std::memory_order_acquire)) {
            emergencyCut();
            finalizeCycle();
        }
    }

    [[nodiscard]] bool isCycleComplete() const noexcept {
        return cycleComplete_.load(std::memory_order_acquire);
    }

    [[nodiscard]] std::uint64_t getTotalCycles() const noexcept {
        return totalCycles_.load(std::memory_order_relaxed);
    }

private:
    std::atomic<bool>          isArmed_{false};
    std::atomic<bool>          isPowered_{false};
    std::atomic<bool>          cycleComplete_{false};
    std::atomic<std::uint32_t> targetDelayUs_{0};
    std::atomic<std::uint32_t> cutDurationMs_{50};
    std::atomic<std::uint64_t> totalCycles_{0};

    static void insertDeadTime() noexcept {
        #if defined(__ARM_ARCH)
        asm volatile("nop; nop; nop; nop;");
        #endif
    }

    void initHardware() noexcept {
        // Налаштування GPIO регістрів та таймерів мікроконтролера
    }

    void setPinState([[maybe_unused]] std::uint32_t pin, [[maybe_unused]] bool state) noexcept {
        // Прямий бітовий запис у BSRR регістр порту
    }

    void startHardwareTimer([[maybe_unused]] std::uint32_t us) noexcept {
        // Запуск 32-бітного апаратного таймера TIM2
    }

    void finalizeCycle() noexcept {
        isArmed_.store(false, std::memory_order_release);
        cycleComplete_.store(true, std::memory_order_release);
        totalCycles_.fetch_add(1, std::memory_order_relaxed);
    }

    void disablePowerSafe() noexcept {
        setPinState(PinHighSide, true);
        setPinState(PinCrowbar, false);
        isPowered_.store(false, std::memory_order_release);
    }
};

} // namespace PowerCut
```
:::

## Фізика комутації: Dead-Time та активний розряд шини

Особливу увагу в реалізації приділено захисту від наскрізного струму (англ. *shoot-through current*). Коли верхній P-MOSFET закривається, а нижній розрядний N-MOSFET відкривається, існує ризик короткочасного одночасного перебування обох ключів у відкритому стані через затримку виходу з насичення. Без захисного інтервалу (dead-time) наскрізний струм короткого замикання від джерела живлення на землю досягає десятків ампер, руйнуючи кремнієву структуру транзисторів за кілька десятків циклів.

Функції комутації вставляють мікропаузу тривалістю 50 нс (`nop` інструкції процесора). Цього інтервалу достатньо, щоб вхідна ємність затвора P-MOSFET встигла розрядитися до надійного замикання каналу, після чого відкривається розрядний N-MOSFET.

Розрядний N-MOSFET замкнений на землю через низькоомний резистор 2.2 Ом. Це обмежує піковий струм розряду ємностей DUT на безпечному рівні (піковий струм `I_peak ≈ 3.3 В / 2.2 Ом ≈ 1.5 А`), водночас гарантуючи спад напруги шини від 3.3 В до нуля за 800 наносекунд.

## Прошивка цільового пристрою: генерація тригера та запис Flash

Цільовий мікроконтролер повинен видавати чіткий імпульс синхронізації безпосередньо перед початком виконання транзакції запису сектора чи оновлення метаданих файлової системи. Це перетворює сліпий випадковий пошук на спрямований фаззинг найвразливішої фази виконання.

У коді цільового пристрою критичні операції з Flash-пам'яттю обрамляються апаратним перемиканням тригерного виводу: логічний рівень HIGH виставляється безпосередньо перед надсиланням низькорівневої команди стирання `0x20` або запису `0x02` по шині SPI, а скидання в LOW відбувається лише після отримання підтвердження завершення операції з регістра статусу пам'яті.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TARGET_TRIGGER_PIN (1U << 12)

/* Імітація запису оновленого блоку прошивки у SPI NOR Flash */
typedef struct {
    uint32_t magic;
    uint32_t seq_number;
    uint32_t crc32;
    uint8_t  payload[256];
} flash_page_payload_t;

/* Простий обчислювач апаратного або програмного CRC32 */
uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
        }
    }
    return ~crc;
}

/* Функція виконання критичної транзакції оновлення */
void execute_critical_flash_update(uint32_t sector_address, uint32_t sequence_id) {
    flash_page_payload_t block;
    block.magic = 0xAA55AA55;
    block.seq_number = sequence_id;
    memset(block.payload, 0x42, sizeof(block.payload));
    block.crc32 = calculate_crc32((const uint8_t *)&block.seq_number, sizeof(block.seq_number) + sizeof(block.payload));

    /* 1. Виставляємо апаратний тригер HIGH: старт критичної зони */
    /* GPIO_TARGET->BSRR = TARGET_TRIGGER_PIN; */

    /* 2. Стирання сектора NOR Flash (типова тривалість 40-100 мс) */
    /* spi_flash_erase_sector(sector_address); */

    /* 3. Програмування сторінки даних (типова тривалість 200-400 мкс) */
    /* spi_flash_write_page(sector_address, (uint8_t*)&block, sizeof(block)); */

    /* 4. Скидаємо тригер у LOW: критична зона завершена успішно */
    /* GPIO_TARGET->BSRR = (TARGET_TRIGGER_PIN << 16); */
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <numeric>

namespace TargetDUT {

struct alignas(4) FlashPageBlock {
    std::uint32_t magic{0xAA55AA55};
    std::uint32_t sequenceId{0};
    std::uint32_t checksum{0};
    std::array<std::uint8_t, 256> payload{};

    [[nodiscard]] std::uint32_t computeChecksum() const noexcept {
        std::uint32_t crc = 0xFFFFFFFF;
        const auto feedByte = [&crc](std::uint8_t byte) noexcept {
            crc ^= byte;
            for (std::uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
            }
        };

        const auto* seqBytes = reinterpret_cast<const std::uint8_t*>(&sequenceId);
        for (std::size_t i = 0; i < sizeof(sequenceId); ++i) {
            feedByte(seqBytes[i]);
        }
        for (const auto b : payload) {
            feedByte(b);
        }
        return ~crc;
    }
};

class FlashTransactionScope {
public:
    explicit FlashTransactionScope(std::uint32_t triggerPinMask) noexcept
        : pinMask_(triggerPinMask) {
        // Виставляємо тригерний пін у HIGH (вхід у вразливу зону)
        setPin(pinMask_, true);
    }

    ~FlashTransactionScope() noexcept {
        // Скидаємо тригерний пін у LOW (вихід із зони)
        setPin(pinMask_, false);
    }

    FlashTransactionScope(const FlashTransactionScope&) = delete;
    FlashTransactionScope& operator=(const FlashTransactionScope&) = delete;

private:
    std::uint32_t pinMask_;

    static void setPin([[maybe_unused]] std::uint32_t pin, [[maybe_unused]] bool state) noexcept {
        // Прямий запис у регістри порту DUT
    }
};

void performProtectedFlashWrite(std::uint32_t address, std::uint32_t seqId) noexcept {
    FlashPageBlock block;
    block.sequenceId = seqId;
    block.payload.fill(0x5A);
    block.checksum = block.computeChecksum();

    // RAII охоплення зони запису тригерним імпульсом
    {
        FlashTransactionScope triggerScope(1U << 12);
        
        // Симуляція стирання та запису SPI Flash
        // spiFlashEraseSector(address);
        // spiFlashWritePage(address, reinterpret_cast<const std::uint8_t*>(&block), sizeof(block));
    }
}

} // namespace TargetDUT
```
:::

## Модуль валідації та аудиту цілісності після відновлення

Після кожного циклу знеструмлення стенд витримує паузу 50 мілісекунд (для повного розряду всіх внутрішніх ємностей кристала), після чого знову замикає верхній P-MOSFET, повертаючи напругу 3.3 В на шину живлення цільового мікроконтролера.

У цей момент запускається контрольний тайм-аут очікування старту (типово 2.0 секунди). Модуль аудиту на хості слухає потік діагностичних повідомлень від цільового пристрою через гальванічно ізольований UART-порт і класифікує стан системи за трьома критичними інваріантами:

1. **Інваріант первинного завантажувача:** ROM-пам'ять та первинний Bootloader не потрапили в стан фатальної паніки (HardFault), не зациклилися в нескінченному перечитуванні пошкоджених адрес та успішно ініціалізували стек процесора.
2. **Інваріант транзакційності файлової системи:** драйвер LittleFS або UBIFS змонтував розділ накопичувача без помилки порушення структури метаданих (`LFS_ERR_CORRUPT`). Якщо обрив стався посеред запису нового файлу, незавершена транзакція відкочується автоматично, а раніше записані дані залишаються неушкодженими.
3. **Інваріант подвійної буферизації A/B розділів:** якщо новий образ прошивки зазнав пошкодження в процесі стирання або запису сторінок, контрольна сума блоку не збігається, і завантажувач безпомилково перемикає активний запуск на попередній стабільний банк пам'яті (Slot A).

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

typedef enum {
    VERDICT_OK_RECOVERED,
    VERDICT_BRICKED_BOOTLOOP,
    VERDICT_SILENT_CORRUPTION,
    VERDICT_TIMEOUT_NO_RESPONSE
} test_verdict_t;

typedef struct {
    uint32_t run_index;
    uint32_t cut_delay_us;
    test_verdict_t verdict;
    char details[128];
} audit_record_t;

/* Парсер виводу діагностичної консолі цільового пристрою */
test_verdict_t audit_target_console_log(const char *log_buffer, size_t length, audit_record_t *record) {
    if (length == 0 || log_buffer == NULL) {
        record->verdict = VERDICT_TIMEOUT_NO_RESPONSE;
        snprintf(record->details, sizeof(record->details), "DUT не відповів на запит завантаження");
        return VERDICT_TIMEOUT_NO_RESPONSE;
    }

    /* Перевірка на фатальні паніки ядра */
    if (strstr(log_buffer, "HardFault_Handler") != NULL || strstr(log_buffer, "PANIC:") != NULL) {
        record->verdict = VERDICT_BRICKED_BOOTLOOP;
        snprintf(record->details, sizeof(record->details), "Виявлено паніку ядра під час старту");
        return VERDICT_BRICKED_BOOTLOOP;
    }

    /* Перевірка цілісності LittleFS */
    if (strstr(log_buffer, "lfs_mount: corrupt") != NULL) {
        record->verdict = VERDICT_SILENT_CORRUPTION;
        snprintf(record->details, sizeof(record->details), "Пошкодження суперблоку файлової системи");
        return VERDICT_SILENT_CORRUPTION;
    }

    /* Перевірка успішного старту та валідного відкату */
    if (strstr(log_buffer, "BOOT_OK") != NULL || strstr(log_buffer, "ROLLBACK_OK") != NULL) {
        record->verdict = VERDICT_OK_RECOVERED;
        snprintf(record->details, sizeof(record->details), "Успішне відновлення або відкат");
        return VERDICT_OK_RECOVERED;
    }

    record->verdict = VERDICT_SILENT_CORRUPTION;
    snprintf(record->details, sizeof(record->details), "Невідомий стан цілі після рестарту");
    return VERDICT_SILENT_CORRUPTION;
}
```
```cpp
#include <string_view>
#include <string>
#include <optional>
#include <format>
#include <iostream>

namespace HarnessAudit {

enum class VerdictStatus {
    OkRecovered,
    BrickedBootloop,
    SilentCorruption,
    TimeoutNoResponse
};

struct AuditResult {
    std::uint32_t  runIndex{0};
    std::uint32_t  cutDelayUs{0};
    VerdictStatus  status{VerdictStatus::TimeoutNoResponse};
    std::string    description{};
};

class TargetLogAnalyzer {
public:
    [[nodiscard]] static AuditResult evaluateLog(std::string_view consoleOutput, std::uint32_t runIdx, std::uint32_t delayUs) noexcept {
        AuditResult res;
        res.runIndex = runIdx;
        res.cutDelayUs = delayUs;

        if (consoleOutput.empty()) {
            res.status = VerdictStatus::TimeoutNoResponse;
            res.description = "Цільовий пристрій не надав консольного виводу після рестарту";
            return res;
        }

        if (consoleOutput.contains("HardFault_Handler") || consoleOutput.contains("PANIC:") || consoleOutput.contains("ASSERT_FAILED")) {
            res.status = VerdictStatus::BrickedBootloop;
            res.description = "Паніка ядра або HardFault під час ініціалізації завантажувача";
            return res;
        }

        if (consoleOutput.contains("lfs_mount: corrupt") || consoleOutput.contains("CRC_MISMATCH_FATAL")) {
            res.status = VerdictStatus::SilentCorruption;
            res.description = "Невідновне пошкодження метаданих або метастабільні байти Flash";
            return res;
        }

        if (consoleOutput.contains("BOOT_OK") || consoleOutput.contains("ROLLBACK_OK") || consoleOutput.contains("TRANSACTION_REPLAY_SUCCESS")) {
            res.status = VerdictStatus::OkRecovered;
            res.description = "Коректне атомарне відновлення стану або відкат на резервний банк";
            return res;
        }

        res.status = VerdictStatus::SilentCorruption;
        res.description = "Нерозпізнаний стан системи: відсутній маркер успішного завантаження";
        return res;
    }
};

} // namespace HarnessAudit
```
:::

## Інтеграція стенда в конвеєр неперервної інтеграції (CI/CD)

Для запуску тестів у промисловому конвеєрі хост тестування виконує сканування простору затримок двома взаємодоповнюючими стратегіями:

1. **Лінійне сканування (Linear Sweep):** Затримка `t_delay` збільшується від 0 до максимального часу операції (наприклад, 400 000 мкс для стирання сектора) з постійним кроком 50 мкс. Це гарантує суцільне покриття кожної фази зарядового насоса та виявляє детерміновані баги перемикання станів.
2. **Псевдовипадкове бомбардування (Random Glitching):** Для тривалого нічного тестування затримка генерується випадково за рівномірним або експоненційним розподілом. Прогін 50 000 циклів дозволяє з високою статистичною достовірністю виключити рідкісні аномалії метастабільності пам'яті.

У разі виявлення вердикту `BRICKED` або `SILENT_CORRUPTION` стенд автоматично зупиняє прогін, зберігає точне значення затримки `t_delay` та повний лог обміну для подальшого аналізу розробниками у налагоджувачі.
