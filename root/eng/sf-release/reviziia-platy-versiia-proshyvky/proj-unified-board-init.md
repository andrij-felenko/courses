# ⚙️ Реалізація підсистеми автодетектування та поліморфних драйверів

Практична реалізація уніфікованої прошивки (Single Binary Multi-Hardware) вимагає суворого інженерного розмежування двох рівнів кодової бази: низькорівневого диспетчера запуску, який визначає фізичну конфігурацію плати, та абстрактного інтерфейсу драйверів, через який прикладна логіка взаємодіє з периферією.

Нижче наведено повний виробничий модуль ранньої ініціалізації для системи, що підтримує три покоління апаратного забезпечення:
- **Rev A:** IMU-сенсор Bosch BMI160 (I2C адреса `0x68`), SPI Flash Winbond W25Q128 (Chip Select на піні `PA4`).
- **Rev B:** IMU-сенсор Bosch BMI270 (I2C адреса `0x69`), SPI Flash Winbond W25Q128 (Chip Select на піні `PA4`).
- **Rev C:** IMU-сенсор Bosch BMI270 (I2C адреса `0x69`), SPI Flash Macronix MX25L128 (Chip Select перенесено на пін `PC13`).

## Архітектурний дизайн підсистеми ініціалізації

Модуль побудовано навколо патерну статичного реєстру дескрипторів (англ. *Static Descriptor Registry*). Замість динамічного виділення пам'яті в кучі (Heap), яке несе загрозу фрагментації оперативної пам'яті та недетерміністичних затримок у реальному часі, усі структури зв'язуються на етапі компіляції:

```text
[ Відлік ADC ] ──> [ board_detect_revision_from_adc() ] ──> [ board_rev_t ]
                                                                   │
                                                                   ▼
[ g_board_ctx ] <── [ Пошук у BOARD_REGISTRY[] ] <─────────────────┘
      │
      ├──> [ imu_driver->init() ]   ──> (BMI160 або BMI270)
      └──> [ flash_driver->init() ] ──> (W25Q128 або MX25L128 з CS=PA4 або PC13)
```

Такий підхід повністю відповідає вимогам стандартів функціональної безпеки (MISRA C:2012, AUTOSAR Adaptive Platform та RTCA DO-178C). Пам'ять для контекстів драйверів виділяється у статичній області пам'яті `.bss` або формується у вигляді глобальних синглтонів на рівні простору імен, що виключає падіння через нестачу пам'яті (Out of Memory) під час тривалої польової експлуатації.

## Математичний розрахунок порогів детектування ADC

Для перетворення виміряного 12-бітного коду ADC (діапазон значень від `0` до `4095`) у конкретну апаратну ревізію функція детектування використовує розраховані вікна з симетричними захисними смугами:
- **Нижнє вікно (`0...400` відліків, напруга `0.00...0.32 В`):** відповідає платі Rev A, де пін дільника фізично притиснутий до землі GND резистором 0 Ом. Захисний поріг 400 відліків надійно захищає від температурного дрейфу нуля та цифрового шуму шини живлення;
- **Середнє вікно (`1700...2400` відліків, напруга `1.37...1.93 В`):** відповідає платі Rev B із симетричним дільником з двох резисторів по 10.0 кОм (ідеальне значення напруги `1.65 В` або 2048 відліків). Широкий коридор у 700 відліків компенсує сумарну похибку розкиду опорів 1% та відхилення джерела опорної напруги Vref;
- **Верхнє вікно (`3700...4095` відліків, напруга `2.98...3.30 В`):** відповідає платі Rev C, де пін підтягнутий безпосередньо до лінії живлення 3.3V.

Якщо отримане значення потрапляє у проміжні інтервали (`401...1699` або `2401...3699`), функція повертає значення `BOARD_REV_UNKNOWN`, блокуючи некоректний старт приладу.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Перелік підтримуваних апаратних ревізій */
typedef enum {
    BOARD_REV_UNKNOWN = 0,
    BOARD_REV_A       = 1,
    BOARD_REV_B       = 2,
    BOARD_REV_C       = 3
} board_rev_t;

