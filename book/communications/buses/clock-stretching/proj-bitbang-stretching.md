# ⚙️ Програмний ведучий I2C із розпізнаванням Clock Stretching та відновленням шини

Коли апаратний контролер мікропроцесора містить помилки реалізації розтягування такту (як це сталося в SoC Broadcom BCM2835) або коли на мікроконтролері бракує вільних апаратних інтерфейсів I2C, єдиним надійним рішенням стає програмна емуляція шини — бітбанґінг (англ. *bit-banging*, пряме програмне керування виводами загального призначення GPIO).

Більшість навчальних реалізацій бітбанґінгу припускаються фатальної помилки: вони генерують імпульси такту «наосліп», перемикаючи лінію SCL між 0 та 1 через фіксовані затримки часу. Коли такий ведучий звертається до цифрового давача температури, вологості (наприклад, SHT21 або HTU21D) чи мікросхеми АЦП, ведений пристрій утримує лінію SCL на рівні 0V для виконання внутрішнього вимірювання. «Сліпий» ведучий цього не помічає, продовжує відлік мікросекунд, фіксує біти з порожньої шини та зчитує суцільні `0xFF` або сміттєві дані.

Нижче наведено промислову реалізацію програмного ведучого I2C, яка містить повний захист від усіх пасток шини: емуляцію відкритого стоку, опитування зворотного зв'язку лінії SCL (SCL sensing), захист від вічного дедлоку через таймаут 35 мс за стандартом SMBus та автоматичну процедуру 9-тактового розблокування завислої лінії SDA.

### Архітектура та правила емуляції відкритого стоку

Для коректної роботи монтажного «І» ведучий ніколи не повинен примусово виставляти на виводах високий рівень у режимі Push-Pull (підключати пін до `V_DD` через верхній транзистор). Якщо ведений тримає 0V, а ведучий подасть 3.3V через push-pull, виникне наскрізне коротке замикання, яке призведе до перегріву й деградації виводів кристала.

Правильне керування лініями Open-Drain через звичайні виводи GPIO будується за двома станами:
1. **Логічний 0 (Active Low):** вивід налаштовується як цифровий вихід (Output) і на ньому встановлюється низький рівень (LOW, 0V). Внутрішній N-MOSFET відкритий на землю.
2. **Логічна 1 (High-Z / Release):** вивід налаштовується як цифровий вхід (Input) без внутрішньої підтяжки (або з нейтральним станом). Пін переходить у стан високого імпедансу (High-Z). Зовнішній резистор-підтяжка `R_p` підтягує лінію до напруги живлення `V_DD`.

### Реалізація драйвера з контролем SCL

Погляньмо на реалізацію драйвера двома мовами. Вкладка C демонструє роботу на рівні структур і функцій з платформонезалежними апаратними викликами; вкладка C++ реалізує сучасний об'єктний підхід стандарту C++20 із строгим контролем типів, безпечною обробкою помилок через `std::expected` та вимірюванням таймаутів через бібліотеку `std::chrono`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Коди помилок шини I2C */
typedef enum {
    I2C_OK = 0,
    I2C_ERR_TIMEOUT = -1,     /* Ведений утримує SCL довше за допустимий таймаут */
    I2C_ERR_NACK_ADDR = -2,    /* Ведений не підтвердив свою адресу */
    I2C_ERR_NACK_DATA = -3,    /* Ведений відхилив байт даних */
    I2C_ERR_BUS_BUSY = -4     /* Лінії шини замкнені або зайняті */
} i2c_status_t;

/* Платформозалежні прототипи функцій низького рівня (HAL) */
extern void hal_gpio_init(void);
extern void hal_scl_drive_low(void);   /* Режим Output, 0V */
extern void hal_scl_release(void);     /* Режим Input (High-Z) */
extern bool hal_scl_read(void);        /* Зчитування логічного рівня піна SCL */
extern void hal_sda_drive_low(void);   /* Режим Output, 0V */
extern void hal_sda_release(void);     /* Режим Input (High-Z) */
extern bool hal_sda_read(void);        /* Зчитування логічного рівня піна SDA */
extern void hal_delay_us(uint32_t us); /* Затримка в мікросекундах */

/* Конфігураційні параметри для швидкості 100 кГц (Standard Mode) */
#define I2C_HALF_CLOCK_US     5
#define I2C_STRETCH_TIMEOUT_US 35000  /* 35 мс за стандартом SMBus */

