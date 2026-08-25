# ⚙️ Програмна емуляція I2C Master з підтримкою Clock Stretching та захистом від зависання

Ця вставка містить повну практичну реалізацію програмного контролера I2C Master (*Bit-Banging*) на виводах GPIO загального призначення, який коректно обробляє апаратне розтягування такту (*clock stretching*) веденими пристроями, запобігає зависанню системи за допомогою апаратних таймаутів та виконує автоматичну процедуру скидання шини при блокуванні лінії SDA.

---

### 1. Архітектура програмного емулятора I2C Master

Програмна реалізація інтерфейсу I2C (*Bit-Banging*, від англ. *bit* — біт та *to bang* — бити, смикати виводами) застосовується в мікроконтролерних системах, коли апаратні контролери I2C вже зайняті іншою периферією, виведені на незручні ніжки плати або мають апаратні дефекти в кремнії (як, наприклад, відома помилка апаратного контролера I2C у процесорах Broadcom BCM2835 у платах Raspberry Pi, де апаратний блок передчасно фіксував біти даних під час розтягування такту на повторному старті).

Головна помилка примітивних реалізацій *Bit-Banging* полягає в конфігурації виводу SCL виключно як виходу двотактного типу (*Push-Pull*) без зчитування його реального стану:

:::tabs
```c
// НАЇВНИЙ, НЕПРАВИЛЬНИЙ ПІДХІД У C:
void naive_i2c_write_bit(bool bit) {
    gpio_set_pin(SDA_PIN, bit);
    gpio_set_pin(SCL_PIN, true); // Примусовий Push-Pull HIGH!
    delay_us(5);                 // Майстер наївно вважає, що на лінії HIGH
    gpio_set_pin(SCL_PIN, false);
}
```
```cpp
// НАЇВНИЙ, НЕПРАВИЛЬНИЙ ПІДХІД У C++:
void naive_i2c_write_bit(GpioPin& scl, GpioPin& sda, bool bit) {
    sda.write(bit);
    scl.write(true);             // Примусовий Push-Pull HIGH!
    delay_us(5);                 // Майстер наївно вважає, що на лінії HIGH
    scl.write(false);
}
```
:::

Якщо ведений пристрій у цей момент притягує лінію SCL до нуля для обробки внутрішніх операцій, наївний майстер:
1. Зчитує сміття з лінії SDA, оскільки ведений ще не встиг підготувати вихідний біт;
2. Намагається силою перевести двотактний вихід у стан 3.3 В проти відкритого N-канального транзистора веденого, що викликає наскрізний струм короткого замикання, нагрівання мікросхеми та просідання напруги живлення;
3. Втрачає синхронізацію кадрів і призводить до зависання всієї підсистеми обміну.

Правильна архітектура вимагає конфігурації виводів SCL та SDA в режимі **відкритого стоку** (*Open-Drain*) з увімкненою внутрішньою або зовнішньою підтяжкою `R_p`. Коли майстер відпускає лінію SCL, він зобов'язаний перевіряти фактичний стан виводу через вхідний буфер і очікувати переходу напруги у високий рівень з обов'язковим контролем лічильника таймауту.

---

### 2. Реалізація драйвера мовами C та C++

Наведений нижче драйвер реалізує повноцінний кінцевий автомат ведучого пристрою з підтримкою умов START, REPEATED START, STOP, передачі байта з перевіркою ACK/NACK, прийому байта з формуванням ACK/NACK, механізму очікування розтягування такту та 9-тактової аварійної послідовності скидання шини.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

// Типи помилок шини I2C
typedef enum {
    I2C_BB_OK = 0,
    I2C_BB_ERROR_NACK = -1,
    I2C_BB_ERROR_SCL_TIMEOUT = -2,
    I2C_BB_ERROR_BUS_BUSY = -3
} i2c_bb_status_t;

// Структура конфігурації апаратних портів та функцій затримки
typedef struct {
    void (*set_scl_low)(void);
    void (*set_scl_high_z)(void);
    bool (*read_scl)(void);
    void (*set_sda_low)(void);
    void (*set_sda_high_z)(void);
    bool (*read_sda)(void);
    void (*delay_half_period_us)(void);
    uint32_t (*get_tick_us)(void);
    uint32_t stretch_timeout_us;
} i2c_bitbang_bus_t;

// Очікування переходу лінії SCL у стан логічної одиниці з таймаутом
static i2c_bb_status_t i2c_bb_wait_scl_high(const i2c_bitbang_bus_t *bus) {
    bus->set_scl_high_z();
    uint32_t start_time = bus->get_tick_us();
    
    // Цикл опитування стану лінії SCL
    while (!bus->read_scl()) {
        uint32_t elapsed = bus->get_tick_us() - start_time;
        if (elapsed >= bus->stretch_timeout_us) {
            return I2C_BB_ERROR_SCL_TIMEOUT;
        }
    }
    return I2C_BB_OK;
}

