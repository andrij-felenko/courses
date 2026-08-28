# ⚙️ Прошивка для радіовипробувань: режим безперервної генерації та керування тестовим трактом

Під час сертифікаційних випробувань бездротового пристрою в безвідлунній камері лабораторія не може тестувати прилад зі стандартною робочою прошивкою. У штатному режимі протоколи зв'язку (Bluetooth Low Energy, Wi-Fi або Zigbee) передають дані короткими імпульсними пачками (*Bursts*) тривалістю від кількох сотень мікросекунд до кількох мілісекунд, після чого передавач вимикається для збереження енергії. Вимірювальний приймач або аналізатор спектра лабораторії вимагає безперервного сигналу зі 100% шпаруватістю (*Duty Cycle*), щоб зафіксувати точну пікову потужність, фазовий шум та спектральну маску на крайніх частотах діапазону.

Тому кожен прилад, що подається на радіосертифікацію RED або FCC, повинен постачатися зі спеціальною **тестовою прошивкою (RF Compliance Test Firmware)**. Ця прошивка забезпечує керування радіотрактом через послідовний порт UART за допомогою стандартизованих команд або інтерфейсу прямого тестування (*Direct Test Mode — DTM* за специфікацією Bluetooth Core v5.4).

## 1. Обов'язкові режими роботи радіотракту в лабораторії

Тестова прошивка зобов'язана реалізовувати чотири обов'язкові стани радіоінтерфейсу:

1. **Нескінченна несуча без модуляції (Continuous Wave — CW / Tone Mode):** Передавач генерує чисту синусоїду на фіксованій частоті з постійною потужністю. Використовується для вимірювання відхилення частоти опорного кварцового резонатора (допуск зазвичай ±20 ppm), фазового шуму синтезатора частоти PLL та гармонік ВЧ-тракту.
2. **Безперервна модульована передача (Continuous Modulated / PRBS9):** Передавач безперервно випромінює псевдовипадкову послідовність бітів довжиною 511 бітів (PRBS9 за поліномом `x⁹ + x⁵ + 1`) із заданим типом модуляції (GFSK, QPSK, OFDM). Застосовується для перевірки зайнятої смуги частот (*Occupied Bandwidth — OBW*), спектральної густини потужності (*PSD*) та випромінювання на краях смуги (*Band Edge Compliance* на каналах 2402 МГц та 2480 МГц для BLE).
3. **Режим безперервного прийому (Continuous RX Mode):** Приймач постійно увімкнений на вибраному каналі без надсилання відповідей. Необхідний для вимірювання паразитних випромінювань гетеродина приймача в камері та перевірки блокування сусідніх каналів (*Receiver Blocking*).
4. **Стрибкоподібна перебудова частоти (Frequency Hopping):** Перемикання каналів за псевдовипадковим алгоритмом для перевірки сумісності зі стандартами FHSS та рівномірності розподілу спектральної енергії.

## 2. Реалізація тестового контролера на мовах C та C++

Нижче наведено повноцінний контролер радіотестування з консольним інтерфейсом UART CLI. Контролер обробляє текстові команди лабораторії, перевіряє межі аргументів та перемикає стани низькорівневого радіотрансивера.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

typedef enum {
    RF_MODE_IDLE = 0,
    RF_MODE_TX_CW,        /* Немодульована синусоїда (Continuous Wave) */
    RF_MODE_TX_MODULATED, /* Псевдовипадковий модульований потік PRBS9 */
    RF_MODE_RX_STANDBY    /* Безперервний прийом */
} rf_test_mode_t;

typedef struct {
    rf_test_mode_t mode;
    uint8_t channel;      /* Номер каналу: 0..39 для BLE (2402..2480 МГц) */
    int8_t power_dbm;     /* Потужність: -20..+8 дБм */
    uint32_t payload_cnt; /* Лічильник відправлених пакетів */
} rf_test_state_t;

static rf_test_state_t g_rf_state = {
    .mode = RF_MODE_IDLE,
    .channel = 0,
    .power_dbm = 0,
    .payload_cnt = 0
};

/* Апаратно-залежні заглушки для взаємодії з регістрами трансивера */
static void hw_radio_stop(void) {
    /* Скидання автоматів станів радіомодуля та вимкнення синтезатора PLL */
}

static void hw_radio_start_cw(uint8_t channel, int8_t power_dbm) {
    /* Налаштування частоти: F_rf = 2402 + channel * 2 МГц */
    /* Встановлення потужності передавача та запуск генерації тону */
}

static void hw_radio_start_modulated(uint8_t channel, int8_t power_dbm) {
    /* Запуск апаратного генератора PRBS9 з безперервною GFSK модуляцією */
}

static void hw_radio_start_rx(uint8_t channel) {
    /* Увімкнення підсилювача LNA та демодулятора в режимі прослуховування */
}

void rf_test_init(void) {
    g_rf_state.mode = RF_MODE_IDLE;
    hw_radio_stop();
}

