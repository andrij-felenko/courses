# ⚙️ Покроковий протокол оживлення та код тестового опитування

Діагностичний протокол першого ввімкнення та автономна тестова прошивка верифікації апаратних вузлів дозволяють локалізувати приховані дефекти монтажу на свіжозмонтованій платі за детермінованим переліком перевірок без ризику термічного або електричного пошкодження напівпровідникових компонентів.

---

## 1. Апаратний протокол первинного контролю (Bring-up Protocol)

Перед першою подачею електричного живлення та підключенням апаратного відлагоджувача заповнюють протокол апаратної верифікації. Кожен крок спирається на пряме вимірювання фізичної величини (опір, падіння напруги, форма сигналу) відповідним лабораторним інструментом.

| Етап | Вузол / Точка контролю | Інструмент | Очікуване значення норми | Фізичний механізм дефекту та дія при відхиленні |
|---|---|---|---|---|
| **0.1** | Візуальний огляд QFP/QFN | Мікроскоп 20x–40x | Відсутність спайок припою, збіг ключа Pin 1, плоске прилягання | Надлишок пасти утворює мости між виводами; видалити спайки мідним обплетенням із флюсом |
| **0.2** | Полярність конденсаторів | Оптичний контроль | Смуга танталу на `+`, смуга алюмінію на `−` | Зворотне ввімкнення танталу викликає лавинний пробій діелектрика; негайно перепаяти |
| **0.3** | Опір рейок `3.3V`, `5V` до GND | Мультиметр (Омметр) | `> 500 Ом` (плавне зростання заряду MLCC до сотен кОм) | Опір `< 2 Ом` означає тверде КЗ: почергово демонтувати захисні супресори, вихідні LDO та кераміку |
| **0.4** | Опір шини ядра `VDD_CORE` | Мультиметр (Омметр) | `> 100 Ом` (MCU) або `15–50 Ом` (FPGA/SoC) | Для MCU опір `< 5 Ом` свідчить про внутрішнє руйнування транзисторів ядра; замінити мікроконтролер |
| **0.5** | Діодне падіння сигнальних пінів | Мультиметр (Diode test) | `0.35–0.65 В` відносно GND (червоний щуп на GND) | Падіння `0.00 В` — пробитий внутрішній ESD-діод буфера GPIO; `OL` — механічний обрив або непропай виводу |
| **1.1** | Вхідна напруга БЖ | Лабораторний БЖ | `V_in = 5.0 В`, ліміт струму `I_limit = 50–100 мА` | Якщо БЖ перейшов у режим CC (`V < 1 В`) — на платі діє приховане КЗ; знеструмити, знайти нагрів |
| **1.2** | Вихід лінійного регулятора | Осцилограф (1:1 AC/DC) | `3.30 В ± 2%`, високочастотні пульсації `< 10 мВ` | Синусоїдальний дзвін `> 200 мВ` вказує на самозбудження LDO через невідповідний ESR вихідного MLCC |
| **1.3** | Тепловий контроль плати | Тепловізор / Ізопропанол | Рівномірне поле температури `< 35 °C` | Миттєве випаровування спирту (1–2 с) на корпусі чіпа викриває точку локального витоку струму |
| **2.1** | Стан лінії ресету `NRST` | Осцилограф / Вольтметр | `V_NRST > 0.85 · VDD` (`2.8–3.3 В`) | Напруга `0 В` — замкнена тактова кнопка, пробитий конденсатор `C_rst`, або спрацював захист Brown-out |
| **2.2** | Напруга регулятора ядра `VCAP` | Вольтметр | `1.20–1.25 В` (для STM32F4/F7/H7) | Напруга `0 В` — непропай зовнішнього конденсатора VCAP або блокування внутрішнього LDO ядра |
| **2.3** | Конфігураційні виводи `BOOT0` | Вольтметр | `0.0 В` (притягнутий через `10 кОм` до GND) | Високий рівень `3.3 В` змушує чіп виконувати заводський ROM-bootloader замість коду у Flash-пам'яті |
| **2.4** | Тактування `OSC_OUT` | Осцилограф (щуп 10x) | Стійка синусоїда номінальної частоти, `V_pp > 1.2 В` | Зрив коливань при дотику щупом 1x — норма через внесену ємність 100 пФ; вимірювати дільником 10x |
| **2.5** | Лінії інтерфейсу `SWD` | Логічний аналізатор / Осцилограф | `SWCLK` — меандр, `SWDIO` — цифрові пакети з ACK | Відсутність відповіді — відсутність спільної землі GND, блокування CoreSight, зависла лінія ресету |

---

## 2. Структура та завдання діагностичної прошивки

