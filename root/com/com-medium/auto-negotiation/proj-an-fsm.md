# ⚙️ Програмне опитування PHY та кінцевий автомат автопогодження

Автоматичне погодження параметрів фізичного рівня в Ethernet-контролерах потребує чіткої програмної взаємодії між мережевим стеком операційної системи (або прошивкою мікроконтролера) та мікросхемою трансивера PHY через послідовну шину MDIO. Кінцевий автомат (FSM) драйвера повинен ініціалізувати перезапуск процедури автопогодження, відстежувати часові інтервали (таймаути), коректно обробляти збої конфігурації Master/Slave у гігабітних режимах, розв'язувати найвищий спільний пріоритет технологій та вчасно сигналізувати про небезпеку виникнення асиметрії дуплексу (Duplex Mismatch).

Нижче наведено практичну реалізацію кінцевого автомата конфігурації, опитування та розв'язання параметрів лінка мовами C та ідіоматичним C++20, а також детальний розбір взаємодії з апаратною шиною MDIO, низькорівневого протоколу біт-бенгінгу, покрокового часового простеження переговорів, архітектури мережевої підсистеми ядра Linux та інтерфейсів користувацького простору ioctl і Netlink.

## 1. Архітектура та стани кінцевого автомата

Програмний кінцевий автомат керування лінком PHY оперує п'ятьма базовими станами:

```general
[ Скидання (RESET) ] ───► [ Ініціалізація та оголошення (ADVERTISE) ]
                                      │
                                      ▼
                            [ Очікування (POLLING) ] ◄──┐ (Таймаут або втрата лінка)
                                      │                 │
                         (AN Complete && Link Up)       │
                                      ▼                 │
                          [ Розв'язання (RESOLVE) ]     │
                                      │                 │
                         (Успіх арбітражу технологій)   │
                                      ▼                 │
                           [ Зв'язок піднято (UP) ] ────┘
```