// Формування умови START на шині
i2c_bb_status_t i2c_bb_start(const i2c_bitbang_bus_t *bus) {
    bus->set_sda_high_z();
    if (i2c_bb_wait_scl_high(bus) != I2C_BB_OK) {
        return I2C_BB_ERROR_SCL_TIMEOUT;
    }
    bus->delay_half_period_us();
    
    if (!bus->read_sda()) {
        return I2C_BB_ERROR_BUS_BUSY;
    }
    
    // Спад SDA при високому рівні SCL -> умова START
    bus->set_sda_low();
    bus->delay_half_period_us();
    bus->set_scl_low();
    bus->delay_half_period_us();
    return I2C_BB_OK;
}

// Формування умови STOP на шині
i2c_bb_status_t i2c_bb_stop(const i2c_bitbang_bus_t *bus) {
    bus->set_sda_low();
    bus->delay_half_period_us();
    
    if (i2c_bb_wait_scl_high(bus) != I2C_BB_OK) {
        return I2C_BB_ERROR_SCL_TIMEOUT;
    }
    bus->delay_half_period_us();
    
    // Наростання SDA при високому рівні SCL -> умова STOP
    bus->set_sda_high_z();
    bus->delay_half_period_us();
    return I2C_BB_OK;
}

// Запис одного байта з контролем розтягування та квитанції ACK/NACK
i2c_bb_status_t i2c_bb_write_byte(const i2c_bitbang_bus_t *bus, uint8_t byte) {
    for (uint8_t i = 0; i < 8; i++) {
        if (byte & 0x80) {
            bus->set_sda_high_z();
        } else {
            bus->set_sda_low();
        }
        byte <<= 1;
        bus->delay_half_period_us();
        
        // Піднімаємо SCL і перевіряємо, чи ведений не заблокував такт
        if (i2c_bb_wait_scl_high(bus) != I2C_BB_OK) {
            return I2C_BB_ERROR_SCL_TIMEOUT;
        }
        bus->delay_half_period_us();
        bus->set_scl_low();
    }
    
    // 9-й такт: Зчитування біта підтвердження ACK від веденого
    bus->set_sda_high_z();
    bus->delay_half_period_us();
    
    if (i2c_bb_wait_scl_high(bus) != I2C_BB_OK) {
        return I2C_BB_ERROR_SCL_TIMEOUT;
    }
    
    bool nack = bus->read_sda();
    bus->delay_half_period_us();
    bus->set_scl_low();
    bus->delay_half_period_us();
    
    return nack ? I2C_BB_ERROR_NACK : I2C_BB_OK;
}

// Зчитування одного байта з генерацією ACK/NACK
i2c_bb_status_t i2c_bb_read_byte(const i2c_bitbang_bus_t *bus, uint8_t *byte, bool send_ack) {
    uint8_t received = 0;
    bus->set_sda_high_z();
    
    for (uint8_t i = 0; i < 8; i++) {
        received <<= 1;
        bus->delay_half_period_us();
        
        // Ведений виставляє біт даних під час LOW або розтягує SCL
        if (i2c_bb_wait_scl_high(bus) != I2C_BB_OK) {
            return I2C_BB_ERROR_SCL_TIMEOUT;
        }
        
        if (bus->read_sda()) {
            received |= 0x01;
        }
        bus->delay_half_period_us();
        bus->set_scl_low();
    }
    
    *byte = received;
    
    // 9-й такт: Формування відповіді ACK (0) або NACK (1) ведучим
    if (send_ack) {
        bus->set_sda_low();
    } else {
        bus->set_sda_high_z();
    }
    bus->delay_half_period_us();
    
    if (i2c_bb_wait_scl_high(bus) != I2C_BB_OK) {
        return I2C_BB_ERROR_SCL_TIMEOUT;
    }
    bus->delay_half_period_us();
    bus->set_scl_low();
    bus->set_sda_high_z();
    bus->delay_half_period_us();
    
    return I2C_BB_OK;
}

// 9-тактова процедура відновлення завислої шини
void i2c_bb_recover_bus(const i2c_bitbang_bus_t *bus) {
    bus->set_sda_high_z();
    bus->set_scl_high_z();
    bus->delay_half_period_us();
    
    // Генеруємо до 9 імпульсів SCL для виштовхування бітів із веденого
    for (uint8_t i = 0; i < 9; i++) {
        if (bus->read_sda()) {
            break; // Ведений відпустив лінію даних
        }
        bus->set_scl_low();
        bus->delay_half_period_us();
        bus->set_scl_high_z();
        bus->delay_half_period_us();
    }
    
    // Формуємо примусовий STOP
    bus->set_sda_low();
    bus->delay_half_period_us();
    bus->set_scl_high_z();
    bus->delay_half_period_us();
    bus->set_sda_high_z();
    bus->delay_half_period_us();
}
```
```cpp
#include <cstdint>
#include <chrono>
#include <expected>
#include <span>
#include <concepts>

enum class I2cError {
    Nack,
    SclTimeout,
    BusBusy,
    BufferOverflow
};

