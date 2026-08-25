# ⚙️ Програмна реалізація точного таймінгу I²C (Bit-Banging)

Програмна емуляція протоколу I²C (*Bit-Banging*, від англ. *bit* — біт та *to bang* — бити, смикати) є класичним інженерним прийомом прямого програмного керування лініями введення-виведення загального призначення (GPIO). До неї звертаються у ситуаціях, коли апаратні модулі I²C мікроконтролера вже вичерпані іншими периферійними завданнями, виводи апаратного контролера заблоковані або незручно розведені на друкованій платі, а також коли необхідно реалізувати нестандартні процедури діагностики та примусового виведення шини зі стану блокування (*Bus Clear / Clock-Toggle Recovery*).

Проте створення надійного програмного ведучого вимагає суворого дотримання часових інтервалів та електричних умов специфікації NXP UM10204. Найпоширеніша помилка розробників-початківців — спроба прямого перемикання виводів мікроконтролера між двотактними режимами Push-Pull логічного нуля (0 В) та Push-Pull логічної одиниці (3.3 В) із приблизними затримками через порожні цикли `for`. Такий підхід грубо порушує специфікацію шини, повністю ламає механізм розтягування такту веденими пристроями і створює пряму загрозу виникнення короткого замикання джерела живлення на землю, коли ведений пристрій утримує лінію SDA на рівні нуля для видачі квитанції ACK у момент, коли ведучий примусово подає на вивід 3.3 В.

У цьому проєкті розглянуто архітектуру, покроковий кінцевий автомат, методику осцилографічної верифікації, особливості роботи в операційних системах реального часу та робочу реалізацію повністю сумісного зі стандартом NXP UM10204 програмного ведучого I²C для режимів Standard-mode (100 кГц) та Fast-mode (400 кГц) мовами C та C++.

---

### Апаратне керування виводами GPIO у режимі відкритого стоку

Фундаментальне правило фізичного рівня I²C стверджує: жоден пристрій на шині ні за яких обставин не повинен активно підключати сигнальні лінії SDA чи SCL до шини живлення `V_DD` через верхній P-канальний польовий транзистор. Високий логічний рівень напруги формується виключно зовнішнім пасивним резистором підтяжки `R_p`.

Для програмної реалізації цього правила виводи GPIO мікроконтролера повинні керуватися за однією з двох апаратних схем:

#### Схема 1. Апаратний Open-Drain режим GPIO (рекомендований)
Сучасні мікроконтролери (наприклад, лінійки ARM Cortex-M — STM32, NXP LPC, Microchip SAM, а також ESP32) підтримують конфігурацію вихідного каскаду GPIO як відкритий стік (*Open-Drain Output*).
- Запис логічного `0` у вихідний регістр даних (`ODR` або `BSRR`) відкриває внутрішній N-канальний MOSFET, притягуючи вивід до землі `GND` (напруга на лінії становить `0.1 ... 0.2 В`).
- Запис логічної `1` у вихідний регістр закриває N-MOSFET, переводячи вивід у стан високого імпедансу (Hi-Z). Резистор підтяжки `R_p` заряджає ємність шини і піднімає напругу до `V_DD`.
- Зчитування фактичного стану лінії здійснюється через вхідний регістр даних (`IDR`).

#### Схема 2. Динамічна зміна напрямку виводу (Input / Output)
Якщо мікроконтролер не має апаратного режиму відкритого стоку (наприклад, класичні 8-бітні чипи AVR ATmega), застосовується динамічна зміна напрямку роботи виводу:
- Для формування **логічного нуля (LOW)** вивід налаштовується як **Output**, а у вихідний регістр записується `0` (активне притягування до нуля).
- Для формування **логічної одиниці (HIGH)** вивід перемикається в режим **Input (Floating / Hi-Z)** без внутрішньої підтяжки. Вихідний буфер вимикається, і зовнішній резистор підтягує лінію до `V_DD`.

---

### Формування каліброваних часових затримок у мікроконтролерах

Для точного формування субмікросекундних часових інтервалів (наприклад, `t_SU;DAT = 100 нс` або `t_HIGH = 600 нс` для режиму 400 кГц) використання стандартних затримок операційної системи (на кшталт `vTaskDelay` або `usleep`) є неприпустимим, оскільки вони мають гранулярність системного кванту часу (зазвичай 1 мс) і викликають перемикання контексту задач.

