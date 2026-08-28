# ⚙️ Автомат безпечного оновлення: опитування паливного мікроконтролера та активний імпульсний тест

Безпечний старт оновлення прошивки по бездротовому каналу вимагає суворого багаторівневого контролю фізичного стану джерела живлення. Якщо запустити стирання та перепрограмування Flash-пам'яті на розрядженій або переохолодженій батареї з високим внутрішнім опором, імпульс струму помпи заряду провалить напругу шини нижче порогу Brownout Reset, що призведе до невідновного пошкодження секторів і перетворення пристрою на «цеглину».

У цій практичній вставці реалізовано скінченний автомат передпольотної перевірки батареї (англ. *Battery Pre-Flight Supervisor*), який послідовно валідує наявність зовнішнього живлення, температурний коридор, відсоток залишкового заряду та виконує активний апаратний імпульсний тест просідання напруги перед наданням дозволу на модифікацію Flash.

---

### Фізичний механізм активного імпульсного тесту (Active Pulse Test)

Пасивне вимірювання напруги батареї у стані спокою або зчитування регістра відсотків заряду з дешевого паливоміра часто дає хибне відчуття безпеки. Наприклад, стара літій-іонна комірка після кількох років експлуатації або охолоджена до `0 °C` може показувати напругу розімкненого кола `OCV = 3.75 В` (що формально відповідає приблизно 45–50% номінальної ємності). Проте внутрішній еквівалентний послідовний опір такої комірки `R_esr` може зрости від початкових 80 мОм до 800–1200 мОм.

Щойно мікроконтролер увімкне радіопередавач на повну потужність і одночасно запустить помпу заряду Flash-пам'яті для стирання першого 64-кілобайтного сектора, сумарний струм споживання підскочить до 300–350 мА. На внутрішньому опорі 1.0 Ом миттєво впаде `0.35 В`, до яких додасться падіння на контактах батарейного відсіку та вхідному стабілізаторі. Напруга на виводі живлення ядра провалиться нижче 2.70 В, викликавши апаратний скид мікроконтролера в момент незавершеного тунелювання електронів у плаваючий затвор Flash.

Щоб запобігти такій катастрофі, прошивка виконує активне зондування реального імпедансу комірки безпосередньо перед стиранням пам'яті:

1. **Замір напруги спокою `V_idle`:** Контролер зчитує стабільну напругу шини живлення до активації сильнострумових вузлів.
2. **Формування каліброваного імпульсу навантаження:** На короткий фіксований проміжок часу `t_pulse = 15 мс` підключається тестове навантаження зі струмом `I_test ≈ 200 мА`. Тривалість 15 мс обрана компромісно: вона достатньо довга, щоб завершилися високочастотні перехідні процеси на керамічних конденсаторах обв'язки (10–50 мкс), але достатньо коротка, щоб не запустити повільну хімічну дифузійну поляризацію електроліту (яка розвивається від 100 мс до секунд). Як навантаження використовується або апаратний тестовий резистор, комутований польовим транзистором, або переведення радіотрансивера в режим передачі немодульованого сигналу (CW mode).
3. **Замір напруги під навантаженням `V_load`:** На 12–14 мілісекунді імпульсу АЦП робить серію з 8 швидких відліків і усереднює їх.
4. **Обчислення динамічного опору:**
   ```
   R_esr = (V_idle - V_load) / I_test
   ```
5. **Екстраполяція найгіршого просідання під час OTA:**
   ```
   Delta_V_worst = I_ota_peak · R_esr
   V_forecast = V_idle - Delta_V_worst
   ```
6. **Порівняння з безпековим бар'єром:** Якщо `V_forecast < V_bor_safe` (де `V_bor_safe = V_BOR + 200 мВ`), автомат виставляє безумовне блокування оновлення.

---

### Крайові випадки та часовий релаксаційний бар'єр

Під час проектування імпульсного тесту слід враховувати три критичні крайові ситуації:

