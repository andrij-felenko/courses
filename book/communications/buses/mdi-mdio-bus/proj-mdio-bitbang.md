# ⚙️ Програмна реалізація драйвера MDC/MDIO (Bit-Banging)

У багатьох вбудованих системах виникає потреба конфігурувати та контролювати трансивер Ethernet PHY або мікросхему багатопортового комутатора без використання виділеного апаратного блоку MII Management. Це типова ситуація для пристроїв, де апаратний MAC-контролер процесора зайнятий основним мережевим інтерфейсом, де використовується зовнішній некерований комутатор з функціями розширеної діагностики (Ethernet Switch IC), або де мікроконтролер загального призначення виконує роль керуючого супервізора системи живлення та моніторингу через довільні ніжки GPIO.

Програмне формування сигналів (*Bit-banging*) на шині MDC/MDIO вимагає суворого дотримання часових діаграм стандартів IEEE 802.3 Clause 22 та Clause 45, коректного перемикання напрямку лінії MDIO у фазі передачі керування (Turnaround), надійного розпізнавання підключених мікросхем та врахування постійної часу розряду й заряду паразитної ємності шини.

---

## 1. Фізичний рівень та часові обмеження шини

Шина MDC/MDIO складається з двох ліній: односпрямованого тактового сигналу **MDC** (*Management Data Clock*), який завжди генерує керівний контролер (ведучий), та двонаправленої лінії даних **MDIO** (*Management Data Input/Output*), стан якої утримується зовнішнім резистором підтяжки до шини живлення.

### Часові параметри стандарту IEEE 802.3 Clause 22

1. **Тактова частота та шпаруватість MDC:**
   Стандарт встановлює максимальну частоту тактового сигналу `f_MDC = 2.5 МГц`, що відповідає мінімальному періоду:
   ```
   T_MDC = 1 / f_MDC = 1 / 2.5·10⁶ = 400 нс
   ```
   Тривалість високого стану (`T_HIGH`) та низького стану (`T_LOW`) тактового імпульсу повинна становити не менше ніж 160 нс кожна. На відміну від шин SPI чи I2S, тактовий сигнал MDC не зобов'язаний бути безперервним: керівний процесор може повністю зупиняти тактування між транзакціями у стані низького рівня («0») або високого рівня («1»). Це дозволяє реалізувати драйвер за допомогою простих програмних затримок без прив'язки до апаратних таймерів.

2. **Правило зміни та вибірки даних на лінії MDIO:**
   - **Виставляння даних:** сторона, що передає біт (контролер або трансивер PHY), змінює логічний рівень на лінії MDIO **суворо за спадним фронтом MDC** (перехід з 1 в 0).
   - **Вибірка даних:** сторона, що приймає біт, фіксує значення лінії MDIO **суворо за наростаючим фронтом MDC** (перехід з 0 в 1).
   - **Час встановлення та утримання:** стан лінії MDIO повинен бути стабільним як мінімум за `t_setup ≥ 10 нс` до наростаючого фронту MDC і утримуватися незмінним щонайменше `t_hold ≥ 10 нс` після нього.

3. **Вимоги до фронтів наростання та опір підтяжки:**
   Оскільки лінія MDIO працює за принципом відкритого стоку (Open-Drain) або перемикання у стан високого імпедансу (Hi-Z), перехід лінії з логічного нуля в логічну одиницю здійснюється виключно за рахунок заряду сумарної паразитної ємності монтажу та вхідних каскадів трансиверів через зовнішній резистор підтяжки `R_p`. Час наростання фронту від 10% до 90% рівня живлення описується класичною експоненційною залежністю:
   ```
   t_rise ≈ 2.2 · R_p · C_bus
   ```
   Якщо до шини підключено 8 трансиверів PHY (наприклад, у керованому комутаторі) із сумарною ємністю `C_bus = 100 пФ`, а опір підтяжки обрано занадто великим (`R_p = 10 кОм`), час наростання становить:
   ```
   t_rise ≈ 2.2 · 10000 · 100·10⁻¹² = 2200 нс = 2.2 мкс
   ```
   Це вп'ятеро перевищує весь період такту 400 нс. Напруга на лінії просто не встигає піднятися до порогу логічної одиниці, що викликає катастрофічні помилки зчитування даних. Для надійної роботи на максимальній частоті 2.5 МГц номінал підтяжки необхідно обирати в діапазоні **1.5–2.2 кОм**, забезпечуючи час наростання `t_rise < 100 нс`.

