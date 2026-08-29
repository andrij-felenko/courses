## Реконфігурація та відновлення стану драйвера (State Recovery)

Скидання мікросхеми за допомогою апаратного виводу nRESET або повного знеструмлення Power-Cycle повертає всі внутрішні регістри пристрою в значення за замовчуванням (Default Reset State). Якщо драйвер після перезапуску просто продовжить опитування даних без повторного налаштування, система зазнає критичного збою в алгоритмах керування. Наприклад, тривісний акселерометр повернеться в режим низької потужності зі зниженою частотою опитування 1 Гц і діапазоном чутливості $\pm 2\,\text{g}$ замість необхідних польотному контролеру 800 Гц і $\pm 16\,\text{g}$, а термометр зафіксує вимкнений стан вимірювального моста.

Повноцінне відновлення вимагає збереження та гарантованого поновлення робочого стану драйвера (**Driver State Restoration**).

### Тіньові регістри конфігурації (Shadow Registers)

Надійний драйвер ніколи не розраховує на те, що зовнішній чип пам'ятає свою конфігурацію. Драйвер підтримує у внутрішній структурі пам'яті RAM мікроконтролера точну копію всіх конфігураційних параметрів — блок тіньових регістрів (**Shadow Register Cache**):

1. **Кешовані параметри робочих режимів**:
   - Режим енергоспоживання (Continuous High-Performance, Low-Power, Single-Shot).
   - Частота вихідних даних (Output Data Rate, ODR) та коефіцієнт децимації цифрового фільтра низьких частот (Digital Low-Pass Filter, DLPF).
   - Повні діапазони вимірювання (Full-Scale Range) та коефіцієнти підсилення аналогового каскаду (PGA Gain).
   - Порогові рівні спрацьовування апаратних переривань (Interrupt Thresholds), режими активного рівня (Active-High/Active-Low) та тривалість імпульсу переривання.
2. **Фабричні калібрувальні коефіцієнти (Factory Trim / OTP Calibration Data)**:
   - Багато сучасних сенсорів (наприклад, барометри BMP280/BMP388, цифрові датчики температури та вологості, магнітометри) містять індивідуальні поліноміальні коефіцієнти калібрування, записані на заводі в одноразово програмовану пам'ять OTP (One-Time Programmable) або ROM.
   - Драйвер зчитує цей масив коефіцієнтів під час першого запуску системи та зберігає його в пам'яті мікроконтролера, захищаючи 16-бітною контрольною сумою CRC-16. Під час виконання процедур ескалації Tier 1 або Tier 2, коли живлення чипа не знімалося, повторне зчитування OTP можна пропустити за умови валідності CRC кешу, що заощаджує час відновлення. Проте після виконання Tier 3 (Power-Cycle) драйвер зобов'язаний заново вичитати фабричні коефіцієнти з чипа та звірити їх із кешованими значеннями.

### Стратегії повторних спроб (Retry Policies) та експоненційний відступ (Exponential Backoff)

Під час виникнення помилки зв'язку драйвер не повинен миттєво ініціювати максимальний рівень ескалації. Одиничний збій на лінії зв'язку може бути наслідком короткочасного електромагнітного імпульсу від спрацьовування сусіднього контактора, реле чи ШІМ-інвертора двигуна.

Стійкий драйвер реалізує кінцевий автомат градуйованого відновлення:

