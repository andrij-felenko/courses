# ⚙️ Практична реалізація уніфікованого рівня транзакцій для I2C та SPI

Коли вбудована система керує групою сенсорів — інерційними вимірювальними модулями (IMU), барометрами, магнітометрами чи зовнішньою енергонезалежною пам'яттю Flash, — розробник неминуче стикається з вибором фізичної шини. Сучасні інтегральні мікросхеми, такі як Bosch BMI270, TDK ICM-42688 чи STMicroelectronics LSM6DSO, виготовляються з універсальним цифровим інтерфейсом: залежно від електричного підключення ніжки вибору протоколу або стану лінії Chip Select (CS) під час подачі живлення, кристал перемикає свій внутрішній кінцевий автомат або на шину I2C, або на шину SPI. Проте вбудоване програмне забезпечення часто пишуть під конкретну шину: виклики апаратного рівня (HAL) жорстко вшивають у тіло функцій зчитування даних акселерометра, перетворюючи драйвер на моноліт, непридатний для повторного використання.

Головна інженерна мета рівня транзакцій (Bus Transaction Layer) — провести жорстку лінію поділу між логікою внутрішніх регістрів мікросхеми та протоколом передачі байтів через фізичні лінії друкованої плати. Драйвер пристрою повинен оперувати виключно абстрактними операціями: «записати байт у регістр `0x1F`», «прочитати 6 послідовних байтів із регістра `0x12`» або «модифікувати бітове поле за маскою». Адаптер шини бере на себе всю низькорівневу рутину: форматування адресного кадру, формування сигналів Repeated START, керування лінією CS, врахування затримок встановлення (setup/hold time), маскування бітів читання/запису (R/W bit) та асинхронний обмін через DMA.

У цій практичній роботі побудовано завершений, промисловий шар транзакцій для мов C99 та C++20. Він містить абстрактний інтерфейс шини, конкретні адаптери для I2C та SPI, емулятор регістрової пам'яті (Mock Adapter) для автоматизованого тестування без заліза, а також драйвер 6-осьового IMU-сенсора, який однаково успішно працює на будь-якому фізичному транспорті.

---

### Фізичні відмінності шин та вимоги до кадрування

Щоб спроєктувати уніфікований інтерфейс, необхідно детально проаналізувати фізичні та протокольні відмінності між двопровідною шиною I2C та чотирипровідною шиною SPI. Кожна з них висуває специфічні вимоги до таймінгів, полярності сигналів та структури адресних пакетів.

Шина I2C використовує топологію з відкритим стоком (open-drain) та спільними підтягувальними резисторами до лінії живлення. Це забезпечує простоту маршрутизації (лише дві сигнальні лінії — SCL та SDA для десятків пристроїв), проте суттєво обмежує швидкість обміну (зазвичай 100 кГц у стандартному режимі Standard Mode або 400 кГц у Fast Mode). Передача кожного байта супроводжується обов'язковим дев'ятим тактом підтвердження (ACK/NACK). Адресація пристрою здійснюється першим байтом транзакції, де молодший біт задає напрям передачі (0 — запис, 1 — читання). Для читання внутрішнього регістра мікроконтролер мусить спершу виконати транзакцію запису (надіслати адресу регістра-вказівника), а потім, не відпускаючи шину сигналом STOP, сформувати умову повторного старту (Repeated START) та надіслати адресу пристрою з бітом читання. Якщо сформувати STOP замість Repeated START, інший майстер на мультимайстер-шині може перехопити керування, або внутрішній лічильник датчика скинеться в нульовий стан.

Шина SPI працює за повнодуплексною топологією з двотактними вихідними каскадами (push-pull). Це дозволяє досягати швидкостей тактування 10–50 МГц. Проте вибір веденого пристрою вимагає окремої фізичної лінії вибору кристала Chip Select (CS або NSS). У протоколі SPI немає стандартизованої адреси пристрою, а повнодуплексна природа вимагає, щоб на кожен зчитаний байт з лінії MISO майстер одночасно видавав такт і байт даних на лінію MOSI (зазвичай нуль `0x00` або dummy-байт). Крім того, виробники мікросхем використовують власні бітові маски для вказівки типу операції та поведінки внутрішнього лічильника адрес:
- **Bosch Sensortec (BMI270, BMP280)**: Старший біт (біт 7) адреси регістра під час читання повинен бути встановлений у `1` (`reg_addr | 0x80`), а під час запису — очищений у `0` (`reg_addr & 0x7F`). Для високих частот тактування SPI (>10 МГц) після передачі байта адреси кристал вимагає додаткового dummy-байта паузи перед тим, як дані з'являться на лінії MISO.
- **STMicroelectronics (LSM6DSO, LIS3DH)**: Біт 7 задає напрям (1 — читання, 0 — запис), а біт 6 задає автоінкремент адресного лічильника (`0x40`). Якщо біт 6 не підняти, кристал повертатиме значення того самого регістра знову і знову при спробі вичитати масив даних за одну транзакцію.
- **Analog Devices (ADXL345)**: Біт 7 задає читання, біт 6 — множинне зчитування (Multiple-byte burst).

Рівень транзакцій зобов'язаний інкапсулювати ці особливості всередині прапорців адаптера, звільняючи високорівневий драйвер від бітових масок конкретної шини.

---

### Математична модель тривалості транзакцій: I2C проти SPI

Для розуміння інженерної ціни вибору шини розрахуємо точний часовий бюджет зчитування 6-байтового пакета сирих даних (акселерометр X, Y, Z по 2 байти) з регістра `0x12`.

Для шини I2C у режимі Fast Mode (тактова частота `f_SCL = 400` кГц, період такту `T_SCL = 2.5` мкс):
1. Сигнал START та час витримки: `t_HD:STA ≈ 0.6` мкс.
2. Байт адреси пристрою з бітом Write (`0xD0`) + 1 біт ACK = 9 тактів = `22.5` мкс.
3. Байт адреси регістра (`0x12`) + 1 біт ACK = 9 тактів = `22.5` мкс.
4. Сигнал Repeated START: `t_SU:STA ≈ 0.6` мкс.
5. Байт адреси пристрою з бітом Read (`0xD1`) + 1 біт ACK = 9 тактів = `22.5` мкс.
6. Зчитування 6 байтів даних: кожні 8 бітів даних + 1 біт ACK/NACK = 6 × 9 тактів = `135.0` мкс.
7. Сигнал STOP та час вільного стану шини: `t_SU:STO + t_BUF ≈ 1.9` мкс.

Загальний час транзакції I2C:
```
T_total_i2c = 0.6 + 22.5 + 22.5 + 0.6 + 22.5 + 135.0 + 1.9 = 205.6 мкс.
```

Для шини SPI на помірній частоті `f_SCK = 10` МГц (період такту `T_SCK = 0.1` мкс):
1. Встановлення сигналу CS у низький рівень (setup time `t_CSS`): `0.05` мкс.
2. Передача 1 байта адреси регістра з прапорцем читання (`0x80 | 0x12`): 8 тактів = `0.8` мкс.
3. Зчитування 6 байтів даних (одночасна передача dummy-нулів): 6 × 8 тактів = `4.8` мкс.
4. Зняття сигналу CS у високий рівень (hold time `t_CSH`): `0.05` мкс.
5. Мінімальна пауза між транзакціями (CS High time `t_CS_HIGH`): `0.1` мкс.

Загальний час транзакції SPI:
```
T_total_spi = 0.05 + 0.8 + 4.8 + 0.05 + 0.1 = 5.8 мкс.
```

Шина SPI виконує те саме зчитування в **35 разів швидше**, звільняючи 200 мікросекунд процесорного часу або каналу DMA на кожній ітерації опитування. У системі стабілізації польоту безпілотного апарата з частотою циклу 1 кГц (бюджет 1000 мкс) транзакція I2C забрала б понад 20% усього доступного часу, тоді як SPI витрачає менше 0.6% бюджету.

---

### Електричні параметри ліній зв'язку та розрахунок компонентів

Надійність рівня транзакцій безпосередньо залежить від фізичного рівня друкованої плати. При проектуванні необхідно враховувати два ключові параметри: паразитну ємність шини та узгодження ліній зв'язку.

#### 1. Розрахунок підтягувальних резисторів I2C (Pull-Up Resistors)

За стандартом NXP I2C-bus specification, максимальна сумарна паразитна ємність ліній SCL та SDA становить `C_bus ≤ 400` пФ. Ця величина складається з ємності доріжок друкованої плати (~1–2 пФ/см), вхідної ємності ніжок мікроконтролера (~5–10 пФ) та вхідної ємності підключених ведених пристроїв (~10 пФ на кожен чіп).

Підтягувальний резистор `R_pullup` повинен задовольняти двом взаємно суперечливим умовам:
- **Мінімальний опір `R_min`**: обмежується максимально допустимим струмом вихідного транзистора з відкритим стоком `I_OL` (зазвичай 3 мА при падінні напруги `V_OL ≤ 0.4` В):
```
R_min = (V_DD - V_OL) / I_OL = (3.3 - 0.4) / 0.003 = 967 Ом.
```
Якщо встановити менший резистор, вихідний каскад не зможе притягнути лінію до логічного нуля, і транзакції падатимуть із помилкою `BUS_ERR_NACK`.

- **Максимальний опір `R_max`**: визначається максимально допустимим часом наростання фронту сигналу `t_r` (для Fast Mode 400 кГц `t_r ≤ 300` нс):
```
R_max = t_r / (0.8473 · C_bus)
```
При ємності шини `C_bus = 150` пФ:
```
R_max = 300·10⁻⁹ / (0.8473 · 150·10⁻¹²) ≈ 2360 Ом (2.36 кОм).
```
Оптимальний вибір для надійної роботи на частоті 400 кГц становить `2.2` кОм. Використання внутрішніх підтяжок мікроконтролера (Internal Pull-Up 30–50 кОм) є грубою помилкою: час наростання складе понад 4 мкс, що призведе до повного спотворення тактових імпульсів.