---

## 2. Анатомія транзакцій та керування напрямком шини

Програмний біт-бенгінг вимагає чіткого керування внутрішнім тригером напрямку GPIO (Input / Output) на кожному етапі кадру.

### Покроковий розбір кадру запису Clause 22 (Write)
1. **Преамбула (Preamble):** Контролер налаштовує пін MDIO як вихід, встановлює на ньому логічну «1» і формує 32 повні тактові імпульси MDC. Цей етап необхідний для того, щоб вхідні цифрові фільтри та автомат розбору кадру всіх підключених мікросхем PHY скинулися в початковий стан очікування.
2. **Початок кадру (Start of Frame, ST):** Контролер послідовно передає 2 біти `0` та `1`.
3. **Код операції (Opcode, OP):** Для операції запису передаються біти `0` та `1`.
4. **Адреса трансивера (PHYAD):** 5 бітів адреси цільового чіпа (від `PHYAD[4]` до `PHYAD[0]`, старшим бітом уперед MSB). Лише той PHY, чия апаратна адреса збігається з переданою, продовжує обробку кадру.
5. **Адреса регістра (REGAD):** 5 бітів адреси регістра (від `REGAD[4]` до `REGAD[0]`, MSB first), вибираючи один із 32 внутрішніх регістрів чіпа.
6. **Зміна напрямку (Turnaround, TA):** При записі контролер продовжує жорстко утримувати лінію MDIO і послідовно передає біти `1` та `0`.
7. **Дані (DATA):** Контролер передає 16 бітів даних від `D15` до `D0`.
8. **Завершення (Idle):** Контролер відпускає лінію MDIO у стан високого імпедансу (вхід) і формує один додатковий холостий такт MDC, повертаючи шину в стан спокою.

### Покроковий розбір кадру читання Clause 22 (Read)
Транзакція читання відрізняється критично важливим моментом передачі контролю над лінією від ведучого MAC до веденого PHY у фазі Turnaround:
1. Контролер передає преамбулу (32 одиниці), ST (`01`), OP (`10` для читання), 5 біт `PHYAD` та 5 біт `REGAD`.
2. **Перший такт фази TA (стан Z):** Одразу після спадного фронту MDC, на якому було передано останній біт адреси регістра `REGAD[0]`, контролер перемикає пін GPIO MDIO у режим високоімпедансного входу (Hi-Z). Лінія відпускається, і зовнішній резистор підтяжки утримує високий рівень напруги. Контролер формує перший наростаючий та спадний фронт MDC.
3. **Другий такт фази TA (стан 0 / підтвердження ACK):** Обраний трансивер PHY перехоплює керування лінією MDIO і на спадному фронті MDC примусово притискає лінію до землі (формуючи логічний нуль `0`). Контролер підіймає MDC у стан «1» і зчитує рівень лінії MDIO:
   - Якщо зчитано `0`: трансивер присутній на шині, успішно розпізнав свою адресу і підтверджує готовність передавати дані.
   - Якщо зчитано `1`: лінія залишилася підтягнутою до живлення. Це однозначно вказує на те, що за вказаною адресою `PHYAD` немає підключеного трансивера або мікросхема знеструмлена.
4. **Прийом даних (DATA):** Трансивер PHY по черзі виставляє 16 бітів даних `D15..D0` на кожному спадному фронті MDC. Контролер зчитує кожен біт за наростаючим фронтом MDC.
5. Після передачі молодшого біта `D0` трансивер PHY негайно вимикає свій вихідний транзистор, переходячи у стан Hi-Z.

### Двоетапна адресація Clause 45
Для доступу до розширеного простору Clause 45 (10GbE / 40GbE / 100GbE) використовується два окремі послідовні кадри з патерном старту `ST = 00`:
1. **Кадр адреси (Address Frame, OP = 00):** Контролер передає 5 бітів порту `PRTAD`, 5 бітів домену пристрою `DEVAD`, біти TA (`10`) та повну 16-бітну адресу цільового регістра. Внутрішній автомат вибраного MMD зберігає цю адресу у своєму тіньовому регістрі адреси.
2. **Кадр даних (Data Frame):** Контролер надсилає другий кадр із тими ж `PRTAD` та `DEVAD`, але з іншим кодом операції:
   - `OP = 01` — запис 16 бітів даних за збереженою адресою;
   - `OP = 11` — читання 16 бітів даних за збереженою адресою;
   - `OP = 10` — читання 16 бітів даних з автоматичним інкрементом покажчика адреси після операції (дозволяє пакетом вичитувати блоки телеметрії та лічильники помилок без повторної відправки кадрів адреси).