1. **RESET (Скидання)**: Програмне скидання чипа PHY через біт `BMCR.15`, очікування апаратного самоочищення біта скидання (тривалість до 500 мс);
2. **ADVERTISE (Оголошення)**: Запис масок підтримуваних режимів у регістри `ANAR` (0x04) та `1000BASE-T Control` (0x09), примусовий перезапуск переговорів через біти `BMCR.12` (AN Enable) та `BMCR.9` (Restart AN);
3. **POLLING (Опитування)**: Періодичне зчитування регістру статусу `BMSR` (0x01) з контролем таймауту (зазвичай від 2.5 до 3.5 секунди за специфікацією IEEE 802.3);
4. **RESOLVE (Розв'язання)**: Зчитування регістрів `ANLPAR` (0x05), `1000BASE-T Status` (0x0A) та `ANER` (0x06), виконання алгоритму Technology Priority Resolution, перевірка конфлікту Master/Slave та виявлення Duplex Mismatch;
5. **UP (Зв'язок активний)**: Передача узгоджених параметрів (швидкість, дуплекс, конфігурація тактування MAC) у конфігураційні регістри мережевого контролера MAC та запуск передавання мережевих кадрів.

## 2. Реалізація драйвера автопогодження

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Базові адреси регістрів MII (IEEE 802.3 Clause 22) */
#define MII_BMCR            0x00
#define MII_BMSR            0x01
#define MII_ANAR            0x04
#define MII_ANLPAR          0x05
#define MII_ANER            0x06
#define MII_1000CR          0x09
#define MII_1000SR          0x0A

/* Бітові маски BMCR (Регістр 0) */
#define BMCR_RESET          (1u << 15)
#define BMCR_AN_ENABLE      (1u << 12)
#define BMCR_RESTART_AN     (1u << 9)

/* Бітові маски BMSR (Регістр 1) */
#define BMSR_AN_COMPLETE    (1u << 5)
#define BMSR_LINK_STATUS    (1u << 2)

/* Бітові маски ANAR / ANLPAR (Регістри 4 та 5) */
#define ADVERTISE_10HALF    (1u << 5)
#define ADVERTISE_10FULL    (1u << 6)
#define ADVERTISE_100HALF   (1u << 7)
#define ADVERTISE_100FULL   (1u << 8)
#define ADVERTISE_PAUSE     (1u << 10)
#define ADVERTISE_ASYM_PAUSE (1u << 11)

/* Бітові маски 1000CR / 1000SR (Регістри 9 та 10) */
#define ADVERTISE_1000HALF  (1u << 8)
#define ADVERTISE_1000FULL  (1u << 9)
#define STATUS_1000HALF     (1u << 10)
#define STATUS_1000FULL     (1u << 11)
#define STATUS_MS_FAULT     (1u << 15)
#define STATUS_MS_RESULT    (1u << 14) /* 1 = Master, 0 = Slave */

/* Бітові маски ANER (Регістр 6) */
#define ANER_LP_AN_ABLE     (1u << 0)
#define ANER_PAGE_RX        (1u << 1)

typedef enum {
    SPEED_UNKNOWN = 0,
    SPEED_10MBPS  = 10,
    SPEED_100MBPS = 100,
    SPEED_1000MBPS = 1000
} eth_speed_t;

typedef enum {
    DUPLEX_HALF = 0,
    DUPLEX_FULL = 1
} eth_duplex_t;

typedef enum {
    CLOCK_SLAVE = 0,
    CLOCK_MASTER = 1
} eth_clock_role_t;

typedef struct {
    eth_speed_t speed;
    eth_duplex_t duplex;
    eth_clock_role_t clock_role;
    bool pause_tx;
    bool pause_rx;
    bool parallel_detection_used;
    bool duplex_mismatch_warning;
} eth_link_result_t;

/* Прототипи апаратного доступу до шини MDIO */
uint16_t mdio_read(uint8_t phy_addr, uint8_t reg_addr);
void mdio_write(uint8_t phy_addr, uint8_t reg_addr, uint16_t val);
void delay_ms(uint32_t ms);

/* Ініціалізація та перезапуск переговорів */
bool phy_start_auto_negotiation(uint8_t phy_addr) {
    /* 1. Налаштовуємо рекламовані можливості (10/100M + PAUSE) */
    uint16_t anar = ADVERTISE_10HALF | ADVERTISE_10FULL |
                    ADVERTISE_100HALF | ADVERTISE_100FULL |
                    ADVERTISE_PAUSE | ADVERTISE_ASYM_PAUSE | 0x0001; /* 802.3 Selector */
    mdio_write(phy_addr, MII_ANAR, anar);

    /* 2. Налаштовуємо гігабітні можливості (1000BASE-T Full) */
    uint16_t gcr = ADVERTISE_1000FULL;
    mdio_write(phy_addr, MII_1000CR, gcr);

    /* 3. Увімкнення та примусовий перезапуск Auto-Negotiation */
    uint16_t bmcr = mdio_read(phy_addr, MII_BMCR);
    bmcr |= (BMCR_AN_ENABLE | BMCR_RESTART_AN);
    mdio_write(phy_addr, MII_BMCR, bmcr);

    return true;
}

/* Опитування завершення та арбітраж результату */
bool phy_poll_and_resolve(uint8_t phy_addr, uint32_t timeout_ms, eth_link_result_t *out_res) {
    uint32_t elapsed = 0;
    bool an_complete = false;

    while (elapsed < timeout_ms) {
        uint16_t bmsr = mdio_read(phy_addr, MII_BMSR);
        
        /* Читаємо повторно для скидання засувки Latching Low */
        if (bmsr & BMSR_LINK_STATUS) {
            bmsr = mdio_read(phy_addr, MII_BMSR);
            if ((bmsr & BMSR_LINK_STATUS) && (bmsr & BMSR_AN_COMPLETE)) {
                an_complete = true;
                break;
            }
        }
        delay_ms(50);
        elapsed += 50;
    }

    if (!an_complete) {
        return false; /* Таймаут переговорів або відсутній фізичний сигнал */
    }

    /* Зчитуємо результати обміну */
    uint16_t anlpar = mdio_read(phy_addr, MII_ANLPAR);
    uint16_t aner   = mdio_read(phy_addr, MII_ANER);
    uint16_t gsr    = mdio_read(phy_addr, MII_1000SR);
    uint16_t gcr    = mdio_read(phy_addr, MII_1000CR);
    uint16_t anar   = mdio_read(phy_addr, MII_ANAR);

    /* Перевірка помилки конфігурації Master/Slave */
    if (gsr & STATUS_MS_FAULT) {
        return false; /* Конфлікт тактування Master/Slave */
    }

    out_res->parallel_detection_used = !(aner & ANER_LP_AN_ABLE);
    out_res->duplex_mismatch_warning = false;

    /* Пріоритет 1: 1000BASE-T Full-Duplex */
    if ((gcr & ADVERTISE_1000FULL) && (gsr & STATUS_1000FULL)) {
        out_res->speed = SPEED_1000MBPS;
        out_res->duplex = DUPLEX_FULL;
        out_res->clock_role = (gsr & STATUS_MS_RESULT) ? CLOCK_MASTER : CLOCK_SLAVE;
    }
    /* Пріоритет 2: 1000BASE-T Half-Duplex */
    else if ((gcr & ADVERTISE_1000HALF) && (gsr & STATUS_1000HALF)) {
        out_res->speed = SPEED_1000MBPS;
        out_res->duplex = DUPLEX_HALF;
        out_res->clock_role = (gsr & STATUS_MS_RESULT) ? CLOCK_MASTER : CLOCK_SLAVE;
    }
    /* Пріоритет 3: 100BASE-TX Full-Duplex */
    else if ((anar & ADVERTISE_100FULL) && (anlpar & ADVERTISE_100FULL)) {
        out_res->speed = SPEED_100MBPS;
        out_res->duplex = DUPLEX_FULL;
    }
    /* Пріоритет 4: 100BASE-TX Half-Duplex */
    else if ((anar & ADVERTISE_100HALF) && (anlpar & ADVERTISE_100HALF)) {
        out_res->speed = SPEED_100MBPS;
        out_res->duplex = DUPLEX_HALF;
        if (out_res->parallel_detection_used) {
            out_res->duplex_mismatch_warning = true;
        }
    }
    /* Пріоритет 5: 10BASE-T Full-Duplex */
    else if ((anar & ADVERTISE_10FULL) && (anlpar & ADVERTISE_10FULL)) {
        out_res->speed = SPEED_10MBPS;
        out_res->duplex = DUPLEX_FULL;
    }
    /* Пріоритет 6: 10BASE-T Half-Duplex */
    else if ((anar & ADVERTISE_10HALF) && (anlpar & ADVERTISE_10HALF)) {
        out_res->speed = SPEED_10MBPS;
        out_res->duplex = DUPLEX_HALF;
        if (out_res->parallel_detection_used) {
            out_res->duplex_mismatch_warning = true;
        }
    } else {
        return false; /* Немає спільних режимів */
    }

    /* Розв'язання симетричного/асиметричного керування потоком PAUSE */
    bool loc_pause = (anar & ADVERTISE_PAUSE) != 0;
    bool loc_asym  = (anar & ADVERTISE_ASYM_PAUSE) != 0;
    bool rem_pause = (anlpar & ADVERTISE_PAUSE) != 0;
    bool rem_asym  = (anlpar & ADVERTISE_ASYM_PAUSE) != 0;

    out_res->pause_tx = (loc_pause && rem_pause) || (loc_asym && rem_pause && rem_asym);
    out_res->pause_rx = (loc_pause && rem_pause) || (loc_pause && loc_asym && rem_asym);

    return true;
}
```
```cpp
#include <cstdint>
#include <chrono>
#include <thread>
#include <expected>
#include <span>

namespace net::phy {

enum class Speed : std::uint16_t {
    Unknown = 0,
    Speed10M = 10,
    Speed100M = 100,
    Speed1000M = 1000
};

enum class Duplex : std::uint8_t {
    Half = 0,
    Full = 1
};

enum class ClockRole : std::uint8_t {
    Slave = 0,
    Master = 1
};

enum class NegotiationError : std::uint8_t {
    HardwareTimeout,
    MasterSlaveFault,
    NoCommonTechnology,
    LinkDown
};

struct LinkProperties {
    Speed speed{Speed::Unknown};
    Duplex duplex{Duplex::Half};
    ClockRole clock_role{ClockRole::Slave};
    bool pause_tx{false};
    bool pause_rx{false};
    bool parallel_detection_used{false};
    bool duplex_mismatch_warning{false};
};

/* Абстрактний апаратний інтерфейс шини керування MDIO */
class IMdioBus {
public:
    virtual ~IMdioBus() = default;
    [[nodiscard]] virtual auto read(std::uint8_t phy_addr, std::uint8_t reg_addr) -> std::uint16_t = 0;
    virtual void write(std::uint8_t phy_addr, std::uint8_t reg_addr, std::uint16_t value) = 0;
};

class AutoNegotiationEngine {
public:
    explicit constexpr AutoNegotiationEngine(IMdioBus& bus, std::uint8_t phy_addr) noexcept
        : bus_{bus}, phy_addr_{phy_addr} {}

    auto restart() -> void {
        constexpr std::uint16_t anar_val = 0x0DE1; // 10/100 Full/Half + PAUSE + IEEE 802.3
        bus_.write(phy_addr_, 0x04, anar_val);

        constexpr std::uint16_t gcr_val = 0x0200;  // 1000BASE-T Full-Duplex
        bus_.write(phy_addr_, 0x09, gcr_val);

        std::uint16_t bmcr = bus_.read(phy_addr_, 0x00);
        bmcr |= (1u << 12) | (1u << 9); // AN Enable | Restart AN
        bus_.write(phy_addr_, 0x00, bmcr);
    }

    [[nodiscard]] auto poll_and_resolve(std::chrono::milliseconds timeout)
        -> std::expected<LinkProperties, NegotiationError> {
        
        const auto deadline = std::chrono::steady_clock::now() + timeout;
        bool ready = false;

        while (std::chrono::steady_clock::now() < deadline) {
            std::uint16_t bmsr = bus_.read(phy_addr_, 0x01);
            if (bmsr & (1u << 2)) { // Link status
                bmsr = bus_.read(phy_addr_, 0x01); // Скидання Latching Low
                if ((bmsr & (1u << 2)) && (bmsr & (1u << 5))) { // Link Up + AN Complete
                    ready = true;
                    break;
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }

        if (!ready) {
            return std::unexpected(NegotiationError::HardwareTimeout);
        }

        const auto anlpar = bus_.read(phy_addr_, 0x05);
        const auto aner   = bus_.read(phy_addr_, 0x06);
        const auto gsr    = bus_.read(phy_addr_, 0x0A);
        const auto gcr    = bus_.read(phy_addr_, 0x09);
        const auto anar   = bus_.read(phy_addr_, 0x04);

        if (gsr & (1u << 15)) { // Master/Slave Configuration Fault
            return std::unexpected(NegotiationError::MasterSlaveFault);
        }

        LinkProperties result{};
        result.parallel_detection_used = !(aner & 0x0001);

        // Арбітраж пріоритетів IEEE 802.3
        if ((gcr & (1u << 9)) && (gsr & (1u << 11))) {
            result.speed = Speed::Speed1000M;
            result.duplex = Duplex::Full;
            result.clock_role = (gsr & (1u << 14)) ? ClockRole::Master : ClockRole::Slave;
        } else if ((gcr & (1u << 8)) && (gsr & (1u << 10))) {
            result.speed = Speed::Speed1000M;
            result.duplex = Duplex::Half;
            result.clock_role = (gsr & (1u << 14)) ? ClockRole::Master : ClockRole::Slave;
        } else if ((anar & (1u << 8)) && (anlpar & (1u << 8))) {
            result.speed = Speed::Speed100M;
            result.duplex = Duplex::Full;
        } else if ((anar & (1u << 7)) && (anlpar & (1u << 7))) {
            result.speed = Speed::Speed100M;
            result.duplex = Duplex::Half;
            result.duplex_mismatch_warning = result.parallel_detection_used;
        } else if ((anar & (1u << 6)) && (anlpar & (1u << 6))) {
            result.speed = Speed::Speed10M;
            result.duplex = Duplex::Full;
        } else if ((anar & (1u << 5)) && (anlpar & (1u << 5))) {
            result.speed = Speed::Speed10M;
            result.duplex = Duplex::Half;
            result.duplex_mismatch_warning = result.parallel_detection_used;
        } else {
            return std::unexpected(NegotiationError::NoCommonTechnology);
        }

        const bool loc_p  = (anar & (1u << 10)) != 0;
        const bool loc_ap = (anar & (1u << 11)) != 0;
        const bool rem_p  = (anlpar & (1u << 10)) != 0;
        const bool rem_ap = (anlpar & (1u << 11)) != 0;

        result.pause_tx = (loc_p && rem_pause) || (loc_asym && rem_pause && rem_asym);
        result.pause_rx = (loc_p && rem_pause) || (loc_p && loc_asym && rem_asym);

        return result;
    }

private:
    IMdioBus& bus_;
    std::uint8_t phy_addr_;
};

} // namespace net::phy
```
:::

## 3. Детальний аналіз критичних крайових випадків у драйвері

Робота з фізичним рівнем відрізняється від високорівневого програмування наявністю неперервних аналогових процесів, десинхронізації кварцових генераторів та механічних шумів під час комутації кабелю. Надійний драйвер зобов'язаний коректно ізолювати операційну систему від апаратних збоїв на лінії.

### 1. Дворегістрове опитування та засувки Latching Low (LL)

Однією з найпоширеніших помилок у початкових реалізаціях драйверів є одноразове читання регістру `BMSR` (0x01). Біт `Link Status` (1.2) володіє апаратною властивістю засувки до зчитування (Latching Low):
* Якщо під час роботи кабелю виникла мікроскопічна втрата контакту або наводка тривалістю 10 мікросекунд, біт `1.2` скидається в `0`;
* Внутрішній фазовий автопідлаштовувач (PLL) приймача миттєво відновлює синхронізацію, і на рівні фізичного сигналу зв'язок стабільний;
* Проте біт `1.2` залишатиметься в стані `0` аж до першого звернення по шині MDIO.

Якщо драйвер читає регістр лише один раз, він сприйме застарілу історію аварії за поточний стан лінії і помилково заявить стеку TCP/IP про падіння лінка. Правильний алгоритм завжди робить **два послідовні зчитування**: перше скидає засувку LL, а друге повертає істинний стан аналогового компаратора в дану мілісекунду.

### 2. Діагностика Parallel Detection та попередження про Duplex Mismatch

Коли в регістрі `BMSR` піднято біт `AN_COMPLETE` (1.5), драйвер зобов'язаний звернутися до регістру `ANER` (0x06) і перевірити біт `ANER.0` (Link Partner Auto-Negotiation Able):
* Якщо `ANER.0 == 1`: партнер повноцінно обмінявся сторінками FLP, дуплексний режим узгоджено симетрично, колізії виключені;
* Якщо `ANER.0 == 0`: зв'язок піднято за допомогою паралельного детектування (Parallel Detection). Це означає, що віддалений пристрій є або застарілим концентратором 10/100, або портом комутатора з жорстко зафіксованими параметрами.

У випадку Parallel Detection драйвер примусово виставляє напівдуплекс (Half-Duplex) і зобов'язаний згенерувати системне попередження у журнал ядра (`dmesg` або syslog):
```text
eth0: Link is Up at 100Mbps Half-Duplex (Parallel Detection) - WARNING: Verify partner duplex setting to avoid Duplex Mismatch!
```
Без такого повідомлення системний адміністратор може тижнями шукати причину низької швидкості передавання файлів при зовні «зеленому» статусі інтерфейсу.

### 3. Обробка конфліктів тактування Master/Slave у 1000BASE-T

Якщо під час переговорів у регістрі `1000BASE-T Status` (0x0A) піднявся біт `STATUS_MS_FAULT` (10.15), це вказує на фатальний конфлікт:
1. Обидва кінці кабелю вручну налаштовані як `Manual Master` або обидва як `Manual Slave`;
2. Або пристрої однакового типу вичерпали ліміт апаратних спроб генерації 11-бітного псевдовипадкового Seed через систематичні колізії (вкрай рідкісна подія, яка вказує на апаратний дефект генератора псевдовипадкових чисел у чипі PHY).

Драйвер не повинен зависати в нескінченному очікуванні. При виявленні `MS_FAULT` алгоритм повинен:
* Скинути прапорці ручного вибору (`Reg 9.12 = 0`), перевівши PHY в повністю автоматичний вибір ролей;
* Якщо автоматичний режим не дає результату — тимчасово вимкнути рекламу 1000BASE-T у регістрі `1000CR` (Reg 9.9 = 0) і перезапустити переговори на резервній швидкості 100BASE-TX Full-Duplex, забезпечивши безперервність роботи мережі до втручання адміністратора.

### 4. Апаратне налаштування керування потоком PAUSE у контролері MAC

Після того, як функція `phy_poll_and_resolve()` повернула логічні прапорці `pause_tx` та `pause_rx`, драйвер зобов'язаний записати ці параметри безпосередньо у внутрішні керуючі регістри контролера **MAC**:
* Якщо `pause_rx == true`: контролер MAC повинен апаратно перехоплювати вхідні кадри з типом `0x8808` та кодом операції `0x0001` (PAUSE), витягувати з них 16-бітний квант часу і призупиняти передавач свого чергового буфера дескрипторів TX DMA;
* Якщо `pause_tx == true`: контролер MAC повинен моніторити рівень заповненості вхідного апаратного FIFO-буфера RX. Коли рівень сягає встановленої водяної позначки (High Watermark), MAC самостійно генерує та транслює у лінію кадр PAUSE на групову адресу `01:80:C2:00:00:01`.

## 4. Протокол шини MDIO та низькорівневий біт-бенгінг

Шина **MDIO/MDC** (Management Data Input/Output) стандартизована в IEEE 802.3 Clause 22 і є синхронною двопровідною шиною типу «ведучий–ведений» (Master-Slave), де контролер MAC виступає Master, а до 32 мікросхем PHY можуть бути підключені як Slave з унікальними 5-бітними апаратними адресами (`PHYAD[4:0]`).

### Структура кадру опитування Clause 22

Кожна операція читання або запису регістру передається у вигляді 32-бітного послідовного кадру:

```general
Поле:       [ PREAMBLE ]   [ ST ]   [ OP ]   [ PHYAD ]   [ REGAD ]   [ TA ]   [ DATA ]
Розрядність:  32 біти       2 біти   2 біти    5 бітів     5 бітів    2 біти   16 бітів
Значення:   1111...1111       01     10 (RD)   00000..     00000..    Z0 (RD)  D15..D0
                                     01 (WR)   11111       11111      10 (WR)
```

1. **PREAMBLE (Преамбула, 32 біти)**: Послідовність із 32 логічних одиниць, що передається по лінії MDIO при активному тактуванні MDC для синхронізації внутрішнього автомата PHY;
2. **ST (Start of Frame, 2 біти)**: Початкова комбінація, яка для Clause 22 строго дорівнює `01`b (у Clause 45 використовується `00`b);
3. **OP (Operation Code, 2 біти)**: Код операції: `10`b — читання (Read), `01`b — запис (Write);
4. **PHYAD (PHY Address, 5 бітів)**: Апаратна адреса трансивера на платі (від `0` до `31`), що зазвичай задається апаратними підтяжками (Bootstrap resistors) на виводах конфігурації чипа;
5. **REGAD (Register Address, 5 бітів)**: Адреса одного з 32 регістрів (від `0x00` до `0x1F`);
6. **TA (Turnaround, 2 біти)**: Захисний часовий інтервал для перемикання напрямку передачі по двонаправленій лінії MDIO:
   * При записі MAC утримує лінію і передає біти `10`b;
   * При читанні MAC відпускає лінію у стан Hi-Z на першому такті, після чого PHY притискає її до нуля (`Z0`b), підтверджуючи готовність видати дані;
7. **DATA (Дані, 16 бітів)**: 16-розрядне значення, що записується в регістр або зчитується з нього, починаючи зі старшого біта `D15`.

### Часові обмеження та програмний біт-бенгінг

Максимальна тактова частота `MDC` за специфікацією становить **2.5 МГц**, що відповідає періоду такту `T_mdc = 400 нс`. Під час програмної реалізації протоколу на виводах загального призначення (GPIO) мікроконтролера розробник повинен суворо дотримуватися часових параметрів сигналу:

* **Час встановлення даних (Setup Time, `t_su >= 10 нс`)**: значення біта на лінії MDIO має бути виставлене та стабілізоване до появи висхідного фронту тактового сигналу MDC;
* **Час утримання даних (Hold Time, `t_h >= 10 нс`)**: стан лінії MDIO не повинен змінюватися протягом як мінімум 10 нс після висхідного фронту MDC;
* **Двонаправлений стан Hi-Z**: під час фази Turnaround при операції читання контролер зобов'язаний своєчасно перевести свій вивід GPIO у режим високоімпедансного входу (Input Float), щоб уникнути апаратного короткого замикання з вихідним каскадом PHY;
* **Апаратна адресація чипа (PHY Strapping)**: при старті живлення PHY фіксує рівні напруг на спеціальних ніжках конфігурації (наприклад, `LED0..LED2` або `RXD0..RXD2`). Якщо підтягувальні резистори розведено некоректно, чип може запуститися з несподіваною адресою `0x01` або `0x1F` замість очікуваної `0x00`. Драйвер повинен підтримувати автоматичне сканування адресного простору від 0 до 31 шляхом опитування регістру `PHYID1` (0x02).

## 5. Покрокове простеження реальної сесії переговорів (Live Trace)

Розглянемо реальну послідовність зміни регістрів трансивера під час підключення патч-корду між сервером 1000BASE-T (PHY Address 0) та гігабітним комутатором:

```general
Час (t)     Подія на лінії та реакція драйвера             Стан регістрів PHY
t = 0 мс    Встромлено кабель. Компаратор виявив напругу.  BMSR = 0x7849 (Link Down, AN Incomplete)
            Запуск початкової паузи Transmit Disable.     BMCR = 0x1140 (AN Enable)

t = 600 мс  Початок відправки пачок FLP (Ability Detect).  ANAR = 0x0DE1 (Реклама 10/100 Full/Half, PAUSE)
            PHY надсилає Base Page з бітом ACK = 0.       1000CR = 0x0200 (Реклама 1000 Full)

t = 750 мс  Прийнято 3 сторінки від комутатора.           ANER = 0x0007 (LP AN Able, Page Rx)
            Перехід до стану Acknowledge Detect.          ANLPAR = 0x4DE1 (LP підтвердив 10/100, ACK=1)

t = 900 мс  Обмін гігабітними сторінками Next Page.       1000SR = 0x4800 (LP 1000 Full Able)
            Генерація Seed_local = 1420, Seed_remote = 810. Вузол стає Master.

t = 1100 мс Запуск аналогових еквалайзерів PAM-5.         BMSR = 0x7869 (AN Complete, але Link ще Down)
            Збіжність DSP фільтрів відлуння та NEXT.      1000SR = 0x7800 (Local & Remote Rx OK, Master)

t = 1350 мс Апаратна синхронізація зафіксована.           BMSR = 0x786D (Link Up! AN Complete!)
            Драйвер читає BMSR двічі, виконує resolve.    Швидкість: 1000 Мбіт/с, Full-Duplex, Master.
```

Після моменту `t = 1350 мс` драйвер конфігурує внутрішній дільник інтерфейсу RGMII/GMII на частоту **125 МГц**, перемикає контролер MAC у повнодуплексний режим без генерації колізій і викликає функцію активації черги передавання операційної системи `netif_wake_queue()`.

## 6. Інтеграція в підсистему phylib ядра Linux та обробка переривань

У виробничих операційних системах періодичне опитування регістрів через затримки `sleep_for` у циклі неприпустиме, оскільки воно марнує процесорний час. Ядро Linux реалізує уніфіковану підсистему **phylib** (`drivers/net/phy/phy.c`), яка поєднує апаратні переривання від чипа PHY з чергами відкладеної обробки (Workqueues).

### Кінцевий автомат станів phylib у Linux

Підсистема ядра керує трансивером за допомогою розширеного графа станів:

```general
[ PHY_DOWN ] ──► [ PHY_STARTING ] ──► [ PHY_READY ] ──► [ PHY_UP ]
                                                            │
                                                            ▼
[ PHY_HALTED ] ◄── [ PHY_NOLINK ] ◄── [ PHY_RUNNING ] ◄── [ PHY_AN ]
```

1. **PHY_DOWN**: Інтерфейс вимкнено адміністратором (`ip link set dev eth0 down`). Живлення трансивера переведено в стан Power Down (`BMCR.11 = 1`);
2. **PHY_STARTING**: Команда підняття інтерфейсу (`ip link set dev eth0 up`). Виконується апаратне скидання PHY, конфігурація регістрів реклами `ANAR` та `1000CR`;
3. **PHY_AN**: Перевірка активності процесу переговорів. Драйвер очікує завершення автопогодження або апаратного сигналу переривання;
4. **PHY_RUNNING**: Лінк успішно піднято (`BMSR.2 = 1` та `BMSR.5 = 1`). Контролер MAC налаштовано на узгоджену швидкість та дуплекс, запущені черги передавання пакетів ядра (`netif_carrier_on()`);
5. **PHY_NOLINK**: Втрата фізичного зв'язку (кабель висмикнуто). Ядро зупиняє черги передавання (`netif_carrier_off()`), скидає таблиці маршрутизації та повертається в стан очікування лінка.

### Обробка апаратних переривань через лінію PHY_INT

Сучасні мікросхеми PHY мають спеціалізований вивід переривання `INT_N` (активний низький рівень), який підключається до окремої лінії GPIO мікроконтролера чи процесора.

Для активації переривань драйвер налаштовує вендор-специфічний регістр маски переривань (наприклад, `MICR` — Management Interrupt Control Register):
* Дозволяються переривання при зміні статусу лінка (Link Status Change), завершенні автопогодження (Auto-Negotiation Completed) та виникненні помилок Remote Fault;
* Коли відбувається подія на лінії, PHY опускає лінію `INT_N` до нуля;
* Обробник переривання процесора (Top-Half ISR) не виконує операцій на шині MDIO (оскільки транзакції MDIO повільні та блокуючі), а лише надсилає подію у фонову чергу робіт ядра (Bottom-Half Worker);
* Робочий потік ядра виконує читання регістру статусу переривань `MISR` (що автоматично скидає лінію `INT_N` у високий стан) і запускає функцію розв'язання параметрів `phy_poll_and_resolve()`.

Такий підхід забезпечує нульове завантаження центрального процесора під час спокою лінії та миттєву реакцію на підключення або відключення кабелю протягом мікросекунд.

## 7. Взаємодія з простором користувача через ioctl та Netlink

Системні утиліти адміністрування мережі (`ethtool`, `mii-diag`, `iproute2`) взаємодіють із драйвером PHY через стандартизовані системні виклики ядра Linux:

* **Класичний інтерфейс ioctl MII**:
  * `SIOCGMIIPHY`: отримання апаратної адреси PHY на шині MDIO;
  * `SIOCGMIIREG`: пряме зчитування 16-бітного значення регістру за вказаною адресою;
  * `SIOCSMIIREG`: прямий запис значення в регістр PHY (вимагає прав `CAP_NET_ADMIN`).
* **Сучасний інтерфейс Generic Netlink (ethtool netlink)**:
  * Повідомлення `ETHTOOL_MSG_LINKMODES_GET`: повертає бітові маски підтримуваних, рекламованих та прийнятих від партнера режимів зв'язку у вигляді 64-розрядних бітмапів;
  * Повідомлення `ETHTOOL_MSG_LINKMODES_SET`: передає нову маску рекламованих технологій при зміні параметрів командою:
    ```bash
    ethtool -s eth0 speed 1000 duplex full autoneg on
    ```

Коли утиліта `ethtool` надсилає запит на зміну параметрів, ядро блокує черги передавача, записує нові маски в регістри `ANAR` (Reg 4) та `1000CR` (Reg 9), після чого встановлює біт `BMCR.9` (Restart Auto-Negotiation), запускаючи новий цикл апаратного рукостискання.

## 8. Порівняльний аналіз архітектур на C та ідіоматичному C++

Реалізація драйвера на мові C та ідіоматичному C++20 демонструє два принципово різні інженерні підходи до керування низькорівневим залізом:

1. **Типобезпека та моделювання помилок**:
   * У версії на C статус операції передається через булевий результат `bool`, а деталі повертаються через покажчик на вихідну структуру. Помилка таймауту та конфлікт Master/Slave не розрізняються за типом поверненого значення;
   * У версії на C++ застосовано сумарний тип `std::expected<LinkProperties, NegotiationError>`. Це примушує компілятор контролювати обробку кожної можливої помилки (`HardwareTimeout`, `MasterSlaveFault`, `NoCommonTechnology`) ще на етапі збірки без використання винятків (`-fno-exceptions`);
   * Атрибут `[[nodiscard]]` гарантує, що результат виклику функції розв'язання не буде випадково проігнорований прикладним кодом, що запобігає прихованим багам у критичних системах.
2. **Детермінізм та нульова динамічна пам'ять (Zero-Allocation)**:
   * Обидві реалізації повністю уникають динамічного виділення пам'яті (`malloc`/`new`), що є обов'язковою вимогою стандартів функціональної безпеки **MISRA C / AUTOSAR C++** для автомобільних мереж Automotive Ethernet (100BASE-T1 / 1000BASE-T1);
   * Усі константи бітових масок у C++ визначені як `constexpr`, що дозволяє оптимізатору компілятора вбудовувати їх у машинні інструкції без виділення глобальних змінних у секції `.data` або `.rodata`. Компілятор генерує максимально компактний машинний код із нульовими накладними витратами часу виконання (Zero Runtime Overhead).
3. **Інкапсуляція апаратного інтерфейсу (RAII)**:
   * В C++ абстрактний клас `IMdioBus` дозволяє легко підміняти апаратний доступ до реальної шини MDIO на програмний емулятор-мокер під час unit-тестування кінцевого автомата на комп'ютері розробника без підключення реальної мікросхеми PHY. Обгортка шини може містити автоматичний м'ютекс блокування (`std::lock_guard`), що гарантує неподільність 32-бітних циклів читання-модифікації-запису в багатопотоковому середовищі RTOS. Завдяки принципу RAII захоплений м'ютекс гарантовано звільняється при виході з області видимості функції навіть у разі аварійного повернення через помилку таймауту.
