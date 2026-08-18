# ⚙️ Програмний драйвер шини MDIO та автомат опитування лінка

Навіть якщо контролер Ethernet MAC самостійно обробляє швидкісні потоки кадрів через прямий доступ до пам'яті (DMA), налаштування фізичного лінка цілком покладається на програмний драйвер. Саме мікропрограма процесора повинна виявити підключений трансивер PHY, скинути його внутрішні регістри, налаштувати список дозволених швидкостей, запустити автопогодження та постійно відстежувати фізичний стан з'єднання (наявність несучої, швидкість 10/100/1000 Мбіт/с, повнодуплексний чи напівдуплексний режим, а також помилки на лінії).

У багатьох вбудованих системах і системах на кристалі (SoC) апаратний контролер шини SMI/MDIO може бути відсутній або зайнятий, або ж виникає потреба керувати зовнішнім комутатором через звичайні виводи загального призначення (GPIO). Нижче наведено повну архітектуру програмного біт-бенгінг драйвера шини MDIO за стандартом IEEE 802.3 Clause 22 та надійний автомат станів опитування лінка.

## 1. Програмний побітовий синтез (Bit-Banging) протоколу MDIO

Шина MDIO складається з двох ліній: односпрямованого тактового сигналу `MDC` та двоспрямованої лінії даних `MDIO`. Для реалізації протоколу на рівні GPIO мікроконтролер повинен вміти:
1. Керувати виводом `MDC` у режимі двотактного виходу (англ. *Push-Pull*);
2. Динамічно перемикати вивід `MDIO` між двотактним виходом (під час передавання преамбули, коду команди, адреси та даних запису) і високоімпедансним входом із підтяжкою (під час прийому даних від PHY).

Часовий регламент вимагає, щоб тривалість високого та низького рівнів тактового сигналу `MDC` становила не менше ніж **160–200 нс** (що відповідає максимальній частоті 2.5 МГц). Дані на лінії `MDIO` фіксуються трансивером PHY за висхідним фронтом `MDC`, а змінюються контролером за спадним фронтом:

```general
        __      __      __      __      __
MDC  __/  \____/  \____/  \____/  \____/  \__
        :       :       :       :       :
MDIO --< Біт 1 >-------< Біт 0 >-------< TA  >--
        :       :       :       :       :
        ▲ вибірка       ▲ вибірка       ▲ зміна напрямку
```

### Захисний інтервал Turnaround (TA)

Особливої уваги потребує фаза зміни напрямку передавання (Turnaround, 2 такти):
* **При записі (Write, OP = 01b)**: Контролер MAC утримує керування лінією `MDIO` протягом усього кадру. У фазі `TA` він послідовно виставляє логічну `1`, а потім логічний `0` (`10`b), після чого одразу передає 16 бітів даних.
* **При читанні (Read, OP = 10b)**: На першому такті фази `TA` контролер переводить свій GPIO-вивід `MDIO` у режим входу (стан високого імпедансу `Z`). Зовнішній резистор підтяжки утримує лінію на високому рівні. На другому такті трансивер PHY, розпізнавши свою адресу, бере керування лінією на себе й примусово притискає її до нуля (`0`), підтверджуючи готовність видавати дані. Якщо під час другого такту лінія залишається у стані логічної одиниці, це свідчить про відсутність PHY за цією адресою (шина підтягнута до VDD, повертається `0xFFFF`).

## 2. Повний життєвий цикл ініціалізації та узгодження лінка

Процес встановлення зв'язку складається з чотирьох строго послідовних кроків:

```general
[ Скидання PHY (BMCR.15) ]
            │
            ▼
[ Перевірка ID (0x02 / 0x03) ]
            │
            ▼
[ Запис здатностей (ANAR / GBCR) ]
            │
            ▼
[ Запуск Auto-Negotiation (BMCR.9) ]
            │
            ▼
[ Опитування BMSR.5 та BMSR.2 ] ◄──┐ (Циклічний моніторинг)
            │                      │
     (Лінк піднято?)               │
      ├── НІ ──────────────────────┘
      └── ТАК
            │
            ▼
[ Розв'язання швидкості та дуплексу (Resolution) ]
            │
            ▼
[ Конфігурація внутрішнього MAC і DMA ]
```

### Крок 1: Програмне скидання (Software Reset)
Драйвер записує одиницю в біт 15 регістра `0x00` (BMCR). Трансивер скидає всі внутрішні PLL, аналогові фільтри та регістри до значень за замовчуванням, визначених strapping-підтяжками. Драйвер опитує цей біт у циклі з тайм-аутом (до 500 мс), чекаючи, поки чіп скине його в нуль, сигналізуючи про готовність до роботи.

### Крок 2: Перевірка ідентифікатора PHY
Драйвер зчитує регістри `0x02` (PHYID1) та `0x03` (PHYID2). Значення `0xFFFF` або `0x0000` вказує на обрив шини, неправильну адресу `PHYAD` або відсутність живлення трансивера. Отримане значення зіставляється з OUI виробника (наприклад, `0x00221560` для трансиверів Microchip KSZ9031 або `0x001C` для Realtek RTL8211).