---

## 3. Модульна реалізація драйвера на C та C++

Нижче наведено промисловий код драйвера програмного біт-бенгінгу, розрахований на роботу в середовищі мікроконтролерів Cortex-M / RISC-V з підтримкою Clause 22, Clause 45, автоматичного сканування шини та коректної обробки статусу лінка.

:::tabs
```c
/* mdio_bitbang.h / mdio_bitbang.c - Повна реалізація драйвера Bit-Banging MDC/MDIO на C */
#ifndef MDIO_BITBANG_H
#define MDIO_BITBANG_H

#include <stdint.h>
#include <stdbool.h>

/* Абстракція низькорівневого доступу до ліній GPIO */
typedef struct {
    void (*set_mdc)(bool level);
    void (*set_mdio_level)(bool level);
    bool (*get_mdio_level)(void);
    void (*set_mdio_dir_output)(bool is_output);
    void (*delay_half_period)(void); /* Затримка ~200 нс для досягнення 2.5 МГц */
} mdio_gpio_ops_t;

typedef struct {
    mdio_gpio_ops_t ops;
} mdio_bus_t;

typedef enum {
    MDIO_OK = 0,
    MDIO_ERR_TIMEOUT,
    MDIO_ERR_NO_DEVICE,
    MDIO_ERR_INVALID_PARAM
} mdio_status_t;

void mdio_bb_init(const mdio_bus_t *bus);
mdio_status_t mdio_bb_c22_write(const mdio_bus_t *bus, uint8_t phy_addr, uint8_t reg_addr, uint16_t data);
mdio_status_t mdio_bb_c22_read(const mdio_bus_t *bus, uint8_t phy_addr, uint8_t reg_addr, uint16_t *data);
mdio_status_t mdio_bb_c45_write(const mdio_bus_t *bus, uint8_t prt_addr, uint8_t dev_addr, uint16_t reg_addr, uint16_t data);
mdio_status_t mdio_bb_c45_read(const mdio_bus_t *bus, uint8_t prt_addr, uint8_t dev_addr, uint16_t reg_addr, uint16_t *data);
uint32_t mdio_bb_scan(const mdio_bus_t *bus);
bool mdio_bb_get_link_status(const mdio_bus_t *bus, uint8_t phy_addr);

#endif /* MDIO_BITBANG_H */

/* --- Реалізація функцій драйвера --- */

static void mdc_pulse(const mdio_bus_t *bus) {
    bus->ops.set_mdc(true);
    bus->ops.delay_half_period();
    bus->ops.set_mdc(false);
    bus->ops.delay_half_period();
}

static void send_preamble(const mdio_bus_t *bus) {
    bus->ops.set_mdio_dir_output(true);
    bus->ops.set_mdio_level(true);
    for (int i = 0; i < 32; ++i) {
        mdc_pulse(bus);
    }
}

static void send_bits(const mdio_bus_t *bus, uint32_t value, uint8_t count) {
    for (int i = (int)count - 1; i >= 0; --i) {
        bool bit = (value >> i) & 1U;
        bus->ops.set_mdio_level(bit);
        bus->ops.delay_half_period();
        bus->ops.set_mdc(true);
        bus->ops.delay_half_period();
        bus->ops.set_mdc(false);
    }
}

static uint16_t receive_bits(const mdio_bus_t *bus, uint8_t count) {
    uint16_t res = 0;
    for (int i = 0; i < (int)count; ++i) {
        bus->ops.set_mdc(true);
        bus->ops.delay_half_period();
        res = (uint16_t)((res << 1) | (bus->ops.get_mdio_level() ? 1U : 0U));
        bus->ops.set_mdc(false);
        bus->ops.delay_half_period();
    }
    return res;
}

void mdio_bb_init(const mdio_bus_t *bus) {
    bus->ops.set_mdio_dir_output(true);
    bus->ops.set_mdio_level(true);
    bus->ops.set_mdc(false);
    bus->ops.delay_half_period();
}

mdio_status_t mdio_bb_c22_write(const mdio_bus_t *bus, uint8_t phy_addr, uint8_t reg_addr, uint16_t data) {
    if (phy_addr > 31 || reg_addr > 31) return MDIO_ERR_INVALID_PARAM;

    send_preamble(bus);
    bus->ops.set_mdio_dir_output(true);

    send_bits(bus, 0x01U, 2);        /* ST = 01 */
    send_bits(bus, 0x01U, 2);        /* OP = 01 (Write) */
    send_bits(bus, phy_addr, 5);     /* PHYAD */
    send_bits(bus, reg_addr, 5);     /* REGAD */
    send_bits(bus, 0x02U, 2);        /* TA = 10 */
    send_bits(bus, data, 16);        /* DATA */

    bus->ops.set_mdio_dir_output(false);
    mdc_pulse(bus);
    return MDIO_OK;
}

mdio_status_t mdio_bb_c22_read(const mdio_bus_t *bus, uint8_t phy_addr, uint8_t reg_addr, uint16_t *data) {
    if (!data || phy_addr > 31 || reg_addr > 31) return MDIO_ERR_INVALID_PARAM;

    send_preamble(bus);
    bus->ops.set_mdio_dir_output(true);

    send_bits(bus, 0x01U, 2);        /* ST = 01 */
    send_bits(bus, 0x02U, 2);        /* OP = 10 (Read) */
    send_bits(bus, phy_addr, 5);     /* PHYAD */
    send_bits(bus, reg_addr, 5);     /* REGAD */

    /* Turnaround: перехід у режим високоімпедансного входу */
    bus->ops.set_mdio_dir_output(false);
    mdc_pulse(bus);                  /* Такт Z */

    /* Зчитування біта підтвердження (ACK від PHY = 0) */
    bus->ops.set_mdc(true);
    bus->ops.delay_half_period();
    bool ack = bus->ops.get_mdio_level();
    bus->ops.set_mdc(false);
    bus->ops.delay_half_period();

    if (ack) return MDIO_ERR_NO_DEVICE;

    *data = receive_bits(bus, 16);
    mdc_pulse(bus);
    return MDIO_OK;
}

mdio_status_t mdio_bb_c45_write(const mdio_bus_t *bus, uint8_t prt_addr, uint8_t dev_addr, uint16_t reg_addr, uint16_t data) {
    if (prt_addr > 31 || dev_addr > 31) return MDIO_ERR_INVALID_PARAM;

    /* 1. Кадр адреси */
    send_preamble(bus);
    bus->ops.set_mdio_dir_output(true);
    send_bits(bus, 0x00U, 2);        /* ST = 00 (Clause 45) */
    send_bits(bus, 0x00U, 2);        /* OP = 00 (Address) */
    send_bits(bus, prt_addr, 5);
    send_bits(bus, dev_addr, 5);
    send_bits(bus, 0x02U, 2);        /* TA = 10 */
    send_bits(bus, reg_addr, 16);
    bus->ops.set_mdio_dir_output(false);
    mdc_pulse(bus);

    /* 2. Кадр запису даних */
    send_preamble(bus);
    bus->ops.set_mdio_dir_output(true);
    send_bits(bus, 0x00U, 2);        /* ST = 00 */
    send_bits(bus, 0x01U, 2);        /* OP = 01 (Write) */
    send_bits(bus, prt_addr, 5);
    send_bits(bus, dev_addr, 5);
    send_bits(bus, 0x02U, 2);        /* TA = 10 */
    send_bits(bus, data, 16);
    bus->ops.set_mdio_dir_output(false);
    mdc_pulse(bus);

    return MDIO_OK;
}

mdio_status_t mdio_bb_c45_read(const mdio_bus_t *bus, uint8_t prt_addr, uint8_t dev_addr, uint16_t reg_addr, uint16_t *data) {
    if (!data || prt_addr > 31 || dev_addr > 31) return MDIO_ERR_INVALID_PARAM;

    /* 1. Кадр адреси */
    send_preamble(bus);
    bus->ops.set_mdio_dir_output(true);
    send_bits(bus, 0x00U, 2);
    send_bits(bus, 0x00U, 2);
    send_bits(bus, prt_addr, 5);
    send_bits(bus, dev_addr, 5);
    send_bits(bus, 0x02U, 2);
    send_bits(bus, reg_addr, 16);
    bus->ops.set_mdio_dir_output(false);
    mdc_pulse(bus);

    /* 2. Кадр читання даних */
    send_preamble(bus);
    bus->ops.set_mdio_dir_output(true);
    send_bits(bus, 0x00U, 2);
    send_bits(bus, 0x03U, 2);        /* OP = 11 (Read) */
    send_bits(bus, prt_addr, 5);
    send_bits(bus, dev_addr, 5);

    bus->ops.set_mdio_dir_output(false);
    mdc_pulse(bus);

    bus->ops.set_mdc(true);
    bus->ops.delay_half_period();
    bool ack = bus->ops.get_mdio_level();
    bus->ops.set_mdc(false);
    bus->ops.delay_half_period();

    if (ack) return MDIO_ERR_NO_DEVICE;

    *data = receive_bits(bus, 16);
    mdc_pulse(bus);
    return MDIO_OK;
}

uint32_t mdio_bb_scan(const mdio_bus_t *bus) {
    uint32_t found_mask = 0;
    for (uint8_t addr = 0; addr < 32; ++addr) {
        uint16_t val = 0;
        if (mdio_bb_c22_read(bus, addr, 0x02, &val) == MDIO_OK) {
            if (val != 0xFFFFU && val != 0x0000U) {
                found_mask |= (1U << addr);
            }
        }
    }
    return found_mask;
}

bool mdio_bb_get_link_status(const mdio_bus_t *bus, uint8_t phy_addr) {
    uint16_t bmsr = 0;
    if (mdio_bb_c22_read(bus, phy_addr, 0x01, &bmsr) != MDIO_OK) return false;
    if (mdio_bb_c22_read(bus, phy_addr, 0x01, &bmsr) != MDIO_OK) return false;
    return (bmsr & (1U << 2)) != 0;
}
```
```cpp
// mdio_bitbang.hpp - C++20 реалізація драйвера Bit-Banging MDC/MDIO
#pragma once

#include <cstdint>
#include <concepts>
#include <expected>
#include <optional>

namespace eth::mdio {

enum class Error : uint8_t {
    Timeout,
    NoDevice,
    BusCollision,
    InvalidParameter
};

// Концепт для валідації апаратних операцій GPIO на етапі компіляції
template <typename T>
concept GpioOperations = requires(T ops, bool lvl, bool is_out) {
    { ops.set_mdc(lvl) } noexcept;
    { ops.set_mdio_level(lvl) } noexcept;
    { ops.get_mdio_level() } noexcept -> std::same_as<bool>;
    { ops.set_mdio_direction(is_out) } noexcept;
    { ops.delay_half_period() } noexcept;
};

template <GpioOperations Ops>
class BitBangBus {
public:
    explicit constexpr BitBangBus(Ops ops) noexcept : ops_(ops) {}

    void init() const noexcept {
        ops_.set_mdio_direction(true);
        ops_.set_mdio_level(true);
        ops_.set_mdc(false);
        ops_.delay_half_period();
    }

    [[nodiscard]] std::expected<void, Error> write_c22(uint8_t phy_addr, uint8_t reg_addr, uint16_t data) const noexcept {
        if (phy_addr > 31 || reg_addr > 31) return std::unexpected(Error::InvalidParameter);

        send_preamble();
        ops_.set_mdio_direction(true);

        send_bits(0b01, 2);              // Start of Frame (ST = 01)
        send_bits(0b01, 2);              // Opcode Write (OP = 01)
        send_bits(phy_addr, 5);          // PHY Address
        send_bits(reg_addr, 5);          // Register Address
        send_bits(0b10, 2);              // Turnaround (TA = 10)
        send_bits(data, 16);             // Data D15..D0

        release_bus();
        return {};
    }

    [[nodiscard]] std::expected<uint16_t, Error> read_c22(uint8_t phy_addr, uint8_t reg_addr) const noexcept {
        if (phy_addr > 31 || reg_addr > 31) return std::unexpected(Error::InvalidParameter);

        send_preamble();
        ops_.set_mdio_direction(true);

        send_bits(0b01, 2);              // Start of Frame (ST = 01)
        send_bits(0b10, 2);              // Opcode Read (OP = 10)
        send_bits(phy_addr, 5);          // PHY Address
        send_bits(reg_addr, 5);          // Register Address

        // Turnaround: перехід у режим входу (Hi-Z)
        ops_.set_mdio_direction(false);
        clock_cycle();                   // Такт Z

        ops_.set_mdc(true);
        ops_.delay_half_period();
        const bool ack_bit = ops_.get_mdio_level();
        ops_.set_mdc(false);
        ops_.delay_half_period();

        if (ack_bit) {
            // Лінія залишилася на рівні 1 — жоден трансивер не відповів
            return std::unexpected(Error::NoDevice);
        }

        const uint16_t value = receive_bits(16);
        release_bus();
        return value;
    }

    [[nodiscard]] std::expected<void, Error> write_c45(uint8_t prt, uint8_t dev, uint16_t reg, uint16_t data) const noexcept {
        if (prt > 31 || dev > 31) return std::unexpected(Error::InvalidParameter);

        // Крок 1: Кадр передачі адреси (OP = 00)
        send_preamble();
        ops_.set_mdio_direction(true);
        send_bits(0b00, 2); // ST = 00 (Clause 45)
        send_bits(0b00, 2); // OP = 00 (Address)
        send_bits(prt, 5);
        send_bits(dev, 5);
        send_bits(0b10, 2); // TA = 10
        send_bits(reg, 16); // 16-бітна адреса
        release_bus();

        // Крок 2: Кадр передачі даних (OP = 01)
        send_preamble();
        ops_.set_mdio_direction(true);
        send_bits(0b00, 2); // ST = 00
        send_bits(0b01, 2); // OP = 01 (Write)
        send_bits(prt, 5);
        send_bits(dev, 5);
        send_bits(0b10, 2); // TA = 10
        send_bits(data, 16);
        release_bus();

        return {};
    }

    [[nodiscard]] std::expected<uint16_t, Error> read_c45(uint8_t prt, uint8_t dev, uint16_t reg) const noexcept {
        if (prt > 31 || dev > 31) return std::unexpected(Error::InvalidParameter);

        // Крок 1: Кадр адреси
        send_preamble();
        ops_.set_mdio_direction(true);
        send_bits(0b00, 2);
        send_bits(0b00, 2);
        send_bits(prt, 5);
        send_bits(dev, 5);
        send_bits(0b10, 2);
        send_bits(reg, 16);
        release_bus();

        // Крок 2: Кадр читання даних (OP = 11)
        send_preamble();
        ops_.set_mdio_direction(true);
        send_bits(0b00, 2);
        send_bits(0b11, 2); // OP = 11 (Read)
        send_bits(prt, 5);
        send_bits(dev, 5);

        ops_.set_mdio_direction(false);
        clock_cycle(); // Z такт

        ops_.set_mdc(true);
        ops_.delay_half_period();
        const bool ack = ops_.get_mdio_level();
        ops_.set_mdc(false);
        ops_.delay_half_period();

        if (ack) return std::unexpected(Error::NoDevice);

        const uint16_t val = receive_bits(16);
        release_bus();
        return val;
    }

    [[nodiscard]] uint32_t scan_bus() const noexcept {
        uint32_t found_mask = 0;
        for (uint8_t addr = 0; addr < 32; ++addr) {
            auto res = read_c22(addr, 0x02); // Читаємо Регістр 2 (PHYID1)
            if (res.has_value() && *res != 0xFFFFU && *res != 0x0000U) {
                found_mask |= (1U << addr);
            }
        }
        return found_mask;
    }

    [[nodiscard]] bool get_link_status(uint8_t phy_addr) const noexcept {
        // Подвійне читання для коректного скидання апаратної засувки Latching Low
        auto first_read  = read_c22(phy_addr, 0x01);
        auto second_read = read_c22(phy_addr, 0x01);
        if (!second_read.has_value()) return false;
        return (*second_read & (1U << 2)) != 0;
    }

private:
    Ops ops_;

    void clock_cycle() const noexcept {
        ops_.set_mdc(true);
        ops_.delay_half_period();
        ops_.set_mdc(false);
        ops_.delay_half_period();
    }

    void send_preamble() const noexcept {
        ops_.set_mdio_direction(true);
        ops_.set_mdio_level(true);
        for (int i = 0; i < 32; ++i) {
            clock_cycle();
        }
    }

    void send_bits(uint32_t val, uint8_t count) const noexcept {
        for (int i = count - 1; i >= 0; --i) {
            const bool bit = (val >> i) & 1U;
            ops_.set_mdio_level(bit);
            ops_.delay_half_period();
            ops_.set_mdc(true);
            ops_.delay_half_period();
            ops_.set_mdc(false);
        }
    }

    [[nodiscard]] uint16_t receive_bits(uint8_t count) const noexcept {
        uint16_t result = 0;
        for (int i = 0; i < count; ++i) {
            ops_.set_mdc(true);
            ops_.delay_half_period();
            result = static_cast<uint16_t>((result << 1) | (ops_.get_mdio_level() ? 1U : 0U));
            ops_.set_mdc(false);
            ops_.delay_half_period();
        }
        return result;
    }

    void release_bus() const noexcept {
        ops_.set_mdio_direction(false);
        clock_cycle();
    }
};

} // namespace eth::mdio
```
:::

