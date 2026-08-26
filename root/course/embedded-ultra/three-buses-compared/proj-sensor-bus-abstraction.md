# ⚙️ Уніфікований драйвер шин та датчиків автопілота

У польотних контролерах безпілотних апаратів програмний контур стабілізації оперує фізичними величинами — вектором кутової швидкості, прискоренням, тиском та напругою живлення. Якщо прив'язати алгоритми обробки безпосередньо до регістрів конкретної мікросхеми чи низькорівневих функцій периферії, будь-яка зміна ревізії плати або перехід на інший тип інтерфейсу (наприклад, перенесення барометра з внутрішньої шини I²C на зовнішню SPI) вимагає переписування всього коду навігації.

Уніфікований шар абстракції шини (Bus Abstraction Layer) розв'язує це завдання через розділення відповідальності на три незалежні рівні:
1. Рівень апаратного драйвера шини (HAL), який керує безпосередньо регістрами мікроконтролера, каналами прямого доступу до пам'яті (DMA), виводами вибору кристала (Chip Select) та обробниками переривань.
2. Рівень абстрактного дескриптора пристрою (`IBusDevice`), який надає драйверам сенсорів стандартизовані методи запису, зчитування та транзакційного обміну без розкриття типу фізичного середовища.
3. Рівень драйвера конкретного чипа (Sensor Driver), який знає карту регістрів, послідовності ініціалізації та формули перерахунку сирих двійкових слів у фізичні одиниці Міжнародної системи (SI).

```
+-------------------------------------------------------------------+
|               Рівень застосунку (EKF / PID Loop)                 |
+-------------------------------------------------------------------+
                                  │
                                  ▼
+-------------------------------------------------------------------+
|             Уніфікований інтерфейс датчика (ISensor)              |
|        read_sample() -> imu_data_t / baro_data_t                  |
+-------------------------------------------------------------------+
                                  │
                                  ▼
+-------------------------------------------------------------------+
|           Уніфікований інтерфейс пристрою шини (IBusDevice)       |
|       read_reg() | write_reg() | read_burst() | transfer()        |
+-------------------------------------------------------------------+
                 │                                   │
                 ▼                                   ▼
+---------------------------------+ +-------------------------------+
|      SpiBusDevice (SPI HAL)     | |     I2cBusDevice (I2C HAL)    |
| - Керування лінією CS (RAII)    | | - 7-біт адресація             |
| - Налаштування дільника SCK     | | - Відновлення шини (9 клоків) |
| - DMA пакетне зчитування        | | - Повторний START при читанні |
+---------------------------------+ +-------------------------------+
```

## Механіка взаємодії та вимоги до реалізації

При проектуванні шинного адаптера для критичних систем реального часу необхідно забезпечити виконання таких інваріантів:

1. **Атомарність транзакцій.** Якщо декілька задач в операційній системі реального часу (RTOS) або різні обробники переривань звертаються до однієї фізичної шини, будь-яка операція передачі повинна захищатися м'ютексом або критичною секцією. В іншому випадку запит зчитування барометра на шині I²C може вклинитися всередину транзакції компаса, що зіпсує внутрішній стан веденого чипа.
2. **Гарантоване зняття вибору мікросхеми.** На шині SPI лінія `CS` має повертатися у стан логічної одиниці навіть у разі помилки передачі або спрацювання тайм-ауту. Якщо лінія `CS` залишиться в нулі, чип не зможе розпізнати початок наступної команди, а всі інші пристрої на спільних лініях `MOSI`/`MISO` виявляться заблокованими. У мові C++ це досягається патерном RAII (Resource Acquisition Is Initialization), де деструктор локального об'єкта піднімає рівень на ніжці при виході з області видимості.
3. **Автоматичне відновлення шини I²C (Bus Clear Sequence).** Якщо ведений пристрій завис із затиснутою до землі лінією `SDA`, контролер не здатний згенерувати умову START чи STOP. Драйвер зобов'язаний виявити цей стан під час ініціалізації, перемкнути виводи в режим програмного керування (GPIO bit-banging), видати серію з 9 тактових імпульсів на лінії `SCL` та змусити ведений пристрій відпустити шину.
4. **Неблокуючий обмін через DMA для швидкісних каналів.** Зчитування 14 байтів вимірів IMU на частоті 8 кГц забирає надто багато процесорного часу при побайтовому опитуванні прапорців передачі (polling). Драйвер повинен ініціювати передачу через контролер прямого доступу до пам'яті й сповіщати про готовність даних сигналом переривання або бінарним семафором.
5. **Когерентність кешу даних (D-Cache Coherency).** На високоефективних ядрах (ARM Cortex-M7 / Cortex-M33) контролер DMA пише дані безпосередньо в системну оперативну пам'ять (SRAM), оминаючи кеш ядра L1. Перед передачею буфера через DMA процесор повинен виконати очищення кешу (`SCB_CleanDCache_by_Addr`), а після завершення прийому — інвалідацію кешу (`SCB_InvalidateDCache_by_Addr`), інакше алгоритм стабілізації прочитає застарілі дані з кеш-ліній.