- **Просідання до Brownout під час самого тестового імпульсу:** Якщо батарея настільки виснажена або замерзла, що навіть тестовий струм 200 мА провалює шину, спрацює апаратний BOR. Проте такий скид є повністю безпечним: він відбувається ДО того, як у Flash стерто хоча б один байт. Пристрій перезавантажиться у стару робочу прошивку. Після повторного старту лічильник невдалих спроб зафіксує збій живлення і заблокує подальші спроби OTA.
- **Обов'язкова релаксаційна пауза (Cooldown Period):** Після вимкнення тестового імпульсу напруга на комірці не повертається до початкового рівня миттєво через явище подвійного електричного шару (ємність поляризації). Якщо одразу почати стирання Flash, реальна напруга буде заниженою. Тому між завершенням тесту і стартом стирання обов'язково витримується пауза релаксації тривалістю 50–100 мс.
- **Адаптивне зниження апетиту (Frequency & Power Throttling):** Якщо прогнозована напруга близька до межі, але оновлення має статус критичного безпекового патчу (Emergency Security Fix), система може застосувати пом'якшення: знизити тактову частоту ядра з 160 МГц до 40 МГц (зменшує струм CPU на 25 мА), знизити частоту шини SPI Flash з 80 МГц до 20 МГц і зменшити потужність передавача радіомодуля з +20 dBm до +10 dBm. Це знижує сумарний піковий струм `I_ota_peak` майже вдвічі й дозволяє безпечно прошити пристрій навіть на помірно зношеній батареї.

---

### Програмна реалізація перевірки батарейного шлюзу

Нижче наведено повноцінні модулі передпольотної діагностики живлення мовами C та C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Результати оцінки стану живлення для OTA */
typedef enum {
    OTA_BATTERY_ALLOW_AC_POWERED = 0, /* Дозволено: підключено зовнішнє джерело */
    OTA_BATTERY_ALLOW_BATTERY_OK = 1, /* Дозволено: параметри акумулятора в нормі */
    OTA_BATTERY_DENY_COLD        = 2, /* Заборонено: температура надто низька */
    OTA_BATTERY_DENY_HOT         = 3, /* Заборонено: температура надто висока */
    OTA_BATTERY_DENY_LOW_SOC     = 4, /* Заборонено: недостатній рівень заряду */
    OTA_BATTERY_DENY_HIGH_ESR    = 5, /* Заборонено: високе просідання під навантаженням */
    OTA_BATTERY_DENY_SENSOR_FAIL = 6  /* Заборонено: апаратний збій вимірювальних кіл */
} ota_battery_verdict_t;

/* Структура конфігурації безпекових порогів */
typedef struct {
    int16_t  temp_min_c;          /* Мінімальна температура (+5 °C) */
    int16_t  temp_max_c;          /* Максимальна температура (+45 °C) */
    uint8_t  min_soc_percent;     /* Мінімальний SoC (45 %) */
    uint16_t v_bor_safe_mv;       /* Поріг відсікання безпеки BOR (2900 мВ) */
    uint16_t test_load_current_ma;/* Струм тестового навантаження (200 мА) */
    uint16_t ota_peak_current_ma; /* Максимальний піковий струм OTA (320 мА) */
} ota_battery_limits_t;

/* Інтерфейс драйверів апаратної платформи */
typedef struct {
    bool     (*is_vbus_present)(void);
    bool     (*read_temperature_c)(int16_t *out_temp_c);
    bool     (*read_soc_percent)(uint8_t *out_soc);
    uint16_t (*read_voltage_mv)(void);
    void     (*set_test_load)(bool enable);
    void     (*delay_ms)(uint32_t ms);
} ota_platform_hal_t;

