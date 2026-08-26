# ⚙️ Програмний супервізор передавача: захист від просідання живлення та циклу BOR

Програмний супервізор передавача запобігає неконтрольованим перезавантаженням мікроконтролера через просідання напруги живлення під час випромінювання радіоімпульсу. Якщо хімічне джерело живлення частково розряджене або охолоджене, прямий запуск вихідного підсилювача передавача на максимальній потужності миттєво обвалює шину живлення нижче апаратного порогу Brown-out Reset (BOR), скидаючи процесор у нескінченний цикл перезавантаження (Bootloop).

Супервізор реалізує чотирирівневий бар'єр безпеки безпосередньо у прошивці:
1. **Діагностика причини перезапуску під час старту**: вичитування апаратних регістрів скиду для виявлення факту попереднього спрацьовування захисту BOR;
2. **Передпусковий аудит батареї під навантаженням**: вимірювання напруги АЦП із короткочасним увімкненням каліброваного тестового струму для оцінки реального внутрішнього опору;
3. **Динамічне дроселювання тактової частоти ядра (Core Clock Throttling)**: тимчасове зниження частоти процесора з 80 МГц до 2 МГц на період випромінювання пакета (зменшує струм ядра з 18 мА до 1 мА, вивільняючи дефіцитний заряд буферного конденсатора виключно для радіотракту);
4. **Адаптивне керування потужністю та плавний пуск (PA Power Ramping)** з обов'язковою релаксаційною паузою між сеансами зв'язку для повного відновлення заряду накопичувальної ємності.

---

## 1. Архітектура та механізми захисту

### Діагностика регістрів скиду (Reset Cause Detection)

Після виходу з апаратного ресету мікроконтролер повинен з'ясувати, чому саме стався перезапуск. Виробники мікроконтролерів передбачають спеціальні апаратні прапорці стану:

- **STM32 (Cortex-M)**: регістр керування тактуванням та скидом `RCC->CSR` містить біт `BORRSTF` (Brown-Out Reset Flag), а також прапорці `PORRSTF` (Power-on Reset), `SFTRSTF` (Software Reset) та `IWDGRSTF` (Independent Watchdog Reset). Запис одиниці в біт `RMVF` (Remove Reset Flag) очищає всі прапорці для фіксації наступних подій;
- **ESP32 (ESP-IDF)**: функція `esp_reset_reason()` повертає перечислення `ESP_RST_BROWNOUT`, якщо внутрішній компаратор виявив просідання живлення;
- **AVR (ATmega/ATtiny)**: регістр `MCUSR` містить прапорець `BORF` (Brown-out Reset Flag).

Якщо прошивка фіксує прапорець `BORRSTF`, це означає, що попередня спроба зв'язку зазнала краху через просідання напруги. У такому разі алгоритм збільшує лічильник збоїв, примусово зменшує вихідну потужність передавача до мінімального рівня та вмикає алгоритм експоненційного відкладення сеансу (Back-off), не дозволяючи системі зациклитися.

### Чому холосте вимірювання напруги не працює

Хімічні джерела (особливо літієві дискові елементи CR2032 та тіонілхлоридні Li-SOCl2) володіють ефектом релаксації: без навантаження їхня електрорушійна сила (ЕРС) відновлюється майже до номінальних 3.0 В навіть за 90% виснаження заряду. Вимірювання напруги АЦП у режимі спокою дає оманливо оптимістичний результат.

Щоб виявити реальний стан джерела, супервізор короткочасно (на 100–200 мкс) підключає каліброване мікронавантаження струмом 5–10 мА (наприклад, через внутрішній тестовий канал або підтяжку GPIO) безпосередньо перед зчитуванням АЦП. Якщо під цим помірним струмом напруга просідає нижче 2.4 В, опір джерела занадто високий для імпульсу 120 мА, і випромінювання на повній потужності гарантовано спричинить перезапуск.

### Збереження енергії шляхом дроселювання тактування

Під час випромінювання пакета (яке триває 10–50 мс) ядро мікроконтролера не виконує математичних розрахунків — воно або крутиться в порожньому циклі очікування прапорця завершення передачі по SPI, або спить в очікуванні зовнішнього переривання `TX_DONE`.

Робота ядра Cortex-M4 на частоті 80 МГц споживає приблизно `18 мА`. Якщо на час передачі перемкнути джерело тактування на внутрішній генератор MSI (2 МГц), споживання ядра падає до `1.0 мА`. За 10 мс передачі економія заряду становить:

```
ΔQ_saved = (18 мА - 1 мА) · 10 мс = 17 мА · 0.01 с = 170 мкКл
```

Цей зекономлений заряд залишається в буферному конденсаторі, знижуючи загальне просідання напруги на `0.35–0.50 В`, що часто є вирішальним фактором між успішною передачею та спрацьовуванням BOR.

---

## 2. Реалізація супервізора на C та ідіоматичному C++

Нижче наведено модульну реалізацію супервізора для вбудованих систем. Реалізація на C використовує структури стану та прямий виклик функцій перемикання тактування; реалізація на C++ реалізує безпечний патерн RAII (Resource Acquisition Is Initialization), шаблон `std::expected` для безпечної обробки помилок живлення та строгу типізацію рівнів потужності.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Порогові напруги живлення шини V_DD (у мілівольтах) */
#define BOR_SAFE_VOLTAGE_MV      2400U  /* Напруга, достатня для повної потужності (+14 dBm) */
#define BOR_ECO_VOLTAGE_MV       2200U  /* Межа переходу на знижену потужність (+2 dBm) */
#define BOR_CRITICAL_VOLTAGE_MV  2050U  /* Критична межа: повна заборона передачі */
#define POST_TX_RECHARGE_MS        80U  /* Час релаксації та перезаряду C_bulk */

/* Статуси виконання сеансу зв'язку */
typedef enum {
    TX_STATUS_OK = 0,
    TX_STATUS_REDUCED_POWER,
    TX_STATUS_ABORTED_LOW_BATTERY,
    TX_STATUS_HARDWARE_TIMEOUT
} tx_status_t;

/* Структура стану супервізора живлення */
typedef struct {
    uint32_t brownout_count;     /* Лічильник зафіксованих аварій BOR */
    uint16_t last_vbat_mv;       /* Останній виміряний рівень напруги (мВ) */
    uint8_t  active_power_dbm;   /* Поточна налаштована потужність PA (dBm) */
    bool     eco_mode_enforced;  /* Примусовий еко-режим після аварії */
} power_supervisor_t;

static power_supervisor_t g_pwr_supervisor;

/*
 * Ініціалізація супервізора: вичитування та скидання апаратних прапорців BOR.
 * На архітектурі STM32 прапорець BORRSTF розташований у регістрі RCC->CSR.
 */
void power_supervisor_init(void) {
    /* Базова адреса регістру контролера тактування та скиду RCC->CSR */
    volatile uint32_t *rcc_csr = (volatile uint32_t *)0x40023874;
    
    /* Біт 25: BORRSTF (Brown-out reset flag) */
    bool was_brownout = (*rcc_csr & (1U << 25)) != 0;

    if (was_brownout) {
        g_pwr_supervisor.brownout_count++;
        g_pwr_supervisor.eco_mode_enforced = true;
        /* Очищення прапорців скиду записом біта 24 (RMVF — Remove reset flag) */
        *rcc_csr |= (1U << 24);
    } else {
        g_pwr_supervisor.eco_mode_enforced = false;
    }

    g_pwr_supervisor.active_power_dbm = 14; /* Базова потужність +14 dBm */
    g_pwr_supervisor.last_vbat_mv = 3000;
}

/*
 * Тимчасове зниження частоти процесорного ядра з 80 МГц до 2 МГц.
 * Зменшує споживання ядра з ~18 мА до ~1 мА під час очікування передавача.
 */
static void clock_throttle_enter_low_freq(void) {
    /* Перемикання системного тактування SYSCLK на внутрішній RC-генератор MSI 2 МГц */
    /* Зменшення затримки Flash Latency (0WS) для мінімізації споживання пам'яті */
}

/*
 * Відновлення повної тактової частоти 80 МГц після завершення випромінювання.
 */
static void clock_throttle_restore_high_freq(void) {
    /* Збільшення Flash Latency до 4WS */
    /* Увімкнення фазового автопідстроювання частоти (PLL) та перемикання SYSCLK на 80 МГц */
}

/*
 * Вимірювання напруги живлення шини V_DD під тестовим імпульсним мікронавантаженням.
 */
static uint16_t measure_vbat_under_load_mv(void) {
    /* 
     * Короткочасне ввімкнення внутрішнього вимірювального кола АЦП (VREFINT).
     * Розрахунок поточної напруги за формулою: V_DD = 3.0 В * VREFINT_CAL / VREFINT_DATA.
     */
    return 2720; /* Симуляція: напруга під навантаженням 2.72 В */
}