// Концепт апаратного інтерфейсу керування лініями GPIO
template <typename T>
concept I2cGpioHal = requires(T hal) {
    { hal.set_scl_low() } -> std::same_as<void>;
    { hal.set_scl_high_z() } -> std::same_as<void>;
    { hal.read_scl() } -> std::same_as<bool>;
    { hal.set_sda_low() } -> std::same_as<void>;
    { hal.set_sda_high_z() } -> std::same_as<void>;
    { hal.read_sda() } -> std::same_as<bool>;
    { hal.delay_half_period() } -> std::same_as<void>;
    { hal.current_time_us() } -> std::same_as<uint32_t>;
};

template <I2cGpioHal Hal>
class I2cBitBangMaster {
public:
    explicit I2cBitBangMaster(Hal hal, uint32_t stretch_timeout_us = 25000)
        : hal_(hal), stretch_timeout_us_(stretch_timeout_us) {}

    std::expected<void, I2cError> start() {
        hal_.set_sda_high_z();
        if (auto res = wait_scl_high(); !res) return res;
        hal_.delay_half_period();

        if (!hal_.read_sda()) {
            return std::unexpected(I2cError::BusBusy);
        }

        hal_.set_sda_low();
        hal_.delay_half_period();
        hal_.set_scl_low();
        hal_.delay_half_period();
        return {};
    }

    std::expected<void, I2cError> stop() {
        hal_.set_sda_low();
        hal_.delay_half_period();
        if (auto res = wait_scl_high(); !res) return res;
        hal_.delay_half_period();

        hal_.set_sda_high_z();
        hal_.delay_half_period();
        return {};
    }

    std::expected<void, I2cError> write_byte(uint8_t byte) {
        for (uint8_t i = 0; i < 8; ++i) {
            if (byte & 0x80) {
                hal_.set_sda_high_z();
            } else {
                hal_.set_sda_low();
            }
            byte <<= 1;
            hal_.delay_half_period();

            if (auto res = wait_scl_high(); !res) return res;
            hal_.delay_half_period();
            hal_.set_scl_low();
        }

        hal_.set_sda_high_z();
        hal_.delay_half_period();
        if (auto res = wait_scl_high(); !res) return res;

        bool nack = hal_.read_sda();
        hal_.delay_half_period();
        hal_.set_scl_low();
        hal_.delay_half_period();

        if (nack) return std::unexpected(I2cError::Nack);
        return {};
    }

    std::expected<uint8_t, I2cError> read_byte(bool send_ack) {
        uint8_t received = 0;
        hal_.set_sda_high_z();

        for (uint8_t i = 0; i < 8; ++i) {
            received <<= 1;
            hal_.delay_half_period();

            if (auto res = wait_scl_high(); !res) return res;
            if (hal_.read_sda()) {
                received |= 0x01;
            }
            hal_.delay_half_period();
            hal_.set_scl_low();
        }

        if (send_ack) {
            hal_.set_sda_low();
        } else {
            hal_.set_sda_high_z();
        }
        hal_.delay_half_period();

        if (auto res = wait_scl_high(); !res) return res;
        hal_.delay_half_period();
        hal_.set_scl_low();
        hal_.set_sda_high_z();
        hal_.delay_half_period();

        return received;
    }

    std::expected<void, I2cError> write(uint8_t address, std::span<const uint8_t> data) {
        auto res = start();
        if (!res) return res;

        res = write_byte(static_cast<uint8_t>(address << 1));
        if (!res) {
            stop();
            return res;
        }

        for (uint8_t b : data) {
            res = write_byte(b);
            if (!res) {
                stop();
                return res;
            }
        }
        return stop();
    }

    std::expected<void, I2cError> read(uint8_t address, std::span<uint8_t> buffer) {
        auto res = start();
        if (!res) return res;

        res = write_byte(static_cast<uint8_t>((address << 1) | 0x01));
        if (!res) {
            stop();
            return res;
        }

        for (size_t i = 0; i < buffer.size(); ++i) {
            bool send_ack = (i + 1 < buffer.size());
            auto byte_res = read_byte(send_ack);
            if (!byte_res) {
                stop();
                return std::unexpected(byte_res.error());
            }
            buffer[i] = *byte_res;
        }
        return stop();
    }

    void recover_bus() {
        hal_.set_sda_high_z();
        hal_.set_scl_high_z();
        hal_.delay_half_period();

        for (uint8_t i = 0; i < 9; ++i) {
            if (hal_.read_sda()) break;
            hal_.set_scl_low();
            hal_.delay_half_period();
            hal_.set_scl_high_z();
            hal_.delay_half_period();
        }

        hal_.set_sda_low();
        hal_.delay_half_period();
        hal_.set_scl_high_z();
        hal_.delay_half_period();
        hal_.set_sda_high_z();
        hal_.delay_half_period();
    }

private:
    std::expected<void, I2cError> wait_scl_high() {
        hal_.set_scl_high_z();
        uint32_t start_time = hal_.current_time_us();

        while (!hal_.read_scl()) {
            if ((hal_.current_time_us() - start_time) >= stretch_timeout_us_) {
                return std::unexpected(I2cError::SclTimeout);
            }
        }
        return {};
    }