/* 
 * Відпускання лінії SCL із контролем розтягування (Clock Stretching) 
 * Повертає I2C_OK після підтвердження високого рівня або I2C_ERR_TIMEOUT
 */
static i2c_status_t i2c_scl_release_and_wait(void) {
    hal_scl_release(); /* Відпускаємо лінію в High-Z, резистор Rp тягне її до VDD */

    uint32_t elapsed_us = 0;
    while (!hal_scl_read()) {
        hal_delay_us(1);
        elapsed_us++;
        if (elapsed_us >= I2C_STRETCH_TIMEOUT_US) {
            return I2C_ERR_TIMEOUT; /* Захист від нескінченного зависання шини */
        }
    }
    return I2C_OK;
}

/* Формування сигналу СТАРТ (START condition) */
static i2c_status_t i2c_start(void) {
    hal_sda_release();
    if (i2c_scl_release_and_wait() != I2C_OK) return I2C_ERR_BUS_BUSY;
    
    hal_delay_us(I2C_HALF_CLOCK_US);
    hal_sda_drive_low(); /* Спад SDA при високому SCL */
    hal_delay_us(I2C_HALF_CLOCK_US);
    hal_scl_drive_low();
    return I2C_OK;
}

/* Формування сигналу СТОП (STOP condition) */
static i2c_status_t i2c_stop(void) {
    hal_sda_drive_low();
    hal_delay_us(I2C_HALF_CLOCK_US);
    
    if (i2c_scl_release_and_wait() != I2C_OK) return I2C_ERR_TIMEOUT;
    hal_delay_us(I2C_HALF_CLOCK_US);
    
    hal_sda_release(); /* Наростання SDA при високому SCL */
    hal_delay_us(I2C_HALF_CLOCK_US);
    return I2C_OK;
}

/* Передача одного байта з контролем підтвердження ACK/NACK */
static i2c_status_t i2c_write_byte(uint8_t byte, bool *ack_received) {
    for (int8_t bit = 7; bit >= 0; bit--) {
        if ((byte >> bit) & 1) {
            hal_sda_release();
        } else {
            hal_sda_drive_low();
        }
        hal_delay_us(I2C_HALF_CLOCK_US);

        /* Підйом SCL з очікуванням веденого */
        if (i2c_scl_release_and_wait() != I2C_OK) return I2C_ERR_TIMEOUT;
        hal_delay_us(I2C_HALF_CLOCK_US);
        hal_scl_drive_low();
    }

    /* 9-й такт: зчитування біта підтвердження (ACK від веденого) */
    hal_sda_release();
    hal_delay_us(I2C_HALF_CLOCK_US);

    if (i2c_scl_release_and_wait() != I2C_OK) return I2C_ERR_TIMEOUT;
    hal_delay_us(I2C_HALF_CLOCK_US / 2);

    /* Якщо ведений притягнув SDA до 0, це ACK (успіх) */
    *ack_received = !hal_sda_read();

    hal_delay_us(I2C_HALF_CLOCK_US / 2);
    hal_scl_drive_low();
    return I2C_OK;
}

/* Зчитування одного байта з генерацією ACK або NACK */
static i2c_status_t i2c_read_byte(uint8_t *byte, bool send_ack) {
    uint8_t result = 0;
    hal_sda_release();

    for (int8_t bit = 7; bit >= 0; bit--) {
        hal_delay_us(I2C_HALF_CLOCK_US);

        /* Ведений може розтягувати такт перед виставленням будь-якого біта даних */
        if (i2c_scl_release_and_wait() != I2C_OK) return I2C_ERR_TIMEOUT;
        hal_delay_us(I2C_HALF_CLOCK_US / 2);

        if (hal_sda_read()) {
            result |= (1 << bit);
        }
        hal_delay_us(I2C_HALF_CLOCK_US / 2);
        hal_scl_drive_low();
    }

    /* 9-й такт: надсилання підтвердження від ведучого */
    if (send_ack) {
        hal_sda_drive_low(); /* ACK: ведучий готовий приймати далі */
    } else {
        hal_sda_release();   /* NACK: завершення читання */
    }
    hal_delay_us(I2C_HALF_CLOCK_US);

    if (i2c_scl_release_and_wait() != I2C_OK) return I2C_ERR_TIMEOUT;
    hal_delay_us(I2C_HALF_CLOCK_US);
    hal_scl_drive_low();
    hal_sda_release();

    *byte = result;
    return I2C_OK;
}

