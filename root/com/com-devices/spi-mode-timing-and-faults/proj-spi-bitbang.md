# ⚙️ Програмна реалізація чотирьох режимів SPI (біт-бенгінг)

Коли апаратний контролер SPI зайнятий іншими периферійними пристроями, виведений на апаратно незручні ніжки або вимагає нестандартної довжини слова та специфічних часових інтервалів перед стробуванням, розробники вбудованих систем застосовують **програмний біт-бенгінг** (*bit-banging* — пряме керування логічними рівнями виводів GPIO з прошивки). Програмна емуляція шини розкриває точну послідовність зміни напруги на лініях SCLK, MOSI та MISO для кожного з чотирьох режимів Motorola SPI, наочно демонструючи, чому біт виставляється на одному фронті, а фіксується на протилежному.

### Архітектура програмного інтерфейсу та часові вимоги

Синхронний послідовний обмін у режимі повного дуплексу (*Full-Duplex*) ґрунтується на одночасному зсуві бітів у двох зустрічних напрямках: ведучий виставляє один біт даних на лінію MOSI і водночас зчитує один біт із лінії MISO на кожному тактовому кроці.

Послідовність маніпуляцій виводами мікроконтролера всередині циклу передачі одного байта кардинально різниться залежно від конфігурації фази `CPHA`:

1. **Режими з `CPHA = 0` (Mode 0 та Mode 2 — вибірка за 1-м фронтом, зміна за 2-м):**
   - Старший біт даних (Bit 7, MSB) повинен бути надійно виставлений на лінію MOSI **до** появи першого тактового перепаду SCLK (одразу після переведення лінії вибору кристала `/CS` у низький рівень 0 В).
   - Ведучий формує перший активний фронт SCLK (перехід від рівня спокою `CPOL` до протилежного стану `!CPOL`).
   - Ведучий зчитує логічний рівень із виводу MISO. Ведений у цю ж мить фіксує стан лінії MOSI.
   - Ведучий формує другий фронт SCLK (повернення до рівня спокою `CPOL`).
   - На цьому спадному для Mode 0 або наростаючому для Mode 2 перепаді ведучий виставляє наступний біт даних (Bit 6) на лінію MOSI.

2. **Режими з `CPHA = 1` (Mode 1 та Mode 3 — зміна за 1-м фронтом, вибірка за 2-м):**
   - У момент активації лінії `/CS` стан ліній даних не має значення.
   - Ведучий формує перший активний фронт SCLK (перехід у стан `!CPOL`).
   - На цьому першому фронті ведучий виставляє черговий біт даних на лінію MOSI, а ведений виштовхує свій біт на MISO.
   - Витримується часова затримка напівперіоду такту `t_half` для завершення перехідних процесів та заряду ємності лінії.
   - Ведучий формує другий фронт SCLK (повернення в рівень спокою `CPOL`).
   - На цьому другому фронті ведучий зчитує стабільний логічний рівень із лінії MISO.

Для забезпечення передбачуваної частоти передачі та захисту від фазового тремтіння (*jitter*), викликаного перериваннями операційної системи або ядра, критичні ділянки біт-бенгінгу часто виконуються з тимчасовим маскуванням переривань.

Нижче наведено структуровану, високопродуктивну реалізацію драйвера біт-бенгінгу на мовах C та C++ з підтримкою потокової передачі буферів довільного розміру.

---

### Реалізація на C та C++

Універсальний драйвер програмного SPI абстрагується від конкретної апаратної платформи через покажчики на функції доступу до виводів GPIO або шаблонні концепції, забезпечуючи точне витримування часових інтервалів.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Визначення чотирьох стандартних режимів Motorola SPI */
typedef enum {
    SPI_MODE_0 = 0, /* CPOL = 0, CPHA = 0 */
    SPI_MODE_1 = 1, /* CPOL = 0, CPHA = 1 */
    SPI_MODE_2 = 2, /* CPOL = 1, CPHA = 0 */
    SPI_MODE_3 = 3  /* CPOL = 1, CPHA = 1 */
} spi_bb_mode_t;

/* Структура конфігурації та апаратних функцій зворотного виклику */
typedef struct {
    void (*set_sclk)(bool level);
    void (*set_mosi)(bool level);
    bool (*get_miso)(void);
    void (*set_cs)(bool level);
    void (*delay_ns)(uint32_t ns);
    spi_bb_mode_t mode;
    uint32_t half_period_ns;
} spi_bitbang_t;

/* Ініціалізація виводів у стан спокою відповідно до обраного режиму */
void spi_bb_init(const spi_bitbang_t *bus) {
    bool cpol = (bus->mode == SPI_MODE_2 || bus->mode == SPI_MODE_3);
    bus->set_cs(true);          /* Неактивний рівень Chip Select (HIGH) */
    bus->set_sclk(cpol);        /* Рівень спокою SCLK згідно з CPOL */
    bus->set_mosi(false);
}