/*
 * Налаштування трансивера на плавний пуск вихідного каскаду (PA Ramp Time).
 */
static void radio_configure_pa_ramp(uint8_t ramp_us) {
    /* Запис у регістр трансивера SX1262 команди SetTxParams(power, ramp_time) */
    (void)ramp_us;
}

/*
 * Безпечна передача радіопакета з повним контролем напруги та дроселюванням ядра.
 */
tx_status_t safe_radio_transmit(const uint8_t *payload, uint8_t length) {
    /* Крок 1: Аудит напруги живлення під мікронавантаженням */
    uint16_t vbat = measure_vbat_under_load_mv();
    g_pwr_supervisor.last_vbat_mv = vbat;

    /* Якщо напруга нижче критичного рівня — відхиляємо передачу, рятуючи від BOR */
    if (vbat < BOR_CRITICAL_VOLTAGE_MV) {
        return TX_STATUS_ABORTED_LOW_BATTERY;
    }

    /* Крок 2: Адаптивний вибір вихідної потужності */
    uint8_t target_power = g_pwr_supervisor.active_power_dbm;
    tx_status_t result_status = TX_STATUS_OK;

    if (vbat < BOR_SAFE_VOLTAGE_MV || g_pwr_supervisor.eco_mode_enforced) {
        target_power = 2; /* Знижуємо до +2 dBm (споживання PA падає зі 120 мА до 35 мА) */
        result_status = TX_STATUS_REDUCED_POWER;
    }

    /* Крок 3: Налаштування плавного фронту наростання PA (40 мкс) для усунення L*di/dt */
    radio_configure_pa_ramp(40);

    /* Крок 4: Дроселювання тактової частоти процесора */
    clock_throttle_enter_low_freq();

    /* 
     * Крок 5: Запуск передачі кадру трансивером по SPI.
     * Процесор очікує переривання TX_DONE у низькоспоживаючому режимі WFI (Wait For Interrupt).
     */
    /* sx1262_send_packet_blocking(payload, length, target_power); */
    (void)payload;
    (void)length;

    /* Крок 6: Миттєве відновлення повної тактової частоти ядра для обробки коду */
    clock_throttle_restore_high_freq();

    return result_status;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace power_safety {

/* Порогові напруги шини живлення V_DD (у мілівольтах) */
inline constexpr uint16_t SafeVoltageMv     = 2400;
inline constexpr uint16_t EcoVoltageMv      = 2200;
inline constexpr uint16_t CriticalVoltageMv = 2050;
inline constexpr uint32_t PostTxRechargeMs  = 80;

/* Причини відмови від передачі радіопакета */
enum class TxError : uint8_t {
    BatteryDepleted,
    HardwareFault,
    TransmitTimeout
};

/* Градація вихідної потужності підсилювача радіотракту */
enum class PowerLevel : uint8_t {
    FullPower14dBm = 14,
    EcoPower2dBm   = 2
};

/*
 * RAII-обгортка керування тактовою частотою процесорного ядра.
 * Знижує частоту при створенні об'єкта та автоматично гарантовано відновлює
 * робочу частоту при виході зі скоупу (навіть при помилках чи перериваннях).
 */
class [[nodiscard]] ScopedClockThrottle {
public:
    ScopedClockThrottle() noexcept {
        throttleTo2MHz();
    }

    ~ScopedClockThrottle() noexcept {
        restoreHighFrequency();
    }

    ScopedClockThrottle(const ScopedClockThrottle&) = delete;
    ScopedClockThrottle& operator=(const ScopedClockThrottle&) = delete;
    ScopedClockThrottle(ScopedClockThrottle&&) = delete;
    ScopedClockThrottle& operator=(ScopedClockThrottle&&) = delete;

private:
    static void throttleTo2MHz() noexcept {
        /* Зниження дільників Flash Latency та перемикання SYSCLK на внутрішній генератор MSI 2 МГц */
    }

    static void restoreHighFrequency() noexcept {
        /* Відновлення затримок Flash та повернення тактування ядра на частоту PLL 80 МГц */
    }
};

/*
 * Промисловий супервізор радіопередавача
 */
class RadioPowerSupervisor {
public:
    RadioPowerSupervisor() noexcept {
        diagnoseAndClearResetFlags();
    }

    [[nodiscard]] uint32_t getBrownoutCount() const noexcept {
        return m_brownoutCount;
    }

    [[nodiscard]] uint16_t getLastMeasuredVoltageMv() const noexcept {
        return m_lastVbatMv;
    }

    [[nodiscard]] bool isEcoModeEnforced() const noexcept {
        return m_ecoModeEnforced;
    }

    /*
     * Виконання безпечної радіопередачі зі збереженням енергетичного балансу шини.
     * Повертає фактично застосований рівень потужності або типізовану помилку.
     */
    [[nodiscard]] std::expected<PowerLevel, TxError> transmit(std::span<const uint8_t> packet) noexcept {
        const uint16_t vbat = measureBatteryUnderLoad();
        m_lastVbatMv = vbat;

        /* Захисний бар'єр: запобігання запуску при виснаженій батареї */
        if (vbat < CriticalVoltageMv) {
            return std::unexpected(TxError::BatteryDepleted);
        }

        const PowerLevel txPower = (vbat < SafeVoltageMv || m_ecoModeEnforced)
            ? PowerLevel::EcoPower2dBm
            : PowerLevel::FullPower14dBm;

        {
            /* RAII-дроселювання частоти процесора на час роботи передавача */
            ScopedClockThrottle throttleGuard;

            /* Налаштування часу наростання PA Ramp (40 мкс) та відправка даних у радіотракт */
            configurePaAndTransmit(packet, txPower);
        }

        return txPower;
    }

private:
    uint32_t m_brownoutCount{0};
    uint16_t m_lastVbatMv{3000};
    bool     m_ecoModeEnforced{false};

    void diagnoseAndClearResetFlags() noexcept {
        volatile uint32_t *rccCsr = reinterpret_cast<volatile uint32_t*>(0x40023874);
        
        /* Перевірка біта 25: BORRSTF (Brown-out Reset Flag) */
        if (*rccCsr & (1U << 25)) {
            m_brownoutCount++;
            m_ecoModeEnforced = true;
            *rccCsr |= (1U << 24); // Очищення прапорця бітом RMVF
        }
    }

    [[nodiscard]] static uint16_t measureBatteryUnderLoad() noexcept {
        /* Зчитування опорного каналу АЦП під короткочасним тестовим струмом */
        return 2720;
    }

    static void configurePaAndTransmit(std::span<const uint8_t> data, PowerLevel power) noexcept {
        /* Передача кадру по SPI та очікування апаратного переривання TX_DONE */
        (void)data;
        (void)power;
    }
};

} // namespace power_safety
```
:::

---

## 3. Крайові випадки та обробка позаштатних ситуацій

Під час практичної експлуатації автономних пристроїв виникають специфічні крайові ситуації, які вимагають надійної програмної реакції:

1. **Аварійний тайм-аут передавача (Hardware TX Timeout)**: якщо трансивер завис через збій кварцового генератора чи апаратне пошкодження антени і не виставляє лінію переривання `TX_DONE`, мікроконтролер не повинен залишатися в режимі очікування нескінченно. Вбудований сторожовий таймер передачі (Software Timeout Timer на 100 мс) примусово знеструмлює радіотракт по лінії скиду `NRST`, скидає живлення радіомодуля та переводить систему в аварійний сон;
2. **Падіння напруги посеред довгого пакета**: при передачі довгих пакетів LoRa на низьких швидкостях (SF12, час у ефірі > 1 секунди) напруга на буферному конденсаторі може поступово опускатися до критичної межі. Якщо АЦП мікроконтролера в фоновому режимі (через DMA) фіксує просідання шини нижче 2.1 В під час передачі, драйвер негайно видає команду аборту `SetStandby()`, зберігаючи ядро від апаратного ресету;
3. **Релаксаційна пауза між ретрансляціями (Inter-Packet Recharge Delay)**: протоколи передачі даних з підтвердженням прийому (ARQ) у разі відсутності квитанції ACK часто намагаються негайно повторити відправку кадру. Безпосередня повторна відправка через 1 мс гарантовано викличе BOR, оскільки буферний конденсатор ще не встиг зарядитися через великий опір батареї. Супервізор примусово блокує повторні спроби передачі на час `t_recharge ≥ 5 · R_int · C_bulk` (типово 80–120 мс), переводячи процесор у режим глибокого сну на період заряду ємності.
