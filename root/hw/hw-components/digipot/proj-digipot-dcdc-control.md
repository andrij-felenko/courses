# ⚙️ Прецизійне калібрування DC-DC перетворювача через цифровий потенціометр

Цифрове підстроювання вихідної напруги імпульсного стабілізатора (DC-DC Buck/Boost) вимагає не просто відправлення байта по шині SPI або I2C, а суворого дотримання апаратних обмежень безпеки. Якщо мікроконтролер запише помилковий код, зависне під час ініціалізації або встановить опір нижче критичного порогу, напруга на виході перетворювача може перевищити допустимий максимум і миттєво знищити живлений процесор чи радіомодуль.

Тут реалізовано драйвер керування цифровим потенціометром (на базі типового 8-бітного чипа з SPI-інтерфейсом та пам'яттю EEPROM, на зразок MCP41010/AD5270), алгоритм безпечного розрахунку коду кроку з урахуванням опору ключа R_W, апаратні й програмні ліміти (soft clamps) та збереження калібрувального значення в енергонезалежну пам'ять.

## 1. Схемотехніка та розрахункова модель

Розглянемо імпульсний знижувальний перетворювач (Buck Converter) із опорною напругою зворотного зв'язку V_FB = 0.800 В. У звичайній фіксованій схемі вихідна напруга задається резистивним дільником:

```text
V_out = V_FB · (1 + R_top / R_bottom)
```

Для створення безпечного коридору регулювання цифровий потенціометр R_digi (номінал 10 кОм, 256 кроків) увімкнено як реостат послідовно з додатковим обмежувальним резистором R_s = 4.7 кОм, і ця гілка під'єднана паралельно до базового нижнього резистора R_2 = 10 кОм. Верхнє плече дільника утворене постійним прецизійним резистором R_1 = 33 кОм.

Сумарний опір нижнього плеча R_bottom(D) дорівнює паралельному з'єднанню R_2 та регульованої гілки (R_s + R_W + D · R_AB):

```text
R_branch(D) = R_s + R_W + (code / 255) · R_AB
R_bottom(D) = ( R_1 · R_branch(D) ) / ( R_2 + R_branch(D) )
```

У цій схемі навіть при повному обриві повзунка (коли опір гілки R_branch прямує до нескінченності) вихідна напруга перетворювача не перевищить верхню безпечну межу:

```text
V_out_max = 0.8 · (1 + 33 кОм / 10 кОм) = 0.8 · (1 + 3.3) = 3.44 В
```

А при нульовому коді (D = 0):

```text
R_branch_min = 4.7 кОм + 0.1 кОм + 0 = 4.8 кОм
R_bottom_min = (10 · 4.8) / (10 + 4.8) ≈ 3.243 кОм
V_out_min = 0.8 · (1 + 33 / 3.243) ≈ 3.344 В
```

### Чому обрано паралельне підмішування замість послідовного включення

У найпростіших аматорських схемах диджипот іноді ставлять послідовно з нижнім резистором дільника. Проте паралельне підмішування струму у вузол FB має вирішальні переваги:
- **Апаратний захист від обриву:** Якщо повзунок диджипота втратить контакт під час вібрації або перебуватиме у високоімпедансному стані під час скидання живлення, резистор R_2 гарантовано утримує вузол зворотного зв'язку на безпечному рівні. Вихідна напруга ні за яких обставин не злетить до вхідної напруги живлення.
- **Підвищення ефективної роздільної здатності:** Регулювання у вузькому вікні напруг (наприклад, 3.30–3.44 В) за допомогою 256 кроків дає крок дискретизації близько 0.5 мВ на крок. Якби диджипот регулював увесь діапазон від 0.8 В до 3.4 В, крок становив би понад 10 мВ.
- **Мінімізація впливу опору ключа R_W:** Оскільки резистор R_s (4.7 кОм) значно більший за опір ключа R_W (100 Ом), температурна нестабільність самого ключа (2000 ppm/°C) практично не впливає на стабільність вихідної напруги.

## 2. Реалізація драйвера та алгоритму керування

Програмний комплекс реалізує:
1. Модуль обчислення коду за цільовою напругою у мілівольтах із попередньою верифікацією діапазону.
2. Протокольний рівень SPI з формуванням контрольних байтів, прямим записом у леткий регістр повзунка (Wiper RAM) та фіксацією налаштування в енергонезалежній пам'яті (EEPROM).
3. Апаратну абстракцію інтерфейсу та безпечну роботу з лінією Chip Select через механізм RAII у версії C++.

:::tabs
@tab C
```c
#include <stdint.h>
#include <stdbool.h>

// Конфігурація апаратного вузла DC-DC та диджипота
#define DCDC_VFB_MV          800      // Опорна напруга FB, мВ (0.8 В)
#define DCDC_R1_OHM          33000    // Верхній резистор дільника, Ом
#define DCDC_R2_OHM          10000    // Базовий нижній резистор, Ом
#define DCDC_RS_OHM          4700     // Обмежувальний послідовний резистор, Ом

#define DIGIPOT_RAB_OHM      10000    // Повний номінал диджипота, Ом
#define DIGIPOT_RW_OHM       100      // Опір замкненого ключа повзунка, Ом
#define DIGIPOT_MAX_STEPS    255      // 8-бітний потенціометр (0..255)

// Команди керування (типовий протокол SPI)
#define CMD_WRITE_WIPER_RAM  0x00     // Запис у леткий регістр повзунка
#define CMD_WRITE_EEPROM     0x20     // Запис поточного значення в EEPROM
#define CMD_READ_WIPER       0x08     // Зчитування стану повзунка

typedef enum {
    DIGIPOT_OK = 0,
    DIGIPOT_ERR_VOLTAGE_OUT_OF_RANGE,
    DIGIPOT_ERR_HARDWARE_FAULT,
    DIGIPOT_ERR_TIMEOUT
} digipot_status_t;

// Апаратна абстракція SPI
typedef void (*spi_cs_func_t)(bool level);
typedef bool (*spi_transfer_func_t)(const uint8_t *tx, uint8_t *rx, uint16_t len);

typedef struct {
    spi_cs_func_t       set_cs;
    spi_transfer_func_t spi_xfer;
    uint8_t             current_code;
    uint16_t            min_safe_mv;
    uint16_t            max_safe_mv;
} digipot_t;

// Розрахунок вихідної напруги за кодом кроку (у мілівольтах)
uint16_t digipot_calculate_voltage(uint8_t code) {
    uint32_t r_branch = DCDC_RS_OHM + DIGIPOT_RW_OHM + 
                        ((uint32_t)code * DIGIPOT_RAB_OHM) / DIGIPOT_MAX_STEPS;
    
    // Паралельне з'єднання R2 та r_branch
    uint32_t r_bottom = (DCDC_R2_OHM * r_branch) / (DCDC_R2_OHM + r_branch);
    
    // V_out = V_FB * (1 + R1 / R_bottom)
    uint32_t v_out = DCDC_VFB_MV + (DCDC_VFB_MV * DCDC_R1_OHM) / r_bottom;
    return (uint16_t)v_out;
}

// Ініціалізація структури драйвера
digipot_status_t digipot_init(digipot_t *dev, spi_cs_func_t cs_fn, spi_transfer_func_t xfer_fn) {
    if (!dev || !cs_fn || !xfer_fn) {
        return DIGIPOT_ERR_HARDWARE_FAULT;
    }
    
    dev->set_cs = cs_fn;
    dev->spi_xfer = xfer_fn;
    dev->set_cs(true); // Деактивація CS (Active-Low)
    
    // Визначаємо фізично доступні межі напруг
    dev->min_safe_mv = digipot_calculate_voltage(DIGIPOT_MAX_STEPS);
    dev->max_safe_mv = digipot_calculate_voltage(0);
    dev->current_code = 128; // За замовчуванням mid-scale
    
    return DIGIPOT_OK;
}

// Прямий запис байта команди в диджипот по SPI
static digipot_status_t digipot_send_cmd(digipot_t *dev, uint8_t cmd, uint8_t data) {
    uint8_t tx_buf[2] = { cmd, data };
    uint8_t rx_buf[2] = { 0, 0 };
    
    dev->set_cs(false);
    bool ok = dev->spi_xfer(tx_buf, rx_buf, 2);
    dev->set_cs(true);
    
    if (!ok) {
        return DIGIPOT_ERR_HARDWARE_FAULT;
    }
    return DIGIPOT_OK;
}

// Встановлення точного коду кроку
digipot_status_t digipot_set_wiper_code(digipot_t *dev, uint8_t code) {
    digipot_status_t res = digipot_send_cmd(dev, CMD_WRITE_WIPER_RAM, code);
    if (res == DIGIPOT_OK) {
        dev->current_code = code;
    }
    return res;
}

// Встановлення бажаної вихідної напруги в мілівольтах
digipot_status_t digipot_set_target_voltage(digipot_t *dev, uint16_t target_mv) {
    if (target_mv < dev->min_safe_mv || target_mv > dev->max_safe_mv) {
        return DIGIPOT_ERR_VOLTAGE_OUT_OF_RANGE;
    }
    
    // Двійковий пошук оптимального коду кроку
    uint8_t best_code = 0;
    int32_t min_diff = 0x7FFFFFFF;
    
    for (int code = 0; code <= DIGIPOT_MAX_STEPS; code++) {
        uint16_t v = digipot_calculate_voltage((uint8_t)code);
        int32_t diff = (int32_t)v - (int32_t)target_mv;
        if (diff < 0) diff = -diff;
        
        if (diff < min_diff) {
            min_diff = diff;
            best_code = (uint8_t)code;
        }
    }
    
    return digipot_set_wiper_code(dev, best_code);
}

// Фіксація поточного положення повзунка в енергонезалежну пам'ять (EEPROM)
digipot_status_t digipot_save_to_eeprom(digipot_t *dev) {
    return digipot_send_cmd(dev, CMD_WRITE_EEPROM, dev->current_code);
}
```
@tab C++
```cpp
#include <cstdint>
#include <cstddef>
#include <concepts>
#include <expected>
#include <array>
#include <algorithm>
#include <cmath>

namespace dcdc_control {

// Конфігураційні константи вузла перетворювача
struct HardwareConfig {
    static constexpr uint32_t vfb_mv         = 800;    // Опора FB, мВ
    static constexpr uint32_t r1_top_ohm     = 33000;  // Верхнє плече, Ом
    static constexpr uint32_t r2_bottom_ohm  = 10000;  // Нижній базовий резистор, Ом
    static constexpr uint32_t rs_series_ohm  = 4700;   // Послідовний резистор захисту, Ом
    static constexpr uint32_t rab_digipot_ohm= 10000;  // Повний опір диджипота, Ом
    static constexpr uint32_t rw_wiper_ohm   = 100;    // Опір ключа, Ом
    static constexpr uint8_t  max_steps      = 255;    // Кількість кроків 8-біт
};

enum class Error : uint8_t {
    VoltageOutOfRange,
    HardwareFault,
    Timeout
};

// Концепт апаратного інтерфейсу SPI з RAII-керуванням лінією Chip Select
template <typename T>
concept SpiInterface = requires(T spi, const uint8_t* tx, uint8_t* rx, size_t len, bool cs) {
    { spi.set_cs(cs) } -> std::same_as<void>;
    { spi.transfer(tx, rx, len) } -> std::same_as<bool>;
};

template <SpiInterface Bus>
class SafeDigiPot {
public:
    explicit SafeDigiPot(Bus& bus) noexcept
        : bus_(bus), current_code_(128) {
        bus_.set_cs(true);
        min_safe_mv_ = calculate_voltage(HardwareConfig::max_steps);
        max_safe_mv_ = calculate_voltage(0);
    }

    // Обчислення напруги для довільного коду (constexpr)
    [[nodiscard]] static constexpr uint16_t calculate_voltage(uint8_t code) noexcept {
        const uint32_t r_branch = HardwareConfig::rs_series_ohm + 
                                  HardwareConfig::rw_wiper_ohm + 
                                  (static_cast<uint32_t>(code) * HardwareConfig::rab_digipot_ohm) / 
                                  HardwareConfig::max_steps;

        const uint32_t r_bottom = (HardwareConfig::r2_bottom_ohm * r_branch) / 
                                  (HardwareConfig::r2_bottom_ohm + r_branch);

        const uint32_t v_out = HardwareConfig::vfb_mv + 
                               (HardwareConfig::vfb_mv * HardwareConfig::r1_top_ohm) / r_bottom;

        return static_cast<uint16_t>(v_out);
    }

    // Встановлення коду повзунка
    [[nodiscard]] std::expected<void, Error> set_wiper_code(uint8_t code) noexcept {
        if (auto res = send_command(0x00, code); !res) {
            return std::unexpected(res.error());
        }
        current_code_ = code;
        return {};
    }

    // Встановлення цільової вихідної напруги
    [[nodiscard]] std::expected<uint16_t, Error> set_target_voltage(uint16_t target_mv) noexcept {
        if (target_mv < min_safe_mv_ || target_mv > max_safe_mv_) {
            return std::unexpected(Error::VoltageOutOfRange);
        }

        uint8_t best_code = 0;
        int32_t min_diff = 0x7FFFFFFF;

        for (uint16_t code = 0; code <= HardwareConfig::max_steps; ++code) {
            const uint16_t v = calculate_voltage(static_cast<uint8_t>(code));
            const int32_t diff = std::abs(static_cast<int32_t>(v) - static_cast<int32_t>(target_mv));
            if (diff < min_diff) {
                min_diff = diff;
                best_code = static_cast<uint8_t>(code);
            }
        }

        if (auto res = set_wiper_code(best_code); !res) {
            return std::unexpected(res.error());
        }

        return calculate_voltage(best_code);
    }

    // Збереження калібрувального значення в EEPROM
    [[nodiscard]] std::expected<void, Error> save_to_eeprom() noexcept {
        return send_command(0x20, current_code_);
    }

    [[nodiscard]] uint8_t current_code() const noexcept { return current_code_; }
    [[nodiscard]] uint16_t min_voltage_mv() const noexcept { return min_safe_mv_; }
    [[nodiscard]] uint16_t max_voltage_mv() const noexcept { return max_safe_mv_; }

private:
    Bus&     bus_;
    uint8_t  current_code_;
    uint16_t min_safe_mv_{0};
    uint16_t max_safe_mv_{0};

    [[nodiscard]] std::expected<void, Error> send_command(uint8_t cmd, uint8_t data) noexcept {
        struct CsGuard {
            Bus& b;
            CsGuard(Bus& bus) : b(bus) { b.set_cs(false); }
            ~CsGuard() { b.set_cs(true); }
        } guard(bus_);

        const std::array<uint8_t, 2> tx_buf{ cmd, data };
        std::array<uint8_t, 2> rx_buf{ 0, 0 };

        if (!bus_.transfer(tx_buf.data(), rx_buf.data(), tx_buf.size())) {
            return std::unexpected(Error::HardwareFault);
        }
        return {};
    }
};

} // namespace dcdc_control
```
:::

## 3. Практичні пастки під час запуску та прошивки

1. **Затримка запису в EEPROM (t_write):** Після команди `0x20` чип диджипота запускає внутрішній генератор високої напруги для перезапису комірок EEPROM. Цей процес триває від 5 до 20 мс. У цей інтервал чип не приймає нових команд по шині SPI. Спроба негайного надсилання наступного байта призведе до втрати зв'язку.
2. **Перехідний процес під час Power-On Reset:** При першій подачі живлення напруга V_DD диджипота зростає поступово. До завершення циклу POR внутрішні CMOS-ключі перебувають у високоімпедансному стані. Саме тому в схемі обов'язково присутній постійний резистор R_2: він забезпечує безпечну прив'язку вузла FB до землі, утримуючи перетворювач у штатному режимі до моменту готовності цифрової шини.
3. **Швидкість наростання напруги (Slew Rate):** Якщо мікроконтролер перемикає потенціометр із мінімального положення у максимальне за один крок, стрибок опору у вузлі FB викликає перехідний викид вихідної напруги імпульсного перетворювача через кінцевий час реакції петлі регулювання. Для плавного регулювання рекомендується змінювати код кроками з інтервалом 1–2 мс на крок.
4. **Компенсація петлі зворотного зв'язку:** Зміна еквівалентного опору дільника FB трохи змінює коефіцієнт передачі петлі регулювання перетворювача. Використання паралельного підмішування у вузькому вікні мінімізує зміну повного опору вузла FB, зберігаючи запас стійкості за фазою стабілізатора без необхідності перерахунку зовнішніх RC-ланцюгів компенсації Type II / Type III.