/* Повний дуплексний обмін одним байтом */
uint8_t spi_bb_transfer_byte(const spi_bitbang_t *bus, uint8_t byte_out) {
    bool cpol = (bus->mode == SPI_MODE_2 || bus->mode == SPI_MODE_3);
    bool cpha = (bus->mode == SPI_MODE_1 || bus->mode == SPI_MODE_3);
    uint8_t byte_in = 0;

    for (uint8_t bit = 0; bit < 8; ++bit) {
        bool out_bit = (byte_out & (1 << (7 - bit))) != 0;

        if (!cpha) {
            /* CPHA = 0: встановлення біта ПЕРЕД 1-м фронтом */
            bus->set_mosi(out_bit);
            bus->delay_ns(bus->half_period_ns);

            /* 1-й фронт: перехід у стан !CPOL (строб вибірки) */
            bus->set_sclk(!cpol);
            bus->delay_ns(bus->half_period_ns);

            /* Зчитування стабільного біта на 1-му фронті */
            if (bus->get_miso()) {
                byte_in |= (1 << (7 - bit));
            }

            /* 2-й фронт: повернення у стан CPOL (підготовка наступного біта) */
            bus->set_sclk(cpol);
        } else {
            /* CPHA = 1: 1-й фронт такту змінює стан лінії */
            bus->set_sclk(!cpol);
            bus->set_mosi(out_bit);
            bus->delay_ns(bus->half_period_ns);

            /* 2-й фронт: повернення у стан CPOL (строб вибірки) */
            bus->set_sclk(cpol);
            bus->delay_ns(bus->half_period_ns);

            /* Зчитування стабільного біта на 2-му фронті */
            if (bus->get_miso()) {
                byte_in |= (1 << (7 - bit));
            }
        }
    }

    return byte_in;
}