---

## 4. Опитування стану проти переривань та оптимізація преамбули

У реальних мережевих драйверах керування фізичним рівнем організовується за однією з двох базових архітектур:

### 1. Періодичне опитування (Polling) та таймери
Найпростіший підхід полягає в запуску періодичного таймера операційної системи (наприклад, у Linux `phylib` опитування відбувається кожні 1000 мс). Кожну секунду драйвер виконує читання регістрів BMSR (Регістр 1) та ANLPAR (Регістр 5). Якщо виявлено зміну біта Link Status або завершення автоузгодження, викликається обробник зміни стану мережевого інтерфейсу (`netif_carrier_on` / `netif_carrier_off`), який налаштовує швидкість та дуплекс у регістрах блоку MAC.

Головний недолік періодичного опитування — затримка реакції на обрив кабелю (до 1 секунди) та постійні накладні витрати процесорного часу на генерацію імпульсів біт-бенгінгу.

### 2. Асинхронне керування за перериваннями (Interrupt-Driven)
Майже всі сучасні мікросхеми PHY мають спеціальну вихідну ніжку переривання (зазвичай з відкритим стоком та активним низьким рівнем — `INT_N` або `IRQ_N`). Цю ніжку підключають до лінії зовнішнього переривання (EXTI) мікроконтролера.