bool rf_test_execute_command(const char *cmd_line, char *resp_buf, size_t resp_max) {
    char cmd[16] = {0};
    int chan = 0;
    int power = 0;

    if (sscanf(cmd_line, "%15s %d %d", cmd, &chan, &power) < 1) {
        snprintf(resp_buf, resp_max, "ERR: EMPTY_CMD\r\n");
        return false;
    }

    if (strcmp(cmd, "STOP") == 0) {
        hw_radio_stop();
        g_rf_state.mode = RF_MODE_IDLE;
        snprintf(resp_buf, resp_max, "OK: RADIO_STOPPED\r\n");
        return true;
    }

    if (chan < 0 || chan > 39) {
        snprintf(resp_buf, resp_max, "ERR: INVALID_CHANNEL (0..39)\r\n");
        return false;
    }

    if (power < -20 || power > 8) {
        snprintf(resp_buf, resp_max, "ERR: INVALID_POWER (-20..+8 dBm)\r\n");
        return false;
    }

    if (strcmp(cmd, "TX_CW") == 0) {
        hw_radio_stop();
        g_rf_state.channel = (uint8_t)chan;
        g_rf_state.power_dbm = (int8_t)power;
        g_rf_state.mode = RF_MODE_TX_CW;
        hw_radio_start_cw(g_rf_state.channel, g_rf_state.power_dbm);
        snprintf(resp_buf, resp_max, "OK: TX_CW CH=%d PWR=%d dBm\r\n", chan, power);
        return true;
    }

    if (strcmp(cmd, "TX_MOD") == 0) {
        hw_radio_stop();
        g_rf_state.channel = (uint8_t)chan;
        g_rf_state.power_dbm = (int8_t)power;
        g_rf_state.mode = RF_MODE_TX_MODULATED;
        hw_radio_start_modulated(g_rf_state.channel, g_rf_state.power_dbm);
        snprintf(resp_buf, resp_max, "OK: TX_MOD PRBS9 CH=%d PWR=%d dBm\r\n", chan, power);
        return true;
    }

    if (strcmp(cmd, "RX") == 0) {
        hw_radio_stop();
        g_rf_state.channel = (uint8_t)chan;
        g_rf_state.mode = RF_MODE_RX_STANDBY;
        hw_radio_start_rx(g_rf_state.channel);
        snprintf(resp_buf, resp_max, "OK: RX_STANDBY CH=%d\r\n", chan);
        return true;
    }

    snprintf(resp_buf, resp_max, "ERR: UNKNOWN_CMD: %s\r\n", cmd);
    return false;
}
```
```cpp
#include <cstdint>
#include <string_view>
#include <span>
#include <charconv>
#include <array>

namespace compliance {

enum class RfMode : uint8_t {
    Idle = 0,
    TxContinuousWave,
    TxModulatedPrbs9,
    RxContinuous
};

struct RadioConfig {
    static constexpr uint8_t MinChannel = 0;
    static constexpr uint8_t MaxChannel = 39;
    static constexpr int8_t MinPowerDbm = -20;
    static constexpr int8_t MaxPowerDbm = 8;
};

class RfComplianceController {
public:
    constexpr RfComplianceController() noexcept = default;

    void init() noexcept {
        stopHardware();
        currentMode_ = RfMode::Idle;
    }

    bool handleCommand(std::string_view cmdLine, std::span<char> responseOut) noexcept {
        auto tokens = tokenize(cmdLine);
        if (tokens.empty()) {
            writeResponse(responseOut, "ERR: EMPTY_CMD\r\n");
            return false;
        }

        const auto verb = tokens[0];
        if (verb == "STOP") {
            stopHardware();
            currentMode_ = RfMode::Idle;
            writeResponse(responseOut, "OK: RADIO_STOPPED\r\n");
            return true;
        }

        if (tokens.size() < 2) {
            writeResponse(responseOut, "ERR: MISSING_ARGS\r\n");
            return false;
        }

        int channel = 0;
        if (!parseNumber(tokens[1], channel) || 
            channel < RadioConfig::MinChannel || channel > RadioConfig::MaxChannel) {
            writeResponse(responseOut, "ERR: INVALID_CHANNEL (0..39)\r\n");
            return false;
        }

        if (verb == "RX") {
            stopHardware();
            channel_ = static_cast<uint8_t>(channel);
            currentMode_ = RfMode::RxContinuous;
            startHardwareRx(channel_);
            writeResponse(responseOut, "OK: RX_STANDBY\r\n");
            return true;
        }

        if (tokens.size() < 3) {
            writeResponse(responseOut, "ERR: MISSING_POWER\r\n");
            return false;
        }

        int power = 0;
        if (!parseNumber(tokens[2], power) || 
            power < RadioConfig::MinPowerDbm || power > RadioConfig::MaxPowerDbm) {
            writeResponse(responseOut, "ERR: INVALID_POWER (-20..+8 dBm)\r\n");
            return false;
        }

        channel_ = static_cast<uint8_t>(channel);
        powerDbm_ = static_cast<int8_t>(power);

        if (verb == "TX_CW") {
            stopHardware();
            currentMode_ = RfMode::TxContinuousWave;
            startHardwareCw(channel_, powerDbm_);
            writeResponse(responseOut, "OK: TX_CW_ACTIVE\r\n");
            return true;
        }

        if (verb == "TX_MOD") {
            stopHardware();
            currentMode_ = RfMode::TxModulatedPrbs9;
            startHardwareModulated(channel_, powerDbm_);
            writeResponse(responseOut, "OK: TX_MOD_PRBS9_ACTIVE\r\n");
            return true;
        }

        writeResponse(responseOut, "ERR: UNKNOWN_COMMAND\r\n");
        return false;
    }

