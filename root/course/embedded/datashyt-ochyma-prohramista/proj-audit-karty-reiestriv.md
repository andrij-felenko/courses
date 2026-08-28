# ⚙️ Аудит карти регістрів та шаблон верифікації чипа

Коли нова мікросхема вперше з'являється на друкованій платі, спроба відразу писати повний високорівневий драйвер із чергами подій, асинхронними перериваннями та каналами DMA майже гарантовано закінчується тривалим і виснажливим пошуком помилок. Якщо датчик повертає суцільні нулі, не відповідає на переривання або видає хаотичні сплески значень, проблема може ховатися на будь-якому з рівнів взаємодії: помилкова 7-бітна адреса пристрою, відсутність біта автоінкременту під час пакетного читання, деструктивне скидання статусних регістрів через Read-Modify-Write, переплутаний порядок байтів у 16-бітному числі або невиконаний апаратний обхідний шлях із листка помилок (Errata Sheet).

Щоб відділити дефекти монтажу заліза від помилок програмної інтерпретації документації, розробник вбудованого ПЗ проводить системний поетапний аудит карти регістрів. Цей процес дозволяє послідовно верифікувати кожен рівень апаратного контракту чипа ще до того, як буде написано перший рядок робочої бізнес-логіки.

## Методологія п'ятиетапного аудиту карти регістрів

Аудит нового чипа виконується строго за п'ятьма послідовними етапами:

### Етап 1. Верифікація шинного зв'язку та ідентифікація чипа (Identity Check)
Перша дія під час першого ввімкнення — зчитування регістра `WHO_AM_I` (або `CHIP_ID` / `DEVICE_ID`) та порівняння отриманого байта з константою з даташита. Якщо замість очікуваного значення (наприклад, `0x6A`) чип повертає `0x00` або `0xFF`, це свідчить про апаратну проблему: відсутність підтягувальних резисторів на лініях I2C, неправильний рівень на піні вибору адреси (`AD0 / SA0`) або відсутність тактування на шині SPI.

Одночасно зчитується регістр версії кремнію (`REV_ID` / `SILICON_REV`), якщо він присутній. Номер ревізії звіряється з переліком Errata Sheet для виявлення потреби в активації спеціальних обхідних шляхів.

### Етап 2. Тестування запису конфігураційних регістрів (R/W Audit)
Мета цього етапу — переконатися, що регістри конфігурації справді приймають дані від мікроконтролера. Для цього використовується шаблон верифікації «запис — зчитування — порівняння» *(Write-Readback Verification)*. 

У конфігураційний регістр записується валідна тестова маска (наприклад, комбінація бітів вибору частоти ODR та увімкнення осей), після чого регістр вичитується назад. Якщо зчитане значення не збігається з записаним, перевіряють, чи не містить регістр зарезервованих бітів із фіксованим фабричним нулем або чи не перебуває чип у захищеному режимі блокування запису (Write Protect).

### Етап 3. Верифікація поведінки прапорців та семантики W1C
Статусні регістри, що сигналізують про готовність даних (`DRDY`) або переповнення буфера (`FIFO_OVERRUN`), часто мають апаратний тип доступу **W1C (Write 1 to Clear)**. 

Під час аудиту перевіряється:
1. Чи встановлюється прапорець `DRDY` після запуску вимірювального тракту.
2. Чи скидається прапорець у `0` при прямому запису бітової одиниці в його позицію.
3. Чи залишаються суміжні прапорці незмінними при запису нуля в інші розряди.

Будь-які спроби застосування класичного виразу `reg &= ~FLAG` тут категорично заборонені, оскільки це призводить до скидання всіх паралельних активних подій.

### Етап 4. Налаштування атомарності вибірок (BDU) та режимів роботи
Перед початком вимірювань обов'язково активується прапорець **Block Data Update (BDU)**. Це захищає від розриву багатобайтових чисел: коли процесор починає вичитувати молодший байт `OUT_X_L`, внутрішній цифровий конвеєр блокує оновлення старшого байта `OUT_X_H`, поки не буде завершено повну транзакцію.

Одночасно виставляються цільовий діапазон повної шкали (FSR) та бажаний темп опитування (ODR).