У внутрішніх регістрах виробника (наприклад, Регістр 18 у Microchip KSZ9031 або Регістр 19 у Realtek RTL8211) налаштовується маска подій, які викликають переривання:
- Зміна стану лінка (Link Up / Link Down);
- Завершення процесу автоузгодження (Auto-Negotiation Complete);
- Виявлення віддаленої аварії (Remote Fault);
- Помилка полярності пар або виявлення надмірного рівня шуму (Energy Efficient Ethernet wake-up).

При виникненні події трансивер притискає ніжку `INT_N` до нуля. Процесор у швидкому обробнику переривання виставляє прапорець, а фоновий потік задач зчитує регістр статусу переривань PHY через шину MDIO. Оскільки регістри переривань PHY зазвичай мають поведінку `RC` (*Read to Clear*), саме зчитування через MDIO автоматично очищає внутрішній прапорець і відпускає лінію `INT_N` у високий стан. Це усуває потребу в періодичному опитуванні шини й забезпечує миттєву реакцію системи на підключення або вимкнення патч-корду.

### 3. Оптимізація обміну через придушення преамбули (Preamble Suppression)
Стандартний кадр Clause 22 містить 32 біти преамбули, що при частоті 2.5 МГц займає 12.8 мкс із загальних 25.6 мкс тривалості транзакції. Тобто половина часу передачі витрачається на передачу синхронізуючих одиниць.