/* Потокова передача масиву байтів із контролем лінії /CS */
void spi_bb_transfer_buffer(const spi_bitbang_t *bus, 
                            const uint8_t *tx_buf, 
                            uint8_t *rx_buf, 
                            size_t length) {
    bus->set_cs(false); /* Активація веденого (LOW) */
    bus->delay_ns(bus->half_period_ns); /* Захисний інтервал t_CSS */

    for (size_t i = 0; i < length; ++i) {
        uint8_t out_val = tx_buf ? tx_buf[i] : 0xFF;
        uint8_t in_val = spi_bb_transfer_byte(bus, out_val);
        if (rx_buf) {
            rx_buf[i] = in_val;
        }
    }

    bus->delay_ns(bus->half_period_ns); /* Захисний інтервал t_CSH */
    bus->set_cs(true);  /* Деактивація веденого (HIGH) */
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <chrono>
#include <array>

enum class SpiMode : uint8_t {
    Mode0 = 0, // CPOL=0, CPHA=0
    Mode1 = 1, // CPOL=0, CPHA=1
    Mode2 = 2, // CPOL=1, CPHA=0
    Mode3 = 3  // CPOL=1, CPHA=1
};

// C++20 концепт апаратного адаптера виводів GPIO
template <typename T>
concept SpiGpioPort = requires(T port, bool level) {
    { port.set_sclk(level) } -> std::same_as<void>;
    { port.set_mosi(level) } -> std::same_as<void>;
    { port.get_miso() }      -> std::same_as<bool>;
    { port.set_cs(level) }   -> std::same_as<void>;
    { port.delay_ns(100u) }  -> std::same_as<void>;
};

// RAII охоронець вибору кристала Chip Select
template <SpiGpioPort Gpio>
class ChipSelectGuard {
public:
    explicit ChipSelectGuard(Gpio& gpio, uint32_t hold_delay_ns = 50)
        : gpio_(gpio), delay_ns_(hold_delay_ns) {
        gpio_.set_cs(false); // Активувати веденого (LOW)
        gpio_.delay_ns(delay_ns_); // Захисна пауза t_CSS
    }

    ~ChipSelectGuard() {
        gpio_.delay_ns(delay_ns_); // Захисна пауза t_CSH
        gpio_.set_cs(true);  // Деактивувати веденого (HIGH)
    }

    ChipSelectGuard(const ChipSelectGuard&) = delete;
    ChipSelectGuard& operator=(const ChipSelectGuard&) = delete;

private:
    Gpio& gpio_;
    uint32_t delay_ns_;
};

// Шаблонний клас програмного контролера SPI
template <SpiGpioPort Gpio>
class SoftwareSpiMaster {
public:
    constexpr SoftwareSpiMaster(Gpio& gpio, SpiMode mode, uint32_t half_period_ns = 500)
        : gpio_(gpio), mode_(mode), half_period_ns_(half_period_ns) {
        init();
    }

    void init() const {
        const bool cpol = (mode_ == SpiMode::Mode2 || mode_ == SpiMode::Mode3);
        gpio_.set_cs(true);
        gpio_.set_sclk(cpol);
        gpio_.set_mosi(false);
    }

    uint8_t transfer_byte(uint8_t byte_out) const {
        const bool cpol = (mode_ == SpiMode::Mode2 || mode_ == SpiMode::Mode3);
        const bool cpha = (mode_ == SpiMode::Mode1 || mode_ == SpiMode::Mode3);
        uint8_t byte_in = 0;

        for (uint8_t bit = 0; bit < 8; ++bit) {
            const bool out_bit = (byte_out & (1 << (7 - bit))) != 0;

            if (!cpha) {
                // CPHA = 0: встановлення біта перед 1-м фронтом
                gpio_.set_mosi(out_bit);
                gpio_.delay_ns(half_period_ns_);

                // 1-й фронт: вибірка
                gpio_.set_sclk(!cpol);
                gpio_.delay_ns(half_period_ns_);
                if (gpio_.get_miso()) {
                    byte_in |= static_cast<uint8_t>(1 << (7 - bit));
                }

                // 2-й фронт: зміна такту назад у спокій
                gpio_.set_sclk(cpol);
            } else {
                // CPHA = 1: 1-й фронт змінює стан лінії
                gpio_.set_sclk(!cpol);
                gpio_.set_mosi(out_bit);
                gpio_.delay_ns(half_period_ns_);

                // 2-й фронт: вибірка
                gpio_.set_sclk(cpol);
                gpio_.delay_ns(half_period_ns_);
                if (gpio_.get_miso()) {
                    byte_in |= static_cast<uint8_t>(1 << (7 - bit));
                }
            }
        }
        return byte_in;
    }

    void transfer(std::span<const uint8_t> tx_data, std::span<uint8_t> rx_data) const {
        const ChipSelectGuard<Gpio> guard(gpio_, half_period_ns_);
        const size_t count = tx_data.size();
        for (size_t i = 0; i < count; ++i) {
            uint8_t byte_rx = transfer_byte(tx_data[i]);
            if (i < rx_data.size()) {
                rx_data[i] = byte_rx;
            }
        }
    }

private:
    Gpio& gpio_;
    SpiMode mode_;
    uint32_t half_period_ns_;
};
```
:::

---

### Приклади для цільових мікроконтролерних платформ

Програмний біт-бенгінг суттєво залежить від швидкодії системних регістрів мікроконтролера. Нижче наведено оптимізовані приклади для трьох поширених екосистем: Arduino, STM32 (з використанням надшвидкого прямого бітового доступу через регістр `BSRR`) та ESP-IDF для двохядерних систем ESP32.

:::tabs
```arduino
// Прямий біт-бенгінг на платформі Arduino
const int PIN_SCLK = 13;
const int PIN_MOSI = 11;
const int PIN_MISO = 12;
const int PIN_CS   = 10;

enum class SpiBbMode : uint8_t { Mode0 = 0, Mode1 = 1, Mode2 = 2, Mode3 = 3 };
SpiBbMode active_mode = SpiBbMode::Mode0;

void spi_bb_setup(SpiBbMode mode) {
    active_mode = mode;
    pinMode(PIN_SCLK, OUTPUT);
    pinMode(PIN_MOSI, OUTPUT);
    pinMode(PIN_MISO, INPUT);
    pinMode(PIN_CS, OUTPUT);

    digitalWrite(PIN_CS, HIGH);
    bool cpol = (active_mode == SpiBbMode::Mode2 || active_mode == SpiBbMode::Mode3);
    digitalWrite(PIN_SCLK, cpol ? HIGH : LOW);
}

uint8_t spi_bb_transfer(uint8_t byte_out) {
    bool cpol = (active_mode == SpiBbMode::Mode2 || active_mode == SpiBbMode::Mode3);
    bool cpha = (active_mode == SpiBbMode::Mode1 || active_mode == SpiBbMode::Mode3);
    uint8_t byte_in = 0;

    for (int8_t bit = 7; bit >= 0; --bit) {
        bool bit_val = bitRead(byte_out, bit);

        if (!cpha) {
            digitalWrite(PIN_MOSI, bit_val ? HIGH : LOW);
            delayMicroseconds(1);
            digitalWrite(PIN_SCLK, cpol ? LOW : HIGH); // 1-й фронт
            delayMicroseconds(1);
            if (digitalRead(PIN_MISO)) bitSet(byte_in, bit);
            digitalWrite(PIN_SCLK, cpol ? HIGH : LOW); // 2-й фронт
        } else {
            digitalWrite(PIN_SCLK, cpol ? LOW : HIGH); // 1-й фронт
            digitalWrite(PIN_MOSI, bit_val ? HIGH : LOW);
            delayMicroseconds(1);
            digitalWrite(PIN_SCLK, cpol ? HIGH : LOW); // 2-й фронт
            delayMicroseconds(1);
            if (digitalRead(PIN_MISO)) bitSet(byte_in, bit);
        }
    }
    return byte_in;
}
```
```stm32
/* Високошвидкісний біт-бенгінг на STM32 через регістри прямого бітового доступу BSRR */
#include "stm32f4xx_ll_gpio.h"

#define PIN_SCLK  LL_GPIO_PIN_5
#define PIN_MISO  LL_GPIO_PIN_6
#define PIN_MOSI  LL_GPIO_PIN_7
#define PIN_CS    LL_GPIO_PIN_4
#define SPI_PORT  GPIOA

static inline void set_sclk(bool level) {
    if (level) LL_GPIO_SetOutputPin(SPI_PORT, PIN_SCLK);
    else LL_GPIO_ResetOutputPin(SPI_PORT, PIN_SCLK);
}

static inline void set_mosi(bool level) {
    if (level) LL_GPIO_SetOutputPin(SPI_PORT, PIN_MOSI);
    else LL_GPIO_ResetOutputPin(SPI_PORT, PIN_MOSI);
}

static inline bool get_miso(void) {
    return LL_GPIO_IsInputPinSet(SPI_PORT, PIN_MISO);
}

uint8_t stm32_spi_bb_transfer_byte(uint8_t out, uint8_t mode) {
    bool cpol = (mode == 2 || mode == 3);
    bool cpha = (mode == 1 || mode == 3);
    uint8_t in = 0;

    for (int8_t i = 7; i >= 0; --i) {
        bool bit = (out >> i) & 1;

        if (!cpha) {
            set_mosi(bit);
            __NOP(); __NOP(); __NOP();
            set_sclk(!cpol);
            __NOP(); __NOP(); __NOP();
            if (get_miso()) in |= (1 << i);
            set_sclk(cpol);
        } else {
            set_sclk(!cpol);
            set_mosi(bit);
            __NOP(); __NOP(); __NOP();
            set_sclk(cpol);
            __NOP(); __NOP(); __NOP();
            if (get_miso()) in |= (1 << i);
        }
    }
    return in;
}
```
```esp-idf
#include "driver/gpio.h"
#include "esp_rom_sys.h"

#define PIN_SCLK GPIO_NUM_18
#define PIN_MOSI GPIO_NUM_23
#define PIN_MISO GPIO_NUM_19
#define PIN_CS   GPIO_NUM_5

void esp_spi_bb_init(uint8_t mode) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << PIN_SCLK) | (1ULL << PIN_MOSI) | (1ULL << PIN_CS),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io_conf);

    io_conf.pin_bit_mask = (1ULL << PIN_MISO);
    io_conf.mode = GPIO_MODE_INPUT;
    gpio_config(&io_conf);

    gpio_set_level(PIN_CS, 1);
    bool cpol = (mode == 2 || mode == 3);
    gpio_set_level(PIN_SCLK, cpol ? 1 : 0);
}