/* Головний автомат перевірки допуску */
ota_battery_verdict_t ota_battery_evaluate_safety(
    const ota_platform_hal_t *hal,
    const ota_battery_limits_t *limits,
    uint16_t *out_forecast_mv
) {
    if (!hal || !limits) {
        return OTA_BATTERY_DENY_SENSOR_FAIL;
    }

    /* 1. Перевірка зовнішнього живлення: якщо USB/мережа активна — безумовний пуск */
    if (hal->is_vbus_present && hal->is_vbus_present()) {
        if (out_forecast_mv) {
            *out_forecast_mv = hal->read_voltage_mv();
        }
        return OTA_BATTERY_ALLOW_AC_POWERED;
    }

    /* 2. Валідація температури комірки */
    int16_t temp_c = 0;
    if (!hal->read_temperature_c || !hal->read_temperature_c(&temp_c)) {
        return OTA_BATTERY_DENY_SENSOR_FAIL;
    }
    if (temp_c < limits->temp_min_c) {
        return OTA_BATTERY_DENY_COLD;
    }
    if (temp_c > limits->temp_max_c) {
        return OTA_BATTERY_DENY_HOT;
    }

    /* 3. Валідація стану заряду (SoC) */
    uint8_t soc = 0;
    if (!hal->read_soc_percent || !hal->read_soc_percent(&soc)) {
        return OTA_BATTERY_DENY_SENSOR_FAIL;
    }
    if (soc < limits->min_soc_percent) {
        return OTA_BATTERY_DENY_LOW_SOC;
    }

    /* 4. Активний імпульсний стрес-тест просідання напруги */
    uint16_t v_idle_mv = hal->read_voltage_mv();
    if (v_idle_mv < limits->v_bor_safe_mv) {
        return OTA_BATTERY_DENY_LOW_SOC;
    }

    /* Вмикаємо каліброване тестове навантаження на 15 мс */
    hal->set_test_load(true);
    hal->delay_ms(15);
    uint16_t v_load_mv = hal->read_voltage_mv();
    hal->set_test_load(false);

    /* Обов'язкова пауза релаксації після тестового імпульсу */
    hal->delay_ms(50);

    if (v_load_mv > v_idle_mv) {
        /* Аномалія вимірювання напруги */
        return OTA_BATTERY_DENY_SENSOR_FAIL;
    }

    uint16_t delta_v_test_mv = v_idle_mv - v_load_mv;

    /* Розрахунок прогнозованого просідання під піковим струмом OTA:
       Delta_V_ota = Delta_V_test * (I_ota_peak / I_test) */
    uint32_t delta_v_ota_mv = ((uint32_t)delta_v_test_mv * limits->ota_peak_current_ma) 
                            / limits->test_load_current_ma;

    if (delta_v_ota_mv >= v_idle_mv) {
        return OTA_BATTERY_DENY_HIGH_ESR;
    }

    uint16_t v_forecast_mv = (uint16_t)(v_idle_mv - delta_v_ota_mv);

    if (out_forecast_mv) {
        *out_forecast_mv = v_forecast_mv;
    }

    /* Перевірка, чи не пробиває прогнозована напруга поріг BOR */
    if (v_forecast_mv < limits->v_bor_safe_mv) {
        return OTA_BATTERY_DENY_HIGH_ESR;
    }

    return OTA_BATTERY_ALLOW_BATTERY_OK;
}
```
```cpp
#include <cstdint>
#include <concepts>
#include <span>
#include <optional>

namespace embedded::power {

/* Результати оцінки стану живлення для OTA */
enum class BatteryVerdict : uint8_t {
    AllowAcPowered,  // Дозволено: живлення від зовнішнього джерела
    AllowBatteryOk,  // Дозволено: параметри акумулятора в нормі
    DenyCold,        // Заборонено: температура надто низька
    DenyHot,         // Заборонено: температура надто висока
    DenyLowSoc,      // Заборонено: недостатній рівень заряду
    DenyHighEsr,     // Заборонено: небезпечне динамічне просідання
    DenySensorFail   // Заборонено: збій апаратних давачів
};

/* Налаштування безпекових меж */
struct SafetyLimits {
    int16_t  tempMinC           = 5;     // +5 °C
    int16_t  tempMaxC           = 45;    // +45 °C
    uint8_t  minSocPercent      = 45;    // 45 %
    uint16_t vBorSafeMv         = 2900;  // 2.90 В
    uint16_t testLoadCurrentMa  = 200;   // 200 мА
    uint16_t otaPeakCurrentMa   = 320;   // 320 мА
};

/* Результат детальної перевірки */
struct CheckResult {
    BatteryVerdict verdict;
    uint16_t       forecastVoltageMv;
    uint16_t       measuredEsrMilliOhm;
};

/* Концепт для апаратного рівня абстракції */
template <typename T>
concept PowerPlatformHal = requires(T hal, bool enable, uint32_t ms) {
    { hal.isVbusPresent() } -> std::same_as<bool>;
    { hal.readTemperatureC() } -> std::same_as<std::optional<int16_t>>;
    { hal.readSocPercent() } -> std::same_as<std::optional<uint8_t>>;
    { hal.readVoltageMv() } -> std::same_as<uint16_t>;
    { hal.setTestLoad(enable) } -> std::same_as<void>;
    { hal.delayMs(ms) } -> std::same_as<void>;
};

/* Автомат безпечного допуску до OTA */
template <PowerPlatformHal THal>
class BatteryPreflightSupervisor {
public:
    constexpr explicit BatteryPreflightSupervisor(const SafetyLimits& limits = {})
        : m_limits(limits) {}