    Hal hal_;
    uint32_t stretch_timeout_us_;
};
```
:::

---

### 3. Низькорівневе керування регістрами GPIO та способи комутації

При реалізації програмного I2C на сучасних 32-бітних мікроконтролерах (STM32, ESP32, RP2040, NXP LPC) вибір способу керування ніжками безпосередньо впливає на швидкодію, форму фронтів та споживання енергії.

Існує два основні підходи до схемотехнічної емуляції відкритого стоку:

#### 3.1. Апаратний режим Open-Drain (Рекомендований)
Виводи GPIO конфігуруються у відповідних регістрах як виходи з відкритим стоком:
- В архітектурі STM32: біти `OTy` регістра `GPIOx_OTYPER` встановлюються в `1` (`Open-Drain`), а режим виводу в `GPIOx_MODER` встановлюється як загальний вихід `01` (`Output mode`).
- Для подачі логічного нуля записується `1` у відповідний біт скидання регістра `GPIOx_BSRR` (нижні 16 біт або скидання `BRy`).
- Для подачі високого рівня (стан Hi-Z) записується `1` у біт встановлення `GPIOx_BSRR` (верхні 16 біт `BSy`). N-канальний польовий транзистор закривається, і зовнішній резистор `R_p` підтягує лінію до `V_DD`.

При цьому вхідний тригер Шмітта залишається активним, тому стан лінії зчитується безпосередньо з регістра `GPIOx_IDR` без жодних перемикань режимів піна.

#### 3.2. Динамічне перемикання напрямку (Direction Toggling)
Якщо мікроконтролер не підтримує апаратний режим відкритого стоку на вибраних виводах (як у старих 8-бітних чіпах PIC або 8051):
- Вихідний регістр даних (`PORT` / `ODR`) фіксується у значенні `0` (LOW).
- Для виставлення нуля вивід перемикається в режим **виходу** (`TRIS = 0` або `MODER = 01`). Транзистор відкривається і притягує лінію до землі.
- Для виставлення одиниці вивід перемикається в режим **входу** (`TRIS = 1` або `MODER = 00`). Внутрішні транзистори вимикаються, вивід переходить у стан Hi-Z, і резистор `R_p` формує високий рівень.

Цей підхід вимагає постійної модифікації регістра напрямку `MODER`, що додає додаткові такти інструкцій на кожну зміну стану сигналу, але гарантує електричну безпеку на будь-якому мікроконтролері.

---

### 4. Апаратна помилка кремнію Broadcom BCM2835 (Raspberry Pi)

Найвідомішим історичним прикладом того, чому потрібна програмна емуляція з коректним очікуванням SCL, є дефект у кристалі однокристальної системи Broadcom BCM2835, яка використовувалася в платах Raspberry Pi поколінь 1, 2, Zero та в обчислювальних модулях CM1.

Апаратний контролер I2C BSC (Broadcom Serial Controller) у цьому чипі містить кремнієву помилку в логіці кінцевого автомата:
1. Під час формування повторного старту (*Repeated START*) або після прийому біта підтвердження ACK, якщо ведений пристрій починає розтягувати такт SCL, апаратний блок BCM2835 коректно утримує лінію SCL, проте його внутрішній кінцевий автомат даних SDA продовжує просуватися за власною часовою сіткою!
2. В результаті лінія SDA змінює свій стан ще до того, як ведений відпустить SCL, або ведучий здійснює вибірку біта SDA у фіксований момент часу, коли напруга SCL ще фізично знаходиться на рівні нуля.
3. Це викликало систематичні збої та спотворення першого байта при роботі з такими популярними мікросхемами, як контролери сенсорних екранів, датчики якості повітря (наприклад, BME680, SGP30) та годинники реального часу RTC (DS3231), які потребують тривалого часу розтягування такту для внутрішніх обчислень.

Єдиним надійним технічним вирішенням цієї проблеми для платформи Linux на Raspberry Pi стало використання ядра Linux із драйвером `i2c-gpio` (bit-banging через підсистему GPIO), який працює за наведеним вище алгоритмом із повною підтримкою розтягування такту через функцію `i2c_bb_wait_scl_high()`.

---

### 5. Інтеграція з операційними системами реального часу (RTOS)

При використанні програмного I2C Master у середовищах із витісняльною багатозадачністю (FreeRTOS, Zephyr OS, ThreadX) необхідно враховувати два критичні фактори: блокування доступу та поведінку під час очікування SCL.

#### 5.1. Захист шини через м'ютекс
Оскільки програмна емуляція не має апаратного захисту від колізій, доступ до шини повинен монополізуватися за допомогою м'ютекса:

:::tabs
```c
// Захоплення шини перед початком транзакції в C / FreeRTOS
if (xSemaphoreTake(i2c_bus_mutex, pdMS_TO_TICKS(100)) == pdTRUE) {
    i2c_bb_start(&bus);
    i2c_bb_write_byte(&bus, dev_addr);
    // ... передача даних ...
    i2c_bb_stop(&bus);
    xSemaphoreGive(i2c_bus_mutex);
}
```
```cpp
// Захоплення шини через RAII std::lock_guard у C++
{
    std::lock_guard<std::mutex> lock(i2c_mutex);
    auto res = master.write(dev_addr, payload);
    if (!res) {
        // Обробка помилки обміну
    }
}
```
:::

#### 5.2. Поведінка під час розтягування такту
Якщо ведений пристрій розтягує такт на тривалий час (наприклад, `5...20 мс` під час запису сторінки EEPROM або обчислення криптографічного підпису в захищеному елементі ATECC608A), активне очікування у циклі `while (!read_scl())` марно завантажує процесорне ядро на 100%.

В оптимізованих драйверах RTOS застосовується комбінована стратегія:
1. **Короткі затримки (< 50 мкс):** виконання швидкого активного циклу з опитуванням таймера мікросекунд;
2. **Тривалі затримки (> 50 мкс):** налаштування виводу SCL на генерацію переривання за наростаючим фронтом (*EXTI Rising Edge*) і переведення поточної задачі у стан очікування семафора чи повідомлення `task_yield()` / `vTaskDelay()`. Щойно ведений відпускає SCL, апаратне переривання EXTI розблоковує задачу, повертаючи ядро до виконання обміну без втрати процесорного часу.

---

### 6. Осцилографічна діагностика та перевірка таймінгів

Під час налагодження програмного драйвера за допомогою логічного аналізатора або цифрового осцилоскопа необхідно контролювати наступні часові інтервали:

```
                  ┌─────────┐               ┌─────────┐
