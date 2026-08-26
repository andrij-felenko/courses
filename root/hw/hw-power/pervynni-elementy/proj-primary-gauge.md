# ⚙️ Програмний профіль батареї, лічба кулонів та депасивація первинних елементів

У пристроях з живленням від вторинних літій-іонних акумуляторів рівень залишкового заряду (State of Charge, SoC) можна з прийнятною точністю оцінити простим періодичним вимірюванням напруги розімкненого кола (Open Circuit Voltage, OCV). Проте для первинних елементів літій-тіонілхлориду (`Li-SOCl₂`) та літієвих монеток `CR2032` цей підхід виявляється абсолютно непридатним: їхня електрохімічна розрядна крива утримує майже ідеальне горизонтальне плато (`3.60–3.65 В` або `2.85–2.90 В`) аж до моменту, коли в комірці залишається менше ніж 2–3% ємності, після чого напруга катастрофічно обвалюється за лічені години.

Єдиний надійний інженерний підхід до довгострокового моніторингу первинних хімічних джерел полягає в комбінації програмної кулонометрії (лічби кулонів), температурного обліку фонового саморозряду за моделлю Арреніуса, предиктивного розрахунку просідання напруги перед кожним увімкненням радіомодему та процедури активної депасивації.

---

### Архітектура та життєвий цикл програмного модуля

Програмний модуль профілювання первинної батареї інтегрується в диспетчер живлення мікроконтролера та виконує чотири взаємопов'язані задачі:

1. **Дискретна лічба кулонів (Coulomb Counting)**: мікроконтролер відстежує точний час перебування в різних режимах енергоспоживання (глибокий сон `EM4/Stop`, робота обчислювального ядра, опитування сенсорів, активна передача радіомодему). Заряд обчислюється як інтеграл `Q = ∑ I_state · Δt_state` у наноампер-годинах (`нА·год`) із фіксацією в незалежній пам'яті (Flash/FRAM/EEPROM). Для мінімізації навантаження на процесор час сну підраховується за допомогою апаратного низькоспоживаючого таймера (LPTIM або RTC), тактованого від кварцового резонатора `32.768 кГц`.
2. **Температурне коригування фонового саморозряду**: щогодинний розрахунок втраченої хімічної ємності на основі вбудованого термодатчика. При підвищенні температури швидкість деградації активної речовини зростає експоненційно, тому модуль додає розрахунковий струм витоку до лічильника витрат.
3. **Предиктивний аналіз просідання напруги перед радіопосилкою**: перед подачею живлення на підсилювач потужності модему (LoRa, NB-IoT, BLE) алгоритм розраховує очікуване падіння напруги `ΔU = I_tx · R_esr`. Якщо прогнозована напруга клем опускається нижче порогу аварійного скидання процесора (`U_brownout + U_margin`), пристрій скасовує передачу або зменшує вихідну потужність передавача (Tx Power), запобігаючи неконтрольованому скиданню ядра (Brownout Reset).
4. **Автоматичний контроль пасивації (для Li-SOCl₂)**: якщо система перебувала у стані безперервного сну понад 30 діб або зафіксовано переохолодження нижче `0 °C`, модуль ініціює керований імпульс депасивації — відкриває окремий ключ із баластним резистором (`15–20 мА` на `50–100 мс`) для розчинення кристалічної плівки `LiCl` перед стартом основного радіомодему.

Життєвий цикл стану батарейного менеджера організовано у вигляді скінченного автомата з детермінованими переходами:

```
[ГЛИБОКИЙ СОН] ──(Таймер RTC)──► [ВИМІР ТЕМПЕРАТУРИ ТА OCV]
                                          │
                                          ▼
                                 [ПРЕДИКТИВНИЙ АНАЛІЗ]
                                    │               │
                            (Потрібна депасивація) (Нормальний стан)
                                    │               │
                                    ▼               │
                         [ІМПУЛЬС ДЕПАСИВАЦІЇ]      │
                                    │               │
                                    └───────┬───────┘
                                            ▼
                                   [СЕАНС ЗВ'ЯЗКУ TX/RX]
                                            │
                                            ▼
                                  [ІНТЕГРАЦІЯ КУЛОНІВ]
                                            │
                                            ▼
                               [ЗБЕРЕЖЕННЯ В FLASH/FRAM]
                                            │
                                            ▼
                                     [ГЛИБОКИЙ СОН]
```

---

### Реалізація на мовах C та C++