1. **Миттєвий повтор транзакції (Immediate Retry)**. Виконується 1 повторна спроба читання/запису без скидання периферії. Якщо збій був одиночним глітчем, транзакція успішно проходить із затримкою не більше кількох мікросекунд.
2. **Ескалація Tier 1 (Soft-Reset + 9 тактів I2C)**. Активується, якщо 2 послідовні транзакції завершилися з помилкою таймауту або NACK.
3. **Ескалація Tier 2 (Hardware nRESET)**. Активується, якщо після виконання Tier 1 чип не відповідає на діагностичний запит ідентифікатора або продовжує повертати помилки.
4. **Ескалація Tier 3 (Power-Cycle MOSFET)**. Застосовується у випадку, коли імпульс nRESET не відновив нормальне функціонування чипа.
5. **Аварійний стан (Fatal Failure / Safe State)**. Якщо після виконання повного циклу знеструмлення Power-Cycle сенсор не проходить перевірку ідентифікатора `WHO_AM_I`, драйвер фіксує відмову апаратного вузла, переводить підсистему в безпечний стан (Safe State), генерує тривожне повідомлення в журнал подій та сповіщає верхній рівень системи про неможливість подальшого використання датчика.

Для запобігання перевантаженню шини живлення та виникненню каскадних колізій (шторму відновлення, Recovery Storm), коли кілька сенсорів на одній шині одночасно намагаються перезапуститися, інтервал між спробами збільшують за алгоритмом **експоненційного відступу з випадковим джитером (Exponential Backoff with Jitter)**:

$$t_{\text{backoff}} = t_{\text{base}} \times 2^{\text{attempt}} + \text{jitter}$$

де $t_{\text{base}}$ — базовий інтервал очікування (наприклад, $10\,\text{ms}$), $\text{attempt}$ — номер поточної спроби, а $\text{jitter}$ — псевдовипадкова добавка в діапазоні $0\text{--}5\,\text{ms}$, розрахована на базі молодших бітів лічильника `DWT->CYCCNT`.

### Діагностична телеметрія та облік відмов

Для забезпечення надійної експлуатації та аналізу відмов у польових умовах драйвер веде внутрішню структуру статистики збоїв:

```c
typedef struct {
    uint32_t timeout_errors;        // Кількість таймаутів очікування прапорців
    uint32_t nack_errors;           // Кількість неотриманих підтверджень ACK
    uint32_t bus_stuck_errors;      // Кількість виявлених блокувань SDA=0
    uint32_t tier1_soft_resets;     // Кількість виконаних програмних скидань
    uint32_t tier2_pin_resets;      // Кількість апаратних імпульсів nRESET
    uint32_t tier3_power_cycles;    // Кількість повних циклів живлення
    uint32_t crc_errors;            // Кількість помилок контрольних сум даних
    uint32_t last_error_code;       // Код останньої зафіксованої помилки
} bus_diagnostics_t;
```

Ці лічильники зберігаються в енергонезалежній пам'яті (EEPROM/Flash) або передаються на диспетчерський пункт через промислові інтерфейси CAN, RS-485 або телеметрію дрона. Різке зростання кількості скидань Tier 2 або Tier 3 під час вібраційних випробувань однозначно вказує на дефект монтажу (нестабільний контакт роз'єму, недостатня ємність фільтруючих конденсаторів або погана якість пайки), дозволяючи локалізувати та усунути проблему до виходу виробу в серійну експлуатацію.

Детальна розробка закінченого апаратного контролера відновлення шини з повною підтримкою всіх трьох рівнів ескалації, діагностичним кільцевим буфером і вимірюванням часових констант розряду наведена в практичній вставці [proj-bus-recovery-controller.md](root:sf-devices/taimauty-pomylky-i-povtorna-initsializatsiia-chypa/proj-bus-recovery-controller.md).

## Стійкий каркас драйвера: архітектурні шаблони C99 та C++20

Об'єднаємо всі розглянуті механізми (детерміновані таймаути, 9-тактове відновлення шини, трирівневу ескалацію та відновлення тіньових регістрів) у єдину цілісну архітектурну модель драйвера периферійного пристрою.

### Патерн драйвера в мові C99

У C99 стійкий драйвер будують на основі структури екземпляра пристрою (`sensor_device_t`), яка інкапсулює апаратні ресурси, стан тіньових регістрів та лічильники помилок. Усі функції драйвера повертають строгий знаковий чи перелічуваний код статусу `bus_status_t`.

### Патерн драйвера в мові C++20