uint8_t esp_spi_bb_transfer(uint8_t data_out, uint8_t mode) {
    bool cpol = (mode == 2 || mode == 3);
    bool cpha = (mode == 1 || mode == 3);
    uint8_t data_in = 0;

    for (int8_t i = 7; i >= 0; --i) {
        uint32_t bit = (data_out >> i) & 1;

        if (!cpha) {
            gpio_set_level(PIN_MOSI, bit);
            esp_rom_delay_us(1);
            gpio_set_level(PIN_SCLK, !cpol);
            esp_rom_delay_us(1);
            if (gpio_get_level(PIN_MISO)) data_in |= (1 << i);
            gpio_set_level(PIN_SCLK, cpol);
        } else {
            gpio_set_level(PIN_SCLK, !cpol);
            gpio_set_level(PIN_MOSI, bit);
            esp_rom_delay_us(1);
            gpio_set_level(PIN_SCLK, cpol);
            esp_rom_delay_us(1);
            if (gpio_get_level(PIN_MISO)) data_in |= (1 << i);
        }
    }
    return data_in;
}
```
:::

---

### Розібраний приклад: Зчитування JEDEC ID Flash-пам'яті Winbond

Для практичної перевірки правильності вибору режиму та функціонування драйвера розгляньмо процес надсилання команди опитування `0x9F` (*Read JEDEC ID*) до мікросхеми Flash-пам'яті Winbond W25Q128 у режимі **Mode 0** та перевірку отриманої відповіді.

```
Часова послідовність на лініях шини:
1. /CS опускається в 0 В.
2. Ведучий передає команду 0x9F (10011111b):
   - Bit 7 = 1 -> MOSI=1 -> SCLK=1 (Smpl) -> SCLK=0
   - Bit 6 = 0 -> MOSI=0 -> SCLK=1 (Smpl) -> SCLK=0
   - Bit 5 = 0 -> MOSI=0 -> SCLK=1 (Smpl) -> SCLK=0
   - Bit 4 = 1 -> MOSI=1 -> SCLK=1 (Smpl) -> SCLK=0
   - Bit 3 = 1 -> MOSI=1 -> SCLK=1 (Smpl) -> SCLK=0
   - Bit 2 = 1 -> MOSI=1 -> SCLK=1 (Smpl) -> SCLK=0
   - Bit 1 = 1 -> MOSI=1 -> SCLK=1 (Smpl) -> SCLK=0
   - Bit 0 = 1 -> MOSI=1 -> SCLK=1 (Smpl) -> SCLK=0