    [[nodiscard]] RfMode mode() const noexcept { return currentMode_; }
    [[nodiscard]] uint8_t channel() const noexcept { return channel_; }
    [[nodiscard]] int8_t power() const noexcept { return powerDbm_; }

private:
    RfMode currentMode_{RfMode::Idle};
    uint8_t channel_{0};
    int8_t powerDbm_{0};

    static void stopHardware() noexcept {
        /* Апаратне вимкнення генератора та підсилювачів */
    }

    static void startHardwareCw(uint8_t ch, int8_t pwr) noexcept {
        /* Налаштування регістрів на генерацію немодульованого тону */
    }

    static void startHardwareModulated(uint8_t ch, int8_t pwr) noexcept {
        /* Запуск генератора PRBS9 з модуляцією GFSK */
    }

    static void startHardwareRx(uint8_t ch) noexcept {
        /* Переведення ВЧ-тракту в режим постійного прийому */
    }

    static bool parseNumber(std::string_view sv, int &val) noexcept {
        const auto res = std::from_chars(sv.data(), sv.data() + sv.size(), val);
        return res.ec == std::errc{};
    }

    static void writeResponse(std::span<char> dst, std::string_view src) noexcept {
        const auto len = std::min(dst.size() - 1, src.size());
        std::copy_n(src.data(), len, dst.data());
        dst[len] = '\0';
    }

    static auto tokenize(std::string_view s) noexcept {
        std::array<std::string_view, 4> tokens{};
        size_t count = 0;
        size_t start = 0;

        while (start < s.size() && count < tokens.size()) {
            while (start < s.size() && (s[start] == ' ' || s[start] == '\r' || s[start] == '\n')) {
                ++start;
            }
            if (start >= s.size()) break;

            size_t end = start;
            while (end < s.size() && s[end] != ' ' && s[end] != '\r' && s[end] != '\n') {
                ++end;
            }
            tokens[count++] = s.substr(start, end - start);
            start = end;
        }
        return std::span<const std::string_view>(tokens.data(), count);
    }
};

} // namespace compliance
```
:::

## 3. Інженерні пастки та особливості поведінки в камері

Розробка тестової прошивки має специфічні особливості, які рідко зустрічаються у штатному коді додатків:

1. **Блокування сторожового таймера (Watchdog Disable):** У штатному режимі сторожовий таймер WDT перезавантажує мікроконтролер, якщо основний цикл зависає. У режимі нескінченної генерації CW мікроконтролер може перебувати в безперервному циклі або апаратному режимі очікування переривань годинами. Якщо прошивка не вимикає WDT або не оновлює його через таймерний тік, прилад раптово перезавантажиться просто посеред 30-хвилинного сканування спектра в камері, що призведе до анулювання результатів тесту.
2. **Теплове регулювання (Thermal Management):** У безперервному режимі передачі зі 100% шпаруватістю вихідний підсилювач потужності (PA) та мікросхема живлення розсіюють значно більше тепла, ніж у реальній роботі з duty cycle 2%. Температура кристала трансивера може зрости на 25–40 °C. Це призводить до теплового дрейфу частоти кварцового генератора та падіння вихідної потужності на 0.5–1.5 дБ. Інженер повинен забезпечити ефективне тепловідведення від корпусу під час лабораторних прогонів.
3. **Стійкість каналу UART до радіовипромінювання:** Кабель послідовного порту, підключений до тестового стенда в безвідлунній камері, має довжину від 5 до 10 метрів і проходить крізь фільтрувальні панелі екранованої кімнати. Якщо лінії RX/TX мікроконтролера не зашунтовані фільтруючими конденсаторами ємністю 10–22 пФ або феритовими намистинами, власне потужне випромінювання антени наведе на кабель ВЧ-струми, які спотворять дані UART або заблокують прийом команд оператора.

## 4. Чекліст підготовки зразків до лабораторії

Під час передачі зразків інженеру-випробувачу лабораторії необхідно надати:

1. **3–5 апаратних примірників:**
   - 1 зразок зі звичайною антеною та тестовою прошивкою (для вимірювання випромінюваних параметрів у камері);
   - 1 зразок із впаяним коаксіальним кабелем U.FL або SMA прямо на виході ВЧ-тракту в обхід антени (для кондуктивних вимірювань потужності та гармонік на спектроаналізаторі);
   - 2 зразки з фінальною робочою прошивкою (для випробувань імунітету та електробезпеки).
2. **Кабель керування та документація CLI:** Інструкція із зазначенням швидкості UART (115200 8N1), схеми підключення перехідника USB-UART та переліку команд.
3. **Електричні параметри живлення:** Допустимий діапазон напруги, тип роз'єму та споживаний струм у режимі максимальної потужності передавача.