#### 2. Хвильовий опір та демпфування ліній SPI

На тактових частотах SPI 10–50 МГц довжина доріжки на платі може стати співрозмірною з довжиною хвилі фронту сигналу (час наростання сучасних виходів МК `t_rise ≈ 1–2` нс відповідає спектральним складовим понад 300 МГц). Якщо доріжка не узгоджена, на приймальному кінці виникають відбиття сигналу (ringing) та викиди напруги (overshoot), що сприймаються приймачем як хибні тактові імпульси.

Для придушення відбиття безпосередньо біля виводів передавача (SCK, MOSI та CS мікроконтролера, а також MISO сенсора) встановлюють послідовні демпфуючі резистори:
```
R_series = Z_0 - R_driver ≈ 50 - 20 = 22..33 Ом,
```
де `Z_0` — хвильовий опір доріжки на друкованій платі (~50 Ом), а `R_driver` — власний вихідний опір транзистора мікроконтролера (~15–25 Ом). Це повністю усуває дзвін і гарантує безпомилковий прийом байтів на високій швидкості.

---

### Архітектура та інтерфейс рівня транзакцій на C99

У мові C99 класичним та найбільш ефективним способом побудови поліморфного інтерфейсу без динамічного виділення пам'яті (`malloc`) є структура віртуальної таблиці функцій (`vtable`) у поєднанні з непрозорим контекстом користувача (`void *ctx` або типізований покажчик). 