У вбудованих системах на базі ядер ARM Cortex-M3/M4/M7/M33 для цієї мети використовується апаратний лічильник циклів ядра модуля трасування **DWT** (*Data Watchpoint and Trace*, регістр `DWT->CYCCNT`). Лічильник інкрементується на кожному такті системної частоти процесора (наприклад, при частоті ядра 168 МГц один такт лічильника відповідає `5.95 нс`).

Розрахунок кількості тактів для затримки `t` наносекунд виконується за формулою:

```
N_cycles = (t_ns · F_CPU_Hz) / 1000000000
```

---

### Покроковий алгоритм кінцевого автомата програмного ведучого

#### 1. Генерація умови START (S)
1. Ведучий переводить обидві лінії SDA та SCL у стан Hi-Z (високий рівень).
2. Виконується перевірка вільного стану шини: зчитуються регістри GPIO. Якщо хоча б одна з ліній утримується на нулі, шина зайнята іншим пристроєм або заблокована.
3. Витримується захисний інтервал `t_BUF` або час встановлення старту `t_SU;STA`.
4. Лінія SDA притягується до нуля (`SDA = LOW`), тоді як SCL залишається високою.
5. Витримується обов'язковий час утримання умови старту `t_HD;STA` (щонайменше 0.6 мкс для 400 кГц).
6. Лінія SCL притягується до нуля (`SCL = LOW`), що сигналізує про початок першого такту передачі даних.

#### 2. Передача інформаційного біта
Для кожного з 8 бітів байта (починаючи зі старшого значущого біта MSB):
1. Поки SCL утримується в нулі (`t_LOW`), ведучий виставляє значення чергового біта на лінію SDA (переводить SDA в нуль або відпускає в Hi-Z).
2. Ведучий витримує нормативний час встановлення даних `t_SU;DAT` (щонайменше 100 нс), щоб перехідний процес на лінії SDA повністю завершився.
3. Ведучий відпускає лінію SCL у стан Hi-Z.
4. **Обробка розтягування такту (Clock Stretching):** Ведучий опитує вхідний стан лінії SCL. Якщо ведений пристрій утримує SCL на рівні нуля (виконує внутрішнє обчислення), ведучий залишається в циклі очікування, контролюючи загальний таймаут операції.
5. Щойно напруга на лінії SCL перевищує `0.7 · V_DD`, ведучий запускає таймер тривалості високого рівня `t_HIGH` (0.6 мкс).
6. Після завершення `t_HIGH` ведучий примусово притягує SCL до нуля (`SCL = LOW`).
7. Витримується час утримання даних `t_HD;DAT` (300 нс), після чого цикл повторюється для наступного біта.

#### 3. Фаза 9-го такту (прийом квитанції ACK/NACK)
1. Після спаду 8-го такту SCL ведучий відпускає лінію SDA у стан Hi-Z, передаючи керування веденому приймачу.
2. Ведений виставляє свій біт підтвердження (`SDA = LOW` для ACK, або залишає SDA у Hi-Z для NACK).
3. Ведучий відпускає SCL у Hi-Z і чекає завершення можливого розтягування такту.
4. Під час фази високого рівня `t_HIGH` ведучий зчитує вхідний стан лінії SDA:
   - Якщо зафіксовано нуль (`SDA == 0`) — ведений підтвердив прийом байта (ACK);
   - Якщо зафіксовано одиницю (`SDA == 1`) — отримано відмову (NACK).
5. Ведучий опускає SCL до нуля, завершуючи передачу байта.

#### 4. Генерація умови STOP (P)
1. Ведучий опускає лінію SDA до нуля при низькому рівні SCL.
2. Ведучий відпускає SCL у стан Hi-Z і чекає підйому лінії до `0.7 · V_DD`.
3. Витримується нормативний час встановлення стопу `t_SU;STO` (0.6 мкс).
4. Ведучий відпускає лінію SDA у стан Hi-Z (наростаючий фронт на SDA при високому SCL).
5. Витримується вільний час шини `t_BUF` (1.3 мкс для 400 кГц) перед дозволом наступної транзакції.