3. Ведений повертає 3 байти відповіді на фіктивних байтах 0xFF від ведучого:
   - Байт 1: 0xEF (Manufacturer ID = Winbond)
   - Байт 2: 0x40 (Memory Type = SPI / Dual / Quad)
   - Байт 3: 0x18 (Capacity = 128 Мбіт = 16 МБ)
4. /CS піднімається в 1.
```

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

bool read_w25q128_jedec_id(const spi_bitbang_t *bus, uint8_t *manuf_id, uint16_t *device_id) {
    uint8_t tx_cmd[4] = {0x9F, 0xFF, 0xFF, 0xFF};
    uint8_t rx_resp[4] = {0};

    spi_bb_transfer_buffer(bus, tx_cmd, rx_resp, 4);

    *manuf_id = rx_resp[1];
    *device_id = ((uint16_t)rx_resp[2] << 8) | rx_resp[3];

    /* Перевірка коду виробника Winbond (0xEF) */
    return (*manuf_id == 0xEF);
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <array>
#include <optional>

struct JedecId {
    uint8_t manufacturer;
    uint8_t memory_type;
    uint8_t capacity;
};

template <SpiGpioPort Gpio>
std::optional<JedecId> read_flash_jedec_id(const SoftwareSpiMaster<Gpio>& spi) {
    const std::array<uint8_t, 4> tx_buffer{0x9F, 0xFF, 0xFF, 0xFF};
    std::array<uint8_t, 4> rx_buffer{0};

    spi.transfer(tx_buffer, rx_buffer);

    if (rx_buffer[1] == 0xEF) {
        return JedecId{
            .manufacturer = rx_buffer[1],
            .memory_type  = rx_buffer[2],
            .capacity     = rx_buffer[3]
        };
    }
    return std::nullopt;
}
```
:::

---

### Аналіз міжкадрових інтервалів та потокової передачі