Кожна транзакція повертає стандартизований код помилки `bus_status_t`, що дозволяє драйверу верхнього рівня розрізняти апаратні проблеми шини (відсутність підтвердження I2C NACK, таймаут тактування, обрив зв'язку) від логічних збоїв самого сенсора.

Нижче наведено заголовний файл `bus_transaction.h`, який визначає контракти взаємодії, типи транзакцій, прапорці конфігурації адрес та базову структуру інтерфейсу шини.

```c
/**
 * @file bus_transaction.h
 * @brief Уніфікований інтерфейс рівня транзакцій (Transaction Layer) на C99.
 */

#ifndef BUS_TRANSACTION_H_
#define BUS_TRANSACTION_H_

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Уніфіковані коди результату виконання транзакції.
 */
typedef enum {
    BUS_OK                =  0,  /**< Транзакція успішно завершена */
    BUS_ERR_INVALID_ARG   = -1,  /**< Некоректні вхідні параметри (NULL-покажчик, нульова довжина) */
    BUS_ERR_TIMEOUT       = -2,  /**< Таймаут очікування апаратного завершення обміну */
    BUS_ERR_NACK          = -3,  /**< Відсутність підтвердження адреси чи даних на шині I2C */
    BUS_ERR_ARBITRATION   = -4,  /**< Втрата арбітражу на мультимайстер-шині I2C */
    BUS_ERR_BUSY          = -5,  /**< Шина зайнята іншою транзакцією або заблокована */
    BUS_ERR_DMA           = -6,  /**< Апаратна помилка каналу прямого доступу до пам'яті */
    BUS_ERR_IO            = -7   /**< Фізична помилка ліній зв'язку або апаратного периферійного блоку */
} bus_status_t;

/**
 * @brief Прапорці кадрування протоколу та модифікації адресного байта.
 */
typedef enum {
    BUS_FLAG_NONE          = 0x00, /**< Стандартне кадрування без модифікації адреси */
    BUS_FLAG_SPI_READ_MSB  = 0x01, /**< SPI: Встановити біт 7 у '1' для операції читання (Bosch/InvenSense) */
    BUS_FLAG_SPI_READ_LSB  = 0x02, /**< SPI: Встановити біт 0 у '1' для читання (Analog Devices) */
    BUS_FLAG_AUTO_INC      = 0x04, /**< SPI: Встановити біт 6 у '1' для автоінкременту регістрів (STMicro) */
    BUS_FLAG_REG_16BIT     = 0x08, /**< 16-бітна адреса регістрів замість стандартної 8-бітної */
    BUS_FLAG_USE_DUMMY     = 0x10  /**< Необхідність передачі 1 dummy-байта перед даними при швидкісному SPI */
} bus_flags_t;

/* Попереднє оголошення інтерфейсу шини */
typedef struct bus_interface bus_interface_t;

/**
 * @brief Віртуальна таблиця операцій шини (Bus VTable).
 */
typedef struct {
    /**
     * @brief Зчитування послідовності байтів із вказаного регістра.
     */
    bus_status_t (*read_reg)(void *ctx, uint16_t reg_addr, uint8_t *data, size_t len);

    /**
     * @brief Запис послідовності байтів у вказаний регістр.
     */
    bus_status_t (*write_reg)(void *ctx, uint16_t reg_addr, const uint8_t *data, size_t len);

    /**
     * @brief Прямий повнодуплексний або напівдуплексний блоковий трансфер.
     */
    bus_status_t (*transfer)(void *ctx, const uint8_t *tx_data, uint8_t *rx_data, size_t len);

    /**
     * @brief Захоплення м'ютекса для блокування шини в RTOS.
     */
    bus_status_t (*lock)(void *ctx, uint32_t timeout_ms);

    /**
     * @brief Звільнення м'ютекса шини.
     */
    bus_status_t (*unlock)(void *ctx);
} bus_ops_t;

/**
 * @brief Загальний дескриптор шини.
 */
struct bus_interface {
    const bus_ops_t *ops;   /**< Таблиця функціональних покажчиків */
    void            *ctx;   /**< Приватний контекст апаратного адаптера */
    uint32_t         flags; /**< Набір прапорців bus_flags_t */
};

/* Допоміжні інлайн-обгортки для компактності коду драйвера */
static inline bus_status_t bus_read_reg(const bus_interface_t *bus, uint16_t reg, uint8_t *data, size_t len) {
    if (!bus || !bus->ops || !bus->ops->read_reg) return BUS_ERR_INVALID_ARG;
    return bus->ops->read_reg(bus->ctx, reg, data, len);
}

static inline bus_status_t bus_write_reg(const bus_interface_t *bus, uint16_t reg, const uint8_t *data, size_t len) {
    if (!bus || !bus->ops || !bus->ops->write_reg) return BUS_ERR_INVALID_ARG;
    return bus->ops->write_reg(bus->ctx, reg, data, len);
}

static inline bus_status_t bus_read_u8(const bus_interface_t *bus, uint16_t reg, uint8_t *val) {
    return bus_read_reg(bus, reg, val, 1);
}

static inline bus_status_t bus_write_u8(const bus_interface_t *bus, uint16_t reg, uint8_t val) {
    return bus_write_reg(bus, reg, &val, 1);
}

/**
 * @brief Атомарна модифікація бітів регістра (Read-Modify-Write).
 */
bus_status_t bus_modify_reg(const bus_interface_t *bus, uint16_t reg, uint8_t mask, uint8_t val);

#ifdef __cplusplus
}
#endif

#endif /* BUS_TRANSACTION_H_ */
```

Коли інтерфейс формалізовано, реалізуємо конкретні апаратні адаптери:
1. `i2c_adapter`: зберігає 7-бітну або 10-бітну адресу веденого пристрою на шині I2C, інкапсулює виклики низькорівневого контролера та формує транзакцію запису адреси регістра з наступним Repeated START для читання даних без звільнення шини.
2. `spi_adapter`: зберігає покажчик на функцію керування лінією Chip Select (GPIO CS), режим тактування, швидкість і прапорці модифікації байта адреси (наприклад, встановлення старшого біта `0x80` для операцій зчитування).
3. `mock_adapter`: програмна імітація регістрової пам'яті розміром 256 байтів для виконання модульних тестів без підключення фізичної плати.

Нижче наведено повну реалізацію адаптерів у файлі `bus_adapters.c`.

```c
/**
 * @file bus_adapters.c
 * @brief Реалізація адаптерів I2C, SPI та Mock у мові C99.
 */

#include "bus_transaction.h"
#include <string.h>

/* ============================================================================
 * Реалізація універсальної операції Read-Modify-Write
 * ============================================================================ */

bus_status_t bus_modify_reg(const bus_interface_t *bus, uint16_t reg, uint8_t mask, uint8_t val) {
    if (!bus) return BUS_ERR_INVALID_ARG;
    
    uint8_t current_val = 0;
    bus_status_t status = bus_read_u8(bus, reg, &current_val);
    if (status != BUS_OK) {
        return status;
    }

    uint8_t new_val = (current_val & ~mask) | (val & mask);
    if (new_val == current_val) {
        return BUS_OK; /* Значення вже встановлено, уникаємо зайвої транзакції */
    }

    return bus_write_u8(bus, reg, new_val);
}

/* ============================================================================
 * I2C Адаптер (I2C Adapter Context & Operations)
 * ============================================================================ */

typedef struct {
    uint8_t  dev_addr_7bit; /**< 7-бітна адреса пристрою на шині I2C */
    uint32_t timeout_ms;    /**< Таймаут виконання апаратної транзакції */
    void    *i2c_hal_handle;/**< Дескриптор апаратного контролера I2C */
} i2c_adapter_ctx_t;

/* Низькорівневі виклики емульованого HAL мікроконтролера */
extern int hal_i2c_master_transmit(void *handle, uint8_t addr, const uint8_t *data, size_len_t len, uint32_t timeout);
extern int hal_i2c_master_write_read(void *handle, uint8_t addr, const uint8_t *tx, size_t tx_len, uint8_t *rx, size_t rx_len, uint32_t timeout);

static bus_status_t i2c_read_reg_impl(void *ctx, uint16_t reg_addr, uint8_t *data, size_t len) {
    i2c_adapter_ctx_t *adapter = (i2c_adapter_ctx_t *)ctx;
    if (!adapter || !data || len == 0) return BUS_ERR_INVALID_ARG;

    uint8_t reg_buf[2];
    size_t reg_len = 1;
    reg_buf[0] = (uint8_t)(reg_addr & 0xFF);

    /* Якщо адреса 16-бітна, надсилаємо старший байт першим (Big Endian) */
    if (reg_addr > 0xFF) {
        reg_buf[0] = (uint8_t)((reg_addr >> 8) & 0xFF);
        reg_buf[1] = (uint8_t)(reg_addr & 0xFF);
        reg_len = 2;
    }

    /* Атомарна I2C транзакція: START -> DevAddr+W -> RegAddr -> RepSTART -> DevAddr+R -> Data -> STOP */
    int res = hal_i2c_master_write_read(adapter->i2c_hal_handle, adapter->dev_addr_7bit,
                                        reg_buf, reg_len, data, len, adapter->timeout_ms);
    if (res == 0) return BUS_OK;
    if (res == -2) return BUS_ERR_NACK;
    if (res == -3) return BUS_ERR_TIMEOUT;
    return BUS_ERR_IO;
}

static bus_status_t i2c_write_reg_impl(void *ctx, uint16_t reg_addr, const uint8_t *data, size_t len) {
    i2c_adapter_ctx_t *adapter = (i2c_adapter_ctx_t *)ctx;
    if (!adapter || !data || len == 0) return BUS_ERR_INVALID_ARG;

    /* Об'єднуємо адресу регістра та байти даних у єдиний буфер передачі */
    uint8_t tx_buffer[64];
    size_t header_len = (reg_addr > 0xFF) ? 2 : 1;
    if (header_len + len > sizeof(tx_buffer)) {
        return BUS_ERR_INVALID_ARG;
    }

    if (header_len == 1) {
        tx_buffer[0] = (uint8_t)(reg_addr & 0xFF);
    } else {
        tx_buffer[0] = (uint8_t)((reg_addr >> 8) & 0xFF);
        tx_buffer[1] = (uint8_t)(reg_addr & 0xFF);
    }
    memcpy(&tx_buffer[header_len], data, len);

    int res = hal_i2c_master_transmit(adapter->i2c_hal_handle, adapter->dev_addr_7bit,
                                      tx_buffer, header_len + len, adapter->timeout_ms);
    if (res == 0) return BUS_OK;
    if (res == -2) return BUS_ERR_NACK;
    if (res == -3) return BUS_ERR_TIMEOUT;
    return BUS_ERR_IO;
}

static bus_status_t i2c_lock_impl(void *ctx, uint32_t timeout_ms) {
    (void)ctx; (void)timeout_ms;
    return BUS_OK; /* Вбудовується виклик xSemaphoreTake у середовищі FreeRTOS */
}

static bus_status_t i2c_unlock_impl(void *ctx) {
    (void)ctx;
    return BUS_OK; /* Вбудовується виклик xSemaphoreGive */
}

static const bus_ops_t i2c_bus_ops = {
    .read_reg  = i2c_read_reg_impl,
    .write_reg = i2c_write_reg_impl,
    .transfer  = NULL,
    .lock      = i2c_lock_impl,
    .unlock    = i2c_unlock_impl
};

void bus_init_i2c_interface(bus_interface_t *bus, i2c_adapter_ctx_t *ctx, uint8_t dev_addr, void *hal_handle) {
    ctx->dev_addr_7bit   = dev_addr;
    ctx->timeout_ms      = 100;
    ctx->i2c_hal_handle  = hal_handle;

    bus->ops   = &i2c_bus_ops;
    bus->ctx   = ctx;
    bus->flags = BUS_FLAG_NONE;
}

/* ============================================================================
 * SPI Адаптер (SPI Adapter Context & Operations)
 * ============================================================================ */

typedef void (*spi_cs_ctrl_fn)(bool active);

typedef struct {
    spi_cs_ctrl_fn  cs_ctrl;       /**< Функція керування лінією Chip Select */
    void           *spi_hal_handle;/**< Дескриптор апаратного SPI периферійного блоку */
    uint32_t        flags;         /**< Прапорці модифікації адресного байта */
    uint32_t        timeout_ms;
} spi_adapter_ctx_t;

extern int hal_spi_transfer_sync(void *handle, const uint8_t *tx, uint8_t *rx, size_t len, uint32_t timeout);

static bus_status_t spi_read_reg_impl(void *ctx, uint16_t reg_addr, uint8_t *data, size_t len) {
    spi_adapter_ctx_t *adapter = (spi_adapter_ctx_t *)ctx;
    if (!adapter || !data || len == 0) return BUS_ERR_INVALID_ARG;

    uint8_t addr_byte = (uint8_t)(reg_addr & 0x7F);

    /* Застосування специфічних прапорців шини SPI для датчиків */
    if (adapter->flags & BUS_FLAG_SPI_READ_MSB) {
        addr_byte |= 0x80; /* Встановлюємо біт 7 у '1' для читання */
    }
    if (adapter->flags & BUS_FLAG_AUTO_INC) {
        addr_byte |= 0x40; /* Встановлюємо біт 6 у '1' для автоінкременту (LSM6DSO) */
    }

    /* Активація Chip Select (активний низький рівень) */
    if (adapter->cs_ctrl) adapter->cs_ctrl(true);

    /* Надсилаємо байт адреси регістра */
    uint8_t dummy_rx = 0;
    int res = hal_spi_transfer_sync(adapter->spi_hal_handle, &addr_byte, &dummy_rx, 1, adapter->timeout_ms);
    if (res != 0) {
        if (adapter->cs_ctrl) adapter->cs_ctrl(false);
        return BUS_ERR_IO;
    }

    /* Якщо потрібен dummy-байт для високих швидкостей SCK */
    if (adapter->flags & BUS_FLAG_USE_DUMMY) {
        uint8_t dummy_tx = 0x00;
        hal_spi_transfer_sync(adapter->spi_hal_handle, &dummy_tx, &dummy_rx, 1, adapter->timeout_ms);
    }

    /* Зчитування корисних даних: надсилаємо нулі, зчитуємо байти з MISO */
    uint8_t dummy_tx_buf[64] = {0};
    res = hal_spi_transfer_sync(adapter->spi_hal_handle, dummy_tx_buf, data, len, adapter->timeout_ms);

    /* Деактивація Chip Select */
    if (adapter->cs_ctrl) adapter->cs_ctrl(false);

    return (res == 0) ? BUS_OK : BUS_ERR_IO;
}

static bus_status_t spi_write_reg_impl(void *ctx, uint16_t reg_addr, const uint8_t *data, size_t len) {
    spi_adapter_ctx_t *adapter = (spi_adapter_ctx_t *)ctx;
    if (!adapter || !data || len == 0) return BUS_ERR_INVALID_ARG;

    uint8_t addr_byte = (uint8_t)(reg_addr & 0x7F); /* Біт 7 залишається '0' для запису */
    if (adapter->flags & BUS_FLAG_AUTO_INC) {
        addr_byte |= 0x40;
    }

    if (adapter->cs_ctrl) adapter->cs_ctrl(true);

    /* Передача адреси */
    uint8_t dummy_rx = 0;
    int res = hal_spi_transfer_sync(adapter->spi_hal_handle, &addr_byte, &dummy_rx, 1, adapter->timeout_ms);
    if (res == 0) {
        /* Передача тіла даних */
        res = hal_spi_transfer_sync(adapter->spi_hal_handle, data, NULL, len, adapter->timeout_ms);
    }

    if (adapter->cs_ctrl) adapter->cs_ctrl(false);

    return (res == 0) ? BUS_OK : BUS_ERR_IO;
}

static const bus_ops_t spi_bus_ops = {
    .read_reg  = spi_read_reg_impl,
    .write_reg = spi_write_reg_impl,
    .transfer  = NULL,
    .lock      = NULL,
    .unlock    = NULL
};

void bus_init_spi_interface(bus_interface_t *bus, spi_adapter_ctx_t *ctx, spi_cs_ctrl_fn cs_fn, void *hal_handle, uint32_t flags) {
    ctx->cs_ctrl        = cs_fn;
    ctx->spi_hal_handle = hal_handle;
    ctx->flags          = flags;
    ctx->timeout_ms     = 100;

    bus->ops   = &spi_bus_ops;
    bus->ctx   = ctx;
    bus->flags = flags;
}

/* ============================================================================
 * Mock / Loopback Адаптер для Unit-тестування без заліза
 * ============================================================================ */

typedef struct {
    uint8_t registers[256];     /**< Віртуальний масив 256 регістрів */
    bool    simulate_nack;      /**< Прапорець емуляції обриву шини */
    size_t  read_transaction_cnt;
    size_t  write_transaction_cnt;
} mock_adapter_ctx_t;

static bus_status_t mock_read_reg_impl(void *ctx, uint16_t reg_addr, uint8_t *data, size_t len) {
    mock_adapter_ctx_t *mock = (mock_adapter_ctx_t *)ctx;
    if (!mock || !data) return BUS_ERR_INVALID_ARG;
    if (mock->simulate_nack) return BUS_ERR_NACK;
    if (reg_addr + len > sizeof(mock->registers)) return BUS_ERR_INVALID_ARG;

    memcpy(data, &mock->registers[reg_addr], len);
    mock->read_transaction_cnt++;
    return BUS_OK;
}

static bus_status_t mock_write_reg_impl(void *ctx, uint16_t reg_addr, const uint8_t *data, size_t len) {
    mock_adapter_ctx_t *mock = (mock_adapter_ctx_t *)ctx;
    if (!mock || !data) return BUS_ERR_INVALID_ARG;
    if (mock->simulate_nack) return BUS_ERR_NACK;
    if (reg_addr + len > sizeof(mock->registers)) return BUS_ERR_INVALID_ARG;

    memcpy(&mock->registers[reg_addr], data, len);
    mock->write_transaction_cnt++;
    return BUS_OK;
}

static const bus_ops_t mock_bus_ops = {
    .read_reg  = mock_read_reg_impl,
    .write_reg = mock_write_reg_impl,
    .transfer  = NULL,
    .lock      = NULL,
    .unlock    = NULL
};

void bus_init_mock_interface(bus_interface_t *bus, mock_adapter_ctx_t *ctx) {
    memset(ctx, 0, sizeof(mock_adapter_ctx_t));
    bus->ops   = &mock_bus_ops;
    bus->ctx   = ctx;
    bus->flags = BUS_FLAG_NONE;
}
```

---

### Драйвер сенсора на базі уніфікованого інтерфейсу (C99)

Тепер створимо повноцінний драйвер 6-осьового IMU (акселерометр + гіроскоп), аналогічного за архітектурою до Bosch BMI270 чи TDK ICM-42688. 

Зверніть увагу: драйвер **не містить жодного рядка коду, специфічного для I2C або SPI**. Він приймає покажчик `const bus_interface_t *bus` під час ініціалізації та виконує виключно транзакції читання/запису регістрів.

```c
/**
 * @file imu_driver.h
 * @brief Драйвер 6-осьового IMU-сенсора на C99.
 */

#ifndef IMU_DRIVER_H_
#define IMU_DRIVER_H_

#include "bus_transaction.h"

#define IMU_REG_CHIP_ID      0x00
#define IMU_REG_PWR_CTRL     0x7D
#define IMU_REG_ACC_CONF     0x40
#define IMU_REG_GYR_CONF     0x42
#define IMU_REG_ACC_X_LSB    0x12
#define IMU_REG_TEMP_LSB     0x22

#define IMU_EXPECTED_CHIP_ID 0x24

typedef struct {
    float x;
    float y;
    float z;
} imu_vec3_t;

typedef struct {
    imu_vec3_t accel_mps2; /**< Прискорення по трьох осях у м/с² */
    imu_vec3_t gyro_rads;   /**< Кутова швидкість по трьох осях у рад/с */
    float      temp_deg_c;  /**< Температура кристала в °C */
} imu_data_t;

typedef struct {
    const bus_interface_t *bus;        /**< Покажчик на уніфікований інтерфейс шини */
    float                  accel_scale;/**< Множник перетворення сирих LSB у м/с² */
    float                  gyro_scale; /**< Множник перетворення сирих LSB у рад/с */
    bool                   initialized;
} imu_sensor_t;

/**
 * @brief Ініціалізація сенсора: перевірка Chip ID та налаштування частоти опитування.
 */
bus_status_t imu_init(imu_sensor_t *dev, const bus_interface_t *bus);

/**
 * @brief Пакетне (burst) зчитування прискорень, кутових швидкостей та температури.
 */
bus_status_t imu_read_all(imu_sensor_t *dev, imu_data_t *out_data);

#endif /* IMU_DRIVER_H_ */
```

Нижче наведено реалізацію логіки датчика у файлі `imu_driver.c`.

```c
/**
 * @file imu_driver.c
 * @brief Реалізація логіки драйвера IMU без прив'язки до фізичної шини.
 */

#include "imu_driver.h"

/* Стандартне гравітаційне прискорення для переводу g у м/с² */
#define GRAVITY_EARTH 9.80665f
#define PI_CONST      3.14159265358979323846f

bus_status_t imu_init(imu_sensor_t *dev, const bus_interface_t *bus) {
    if (!dev || !bus) return BUS_ERR_INVALID_ARG;

    dev->bus         = bus;
    dev->initialized = false;

    /* 1. Зчитування ідентифікатора кристала (Chip ID / WHO_AM_I) */
    uint8_t chip_id = 0;
    bus_status_t status = bus_read_u8(dev->bus, IMU_REG_CHIP_ID, &chip_id);
    if (status != BUS_OK) {
        return status;
    }

    if (chip_id != IMU_EXPECTED_CHIP_ID) {
        return BUS_ERR_IO; /* Невідомий чіп або апаратна помилка ліній зв'язку */
    }

    /* 2. Переведення сенсора в активний режим живлення (Power Control) */
    status = bus_write_u8(dev->bus, IMU_REG_PWR_CTRL, 0x0E); /* Увімкнути Accel, Gyro та температурний сенсор */
    if (status != BUS_OK) {
        return status;
    }

    /* 3. Конфігурація акселерометра: діапазон ±4g, частота видачі ODR = 100 Гц */
    status = bus_write_u8(dev->bus, IMU_REG_ACC_CONF, 0xA8);
    if (status != BUS_OK) {
        return status;
    }

    /* 4. Конфігурація гіроскопа: діапазон ±2000 dps, ODR = 100 Гц */
    status = bus_write_u8(dev->bus, IMU_REG_GYR_CONF, 0xA9);
    if (status != BUS_OK) {
        return status;
    }

    /* Розрахунок масштабних коефіцієнтів у системі SI:
     * Для ±4g при 16-бітному знаковому форматі: 4.0 * 9.80665 / 32768.0 LSB
     * Для ±2000 dps: 2000.0 * (PI / 180.0) / 32768.0 LSB */
    dev->accel_scale  = (4.0f * GRAVITY_EARTH) / 32768.0f;
    dev->gyro_scale   = (2000.0f * (PI_CONST / 180.0f)) / 32768.0f;
    dev->initialized  = true;

    return BUS_OK;
}

bus_status_t imu_read_all(imu_sensor_t *dev, imu_data_t *out_data) {
    if (!dev || !dev->initialized || !out_data) return BUS_ERR_INVALID_ARG;

    /* Пакетне зчитування 12 послідовних байтів: Accel (X,Y,Z = 6 байтів) + Gyro (X,Y,Z = 6 байтів) */
    uint8_t raw_buf[12];
    bus_status_t status = bus_read_reg(dev->bus, IMU_REG_ACC_X_LSB, raw_buf, sizeof(raw_buf));
    if (status != BUS_OK) {
        return status;
    }

    /* Розпакування 16-бітних знакових чисел у форматі Little-Endian (доповнення до 2) */
    int16_t raw_ax = (int16_t)((uint16_t)raw_buf[0]  | ((uint16_t)raw_buf[1]  << 8));
    int16_t raw_ay = (int16_t)((uint16_t)raw_buf[2]  | ((uint16_t)raw_buf[3]  << 8));
    int16_t raw_az = (int16_t)((uint16_t)raw_buf[4]  | ((uint16_t)raw_buf[5]  << 8));

    int16_t raw_gx = (int16_t)((uint16_t)raw_buf[6]  | ((uint16_t)raw_buf[7]  << 8));
    int16_t raw_gy = (int16_t)((uint16_t)raw_buf[8]  | ((uint16_t)raw_buf[9]  << 8));
    int16_t raw_gz = (int16_t)((uint16_t)raw_buf[10] | ((uint16_t)raw_buf[11] << 8));

    out_data->accel_mps2.x = (float)raw_ax * dev->accel_scale;
    out_data->accel_mps2.y = (float)raw_ay * dev->accel_scale;
    out_data->accel_mps2.z = (float)raw_az * dev->accel_scale;

    out_data->gyro_rads.x  = (float)raw_gx * dev->gyro_scale;
    out_data->gyro_rads.y  = (float)raw_gy * dev->gyro_scale;
    out_data->gyro_rads.z  = (float)raw_gz * dev->gyro_scale;

    /* Зчитування 2 байтів температури */
    uint8_t temp_buf[2];
    status = bus_read_reg(dev->bus, IMU_REG_TEMP_LSB, temp_buf, sizeof(temp_buf));
    if (status == BUS_OK) {
        int16_t raw_temp = (int16_t)((uint16_t)temp_buf[0] | ((uint16_t)temp_buf[1] << 8));
        out_data->temp_deg_c = 23.0f + ((float)raw_temp / 512.0f);
    } else {
        out_data->temp_deg_c = 0.0f;
    }

    return BUS_OK;
}
```

---

### Ідіоматична реалізація рівня транзакцій на C++20

У стандарті C++20 рівень транзакцій досягає найвищої виразності завдяки двом концептуальним інструментам:
1. **Концепти (Concepts)**: дозволяють реалізувати статичний поліморфізм із нульовими накладними витратами часу виконання (Zero-Cost Abstraction). Якщо тип шини відомий на етапі компіляції, компілятор інлайнить усі виклики читання регістрів напряму в код драйвера, усуваючи непрямі переходи за покажчиками.
2. **Типи `std::span` та `std::expected`**: гарантують безпеку роботи з буферами пам'яті без ризику виходу за межі діапазону та виключають ігнорування статусів помилок завдяки строго типізованим кодам `enum class`.

Нижче наведено заголовний файл `BusConcepts.hpp`, який формує ядро C++20 підсистеми.

```cpp
/**
 * @file BusConcepts.hpp
 * @brief Сучасні інтерфейси, концепти та типи результатів на C++20.
 */

#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <concepts>
#include <string_view>

namespace embedded::bus {

/**
 * @brief Строго типізовані коди помилок транзакцій шини.
 */
enum class BusError : int8_t {
    InvalidArg   = -1,
    Timeout      = -2,
    Nack         = -3,
    Arbitration  = -4,
    Busy         = -5,
    DmaFault     = -6,
    IoError      = -7
};

/**
 * @brief Прапорці конфігурації кадрування.
 */
enum class BusFlags : uint32_t {
    None         = 0x00,
    SpiReadMsb   = 0x01,
    SpiReadLsb   = 0x02,
    AutoInc      = 0x04,
    Reg16Bit     = 0x08,
    UseDummy     = 0x10
};

[[nodiscard]] constexpr BusFlags operator|(BusFlags a, BusFlags b) noexcept {
    return static_cast<BusFlags>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

[[nodiscard]] constexpr bool has_flag(BusFlags flags, BusFlags check) noexcept {
    return (static_cast<uint32_t>(flags) & static_cast<uint32_t>(check)) != 0;
}

/**
 * @brief C++20 Концепт транспорту шини для статичного поліморфізму (Compile-time).
 */
template <typename T>
concept BusTransport = requires(T bus, uint16_t reg, std::span<uint8_t> rx_buf, std::span<const uint8_t> tx_buf) {
    { bus.read_reg(reg, rx_buf) }   -> std::same_as<std::expected<void, BusError>>;
    { bus.write_reg(reg, tx_buf) }  -> std::same_as<std::expected<void, BusError>>;
};

/**
 * @brief Абстрактний інтерфейс для динамічного поліморфізму (Runtime).
 */
class IBusAdapter {
public:
    virtual ~IBusAdapter() = default;

    [[nodiscard]] virtual std::expected<void, BusError> read_reg(uint16_t reg_addr, std::span<uint8_t> rx_data) = 0;
    [[nodiscard]] virtual std::expected<void, BusError> write_reg(uint16_t reg_addr, std::span<const uint8_t> tx_data) = 0;
    
    [[nodiscard]] virtual std::expected<void, BusError> lock(uint32_t timeout_ms) {
        (void)timeout_ms;
        return {};
    }
    virtual void unlock() noexcept {}

    /**
     * @brief Зручний шаблонний метод зчитування одного байта.
     */
    [[nodiscard]] std::expected<uint8_t, BusError> read_u8(uint16_t reg_addr) {
        uint8_t val = 0;
        auto res = read_reg(reg_addr, std::span<uint8_t>(&val, 1));
        if (!res) return std::unexpected(res.error());
        return val;
    }

    /**
     * @brief Запис одного байта.
     */
    [[nodiscard]] std::expected<void, BusError> write_u8(uint16_t reg_addr, uint8_t val) {
        return write_reg(reg_addr, std::span<const uint8_t>(&val, 1));
    }

    /**
     * @brief Атомарна модифікація бітів за маскою.
     */
    [[nodiscard]] std::expected<void, BusError> modify_reg(uint16_t reg_addr, uint8_t mask, uint8_t val) {
        auto current = read_u8(reg_addr);
        if (!current) return std::unexpected(current.error());

        uint8_t new_val = (*current & ~mask) | (val & mask);
        if (new_val == *current) return {};

        return write_u8(reg_addr, new_val);
    }
};

} // namespace embedded::bus
```

Нижче реалізовано C++20 адаптери для шин I2C, SPI та Mock-емулятора з RAII-обгорткою блокування ліній `CsGuard` та `BusLockGuard`.

```cpp
/**
 * @file CppAdapters.hpp
 * @brief C++20 реалізація адаптерів I2cAdapter, SpiAdapter та MockBusAdapter.
 */

#pragma once

#include "BusConcepts.hpp"
#include <array>
#include <vector>
#include <functional>
#include <cstring>

namespace embedded::bus {

/**
 * @brief RAII-обгортка керування лінією Chip Select шини SPI.
 */
class CsGuard {
public:
    explicit CsGuard(std::function<void(bool)> cs_fn) : cs_fn_(std::move(cs_fn)) {
        if (cs_fn_) cs_fn_(true); // Активний низький рівень (CS Low)
    }

    ~CsGuard() {
        if (cs_fn_) cs_fn_(false); // Деактивація (CS High)
    }

    CsGuard(const CsGuard&) = delete;
    CsGuard& operator=(const CsGuard&) = delete;

private:
    std::function<void(bool)> cs_fn_;
};

/**
 * @brief C++20 I2C Адаптер.
 */
class I2cAdapter final : public IBusAdapter {
public:
    I2cAdapter(uint8_t dev_addr, void* hal_handle, uint32_t timeout_ms = 100)
        : dev_addr_(dev_addr), hal_handle_(hal_handle), timeout_ms_(timeout_ms) {}

    std::expected<void, BusError> read_reg(uint16_t reg_addr, std::span<uint8_t> rx_data) override {
        if (rx_data.empty()) return std::unexpected(BusError::InvalidArg);

        uint8_t reg_byte = static_cast<uint8_t>(reg_addr & 0xFF);
        // Імітація виклику HAL write-read із Repeated START
        int res = hal_mock_i2c_transfer(dev_addr_, &reg_byte, 1, rx_data.data(), rx_data.size());
        if (res == 0) return {};
        if (res == -2) return std::unexpected(BusError::Nack);
        return std::unexpected(BusError::IoError);
    }

    std::expected<void, BusError> write_reg(uint16_t reg_addr, std::span<const uint8_t> tx_data) override {
        if (tx_data.empty()) return std::unexpected(BusError::InvalidArg);

        std::array<uint8_t, 64> tx_buffer{};
        if (tx_data.size() + 1 > tx_buffer.size()) return std::unexpected(BusError::InvalidArg);

        tx_buffer[0] = static_cast<uint8_t>(reg_addr & 0xFF);
        std::memcpy(&tx_buffer[1], tx_data.data(), tx_data.size());

        int res = hal_mock_i2c_transmit(dev_addr_, tx_buffer.data(), tx_data.size() + 1);
        if (res == 0) return {};
        return std::unexpected(BusError::IoError);
    }

private:
    uint8_t  dev_addr_;
    void*    hal_handle_;
    uint32_t timeout_ms_;

    // Локальні заглушки для демонстрації
    int hal_mock_i2c_transfer(uint8_t, const uint8_t*, size_t, uint8_t*, size_t) { return 0; }
    int hal_mock_i2c_transmit(uint8_t, const uint8_t*, size_t) { return 0; }
};

/**
 * @brief C++20 SPI Адаптер із підтримкою RAII CS та прапорців автоінкременту.
 */
class SpiAdapter final : public IBusAdapter {
public:
    SpiAdapter(std::function<void(bool)> cs_ctrl, void* hal_handle, BusFlags flags = BusFlags::SpiReadMsb)
        : cs_ctrl_(std::move(cs_ctrl)), hal_handle_(hal_handle), flags_(flags) {}

    std::expected<void, BusError> read_reg(uint16_t reg_addr, std::span<uint8_t> rx_data) override {
        if (rx_data.empty()) return std::unexpected(BusError::InvalidArg);

        uint8_t addr_byte = static_cast<uint8_t>(reg_addr & 0x7F);
        if (has_flag(flags_, BusFlags::SpiReadMsb)) addr_byte |= 0x80;
        if (has_flag(flags_, BusFlags::AutoInc))    addr_byte |= 0x40;

        CsGuard guard(cs_ctrl_);

        int res = hal_mock_spi_transfer(&addr_byte, nullptr, 1);
        if (res != 0) return std::unexpected(BusError::IoError);

        res = hal_mock_spi_transfer(nullptr, rx_data.data(), rx_data.size());
        if (res != 0) return std::unexpected(BusError::IoError);

        return {};
    }

    std::expected<void, BusError> write_reg(uint16_t reg_addr, std::span<const uint8_t> tx_data) override {
        if (tx_data.empty()) return std::unexpected(BusError::InvalidArg);

        uint8_t addr_byte = static_cast<uint8_t>(reg_addr & 0x7F);
        if (has_flag(flags_, BusFlags::AutoInc)) addr_byte |= 0x40;

        CsGuard guard(cs_ctrl_);

        int res = hal_mock_spi_transfer(&addr_byte, nullptr, 1);
        if (res == 0) {
            res = hal_mock_spi_transfer(tx_data.data(), nullptr, tx_data.size());
        }

        return (res == 0) ? std::expected<void, BusError>{} : std::unexpected(BusError::IoError);
    }

private:
    std::function<void(bool)> cs_ctrl_;
    void*                     hal_handle_;
    BusFlags                  flags_;

    int hal_mock_spi_transfer(const uint8_t*, uint8_t*, size_t) { return 0; }
};

/**
 * @brief C++20 Mock Адаптер для автоматизованого тестування (Host Unit Testing).
 */
class MockBusAdapter final : public IBusAdapter {
public:
    MockBusAdapter() {
        memory_.fill(0x00);
    }

    std::expected<void, BusError> read_reg(uint16_t reg_addr, std::span<uint8_t> rx_data) override {
        if (inject_nack_) return std::unexpected(BusError::Nack);
        if (reg_addr + rx_data.size() > memory_.size()) return std::unexpected(BusError::InvalidArg);

        std::memcpy(rx_data.data(), &memory_[reg_addr], rx_data.size());
        read_count_++;
        return {};
    }

    std::expected<void, BusError> write_reg(uint16_t reg_addr, std::span<const uint8_t> tx_data) override {
        if (inject_nack_) return std::unexpected(BusError::Nack);
        if (reg_addr + tx_data.size() > memory_.size()) return std::unexpected(BusError::InvalidArg);

        std::memcpy(&memory_[reg_addr], tx_data.data(), tx_data.size());
        write_count_++;
        return {};
    }

    void set_reg(uint8_t reg, uint8_t val) noexcept { memory_[reg] = val; }
    [[nodiscard]] uint8_t get_reg(uint8_t reg) const noexcept { return memory_[reg]; }
    void set_inject_nack(bool enable) noexcept { inject_nack_ = enable; }
    [[nodiscard]] size_t read_count() const noexcept { return read_count_; }
    [[nodiscard]] size_t write_count() const noexcept { return write_count_; }

private:
    std::array<uint8_t, 256> memory_{};
    bool                     inject_nack_{false};
    size_t                   read_count_{0};
    size_t                   write_count_{0};
};

} // namespace embedded::bus
```

Тепер створимо шаблонний C++20 драйвер датчика, який підтримує як динамічну диспетчеризацію (`IBusAdapter&`), так і концептуальний статичний поліморфізм (`BusTransport`).

```cpp
/**
 * @file CppImuDriver.hpp
 * @brief Сучасний C++20 драйвер IMU-сенсора з підтримкою Концептів.
 */

#pragma once

#include "BusConcepts.hpp"
#include <numbers>

namespace embedded::sensor {

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct ImuSample {
    Vector3f accel_mps2;
    Vector3f gyro_rads;
    float    temp_celsius{0.0f};
};

/**
 * @brief Шаблонний C++20 драйвер 6-осьового сенсора.
 * @tparam BusClass Тип шини, що задовольняє концепт bus::BusTransport або IBusAdapter.
 */
template <typename BusClass>
class ImuDriver {
public:
    static constexpr uint8_t REG_CHIP_ID   = 0x00;
    static constexpr uint8_t REG_PWR_CTRL  = 0x7D;
    static constexpr uint8_t REG_ACC_CONF  = 0x40;
    static constexpr uint8_t REG_GYR_CONF  = 0x42;
    static constexpr uint8_t REG_ACC_DATA  = 0x12;
    static constexpr uint8_t REG_TEMP_DATA = 0x22;

    static constexpr uint8_t EXPECTED_ID   = 0x24;

    explicit ImuDriver(BusClass& bus) : bus_(bus) {}

    [[nodiscard]] std::expected<void, bus::BusError> init() {
        // 1. Перевірка Chip ID
        uint8_t chip_id = 0;
        auto res = bus_.read_reg(REG_CHIP_ID, std::span<uint8_t>(&chip_id, 1));
        if (!res) return std::unexpected(res.error());

        if (chip_id != EXPECTED_ID) {
            return std::unexpected(bus::BusError::IoError);
        }

        // 2. Увімкнення живлення акселерометра та гіроскопа
        uint8_t pwr_on = 0x0E;
        res = bus_.write_reg(REG_PWR_CTRL, std::span<const uint8_t>(&pwr_on, 1));
        if (!res) return std::unexpected(res.error());

        // 3. Конфігурація діапазонів
        uint8_t acc_cfg = 0xA8; // ±4g
        res = bus_.write_reg(REG_ACC_CONF, std::span<const uint8_t>(&acc_cfg, 1));
        if (!res) return std::unexpected(res.error());

        uint8_t gyr_cfg = 0xA9; // ±2000 dps
        res = bus_.write_reg(REG_GYR_CONF, std::span<const uint8_t>(&gyr_cfg, 1));
        if (!res) return std::unexpected(res.error());

        constexpr float gravity = 9.80665f;
        accel_scale_ = (4.0f * gravity) / 32768.0f;
        gyro_scale_  = (2000.0f * (std::numbers::pi_v<float> / 180.0f)) / 32768.0f;
        initialized_ = true;

        return {};
    }

    [[nodiscard]] std::expected<ImuSample, bus::BusError> read_sample() {
        if (!initialized_) return std::unexpected(bus::BusError::InvalidArg);

        std::array<uint8_t, 12> raw{};
        auto res = bus_.read_reg(REG_ACC_DATA, std::span<uint8_t>(raw));
        if (!res) return std::unexpected(res.error());

        auto unpack_s16 = [](uint8_t lsb, uint8_t msb) noexcept -> int16_t {
            return static_cast<int16_t>(static_cast<uint16_t>(lsb) | (static_cast<uint16_t>(msb) << 8));
        };

        ImuSample sample{};
        sample.accel_mps2.x = static_cast<float>(unpack_s16(raw[0], raw[1])) * accel_scale_;
        sample.accel_mps2.y = static_cast<float>(unpack_s16(raw[2], raw[3])) * accel_scale_;
        sample.accel_mps2.z = static_cast<float>(unpack_s16(raw[4], raw[5])) * accel_scale_;

        sample.gyro_rads.x  = static_cast<float>(unpack_s16(raw[6], raw[7])) * gyro_scale_;
        sample.gyro_rads.y  = static_cast<float>(unpack_s16(raw[8], raw[9])) * gyro_scale_;
        sample.gyro_rads.z  = static_cast<float>(unpack_s16(raw[10], raw[11])) * gyro_scale_;

        std::array<uint8_t, 2> temp_raw{};
        if (bus_.read_reg(REG_TEMP_DATA, std::span<uint8_t>(temp_raw))) {
            int16_t raw_temp = unpack_s16(temp_raw[0], temp_raw[1]);
            sample.temp_celsius = 23.0f + (static_cast<float>(raw_temp) / 512.0f);
        }

        return sample;
    }

private:
    BusClass& bus_;
    float     accel_scale_{0.0f};
    float     gyro_scale_{0.0f};
    bool      initialized_{false};
};

} // namespace embedded::sensor
```

---

### Модульне тестування та перевірка перемикання шин (Test Harness)

Продемонструємо повний цикл виконання модульних тестів на хост-системі: ініціалізація датчика через `MockBusAdapter`, емуляція значень сили тяжіння, перевірка коректності масштабування та обробка інжекції помилок зв'язку (NACK).

```cpp
/**
 * @file main_test.cpp
 * @brief Повний виконуваний тестовий набір для перевірки Transaction Layer.
 */

#include "CppAdapters.hpp"
#include "CppImuDriver.hpp"
#include <iostream>
#include <cassert>
#include <cmath>

int main() {
    using namespace embedded::bus;
    using namespace embedded::sensor;

    std::cout << "[TEST] 1. Ініціалізація віртуальної шини Mock Adapter..." << std::endl;
    MockBusAdapter mock_bus;

    // Встановлюємо очікуваний Chip ID в регістрі 0x00
    mock_bus.set_reg(ImuDriver<MockBusAdapter>::REG_CHIP_ID, 0x24);

    ImuDriver<MockBusAdapter> imu(mock_bus);

    auto init_res = imu.init();
    assert(init_res.has_value() && "Ініціалізація IMU має пройти успішно");
    std::cout << "  -> IMU успішно ініціалізовано. Chip ID підтверджено." << std::endl;
    std::cout << "  -> Регістр PWR_CTRL: 0x" << std::hex << (int)mock_bus.get_reg(0x7D) << std::dec << std::endl;
    assert(mock_bus.get_reg(0x7D) == 0x0E);

    std::cout << "[TEST] 2. Емуляція відліків сенсора (1g по осі Z, 0 по осях X та Y)..." << std::endl;
    // 1g = ~8192 LSB при шкалі ±4g (32768 / 4 = 8192)
    int16_t sim_az = 8192;
    mock_bus.set_reg(0x12, 0x00); // Accel X LSB
    mock_bus.set_reg(0x13, 0x00); // Accel X MSB
    mock_bus.set_reg(0x14, 0x00); // Accel Y LSB
    mock_bus.set_reg(0x15, 0x00); // Accel Y MSB
    mock_bus.set_reg(0x16, static_cast<uint8_t>(sim_az & 0xFF));        // Accel Z LSB
    mock_bus.set_reg(0x17, static_cast<uint8_t>((sim_az >> 8) & 0xFF)); // Accel Z MSB

    auto sample_res = imu.read_sample();
    assert(sample_res.has_value() && "Зчитування відліку має пройти успішно");

    const auto& sample = *sample_res;
    std::cout << "  -> Зчитане прискорення: X=" << sample.accel_mps2.x 
              << " Y=" << sample.accel_mps2.y 
              << " Z=" << sample.accel_mps2.z << " м/с²" << std::endl;

    assert(std::abs(sample.accel_mps2.z - 9.80665f) < 0.05f && "Прискорення Z має дорівнювати 1g (~9.81 м/с²)");

    std::cout << "[TEST] 3. Перевірка реакції на апаратну помилку шини (NACK Injection)..." << std::endl;
    mock_bus.set_inject_nack(true);
    auto failed_sample = imu.read_sample();
    assert(!failed_sample.has_value() && "Транзакція має завершитися помилкою при NACK");
    assert(failed_sample.error() == BusError::Nack);
    std::cout << "  -> Драйвер коректно повернув BusError::Nack без падіння системи." << std::endl;

    std::cout << "\n[SUCCESS] Усі модульні тести рівня транзакцій пройдено успішно!" << std::endl;
    return 0;
}
```

---

### Детальний аналіз інженерних механізмів та компромісів

Розглянемо глибинні аспекти функціонування рівня транзакцій у реальних системах із високими вимогами до надійності, швидкодії та детермінізму.

#### 1. Полярність і фаза тактування SPI (SPI Modes 0, 1, 2, 3)

Протокол SPI не має єдиного жорсткого стандарту тактування, тому рівень транзакцій підтримує 4 комбінації полярності `CPOL` (стан SCK у спокої) та фази `CPHA` (фронт вибірки даних):
- **Mode 0 (CPOL=0, CPHA=0)**: SCK у стані спокою має рівень LOW. Дані виставляються передавачем по спадаючому фронту і фіксуються (семплюються) приймачем по першому наростаючому фронту SCK.
- **Mode 1 (CPOL=0, CPHA=1)**: SCK у спокої LOW. Дані виставляються по першому наростаючому фронту і зчитуються по другому спадаючому фронту.
- **Mode 2 (CPOL=1, CPHA=0)**: SCK у спокої HIGH. Семплювання відбувається по першому спадаючому фронту.
- **Mode 3 (CPOL=1, CPHA=1)**: SCK у спокої HIGH. Семплювання відбувається по наростаючому фронту SCK.

Переважна більшість сучасних цифрових сенсорів підтримують одночасно **Mode 0 та Mode 3**, оскільки в обох режимах активним фронтом фіксації бітів є передній наростаючий фронт тактового сигналу SCK.

#### 2. Апаратний DMA-обмін та когерентність кешу даних

У високопродуктивних мікроконтролерах на базі архітектури ARM Cortex-M7 (наприклад, STM32H7, NXP i.MX RT1060) присутній кеш даних першого рівня (L1 D-Cache). Коли рівень транзакцій ініціює зчитування великого пакета даних (наприклад, 512 байтів FIFO сенсора через SPI) за допомогою прямого доступу до пам'яті (DMA), виникає проблема узгодженості кешу:
1. Процесор виділяє буфер для прийому даних у звичайній пам'яті SRAM.
2. Контролер DMA записує байти безпосередньо в фізичні комірки SRAM, оминаючи L1 D-Cache.
3. Коли драйвер пристрою намагається прочитати масив даних, процесор повертає застарілі значення з рядків кешу (Cache Dirty Read).

Щоб вирішити цю проблему без захаращення коду драйвера сенсора, адаптер рівня транзакцій бере на себе операції інвалідації та очищення кешу перед початком і після завершення DMA-транзакції:
- Перед початком передачі (`write_reg` через DMA): викликається `SCB_CleanDCache_by_Addr((uint32_t*)buf, len)`, що скидає брудні рядки кешу в фізичну пам'ять.
- Після завершення прийому (`read_reg` через DMA): викликається `SCB_InvalidateDCache_by_Addr((uint32_t*)buf, len)`, що змушує ядро завантажити свіжі дані з фізичної SRAM під час наступного звернення.
- Альтернативний шлях: розміщення буферів рівня транзакцій у спеціальній некешованій області пам'яті (Non-Cacheable SRAM), сконфігурованій через блок захисту пам'яті (MPU — Memory Protection Unit). При цьому адреси буферів повинні бути вирівняні за межею рядка кешу (32 байти для Cortex-M7).

#### 3. Багатозадачність, RTOS та уникнення взаємних блокувань (Deadlocks)

На реальних платах до однієї фізичної шини I2C або SPI часто підключено декілька мікросхем: IMU-сенсор на частоті 1 кГц у високопріоритетній задачі стабілізації польоту, барометр на частоті 50 Гц у задачі навігації та зовнішній чип пам'яті EEPROM у фоновій задачі збереження налаштувань.

Якщо дві задачі спробують одночасно викликати транзакцію на спільній шині, відбудеться катастрофічне накладання сигналів (байти адреси другого пристрою перервуть передачу даних першого).

Рівень транзакцій вирішує це за допомогою вбудованого блокування (Bus Mutex):
1. **Пріоритетне успадкування (Priority Inheritance)**: М'ютекс шини створюється з підтримкою успадкування пріоритету (`xSemaphoreCreateMutex()`). Якщо низькопріоритетна задача збереження EEPROM захопила шину, а високопріоритетна задача польотного контролера намагається зчитати IMU, операційна система FreeRTOS тимчасово піднімає пріоритет фонової задачі, запобігаючи інверсії пріоритетів (Priority Inversion).
2. **Заборона блокувань у перериваннях (ISR Safety)**: Оскільки захоплення м'ютекса є блокуючою операцією (`osWaitForever`), його категорично заборонено викликати з обробників переривань. Якщо сенсор сигналізує про готовність даних через лінію IRQ (Data Ready), обробник переривання лише надсилає сповіщення задачі-обробнику (`xTaskNotifyFromISR`), яка вже в контексті потоку захоплює м'ютекс рівня транзакцій та зчитує дані.

#### 4. Алгоритм відновлення завислої шини I2C (Bus Lockup Recovery)

Найпоширенішою апаратною несправністю шини I2C є «зависання в нулі» лінії SDA (SDA Stuck Low). Це трапляється, якщо мікроконтролер перезавантажується (через скидання сторожовим таймером Watchdog або відлагоджувачем SWD) прямо в середині транзакції зчитування, коли ведений пристрій виставляє нульовий біт на лінію SDA. Після перезапуску мікроконтролер вважає шину вільною і намагається сформувати сигнал START, проте не може притягнути SDA до нуля, оскільки лінія вже притягнута веденим пристроєм. Ведений пристрій вічно очікує тактового імпульсу SCL, а майстер вічно очікує звільнення лінії SDA.

Адаптер I2C на рівні транзакцій містить автоматичну процедуру виходу з цього стану:
1. Якщо під час ініціалізації лінія SDA зафіксована на низькому рівні, апаратний I2C-контролер тимчасово вимикається.
2. Піни SCL та SDA переналаштовуються в режим звичайного GPIO Open-Drain виходу.
3. Програмно генерується серія з 9 тактових імпульсів на лінії SCL (тактування з частотою ~50 кГц). Кожен імпульс змушує ведений пристрій виштовхнути наступний біт зі свого внутрішнього зсувного регістра. На 9-му такті ведений пристрій відпускає лінію SDA в стан логічної одиниці, очікуючи підтвердження NACK від майстра.
4. Майстер формує явну послідовність STOP: при високому рівні SCL лінія SDA переводиться з низького рівня у високий.
5. Піни повертаються в режим альтернативної функції апаратного I2C.

Нижче наведено практичну реалізацію функції відновлення шини:

```c
/**
 * @brief Процедура апаратного розблокування завислої шини I2C (9 SCL Pulses).
 */
bus_status_t i2c_bus_recover_stuck_sda(void (*set_scl)(bool), void (*set_sda)(bool), bool (*get_sda)(void), void (*delay_us)(uint32_t)) {
    if (!set_scl || !set_sda || !get_sda || !delay_us) return BUS_ERR_INVALID_ARG;

    set_sda(true); // Відпускаємо SDA (Open-Drain підтягнутий до VDD)
    set_scl(true); // Відпускаємо SCL
    delay_us(10);

    // Якщо SDA вже у високому рівні, шина здорова
    if (get_sda()) {
        return BUS_OK;
    }

    // Генеруємо до 9 імпульсів тактування SCL
    for (int i = 0; i < 9; i++) {
        set_scl(false);
        delay_us(10);
        set_scl(true);
        delay_us(10);

        if (get_sda()) {
            break; // Ведений пристрій звільнив лінію SDA
        }
    }

    // Формуємо явний сигнал STOP: при SCL=HIGH переводимо SDA з LOW у HIGH
    set_sda(false);
    delay_us(10);
    set_scl(true);
    delay_us(10);
    set_sda(true);
    delay_us(10);

    return get_sda() ? BUS_OK : BUS_ERR_IO;
}
```

Ця процедура гарантує 100% відновлення працездатності пристрою без необхідності фізичного вимкнення живлення плати.

#### 5. Робота з апаратним буфером FIFO датчика та пакетний режим

У сучасних інерційних датчиках (IMU) пряме потокове опитування кожного зразка за перериванням Data Ready стає надто ресурсомістким, коли частота видачі перевищує 1 кГц. Якщо процесор змушений кожну мілісекунду обробляти переривання, захоплювати м'ютекс шини та виконувати транзакцію, накладні витрати на перемикання контексту операційної системи можуть перевищити 15% усього процесорного часу.

Вирішенням є використання апаратного кільцевого буфера FIFO (First-In, First-Out), інтегрованого безпосередньо в кремній сенсора:
- Сенсор накопичує вимірювання у власному внутрішньому буфері об'ємом 512–2048 байтів.
- Лінія переривання налаштовується на спрацьовування за порогом заповнення (FIFO Watermark Threshold), наприклад, кожні 32 зразки.
- Замість 1000 переривань на секунду мікроконтролер отримує лише 31 переривання (1000 / 32 ≈ 31.25 Гц).
- Обробник переривання запускає єдину пакетну (Burst) DMA-транзакцію через рівень транзакцій:
```c
/* Зчитування кількості байтів у FIFO */
uint8_t count_buf[2];
bus_read_reg(dev->bus, REG_FIFO_COUNTH, count_buf, 2);
uint16_t fifo_bytes = (uint16_t)((count_buf[0] << 8) | count_buf[1]);

/* Пакетне зчитування всього масиву через SPI DMA */
bus_read_reg(dev->bus, REG_FIFO_DATA, dma_rx_buffer, fifo_bytes);
```

Рівень транзакцій забезпечує передачу всього 512-байтового блоку за одну неподільну операцію з утриманням лінії CS у низькому рівні та автоматичним автоінкрементом внутрішнього вказівника FIFO.

#### 6. Асинхронний неблокуючий диспетчер транзакцій (Async Transaction Manager)

У системах реального часу із наджорсткими вимогами до затримок блокуюче очікування завершення передачі (навіть 5.8 мкс для SPI) може бути неприпустимим у високопріоритетних задачах. У таких архітектурах рівень транзакцій розширюють асинхронним диспетчером черги (Async Transaction Queue).

Замість блокування викликаючого потоку запит упаковується у дескриптор транзакції та ставиться у неблокуючу чергу повідомлень:
```c
typedef void (*bus_callback_fn)(bus_status_t status, void *user_arg);

typedef struct {
    uint16_t         reg_addr;
    uint8_t         *rx_buf;
    const uint8_t   *tx_buf;
    size_t           len;
    bus_callback_fn  callback;
    void            *user_arg;
} bus_async_request_t;
```

Машина станів асинхронного драйвера працює за такою схемою:
1. Викликаючий потік викликає `bus_submit_async(&request)` і негайно продовжує виконання інших алгоритмів (наприклад, розрахунок фільтра Калмана або навігаційної матриці).
2. Диспетчер шини активує лінію CS і запускає передачу через DMA-контролер.
3. Коли DMA завершує прийом останнього байта, апаратне переривання `DMA_IRQHandler` скидає лінію CS у високий рівень і викликає `callback(BUS_OK, user_arg)`.
4. Зворотний виклик або розпаковує дані безпосередньо в обробнику (якщо операція швидка), або надсилає сигнал задачі-споживачу (`xTaskNotifyFromISR`).

Така архітектура дозволяє досягти 100% утилізації процесорного ядра, повністю виключаючи порожні цикли очікування апаратних прапорців готовності периферійних модулів.

#### 7. Повторні спроби та статистика надійності (Retries and Error Tracking)

У промислових середовищах із високим рівнем електромагнітних завад (EMI від моторів, силових ключів інверторів) на сигнальних лініях I2C/SPI можуть виникати поодинокі спотворення бітів. Якщо драйвер після першого ж збою NACK викине панічну помилку, система аварійно зупиниться.

Рівень транзакцій інкапсулює надійну політику повторних спроб (Retry Policy):
- **Експоненційний відступ (Exponential Backoff)**: перед кожною повторною спробою адаптер вичікує наростаючу паузу (наприклад, 100 мкс, 200 мкс, 400 мкс). Це запобігає тривалому заклинюванню шини при переході веденого пристрою в режим внутрішнього перезавантаження (Power-on Reset).
- **Лічильники деградації (Bus Health Metrics)**: дескриптор шини веде облік успішних та збійних транзакцій:
```c
typedef struct {
    uint32_t total_transactions;
    uint32_t nack_count;
    uint32_t timeout_count;
    uint32_t bus_recovery_count;
} bus_health_stats_t;
```
Якщо відсоток помилок перевищує 5% за секунду, діагностичний монітор системи сповіщає про фізичне погіршення контакту в роз'ємі чи деградацію підтягувальних резисторів до того, як датчик повністю вийде з ладу.

#### 8. Керування доменами живлення та запобігання паразитним витокам струму

В автономних пристроях із живленням від акумулятора мікроконтролер часто повністю знеструмлює датчики через польовий транзистор (P-MOSFET High-Side Switch) під час глибокого сну (Deep Sleep). Якщо при цьому сигнальні лінії шини (SCK, MOSI, CS для SPI або SCL, SDA для I2C) залишаються підключеними до живлення 3.3 В або сконфігуровані як виходи з високим рівнем, виникає небезпечний ефект паразитного живлення (Phantom Powering).

Струм від ліній шини протікає через внутрішні захисні діоди від статики (ESD Protection Diodes) всередину кристала сенсора до його шини VDD. Напруга на знеструмленому датчику піднімається до 2.7 В (3.3 В мінус 0.6 В падіння на діоді). Датчик не вимикається повністю, а зависає у нестійкому стані, споживаючи від 2 до 5 мА зайвого струму, а при повторній подачі повноцінного живлення внутрішній генератор скидання (Power-on Reset) не спрацьовує через відсутність повного спаду напруги до нуля.

Рівень транзакцій запобігає цій проблемі за допомогою функції керування доменом живлення `bus_set_power_state()`:
1. Перед знеструмленням сенсора всі лінії шини SPI/I2C програмно перемикаються в стан високоімпедансного входу без підтяжок (Analog Input / Floating Input).
2. Після подачі живлення на датчик адаптер шини вичікує обов'язковий апаратний час стабілізації напруги кристала `t_POR` (зазвичай від 1 до 10 мс залежно від моделі датчика).
3. Після закінчення паузи лінії шини перемикаються в активний режим периферії, лінія CS встановлюється у високий рівень, і запускається процедура перевірки ідентифікатора чіпа.

#### 9. Регістрові протоколи мікросхем: таблиця апаратних особливостей

Кожен виробник кремнієвих сенсорів впроваджує власні правила кадрування SPI-транзакцій. Зведемо їх у структуровану таблицю, на базі якої формуються бітові прапорці `bus_flags_t`:

| Сімейство мікросхем | Типові чіпи | R/W біт на SPI | Автоінкремент адреси на SPI | Dummy-байти при високій частоті | Особливості живлення та ініціалізації |
|---|---|---|---|---|---|
| **Bosch Sensortec** | BMI270, BMI160, BMP280, BME680 | Біт 7 = 1 (Read), Біт 7 = 0 (Write) | Автоматичний за замовчуванням | 1 dummy-байт на SPI при `f > 10` МГц | Потрібна затримка 450 мкс після подачі живлення; завантаження мікрокоду 8 КБ у BMI270 |
| **STMicroelectronics** | LSM6DSO, LIS3DH, LPS22HB | Біт 7 = 1 (Read), Біт 7 = 0 (Write) | Біт 6 = 1 (вмикає auto-increment) | Не потрібні до 10 МГц | Автоінкремент в I2C увімкнено завжди, а в SPI вимагає біта `0x40` |
| **TDK / InvenSense** | MPU6050, ICM-42688-P, ICM-20948 | Біт 7 = 1 (Read), Біт 7 = 0 (Write) | Автоматичний за замовчуванням | Не потрібні до 24 МГц | Наявність банку регістрів (вимагає запису в `REG_BANK_SEL` перед доступом до розширених функцій) |
| **Analog Devices** | ADXL345, ADIS16470 | Біт 7 = 1 (Read), Біт 7 = 0 (Write) | Біт 6 = 1 (Multiple-byte burst) | Не потрібні | 16-бітна адресація команд у промислових гіроскопах ADIS |
| **Texas Instruments** | ADS1115, TMP117 | Лише I2C адресація | Покажчик Pointer Register | — | 16-бітні значення передаються у форматі Big-Endian |

Завдяки рівню транзакцій усі ці апаратні відмінності концентруються у полі `flags` структури `bus_interface_t`, а код драйвера залишається кришталево чистим і зосередженим виключно на фізиці вимірювань.

#### 10. Компіляторна оптимізація та асемблерний аналіз викликів

Порівняємо накладні витрати на виклик транзакції у варіантах C99 та C++20 на мікроконтролері ARM Cortex-M4 (інструкції Thumb-2):

У мові C99 виклик `bus_read_reg(dev->bus, reg, data, len)` транслюється в непрямий виклик через покажчик на функцію:
```asm
ldr     r3, [r0, #0]       ; Завантаження покажчика на vtable (bus->ops)
ldr     r3, [r3, #0]       ; Завантаження адреси функції read_reg
ldr     r0, [r0, #4]       ; Завантаження контексту bus->ctx у перший аргумент
blx     r3                 ; Непрямий перехід (Branch with Link and Exchange)
```
Це коштує 4 машинних інструкції та орієнтовно 6–8 тактів процесора (з урахуванням можливого скидання конвеєра переходів).

У варіанті C++20 із концептом `BusTransport`, коли тип `SpiAdapter` передається як шаблонний параметр `template <BusTransport Bus> class ImuDriver`, компілятор GCC/Clang з оптимізацією `-O2` повністю ліквідує віртуальну таблицю:
```asm
; Прямий інлайнінг коду адаптера:
movs    r3, #128           ; Формування прапорця читання SPI (0x80)
orrs    r1, r3             ; Модифікація адреси регістра
bl      hal_spi_transfer   ; Прямий перехід на функцію передачі без непрямих покажчиків
```
Таким чином, C++20 забезпечує абсолютну гнучкість розробки без жодного такту накладних витрат у критичних до швидкодії циклах опитування сенсорів.

#### 11. Організація автоматизованого CI/CD конвеєра без апаратних стендів

Однією з найбільших переваг відокремлення чіпа від шини є можливість запускати 100% тестів логіки датчика на звичайному сервері збірки (x86-64 Linux/Windows у GitHub Actions чи GitLab CI) без використання фізичних мікроконтролерів і плат.

Тестовий конвеєр працює за такою схемою:
1. Тестовий фреймворк (GoogleTest, Catch2 або Unity) створює екземпляр `MockBusAdapter`.
2. Тест попередньо заповнює масив віртуальних регістрів сенсора тестовими даними (наприклад, калібрувальними коефіцієнтами фабричного тесту, відліками прискорення вільного падіння чи симуляцією обертання гіроскопа).
3. Викликаються методи драйвера `init()`, `read_sample()` чи `configure_filter()`.
4. Тест верифікує не лише вихідні фізичні величини у системі SI, а й точну послідовність записів у регістри (перевіряє, чи не були стерті біти сусідніх конфігурацій під час операції Read-Modify-Write).
5. Тест вмикає прапорець інжекції помилок (`simulate_nack = true`) і перевіряє, що драйвер не зависає у нескінченному циклі, коректно повертає код помилки та переводить кінцевий автомат сенсора в безпечний режим (Safe Mode).

Це скорочує час виявлення регресійних помилок з годин лабораторних випробувань до мілісекунд у автоматизованому пайплайні.

#### 12. Діагностика та апаратне трасування транзакцій (Logic Analyzer Hooks)

У складних розподілених системах для діагностики рідкісних часових збоїв та арбітражу шини рівень транзакцій підтримує інструментування через апаратні піни налагодження або трасування Segger SystemView / ITM (Instrumentation Trace Macrocell).

Шляхом додавання діагностичних макросів на початку та в кінці кожної транзакції:
```c
#define TRACE_BUS_START(id)  do { GPIO_DBG_PORT->BSRR = (1 << (id)); } while(0)
#define TRACE_BUS_END(id)    do { GPIO_DBG_PORT->BRR  = (1 << (id)); } while(0)

static bus_status_t spi_read_reg_instrumented(void *ctx, uint16_t reg, uint8_t *d, size_t l) {
    TRACE_BUS_START(PIN_DBG_SPI_TRX);
    bus_status_t st = spi_read_reg_impl(ctx, reg, d, l);
    TRACE_BUS_END(PIN_DBG_SPI_TRX);
    return st;
}
```
Інженер отримує можливість підключити 8-канальний логічний аналізатор (Saleae Logic або Sigrok Logic Analyzer) і на одній часовій діаграмі бачити точну взаємодію між фізичними сигналами шини (SCK, MOSI, MISO, CS) та маркерами виконання завдань операційної системи RTOS. Це дозволяє миттєво виявляти затримки витіснення (preemption latency), періоди блокування м'ютексів та джиттер опитування сенсорів.