Після встановлення першого контакту відлагоджувача з мікроконтролером у Flash-пам'ять завантажують спеціалізовану діагностичну прошивку (*Bring-up Test Runner*). Її головна мета — протестувати кожен базовий блок кристала ізольовано, не залучаючи складних операційних систем реального часу (RTOS) чи важких стеків протоколів, які можуть зависнути на етапі ініціалізації.

Програма виконує три послідовні діагностичні фази:

1. **Верифікація тактових доменів та джерел синхронізації:**
   Прошивка перевіряє стан прапорців готовності внутрішнього високочастотного генератора (HSI), ініціалізує ланцюг запуску зовнішнього кварцового резонатора (HSE) із програмним таймаутом і фіксує стабільність фазового автопідстроювання частоти (PLL). Якщо кварцовий резонатор не збуджується через неправильно підібрану ємність навантажувальних конденсаторів C1/C2, функція повертає код таймауту, не блокуючи виконання решти тестів.

2. **Апаратний генератор контрольних сигналів (Testpoints Exerciser):**
   На виділені діагностичні контактні майданчики (Test Points) плати виводяться тестові імпульси меандру фіксованої частоти. Це дозволяє осцилографом або логічним аналізатором за секунду перевірити цілісність доріжок портів введення-виведення (GPIO), переконатися у відсутності замикань на сусідні земляні полігони та перевірити роботу вихідних двотактних буферів (Push-Pull).

3. **Сканування внутрішньосистемних шин (I2C Bus Scanner):**
   Модуль надсилає запити початку транзакції (START bit) та опитує адресний простір від `0x08` до `0x77`. Якщо бортовий датчик (термометр, акселерометр, EEPROM) розпаяний правильно, отримує живлення і підтягнутий резисторами Pull-Up, він відповідає бітом підтвердження ACK (лінія SDA притискається до землі на 9-му такті). Якщо лінія обірвана або чіп знеструмлений, генерується стан NACK.

Нижче наведено повну реалізацію діагностичного модуля: на чистому C для прямої роботи з регістрами мікроконтролера та ідіоматичному C++20 з використанням просторів імен, строгої типізації `enum class`, структур безпечної адресації та контейнерів `std::span` і `std::expected`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define RCC_BASE        0x40023800U
#define RCC_CR          (*(volatile uint32_t *)(RCC_BASE + 0x00U))
#define RCC_CFGR        (*(volatile uint32_t *)(RCC_BASE + 0x08U))
#define RCC_AHB1ENR     (*(volatile uint32_t *)(RCC_BASE + 0x30U))
#define RCC_APB1ENR     (*(volatile uint32_t *)(RCC_BASE + 0x40U))

#define GPIOA_BASE      0x40020000U
#define GPIOA_MODER     (*(volatile uint32_t *)(GPIOA_BASE + 0x00U))
#define GPIOA_ODR       (*(volatile uint32_t *)(GPIOA_BASE + 0x14U))
#define GPIOA_BSRR      (*(volatile uint32_t *)(GPIOA_BASE + 0x18U))

#define I2C1_BASE       0x40005400U
#define I2C1_CR1        (*(volatile uint32_t *)(I2C1_BASE + 0x00U))
#define I2C1_CR2        (*(volatile uint32_t *)(I2C1_BASE + 0x04U))
#define I2C1_SR1        (*(volatile uint32_t *)(I2C1_BASE + 0x14U))
#define I2C1_SR2        (*(volatile uint32_t *)(I2C1_BASE + 0x18U))
#define I2C1_DR         (*(volatile uint32_t *)(I2C1_BASE + 0x10U))

#define RCC_CR_HSIRDY   (1U << 1)
#define RCC_CR_HSEON    (1U << 16)
#define RCC_CR_HSERDY   (1U << 17)
#define RCC_CR_PLLON    (1U << 24)
#define RCC_CR_PLLRDY   (1U << 25)

#define I2C_SR1_SB      (1U << 0)
#define I2C_SR1_ADDR    (1U << 1)
#define I2C_SR1_AF      (1U << 10)
#define I2C_CR1_START   (1U << 8)
#define I2C_CR1_STOP    (1U << 9)
#define I2C_CR1_PE      (1U << 0)

typedef enum {
    BRINGUP_OK = 0,
    BRINGUP_ERR_HSE_TIMEOUT,
    BRINGUP_ERR_PLL_TIMEOUT,
    BRINGUP_ERR_I2C_TIMEOUT,
    BRINGUP_ERR_I2C_NACK
} bringup_status_t;

typedef struct {
    bool hsi_ready;
    bool hse_ready;
    bool pll_ready;
    uint8_t i2c_devices_found;
} bringup_report_t;