Нижче наведено повну реалізацію адаптерів та драйверів мовами C та C++.

:::tabs
```c
/* ============================================================================
 * bus_hal.h & bus_hal.c — Уніфікований шар шин автопілота на C
 * ============================================================================ */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коди результатів операцій на шині */
typedef enum {
    BUS_OK = 0,
    BUS_ERR_TIMEOUT,
    BUS_ERR_NACK,
    BUS_ERR_ARBITRATION_LOST,
    BUS_ERR_INVALID_PARAM,
    BUS_ERR_BUSY
} bus_status_t;

/* Опереджувальне оголошення дескриптора пристрою */
typedef struct bus_device bus_device_t;

/* Таблиця віртуальних методів операцій шини */
typedef struct {
    bus_status_t (*write_reg)(const bus_device_t *dev, uint8_t reg, const uint8_t *data, size_t len);
    bus_status_t (*read_reg)(const bus_device_t *dev, uint8_t reg, uint8_t *data, size_t len);
    bus_status_t (*transfer)(const bus_device_t *dev, const uint8_t *tx, uint8_t *rx, size_t len);
} bus_ops_t;

/* Загальний дескриптор пристрою на шині */
struct bus_device {
    const bus_ops_t *ops;
    void *bus_handle;       /* Вказівник на апаратний дескриптор (SPI_TypeDef, I2C_TypeDef) */
    uint32_t config_param;  /* Номер ніжки CS для SPI або 7-бітна адреса для I2C */
};

/* ----------------------------------------------------------------------------
 * Реалізація адаптера SPI
 * ---------------------------------------------------------------------------- */
extern void gpio_pin_write(uint32_t pin, bool level);
extern bus_status_t spi_hardware_transfer(void *spi_inst, const uint8_t *tx, uint8_t *rx, size_t len);

static bus_status_t spi_dev_write_reg(const bus_device_t *dev, uint8_t reg, const uint8_t *data, size_t len) {
    uint32_t cs_pin = dev->config_param;
    uint8_t reg_header = reg & 0x7F; /* Біт 7 = 0 для запису в типових SPI-сенсорах */

    gpio_pin_write(cs_pin, false); /* Активуємо Chip Select (Active LOW) */
    
    bus_status_t status = spi_hardware_transfer(dev->bus_handle, &reg_header, NULL, 1);
    if (status == BUS_OK && len > 0 && data != NULL) {
        status = spi_hardware_transfer(dev->bus_handle, data, NULL, len);
    }
    
    gpio_pin_write(cs_pin, true); /* Деактивуємо Chip Select */
    return status;
}

static bus_status_t spi_dev_read_reg(const bus_device_t *dev, uint8_t reg, uint8_t *data, size_t len) {
    uint32_t cs_pin = dev->config_param;
    uint8_t reg_header = reg | 0x80; /* Біт 7 = 1 для читання */

    gpio_pin_write(cs_pin, false);
    
    bus_status_t status = spi_hardware_transfer(dev->bus_handle, &reg_header, NULL, 1);
    if (status == BUS_OK && len > 0 && data != NULL) {
        status = spi_hardware_transfer(dev->bus_handle, NULL, data, len);
    }
    
    gpio_pin_write(cs_pin, true);
    return status;
}

static bus_status_t spi_dev_transfer(const bus_device_t *dev, const uint8_t *tx, uint8_t *rx, size_t len) {
    uint32_t cs_pin = dev->config_param;
    gpio_pin_write(cs_pin, false);
    bus_status_t status = spi_hardware_transfer(dev->bus_handle, tx, rx, len);
    gpio_pin_write(cs_pin, true);
    return status;
}

static const bus_ops_t g_spi_bus_ops = {
    .write_reg = spi_dev_write_reg,
    .read_reg  = spi_dev_read_reg,
    .transfer  = spi_dev_transfer
};

void spi_device_init(bus_device_t *dev, void *spi_inst, uint32_t cs_pin) {
    dev->ops = &g_spi_bus_ops;
    dev->bus_handle = spi_inst;
    dev->config_param = cs_pin;
    gpio_pin_write(cs_pin, true);
}

/* ----------------------------------------------------------------------------
 * Реалізація адаптера I2C з процедурою відновлення шини (Bus Recovery)
 * ---------------------------------------------------------------------------- */
extern bus_status_t i2c_hardware_write(void *i2c_inst, uint8_t addr, uint8_t reg, const uint8_t *data, size_t len);
extern bus_status_t i2c_hardware_read(void *i2c_inst, uint8_t addr, uint8_t reg, uint8_t *data, size_t len);
extern void i2c_gpio_mode_set_gpio(void);
extern void i2c_gpio_mode_set_hardware(void);
extern bool i2c_gpio_read_sda(void);
extern void i2c_gpio_write_scl(bool level);
extern void i2c_gpio_write_sda(bool level);
extern void delay_us(uint32_t us);

/* Апаратне відновлення шини I2C при зависанні веденого пристрою в стані LOW */
void i2c_bus_recover(void) {
    i2c_gpio_mode_set_gpio();
    i2c_gpio_write_sda(true);
    i2c_gpio_write_scl(true);
    delay_us(5);

    /* Якщо лінія SDA притиснута до землі, генеруємо до 9 імпульсів SCL */
    for (int i = 0; i < 9; i++) {
        if (i2c_gpio_read_sda()) {
            break; /* Ведений пристрій відпустив лінію SDA */
        }
        i2c_gpio_write_scl(false);
        delay_us(5);
        i2c_gpio_write_scl(true);
        delay_us(5);
    }

    /* Формуємо примусову умову STOP: перехід SDA з LOW у HIGH при високому SCL */
    i2c_gpio_write_sda(false);
    delay_us(5);
    i2c_gpio_write_scl(true);
    delay_us(5);
    i2c_gpio_write_sda(true);
    delay_us(5);

    i2c_gpio_mode_set_hardware();
}

static bus_status_t i2c_dev_write_reg(const bus_device_t *dev, uint8_t reg, const uint8_t *data, size_t len) {
    uint8_t addr = (uint8_t)dev->config_param;
    bus_status_t status = i2c_hardware_write(dev->bus_handle, addr, reg, data, len);
    if (status == BUS_ERR_TIMEOUT) {
        i2c_bus_recover();
    }
    return status;
}

static bus_status_t i2c_dev_read_reg(const bus_device_t *dev, uint8_t reg, uint8_t *data, size_t len) {
    uint8_t addr = (uint8_t)dev->config_param;
    bus_status_t status = i2c_hardware_read(dev->bus_handle, addr, reg, data, len);
    if (status == BUS_ERR_TIMEOUT) {
        i2c_bus_recover();
    }
    return status;
}

static const bus_ops_t g_i2c_bus_ops = {
    .write_reg = i2c_dev_write_reg,
    .read_reg  = i2c_dev_read_reg,
    .transfer  = NULL /* I2C за своєю природою напівдуплексний */
};

void i2c_device_init(bus_device_t *dev, void *i2c_inst, uint8_t i2c_7bit_addr) {
    dev->ops = &g_i2c_bus_ops;
    dev->bus_handle = i2c_inst;
    dev->config_param = (uint32_t)i2c_7bit_addr;
}

/* ----------------------------------------------------------------------------
 * Драйвер IMU (ICM-42688-P) над уніфікованою шиною
 * ---------------------------------------------------------------------------- */
typedef struct {
    int16_t accel_x, accel_y, accel_z;
    int16_t gyro_x,  gyro_y,  gyro_z;
    int16_t temp;
} imu_raw_t;

bus_status_t icm42688_read_raw(const bus_device_t *dev, imu_raw_t *out) {
    uint8_t raw_buf[14];
    /* Адреса початкового регістра даних акселерометра ICM42688_REG_ACCEL_DATA_X1 = 0x1F */
    bus_status_t status = dev->ops->read_reg(dev, 0x1F, raw_buf, sizeof(raw_buf));
    if (status != BUS_OK) {
        return status;
    }

    out->accel_x = (int16_t)((raw_buf[0]  << 8) | raw_buf[1]);
    out->accel_y = (int16_t)((raw_buf[2]  << 8) | raw_buf[3]);
    out->accel_z = (int16_t)((raw_buf[4]  << 8) | raw_buf[5]);
    out->gyro_x  = (int16_t)((raw_buf[6]  << 8) | raw_buf[7]);
    out->gyro_y  = (int16_t)((raw_buf[8]  << 8) | raw_buf[9]);
    out->gyro_z  = (int16_t)((raw_buf[10] << 8) | raw_buf[11]);
    out->temp    = (int16_t)((raw_buf[12] << 8) | raw_buf[13]);
    return BUS_OK;
}
```
```cpp
/* ============================================================================
 * bus_hal.hpp — Уніфікований шар шин автопілота на ідіоматичному C++20
 * ============================================================================ */
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <concepts>

namespace avionics {

enum class BusError : uint8_t {
    Timeout,
    Nack,
    ArbitrationLost,
    InvalidParam,
    Busy
};

/* Контракт абстрактного пристрою на довільній послідовній шині */
class IBusDevice {
public:
    virtual ~IBusDevice() = default;
    virtual std::expected<void, BusError> write_reg(uint8_t reg, std::span<const uint8_t> data) = 0;
    virtual std::expected<void, BusError> read_reg(uint8_t reg, std::span<uint8_t> data) = 0;
    virtual std::expected<void, BusError> transfer(std::span<const uint8_t> tx, std::span<uint8_t> rx) = 0;
};

/* Апаратні функції платформи */
extern void gpio_pin_write(uint32_t pin, bool level);
extern std::expected<void, BusError> spi_hw_xfer(void* inst, std::span<const uint8_t> tx, std::span<uint8_t> rx);
extern std::expected<void, BusError> i2c_hw_write(void* inst, uint8_t addr, uint8_t reg, std::span<const uint8_t> data);
extern std::expected<void, BusError> i2c_hw_read(void* inst, uint8_t addr, uint8_t reg, std::span<uint8_t> data);
extern void i2c_hw_recover();

/* RAII-обгортка для автоматичного керування вибором мікросхеми CS */
class ChipSelectGuard {
public:
    explicit ChipSelectGuard(uint32_t cs_pin) noexcept : cs_pin_(cs_pin) {
        gpio_pin_write(cs_pin_, false); /* CS Active LOW */
    }
    ~ChipSelectGuard() noexcept {
        gpio_pin_write(cs_pin_, true);  /* CS High (Idle) */
    }
    ChipSelectGuard(const ChipSelectGuard&) = delete;
    ChipSelectGuard& operator=(const ChipSelectGuard&) = delete;

private:
    uint32_t cs_pin_;
};

/* Реалізація для пристрою на шині SPI */
class SpiBusDevice final : public IBusDevice {
public:
    constexpr SpiBusDevice(void* spi_inst, uint32_t cs_pin) noexcept
        : spi_inst_(spi_inst), cs_pin_(cs_pin) {
        gpio_pin_write(cs_pin_, true);
    }

    std::expected<void, BusError> write_reg(uint8_t reg, std::span<const uint8_t> data) override {
        ChipSelectGuard cs(cs_pin_);
        uint8_t reg_header = reg & 0x7FU;
        auto res = spi_hw_xfer(spi_inst_, std::span(&reg_header, 1), {});
        if (!res) return res;
        if (!data.empty()) {
            return spi_hw_xfer(spi_inst_, data, {});
        }
        return {};
    }

    std::expected<void, BusError> read_reg(uint8_t reg, std::span<uint8_t> data) override {
        ChipSelectGuard cs(cs_pin_);
        uint8_t reg_header = reg | 0x80U;
        auto res = spi_hw_xfer(spi_inst_, std::span(&reg_header, 1), {});
        if (!res) return res;
        if (!data.empty()) {
            return spi_hw_xfer(spi_inst_, {}, data);
        }
        return {};
    }

    std::expected<void, BusError> transfer(std::span<const uint8_t> tx, std::span<uint8_t> rx) override {
        ChipSelectGuard cs(cs_pin_);
        return spi_hw_xfer(spi_inst_, tx, rx);
    }

private:
    void* spi_inst_;
    uint32_t cs_pin_;
};

/* Реалізація для пристрою на шині I2C */
class I2cBusDevice final : public IBusDevice {
public:
    constexpr I2cBusDevice(void* i2c_inst, uint8_t addr_7bit) noexcept
        : i2c_inst_(i2c_inst), addr_7bit_(addr_7bit) {}

    std::expected<void, BusError> write_reg(uint8_t reg, std::span<const uint8_t> data) override {
        auto res = i2c_hw_write(i2c_inst_, addr_7bit_, reg, data);
        if (!res && res.error() == BusError::Timeout) {
            i2c_hw_recover();
        }
        return res;
    }

    std::expected<void, BusError> read_reg(uint8_t reg, std::span<uint8_t> data) override {
        auto res = i2c_hw_read(i2c_inst_, addr_7bit_, reg, data);
        if (!res && res.error() == BusError::Timeout) {
            i2c_hw_recover();
        }
        return res;
    }

    std::expected<void, BusError> transfer(std::span<const uint8_t>, std::span<uint8_t>) override {
        return std::unexpected(BusError::InvalidParam);
    }

private:
    void* i2c_inst_;
    uint8_t addr_7bit_;
};

/* Типізований драйвер IMU-сенсора */
struct ImuSample {
    float accel_x, accel_y, accel_z; /* у м/с² */
    float gyro_x,  gyro_y,  gyro_z;  /* у рад/с */
    float temp_c;                    /* у °C */
};

class Icm42688Driver {
public:
    explicit constexpr Icm42688Driver(IBusDevice& bus) noexcept : bus_(bus) {}

    std::expected<ImuSample, BusError> read_sensor() {
        std::array<uint8_t, 14> raw{};
        auto res = bus_.read_reg(0x1F, raw);
        if (!res) return std::unexpected(res.error());

        auto parse_i16 = [](uint8_t msb, uint8_t lsb) -> int16_t {
            return static_cast<int16_t>((static_cast<uint16_t>(msb) << 8) | lsb);
        };

        constexpr float ACCEL_SCALE = 9.80665f / 2048.0f; /* ±16g */
        constexpr float GYRO_SCALE  = 0.0174532925f / 16.4f; /* ±2000 dps */

        return ImuSample{
            .accel_x = parse_i16(raw[0],  raw[1])  * ACCEL_SCALE,
            .accel_y = parse_i16(raw[2],  raw[3])  * ACCEL_SCALE,
            .accel_z = parse_i16(raw[4],  raw[5])  * ACCEL_SCALE,
            .gyro_x  = parse_i16(raw[6],  raw[7])  * GYRO_SCALE,
            .gyro_y  = parse_i16(raw[8],  raw[9])  * GYRO_SCALE,
            .gyro_z  = parse_i16(raw[10], raw[11]) * GYRO_SCALE,
            .temp_c  = parse_i16(raw[12], raw[13]) / 132.48f + 25.0f
        };
    }

private:
    IBusDevice& bus_;
};

} // namespace avionics
```
:::