### Крок 3: Оголошення власних параметрів зв'язку
Перед запуском погодження драйвер налаштовує локальні можливості:
* У регістр `0x04` (ANAR) записуються біти дозволених швидкостей 10BASE-T та 100BASE-TX (Full/Half Duplex), підтримка керування потоком (Pause Frames, біти 10 і 11), а також обов'язковий селектор IEEE 802.3 (`00001`b у бітах `[4:0]`);
* Для гігабітних PHY у регістр `0x09` (1000BASE-T Control) записуються біти 9 (1000BASE-T Full Duplex) та 8 (1000BASE-T Half Duplex).

### Крок 4: Запуск та очікування автопогодження
Драйвер встановлює біт 12 (`Auto-Negotiation Enable`) та біт 9 (`Restart Auto-Negotiation`) у регістрі `BMCR`. PHY починає випромінювати в кабель пачки імпульсів FLP (Fast Link Pulses).

Драйвер переходить до періодичного опитування регістра `0x01` (BMSR) кожні 50–100 мс:
* Спочатку перевіряється біт 2 (`Link Status`). Оскільки цей біт має апаратну властивість **Latching Low** (пам'ятає факт попереднього падіння зв'язку), драйвер зобов'язаний зчитати BMSR двічі поспіль: перше зчитування скидає засувку, друге повертає актуальний фізичний стан;
* Якщо біт 2 став рівним 1, драйвер перевіряє біт 5 (`Auto-Negotiation Complete`). Його одиничний стан гарантує, що сторінки FLP успішно прийняті від лінк-партнера, підтверджені трьома копіями, і параметри зв'язку можна обчислювати.

### Крок 5: Пріоритетне розв'язання результату (Priority Resolution)
Параметри лінка визначаються логічним множенням (побітовим І) власних оголошених можливостей (`ANAR`, `GBCR`) та можливостей віддаленого партнера (`ANLPAR`, `GBSR`). Згідно з таблицею пріоритетів стандарту IEEE 802.3 обирається найшвидший спільний режим:

```general
1. 1000BASE-T Full Duplex (якщо GBCR.9 = 1 AND GBSR.11 = 1)
2. 1000BASE-T Half Duplex (якщо GBCR.8 = 1 AND GBSR.10 = 1)
3. 100BASE-TX Full Duplex (якщо ANAR.8 = 1 AND ANLPAR.8 = 1)
4. 100BASE-TX Half Duplex (якщо ANAR.7 = 1 AND ANLPAR.7 = 1)
5. 10BASE-T Full Duplex   (якщо ANAR.6 = 1 AND ANLPAR.6 = 1)
6. 10BASE-T Half Duplex   (якщо ANAR.5 = 1 AND ANLPAR.5 = 1)
```

Після обчислення результату драйвер зобов'язаний переконфігурувати внутрішні регістри MAC-контролера (встановити відповідну частоту тактування шини MII/RGMII та режим дуплексу), щоб прийом і передавання кадрів велися синхронно з фізичним середовищем.

## 3. Програмна реалізація драйвера

Нижче наведено модульну, перевірену на практиці реалізацію біт-бенгінг драйвера MDIO та кінцевого автомата погодження.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Регістри IEEE 802.3 Clause 22 */
#define MDIO_REG_BMCR       0x00
#define MDIO_REG_BMSR       0x01
#define MDIO_REG_PHYID1     0x02
#define MDIO_REG_PHYID2     0x03
#define MDIO_REG_ANAR       0x04
#define MDIO_REG_ANLPAR     0x05
#define MDIO_REG_GBCR       0x09
#define MDIO_REG_GBSR       0x0A

/* Біти керування BMCR (0x00) */
#define BMCR_RESET          (1U << 15)
#define BMCR_SPEED_100      (1U << 13)
#define BMCR_AN_ENABLE      (1U << 12)
#define BMCR_AN_RESTART     (1U << 9)
#define BMCR_FULL_DUPLEX    (1U << 8)
#define BMCR_SPEED_1000     (1U << 6)

/* Біти статусу BMSR (0x01) */
#define BMSR_AN_COMPLETE    (1U << 5)
#define BMSR_LINK_STATUS    (1U << 2)

/* Біти здатностей ANAR / ANLPAR */
#define ADVERTISE_PAUSE_ASYM (1U << 11)
#define ADVERTISE_PAUSE_SYM  (1U << 10)
#define ADVERTISE_100_FULL   (1U << 8)
#define ADVERTISE_100_HALF   (1U << 7)
#define ADVERTISE_10_FULL    (1U << 6)
#define ADVERTISE_10_HALF    (1U << 5)
#define ADVERTISE_CSMA       (1U << 0)

/* Біти гігабітного керування та статусу */
#define GBCR_ADV_1000_FULL   (1U << 9)
#define GBCR_ADV_1000_HALF   (1U << 8)
#define GBSR_LP_1000_FULL    (1U << 11)
#define GBSR_LP_1000_HALF    (1U << 10)

typedef enum {
    LINK_SPEED_UNKNOWN = 0,
    LINK_SPEED_10M     = 10,
    LINK_SPEED_100M    = 100,
    LINK_SPEED_1000M   = 1000
} LinkSpeed;

typedef enum {
    LINK_DUPLEX_HALF = 0,
    LINK_DUPLEX_FULL = 1
} LinkDuplex;