У C++20 драйвер реалізують як шаблонний клас із нульовою вартістю абстракцій (Zero-Cost Abstractions). Апаратні інтерфейси передаються як шаблонні параметри з перевіркою концептів (`concepts`), що виключає оверхед віртуальних викликів і покажчиків на функції, дозволяючи компілятору повністю вбудовувати низькорівневий код (Inlining).

Обробка помилок організована через тип `std::expected<T, BusError>`, що гарантує на етапі компіляції неможливість використання прочитаних даних без перевірки статусу операції.

:::tabs
@tab C99
```c
#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"

typedef struct {
    // Апаратні ресурси
    I2C_TypeDef *i2c;
    GPIO_TypeDef *scl_port;
    uint16_t scl_pin;
    GPIO_TypeDef *sda_port;
    uint16_t sda_pin;
    GPIO_TypeDef *nrst_port;
    uint16_t nrst_pin;
    GPIO_TypeDef *pwr_port;
    uint16_t pwr_pin;

    // Конфігурація
    uint8_t dev_addr;
    uint8_t expected_id;

    // Тіньові регістри (кеш)
    uint8_t shadow_ctrl_reg;
    uint8_t shadow_config_reg;

    // Лічильники відмов
    uint8_t consecutive_errors;
    uint32_t total_recoveries;
} sensor_device_t;

int sensor_read_register(sensor_device_t *dev, uint8_t reg, uint8_t *val);
int sensor_write_register(sensor_device_t *dev, uint8_t reg, uint8_t val);
int sensor_recover_escalation(sensor_device_t *dev);

int sensor_init(sensor_device_t *dev) {
    uint8_t id = 0;
    int res = sensor_read_register(dev, 0x0F /* WHO_AM_I */, &id);
    if (res != 0 || id != dev->expected_id) {
        return sensor_recover_escalation(dev);
    }

    // Записуємо робочі конфігураційні регістри
    dev->shadow_ctrl_reg = 0x57;   // ODR = 100 Hz, всі осі увімкнено
    dev->shadow_config_reg = 0x08; // Діапазон +/-4g
    res = sensor_write_register(dev, 0x20, dev->shadow_ctrl_reg);
    if (res != 0) return sensor_recover_escalation(dev);

    res = sensor_write_register(dev, 0x21, dev->shadow_config_reg);
    if (res != 0) return sensor_recover_escalation(dev);

    dev->consecutive_errors = 0;
    return 0; // Успішно ініціалізовано
}

int sensor_recover_escalation(sensor_device_t *dev) {
    dev->consecutive_errors++;
    dev->total_recoveries++;

    // Рівень 1: Розблокування шини 9 тактами + Soft-Reset
    if (dev->consecutive_errors == 1) {
        // Спроба відправити Soft-Reset команду
        uint8_t reset_cmd = 0xB6;
        sensor_write_register(dev, 0x25, reset_cmd);
    }
    // Рівень 2: Імпульс nRESET
    else if (dev->consecutive_errors == 2 && dev->nrst_port) {
        dev->nrst_port->BSRR = (1U << (dev->nrst_pin + 16)); // Low
        dev->nrst_port->BSRR = (1U << dev->nrst_pin);        // High
    }
    // Рівень 3: Повний Power-Cycle
    else if (dev->consecutive_errors >= 3 && dev->pwr_port) {
        // chip_power_cycle
    }

    // Після будь-якого скидання перевіряємо працездатність зчитуванням ID
    uint8_t id = 0;
    if (sensor_read_register(dev, 0x0F, &id) == 0 && id == dev->expected_id) {
        // Відновлюємо конфігурацію з тіньових регістрів
        sensor_write_register(dev, 0x20, dev->shadow_ctrl_reg);
        sensor_write_register(dev, 0x21, dev->shadow_config_reg);
        dev->consecutive_errors = 0;
        return 0; // Відновлено
    }

    return -1; // Спроба відновлення невдала
}
```
@tab C++20
```cpp
#include <cstdint>
#include <expected>
#include <chrono>
#include "stm32f4xx.h"

template <typename BusInterface, typename PowerController>
class ResilientSensorDriver {
public:
    struct ShadowConfig {
        uint8_t ctrl_reg{0x57};
        uint8_t config_reg{0x08};
    };

    ResilientSensorDriver(BusInterface bus, PowerController power, uint8_t dev_addr, uint8_t expected_id) noexcept
        : bus_{bus}, power_{power}, dev_addr_{dev_addr}, expected_id_{expected_id} {}

    [[nodiscard]] std::expected<void, BusError> initialize() noexcept {
        auto check_id = [this]() -> std::expected<void, BusError> {
            auto id_res = bus_.read_byte(dev_addr_, 0x0F /* WHO_AM_I */);
            if (!id_res.has_value() || *id_res != expected_id_) {
                return std::unexpected(BusError::Nack);
            }
            return {};
        };

        if (!check_id().has_value()) {
            return recover_and_reconfigure();
        }

        // Запис конфігурації
        auto res1 = bus_.write_byte(dev_addr_, 0x20, shadow_cfg_.ctrl_reg);
        if (!res1.has_value()) return recover_and_reconfigure();

        auto res2 = bus_.write_byte(dev_addr_, 0x21, shadow_cfg_.config_reg);
        if (!res2.has_value()) return recover_and_reconfigure();

        consecutive_faults_ = 0;
        return {};
    }

    [[nodiscard]] std::expected<int16_t, BusError> read_measurement(uint8_t lsb_reg, uint8_t msb_reg) noexcept {
        auto lsb = bus_.read_byte(dev_addr_, lsb_reg);
        if (!lsb) {
            auto rec = recover_and_reconfigure();
            if (!rec) return std::unexpected(rec.error());
            return std::unexpected(lsb.error());
        }

        auto msb = bus_.read_byte(dev_addr_, msb_reg);
        if (!msb) {
            auto rec = recover_and_reconfigure();
            if (!rec) return std::unexpected(rec.error());
            return std::unexpected(msb.error());
        }

        consecutive_faults_ = 0;
        return static_cast<int16_t>((*msb << 8) | *lsb);
    }

private:
    BusInterface bus_;
    PowerController power_;
    uint8_t dev_addr_;
    uint8_t expected_id_;
    ShadowConfig shadow_cfg_{};
    uint8_t consecutive_faults_{0};

    [[nodiscard]] std::expected<void, BusError> recover_and_reconfigure() noexcept {
        ++consecutive_faults_;

        if (consecutive_faults_ == 1) {
            // Tier 1: Відновлення шини + Soft Reset
            bus_.recover_bus();
            bus_.write_byte(dev_addr_, 0x25, 0xB6);
        } else if (consecutive_faults_ == 2) {
            // Tier 2: Апаратний імпульс nRESET
            power_.pulse_reset_pin();
        } else {
            // Tier 3: Повний Power-Cycle MOSFET
            power_.execute_power_cycle();
            consecutive_faults_ = 0;
        }

        // Перевірка відновлення працездатності
        auto id_check = bus_.read_byte(dev_addr_, 0x0F);
        if (id_check && *id_check == expected_id_) {
            // Відновлення тіньових регістрів
            bus_.write_byte(dev_addr_, 0x20, shadow_cfg_.ctrl_reg);
            bus_.write_byte(dev_addr_, 0x21, shadow_cfg_.config_reg);
            consecutive_faults_ = 0;
            return {};
        }

        return std::unexpected(BusError::BusStuck);
    }
};
```
:::

Використання детермінованих монотонних таймаутів, процедури 9 тактів розблокування шини, градуйованої трирівневої ескалації та кешу тіньових регістрів перетворює вразливий лабораторний драйвер на надійний промисловий програмний компонент, здатний автономно відновлювати працездатність обладнання після найважчих апаратних збоїв.