/*
 * Процедура аварійного очищення шини (Bus Recovery / Clear):
 * генерує до 9 тактів SCL для виштовхування завислого біта веденого
 */
void i2c_recover_bus(void) {
    hal_sda_release();
    hal_scl_release();
    hal_delay_us(I2C_HALF_CLOCK_US);

    /* Якщо SDA утримується на 0, генеруємо такти доти, доки SDA не звільниться */
    for (uint8_t i = 0; i < 9; i++) {
        if (hal_sda_read()) break;

        hal_scl_drive_low();
        hal_delay_us(I2C_HALF_CLOCK_US);
        hal_scl_release();
        hal_delay_us(I2C_HALF_CLOCK_US);
    }

    /* Завершуємо процедуру примусовим формуванням сигналу STOP */
    i2c_stop();
}
```
```cpp
#include <cstdint>
#include <chrono>
#include <expected>
#include <span>
#include <concepts>

enum class I2cError : int8_t {
    Timeout = -1,
    NackAddress = -2,
    NackData = -3,
    BusBusy = -4
};

/* Концепт для низькорівневого апаратного адаптера виводів GPIO */
template <typename T>
concept I2cHalPinAdapter = requires(T hal, uint32_t us) {
    { hal.scl_drive_low() } -> std::same_as<void>;
    { hal.scl_release() }   -> std::same_as<void>;
    { hal.scl_read() }      -> std::same_as<bool>;
    { hal.sda_drive_low() } -> std::same_as<void>;
    { hal.sda_release() }   -> std::same_as<void>;
    { hal.sda_read() }      -> std::same_as<bool>;
    { hal.delay_us(us) }    -> std::same_as<void>;
};

template <I2cHalPinAdapter Hal>
class BitbangI2cMaster {
public:
    explicit constexpr BitbangI2cMaster(Hal& hal, uint32_t half_period_us = 5, 
                                        uint32_t timeout_us = 35000) noexcept
        : hal_(hal), half_period_us_(half_period_us), timeout_us_(timeout_us) {}

    /* Запис послідовності байтів у ведений пристрій */
    std::expected<void, I2cError> write(uint8_t addr_7bit, std::span<const uint8_t> data) noexcept {
        auto res = start();
        if (!res) return res;

        /* Байт адреси з бітом запису (R/W = 0) */
        uint8_t addr_byte = static_cast<uint8_t>(addr_7bit << 1);
        bool ack = false;
        if (auto w_res = write_byte(addr_byte, ack); !w_res) {
            stop();
            return w_res;
        }
        if (!ack) {
            stop();
            return std::unexpected(I2cError::NackAddress);
        }

        for (const uint8_t byte : data) {
            if (auto w_res = write_byte(byte, ack); !w_res) {
                stop();
                return w_res;
            }
            if (!ack) {
                stop();
                return std::unexpected(I2cError::NackData);
            }
        }

        return stop();
    }

    /* Зчитування послідовності байтів із веденого пристрою */
    std::expected<void, I2cError> read(uint8_t addr_7bit, std::span<uint8_t> buffer) noexcept {
        auto res = start();
        if (!res) return res;

        /* Байт адреси з бітом читання (R/W = 1) */
        uint8_t addr_byte = static_cast<uint8_t>((addr_7bit << 1) | 0x01);
        bool ack = false;
        if (auto w_res = write_byte(addr_byte, ack); !w_res) {
            stop();
            return w_res;
        }
        if (!ack) {
            stop();
            return std::unexpected(I2cError::NackAddress);
        }

        const size_t len = buffer.size();
        for (size_t i = 0; i < len; ++i) {
            bool send_ack = (i + 1 < len); /* Для останнього байта шлемо NACK */
            if (auto r_res = read_byte(buffer[i], send_ack); !r_res) {
                stop();
                return r_res;
            }
        }

        return stop();
    }

    /* Процедура 9-тактового аварійного розблокування завислої шини */
    void recover_bus() noexcept {
        hal_.sda_release();
        hal_.scl_release();
        hal_.delay_us(half_period_us_);

        for (uint8_t i = 0; i < 9; ++i) {
            if (hal_.sda_read()) break;
            hal_.scl_drive_low();
            hal_.delay_us(half_period_us_);
            hal_.scl_release();
            hal_.delay_us(half_period_us_);
        }
        stop();
    }

private:
    Hal& hal_;
    uint32_t half_period_us_;
    uint32_t timeout_us_;

