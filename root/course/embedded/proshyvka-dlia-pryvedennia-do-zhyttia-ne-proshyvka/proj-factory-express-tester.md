# ⚙️ Архітектура та прошивка заводського експрес-тестера плати

Коли свіжозібрана плата потрапляє на стенд функціонального тестування, прошивка має за кілька секунд перевірити цілісність усіх цифрових шин, пам'яті та ліній живлення, локалізувати виробничий дефект до конкретної мікросхеми чи доріжки та повернути структурований звіт оператору конвеєра. У цій вставці наведено повний автономний каркас заводського експрес-тестера (FCT runner), що реалізує захищену від зависань логіку: покроковий контроль напруг і струмів, маршовий тест оперативної пам'яті March C-, примусове відновлення заблокованих шин [I2C](root:com-devices/i2c-bus), опитування ідентифікаторів [SPI-пам'яті](root:hw-components/spi-flash), роботу генератора неперервної несучої (CW Mode) для RF-тракту та генерацію JSON-звіту через послідовний порт.

## Архітектурний контракт тестера

Головна вимога до технологічного коду тестування — абсолютна стійкість до будь-яких апаратних несправностей. Якщо на шині I2C лінія SDA замкнена на землю, чип пам'яті Flash не відповідає, а кварцовий резонатор не збуджується, прошивка тестера не має права зависнути в нескінченному циклі очікування квитанції, впасти в [HardFault](root:sf-devices/hardfault) або піти у вічне перезавантаження.

Кожен апаратний тест оформлюється як незалежний модуль із фіксованим детермінованим таймаутом і повертає уніфікований код результату. Каркас будується навколо таблиці тестових дескрипторів із нульовим динамічним виділенням пам'яті (no heap allocation):

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Runner Engine                       │
│  - Ініціалізація апаратного таймера таймаутів (100 мкс)     │
│  - Статичний буфер звіту (без malloc / heap)                │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
       ┌───────▼────────┐             ┌────────▼───────┐
       │ Test Suite     │             │ Test Reporter  │
       │ - Power Rails  │             │ - UART/USB CDC │
       │ - Memory March │             │ - Binary TLV   │
       │ - Clock PLL    │             │ - JSON Output  │
       │ - I2C Scanner  │             └────────────────┘
       │ - SPI JEDEC    │
       │ - CW RF Tone   │
       │ - OTP / eFuse  │
       └────────────────┘
```

## Покроковий протокол перевірки живлення (Фаза 0)

Жоден цифровий тест не запускається доти, доки стенд не підтвердить безпеку силових кіл. Помилка монтажу (наприклад, пробитий керамічний конденсатор типорозміру 0402 або закорочений вихід стабілізатора) за необмеженого струму живлення здатна перепалити внутрішні доріжки друкованої плати менш ніж за 10 мілісекунд.

Протокол подачі живлення на голчастому ложі виконується у три послідовні кроки:

1. **Контроль струму ввімкнення (Inrush Current)**. Стенд подає напругу 3.3 В через плавний пуск (*Soft-Start*) із вимірюванням пікового струму заряду фільтруючих конденсаторів. Якщо струм перевищує 400 мА або триває понад 3 мс, апаратний компаратор стенда вимикає силове реле за час менше 50 мкс. Це захищає плату від теплового руйнування при прямому замиканні силової шини на екран або землю.
2. **Контроль струму спокою (Quiescent Current, I_q)**. Стенд утримує лінію апаратного скидання `RESET` мікроконтролера в низькому рівні. Усі транзистори ядра заблоковані, тому струм плати визначається лише споживанням лінійних стабілізаторів (LDO) та обв'язки (норма: 100 мкА — 2.5 мА). Завищений струм спокою (понад 15–20 мА) свідчить про зворотну полярність діодів захисту, мікротріщини під корпусами BGA або провідні залишки флюсу між виводами.
3. **Внутрішній моніторинг рейок через вбудований АЦП**. Після відпускання лінії `RESET` технологічна прошивка опитує внутрішній канал джерела опорної напруги (V_REFINT). Знаючи каліброване фабричне значення V_REFINT, обчислюються реальні напруги шини живлення ядра V_CORE та аналогового домену V_DDA. Якщо напруга ядра відхиляється від номіналу більш ніж на ±3%, тест зупиняється з кодом помилки живлення, блокуючи подальший запуск енергоємних модулів.

## Алгоритм тестування пам'яті March C- та фізика дефектів

Внутрішня статична пам'ять (SRAM) будується на матрицях шеститранзисторних (6T) комірок. Під час кристального виробництва або термічного шоку паяння в масиві виникають мікродефекти: обриви ліній вибірки (*wordline*), замикання бітових ліній (*bitline*), витоки підкладки та паразитні ємнісні зв'язки між сусідніми комірками.

Простий запис і зчитування одного масиву байтів не виявляють взаємного впливу сусідніх бітів. Технологічна прошивка запускає класичний маршовий тест **March C-**, що має лінійну складність 10 · N операцій для N слів і гарантує повне виявлення таких класів відмов:

* **Stuck-At Fault (SAF)**: комірка апаратно «прилипла» до постійного логічного 0 або 1 незалежно від операцій запису.
* **Transition Fault (TF)**: комірка не здатна змінити стан (0→1 або 1→0) за один такт доступу.
* **Coupling Fault (CF)**: зміна стану в одній комірці-агресорі призводить до інверсії (*Inversion Coupling*) або примусового перезапису (*Idempotent Coupling*) значення у сусідній комірці-жертві.
* **Address Decoder Fault (AF)**: дефект внутрішнього дешифратора адреси, коли звернення до однієї комірки призводить до читання чи запису в іншу.

Шість фаз маршу виконуються у строгому порядку:

1. `↕ (w0)` — початкове заповнення нулями всього виділеного буфера (напрямок адресації довільний).
2. `⇑ (r0, w1)` — прямий прохід знизу вгору: читаємо 0, перевіряємо відсутність SAF0, записуємо 1.
3. `⇑ (r1, w0)` — прямий прохід знизу вгору: читаємо 1, перевіряємо відсутність SAF1, записуємо 0.
4. `⇓ (r0, w1)` — зворотний прохід згори вниз: читаємо 0, перевіряємо чутливість до зміни адрес, записуємо 1.
5. `⇓ (r1, w0)` — зворотний прохід згори вниз: читаємо 1, перевіряємо зворотні ємнісні витоки, записуємо 0.
6. `↕ (r0)` — фінальне суцільне зчитування нулів для підтвердження утримання заряду (*Data Retention*).

> ⚠️ **Ізоляція пам'яті під час тесту.** Оскільки March C- перезаписує кожен біт простору інверсними масками, цей тест не можна запускати на області пам'яті, де розташований активний стек процесора або таблиця векторів переривань. Прошивка виділяє окремий статичний масив і тимчасово маскує переривання (регістр `PRIMASK`), унеможливлюючи спотворення контексту.

## Робота генератора неперервної несучої (CW Mode) для RF

Перевірка високочастотного тракту (Wi-Fi, BLE, Sub-GHz) на заводі виконується без встановлення мережевого з'єднання. Спроба підключення до точки доступу займає до 10–15 секунд і залежить від зовнішніх радіозавад. Натомість плата поміщається в екрановану камеру (*RF Shield Box*), а прошивка переводить трансивер у режим **Continuous Wave (CW)** — генерацію немодульованої синусоїдальної несучої.

Процедура радіотестування охоплює два вимірювання:

1. **Вимірювання вихідної потужності (P_out) на сітці трьох частот**. Прошивка по черзі вмикає несучу на нижньому (2402 МГц), середньому (2440 МГц) та верхньому (2480 МГц) каналах із програмним рівнем +4.0 dBm. Вимірювач потужності стенда через калібрований коаксіальний зонд зчитує рівень сигналу. Відхилення понад ±1.5 dBm вказує на брак паяння погоджувального балуна (*balun*), сколотий керамічний конденсатор фільтра або порушення імпедансу доріжки друкованої антени (50 Ом).
2. **Калібрування частотного зміщення кварцу (Δf)**. Стенд вимірює точну частоту згенерованого піку. Якщо частота зміщена понад ±10 ppm через виробничий розкид навантажувальних конденсаторів кварцового резонатора, прошивка виконує підстроювання вбудованого ємнісного масиву (*capacitance tuning array*). Знайдене калібрувальне значення записується в OTP/eFuse, забезпечуючи стабільний радіозв'язок без затягування синхронізації в польових умовах.

## Реалізація експрес-тестера

Нижче наведено робочий код ядра тестового рушія, перевірки пам'яті March C-, розблокування шини I2C та верифікації ідентифікаторів периферійних мікросхем.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TEST_REPORT_MAX_LEN 1024
#define I2C_TIMEOUT_CYCLES  5000
#define SPI_TIMEOUT_CYCLES  8000

typedef enum {
    TEST_RES_PASS = 0,
    TEST_RES_FAIL = 1,
    TEST_RES_TIMEOUT = 2,
    TEST_RES_BUS_LOCKED = 3,
    TEST_RES_INVALID_ID = 4
} test_result_t;

typedef struct {
    const char* name;
    test_result_t (*run)(char* err_msg, uint32_t max_err_len);
    uint32_t execution_time_us;
} test_case_t;

/* Симуляція апаратного таймера мікросекунд */
static inline uint32_t timer_get_us(void) {
    extern volatile uint32_t g_system_us_ticks;
    return g_system_us_ticks;
}

/* 1. Маршовий тест оперативної пам'яті (March C- Pattern) */
test_result_t test_ram_march_c(char* err_msg, uint32_t max_err_len) {
    #define RAM_TEST_WORDS 256
    static uint32_t test_buffer[RAM_TEST_WORDS];
    volatile uint32_t* ram = test_buffer;
    size_t n = RAM_TEST_WORDS;

    /* Фаза 1: ↕(w0) — запис нулів */
    for (size_t i = 0; i < n; i++) {
        ram[i] = 0x00000000;
    }

    /* Фаза 2: ⇑(r0, w1) — читання 0, запис 1 */
    for (size_t i = 0; i < n; i++) {
        if (ram[i] != 0x00000000) {
            strncpy(err_msg, "RAM: SAF0/TF fault at phase 2", max_err_len);
            return TEST_RES_FAIL;
        }
        ram[i] = 0xFFFFFFFF;
    }

    /* Фаза 3: ⇑(r1, w0) — читання 1, запис 0 */
    for (size_t i = 0; i < n; i++) {
        if (ram[i] != 0xFFFFFFFF) {
            strncpy(err_msg, "RAM: SAF1/TF fault at phase 3", max_err_len);
            return TEST_RES_FAIL;
        }
        ram[i] = 0x00000000;
    }

    /* Фаза 4: ⇓(r0, w1) — збіжне читання 0, запис 1 */
    for (size_t i = n; i > 0; i--) {
        size_t idx = i - 1;
        if (ram[idx] != 0x00000000) {
            strncpy(err_msg, "RAM: Coupling fault at phase 4", max_err_len);
            return TEST_RES_FAIL;
        }
        ram[idx] = 0xFFFFFFFF;
    }

    /* Фаза 5: ⇓(r1, w0) — читання 1, запис 0 */
    for (size_t i = n; i > 0; i--) {
        size_t idx = i - 1;
        if (ram[idx] != 0xFFFFFFFF) {
            strncpy(err_msg, "RAM: Coupling fault at phase 5", max_err_len);
            return TEST_RES_FAIL;
        }
        ram[idx] = 0x00000000;
    }

    /* Фаза 6: ↕(r0) — фінальна верифікація нулів */
    for (size_t i = 0; i < n; i++) {
        if (ram[i] != 0x00000000) {
            strncpy(err_msg, "RAM: Retention fault at phase 6", max_err_len);
            return TEST_RES_FAIL;
        }
    }

    return TEST_RES_PASS;
}

/* 2. Апаратне відновлення та сканування I2C шини */
extern void gpio_set_i2c_scl(bool level);
extern void gpio_set_i2c_sda(bool level);
extern bool gpio_get_i2c_sda(void);
extern void gpio_set_i2c_mode_gpio(void);
extern void gpio_set_i2c_mode_peripheral(void);
extern bool hal_i2c_read_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t* val, uint32_t timeout);

static void i2c_bus_recovery_sequence(void) {
    gpio_set_i2c_mode_gpio();
    gpio_set_i2c_sda(true);

    /* Генерація 9 імпульсів SCL для вивільнення завислого slave */
    for (int i = 0; i < 9; i++) {
        gpio_set_i2c_scl(false);
        for (volatile int d = 0; d < 20; d++);
        gpio_set_i2c_scl(true);
        for (volatile int d = 0; d < 20; d++);
        if (gpio_get_i2c_sda()) {
            break; /* Ведений відпустив шину */
        }
    }

    /* Стоп-умова (SDA переходить з 0 в 1 при високому SCL) */
    gpio_set_i2c_scl(false);
    gpio_set_i2c_sda(false);
    for (volatile int d = 0; d < 20; d++);
    gpio_set_i2c_scl(true);
    for (volatile int d = 0; d < 20; d++);
    gpio_set_i2c_sda(true);

    gpio_set_i2c_mode_peripheral();
}

test_result_t test_i2c_sensors(char* err_msg, uint32_t max_err_len) {
    i2c_bus_recovery_sequence();

    /* Перевірка IMU ICM-42688 (I2C адреса 0x68, регістр WHO_AM_I 0x75, очікується 0x47) */
    uint8_t imu_id = 0;
    if (!hal_i2c_read_reg(0x68, 0x75, &imu_id, I2C_TIMEOUT_CYCLES)) {
        strncpy(err_msg, "I2C: IMU (0x68) NACK / Timeout", max_err_len);
        return TEST_RES_TIMEOUT;
    }
    if (imu_id != 0x47) {
        strncpy(err_msg, "I2C: IMU ID mismatch (expected 0x47)", max_err_len);
        return TEST_RES_INVALID_ID;
    }

    /* Перевірка барометра BMP390 (I2C адреса 0x77, регістр CHIP_ID 0x00, очікується 0x60) */
    uint8_t baro_id = 0;
    if (!hal_i2c_read_reg(0x77, 0x00, &baro_id, I2C_TIMEOUT_CYCLES)) {
        strncpy(err_msg, "I2C: Barometer (0x77) NACK / Timeout", max_err_len);
        return TEST_RES_TIMEOUT;
    }
    if (baro_id != 0x60) {
        strncpy(err_msg, "I2C: Barometer ID mismatch (expected 0x60)", max_err_len);
        return TEST_RES_INVALID_ID;
    }

    return TEST_RES_PASS;
}

/* 3. Перевірка SPI Flash JEDEC ID */
extern void hal_spi_cs_select(bool active);
extern void hal_spi_transfer(const uint8_t* tx, uint8_t* rx, size_t len);

test_result_t test_spi_nor_flash(char* err_msg, uint32_t max_err_len) {
    uint8_t cmd[4] = {0x9F, 0x00, 0x00, 0x00}; /* JEDEC Read ID command */
    uint8_t resp[4] = {0};

    hal_spi_cs_select(true);
    hal_spi_transfer(cmd, resp, sizeof(cmd));
    hal_spi_cs_select(false);

    uint8_t mfg_id = resp[1];
    uint8_t mem_type = resp[2];
    uint8_t capacity = resp[3];

    /* Перевірка на Winbond W25Q128 (0xEF, 0x40, 0x18) */
    if (mfg_id == 0x00 || mfg_id == 0xFF) {
        strncpy(err_msg, "SPI Flash: MISO stuck at 0/1 (no response)", max_err_len);
        return TEST_RES_BUS_LOCKED;
    }
    if (mfg_id != 0xEF || capacity != 0x18) {
        strncpy(err_msg, "SPI Flash: Unknown JEDEC ID / Capacity", max_err_len);
        return TEST_RES_INVALID_ID;
    }

    return TEST_RES_PASS;
}

/* Таблиця тестового набору */
static test_case_t g_suite[] = {
    {"RAM_MARCH_C", test_ram_march_c, 0},
    {"I2C_WHO_AM_I", test_i2c_sensors, 0},
    {"SPI_FLASH_ID", test_spi_nor_flash, 0}
};

/* Виконання всіх тестів та формування вихідного звіту */
extern void uart_send_string(const char* str);

void test_runner_execute_all(void) {
    char report[TEST_REPORT_MAX_LEN] = "{\"fct_report\":[";
    bool all_passed = true;
    size_t count = sizeof(g_suite) / sizeof(g_suite[0]);

    for (size_t i = 0; i < count; i++) {
        char err_buf[64] = {0};
        uint32_t t_start = timer_get_us();
        test_result_t res = g_suite[i].run(err_buf, sizeof(err_buf));
        uint32_t t_elapsed = timer_get_us() - t_start;
        g_suite[i].execution_time_us = t_elapsed;

        if (res != TEST_RES_PASS) {
            all_passed = false;
        }

        /* Додавання результату до JSON */
        const char* status_str = (res == TEST_RES_PASS) ? "PASS" : "FAIL";
        strcat(report, "{\"test\":\"");
        strcat(report, g_suite[i].name);
        strcat(report, "\",\"status\":\"");
        strcat(report, status_str);
        strcat(report, "\"}");
        if (i + 1 < count) {
            strcat(report, ",");
        }
    }

    strcat(report, "],\"verdict\":\"");
    strcat(report, all_passed ? "PASS" : "FAIL");
    strcat(report, "\"}\r\n");

    uart_send_string(report);
}
```
```cpp
#include <array>
#include <string_view>
#include <expected>
#include <span>
#include <cstdint>

enum class TestError : uint8_t {
    Timeout,
    BusLocked,
    InvalidId,
    MemoryFault
};

struct TestResult {
    std::string_view name;
    bool passed;
    std::string_view details;
    uint32_t duration_us;
};

/* 1. Безпечний March C- тестер ОЗП з шаблонізацією розміру */
template <size_t WordCount>
class RamTester {
public:
    static constexpr std::expected<void, TestError> run(std::span<uint32_t, WordCount> buffer) noexcept {
        /* Фаза 1: ↕(w0) */
        for (auto& cell : buffer) {
            cell = 0x00000000;
        }

        /* Фаза 2: ⇑(r0, w1) */
        for (auto& cell : buffer) {
            if (cell != 0x00000000) return std::unexpected(TestError::MemoryFault);
            cell = 0xFFFFFFFF;
        }

        /* Фаза 3: ⇑(r1, w0) */
        for (auto& cell : buffer) {
            if (cell != 0xFFFFFFFF) return std::unexpected(TestError::MemoryFault);
            cell = 0x00000000;
        }

        /* Фаза 4: ⇓(r0, w1) */
        for (size_t i = buffer.size(); i > 0; --i) {
            if (buffer[i - 1] != 0x00000000) return std::unexpected(TestError::MemoryFault);
            buffer[i - 1] = 0xFFFFFFFF;
        }

        /* Фаза 5: ⇓(r1, w0) */
        for (size_t i = buffer.size(); i > 0; --i) {
            if (buffer[i - 1] != 0xFFFFFFFF) return std::unexpected(TestError::MemoryFault);
            buffer[i - 1] = 0x00000000;
        }

        /* Фаза 6: ↕(r0) */
        for (const auto& cell : buffer) {
            if (cell != 0x00000000) return std::unexpected(TestError::MemoryFault);
        }

        return {};
    }
};

/* 2. RAII-обгортка для безпечного відновлення та роботи з шиною I2C */
class I2CBusGuard {
public:
    explicit I2CBusGuard() noexcept {
        recover_bus();
    }

    ~I2CBusGuard() noexcept = default;

    [[nodiscard]] std::expected<uint8_t, TestError> read_register(uint8_t dev_addr, uint8_t reg_addr) const noexcept {
        extern bool hal_i2c_read_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t* val, uint32_t timeout);
        uint8_t val = 0;
        if (!hal_i2c_read_reg(dev_addr, reg_addr, &val, 5000)) {
            return std::unexpected(TestError::Timeout);
        }
        return val;
    }

private:
    static void recover_bus() noexcept {
        extern void gpio_set_i2c_mode_gpio();
        extern void gpio_set_i2c_scl(bool level);
        extern void gpio_set_i2c_sda(bool level);
        extern bool gpio_get_i2c_sda();
        extern void gpio_set_i2c_mode_peripheral();

        gpio_set_i2c_mode_gpio();
        gpio_set_i2c_sda(true);

        for (int i = 0; i < 9; ++i) {
            gpio_set_i2c_scl(false);
            for (volatile int d = 0; d < 20; ++d);
            gpio_set_i2c_scl(true);
            for (volatile int d = 0; d < 20; ++d);
            if (gpio_get_i2c_sda()) break;
        }

        gpio_set_i2c_scl(false);
        gpio_set_i2c_sda(false);
        for (volatile int d = 0; d < 20; ++d);
        gpio_set_i2c_scl(true);
        for (volatile int d = 0; d < 20; ++d);
        gpio_set_i2c_sda(true);

        gpio_set_i2c_mode_peripheral();
    }
};

/* 3. Модуль верифікації Flash-пам'яті */
struct JedecId {
    uint8_t manufacturer;
    uint8_t memory_type;
    uint8_t capacity;
};

class SpiFlashProbe {
public:
    [[nodiscard]] static std::expected<JedecId, TestError> read_jedec_id() noexcept {
        extern void hal_spi_cs_select(bool active);
        extern void hal_spi_transfer(const uint8_t* tx, uint8_t* rx, size_t len);

        const std::array<uint8_t, 4> tx_buf = {0x9F, 0x00, 0x00, 0x00};
        std::array<uint8_t, 4> rx_buf = {0};

        hal_spi_cs_select(true);
        hal_spi_transfer(tx_buf.data(), rx_buf.data(), tx_buf.size());
        hal_spi_cs_select(false);

        if (rx_buf[1] == 0x00 || rx_buf[1] == 0xFF) {
            return std::unexpected(TestError::BusLocked);
        }

        return JedecId{rx_buf[1], rx_buf[2], rx_buf[3]};
    }
};

/* Каркас Test Runner на основі статичних дескрипторів */
class TestRunner {
public:
    static void execute_suite() noexcept {
        extern void uart_send_string(const char* str);
        extern uint32_t timer_get_us();

        bool overall_pass = true;

        // 1. RAM Test
        std::array<uint32_t, 256> ram_buf{};
        auto ram_res = RamTester<256>::run(ram_buf);
        if (!ram_res) overall_pass = false;

        // 2. I2C Tests
        I2CBusGuard i2c_guard;
        auto imu_res = i2c_guard.read_register(0x68, 0x75);
        if (!imu_res || *imu_res != 0x47) overall_pass = false;

        auto baro_res = i2c_guard.read_register(0x77, 0x00);
        if (!baro_res || *baro_res != 0x60) overall_pass = false;

        // 3. SPI Flash Test
        auto flash_res = SpiFlashProbe::read_jedec_id();
        if (!flash_res || flash_res->manufacturer != 0xEF || flash_res->capacity != 0x18) {
            overall_pass = false;
        }

        if (overall_pass) {
            uart_send_string("{\"status\":\"PASS\",\"details\":\"All peripherals verified\"}\r\n");
        } else {
            uart_send_string("{\"status\":\"FAIL\",\"details\":\"Hardware verification error\"}\r\n");
        }
    }
};
```
:::

## Інженерні пастки заводського тестера

Під час написання коду для фабричного стенда виникають чотири критичні пастки, невластиві звичайній розробці прикладних програм:

1. **Зависання I2C під час обриву живлення slave-чипа.** Якщо сенсор втрачає живлення під час транзакції читання в момент видачі біта `0`, лінія SDA залишається притягнутою до землі. Апаратний I2C контролер мікроконтролера впадає в стан *Bus Busy* і блокує всі подальші виклики API. Програмне генерування 9 тактових імпульсів SCL у режимі GPIO (*bit-banging*) перед ініціалізацією периферійного модуля є обов'язковим для повернення шини до робочого стану.

2. **Руйнування стека під час тестування пам'яті.** Алгоритм March C- записує інверсні бітові маски по всьому адресному простору. Якщо виділити під тест оперативну пам'ять, де розташований поточний стек процесора або таблиця векторів переривань, контролер негайно звалиться в апаратний збій. Тестування ОЗП виконують або виділеними статичними буферами, або в асемблерному стартапі до ініціалізації середовища C runtime (`__main`).

3. **Стрибки напруги під час запису eFuse/OTP.** Пропалювання кремнієвих перемичок вимагає імпульсного струму до 200 мА при строго контрольованій напрузі V_PP. Якщо на стенді просяде лінія живлення 3.3 В, біт згорить частково, спричинивши плаваючий дефект зчитування в польових умовах. Будь-який запис OTP має супроводжуватися апаратною перевіркою стабільності напруги через вбудований АЦП.

4. **Правила трасування тестових майданчиків (Design for Testability, DFT).** Тестові площадки мають проєктуватися діаметром 0.8–1.0 мм із міжосьовою відстанню не менше 1.27 мм на нижньому боці плати. Заборонено розміщувати відкриті перехідні отвори (*vias*) безпосередньо в центрі площадки без тентування маскою: голка зонда провалюється в отвір або накопичує залишки флюсу, що призводить до хибних спрацьовувань тестера контактного опору.