---

### Робоча реалізація: C та C++

Нижче наведено повний вихідний код модуля програмного I²C із суворим дотриманням часових параметрів UM10204.

:::tabs
```c
/* Програмний ведучий I2C (Bit-Banging) з точним дотриманням UM10204 (C11) */
#include <stdint.h>
#include <stdbool.h>

/* Низькорівнева апаратна платформа: доступ до GPIO та лічильника тактів */
extern void hw_gpio_sda_low(void);
extern void hw_gpio_sda_hiz(void);
extern uint8_t hw_gpio_sda_read(void);

extern void hw_gpio_scl_low(void);
extern void hw_gpio_scl_hiz(void);
extern uint8_t hw_gpio_scl_read(void);

extern void hw_delay_ns(uint32_t ns);
extern uint32_t hw_get_dwt_cycles(void);

typedef enum {
    I2C_OK           = 0,
    I2C_ERR_TIMEOUT  = -1,
    I2C_ERR_NACK     = -2,
    I2C_ERR_BUS_BUSY = -3
} i2c_status_t;

typedef struct {
    uint32_t t_low_ns;
    uint32_t t_high_ns;
    uint32_t t_su_dat_ns;
    uint32_t t_hd_dat_ns;
    uint32_t t_hd_sta_ns;
    uint32_t t_su_sta_ns;
    uint32_t t_su_sto_ns;
    uint32_t t_buf_ns;
    uint32_t timeout_cycles;
} i2c_bb_timing_t;

/* Нормативні параметри для Fast-mode (400 кГц) */
static const i2c_bb_timing_t TIMING_FAST_400K = {
    .t_low_ns        = 1300,
    .t_high_ns       = 600,
    .t_su_dat_ns     = 100,
    .t_hd_dat_ns     = 300,
    .t_hd_sta_ns     = 600,
    .t_su_sta_ns     = 600,
    .t_su_sto_ns     = 600,
    .t_buf_ns        = 1300,
    .timeout_cycles  = 16800000 /* ~100 мс при тактовій частоті ядра 168 МГц */
};

/* Очікування наростання SCL з апаратним захистом від зависання (Clock Stretching) */
static i2c_status_t wait_scl_high(const i2c_bb_timing_t *t) {
    hw_gpio_scl_hiz();
    const uint32_t start_cycles = hw_get_dwt_cycles();

    while (hw_gpio_scl_read() == 0) {
        if ((hw_get_dwt_cycles() - start_cycles) > t->timeout_cycles) {
            return I2C_ERR_TIMEOUT;
        }
    }
    return I2C_OK;
}

/* Формування умови START: спадний фронт SDA при високому рівні SCL */
i2c_status_t i2c_bb_start(const i2c_bb_timing_t *t) {
    hw_gpio_sda_hiz();
    if (wait_scl_high(t) != I2C_OK) {
        return I2C_ERR_BUS_BUSY;
    }
    hw_delay_ns(t->t_su_sta_ns);

    /* Спадний перепад на лінії даних */
    hw_gpio_sda_low();
    hw_delay_ns(t->t_hd_sta_ns);

    /* Фіксація початку тактування */
    hw_gpio_scl_low();
    hw_delay_ns(t->t_low_ns);
    return I2C_OK;
}

/* Формування умови STOP: наростаючий фронт SDA при високому рівні SCL */
i2c_status_t i2c_bb_stop(const i2c_bb_timing_t *t) {
    hw_gpio_scl_low();
    hw_gpio_sda_low();
    hw_delay_ns(t->t_low_ns);

    if (wait_scl_high(t) != I2C_OK) {
        return I2C_ERR_TIMEOUT;
    }
    hw_delay_ns(t->t_su_sto_ns);

    /* Наростаючий перепад на лінії даних */
    hw_gpio_sda_hiz();
    hw_delay_ns(t->t_buf_ns);
    return I2C_OK;
}

/* Передача 8 бітів даних та зчитування біта підтвердження ACK/NACK */
i2c_status_t i2c_bb_write_byte(const i2c_bb_timing_t *t, uint8_t byte) {
    for (int8_t i = 7; i >= 0; i--) {
        if ((byte >> i) & 1) {
            hw_gpio_sda_hiz();
        } else {
            hw_gpio_sda_low();
        }
        hw_delay_ns(t->t_su_dat_ns);

        if (wait_scl_high(t) != I2C_OK) {
            return I2C_ERR_TIMEOUT;
        }
        hw_delay_ns(t->t_high_ns);

        hw_gpio_scl_low();
        hw_delay_ns(t->t_hd_dat_ns);
    }

    /* 9-й такт: перехід лінії SDA під контроль приймача */
    hw_gpio_sda_hiz();
    hw_delay_ns(t->t_su_dat_ns);

    if (wait_scl_high(t) != I2C_OK) {
        return I2C_ERR_TIMEOUT;
    }
    hw_delay_ns(t->t_high_ns);

    /* Зчитування квитанції: 0 = ACK, 1 = NACK */
    const uint8_t nack = hw_gpio_sda_read();

    hw_gpio_scl_low();
    hw_delay_ns(t->t_low_ns);

    return (nack == 0) ? I2C_OK : I2C_ERR_NACK;
}

/* Прийом 8 бітів даних із генерацією квитанції ACK або NACK ведучим */
i2c_status_t i2c_bb_read_byte(const i2c_bb_timing_t *t, uint8_t *out_byte, bool send_ack) {
    uint8_t byte = 0;
    hw_gpio_sda_hiz();

    for (int8_t i = 7; i >= 0; i--) {
        if (wait_scl_high(t) != I2C_OK) {
            return I2C_ERR_TIMEOUT;
        }
        hw_delay_ns(t->t_high_ns);

        if (hw_gpio_sda_read()) {
            byte |= (uint8_t)(1U << i);
        }

        hw_gpio_scl_low();
        hw_delay_ns(t->t_low_ns);
    }

    /* 9-й такт: видача підтвердження ведучим */
    if (send_ack) {
        hw_gpio_sda_low();  /* ACK = 0 */
    } else {
        hw_gpio_sda_hiz();  /* NACK = 1 */
    }
    hw_delay_ns(t->t_su_dat_ns);

    if (wait_scl_high(t) != I2C_OK) {
        return I2C_ERR_TIMEOUT;
    }
    hw_delay_ns(t->t_high_ns);

    hw_gpio_scl_low();
    hw_gpio_sda_hiz();
    hw_delay_ns(t->t_low_ns);

    *out_byte = byte;
    return I2C_OK;
}
```
```cpp
// Програмний ведучий I2C (Bit-Banging) з точним дотриманням UM10204 (C++20)
#pragma once
#include <cstdint>
#include <chrono>
#include <span>
#include <expected>
#include <concepts>

namespace i2c::bitbang {

using namespace std::chrono_literals;

enum class Error : uint8_t {
    Timeout,
    NackReceived,
    BusBusy,
    ArbitrationLost
};

struct TimingConfig {
    std::chrono::nanoseconds t_low{1300ns};
    std::chrono::nanoseconds t_high{600ns};
    std::chrono::nanoseconds t_su_dat{100ns};
    std::chrono::nanoseconds t_hd_dat{300ns};
    std::chrono::nanoseconds t_hd_sta{600ns};
    std::chrono::nanoseconds t_su_sta{600ns};
    std::chrono::nanoseconds t_su_sto{600ns};
    std::chrono::nanoseconds t_buf{1300ns};
    std::chrono::milliseconds timeout{100ms};
};

template <typename GpioPolicy, typename TimerPolicy>
class SoftwareI2cMaster {
public:
    explicit constexpr SoftwareI2cMaster(TimingConfig timing = TimingConfig{}) noexcept
        : timing_{timing} {}

    [[nodiscard]] std::expected<void, Error> start() noexcept {
        GpioPolicy::sda_hiz();
        if (auto res = wait_scl_high(); !res) return res;
        TimerPolicy::delay_ns(timing_.t_su_sta.count());

        GpioPolicy::sda_low();
        TimerPolicy::delay_ns(timing_.t_hd_sta.count());

        GpioPolicy::scl_low();
        TimerPolicy::delay_ns(timing_.t_low.count());
        return {};
    }

    [[nodiscard]] std::expected<void, Error> stop() noexcept {
        GpioPolicy::scl_low();
        GpioPolicy::sda_low();
        TimerPolicy::delay_ns(timing_.t_low.count());

        if (auto res = wait_scl_high(); !res) return res;
        TimerPolicy::delay_ns(timing_.t_su_sto.count());

        GpioPolicy::sda_hiz();
        TimerPolicy::delay_ns(timing_.t_buf.count());
        return {};
    }

    [[nodiscard]] std::expected<void, Error> write_byte(uint8_t byte) noexcept {
        for (int8_t i = 7; i >= 0; --i) {
            if ((byte >> i) & 1U) {
                GpioPolicy::sda_hiz();
            } else {
                GpioPolicy::sda_low();
            }
            TimerPolicy::delay_ns(timing_.t_su_dat.count());

            if (auto res = wait_scl_high(); !res) return res;
            TimerPolicy::delay_ns(timing_.t_high.count());

            GpioPolicy::scl_low();
            TimerPolicy::delay_ns(timing_.t_hd_dat.count());
        }

        // 9-й такт: перевірка квитанції ACK/NACK
        GpioPolicy::sda_hiz();
        TimerPolicy::delay_ns(timing_.t_su_dat.count());

        if (auto res = wait_scl_high(); !res) return res;
        TimerPolicy::delay_ns(timing_.t_high.count());

        const bool nack = GpioPolicy::sda_read();
        GpioPolicy::scl_low();
        TimerPolicy::delay_ns(timing_.t_low.count());

        if (nack) {
            return std::unexpected(Error::NackReceived);
        }
        return {};
    }

    [[nodiscard]] std::expected<uint8_t, Error> read_byte(bool send_ack) noexcept {
        uint8_t byte = 0;
        GpioPolicy::sda_hiz();

        for (int8_t i = 7; i >= 0; --i) {
            if (auto res = wait_scl_high(); !res) return std::unexpected(res.error());
            TimerPolicy::delay_ns(timing_.t_high.count());

            if (GpioPolicy::sda_read()) {
                byte |= static_cast<uint8_t>(1U << i);
            }

            GpioPolicy::scl_low();
            TimerPolicy::delay_ns(timing_.t_low.count());
        }

        // 9-й такт: стробування квитанції ведучим
        if (send_ack) {
            GpioPolicy::sda_low();
        } else {
            GpioPolicy::sda_hiz();
        }
        TimerPolicy::delay_ns(timing_.t_su_dat.count());

        if (auto res = wait_scl_high(); !res) return std::unexpected(res.error());
        TimerPolicy::delay_ns(timing_.t_high.count());

        GpioPolicy::scl_low();
        GpioPolicy::sda_hiz();
        TimerPolicy::delay_ns(timing_.t_low.count());

        return byte;
    }

    [[nodiscard]] std::expected<void, Error> write_transaction(
        uint8_t device_address, std::span<const uint8_t> buffer) noexcept {
        if (auto res = start(); !res) return res;

        // Передача адреси веденого зі знятим бітом R/W (0 = Write)
        const uint8_t addr_byte = static_cast<uint8_t>(device_address << 1U);
        if (auto res = write_byte(addr_byte); !res) {
            (void)stop();
            return res;
        }

        for (const auto val : buffer) {
            if (auto res = write_byte(val); !res) {
                (void)stop();
                return res;
            }
        }

        return stop();
    }

private:
    [[nodiscard]] std::expected<void, Error> wait_scl_high() noexcept {
        GpioPolicy::scl_hiz();
        const auto start_tick = TimerPolicy::get_ticks();

        while (!GpioPolicy::scl_read()) {
            if (TimerPolicy::ticks_to_ms(TimerPolicy::get_ticks() - start_tick) >= timing_.timeout.count()) {
                return std::unexpected(Error::Timeout);
            }
        }
        return {};
    }

    TimingConfig timing_;
};

} // namespace i2c::bitbang
```
:::