    std::expected<void, I2cError> scl_release_and_wait() noexcept {
        hal_.scl_release();
        uint32_t elapsed = 0;
        while (!hal_.scl_read()) {
            hal_.delay_us(1);
            if (++elapsed >= timeout_us_) {
                return std::unexpected(I2cError::Timeout);
            }
        }
        return {};
    }

    std::expected<void, I2cError> start() noexcept {
        hal_.sda_release();
        if (auto res = scl_release_and_wait(); !res) return std::unexpected(I2cError::BusBusy);
        
        hal_.delay_us(half_period_us_);
        hal_.sda_drive_low();
        hal_.delay_us(half_period_us_);
        hal_.scl_drive_low();
        return {};
    }

    std::expected<void, I2cError> stop() noexcept {
        hal_.sda_drive_low();
        hal_.delay_us(half_period_us_);
        if (auto res = scl_release_and_wait(); !res) return res;
        hal_.delay_us(half_period_us_);
        hal_.sda_release();
        hal_.delay_us(half_period_us_);
        return {};
    }

    std::expected<void, I2cError> write_byte(uint8_t byte, bool& ack) noexcept {
        for (int8_t bit = 7; bit >= 0; --bit) {
            if ((byte >> bit) & 1) {
                hal_.sda_release();
            } else {
                hal_.sda_drive_low();
            }
            hal_.delay_us(half_period_us_);

            if (auto res = scl_release_and_wait(); !res) return res;
            hal_.delay_us(half_period_us_);
            hal_.scl_drive_low();
        }

        hal_.sda_release();
        hal_.delay_us(half_period_us_);
        if (auto res = scl_release_and_wait(); !res) return res;
        hal_.delay_us(half_period_us_ / 2);

        ack = !hal_.sda_read();

        hal_.delay_us(half_period_us_ / 2);
        hal_.scl_drive_low();
        return {};
    }