SCL (Master High) │         │               │         │
                  ┘         └───────────────┘         └─────
                                 ▲             ▲
                                 │◄─ t_stretch─►│
SCL (Bus Actual)  ───────────────┘             └────────────
```

1. **Фаза утримання SCL веденим (`t_stretch`):** на екрані осцилоскопа спостерігається як асиметричне подовження фази низького рівня перед 9-м тактом ACK або між окремими байтами.
2. **Форма наростаючого фронту:** наростання з нуля до 3.3 В має плавний експоненційний вигляд із часом наростання `t_r = 0.85 · R_p · C_b`. Якщо час наростання перевищує 1000 нс, необхідно зменшити опір підтяжки `R_p` (наприклад, з 10 кОм до 2.2 кОм).
3. **Захисний інтервал встановлення даних (`t_SU:DAT`):** стан лінії SDA повинен залишатися стабільним щонайменше 100 нс (для Standard-Mode — 250 нс) до моменту, коли напруга SCL перетне поріг `0.7 · V_DD`. Програмна затримка `delay_half_period_us()` у коді драйвера забезпечує запас стабільності понад 1.25...2.5 мкс, що гарантує безпомилкову роботу навіть при значних паразитах монтажу.

---

### 7. Програмна фільтрація високочастотних завад (Glitch Filtering)

В умовах промислового цеху або поруч із імпульсними перетворювачами напруги лінія SCL може зазнавати наведених імпульсних завад тривалістю `10...50 нс`. Оскільки програмний вхідний буфер мікроконтролера зазвичай опитується безпосередньо ядром, короткочасний сплеск напруги під час розтягування такту веденим може бути помилково розпізнаний функцією `wait_scl_high()` як завершення затримки.

Для усунення хибних спрацьовувань застосовується програмний цифровий фільтр мажоритарного голосування:

:::tabs
```c
// Функція опитування SCL із триточковим цифровим фільтром
static bool i2c_bb_read_scl_filtered(const i2c_bitbang_bus_t *bus) {
    uint8_t high_samples = 0;
    for (uint8_t i = 0; i < 3; i++) {
        if (bus->read_scl()) {
            high_samples++;
        }
    }
    // Рівень вважається високим, лише якщо щонайменше 2 вибірки з 3 підтвердили 1
    return (high_samples >= 2);
}
```
```cpp
// Шаблонний фільтр вибірки SCL у C++
template <typename Hal>
bool read_scl_filtered(Hal& hal) {
    uint8_t high_samples = 0;
    for (uint8_t i = 0; i < 3; ++i) {
        if (hal.read_scl()) {
            ++high_samples;
        }
    }
    return (high_samples >= 2);
}
```
:::

---

### 8. Приклад апаратної прив'язки (HAL Porting) для STM32 та ESP32

Для інтеграції вищенаведеного абстрактного драйвера в конкретний мікроконтролер необхідно реалізувати низькорівневі функції керування виводами.

#### 8.1. Реалізація для STM32 (прямий доступ до регістрів LL)

В архітектурі STM32 (наприклад, STM32F4 або STM32G4) виводи PB8 (SCL) та PB9 (SDA) налаштовуються в режимі `GPIO_MODE_OUTPUT` із типом `GPIO_OUTPUT_OPENDRAIN`. Керування здійснюється атомарним записом у регістр `BSRR`:

:::tabs
```c
// Реалізація низькорівневого HAL для STM32 мовою C
#include "stm32f4xx.h"