Якщо біт 6 регістра 1 (`BMSR_PREAMBLE_SUPPR`) дорівнює одиниці, трансивер підтримує роботу з короткою преамбулою. Після першої ініціалізуючої транзакції з повною 32-бітною преамбулою контролер має право надсилати всі наступні кадри лише з 1 тактом преамбули (або без неї взагалі, починаючи транзакцію безпосередньо з комбінації Start of Frame `01`). Це подвоює пропускну здатність шини, скорочуючи тривалість транзакції до 13.2 мкс, що критично важливо для багатопортових комутаторів із 24 або 48 портами на спільній шині MDIO.

---

## 5. Діагностика та практичні пастки реалізації

Під час проектування та налагодження програмного драйвера біт-бенгінгу інженери найчастіше стикаються з такими апаратними й програмними проблемами:

### 1. Неадекватність внутрішніх підтяжок мікроконтролера
Внутрішні підтягувальні резистори портів введення-виведення більшості мікроконтролерів (STM32, ESP32, AVR, PIC) мають типовий номінал 30–50 кОм. Спроба зекономити один дискретний резистор на платі й увімкнути внутрішню підтяжку на ніжці MDIO призводить до повної непрацездатності шини на частотах понад 50 кГц. Велика постійна часу RC перетворює прямокутний сигнал на повільну пилкоподібну напругу. Для надійної роботи на платі **обов'язково** повинен бути встановлений зовнішній прецизійний резистор **1.5–2.2 кОм**, підключений до тієї ж шини живлення вводу-виводу, що й трансивер (3.3 В або 2.5 В).