    std::expected<void, I2cError> read_byte(uint8_t& byte, bool send_ack) noexcept {
        uint8_t val = 0;
        hal_.sda_release();

        for (int8_t bit = 7; bit >= 0; --bit) {
            hal_.delay_us(half_period_us_);
            if (auto res = scl_release_and_wait(); !res) return res;
            hal_.delay_us(half_period_us_ / 2);

            if (hal_.sda_read()) {
                val |= static_cast<uint8_t>(1 << bit);
            }
            hal_.delay_us(half_period_us_ / 2);
            hal_.scl_drive_low();
        }

        if (send_ack) {
            hal_.sda_drive_low();
        } else {
            hal_.sda_release();
        }
        hal_.delay_us(half_period_us_);

        if (auto res = scl_release_and_wait(); !res) return res;
        hal_.delay_us(half_period_us_);
        hal_.scl_drive_low();
        hal_.sda_release();

        byte = val;
        return {};
    }
};
```
:::

### Детальний розбір критичних ділянок коду

Розгляньмо ключові нюанси функціонування коду, які відрізняють надійний системний драйвер від аматорського скрипту:

1. **Функція `scl_release_and_wait()`:**
   Це серцевина підтримки Clock Stretching. Після переведення піна SCL у режим високого імпедансу функція не просто чекає `I2C_HALF_CLOCK_US`, а входить у цикл опитування `while (!hal_scl_read())`. Якщо ведений пристрій тримає SCL на рівні 0V (наприклад, під час внутрішнього аналого-цифрового перетворення або запису сторінки Flash), ведучий зациклюється на затримці `hal_delay_us(1)`, залишаючи свій вихід у High-Z.

2. **Захист лічильником таймауту (35 000 мкс):**
   Без лічильника `elapsed_us` будь-який апаратний збій веденого (зависання ядра сенсора, короткий замикач на платі, обрив живлення під час транзакції) перетворив би цикл `while` на нескінченний дедлок. Значення 35 мс обрано відповідно до стандарту SMBus `t_TIMEOUT`. Якщо ведений не звільнив лінію за цей час, функція повертає код `I2C_ERR_TIMEOUT`, даючи змогу верхньому рівню застосунку зафіксувати аномалію та ініціювати перезавантаження шини або живлення периферії.

3. **Семплування біта ACK посередині імпульсу:**
   Зверніть увагу на поділ затримки високого рівня: `hal_delay_us(I2C_HALF_CLOCK_US / 2)`. Опитування стану лінії SDA виконується суворо посередині високого стану SCL, коли всі перехідні процеси перезаряджання паразитної ємності шини `C_b` через резистор `R_p` гарантовано завершилися, а сигнал стабілізувався.

4. **Процедура аварійного розблокування `i2c_recover_bus()`:**
   Типова проблема I2C виникає, коли мікроконтролер ведучого перезавантажується (через Watchdog або скидання живлення) посеред операції зчитування байта, у момент, коли ведений пристрій якраз передавав логічний «0» на лінії SDA. Після рестарту апаратний I2C-контролер ведучого бачить SDA = 0V, вважає шину зайнятою іншим майстром і намертво блокується.
   Програмна процедура відновлення перемикає піни в режим GPIO і надсилає до 9 тактів SCL. Кожен такт змушує ведений пристрій виштовхувати наступний біт зі свого внутрішнього зсувного регістра. Максимум через 9 тактів ведений дійде до фази ACK/NACK, відпустить лінію SDA у стан High-Z (SDA = 1) і буде готовий прийняти команду STOP для остаточного повернення шини у стан спокою.

### Крайові випадки: фізика фронтів, ємність шини та тригери Шмітта

При програмній реалізації протоколу на мікроконтролерах часто забувають про аналогову природу відкритого стоку. Коли ведучий відпускає лінію SCL у High-Z, наростання напруги відбувається не миттєво, а за експоненційним законом заряджання RC-ланцюга:

```
V(t) = V_DD · (1 - e^(-t / (R_p · C_b)))
```

де `R_p` — опір підтягувального резистора, а `C_b` — сумарна паразитна ємність лінії (доріжки друкованої плати, вхідні ємності пінів мікросхем, кабелі).

Для досягнення логічного рівня одиниці (`V_IH = 0.7 · V_DD`) лінії потрібен час:

```
t_r = 0.8473 · R_p · C_b
```

Якщо на шині висить кілька модулів із сумарною ємністю `C_b = 300 пФ` при резисторі `R_p = 4.7 кОм`, час наростання фронту становить:

```
t_r ≈ 0.8473 · 4700 · 300·10^(-12) ≈ 1.19 мкс
```

Це призводить до двох критичних наслідків для програмного драйвера:
1. **Фальшивий Clock Stretching:** Якщо ведучий викликає `hal_scl_read()` занадто швидко після `hal_scl_release()` (наприклад, через 50 наносекунд на швидкому мікроконтролері з частотою 480 МГц), напруга на лінії ще не встигне перетнути поріг `V_IH`. Програма сприйме повільне аналогове наростання як утримання лінії веденим і зайде у фальшивий цикл розтягування. Саме тому в коді перед опитуванням встановлюється мінімальна затримка в 1 мікросекунду або додається явний фільтр брязкоту.
2. **Необхідність тригера Шмітта на вході GPIO:** Повільний фронт наростання напруги у зоні невизначеності (між `0.3 · V_DD` та `0.7 · V_DD`) робить вхідний буфер вразливим до високочастотних шумів. Будь-яка наведена завада в цій зоні може викликати багаторазове хибне спрацьовування вхідного логічного вентиля. Тому піни GPIO, виділені під програмний I2C, обов'язково повинні мати ввімкнений гістерезис (тригер Шмітта, Schmitt Trigger input).

### Сенсорні режими: Hold Master проти No Hold Master

Класичним прикладом взаємодії з Clock Stretching у практичній розробці є популярні цифрові давачі вологості та температури сімейства Sensirion SHT21 / Silicon Labs Si7021 / TE HTU21D. У їхніх даташитах описано два фундаментальні режими вимірювання:

1. **Режим Hold Master (використовує Clock Stretching):**
   Ведучий відправляє команду запуску вимірювання (наприклад, `0xE3` для температури) і відразу генерує повторний СТАРТ (Repeated START) із адресою читання. Давач відповідає бітом ACK, після чого негайно притягує лінію SCL до 0V і тримає її у стані розтягування протягом усього часу роботи свого АЦП (близько 65–85 мс). Ведучий залишається заблокованим на лінії SCL, доки сенсор не завершить перетворення й не відпустить такт, після чого ведучий безперервно зчитує 2 байти результату та 1 байт контрольної суми CRC.
   *Перевага:* мінімальний протокольний оверхед — усього одна I2C-транзакція.
   *Недолік:* шина повністю паралізована на 85 мс; якщо ведучий працює під керуванням RTOS або обслуговує інші критичні датчики, такий підхід неприйнятний, а на шинах SMBus це викликає спрацьовування таймауту 35 мс.

2. **Режим No Hold Master (без Clock Stretching):**
   Ведучий надсилає команду запуску (`0xF3`), але сенсор після отримання байта видає ACK і відпускає SCL, не блокуючи шину. Сенсор починає вимірювання автономно, а шина I2C залишається вільною для спілкування ведучого з іншими чипами.
   Щоб дізнатися, чи завершилося перетворення, ведучий періодично намагається прочитати дані. Поки АЦП зайнятий, сенсор відповідає сигналом NACK (відхилення адреси). Щойно перетворення готове, сенсор відповідає ACK і повертає байти вимірювання.
   *Перевага:* шина не блокується, повна сумісність із дефектними контролерами (як BCM2835 у Raspberry Pi) та протоколом SMBus.
   *Недолік:* багаторазові холості запити створюють додатковий трафік на шині.

### Взаємодія з двонаправленими перетворювачами рівнів (Level Shifters)

У змішаних системах, де ведучий мікроконтролер працює від 3.3V, а ведений давач або контролер двигуна живиться від 5V (або 1.8V у сучасних мобільних чипах), між ними встановлюють двонаправлений перетворювач рівнів на дискретних польових транзисторах (класична схема на BSS138 або спеціалізовані мікросхеми на зразок TI PCA9306 чи NXP PCA9517).

Схема на MOSFET містить два підтягувальні резистори: `R_p1` до низьковольтного живлення `V_DD1` (3.3V) та `R_p2` до високовольтного `V_DD2` (5V), а транзистор увімкнений між ними за схемою зі спільним затвором (затвор підключено до `V_DD1`).

Коли ведений на боці 5V активує Clock Stretching і притягує лінію SCL до 0V:
1. Паразитний діод у структурі транзистора зміщується у прямому напрямку, затвор-витік відкриває MOSFET, і напруга на боці 3.3V також падає до 0V (точніше, до залишкової напруги відкритого каналу `V_OL = I_pull-up · R_DS(on) ≈ 0.1–0.2V`).
2. Ведучий 3.3V бачить цей нуль і коректно зупиняє свій такт.
3. Проте, коли ведений відпускає лінію, транзистор закривається, і кожна сторона заряджається своїм власним RC-ланцюгом. Якщо підтягувальні резистори підібрані занадто великими (наприклад, 10 кОм замість 2.2–4.7 кОм), наростання напруги на високовольтному боці 5V відбуватиметься значно повільніше, ніж на боці 3.3V. Ведучий може зафіксувати `V_IH` на своєму піні раніше, ніж ведений на боці 5V розпізнає високий рівень, що призведе до збою синхронізації та порушення часового вікна утримання даних `t_HD:DAT`.

### Діагностика Clock Stretching на логічному аналізаторі

Під час налагодження обміну через логічний аналізатор (Saleae Logic, Sigrok / PulseView або цифровий осцилограф) важливо вміти візуально відрізняти нормальне розтягування такту від аномалій шини:

1. **Нормальний Clock Stretching:**
   На осцилограмі видно, що лінія SCL залишається на рівні 0V протягом тривалого часу (від кількох мікросекунд до десятків мілісекунд), при цьому лінія SDA залишається нерухомою (зазвичай на рівні 0V під час фази ACK або на рівні першого біта відповіді). Після закінчення паузи SCL плавно наростає за експонентою до `V_DD`, і лише після досягнення рівня `0.7 · V_DD` ведучий генерує черговий спадний фронт.

2. **Апаратний збій контролера (баг типу BCM2835):**
   На декодері протоколу з'являються прапорці «Missing ACK», «Unexpected START/STOP» або «Frame Error». На аналоговому графіку видно, що лінія SCL формує вузькі паразитні імпульси (глітчі, англ. *glitches*) або лінія SDA починає перемикатися в момент, коли SCL ще перебуває на рівні 0V, що свідчить про розсинхронізацію внутрішнього автомата ведучого.

3. **Колізія арбітражу (Arbitration Loss):**
   Якщо два ведучі одночасно звернулися до шини, і один із них намагається формувати такт, а інший повільніший ведучий або ведений утримує SCL, результуючий такт на шині автоматично синхронізується за найдовшим низьким рівнем. Ведучий із коротшим періодом `t_LOW` чекає ведучого з довшим періодом, що є штатною поведінкою монтажного «І».

4. **Зависання лінії SDA (Bus Lockup):**
   Лінія SCL вільна (3.3V), але лінія SDA намертво сидить у нулі (0V). Будь-які спроби ведучого сформувати сигнал СТАРТ завершуються невдачею, оскільки ведучий не може забезпечити спадний перепад SDA при високому SCL. Застосування функції `i2c_recover_bus()` у цей момент чітко показує 9 імпульсів на SCL, після чого на 4–8 такті лінія SDA різко підстрибує до 3.3V, а завершальний сигнал СТОП повертає шину до робочого стану.

### Взаємодія з операційними системами реального часу (RTOS)

Коли програмний I2C-драйвер інтегрується в систему під керуванням операційної системи реального часу (FreeRTOS, Zephyr або RT-Thread), постає питання оптимізації процесорного часу під час тривалого розтягування такту.

Якщо давач розтягує такт на 10–50 мілісекунд, тупе очікування у циклі `while (!hal_scl_read())` з монопольним завантаженням процесора марнує обчислювальні ресурси та блокує виконання потоків із нижчим пріоритетом.

У професійних RTOS-драйверах застосовують гібридну схему:
1. Перші 50–100 мікросекунд очікування виконуються у короткому циклі активного опитування (busy-wait), оскільки більшість дрібних мікросхем (EEPROM, ЦАП) розтягують такт лише на час переривання (2–20 мкс), і перемикання контексту RTOS зайняло б більше часу, ніж саме очікування.
2. Якщо лінія SCL не піднялася через 100 мкс, драйвер перемикає пін SCL у режим переривання за наростаючим фронтом (GPIO Rising Edge Interrupt), переводить поточну задачу у стан блокування (`vTaskSuspend()` або очікування бінарного семафора `xSemaphoreTake()`) і передає процесор іншим потокам.
3. Коли ведений нарешті відпускає лінію SCL і напруга досягає `V_IH`, апаратне переривання GPIO розблоковує задачу I2C через `xSemaphoreGiveFromISR()`, драйвер відновлює генерацію такту та завершує транзакцію.

Така архітектура поєднує високу швидкість на коротких затримках із повною енергоефективністю та багатозадачністю на довгих апаратних операціях ведених пристроїв.

### Платформенна адаптація та нульова вартість абстракцій (Zero-Cost HAL)

Шаблонний клас `BitbangI2cMaster` у вкладці C++ використовує концепт `I2cHalPinAdapter`. Це дозволяє компілятору повністю вбудовувати (інлайнити) низькорівневі маніпуляції регістрами GPIO без жодних накладних витрат на виклики віртуальних функцій чи покажчиків:

```cpp
struct Stm32GpioAdapter {
    static void scl_drive_low() noexcept { GPIOB->BSRR = GPIO_BSRR_BR6; }
    static void scl_release()   noexcept { GPIOB->BSRR = GPIO_BSRR_BS6; }
    static bool scl_read()      noexcept { return (GPIOB->IDR & GPIO_IDR_ID6) != 0; }
    static void sda_drive_low() noexcept { GPIOB->BSRR = GPIO_BSRR_BR7; }
    static void sda_release()   noexcept { GPIOB->BSRR = GPIO_BSRR_BS7; }
    static bool sda_read()      noexcept { return (GPIOB->IDR & GPIO_IDR_ID7) != 0; }
    static void delay_us(uint32_t us) noexcept { DWT_Delay_us(us); }
};
```

Такий підхід гарантує максимальну швидкодію на мікроконтролерах із обмеженими обчислювальними ресурсами, зберігаючи чисту архітектуру та повну портативність коду між різними сімействами чипів. Використання апаратного лічильника циклів ядра DWT (Data Watchpoint and Trace) в ARM Cortex-M забезпечує наносекундну точність формування часових інтервалів `t_LOW` та `t_HIGH` без використання апаратних таймерів загального призначення.