Нижче наведено повністю працездатний, незалежний від апаратної платформи модуль обліку енергії та предиктивної оцінки батарейного вузла.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Тип хімічної системи первинного елемента */
typedef enum {
    BATTERY_CHEM_LITHIUM_THIONYL, /* Li-SOCl2 (3.6 В, висока пасивація) */
    BATTERY_CHEM_COIN_CR2032,      /* Li-MnO2 (3.0 В, високий ESR) */
    BATTERY_CHEM_ALKALINE          /* Zn-MnO2 (1.5 В, похилий розряд) */
} battery_chem_t;

/* Конфігурація параметрів батарейного вузла */
typedef struct {
    battery_chem_t chem;
    uint32_t nominal_capacity_uah; /* Номінальна ємність у мкА·год */
    uint32_t esr_milliohm;          /* Еквівалентний послідовний опір (мОм) */
    uint16_t brownout_limit_mv;    /* Поріг аварійного скидання MCU (мВ) */
    uint16_t base_self_discharge_ppm_year; /* Базовий саморозряд при +25C (ppm/рік) */
} battery_config_t;

/* Стан обліку заряду та здоров'я батареї */
typedef struct {
    battery_config_t cfg;
    uint64_t consumed_nanoamp_hours; /* Інтегратор витраченої ємності */
    uint32_t last_pulse_timestamp_s; /* Час останнього силового імпульсу */
    bool depassivation_needed;       /* Прапорець потреби депасивації */
} battery_gauge_t;

/* Ініціалізація структури обліку */
void battery_gauge_init(battery_gauge_t *gauge, const battery_config_t *cfg) {
    if (!gauge || !cfg) return;
    gauge->cfg = *cfg;
    gauge->consumed_nanoamp_hours = 0;
    gauge->last_pulse_timestamp_s = 0;
    gauge->depassivation_needed = false;
}

/* Облік заряду, спожитого в режимі сну за інтервал часу */
void battery_gauge_track_sleep(battery_gauge_t *gauge, uint32_t duration_ms, uint32_t sleep_current_na) {
    if (!gauge) return;
    /* Переведення наноампер-мілісекунд у наноампер-години: nA * ms / 3600000 */
    uint64_t consumed_nah = ((uint64_t)sleep_current_na * duration_ms) / 3600000ULL;
    gauge->consumed_nanoamp_hours += consumed_nah;
}

/* Облік заряду активного імпульсу струму */
void battery_gauge_track_pulse(battery_gauge_t *gauge, uint32_t duration_us, uint32_t current_ua, uint32_t now_s) {
    if (!gauge) return;
    /* uA * us / 3600000000 = uAh -> * 1000 = nAh */
    uint64_t consumed_nah = ((uint64_t)current_ua * duration_us) / 3600000ULL;
    gauge->consumed_nanoamp_hours += consumed_nah;
    gauge->last_pulse_timestamp_s = now_s;
    gauge->depassivation_needed = false;
}

/* Періодичний облік фонового саморозряду з температурною поправкою */
void battery_gauge_update_self_discharge(battery_gauge_t *gauge, int8_t temp_celsius, uint32_t interval_hours) {
    if (!gauge) return;
    
    /* Фактор Арреніуса: подвоєння швидкості на кожні 10°C понад +25°C */
    float temp_factor = 1.0f;
    if (temp_celsius > 25) {
        int8_t delta_t = temp_celsius - 25;
        temp_factor = 1.0f + (float)delta_t * 0.08f; /* Лінеаризація для MCU без FPU */
    } else if (temp_celsius < 10) {
        temp_factor = 0.6f;
    }

    /* Розрахунок втрат на годину від номінальної ємності */
    uint64_t nom_nah = (uint64_t)gauge->cfg.nominal_capacity_uah * 1000ULL;
    uint64_t annual_loss_nah = (nom_nah * gauge->cfg.base_self_discharge_ppm_year) / 1000000ULL;
    uint64_t hour_loss_nah = (uint64_t)((annual_loss_nah / 8760ULL) * temp_factor);

    gauge->consumed_nanoamp_hours += (hour_loss_nah * interval_hours);

    /* Перевірка потреби депасивації для Li-SOCl2 (якщо спокій > 30 діб або мороз) */
    if (gauge->cfg.chem == BATTERY_CHEM_LITHIUM_THIONYL) {
        if ((interval_hours > 720) || (temp_celsius < 0 && interval_hours > 168)) {
            gauge->depassivation_needed = true;
        }
    }
}