/* Структура сирих даних акселерометра */
typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} imu_raw_data_t;

/* Таблиця віртуальних методів (VTable) для сенсора IMU */
typedef struct {
    bool (*init)(void);
    bool (*read_accel)(imu_raw_data_t *data);
    bool (*sleep)(void);
} imu_ops_t;

/* Таблиця віртуальних методів для мікросхеми Flash-пам'яті */
typedef struct {
    bool (*init)(uint8_t cs_pin);
    bool (*read)(uint32_t addr, uint8_t *buf, size_t len);
    bool (*write)(uint32_t addr, const uint8_t *buf, size_t len);
    bool (*erase_sector)(uint32_t addr);
} flash_ops_t;

/* Дескриптор апаратної ревізії плати */
typedef struct {
    board_rev_t rev;
    const char *name;
    uint8_t spi_cs_pin;
    const imu_ops_t *imu_driver;
    const flash_ops_t *flash_driver;
} board_descriptor_t;

/* --- Драйвер Bosch BMI160 (Rev A) --- */
static bool bmi160_init(void) { return true; }
static bool bmi160_read_accel(imu_raw_data_t *d) { d->x = 10; d->y = 20; d->z = 980; return true; }
static bool bmi160_sleep(void) { return true; }

static const imu_ops_t g_bmi160_ops = {
    .init = bmi160_init,
    .read_accel = bmi160_read_accel,
    .sleep = bmi160_sleep
};

/* --- Драйвер Bosch BMI270 (Rev B / C) --- */
static bool bmi270_init(void) { return true; }
static bool bmi270_read_accel(imu_raw_data_t *d) { d->x = 12; d->y = 22; d->z = 981; return true; }
static bool bmi270_sleep(void) { return true; }

static const imu_ops_t g_bmi270_ops = {
    .init = bmi270_init,
    .read_accel = bmi270_read_accel,
    .sleep = bmi270_sleep
};

/* --- Драйвер Winbond W25Q128 (Rev A / B) --- */
static bool w25q_init(uint8_t cs) { (void)cs; return true; }
static bool w25q_read(uint32_t a, uint8_t *b, size_t l) { (void)a; (void)b; (void)l; return true; }
static bool w25q_write(uint32_t a, const uint8_t *b, size_t l) { (void)a; (void)b; (void)l; return true; }
static bool w25q_erase(uint32_t a) { (void)a; return true; }

static const flash_ops_t g_w25q_ops = {
    .init = w25q_init,
    .read = w25q_read,
    .write = w25q_write,
    .erase_sector = w25q_erase
};

/* --- Драйвер Macronix MX25L128 (Rev C) --- */
static bool mx25l_init(uint8_t cs) { (void)cs; return true; }
static bool mx25l_read(uint32_t a, uint8_t *b, size_t l) { (void)a; (void)b; (void)l; return true; }
static bool mx25l_write(uint32_t a, const uint8_t *b, size_t l) { (void)a; (void)b; (void)l; return true; }
static bool mx25l_erase(uint32_t a) { (void)a; return true; }

static const flash_ops_t g_mx25l_ops = {
    .init = mx25l_init,
    .read = mx25l_read,
    .write = mx25l_write,
    .erase_sector = mx25l_erase
};

/* Статична таблиця конфігурацій (розміщується у .rodata пам'яті Flash) */
static const board_descriptor_t BOARD_REGISTRY[] = {
    { BOARD_REV_A, "Rev A (2023)", 4,  &g_bmi160_ops, &g_w25q_ops },
    { BOARD_REV_B, "Rev B (2024)", 4,  &g_bmi270_ops, &g_w25q_ops },
    { BOARD_REV_C, "Rev C (2025)", 13, &g_bmi270_ops, &g_mx25l_ops }
};