typedef struct {
    bool link_up;
    LinkSpeed speed;
    LinkDuplex duplex;
    bool pause_rx;
    bool pause_tx;
} LinkStatus;

/* Апаратні операції GPIO (реалізуються для конкретної платформи) */
typedef struct {
    void (*set_mdc)(bool level);
    void (*set_mdio_dir_out)(bool out);
    void (*set_mdio_data)(bool level);
    bool (*get_mdio_data)(void);
    void (*delay_half_period)(void); /* Затримка ~200 нс (для MDC = 2.5 МГц) */
} MdioGpioOps;

typedef struct {
    const MdioGpioOps *ops;
    uint8_t phy_addr;
} EthernetPhyDriver;

/* Допоміжні функції побітового зв'язку */
static void mdio_clock_cycle(const MdioGpioOps *ops) {
    ops->set_mdc(false);
    ops->delay_half_period();
    ops->set_mdc(true);
    ops->delay_half_period();
}

static void mdio_send_bits(const MdioGpioOps *ops, uint32_t value, uint8_t count) {
    for (int8_t i = (int8_t)(count - 1); i >= 0; --i) {
        ops->set_mdc(false);
        ops->set_mdio_data((value >> i) & 1U);
        ops->delay_half_period();
        ops->set_mdc(true);
        ops->delay_half_period();
    }
}

static void mdio_send_preamble(const MdioGpioOps *ops) {
    ops->set_mdio_dir_out(true);
    ops->set_mdio_data(true);
    for (uint8_t i = 0; i < 32; ++i) {
        mdio_clock_cycle(ops);
    }
}

/* Читання регістра Clause 22 */
bool mdio_read(const EthernetPhyDriver *phy, uint8_t reg_addr, uint16_t *value) {
    const MdioGpioOps *ops = phy->ops;
    mdio_send_preamble(ops);

    /* ST=01 (2 біти), OP=10 (читання, 2 біти) */
    mdio_send_bits(ops, 0x01, 2);
    mdio_send_bits(ops, 0x02, 2);

    /* PHYAD (5 бітів), REGAD (5 бітів) */
    mdio_send_bits(ops, phy->phy_addr, 5);
    mdio_send_bits(ops, reg_addr, 5);

    /* Turnaround: перемикаємося на вхід */
    ops->set_mdio_dir_out(false);
    
    /* Такт 1 фази TA (стан Z) */
    ops->set_mdc(false);
    ops->delay_half_period();
    ops->set_mdc(true);
    ops->delay_half_period();

    /* Такт 2 фази TA: перевіряємо, чи притиснув PHY лінію до нуля */
    ops->set_mdc(false);
    ops->delay_half_period();
    bool ack = (ops->get_mdio_data() == false);
    ops->set_mdc(true);
    ops->delay_half_period();

    if (!ack) {
        return false; /* PHY не відповів на запит */
    }

    /* Читання 16 бітів даних */
    uint16_t data = 0;
    for (uint8_t i = 0; i < 16; ++i) {
        ops->set_mdc(false);
        ops->delay_half_period();
        data = (data << 1) | (ops->get_mdio_data() ? 1U : 0U);
        ops->set_mdc(true);
        ops->delay_half_period();
    }

    /* Додатковий такт для повернення шини в стан спокою */
    mdio_clock_cycle(ops);

    *value = data;
    return true;
}

/* Запис регістра Clause 22 */
bool mdio_write(const EthernetPhyDriver *phy, uint8_t reg_addr, uint16_t value) {
    const MdioGpioOps *ops = phy->ops;
    mdio_send_preamble(ops);

    /* ST=01 (2 біти), OP=01 (запис, 2 біти) */
    mdio_send_bits(ops, 0x01, 2);
    mdio_send_bits(ops, 0x01, 2);

    /* PHYAD (5 бітів), REGAD (5 бітів) */
    mdio_send_bits(ops, phy->phy_addr, 5);
    mdio_send_bits(ops, reg_addr, 5);

    /* TA = 10b (2 біти) */
    mdio_send_bits(ops, 0x02, 2);

    /* 16 бітів даних */
    mdio_send_bits(ops, value, 16);

    /* Відпускаємо шину */
    ops->set_mdio_dir_out(false);
    mdio_clock_cycle(ops);
    return true;
}

/* Ініціалізація та налаштування автопогодження */
bool phy_init(const EthernetPhyDriver *phy) {
    uint16_t val = 0;

    /* Перевіряємо присутність чіпа */
    if (!mdio_read(phy, MDIO_REG_PHYID1, &val) || val == 0xFFFF || val == 0x0000) {
        return false;
    }

    /* Запускаємо програмне скидання */
    mdio_write(phy, MDIO_REG_BMCR, BMCR_RESET);
    for (int timeout = 0; timeout < 100; ++timeout) {
        if (mdio_read(phy, MDIO_REG_BMCR, &val) && !(val & BMCR_RESET)) {
            break;
        }
    }

    /* Оголошуємо всі швидкості 10/100/1000 та підтримку PAUSE */
    uint16_t anar = ADVERTISE_CSMA | ADVERTISE_10_HALF | ADVERTISE_10_FULL |
                    ADVERTISE_100_HALF | ADVERTISE_100_FULL |
                    ADVERTISE_PAUSE_SYM | ADVERTISE_PAUSE_ASYM;
    mdio_write(phy, MDIO_REG_ANAR, anar);

    uint16_t gbcr = GBCR_ADV_1000_FULL | GBCR_ADV_1000_HALF;
    mdio_write(phy, MDIO_REG_GBCR, gbcr);

    /* Запускаємо автопогодження */
    uint16_t bmcr = BMCR_AN_ENABLE | BMCR_AN_RESTART;
    mdio_write(phy, MDIO_REG_BMCR, bmcr);

    return true;
}