static void delay_cycles(volatile uint32_t cycles) {
    while (cycles > 0) {
        cycles--;
    }
}

bringup_status_t bringup_clock_check(bringup_report_t *report) {
    report->hsi_ready = (RCC_CR & RCC_CR_HSIRDY) != 0;
    
    RCC_CR |= RCC_CR_HSEON;
    uint32_t timeout = 50000;
    while (!(RCC_CR & RCC_CR_HSERDY) && timeout > 0) {
        timeout--;
    }
    report->hse_ready = (timeout > 0);
    if (!report->hse_ready) {
        return BRINGUP_ERR_HSE_TIMEOUT;
    }

    report->pll_ready = (RCC_CR & RCC_CR_PLLRDY) != 0;
    return BRINGUP_OK;
}

void bringup_gpio_toggle_testpoints(uint32_t iterations) {
    RCC_AHB1ENR |= (1U << 0);
    
    GPIOA_MODER &= ~((3U << (5 * 2)) | (3U << (6 * 2)) | (3U << (7 * 2)));
    GPIOA_MODER |=  ((1U << (5 * 2)) | (1U << (6 * 2)) | (1U << (7 * 2)));

    for (uint32_t i = 0; i < iterations; ++i) {
        GPIOA_BSRR = (1U << 5) | (1U << 6) | (1U << 7);
        delay_cycles(1000);
        
        GPIOA_BSRR = (1U << (5 + 16)) | (1U << (6 + 16)) | (1U << (7 + 16));
        delay_cycles(1000);
    }
}

bringup_status_t bringup_i2c_probe_address(uint8_t addr_7bit) {
    I2C1_CR1 |= I2C_CR1_START;
    uint32_t timeout = 20000;
    while (!(I2C1_SR1 & I2C_SR1_SB) && timeout > 0) {
        timeout--;
    }
    if (timeout == 0) {
        I2C1_CR1 |= I2C_CR1_STOP;
        return BRINGUP_ERR_I2C_TIMEOUT;
    }

    I2C1_DR = (uint32_t)(addr_7bit << 1);
    timeout = 20000;
    while (!(I2C1_SR1 & (I2C_SR1_ADDR | I2C_SR1_AF)) && timeout > 0) {
        timeout--;
    }
    
    if (I2C1_SR1 & I2C_SR1_AF) {
        I2C1_SR1 &= ~I2C_SR1_AF;
        I2C1_CR1 |= I2C_CR1_STOP;
        return BRINGUP_ERR_I2C_NACK;
    }

    (void)I2C1_SR1;
    (void)I2C1_SR2;
    I2C1_CR1 |= I2C_CR1_STOP;
    return BRINGUP_OK;
}