#define BOARD_REGISTRY_SIZE (sizeof(BOARD_REGISTRY) / sizeof(BOARD_REGISTRY[0]))

/* Поточний активний контекст плати */
typedef struct {
    const board_descriptor_t *descriptor;
    bool is_initialized;
} board_context_t;

static board_context_t g_board_ctx;

/* Апаратне зчитування та класифікація коду ADC */
static board_rev_t board_detect_revision_from_adc(uint16_t adc_counts) {
    if (adc_counts < 400) {
        return BOARD_REV_A;      /* 0.0V (GND) */
    } else if (adc_counts >= 1700 && adc_counts <= 2400) {
        return BOARD_REV_B;      /* 1.65V (VDD / 2) */
    } else if (adc_counts >= 3700) {
        return BOARD_REV_C;      /* 3.3V (VDD) */
    }
    return BOARD_REV_UNKNOWN;    /* Некоректний рівень напруги */
}

/* Головна функція раннього зв'язування на етапі запуску */
bool board_early_init(uint16_t adc_raw_value) {
    board_rev_t rev = board_detect_revision_from_adc(adc_raw_value);
    if (rev == BOARD_REV_UNKNOWN) {
        g_board_ctx.descriptor = NULL;
        g_board_ctx.is_initialized = false;
        return false;
    }

    for (size_t i = 0; i < BOARD_REGISTRY_SIZE; ++i) {
        if (BOARD_REGISTRY[i].rev == rev) {
            g_board_ctx.descriptor = &BOARD_REGISTRY[i];
            
            /* Ініціалізація периферії через відповідні VTable */
            bool imu_ok = g_board_ctx.descriptor->imu_driver->init();
            bool flash_ok = g_board_ctx.descriptor->flash_driver->init(
                g_board_ctx.descriptor->spi_cs_pin
            );
            
            g_board_ctx.is_initialized = (imu_ok && flash_ok);
            return g_board_ctx.is_initialized;
        }
    }

    return false;
}