/* Опитування стану та пріоритетне розв'язання параметрів лінка */
LinkStatus phy_poll_status(const EthernetPhyDriver *phy) {
    LinkStatus status = {0};
    uint16_t bmsr = 0;

    /* Перше читання скидає засувку Latching Low, друге дає реальний статус */
    mdio_read(phy, MDIO_REG_BMSR, &bmsr);
    if (!mdio_read(phy, MDIO_REG_BMSR, &bmsr) || !(bmsr & BMSR_LINK_STATUS)) {
        status.link_up = false;
        return status;
    }

    status.link_up = true;

    /* Якщо автопогодження не завершено, параметри ще не визначено */
    if (!(bmsr & BMSR_AN_COMPLETE)) {
        status.speed = LINK_SPEED_UNKNOWN;
        return status;
    }

    /* Зчитуємо локальні та віддалені здатності */
    uint16_t gbcr = 0, gbsr = 0, anar = 0, anlpar = 0;
    mdio_read(phy, MDIO_REG_GBCR, &gbcr);
    mdio_read(phy, MDIO_REG_GBSR, &gbsr);
    mdio_read(phy, MDIO_REG_ANAR, &anar);
    mdio_read(phy, MDIO_REG_ANLPAR, &anlpar);

    /* Таблиця пріоритетів IEEE 802.3 */
    if ((gbcr & GBCR_ADV_1000_FULL) && (gbsr & GBSR_LP_1000_FULL)) {
        status.speed = LINK_SPEED_1000M;
        status.duplex = LINK_DUPLEX_FULL;
    } else if ((gbcr & GBCR_ADV_1000_HALF) && (gbsr & GBSR_LP_1000_HALF)) {
        status.speed = LINK_SPEED_1000M;
        status.duplex = LINK_DUPLEX_HALF;
    } else if ((anar & ADVERTISE_100_FULL) && (anlpar & ADVERTISE_100_FULL)) {
        status.speed = LINK_SPEED_100M;
        status.duplex = LINK_DUPLEX_FULL;
    } else if ((anar & ADVERTISE_100_HALF) && (anlpar & ADVERTISE_100_HALF)) {
        status.speed = LINK_SPEED_100M;
        status.duplex = LINK_DUPLEX_HALF;
    } else if ((anar & ADVERTISE_10_FULL) && (anlpar & ADVERTISE_10_FULL)) {
        status.speed = LINK_SPEED_10M;
        status.duplex = LINK_DUPLEX_FULL;
    } else if ((anar & ADVERTISE_10_HALF) && (anlpar & ADVERTISE_10_HALF)) {
        status.speed = LINK_SPEED_10M;
        status.duplex = LINK_DUPLEX_HALF;
    }

    /* Обчислення режиму керування потоком PAUSE (IEEE 802.3 Annex 28B) */
    bool loc_sym = (anar & ADVERTISE_PAUSE_SYM) != 0;
    bool loc_asym = (anar & ADVERTISE_PAUSE_ASYM) != 0;
    bool lp_sym = (anlpar & ADVERTISE_PAUSE_SYM) != 0;
    bool lp_asym = (anlpar & ADVERTISE_PAUSE_ASYM) != 0;

    if (loc_sym && lp_sym) {
        status.pause_rx = true;
        status.pause_tx = true;
    } else if (loc_asym && lp_sym && lp_asym) {
        status.pause_rx = true;
        status.pause_tx = false;
    } else if (loc_sym && loc_asym && lp_asym) {
        status.pause_rx = false;
        status.pause_tx = true;
    }

    return status;
}
```
```cpp
#include <cstdint>
#include <expected>
#include <concepts>
#include <chrono>
#include <thread>
#include <optional>