### 2. Стан невизначеності при обриві кабелю та засувка Latching Low
Якщо мережевий кабель від'єднати і через секунду підключити назад, аналогова частина PHY відновить зв'язок і підійме лінійні сигнали. Проте біт 2 у регістрі 1 (BMSR) залишиться рівним `0`. Якщо програмний потік опитування виконує лише одне зчитування регістра `BMSR`, драйвер повідомить операційну систему про обрив з'єднання і вимкне мережевий інтерфейс. Лише патерн подвійного послідовного читання гарантує, що перше звернення очистить зафіксовану в минулому аварію, а друге поверне дійсний поточний статус.

### 3. Дзвін та відбиття тактового сигналу MDC
На великих друкованих платах із довжиною траси понад 15–20 см круті фронти перемикання сучасних вихідних драйверів мікроконтролерів (швидкість наростання менше 1–2 нс) спричиняють високочастотний дзвін та відбиття сигналу на лінії MDC. Трансивер PHY з чутливим тригером Шмітта на вході такту сприймає цей дзвін як серію додаткових паразитних тактових імпульсів, що зміщує бітовий зсувний регістр і повністю руйнує кадр. Для усунення цього ефекту послідовно з виходом MDC мікроконтролера встановлюють демпфуючий резистор номіналом 22–33 Ω безпосередньо біля вихідної ніжки процесора, або знижують швидкість наростання (Slew Rate Control) у конфігураційних регістрах GPIO.