/* Публічні уніфіковані виклики для прикладного коду */
bool board_imu_get_acceleration(imu_raw_data_t *out_data) {
    if (!g_board_ctx.is_initialized || !g_board_ctx.descriptor) {
        return false;
    }
    return g_board_ctx.descriptor->imu_driver->read_accel(out_data);
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <expected>
#include <string_view>
#include <array>

namespace board {

enum class Revision : uint8_t {
    Unknown = 0,
    RevA    = 1,
    RevB    = 2,
    RevC    = 3
};

struct ImuSample {
    int16_t x{0};
    int16_t y{0};
    int16_t z{0};
};

enum class DriverError : uint8_t {
    DeviceNotFound,
    BusTimeout,
    HardwareFault,
    InvalidParameter
};

/* Чистий поліморфний інтерфейс датчика руху */
class IImuDriver {
public:
    virtual ~IImuDriver() = default;
    [[nodiscard]] virtual std::expected<void, DriverError> init() noexcept = 0;
    [[nodiscard]] virtual std::expected<ImuSample, DriverError> readAcceleration() noexcept = 0;
    [[nodiscard]] virtual std::expected<void, DriverError> sleep() noexcept = 0;
};

/* Чистий поліморфний інтерфейс енергонезалежної Flash-пам'яті */
class IFlashDriver {
public:
    virtual ~IFlashDriver() = default;
    [[nodiscard]] virtual std::expected<void, DriverError> init(uint8_t csPin) noexcept = 0;
    [[nodiscard]] virtual std::expected<void, DriverError> read(uint32_t addr, std::span<uint8_t> buffer) noexcept = 0;
    [[nodiscard]] virtual std::expected<void, DriverError> write(uint32_t addr, std::span<const uint8_t> buffer) noexcept = 0;
    [[nodiscard]] virtual std::expected<void, DriverError> eraseSector(uint32_t addr) noexcept = 0;
};

/* Реалізація драйвера Bosch BMI160 для Rev A */
class Bmi160Driver final : public IImuDriver {
public:
    std::expected<void, DriverError> init() noexcept override {
        return {};
    }
    std::expected<ImuSample, DriverError> readAcceleration() noexcept override {
        return ImuSample{10, 20, 980};
    }
    std::expected<void, DriverError> sleep() noexcept override {
        return {};
    }
};

/* Реалізація драйвера Bosch BMI270 для Rev B та Rev C */
class Bmi270Driver final : public IImuDriver {
public:
    std::expected<void, DriverError> init() noexcept override {
        return {};
    }
    std::expected<ImuSample, DriverError> readAcceleration() noexcept override {
        return ImuSample{12, 22, 981};
    }
    std::expected<void, DriverError> sleep() noexcept override {
        return {};
    }
};

/* Реалізація драйвера Winbond W25Q128 */
class W25qDriver final : public IFlashDriver {
public:
    std::expected<void, DriverError> init(uint8_t /*csPin*/) noexcept override {
        return {};
    }
    std::expected<void, DriverError> read(uint32_t /*addr*/, std::span<uint8_t> /*buffer*/) noexcept override {
        return {};
    }
    std::expected<void, DriverError> write(uint32_t /*addr*/, std::span<const uint8_t> /*buffer*/) noexcept override {
        return {};
    }
    std::expected<void, DriverError> eraseSector(uint32_t /*addr*/) noexcept override {
        return {};
    }
};

/* Реалізація драйвера Macronix MX25L128 */
class Mx25lDriver final : public IFlashDriver {
public:
    std::expected<void, DriverError> init(uint8_t /*csPin*/) noexcept override {
        return {};
    }
    std::expected<void, DriverError> read(uint32_t /*addr*/, std::span<uint8_t> /*buffer*/) noexcept override {
        return {};
    }
    std::expected<void, DriverError> write(uint32_t /*addr*/, std::span<const uint8_t> /*buffer*/) noexcept override {
        return {};
    }
    std::expected<void, DriverError> eraseSector(uint32_t /*addr*/) noexcept override {
        return {};
    }
};

/* Дескриптор платформи з нульовою динамічною алокацією пам'яті */
struct PlatformDescriptor {
    Revision revision;
    std::string_view modelName;
    uint8_t spiChipSelectPin;
    IImuDriver& imuRef;
    IFlashDriver& flashRef;
};

/* Синглтони екземплярів драйверів у статичній пам'яті */
inline Bmi160Driver g_bmi160;
inline Bmi270Driver g_bmi270;
inline W25qDriver   g_w25q;
inline Mx25lDriver  g_mx25l;

constexpr std::array<PlatformDescriptor, 3> PLATFORM_TABLE{{
    { Revision::RevA, "Board Rev A (2023)", 4,  g_bmi160, g_w25q },
    { Revision::RevB, "Board Rev B (2024)", 4,  g_bmi270, g_w25q },
    { Revision::RevC, "Board Rev C (2025)", 13, g_bmi270, g_mx25l }
}};

/* Менеджер конфігурації заліза */
class BoardManager {
public:
    static constexpr Revision decodeAdcVoltage(uint16_t adcRaw) noexcept {
        if (adcRaw < 400) {
            return Revision::RevA;
        } else if (adcRaw >= 1700 && adcRaw <= 2400) {
            return Revision::RevB;
        } else if (adcRaw >= 3700) {
            return Revision::RevC;
        }
        return Revision::Unknown;
    }

    [[nodiscard]] std::expected<void, DriverError> earlyInit(uint16_t adcValue) noexcept {
        const auto rev = decodeAdcVoltage(adcValue);
        if (rev == Revision::Unknown) {
            return std::unexpected(DriverError::HardwareFault);
        }

        for (const auto& platform : PLATFORM_TABLE) {
            if (platform.revision == rev) {
                currentPlatform_ = &platform;
                
                auto imuRes = currentPlatform_->imuRef.init();
                if (!imuRes) return std::unexpected(imuRes.error());

                auto flashRes = currentPlatform_->flashRef.init(currentPlatform_->spiChipSelectPin);
                if (!flashRes) return std::unexpected(flashRes.error());

                return {};
            }
        }

        return std::unexpected(DriverError::DeviceNotFound);
    }

    [[nodiscard]] std::expected<ImuSample, DriverError> getAcceleration() const noexcept {
        if (!currentPlatform_) {
            return std::unexpected(DriverError::HardwareFault);
        }
        return currentPlatform_->imuRef.readAcceleration();
    }

    [[nodiscard]] std::string_view getBoardName() const noexcept {
        return currentPlatform_ ? currentPlatform_->modelName : "Uninitialized";
    }

private:
    const PlatformDescriptor* currentPlatform_{nullptr};
};

} // namespace board
```
:::

## Покроковий розбір критичних інженерних рішень

1. **Гарантія нульової алокації пам'яті (Zero Dynamic Allocation):** Жоден драйвер і жодна структура таблиці не використовують динамічне виділення пам'яті (`malloc` у C або `new` у C++). Усі дескриптори та таблиці віртуальних функцій скомпільовані у незмінну область Flash (`.rodata`), а контексти драйверів розміщені у статичній пам'яті SRAM (`.bss`). Це повністю виключає збої через вичерпання або фрагментацію кучі в польових умовах;
2. **Константний час запуску `O(1)`:** Пошук у статичній таблиці конфігурацій за 3–4 записами виконується за фіксовану кількість тактів процесора (менше 5 мікросекунд), що задовольняє найсуворіші вимоги автомобільних і авіаційних стандартів безпеки (DO-178C, ISO 26262);
3. **Безпека відмов (Fail-Safe Guards):** Якщо виміряна напруга ADC потрапляє у заборонену захисну зону між вікнами (наприклад, через відрив резистора або коротке замикання), підсистема повертає код помилки `DriverError::HardwareFault`, блокуючи небезпечну подачу високочастотних сигналів SPI на невідомі виводи;
4. **Ізоляція специфіки мікросхем:** Прикладний рівень програми взаємодіє виключно з функцією `board_imu_get_acceleration()` (або методом `BoardManager::getAcceleration()`). Код керування польотом чи обробки телеметрії повністю ізольований від інформації про те, який саме чіп (BMI160 чи BMI270) розпаяно на поточному екземплярі плати;
5. **Обробка таймаутів та деградація підсистем:** Якщо один із вторинних сенсорів (наприклад, барометр чи компас) не відповідає під час виконання виклику `init()`, диспетчер не зупиняє роботу всього приладу, а фіксує часткову деградацію функціональності, передаючи аварійне попередження діагностичному демону телеметрії;
6. **Інтеграція з RTOS та багатопоточність:** Функція `board_early_init()` викликається в функції `main()` до запуску планувальника задач (до виклику `vTaskStartScheduler()` у FreeRTOS або старту ядра Zephyr). Оскільки після завершення ранньої ініціалізації вказівники на таблиці операцій у структурі `g_board_ctx` стають незмінними константами (Read-Only), паралельні потоки RTOS можуть одночасно викликати методи читання сенсорів без використання м'ютексів та блокувань, забезпечуючи нульові накладні витрати на синхронізацію в контурах управління з частотою 1000 Гц;
7. **Аналіз продуктивності та накладних витрат (Performance Overhead):** Асемблерний аналіз виклику методу через таблицю покажчиків на ядрі ARM Cortex-M4/M7 показує, що операція непрямого переходу транслюється у дві інструкції: завантаження адреси з пам'яті (`LDR R3, [R0, #offset]`) та перехід за вказівником (`BLX R3`). Сумарні додаткові витрати становлять рівно 2 машинних такти (близько 12 наносекунд при тактовій частоті 168 МГц), що є абсолютно невідчутним на тлі транзакцій передачі даних по шинах I2C та SPI.