---

### Методика осцилографічної верифікації та калібрування таймінгів

Для підтвердження повної відповідності створеного драйвера специфікації NXP UM10204 виконується апаратне тестування цифровим осцилографом із функцією декодування I²C за наступними кроками:

#### 1. Налаштування схеми синхронізації (Trigger Setup)
- **Тригер за умовою I2C Start:** Синхронізація розгортки на спадному перепаді SDA при високому рівні SCL для аналізу тривалості `t_HD;STA` та часу встановлення `t_SU;STA`.
- **Тригер за тривалістю імпульсу (Pulse Width Trigger):** Налаштовується на лінію SCL для виявлення випадкових аномально коротких імпульсів (`t < t_LOW_min` або `t < t_HIGH_min`), які свідчать про гонки сигналів у коді перемикання GPIO.

#### 2. Вимірювання часових інтервалів курсорами
- Встановити перший курсор на точку перетину напруги SDA рівня `0.7 · V_DD` (для зростання) або `0.3 · V_DD` (для спаду).
- Встановити другий курсор на точку перетину напруги SCL рівня `0.7 · V_DD`.
- Переконатися, що виміряна різниця `Δt` перевищує мінімальний норматив часу встановлення `t_SU;DAT` (100 нс для 400 кГц).

---

### Інтеграція в операційні системи реального часу (RTOS)