void stm32_scl_low(void) {
    GPIOB->BSRR = GPIO_BSRR_BR8; // Скидання PB8 в 0
}

void stm32_scl_high_z(void) {
    GPIOB->BSRR = GPIO_BSRR_BS8; // Відпускання PB8 у Hi-Z
}

bool stm32_read_scl(void) {
    return (GPIOB->IDR & GPIO_IDR_ID8) != 0;
}

void stm32_sda_low(void) {
    GPIOB->BSRR = GPIO_BSRR_BR9; // Скидання PB9 в 0
}

void stm32_sda_high_z(void) {
    GPIOB->BSRR = GPIO_BSRR_BS9; // Відпускання PB9 у Hi-Z
}

bool stm32_read_sda(void) {
    return (GPIOB->IDR & GPIO_IDR_ID9) != 0;
}

void stm32_delay_half(void) {
    // Затримка 5 мкс для швидкості 100 кГц (T_SCL/2)
    for (volatile uint32_t i = 0; i < 80; i++) {
        __NOP();
    }
}
```
```cpp
// Реалізація HAL для STM32 мовою C++ у вигляді структури
#include "stm32f4xx.h"

struct Stm32I2cHal {
    static void set_scl_low() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BR8;
    }
    static void set_scl_high_z() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BS8;
    }
    static bool read_scl() noexcept {
        return (GPIOB->IDR & GPIO_IDR_ID8) != 0;
    }
    static void set_sda_low() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BR9;
    }
    static void set_sda_high_z() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BS9;
    }
    static bool read_sda() noexcept {
        return (GPIOB->IDR & GPIO_IDR_ID9) != 0;
    }
    static void delay_half_period() noexcept {
        for (volatile uint32_t i = 0; i < 80; ++i) {
            __NOP();
        }
    }
    static uint32_t current_time_us() noexcept {
        return DWT->CYCCNT / (SystemCoreClock / 1000000);
    }
};
```
:::

#### 8.2. Реалізація для ESP32 (ESP-IDF Direct Registers)

В однокристальних системах ESP32/ESP32-S3 прямий доступ до виводів GPIO здійснюється через регістри швидкого встановлення та скидання `GPIO.out_w1ts` та `GPIO.out_w1tc`:

:::tabs
```c
// Реалізація HAL для ESP32 мовою C
#include "soc/gpio_struct.h"
#include "esp_timer.h"

#define PIN_SCL 22
#define PIN_SDA 21

void esp32_scl_low(void) {
    GPIO.out_w1tc = (1ULL << PIN_SCL);
}

void esp32_scl_high_z(void) {
    GPIO.out_w1ts = (1ULL << PIN_SCL);
}

bool esp32_read_scl(void) {
    return (GPIO.in >> PIN_SCL) & 0x1;
}

void esp32_sda_low(void) {
    GPIO.out_w1tc = (1ULL << PIN_SDA);
}

void esp32_sda_high_z(void) {
    GPIO.out_w1ts = (1ULL << PIN_SDA);
}

bool esp32_read_sda(void) {
    return (GPIO.in >> PIN_SDA) & 0x1;
}

uint32_t esp32_get_us(void) {
    return (uint32_t)esp_timer_get_time();
}
```
```cpp
// Реалізація HAL для ESP32 мовою C++
#include "soc/gpio_struct.h"
#include "esp_timer.h"

struct Esp32I2cHal {
    static constexpr uint32_t SclPin = 22;
    static constexpr uint32_t SdaPin = 21;