### Етап 5. Пакетне вичитування (Burst Read), порядок байтів та знакове розширення
Для вичитування всіх осей датчика використовується єдина безперервна транзакція. Під час аудиту перевіряється:
- Чи вимагає чип встановлення біта автоінкременту (наприклад, `0x80` для мікросхем STMicroelectronics).
- Як саме склеюються байти: у форматі Little-Endian (`(uint16_t)buf[0] | ((uint16_t)buf[1] << 8)`) чи Big-Endian.
- Чи коректно працює знакове розширення (Two's Complement) для від'ємних чисел (коли старший біт дорівнює `1`).
- Чи відповідає розраховане фізичне значення прискорення очікуваному значенню гравітації Землі (приблизно `+9.81 м/с²` або `-9.81 м/с²` на осі, орієнтованій вертикально, та близько `0 м/с²` на горизонтальних осях).

Нижче наведено повний автономний тестовий модуль аудиту карти регістрів двома мовами: чистим C із функціональними вказівниками на шинний транспорт та сучасним ідіоматичним C++20 з використанням концептів, переліків `enum class` та структурованої обробки помилок через `std::expected`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Оффсети регістрів 3-осьового акселерометра */
#define REG_WHO_AM_I        0x0F
#define REG_CTRL_REG1       0x20
#define REG_CTRL_REG2       0x21
#define REG_STATUS_REG      0x27
#define REG_OUT_X_L         0x28
#define REG_OUT_X_H         0x29
#define REG_OUT_Y_L         0x2A
#define REG_OUT_Y_H         0x2B
#define REG_OUT_Z_L         0x2C
#define REG_OUT_Z_H         0x2D

/* Очікувані константи та бітові маски */
#define CHIP_ID_EXPECTED    0x6A
#define I2C_AUTO_INCREMENT  0x80  /* Старший біт адреси для Burst-читання ST-чипів */

/* CTRL_REG1 біти: [7:4 ODR] [3:2 PowerMode] [1:0 AxesEnable] */
#define CTRL1_ODR_100HZ     (0x04 << 4)
#define CTRL1_AXES_XYZ_EN   (0x07 << 0)

/* CTRL_REG2 біти: [7 BDU] [5:4 FSR] */
#define CTRL2_BDU_ENABLE    (1 << 7)
#define CTRL2_FSR_2G        (0x00 << 4)
#define CTRL2_FSR_4G        (0x01 << 4)

/* STATUS_REG біти (W1C або RO) */
#define STATUS_ZYXDA        (1 << 3)  /* Дані по всіх 3 осях готові */
#define STATUS_FIFO_OVR     (1 << 6)  /* Переповнення буфера FIFO */

/* Коди повернення процедури аудиту */
typedef enum {
    AUDIT_OK = 0,
    AUDIT_ERR_COMM = -1,
    AUDIT_ERR_INVALID_ID = -2,
    AUDIT_ERR_REG_RW_FAIL = -3,
    AUDIT_ERR_TIMEOUT = -4
} audit_status_t;

/* Структура абстракції апаратного транспорту шини */
typedef struct {
    void *bus_ctx;
    uint8_t dev_addr;
    int (*read_reg)(void *ctx, uint8_t dev_addr, uint8_t reg, uint8_t *buf, size_t len);
    int (*write_reg)(void *ctx, uint8_t dev_addr, uint8_t reg, const uint8_t *buf, size_t len);
} sensor_bus_t;

/* Результат вимірювання у фізичних одиницях SI (м/с²) */
typedef struct {
    float x;
    float y;
    float z;
} accel_data_t;

/* 1. Аудит ідентифікатора чипа */
audit_status_t sensor_verify_identity(const sensor_bus_t *bus) {
    uint8_t chip_id = 0;
    if (bus->read_reg(bus->bus_ctx, bus->dev_addr, REG_WHO_AM_I, &chip_id, 1) != 0) {
        return AUDIT_ERR_COMM;
    }
    if (chip_id != CHIP_ID_EXPECTED) {
        return AUDIT_ERR_INVALID_ID;
    }
    return AUDIT_OK;
}

/* 2. Аудит доступності запису в R/W регістр без сліпих побічних ефектів */
audit_status_t sensor_audit_rw_register(const sensor_bus_t *bus) {
    uint8_t original_val = 0;
    uint8_t test_val = CTRL1_ODR_100HZ | CTRL1_AXES_XYZ_EN;
    uint8_t readback_val = 0;

    /* Зберігаємо початковий стан регістра */
    if (bus->read_reg(bus->bus_ctx, bus->dev_addr, REG_CTRL_REG1, &original_val, 1) != 0) {
        return AUDIT_ERR_COMM;
    }

    /* Записуємо тестову конфігурацію */
    if (bus->write_reg(bus->bus_ctx, bus->dev_addr, REG_CTRL_REG1, &test_val, 1) != 0) {
        return AUDIT_ERR_COMM;
    }

    /* Зчитуємо назад і порівнюємо */
    if (bus->read_reg(bus->bus_ctx, bus->dev_addr, REG_CTRL_REG1, &readback_val, 1) != 0) {
        return AUDIT_ERR_COMM;
    }

    if (readback_val != test_val) {
        return AUDIT_ERR_REG_RW_FAIL;
    }

    return AUDIT_OK;
}

/* 3. Ініціалізація: блокування BDU + шкала FSR + частота ODR */
audit_status_t sensor_init_configuration(const sensor_bus_t *bus) {
    uint8_t ctrl2 = CTRL2_BDU_ENABLE | CTRL2_FSR_2G;
    if (bus->write_reg(bus->bus_ctx, bus->dev_addr, REG_CTRL_REG2, &ctrl2, 1) != 0) {
        return AUDIT_ERR_COMM;
    }

    uint8_t ctrl1 = CTRL1_ODR_100HZ | CTRL1_AXES_XYZ_EN;
    if (bus->write_reg(bus->bus_ctx, bus->dev_addr, REG_CTRL_REG1, &ctrl1, 1) != 0) {
        return AUDIT_ERR_COMM;
    }

    return AUDIT_OK;
}

/* 4. Пакетне вичитування даних та перетворення у фізичну величину */
audit_status_t sensor_read_acceleration(const sensor_bus_t *bus, accel_data_t *out_data) {
    uint8_t raw_buf[6];
    uint8_t start_reg = REG_OUT_X_L | I2C_AUTO_INCREMENT;

    /* Пакетне читання 6 регістрів поспіль за одну транзакцію */
    if (bus->read_reg(bus->bus_ctx, bus->dev_addr, start_reg, raw_buf, 6) != 0) {
        return AUDIT_ERR_COMM;
    }

    /* Склеювання байтів Little-Endian у 16-бітні знакові числа */
    int16_t raw_x = (int16_t)((uint16_t)raw_buf[0] | ((uint16_t)raw_buf[1] << 8));
    int16_t raw_y = (int16_t)((uint16_t)raw_buf[2] | ((uint16_t)raw_buf[3] << 8));
    int16_t raw_z = (int16_t)((uint16_t)raw_buf[4] | ((uint16_t)raw_buf[5] << 8));

    /* Масштабування: для FSR = ±2g чутливість становить 0.061 мг/LSB */
    const float sensitivity_g_per_lsb = 0.000061f;
    const float g_to_ms2 = 9.80665f;

    out_data->x = (float)raw_x * sensitivity_g_per_lsb * g_to_ms2;
    out_data->y = (float)raw_y * sensitivity_g_per_lsb * g_to_ms2;
    out_data->z = (float)raw_z * sensitivity_g_per_lsb * g_to_ms2;

    return AUDIT_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <concepts>

namespace driver {

/* Типізовані оффсети регістрів чипа */
enum class Reg : uint8_t {
    WhoAmI       = 0x0F,
    Ctrl1        = 0x20,
    Ctrl2        = 0x21,
    Status       = 0x27,
    OutXL        = 0x28,
    OutXH        = 0x29,
    OutYL        = 0x2A,
    OutYH        = 0x2B,
    OutZL        = 0x2C,
    OutZH        = 0x2D
};

/* Концепт абстракції апаратного транспорту шини */
template <typename T>
concept BusTransport = requires(T transport, uint8_t dev_addr, Reg reg, std::span<uint8_t> rx, std::span<const uint8_t> tx) {
    { transport.read(dev_addr, reg, rx) } -> std::same_as<bool>;
    { transport.write(dev_addr, reg, tx) } -> std::same_as<bool>;
};

enum class SensorError {
    BusError,
    InvalidDeviceIdentifier,
    RegisterVerificationMismatch,
    DataNotReady,
    OverrunDetected
};

struct AccelSample {
    float x_ms2;
    float y_ms2;
    float z_ms2;
};

template <BusTransport Transport>
class AccelSensor {
public:
    constexpr explicit AccelSensor(Transport& transport, uint8_t dev_addr = 0x6A) noexcept
        : transport_(transport), dev_addr_(dev_addr) {}

    /* 1. Верифікація ID чипа */
    [[nodiscard]] std::expected<void, SensorError> verify_identity() noexcept {
        uint8_t id = 0;
        if (!read_single_reg(Reg::WhoAmI, id)) {
            return std::unexpected(SensorError::BusError);
        }
        if (id != ExpectedChipId) {
            return std::unexpected(SensorError::InvalidDeviceIdentifier);
        }
        return {};
    }

    /* 2. Аудит запису конфігураційних регістрів */
    [[nodiscard]] std::expected<void, SensorError> audit_configuration() noexcept {
        constexpr uint8_t test_mask = Ctrl1Odr100Hz | Ctrl1AxesXyz;
        if (!write_single_reg(Reg::Ctrl1, test_mask)) {
            return std::unexpected(SensorError::BusError);
        }

        uint8_t readback = 0;
        if (!read_single_reg(Reg::Ctrl1, readback)) {
            return std::unexpected(SensorError::BusError);
        }

        if (readback != test_mask) {
            return std::unexpected(SensorError::RegisterVerificationMismatch);
        }
        return {};
    }

    /* 3. Ініціалізація BDU та діапазону чутливості */
    [[nodiscard]] std::expected<void, SensorError> initialize() noexcept {
        constexpr uint8_t ctrl2_val = Ctrl2BduEnable | Ctrl2Fsr2G;
        if (!write_single_reg(Reg::Ctrl2, ctrl2_val)) {
            return std::unexpected(SensorError::BusError);
        }

        constexpr uint8_t ctrl1_val = Ctrl1Odr100Hz | Ctrl1AxesXyz;
        if (!write_single_reg(Reg::Ctrl1, ctrl1_val)) {
            return std::unexpected(SensorError::BusError);
        }
        return {};
    }

    /* 4. Пакетне вичитування осей */
    [[nodiscard]] std::expected<AccelSample, SensorError> read_acceleration() noexcept {
        uint8_t buffer[6] = {};
        /* Встановлюємо старший біт адреси для автоінкременту в I2C */
        const auto burst_reg = static_cast<Reg>(static_cast<uint8_t>(Reg::OutXL) | AutoIncrementFlag);

        if (!transport_.read(dev_addr_, burst_reg, std::span{buffer})) {
            return std::unexpected(SensorError::BusError);
        }

        const auto raw_x = static_cast<int16_t>(static_cast<uint16_t>(buffer[0]) | (static_cast<uint16_t>(buffer[1]) << 8));
        const auto raw_y = static_cast<int16_t>(static_cast<uint16_t>(buffer[2]) | (static_cast<uint16_t>(buffer[3]) << 8));
        const auto raw_z = static_cast<int16_t>(static_cast<uint16_t>(buffer[4]) | (static_cast<uint16_t>(buffer[5]) << 8));

        constexpr float Sensitivity = 0.000061f; // 0.061 мг/LSB
        constexpr float Gravity = 9.80665f;

        return AccelSample{
            .x_ms2 = static_cast<float>(raw_x) * Sensitivity * Gravity,
            .y_ms2 = static_cast<float>(raw_y) * Sensitivity * Gravity,
            .z_ms2 = static_cast<float>(raw_z) * Sensitivity * Gravity
        };
    }

private:
    static constexpr uint8_t ExpectedChipId    = 0x6A;
    static constexpr uint8_t AutoIncrementFlag = 0x80;

    static constexpr uint8_t Ctrl1Odr100Hz     = (0x04 << 4);
    static constexpr uint8_t Ctrl1AxesXyz      = (0x07 << 0);
    static constexpr uint8_t Ctrl2BduEnable    = (1 << 7);
    static constexpr uint8_t Ctrl2Fsr2G        = (0x00 << 4);

    Transport& transport_;
    uint8_t dev_addr_;

    bool read_single_reg(Reg reg, uint8_t& val) noexcept {
        return transport_.read(dev_addr_, reg, std::span<uint8_t, 1>{&val, 1});
    }

    bool write_single_reg(Reg reg, uint8_t val) noexcept {
        const uint8_t buf = val;
        return transport_.write(dev_addr_, reg, std::span<const uint8_t, 1>{&buf, 1});
    }
};

} // namespace driver
```
:::

## Чеклист аудиту карти регістрів перед передачею в експлуатацію

Перед тим як вважати драйвер завершеним і інтегрувати його у фінальну прошивку виробу, виконайте контрольний аудит за такими пунктами:

- [ ] **Адреса та ідентифікація:** підтверджено фактичну напругу на пінах конфігурації адреси (`SA0 / AD0`) та отримано точний збіг значення `WHO_AM_I` з таблицею даташита.
- [ ] **Затримка після ввімкнення (`t_boot` / `t_startup`):** у коді перед першим зверненням витримано паузу скидання за живленням (Power-on Reset) відповідно до таймінгів електричних характеристик.
- [ ] **Атомарність вибірок (BDU):** біт блокування оновлення буфера активовано, виключаючи розрив між старшим і молодшим байтами при повільному чиненні шини.
- [ ] **Типи доступу статусних регістрів:** перевірено, чи є регістр прапорців переривання типом W1C або COR; з коду усунено будь-які деструктивні конструкції Read-Modify-Write над статусами.
- [ ] **Автоінкремент адреси:** перевірено, чи вимагає шинний інтерфейс маскування біта 7 (STMicroelectronics) або прапорця у командному слові (TI/Analog Devices) для коректного Burst-зчитування.
- [ ] **Склеювання та знакове розширення:** підтверджено формат числа (Two's Complement, Left/Right aligned) та перевірено поведінку від'ємних значень на тестових відліках зі старшим бітом '1'.
- [ ] **Апаратний листок помилок (Errata Sheet):** перевірено номер поточної ревізії кристала на платі проти реєстру відомих багів виробника, необхідні обхідні шляхи реалізовано та протестовано на стенді.