## Інженерний аналіз та крайові випадки

1. **Затримки перемикання лінії Chip Select.** Високошвидкісні SPI-чипи вимагають дотримання часових інтервалів між спадним фронтом `CS` та першим тактовим імпульсом `SCK` (Setup Time, зазвичай 10–50 нс), а також між останнім тактом і поверненням `CS` у високий стан (Hold Time). На сучасних мікроконтролерах із тактовою частотою ядра 400–480 МГц прямий запис у регістр GPIO виконується за 2–5 нс. Якщо апаратний блок SPI запускається занадто швидко після маніпуляції ніжкою `CS`, перший біт може бути спотворений. У таких випадках між перемиканням `CS` та записом у регістр передачі вставляють 2–4 інструкції `__NOP()`.

2. **Обробка NACK при відключеному або несправному датчику.** У разі втрати контакту в кабелі зовнішнього магнітометра шина I²C генерує помилку `BUS_ERR_NACK` уже на етапі передачі адреси. Драйвер вищого рівня не повинен зависати в нескінченній спробі повторного опитування у тому ж мілісекундному такті. Необхідно зафіксувати відмову вузла, перевести датчик у статус `UNHEALTHY` і сповістити алгоритм об'єднання вимірів (Sensor Fusion) про необхідність переходу на резервний чип або використання оцінки курсу лише за гіроскопом.

3. **Колізія дільників частоти при спільному використанні шини SPI.** Якщо на одній шині SPI паралельно працюють швидкісний IMU (підтримує частоту `SCK` до 24 МГц) та повільніший контролер дисплея OSD (максимум 10 МГц), конфігурація апаратного модуля SPI має динамічно перемикати передподільник (prescaler) перед активацією лінії `CS` відповідного пристрою. Шар абстракції шини інкапсулює це перемикання всередині методу передачі дескриптора пристрою.

4. **Діагностика за допомогою логічного аналізатора.** Під час відлагодження взаємодії сигналів шини рекомендується підключати 8-канальний цифровий аналізатор безпосередньо до тестових майданчиків (Test Points) біля сенсора. При аналізі сигналу SPI перевіряють відсутність викидів дзвінка на лінії `SCK`, стабільність сигналу `CS` під час усього пакета передачі та затримку готовності даних на лінії `MISO` (Data Valid Time). Для шини I²C перевіряють тривалість фронту наростання на осцилографі: якщо `t_rise` перевищує 300 нс при 400 кГц, необхідно зменшити номінал резисторів `R_p` (наприклад, з 4.7 кОм до 2.2 кОм або 1.5 кОм).