uint8_t bringup_scan_i2c_bus(void) {
    uint8_t found = 0;
    for (uint8_t addr = 0x08; addr < 0x78; ++addr) {
        if (bringup_i2c_probe_address(addr) == BRINGUP_OK) {
            found++;
        }
        delay_cycles(500);
    }
    return found;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <expected>

namespace bringup {

struct Registers {
    static constexpr std::uintptr_t rcc_base   = 0x40023800U;
    static constexpr std::uintptr_t gpioa_base = 0x40020000U;
    static constexpr std::uintptr_t i2c1_base  = 0x40005400U;

    static volatile std::uint32_t& rcc_cr()   { return *reinterpret_cast<volatile std::uint32_t*>(rcc_base + 0x00U); }
    static volatile std::uint32_t& rcc_ahb1() { return *reinterpret_cast<volatile std::uint32_t*>(rcc_base + 0x30U); }
    static volatile std::uint32_t& gpio_moder(){ return *reinterpret_cast<volatile std::uint32_t*>(gpioa_base + 0x00U); }
    static volatile std::uint32_t& gpio_bsrr() { return *reinterpret_cast<volatile std::uint32_t*>(gpioa_base + 0x18U); }
    static volatile std::uint32_t& i2c_cr1()  { return *reinterpret_cast<volatile std::uint32_t*>(i2c1_base + 0x00U); }
    static volatile std::uint32_t& i2c_sr1()  { return *reinterpret_cast<volatile std::uint32_t*>(i2c1_base + 0x14U); }
    static volatile std::uint32_t& i2c_sr2()  { return *reinterpret_cast<volatile std::uint32_t*>(i2c1_base + 0x18U); }
    static volatile std::uint32_t& i2c_dr()   { return *reinterpret_cast<volatile std::uint32_t*>(i2c1_base + 0x10U); }
};

enum class Error : std::uint8_t {
    hse_timeout,
    pll_timeout,
    i2c_timeout,
    i2c_nack
};

struct ClockStatus {
    bool hsi_ready{false};
    bool hse_ready{false};
    bool pll_ready{false};
};

class BringupRunner {
public:
    static void delay(std::uint32_t count) noexcept {
        volatile std::uint32_t c = count;
        while (c > 0) {
            --c;
        }
    }

    static std::expected<ClockStatus, Error> verify_clocks() noexcept {
        ClockStatus status;
        constexpr std::uint32_t hsirdy_mask = (1U << 1);
        constexpr std::uint32_t hseon_mask  = (1U << 16);
        constexpr std::uint32_t hserdy_mask = (1U << 17);
        constexpr std::uint32_t pllrdy_mask = (1U << 25);

        status.hsi_ready = (Registers::rcc_cr() & hsirdy_mask) != 0;

        Registers::rcc_cr() |= hseon_mask;
        std::uint32_t timeout = 50000;
        while (!(Registers::rcc_cr() & hserdy_mask) && timeout > 0) {
            --timeout;
        }
        
        status.hse_ready = (timeout > 0);
        if (!status.hse_ready) {
            return std::unexpected(Error::hse_timeout);
        }

        status.pll_ready = (Registers::rcc_cr() & pllrdy_mask) != 0;
        return status;
    }

    static void exerciser_testpoints(std::span<const std::uint8_t> pins, std::uint32_t cycles) noexcept {
        Registers::rcc_ahb1() |= (1U << 0);

        for (auto pin : pins) {
            Registers::gpio_moder() &= ~(3U << (pin * 2));
            Registers::gpio_moder() |=  (1U << (pin * 2));
        }

        for (std::uint32_t i = 0; i < cycles; ++i) {
            std::uint32_t set_mask = 0;
            std::uint32_t reset_mask = 0;
            for (auto pin : pins) {
                set_mask |= (1U << pin);
                reset_mask |= (1U << (pin + 16));
            }
            Registers::gpio_bsrr() = set_mask;
            delay(1000);
            Registers::gpio_bsrr() = reset_mask;
            delay(1000);
        }
    }

    static std::expected<void, Error> probe_i2c_device(std::uint8_t address_7bit) noexcept {
        constexpr std::uint32_t start_bit = (1U << 8);
        constexpr std::uint32_t stop_bit  = (1U << 9);
        constexpr std::uint32_t sb_flag   = (1U << 0);
        constexpr std::uint32_t addr_flag = (1U << 1);
        constexpr std::uint32_t af_flag   = (1U << 10);

        Registers::i2c_cr1() |= start_bit;
        std::uint32_t timeout = 20000;
        while (!(Registers::i2c_sr1() & sb_flag) && timeout > 0) {
            --timeout;
        }
        if (timeout == 0) {
            Registers::i2c_cr1() |= stop_bit;
            return std::unexpected(Error::i2c_timeout);
        }

        Registers::i2c_dr() = static_cast<std::uint32_t>(address_7bit << 1);
        timeout = 20000;
        while (!(Registers::i2c_sr1() & (addr_flag | af_flag)) && timeout > 0) {
            --timeout;
        }

        if (Registers::i2c_sr1() & af_flag) {
            Registers::i2c_sr1() &= ~af_flag;
            Registers::i2c_cr1() |= stop_bit;
            return std::unexpected(Error::i2c_nack);
        }

        static_cast<void>(Registers::i2c_sr1());
        static_cast<void>(Registers::i2c_sr2());
        Registers::i2c_cr1() |= stop_bit;
        return {};
    }
};

} // namespace bringup
```
:::

---

## 3. Діагностичний розбір та усунення апаратних відмов

1. **`BRINGUP_ERR_HSE_TIMEOUT` / `Error::hse_timeout`:**
   - **Симптом:** Мікроконтролер успішно працює на внутрішньому HSI-генераторі, але функція ініціалізації HSE випадає за таймаутом.
   - **Причина:** Завищена паразитна ємність трасування кварцового резонатора або помилковий номінал навантажувальних конденсаторів C1/C2 (наприклад, встановлено 47 пФ замість 12 пФ). При такій ємності еквівалентний від'ємний опір інвертора не перекриває динамічний опір втрат кристала (ESR).
   - **Рішення:** Замінити навантажувальні конденсатори на менший номінал (10–12 пФ) або змити залишки флюсу між ніжками резонатора, які створюють струмовий витік.

2. **Відсутність перемикання на виводах контрольних точок (Testpoints Exerciser):**
   - **Симптом:** Осцилограф показує постійний рівень 0 В або 3.3 В на тестових пінах.
   - **Причина:** Порт введення-виведення не отримує тактування через відсутність запису відповідного біта в регістрі `RCC_AHB1ENR`, або вивід закорочений на сусідню земляну площину під маскою друкованої плати.
   - **Рішення:** Перевірити напругу на піні мультиметром у режимі опору; при вимкненому живленні переконатися у відсутності КЗ доріжки на землю або живлення.

3. **`BRINGUP_ERR_I2C_NACK` / `Error::i2c_nack` на всіх адресах шини:**
   - **Симптом:** Сканер не знаходить жодного веденого пристрою на шині I2C.
   - **Причина:** Відсутність зовнішніх підтягувальних резисторів Pull-Up номіналом 2.2–4.7 кОм на лініях `SCL` та `SDA`. Внутрішні підтяжки мікроконтролера (зазвичай 40 кОм) занадто слабкі для формування крутих фронтів сигналу на ємності доріжок.
   - **Рішення:** Перевірити осцилографом наявність високого рівня 3.3 В на обох лініях у стані спокою шини (Idle). Якщо рівень дорівнює 0 В — допаяти підтягувальні резистори.

4. **Зависання шини I2C (`BRINGUP_ERR_I2C_TIMEOUT`):**
   - **Симптом:** Прошивка зависає на першій спробі виставити стан START.
   - **Причина:** Ведений пристрій завис у стані передачі байта через збій скидання і тримає лінію `SDA` притиснутою до нуля.
   - **Рішення:** Виконати процедуру примусового скидання шини (I2C Bus Clear): перевести вивід `SCL` у режим GPIO Push-Pull і згенерувати 9 послідовних тактових імпульсів, дозволяючи веденому чіпу звільнити лінію SDA, після чого згенерувати умову STOP.

---

## 4. Відновлення завислої шини I2C (Bus Clear Procedure)

Поширена апаратна пастка під час налагодження нової плати: мікроконтролер скидається посеред транзакції зчитування, коли ведена мікросхема (наприклад, датчик температури чи EEPROM) саме передавала нульовий біт даних і притискала лінію `SDA` до землі. 

Оскільки ведений пристрій не має власної лінії апаратного скидання і тактується виключно від лінії `SCL`, після перезавантаження мікроконтролера ведений чіп залишається у стані очікування тактових імпульсів, безперервно утримуючи `SDA = 0`. Апаратний модуль I2C мікроконтролера бачить заблоковану лінію даних, вважає шину зайнятою (*Bus Busy*) і відмовляється генерувати стан `START`.

Для виходу з цього глухого кута перед ініціалізацією модуля I2C виконують програмне розблокування:

1. Виводи `SCL` та `SDA` конфігурують як звичайні цифрові виходи GPIO у режимі відкритого стоку (Open-Drain).
2. Лінію `SDA` залишають у високому стані (відпускають підтяжці Pull-Up).
3. На лінії `SCL` програмно генерують **9 послідовних тактових імпульсів** із частотою 50–100 кГц. Отримуючи імпульси тактування, ведений чіп досилає решту бітів поточного байта даних і досягає біта NACK/ACK, після чого відпускає лінію `SDA` у високий рівень.
4. Контролер перевіряє стан лінії `SDA`: якщо вона піднялася до 3.3 В, генерується коректна умова `STOP` (перехід `SDA` з низького рівня у високий при високому рівні `SCL`).
5. Виводи повертаються під контроль периферійного модуля I2C.

---

## 5. Верифікація внутрішніх опорних джерел через АЦП

Останній крок первинного апаратного аудиту мікроконтролера — перевірка точності внутрішнього джерела опорної напруги (Bandgap Reference, `VREFINT`) та шини вимірювання напруги живлення ядра.

Більшість чіпів ARM Cortex-M мають внутрішній канал аналого-цифрового перетворювача (АЦП), підключений до стабільного джерела `VREFINT` із типовим значенням `1.20 В ± 1%`, а також заводську калібрувальну константу, збережену в захищеній пам'яті (System ROM) при напрузі живлення `3.30 В`.

```
VDDA_реальна = 3.30 В · ADC_CAL / ADC_DATA  [розрахунок справжньої напруги аналогового живлення]
```

Зчитування значення цього каналу дозволяє безпосередньо з коду прошивки виміряти реальну напругу на виводі `VDDA`. Якщо обчислена напруга живлення суттєво відрізняється від номінальних 3.3 В (наприклад, становить 2.9 В або 3.7 В), це однозначно вказує на дефект лінійного стабілізатора, перевантаження шини або надмірний падіння напруги на феритовій бусині (Ferrite Bead) фільтра аналогового живлення.