Під час використання програмного I²C в операційних системах реального часу (FreeRTOS, Zephyr, RT-Thread) виникає специфічна часова проблема: витісняюча багатозадачність (*Preemptive Multitasking*).

Якщо посеред формування інтервалу `t_SU;DAT` або `t_HIGH` планувальник операційної системи перерве задачу програмного I²C для виконання вищої за пріоритетом задачі на 5–10 мікросекунд:
- Інтервал `t_HIGH` або `t_LOW` штучно подовжиться. Для ведених пристроїв це не є фатальним (I²C є статичною синхронною шиною, здатною працювати на будь-якій зниженій швидкості).
- Проте якщо переривання станеться між спадом SDA та спадом SCL при формуванні START, затримка `t_HD;STA` виросте в десятки разів, що може викликати таймаути в деяких швидких цифрових датчиках.

Для критичних промислових транзакцій застосовують захист критичних секцій:

:::tabs
```c
taskENTER_CRITICAL();
i2c_bb_write_byte(&TIMING_FAST_400K, data_byte);
taskEXIT_CRITICAL();
```
```cpp
{
    const std::lock_guard<CriticalSection> lock{cs};
    (void)i2c_master.write_byte(data_byte);
}
```
:::

---

### Аварійне відновлення заблокованої шини (Clock-Toggle Bus Clear)