/* Прогноз просідання напруги перед радіопосилкою (повертає очікувану напругу клем у мВ) */
uint16_t battery_predict_pulse_voltage_mv(const battery_gauge_t *gauge, uint16_t ocv_mv, uint32_t pulse_current_ua) {
    if (!gauge) return 0;
    
    /* Омічний спад: ΔU (мВ) = I (мкА) * ESR (мОм) / 1000000 */
    uint32_t sag_mv = ((uint64_t)pulse_current_ua * gauge->cfg.esr_milliohm) / 1000000ULL;
    
    if (ocv_mv <= sag_mv) {
        return 0;
    }
    return (ocv_mv - (uint16_t)sag_mv);
}

/* Отримання залишкового заряду у відсотках (0..100) */
uint8_t battery_get_state_of_charge_pct(const battery_gauge_t *gauge) {
    if (!gauge) return 0;
    uint64_t nom_nah = (uint64_t)gauge->cfg.nominal_capacity_uah * 1000ULL;
    if (gauge->consumed_nanoamp_hours >= nom_nah) {
        return 0;
    }
    uint64_t remaining_nah = nom_nah - gauge->consumed_nanoamp_hours;
    return (uint8_t)((remaining_nah * 100ULL) / nom_nah);
}
```
```cpp
#include <cstdint>
#include <chrono>
#include <algorithm>

namespace embedded::power {

enum class Chemistry : uint8_t {
    LithiumThionyl, /* Li-SOCl2 */
    CoinCr2032,     /* Li-MnO2 */
    Alkaline        /* Zn-MnO2 */
};

struct BatterySpecs {
    Chemistry chem{Chemistry::LithiumThionyl};
    uint32_t nominalCapacityMicroAmpHours{2400000}; /* 2.4 А·год */
    uint32_t esrMilliohm{50000};                    /* 50 Ом для бобінного елемента */
    uint16_t brownoutLimitMilliVolts{2200};         /* 2.2 В */
    uint16_t baseSelfDischargePpmYear{10000};       /* 1% = 10000 ppm/рік */
};

class PrimaryBatteryGauge {
public:
    constexpr explicit PrimaryBatteryGauge(const BatterySpecs& specs) noexcept
        : specs_(specs), consumedNanoAmpHours_(0), lastPulseTimeSeconds_(0), depassivationNeeded_(false) {}

    /* Облік глибокого сну */
    void trackSleep(std::chrono::milliseconds duration, uint32_t sleepCurrentNanoAmps) noexcept {
        const auto consumedNah = (static_cast<uint64_t>(sleepCurrentNanoAmps) * duration.count()) / 3600000ULL;
        consumedNanoAmpHours_ += consumedNah;
    }

    /* Облік активного імпульсу */
    void trackPulse(std::chrono::microseconds duration, uint32_t currentMicroAmps, uint32_t currentTimeSeconds) noexcept {
        const auto consumedNah = (static_cast<uint64_t>(currentMicroAmps) * duration.count()) / 3600000ULL;
        consumedNanoAmpHours_ += consumedNah;
        lastPulseTimeSeconds_ = currentTimeSeconds;
        depassivationNeeded_ = false;
    }

    /* Оновлення саморозряду з урахуванням температури */
    void updateSelfDischarge(int8_t temperatureCelsius, std::chrono::hours interval) noexcept {
        float tempFactor = 1.0f;
        if (temperatureCelsius > 25) {
            tempFactor += static_cast<float>(temperatureCelsius - 25) * 0.08f;
        } else if (temperatureCelsius < 10) {
            tempFactor = 0.6f;
        }

        const uint64_t nominalNah = static_cast<uint64_t>(specs_.nominalCapacityMicroAmpHours) * 1000ULL;
        const uint64_t annualLossNah = (nominalNah * specs_.baseSelfDischargePpmYear) / 1000000ULL;
        const uint64_t hourLossNah = static_cast<uint64_t>((annualLossNah / 8760ULL) * tempFactor);

        consumedNanoAmpHours_ += (hourLossNah * interval.count());

        if (specs_.chem == Chemistry::LithiumThionyl) {
            if (interval.count() > 720 || (temperatureCelsius < 0 && interval.count() > 168)) {
                depassivationNeeded_ = true;
            }
        }
    }

    /* Прогнозування клемної напруги під час імпульсу (мВ) */
    [[nodiscard]] constexpr uint16_t predictPulseVoltage(uint16_t ocvMilliVolts, uint32_t pulseCurrentMicroAmps) const noexcept {
        const uint32_t sagMilliVolts = (static_cast<uint64_t>(pulseCurrentMicroAmps) * specs_.esrMilliohm) / 1000000ULL;
        if (ocvMilliVolts <= sagMilliVolts) {
            return 0;
        }
        return static_cast<uint16_t>(ocvMilliVolts - sagMilliVolts);
    }