    [[nodiscard]] CheckResult evaluate(THal& hal) const noexcept {
        // 1. Якщо підключено мережевий адаптер або USB — повний допуск
        if (hal.isVbusPresent()) {
            return {
                .verdict = BatteryVerdict::AllowAcPowered,
                .forecastVoltageMv = hal.readVoltageMv(),
                .measuredEsrMilliOhm = 0
            };
        }

        // 2. Перевірка температури комірки
        const auto tempC = hal.readTemperatureC();
        if (!tempC.has_value()) {
            return {.verdict = BatteryVerdict::DenySensorFail, .forecastVoltageMv = 0, .measuredEsrMilliOhm = 0};
        }
        if (*tempC < m_limits.tempMinC) {
            return {.verdict = BatteryVerdict::DenyCold, .forecastVoltageMv = 0, .measuredEsrMilliOhm = 0};
        }
        if (*tempC > m_limits.tempMaxC) {
            return {.verdict = BatteryVerdict::DenyHot, .forecastVoltageMv = 0, .measuredEsrMilliOhm = 0};
        }

        // 3. Перевірка рівня заряду (SoC)
        const auto soc = hal.readSocPercent();
        if (!soc.has_value()) {
            return {.verdict = BatteryVerdict::DenySensorFail, .forecastVoltageMv = 0, .measuredEsrMilliOhm = 0};
        }
        if (*soc < m_limits.minSocPercent) {
            return {.verdict = BatteryVerdict::DenyLowSoc, .forecastVoltageMv = 0, .measuredEsrMilliOhm = 0};
        }

        // 4. Активний стрес-тест імпедансу комірки
        const uint16_t vIdle = hal.readVoltageMv();
        if (vIdle < m_limits.vBorSafeMv) {
            return {.verdict = BatteryVerdict::DenyLowSoc, .forecastVoltageMv = vIdle, .measuredEsrMilliOhm = 0};
        }

        // Вмикаємо навантаження на 15 мілісекунд
        hal.setTestLoad(true);
        hal.delayMs(15);
        const uint16_t vLoad = hal.readVoltageMv();
        hal.setTestLoad(false);

        // Пауза релаксації для відновлення хімічного стану поверхні електродів
        hal.delayMs(50);

        if (vLoad > vIdle) {
            return {.verdict = BatteryVerdict::DenySensorFail, .forecastVoltageMv = 0, .measuredEsrMilliOhm = 0};
        }

        const uint16_t deltaVTest = vIdle - vLoad;
        const auto esrMilliOhm = static_cast<uint16_t>(
            (static_cast<uint32_t>(deltaVTest) * 1000) / m_limits.testLoadCurrentMa
        );

        const auto deltaVOta = static_cast<uint32_t>(
            (static_cast<uint32_t>(deltaVTest) * m_limits.otaPeakCurrentMa) / m_limits.testLoadCurrentMa
        );

        if (deltaVOta >= vIdle) {
            return {.verdict = BatteryVerdict::DenyHighEsr, .forecastVoltageMv = 0, .measuredEsrMilliOhm = esrMilliOhm};
        }

        const auto vForecast = static_cast<uint16_t>(vIdle - deltaVOta);

        if (vForecast < m_limits.vBorSafeMv) {
            return {
                .verdict = BatteryVerdict::DenyHighEsr,
                .forecastVoltageMv = vForecast,
                .measuredEsrMilliOhm = esrMilliOhm
            };
        }

        return {
            .verdict = BatteryVerdict::AllowBatteryOk,
            .forecastVoltageMv = vForecast,
            .measuredEsrMilliOhm = esrMilliOhm
        };
    }

private:
    SafetyLimits m_limits;
};

} // namespace embedded::power
```
:::

---

### Протокольна телеметрія відхилених запитів для сервера кампанії

Коли автомат блокує оновлення, прошивка надсилає у відповідь на команду сервера оновлень структурований пакет телеметрії із зазначенням причини та рекомендованого вікна повторної спроби (англ. *Retry-After Interval*):

- **Код `OTA_RETRY_COLD` (`DenyCold`):** Сервер отримує значення поточної температури (наприклад, `-2 °C`) і відкладає надсилання завдання на 6–8 годин, очікуючи денного прогріву пристрою прямим сонячним промінням.
- **Код `OTA_RETRY_LOW_SOC` (`DenyLowSoc`):** Повідомляє про поточний заряд (наприклад, `28%`) та необхідність підзарядки або заміни батареї.
- **Код `OTA_ALERT_HIGH_ESR` (`DenyHighEsr`):** Передає розрахований внутрішній опір комірки (наприклад, `850 мОм`). Сервер фіксує апаратну деградацію батареї (State of Health) і генерує сервісну задачу для техніка, не витрачаючи енергію на подальші безплідні спроби зв'язку.

Такий зворотний зв'язок перетворює сліпу кампанію розсилки прошивок на інтелектуальний польовий процес, захищений від масового самознищення парку пристроїв.