### 4. Конфлікт драйверів у фазі Turnaround
Якщо програмний стек на високій частоті процесора затримується з перемиканням піна GPIO з виходу у вхід під час першого такту TA операції читання, вихідний каскад мікроконтролера залишається в режимі Push-Pull з рівнем логічної одиниці («1»). Коли на другому такті TA ведений трансивер PHY відкриває свій нижній ключ і притискає шину до нуля («0»), виникає пряме коротке замикання між виходами двох мікросхем. Це викликає сплеск струму до 40–80 мА, локальне просідання напруги живлення ядра і може пошкодити захисні діоди вхідного порту PHY. Тому в драйвері перемикання напрямку піна повинно відбуватися негайно після видачі останнього біта адреси регістра `REGAD[0]`.

### 5. Налагодження за допомогою логічного аналізатора
Для перевірки роботи програмного біт-бенгінгу незамінним інструментом є цифровий логічний аналізатор (наприклад, Saleae Logic або вбудований у DSO). Під час налаштування декодера протоколу MDIO в утиліті аналізу необхідно задати такі параметри:
- **Канал такту (Clock):** пін MDC, вибірка за наростаючим фронтом (*Rising edge*);
- **Канал даних (Data):** пін MDIO;
- **Початковий стан:** вимагати 32-бітну преамбулу для Clause 22 або дозволяти скорочену преамбулу (*Preamble Suppression*);
- **Поріг напруги (Threshold):** для лінії живлення 3.3 В встановити рівень перемикання 1.65 В, а для низьковольтних шин Clause 45 (1.2 В) — рівень 0.6 В.

Якщо аналізатор фіксує кадри без помилок, але функція читання повертає нулі, слід звернути увагу на затримку між спадним фронтом такту та зміною сигналу на виході трансивера PHY: час поширення сигналу `t_val` від чіпа до мікроконтролера не повинен перевищувати половину тактового періоду.