    static void set_scl_low() noexcept {
        GPIO.out_w1tc = (1ULL << SclPin);
    }
    static void set_scl_high_z() noexcept {
        GPIO.out_w1ts = (1ULL << SclPin);
    }
    static bool read_scl() noexcept {
        return (GPIO.in >> SclPin) & 0x1;
    }
    static void set_sda_low() noexcept {
        GPIO.out_w1tc = (1ULL << SdaPin);
    }
    static void set_sda_high_z() noexcept {
        GPIO.out_w1ts = (1ULL << SdaPin);
    }
    static bool read_sda() noexcept {
        return (GPIO.in >> SdaPin) & 0x1;
    }
    static void delay_half_period() noexcept {
        uint64_t start = esp_timer_get_time();
        while ((esp_timer_get_time() - start) < 5) {}
    }
    static uint32_t current_time_us() noexcept {
        return static_cast<uint32_t>(esp_timer_get_time());
    }
};
```
:::

---

### 9. Покрокова таблиця станів автомата при розтягуванні такту

Для візуалізації послідовності сигналів під час сеансу зв'язку наведено таблицю станів ліній під час передачі 1 байта з виникненням розтягування перед бітом підтвердження ACK:

| Крок | Дія ведучого | Стан MOSFET ведучого | Стан MOSFET веденого | Рівень SCL на шині | Рівень SDA на шині | Подія кінцевого автомата |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Виставлення біта 7 | Відкритий (0) | Закритий (Hi-Z) | 0.0 В (LOW) | `байт & 0x80` | Підготовка біта даних |
| 2 | Формування такту 7 | Закритий (Hi-Z) | Закритий (Hi-Z) | 3.3 В (HIGH) | Стабільний | Ведений стробує біт 7 |
| 3 | Спад такту 7 | Відкритий (0) | Закритий (Hi-Z) | 0.0 В (LOW) | Зміна | Підготовка наступного біта |
| ... | Передача бітів 6...0 | Перемикання | Прийом бітів | Імпульси SCL | Дані 6...0 | Зсув у вхідний регістр |
| 4 | Спад 8-го біта | Відкритий (0) | **ВІДКРИВАЄТЬСЯ (0)** | 0.0 В (LOW) | Hi-Z | Ведений заповнив буфер і підняв прапорець `RXNE` |
| 5 | Майстер відпускає SCL | **Закритий (Hi-Z)** | **Утримує (0)** | **0.0 В (LOW)** | `0` (ACK) | **АКТИВНЕ РОЗТЯГУВАННЯ ТАКТУ (`t_stretch`)** |
| 6 | Опитування `wait_scl_high` | Закритий (Hi-Z) | Утримує (0) | 0.0 В (LOW) | `0` (ACK) | Майстер зависає в циклі `while(!read_scl())` |
| 7 | Ведений вичитує `RXDR` | Закритий (Hi-Z) | **ЗАКРИВАЄТЬСЯ (Hi-Z)** | **3.3 В (HIGH)** | `0` (ACK) | SCL піднімається через резистор `R_p` |
| 8 | Зчитування квитанції | Закритий (Hi-Z) | Утримує SDA=0 | 3.3 В (HIGH) | `0` (ACK) | Майстер зчитує успішний ACK |
| 9 | Завершення такту ACK | Відкритий (0) | Закритий (Hi-Z) | 0.0 В (LOW) | Hi-Z | Перехід до наступного байта кадру |

---

### 10. Порівняльний аналіз: Апаратний I2C проти Bit-Banging

| Характеристика | Апаратний контролер I2C | Програмний Bit-Banging (наведений) |
| :--- | :--- | :--- |
| **Завантаження процесорного ядра (CPU)** | Мінімальне (0...2% при використанні DMA) | Високе (10...40% під час активного опитування) |
| **Реакція на помилки кремнію (Silicon Bugs)** | Фіксована на рівні кристала (не виправляється) | Гнучка (повний програмний контроль та виправлення) |
| **Підтримка Clock Stretching** | Апаратна (якщо не пошкоджена в кремнії) | Повна програмна з регульованим таймаутом |
| **Прив'язка до фізичних виводів плати** | Жорстко обмежена матрицею AF пінів | Будь-які доступні виводи GPIO на платі |
| **Відновлення після зависання шини** | Часто вимагає повного скидання периферії | Вбудована функція `recover_bus()` (9 імпульсів) |
| **Максимальна робоча швидкість** | До 1 Мбіт/с (Fast-Mode Plus) або 3.4 Мбіт/с | До 100...400 кбіт/с (обмежується тактовою частотою) |

---

### 11. Налаштування драйвера `i2c-gpio` у середовищі Linux (Device Tree)

В операційних системах Linux на базі одноплатних комп'ютерів (Raspberry Pi, BeagleBone, Allwinner) стандартний підхід полягає у використанні ядра Linux із модулем `i2c-gpio`. Цей модуль створює стандартний вузол `/dev/i2c-N`, реалізуючи Bit-Banging із повноцінною підтримкою розтягування такту на рівні ядра.

Конфігурація описується у дереві пристроїв (*Device Tree Overlay*):

```dts
/dts-v1/;
/plugin/;