    /* Чи безпечно запускати передачу без ризику Brownout */
    [[nodiscard]] constexpr bool isSafeForTransmission(uint16_t ocvMilliVolts, uint32_t pulseCurrentMicroAmps) const noexcept {
        return predictPulseVoltage(ocvMilliVolts, pulseCurrentMicroAmps) >= specs_.brownoutLimitMilliVolts;
    }

    /* Відсоток залишкової ємності (0..100) */
    [[nodiscard]] constexpr uint8_t stateOfChargePercent() const noexcept {
        const uint64_t nominalNah = static_cast<uint64_t>(specs_.nominalCapacityMicroAmpHours) * 1000ULL;
        if (consumedNanoAmpHours_ >= nominalNah) {
            return 0;
        }
        const uint64_t remainingNah = nominalNah - consumedNanoAmpHours_;
        return static_cast<uint8_t>((remainingNah * 100ULL) / nominalNah);
    }

    [[nodiscard]] constexpr bool isDepassivationNeeded() const noexcept {
        return depassivationNeeded_;
    }

private:
    BatterySpecs specs_;
    uint64_t consumedNanoAmpHours_{0};
    uint32_t lastPulseTimeSeconds_{0};
    bool depassivationNeeded_{false};
};

} // namespace embedded::power
```
:::

---

### Тонкощі збереження стану, вибірки АЦП та виробничого калібрування

Для бездоганної роботи лічильника кулонів протягом 10–20 років необхідно враховувати апаратні обмеження енергонезалежної пам'яті, схемотехніку аналого-цифрового тракту та методи виробничого тестування:

1. **Зношування секторів Flash-пам'яті (Flash Wear-Leveling)**: запис поточного значення лічильника заряду після кожного сеансу зв'язку (наприклад, кожні 15 хвилин) створить `35 000` циклів запису на рік, що вичерпає ресурс звичайної Flash-пам'яті (типово 10 000–100 000 циклів) за кілька років. Запис слід виконувати не частіше одного разу на добу або накопичувати дельту в ретенційній оперативній пам'яті (Backup SRAM / Retention RAM), живленої від домену RTC під час глибокого сну.
2. **Атомарність оновлення при раптовому вимкненні**: запис структури обліку повинен містити контрольну суму (CRC16/CRC32) та порядковий номер транзакції (Sequence ID) із використанням кільцевого буфера або подвійної структури (Double-buffering / Ping-Pong structure). Це гарантує відновлення коректного стану, якщо живлення пропаде безпосередньо в момент стирання сектора пам'яті.
3. **Синхронізація з сторожовим таймером (Watchdog)**: тривалість процедури програмної депасивації (`50–100 мс`) та вимірювання АЦП повинна бути меншою за мінімальний тайм-аут сторожового таймера мікроконтролера, щоб уникнути помилкового перезапуску ядра під час активного пропалювання плівки `LiCl`.
4. **Час вибірки АЦП при високому імпедансі джерела**: оскільки внутрішній опір первинних елементів або вимірювальних дільників напруги досягає сотень кілоом, час заряду вхідного конденсатора вибірки-зберігання АЦП `C_sh` зростає. Час семплювання `t_sample` слід програмно збільшувати до `10–50 мкс`, інакше зчитуване значення напруги буде суттєво заниженим.
5. **Адаптивна динамічна оцінка ESR за відскоком напруги**: алгоритм може самостійно калібрувати внутрішній опір під час роботи. Для цього напруга батареї вимірюється двічі: наприкінці активного радіопакету під відомим струмом `I_tx` та через `5 мс` після переходу в режим сну. Різниця напруг `ΔU_meas` ділиться на відомий струм, даючи поточний реальний опір `R_esr = ΔU_meas / I_tx`, що автоматично враховує як старіння хімії, так і поточну температуру.
6. **Виробнича депасивація перед монтажем на лінію**: елементи `Li-SOCl₂`, що лежали на складі виробника понад 6 місяців, монтують у пристрій уже в пасивованому стані. На заводському випробувальному стенді (FCT) обов'язково проганяють автоматичний цикл контрольованого струмового навантаження (`50 мА` протягом `2–5 секунд`) для розчинення первинної плівки `LiCl` перед прошивкою та тестуванням радіотракту.