namespace net::phy {

enum class Register : uint8_t {
    Bmcr   = 0x00,
    Bmsr   = 0x01,
    PhyId1 = 0x02,
    PhyId2 = 0x03,
    Anar   = 0x04,
    Anlpar = 0x05,
    Gbcr   = 0x09,
    Gbsr   = 0x0A
};

namespace bmcr_bits {
    constexpr uint16_t Reset         = 1U << 15;
    constexpr uint16_t Speed100      = 1U << 13;
    constexpr uint16_t AutoNegEnable = 1U << 12;
    constexpr uint16_t RestartAutoNeg= 1U << 9;
    constexpr uint16_t FullDuplex    = 1U << 8;
    constexpr uint16_t Speed1000     = 1U << 6;
}

namespace bmsr_bits {
    constexpr uint16_t AutoNegDone   = 1U << 5;
    constexpr uint16_t LinkStatus    = 1U << 2;
}

namespace anar_bits {
    constexpr uint16_t PauseAsym     = 1U << 11;
    constexpr uint16_t PauseSym      = 1U << 10;
    constexpr uint16_t Adv100Full    = 1U << 8;
    constexpr uint16_t Adv100Half    = 1U << 7;
    constexpr uint16_t Adv10Full     = 1U << 6;
    constexpr uint16_t Adv10Half     = 1U << 5;
    constexpr uint16_t Selector802_3 = 0x0001;
}

namespace gb_bits {
    constexpr uint16_t Adv1000Full   = 1U << 9;
    constexpr uint16_t Adv1000Half   = 1U << 8;
    constexpr uint16_t Lp1000Full    = 1U << 11;
    constexpr uint16_t Lp1000Half    = 1U << 10;
}

enum class Speed : uint16_t { Unknown = 0, Mbps10 = 10, Mbps100 = 100, Mbps1000 = 1000 };
enum class Duplex : uint8_t { Half, Full };
enum class DriverError { BusError, Timeout, DeviceNotFound, ResetFailed };

struct LinkState {
    bool link_up{false};
    Speed speed{Speed::Unknown};
    Duplex duplex{Duplex::Half};
    bool pause_rx{false};
    bool pause_tx{false};
};

/* Концепт апаратного інтерфейсу GPIO для переносимості */
template <typename T>
concept GpioInterface = requires(T g, bool level) {
    { g.set_mdc(level) };
    { g.set_mdio_direction_out(level) };
    { g.set_mdio_data(level) };
    { g.get_mdio_data() } -> std::same_as<bool>;
    { g.delay_half_period() };
};

template <GpioInterface Gpio>
class MdioDriver {
public:
    explicit MdioDriver(Gpio gpio, uint8_t phy_addr)
        : gpio_(gpio), phy_addr_(phy_addr) {}

    std::expected<uint16_t, DriverError> read_register(Register reg) {
        send_preamble();
        send_bits(0x01, 2); // ST = 01b
        send_bits(0x02, 2); // OP = 10b (Read)
        send_bits(phy_addr_, 5);
        send_bits(static_cast<uint8_t>(reg), 5);

        gpio_.set_mdio_direction_out(false); // Вхід

        // TA такт 1
        clock_cycle();

        // TA такт 2 (перевірка підтвердження)
        gpio_.set_mdc(false);
        gpio_.delay_half_period();
        bool ack = !gpio_.get_mdio_data();
        gpio_.set_mdc(true);
        gpio_.delay_half_period();

        if (!ack) {
            return std::unexpected(DriverError::DeviceNotFound);
        }

        uint16_t data = 0;
        for (int i = 0; i < 16; ++i) {
            gpio_.set_mdc(false);
            gpio_.delay_half_period();
            data = (data << 1) | (gpio_.get_mdio_data() ? 1U : 0U);
            gpio_.set_mdc(true);
            gpio_.delay_half_period();
        }

        clock_cycle();
        return data;
    }

    std::expected<void, DriverError> write_register(Register reg, uint16_t value) {
        send_preamble();
        send_bits(0x01, 2); // ST = 01b
        send_bits(0x01, 2); // OP = 01b (Write)
        send_bits(phy_addr_, 5);
        send_bits(static_cast<uint8_t>(reg), 5);
        send_bits(0x02, 2); // TA = 10b
        send_bits(value, 16);

        gpio_.set_mdio_direction_out(false);
        clock_cycle();
        return {};
    }