/ {
    compatible = "brcm,bcm2835";

    fragment@0 {
        target-path = "/";
        __overlay__ {
            i2c_soft: i2c-gpio-soft {
                compatible = "i2c-gpio";
                gpios = <&gpio 23 0>, /* SDA: GPIO23, активний 0 */
                        <&gpio 24 0>; /* SCL: GPIO24, активний 0 */
                i2c-gpio,delay-us = <2>; /* Затримка: швидкість ~100 кГц */
                i2c-gpio,timeout-ms = <50>; /* Таймаут розтягування: 50 мс */
                #address-cells = <1>;
                #size-cells = <0>;
                status = "okay";
            };
        };
    };
};
```

Параметр `i2c-gpio,timeout-ms = <50>` передається у внутрішню функцію ядра `i2c_bitbang_wait_scl()`, де ядро автоматично контролює час очікування сигналу від веденого вузла, запобігаючи блокуванню системних викликів `read()` та `write()` у просторі користувача.

---

### 12. Покроковий розбір реального діагностичного сеансу (Датчик SHT31)

Розглянемо практичний випадок опитування цифрового давача вологості та температури Sensirion SHT31 на шині 400 кГц.

#### 12.1. Сценарій обміну
1. Ведучий надсилає команду одноразового вимірювання високої точності: `START` -> `0x44 (Write)` -> `0x2C` -> `0x06` -> `STOP`.
2. Ведучий надсилає команду зчитування: `START` -> `0x44 (Read)`.
3. Оскільки датчик перебуває в процесі аналогового вимірювання (який триває `15 мс`), ведений використовує апаратний режим Clock Stretching: після прийому своєї адреси він виставляє біт ACK (SDA=0) і примусово утримує тактову лінію SCL на рівні нуля протягом усіх 15 мілісекунд.
4. Ведучий, викликавши `i2c_bb_wait_scl_high()`, фіксує низький рівень SCL і очікує.
5. Через 15 мс датчик завершує квантування, закриває свій польовий транзистор на SCL, лінія повертається до 3.3 В, і ведучий негайно зчитує 6 байтів виміряних даних (температура MSB/LSB/CRC та вологість MSB/LSB/CRC).

Якщо прошивка ведучого не підтримує розтягування такту, на кроці 3 вона згенерує тактовий імпульс для читання першого байта безпосередньо під час аналогового перетворення датчика. Оскільки ведений не готовий, він поверне стан NACK або видасть байт `0xFF`, що призведе до фатальної помилки вимірювання.

---

### 14. Апаратні таймери та лічильники циклів DWT проти затримок на циклах

У наведених прикладах функції затримки півперіоду `delay_half_period_us()` використовують програмні цикли `__NOP()`. Для простих демонстраційних завдань цього достатньо, проте в промисловому коді такий підхід має суттєві недоліки:
- **Залежність від частоти ядра:** при динамічній зміні частоти тактування MCU (технології енергозбереження Dynamic Frequency Scaling / DVFS) швидкість шини I2C плаває;
- **Оптимізація компілятора:** рівні оптимізації `-O2` або `-O3` можуть викидати порожні цикли або змінювати кількість тактів на ітерацію.

Для забезпечення абсолютної часової стабільності інтервалів `T_LOW`, `T_HIGH` та таймаутів очікування розтягування рекомендується використовувати апаратний 32-бітний лічильник циклів ядра DWT (Data Watchpoint and Trace) у мікроконтролерах ARM Cortex-M3/M4/M7/M33:

:::tabs
```c
// Ініціалізація та точна затримка через лічильник DWT у C
void dwt_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

void dwt_delay_us(uint32_t us) {
    uint32_t start_cycles = DWT->CYCCNT;
    uint32_t required_cycles = us * (SystemCoreClock / 1000000);
    while ((DWT->CYCCNT - start_cycles) < required_cycles) {
        // Очікування завершення апаратного відліку
    }
}
```
```cpp
// Точна затримка DWT у C++ з використанням constexpr
class DwtTimer {
public:
    static void init() noexcept {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    }

    static void delay_us(uint32_t us) noexcept {
        const uint32_t start = DWT->CYCCNT;
        const uint32_t count = us * (SystemCoreClock / 1000000);
        while ((DWT->CYCCNT - start) < count) {
            // Апаратне очікування
        }
    }
};
```
:::

Використання апаратного лічильника гарантує точність формування часових інтервалів до одного такту процесора, виключає вплив кодогенерації компілятора і забезпечує надійну фіксацію будь-яких затримок розтягування такту з боку ведених пристроїв.

---

### 15. Карта несправностей та чек-лист апаратної перевірки

Під час запуску програмного I2C Master рекомендується перевірити типові апаратні та схемотехнічні дефекти:

1. **Помилка `I2C_BB_ERROR_BUS_BUSY` на старті:**
   - *Причина:* Лінія SDA постійно притягнута до нуля (0 В).
   - *Перевірка:* Відключити ведені пристрої по черзі; виконати виклик `i2c_bb_recover_bus()`; перевірити наявність короткого замикання доріжки на землю.

2. **Помилка `I2C_BB_ERROR_SCL_TIMEOUT`:**
   - *Причина:* Лінія SCL не піднімається вище 0.8 В після переведення в стан Hi-Z.
   - *Перевірка:* Відсутній або обірваний резистор підтяжки `R_p`; надмірно велика ємність шини (> 400 пФ); ведений мікроконтролер завис у нескінченному циклі обробника переривання, тримаючи відкритим затвор вихідного транзистора.

3. **Спорадичні помилки `I2C_BB_ERROR_NACK`:**
   - *Причина:* Занадто великий опір підтяжки `R_p` (наприклад, 47 кОм), через що час наростання `t_r` перевищує допустимий захисний інтервал, і ведений пропускає адресний строб.
   - *Лікування:* Замінити резистори підтяжки на номінал 2.2...4.7 кОм.

Програмна реалізація Bit-Banging із повноцінною обробкою розтягування такту та контролем таймаутів є незамінним інструментом при побудові високонадійних вбудованих систем, де відмова окремого веденого датчика не повинна блокувати роботу основного керуючого комп'ютера. Вона забезпечує повний контроль над кожною мікросекундою протоколу, дозволяє обходити кремнієві дефекти апаратних контролерів і слугує надійним еталоном під час розробки та тестування нових пристроїв I2C та SMBus.