Одна з найнебезпечніших ситуацій у роботі шини I²C виникає, коли ведучий пристрій зазнає раптового апаратного перезавантаження (наприклад, через скидання сторожовим таймером Watchdog або просідання напруги живлення Brown-Out Reset) прямо посеред операції читання даних.

Якщо в цей момент ведений пристрій якраз передавав інформаційний біт логічного нуля (`SDA = 0`), він залишається у стані очікування спаду тактового імпульсу SCL, продовжуючи нескінченно притягувати лінію SDA до землі. Після перезавантаження ведучий намагається сформувати умову START, проте бачить нуль на лінії SDA і вважає шину постійно зайнятою (*Bus Locked / Bus Deadlock*).

Специфікація NXP UM10204 регламентує стандартний алгоритм відновлення шини (*Bus Clear Sequence*):

1. Ведучий примусово переводить лінію SDA у стан Hi-Z (не намагається тягнути її силою).
2. Ведучий генерує серію з **9 послідовних тактових імпульсів на лінії SCL** із дотриманням стандартних інтервалів `t_LOW` та `t_HIGH`.
3. Кожен тактовий імпульс змушує ведений пристрій зрушити свій внутрішній апаратний регістр передавача на один біт. Щонайбільше за 9 тактів ведений передасть усі біти поточного байта і дійде до фази очікування квитанції або відпустить лінію SDA.
4. На кожному такті ведучий опитує стан лінії SDA. Щойно SDA повертається у високий рівень (Hi-Z), ведучий негайно генерує стандартну умову **STOP (P)**.
5. Після умови STOP усі апаратні кінцеві автомати ведених вузлів остаточно повертаються у вихідний стан очікування адреси.

Функція аварійного відновлення обов'язково включається в процедуру ініціалізації будь-якого промислового драйвера перед запуском регулярного обміну.