    std::expected<void, DriverError> init() {
        auto id = read_register(Register::PhyId1);
        if (!id || *id == 0xFFFF || *id == 0x0000) {
            return std::unexpected(DriverError::DeviceNotFound);
        }

        if (!write_register(Register::Bmcr, bmcr_bits::Reset)) {
            return std::unexpected(DriverError::BusError);
        }

        // Очікуємо завершення програмного скидання
        bool reset_ok = false;
        for (int i = 0; i < 50; ++i) {
            auto bmcr = read_register(Register::Bmcr);
            if (bmcr && !(*bmcr & bmcr_bits::Reset)) {
                reset_ok = true;
                break;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }

        if (!reset_ok) {
            return std::unexpected(DriverError::ResetFailed);
        }

        // Оголошуємо підтримувані швидкості
        uint16_t anar = anar_bits::Selector802_3 | anar_bits::Adv10Half | anar_bits::Adv10Full |
                        anar_bits::Adv100Half | anar_bits::Adv100Full |
                        anar_bits::PauseSym | anar_bits::PauseAsym;
        write_register(Register::Anar, anar);

        uint16_t gbcr = gb_bits::Adv1000Full | gb_bits::Adv1000Half;
        write_register(Register::Gbcr, gbcr);

        // Перезапускаємо автопогодження
        write_register(Register::Bmcr, bmcr_bits::AutoNegEnable | bmcr_bits::RestartAutoNeg);
        return {};
    }

    std::expected<LinkState, DriverError> poll_link() {
        LinkState state{};

        // Подвійне читання для очищення засувки Latching Low
        read_register(Register::Bmsr);
        auto bmsr = read_register(Register::Bmsr);
        if (!bmsr) {
            return std::unexpected(DriverError::BusError);
        }

        if (!(*bmsr & bmsr_bits::LinkStatus)) {
            state.link_up = false;
            return state;
        }

        state.link_up = true;
        if (!(*bmsr & bmsr_bits::AutoNegDone)) {
            state.speed = Speed::Unknown;
            return state;
        }

        auto gbcr = read_register(Register::Gbcr).value_or(0);
        auto gbsr = read_register(Register::Gbsr).value_or(0);
        auto anar = read_register(Register::Anar).value_or(0);
        auto anlpar = read_register(Register::Anlpar).value_or(0);

        // Вибір за пріоритетом IEEE 802.3
        if ((gbcr & gb_bits::Adv1000Full) && (gbsr & gb_bits::Lp1000Full)) {
            state.speed = Speed::Mbps1000;
            state.duplex = Duplex::Full;
        } else if ((gbcr & gb_bits::Adv1000Half) && (gbsr & gb_bits::Lp1000Half)) {
            state.speed = Speed::Mbps1000;
            state.duplex = Duplex::Half;
        } else if ((anar & anar_bits::Adv100Full) && (anlpar & anar_bits::Adv100Full)) {
            state.speed = Speed::Mbps100;
            state.duplex = Duplex::Full;
        } else if ((anar & anar_bits::Adv100Half) && (anlpar & anar_bits::Adv100Half)) {
            state.speed = Speed::Mbps100;
            state.duplex = Duplex::Half;
        } else if ((anar & anar_bits::Adv10Full) && (anlpar & anar_bits::Adv10Full)) {
            state.speed = Speed::Mbps10;
            state.duplex = Duplex::Full;
        } else if ((anar & anar_bits::Adv10Half) && (anlpar & anar_bits::Adv10Half)) {
            state.speed = Speed::Mbps10;
            state.duplex = Duplex::Half;
        }

        bool loc_sym  = (anar & anar_bits::PauseSym) != 0;
        bool loc_asym = (anar & anar_bits::PauseAsym) != 0;
        bool lp_sym   = (anlpar & anar_bits::PauseSym) != 0;
        bool lp_asym  = (anlpar & anar_bits::PauseAsym) != 0;

        if (loc_sym && lp_sym) {
            state.pause_rx = true;
            state.pause_tx = true;
        } else if (loc_asym && lp_sym && lp_asym) {
            state.pause_rx = true;
            state.pause_tx = false;
        } else if (loc_sym && loc_asym && lp_asym) {
            state.pause_rx = false;
            state.pause_tx = true;
        }

        return state;
    }

    /* Непрямий доступ до регістрів Clause 45 (MMD) */
    std::expected<uint16_t, DriverError> read_mmd(uint8_t dev_addr, uint16_t reg_addr) {
        // Крок 1: вибір адреси пристрою
        if (!write_register(Register::MmdAcr, dev_addr & 0x1F)) return std::unexpected(DriverError::BusError);
        // Крок 2: встановлення цільової адреси
        if (!write_register(Register::MmdAadr, reg_addr)) return std::unexpected(DriverError::BusError);
        // Крок 3: перехід у режим читання даних без автоінкременту (біти 15:14 = 01b)
        if (!write_register(Register::MmdAcr, (1U << 14) | (dev_addr & 0x1F))) return std::unexpected(DriverError::BusError);
        // Крок 4: безпосереднє читання даних
        return read_register(Register::MmdAadr);
    }

    std::expected<void, DriverError> write_mmd(uint8_t dev_addr, uint16_t reg_addr, uint16_t val) {
        if (!write_register(Register::MmdAcr, dev_addr & 0x1F)) return std::unexpected(DriverError::BusError);
        if (!write_register(Register::MmdAadr, reg_addr)) return std::unexpected(DriverError::BusError);
        if (!write_register(Register::MmdAcr, (1U << 14) | (dev_addr & 0x1F))) return std::unexpected(DriverError::BusError);
        return write_register(Register::MmdAadr, val);
    }

private:
    void clock_cycle() {
        gpio_.set_mdc(false);
        gpio_.delay_half_period();
        gpio_.set_mdc(true);
        gpio_.delay_half_period();
    }

    void send_bits(uint32_t val, uint8_t count) {
        for (int8_t i = count - 1; i >= 0; --i) {
            gpio_.set_mdc(false);
            gpio_.set_mdio_data((val >> i) & 1U);
            gpio_.delay_half_period();
            gpio_.set_mdc(true);
            gpio_.delay_half_period();
        }
    }

    void send_preamble() {
        gpio_.set_mdio_direction_out(true);
        gpio_.set_mdio_data(true);
        for (int i = 0; i < 32; ++i) {
            clock_cycle();
        }
    }

    Gpio gpio_;
    uint8_t phy_addr_;
};

} // namespace net::phy
```
:::

## 4. Інтеграція з MAC-контролером після розв'язання лінка

Узгодження параметрів між PHY та віддаленим комутатором є лише половиною завдання: контролер MAC не має прямого зв'язку з кабелем і не знає, на якій швидкості запрацював аналоговий тракт. Тому після того, як драйвер PHY зафіксував `AN_COMPLETE` та обчислив переможний режим, він зобов'язаний негайно оновити конфігурацію локального блоку MAC:

1. **Перемикання тактового генератора передавача**:
   * Для **1000BASE-T** (RGMII): тактова лінія `TXC` повинна тактуватися частотою **125.0 МГц** (з подвоєною вибіркою DDR), а внутрішня шина DMA переводиться в режим обробки 1 Гбіт/с;
   * Для **100BASE-TX**: `TXC` перемикається на **25.0 МГц** (для MII) або `REF_CLK` залишається 50.0 МГц (для RMII) з відліком 2 бітів за такт;
   * Для **10BASE-T**: тактова лінія перемикається на **2.5 МГц** (або у режимі RMII вмикається дільник вибірки `1:10`).
2. **Конфігурація дуплексу в блоці MAC**:
   * У повнодуплексному режимі (`Full Duplex`) контролер MAC повністю вимикає логіку перевірки колізій (ігнорує сигнали `CRS` та `COL`), дозволяючи передавачеві відправляти кадри навіть під час безперервного надходження вхідних пакетів;
   * У напівдуплексному режимі (`Half Duplex`) MAC вмикає таймер затримки колізій (Slot Time = 512 бітових інтервалів для 10/100M або 4096 бітів для 1000M з механізмом Carrier Extension) та автомат генерації сигналу Jamming і повторних спроб (Truncated Binary Exponential Backoff).
3. **Керування паузами передавача (Flow Control)**:
   * Якщо узгоджено `pause_tx = true`, MAC отримує дозвіл надсилати контрольні кадри PAUSE (Opcode `0x0001` на мультикаст-адресу `01:80:C2:00:00:01`) у разі переповнення внутрішніх апаратних FIFO-буферів прийому;
   * Якщо узгоджено `pause_rx = true`, апаратний парсер MAC при отриманні вхідного кадру PAUSE тимчасово зупиняє передачу нових кадрів із черги DMA на вказану в кадрі кількість квантів часу.

## 5. Діагностика якості лінії та рефлектометрія кабелю (TDR)

Сучасні трансивери PHY містять апаратні засоби безперервного контролю фізичного стану кабелю:

* **Моніторинг помилок очікування (Idle Error Count)**:
  Регістр `0x0A` (GBSR) містить 8-бітовий лічильник `Idle Error Count` (біти `[7:0]`). Під час відсутності корисного трафіку гігабітний трансивер передає безперервний потік символів IDLE PAM-5. Якщо шум, перехресні наводки або температурний дрейф викликають помилки дискримінатора АЦП, лічильник зростає. Періодичне зчитування цього регістра дозволяє драйверу виявити деградацію лінії задовго до повного розриву зв'язку.
* **Рефлектометрія часової області (TDR — Time Domain Reflectometry)**:
  Більшість мікросхем (наприклад, Microchip KSZ9031 через регістр MMD 0x1C або Realtek RTL8211 через vendor-регістри) дозволяють виконати тестування кабелю при відключеному лінку. PHY генерує в кожну пару короткий зондувальний імпульс напруги і вимірює час до приходу відбитого сигналу. Якщо пара обірвана, відбитий імпульс повертається з тією самою полярністю (коефіцієнт відбиття `+1`); якщо замкнена накоротко — з протилежною полярністю (`−1`). Знаючи швидкість поширення сигналу в кабелі (Nominal Velocity of Propagation, для Cat5e `NVP ≈ 0.69·c ≈ 2.07·10⁸ м/с`), драйвер обчислює точну відстань до місця пошкодження кабелю з похибкою до 1 метра:

```general
L = (v · t) / 2
= (0.69 · 3·10⁸ м/с · t) / 2      [t — час затримки відлуння]
```

Окрім визначення довжини, TDR-аналізатор оцінює якість самого контакту за амплітудою відбиття (Return Loss). Якщо в роз'ємі виникло окиснення або неякісний обтиск, коефіцієнт відбиття набуває проміжних значень `0.2–0.5`. Драйвер може зчитати ці дані та завчасно попередити мережевого адміністратора про ризик деградації каналу до падіння швидкості з 1 Гбіт/с до 100 Мбіт/с. Додатково аналізується запас завадостійкості (Signal-to-Noise Ratio Margin): якщо рівень шуму від сусідніх пар наближається до порогу помилки декодера Вітербі, PHY фіксує передінфарктний стан каналу.

## 6. Переривання проти періодичного опитування (Interrupt vs Polling)

У вбудованих системах з високим навантаженням циклічне опитування шини MDIO кожні 50 мс витрачає процесорний час. Більшість трансиверів PHY мають вивід апаратного переривання `INT_N` (активний низький рівень з відкритим стоком).

Для переходу на подієву модель драйвер виконує такі налаштування:
1. Записує маску дозволених подій у специфічний регістр переривань PHY (наприклад, біти `Link Up`, `Link Down`, `Auto-Negotiation Complete`, `Parallel Detection Fault`);
2. Обробник переривання мікроконтролера за спадним фронтом на виводі `INT_N` виставляє прапорець або надсилає подію в чергу RTOS;
3. Потік завдань драйвера зчитує регістр статусу переривань PHY (що автоматично скидає лінію `INT_N` у високий рівень завдяки підтяжці) та одноразово викликає функцію `phy_poll_status()`.

Така архітектура скорочує навантаження на шину керування практично до нуля в стабільному стані зв'язку, миттєво реагуючи на підключення або від'єднання кабелю.

## 7. Автоматичне схрещування пар (Auto-MDI/MDI-X) та корекція полярності

Історично для з'єднання двох комп'ютерів безпосередньо вимагався спеціальний перехресний кабель (англ. *Crossover Cable*), де пара передавання `TX+/TX-` на одному кінці з'єднувалася з парою прийому `RX+/RX-` на іншому. Сучасні трансивери виконують цю операцію повністю автоматично за допомогою автомата станів **Auto-MDIX** (HP Auto-MDIX, стандартизовано в IEEE 802.3ab):

* Під час запуску автопогодження внутрішній комутатор PHY періодично міняє призначення контактів роз'єму (перемикаючи пари між прямим режимом MDI та схрещеним MDI-X);
* Щоб два з'єднані пристрої не перемикали свої пари синхронно (що призвело б до нескінченного циклу без виявлення сигналу), тривалість перебування в кожному режимі модулюється внутрішнім псевдовипадковим генератором (англ. *Linear Feedback Shift Register*, LFSR);
* Як тільки приймач детектує на своїх вхідних виводах валідні імпульси FLP або NLP, комутатор фіксує поточну конфігурацію пар до наступного розриву лінка.

Аналогічно, цифровий сигнальний процесор (DSP) приймача виявляє перевернуту полярність окремих жил усередині пари (якщо монтажник переплутав смугасту й суцільну жилу, інвертувавши знак напруги). DSP визначає знак за початковими імпульсами синхронізації та програмно інвертує знак відліків АЦП перед декодуванням, усуваючи потребу в ручному ремонті роз'єму.

## 8. Енергоефективний Ethernet (EEE, IEEE 802.3az) та режим Low Power Idle

У гігабітних мережах трансивери PHY споживають значну потужність (близько 0.5–1.0 Вт на порт), навіть коли мережею не передається жодного байта даних, оскільки лінія безперервно заповнюється символами IDLE PAM-5 для підтримки роботи еквалайзерів і PLL.

Стандарт **Energy Efficient Ethernet** (EEE) дозволяє знизити споживання до 90% під час пауз у трафіку:
1. Під час автопогодження вузли перевіряють взаємну підтримку EEE через непрямі регістри Clause 45: `MMD 7, Reg 60` (EEE Advertisement) та `MMD 7, Reg 61` (EEE Link Partner Ability);
2. Якщо обидва кінці підтримують EEE, за відсутності кадрів MAC-контролер подає сигнал переходу в режим **LPI** (англ. *Low Power Idle*, спеціальний кодовий символ на шині MII/RGMII);
3. PHY вимикає більшу частину своїх аналогових передавачів, ЦАП і підсилювачів, переходячи в «сплячий» режим;
4. Для запобігання розсинхронізації схем ехокомпенсації та PLL PHY періодично прокидається на короткий інтервал (англ. *Refresh Period*, близько 20–24 мкс кожні кілька мілісекунд), передаючи короткий тестовий спалах;
5. Коли в черзі MAC з'являється новий кадр, PHY виходить зі сну за час пробудження (англ. *Wake Time*, близько 16–30 мкс для 1000BASE-T) і негайно відновлює передавання.

## 9. Архітектура підсистеми Phylib в операційній системі Linux

В операційних системах сімейства Linux керування фізичним рівнем повністю винесено в стандартизовану підсистему ядра — **phylib** та **phylink**. Це звільняє авторів драйверів мережевих карт від необхідності писати власний код опитування регістрів:

* Драйвер контролера MAC реєструє структуру шини MDIO `struct mii_bus` з функціями читання та запису (`read`, `write`);
* Ядро виконує сканування шини за адресами 0..31, зчитує `PHYID1`/`PHYID2` та зіставляє їх із базою зареєстрованих драйверів трансиверів `struct phy_driver`;
* Драйвер мережевого адаптера підключається до виявленого PHY функцією `phy_connect()` або `phylink_connect_phy()`, передаючи вказівник на функцію зворотного виклику `adjust_link()`;
* Внутрішній автомат станів ядра `phy_state_machine()` бере на себе періодичне опитування `BMSR`, обробку переривань, скидання пристрою та обчислення фінальної швидкості. Щоразу, коли стан лінка змінюється, ядро викликає функцію `adjust_link()`, де мережева карта підлаштовує параметри свого внутрішнього блоку MAC.

В описі апаратної конфігурації платформи (Device Tree) зв'язок між MAC і PHY описується декларативними вузлами:

```dts
&gmac0 {
    phy-mode = "rgmii-id";
    phy-handle = <&phy0>;
    status = "okay";

    mdio {
        #address-cells = <1>;
        #size-cells = <0>;

        phy0: ethernet-phy@1 {
            reg = <1>;
            rxc-skew-ps = <2000>;
            txc-skew-ps = <2000>;
        };
    };
};
```

Такий підхід забезпечує абсолютну переносимість мережевого коду: один і той самий контролер MAC може прозоро працювати з десятками різних моделей трансиверів Fast, Gigabit чи 10-Gigabit Ethernet без жодних змін у вихідному коді драйвера.