Під час неперервної передачі великих масивів даних (наприклад, запису блоку даних у Flash-пам'ять або передачі фреймбуфера на екран) виникає питання збереження фазової неперервності між сусідніми байтами:

1. **Поведінка ліній між 8-м бітом поточного байта та 7-м бітом наступного байта:**
   У режимі `CPHA = 0` вибірка останнього біта D0 відбувається на 8-му провідному фронті SCLK, а на 8-му спадному фронті лінія SCLK повертається у стан спокою. Одразу після цього спаду ведучий зобов'язаний виставити старший біт D7 наступного байта на лінію MOSI, не чекаючи наступного тактового імпульсу. Якщо між викликами функцій передачі байтів виникає програмна затримка, лінія MOSI повинна стабільно утримувати рівень біта D7 нового байта протягом усього міжкадрового інтервалу.

2. **Повернення до полярності спокою `CPOL` у режимах `CPHA = 1`:**
   У режимах `CPHA = 1` кожен байтовий цикл обов'язково завершується поверненням лінії SCLK до рівня спокою `CPOL`. Якщо програмний цикл пропустить останній напівперіод повернення і спробує розпочати новий байт безпосередньо з активного фронту, ведений пристрій не зможе згенерувати внутрішній строб для зсуву нового біта D7, що викличе випадання біта або залипання лінії.

3. **Фазове тремтіння через обробку системних переривань:**
   Якщо посеред передачі байта мікроконтролер перериває виконання коду на виклик таймерного або мережевого переривання (ISR), тривалість поточного напівперіоду SCLK може випадково збільшитися з 1 мкс до 50–100 мкс. Для статичних мікросхем SPI (де цифрові тригери зберігають заряд необмежено довго) це не призводить до втрати даних. Проте динамічні пристрої та деякі високошвидкісні АЦП мають внутрішній таймаут транзакції (*Bus Inactivity Timeout*), після якого вони автоматично скидають внутрішній автомат кадру. Тому при передачі чутливих послідовностей рекомендується блокувати переривання на час передачі одного кадру.

---

### Програмний ведений вузол (Software SPI Slave)

Реалізація веденого вузла (Slave) шляхом біт-бенгінгу становить набагато складніше інженерне завдання, ніж створення ведучого. Якщо ведучий самостійно задає темп тактування та формує затримки, то ведений зобов'язаний асинхронно реагувати на зовнішні тактові перепади, сформовані стороннім генератором.

#### Архітектура обробника переривань EXTI

Ведений вузол налаштовує вивід SCLK як джерело зовнішнього переривання (EXTI на мікроконтролерах STM32 або GPIO Interrupt на ESP32):
- Для режимів `CPHA = 0` ведений повинен підготувати свій вивід MISO за перериванням від спаду лінії `/CS`. Кожен наступний провідний фронт SCLK викликає зчитування біта з лінії MOSI, а задній фронт — виставлення наступного біта на MISO.
- Для режимів `CPHA = 1` первинна зміна біта на MISO виконується за першим перепадом SCLK, а вибірка — за другим.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Стан програмного веденого вузла */
typedef struct {
    uint8_t tx_byte;
    uint8_t rx_byte;
    uint8_t bit_index;
    bool cpol;
    bool cpha;
    void (*set_miso)(bool level);
    bool (*get_mosi)(void);
} spi_slave_bb_t;

/* Обробник спадного перепаду лінії /CS */
void spi_slave_cs_fall_isr(spi_slave_bb_t *slave) {
    slave->bit_index = 0;
    slave->rx_byte = 0;

    /* Для CPHA=0 виставляємо старший біт D7 одразу по спаду CS */
    if (!slave->cpha) {
        bool out_bit = (slave->tx_byte & (1 << 7)) != 0;
        slave->set_miso(out_bit);
    }
}

/* Обробник тактового фронту SCLK */
void spi_slave_sclk_edge_isr(spi_slave_bb_t *slave, bool is_leading_edge) {
    if (!slave->cpha) {
        if (is_leading_edge) {
            /* 1-й фронт: вибірка з лінії MOSI */
            if (slave->get_mosi()) {
                slave->rx_byte |= (1 << (7 - slave->bit_index));
            }
        } else {
            /* 2-й фронт: виставлення наступного біта */
            slave->bit_index++;
            if (slave->bit_index < 8) {
                bool out_bit = (slave->tx_byte & (1 << (7 - slave->bit_index))) != 0;
                slave->set_miso(out_bit);
            }
        }
    } else {
        if (is_leading_edge) {
            /* 1-й фронт: виставлення чергового біта */
            bool out_bit = (slave->tx_byte & (1 << (7 - slave->bit_index))) != 0;
            slave->set_miso(out_bit);
        } else {
            /* 2-й фронт: вибірка з лінії MOSI */
            if (slave->get_mosi()) {
                slave->rx_byte |= (1 << (7 - slave->bit_index));
            }
            slave->bit_index++;
        }
    }
}
```
```cpp
#include <cstdint>
#include <concepts>

template <typename Gpio>
class SoftwareSpiSlave {
public:
    SoftwareSpiSlave(Gpio& gpio, bool cpol, bool cpha)
        : gpio_(gpio), cpol_(cpol), cpha_(cpha) {}

    void on_cs_fall(uint8_t next_tx_byte) {
        tx_byte_ = next_tx_byte;
        rx_byte_ = 0;
        bit_index_ = 0;

        if (!cpha_) {
            // CPHA=0: виставити D7 негайно по спаду CS
            gpio_.set_miso((tx_byte_ & 0x80) != 0);
        }
    }

    void on_sclk_edge(bool is_leading_edge) {
        if (!cpha_) {
            if (is_leading_edge) {
                if (gpio_.get_mosi()) rx_byte_ |= static_cast<uint8_t>(1 << (7 - bit_index_));
            } else {
                if (++bit_index_ < 8) {
                    gpio_.set_miso((tx_byte_ & (1 << (7 - bit_index_))) != 0);
                }
            }
        } else {
            if (is_leading_edge) {
                gpio_.set_miso((tx_byte_ & (1 << (7 - bit_index_))) != 0);
            } else {
                if (gpio_.get_mosi()) rx_byte_ |= static_cast<uint8_t>(1 << (7 - bit_index_));
                ++bit_index_;
            }
        }
    }

    uint8_t received_byte() const noexcept { return rx_byte_; }

private:
    Gpio& gpio_;
    bool cpol_;
    bool cpha_;
    uint8_t tx_byte_{0};
    uint8_t rx_byte_{0};
    uint8_t bit_index_{0};
};
```
:::

#### Обмеження швидкості програмного веденого

Через апаратну латентність входу в переривання (`t_latency ≈ 12–16` тактів процесора на ядрах ARM Cortex-M) та час виконання коду обробника ISR, програмний ведений SPI суттєво обмежений за частотою. Якщо тактовий сигнал SCLK перевищує 200–500 кГц, процесор не встигатиме обробляти фронти, що призведе до накопичення фазових помилок і пропуску бітів. Для частот понад 1 МГц ведений вузол SPI обов'язково повинен реалізовуватися виключно на апаратному кремнієвому контролері з підтримкою DMA.

---

### Апаратний самоконтроль: Перевірка петлею (Loopback Test)

Надійним способом комплексної перевірки коректності реалізації всіх чотирьох режимів у прошивці є **тест замкненої петлі** (*Loopback*): фізичне з'єднання виводу MOSI безпосередньо з виводом MISO на платі мікроконтролера. 

Оскільки в петльовому тесті лінія передачі безпосередньо керує лінією прийому, цей метод дозволяє виявити навіть мінімальні часові розходження між моментом виставлення біта та моментом його стробування: якщо фаза `CPHA` або полярність `CPOL` запрограмовані з помилкою, зчитаний байт не співпаде з відправленим тестовим патерном.

У такому режимі кожен переданий біт повинен миттєво повертатися у вхідний буфер без спотворень.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Тестування всіх 4 режимів через закорочені виводи MOSI та MISO */
bool spi_bb_run_loopback_test(const spi_bitbang_t *bus_template) {
    const uint8_t test_patterns[] = {0x00, 0xFF, 0xAA, 0x55, 0xA5, 0x5A, 0xC3, 0x3C};
    const size_t num_patterns = sizeof(test_patterns) / sizeof(test_patterns[0]);

    spi_bitbang_t test_bus = *bus_template;

    for (int mode = 0; mode < 4; ++mode) {
        test_bus.mode = (spi_bb_mode_t)mode;
        spi_bb_init(&test_bus);

        for (size_t i = 0; i < num_patterns; ++i) {
            uint8_t tx = test_patterns[i];
            test_bus.set_cs(false);
            test_bus.delay_ns(test_bus.half_period_ns);

            uint8_t rx = spi_bb_transfer_byte(&test_bus, tx);

            test_bus.delay_ns(test_bus.half_period_ns);
            test_bus.set_cs(true);

            if (rx != tx) {
                /* Помилка: невідповідність отриманого байта переданому */
                return false;
            }
        }
    }
    return true;
}
```
```cpp
#include <array>
#include <cstdint>
#include <iostream>

template <SpiGpioPort Gpio>
bool run_spi_loopback_suite(Gpio& gpio) {
    constexpr std::array<uint8_t, 8> test_vectors{
        0x00, 0xFF, 0xAA, 0x55, 0xA5, 0x5A, 0x12, 0x89
    };

    const std::array<SpiMode, 4> all_modes{
        SpiMode::Mode0, SpiMode::Mode1, SpiMode::Mode2, SpiMode::Mode3
    };

    for (auto mode : all_modes) {
        SoftwareSpiMaster<Gpio> master(gpio, mode, 1000);

        for (uint8_t tx_val : test_vectors) {
            std::array<uint8_t, 1> tx_buf{tx_val};
            std::array<uint8_t, 1> rx_buf{0};

            master.transfer(tx_buf, rx_buf);

            if (rx_buf[0] != tx_val) {
                return false; // Помилка петльового тесту
            }
        }
    }
    return true;
}
```
:::

---

### Порівняння біт-бенгінгу з апаратним SPI та контролерами DMA

Програмна емуляція шини SPI через виводи загального призначення GPIO має як фундаментальні переваги у гнучкості, так і суттєві архітектурні обмеження щодо навантаження на обчислювальне ядро процесора:

1. **Навантаження на центральний процесор (CPU Load):**
   Під час біт-бенгінгу процесор перебуває у стані активного очікування (*Busy-Waiting*) протягом усього часу передачі кожного біта. Навіть на швидкості 100 кбіт/с ядро мікроконтролера завантажене на 100%, спалюючи мільйони тактів на виконання порожніх циклів затримок та опитування регістрів. На противагу цьому, апаратний блок SPI у зв'язці з контролером прямого доступу до пам'яті (DMA) здійснює пересилання багатокілобайтних буферів у фоновому режимі з нульовим навантаженням на ядро, генеруючи єдине переривання після завершення всього блоку.

2. **Нестандартні формати кадру:**
   Більшість апаратних периферійних модулів SPI в мікроконтролерах жорстко обмежені довжиною слова у 8 або 16 бітів (деякі сучасні чіпи підтримують від 4 до 32 бітів). Якщо розробник підключає спеціалізований графічний дисплей із 9-бітним інтерфейсом (де 9-й біт позначає перемикання між командою та даними) або 24-бітний вимірювальний АЦП безперервного перетворення, апаратний модуль змушений розбивати слово на штучні байти з паразитними паузами. Програмний біт-бенгінг дозволяє реалізувати довільну розрядність слова (наприклад, цикл `for (int i = 0; i < 24; ++i)`) без зміни конфігурації регістрів.

3. **Контроль цілісності та апаратні контрольні суми:**
   У випадках, коли шина SPI працює в умовах сильних електромагнітних завад (наприклад, поблизу імпульсних перетворювачів напруги або силових драйверів двигунів), окремі біти можуть спотворюватися через наведені імпульсні перешкоди. У програмному біт-бенгінгу рекомендується супроводжувати кожен переданий пакет розрахунком циклічного надлишкового коду CRC-8 або CRC-16. Ведений пристрій обчислює контрольну суму вхідного потоку і передає її у відповідь останнім байтом кадру, що дозволяє ведучому миттєво виявити збій та ініціювати повторну транзакцію.

---

### Осцилографічна діагностика та аналіз форми сигналів

При налагодженні програмного SPI цифровий осцилограф або логічний аналізатор (наприклад, Saleae Logic або сумісний інструмент на базі RP2040) повинен підключатися безпосередньо до виводів мікроконтролера:

1. **Налаштування тригера логічного аналізатора:**
   - Тригер запуску встановлюється за **спадним фронтом лінії `/CS`** (1 → 0). Це дозволяє зафіксувати початок кадру та перевірити захисний інтервал `t_CSS`.
   - Частота дискретизації аналізатора повинна щонайменше у 10–20 разів перевищувати швидкість біт-бенгінгу (наприклад, 20–50 Мвиб/с для сигналу SCLK з періодом 1 мкс), щоб точно бачити взаємне розташування фронтів.

2. **Діагностика завалу фронтів (RC-деградація):**
   - На довгих з'єднувальних дротах або при використанні макетних плат паразитна ємність лінії `C_bus` разом із вихідним опором портів GPIO формує інтегруючий RC-ланцюг.
   - Якщо наростання сигналу SCLK займає понад 30% тривалості напівперіоду `t_half`, вхідний тригер веденого може зафіксувати брязкіт (*ringing*) або спрацювати із затримкою, що порушить час вибірки. У таких випадках програмні затримки `t_half` збільшують, знижуючи швидкість передачі до відновлення прямокутної форми імпульсів.

---

### Розрахунок резисторів підтяжки та узгодження ліній зв'язку

При підключенні кількох ведених або роботі через довгі з'єднувальні шлейфи виникає потреба встановлення зовнішніх підтягуючих резисторів (*Pull-Up* або *Pull-Down*):

1. **Мінімальний опір підтяжки `R_min`:**
   Обмежується максимальним вихідним струмом розряду польового транзистора вхідного/вихідного каскаду GPIO `I_OL` (зазвичай від 4 до 8 мА), щоб напруга низького рівня не перевищувала поріг `V_OL = 0.4 В`:

```
R_min = (V_DD - V_OL) / I_OL
R_min = (3.3 - 0.4) / 0.004 = 725 Ом
```

2. **Максимальний опір підтяжки `R_max`:**
   Визначається сумарною паразитною ємністю лінії `C_bus` (ємність монтажних доріжок плюс вхідна ємність виводів мікросхем, типово 30–100 пФ) та допустимим часом наростання фронту `t_rise` (який не повинен перевищувати 20% тривалості напівперіоду `t_half`):

```
R_max = t_rise / (0.8473 · C_bus)
```

Для шини з сумарною ємністю `C_bus = 50 пФ` та цільовим часом наростання `t_rise = 50 нс`:

```
R_max = 50 · 10⁻⁹ / (0.8473 · 50 · 10⁻¹²) ≈ 1180 Ом (1.2 кОм)
```

Застосування занадто високого номіналу підтяжки (наприклад, внутрішніх резисторів мікроконтролера 40–100 кОм) призводить до сильного завалу наростаючого фронту при `CPOL = 1`, через що ведений пристрій фіксує помилкові строби вибірки.

---

### Пастки часових затримок та компіляторних оптимізацій

При створенні та експлуатації програмного драйвера біт-бенгінгу виникають чотири критичні інженерні ризики:

1. **Видалення порожніх циклів затримок оптимізатором GCC:**
   Якщо для формування часової затримки напівперіоду `t_half` використовується простий цикл `for (volatile int i=0; i<50; ++i);`, поведінка коду залежатиме від оптимізатора (`-O0`, `-O2` чи `-O3`). На високих рівнях оптимізації компілятор може замінити або розгорнути цикл, внаслідок чого частота SCLK зросте понад максимальну частоту веденого кристала, спричиняючи порушення часу встановлення `t_SU`. Слід використовувати апаратні таймери або вставки `__NOP()` з ключовим словом `asm volatile`.

2. **Асиметрія скважності через неоднаковий час читання та запису GPIO:**
   На мікроконтролерах із багаторівневою шинною топологією (наприклад, шини AHB/APB у процесорах ARM Cortex-M) читання регістра вхідних даних `IDR` займає на 2–4 цикли ядра більше, ніж запис у регістр встановлення/скидання `BSRR`, через наявність конвеєрів та буферів запису. Якщо не вирівнювати паузи, тривалість високого та низького напівперіодів такту буде різнитися, що спотворює часовий бюджет на граничних швидкостях.

3. **Порушення часу підготовки `t_CSS` перед першим тактовим фронтом:**
   У режимах `CPHA = 0` ведений кристал виставляє старший біт на лінію MISO по спаду `/CS`. Якщо програмний код опускає `/CS` і на наступному ж рядку формує активний фронт SCLK, швидкісний процесор із частотою 168–240 МГц випередить вихідний каскад веденого датчика. Ведучий прочитає випадковий шум або стан підтяжки замість валідного біта D7.

4. **Помилка висячого виводу під час зміни режиму:**
   Якщо в конфігурації `CPOL = 1` мікроконтролер переводить вивід SCLK зі стану спокою в нуль під час перезавантаження або динамічного перемикання режимів, ведений пристрій фіксує помилковий строб. Усі лінії SCLK для режимів Mode 2 та Mode 3 повинні мати апаратні підтягуючі резистори (*Pull-Up*) номіналом 4.7–10 кОм до лінії живлення `V_DD`.
