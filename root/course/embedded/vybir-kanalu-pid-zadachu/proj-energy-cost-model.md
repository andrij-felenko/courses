# ⚙️ Моделювання енергетичного балансу та вартості сеансу зв'язку

Коли інженер проєктує автономний вбудований вузол, паспорти компонентів надають лише розрізнені статичні числа: струм сну 2 мкА, струм випромінювача 30 мА, швидкість передачі 125 кбіт/с. Спроба обчислити термін служби пристрою за наївною формулою ділення номінальної ємності батареї на струм активної передачі дає похибку в 3–5 разів. Реальний сеанс зв'язку — це динамічний процес, у якому левова частка заряду витрачається на невидимі фази: стабілізацію кварцового генератора, розгін синтезатора частоти PLL, прослуховування ефіру в очікуванні квітанції підтвердження (ACK), внутрішні затримки стеку протоколів, перехідні процеси вимкнення DC-DC перетворювача та фоновий саморозряд джерела живлення.

Нижче наведено завершену фізичну модель та програмний калькулятор мовами C та C++, який розраховує заряд однієї транзакції для чотирьох типів бездротових інтерфейсів (BLE 5.0, LoRaWAN на коефіцієнтах SF7 та SF12, NB-IoT у режимі збереження енергії PSM та LTE Cat-1) і визначає реальну багаторічну автономність системи.

## Фізична модель фаз сеансу зв'язку

Енергетичний профіль будь-якого циклу виходу на зв'язок розбивається на чотири послідовні фази з різним рівнем споживання:

1. **Фаза пробудження та ініціалізації (`t_prep`, `I_prep`):** вихід ядра мікроконтролера та радіочипа з режиму глибокого сну. На цьому етапі вмикається внутрішній DC-DC конвертер, запускається високочастотний кварцовий резонатор (HFXO на 32–40 МГц), стабілізується фазове автопідстроювання частоти (PLL) та завантажуються конфігураційні регістри радіотракту через шину SPI або внутрішню шину SoC. Струм на цій фазі становить від 4 до 30 мА, а тривалість варіюється від 1.5 мс для мікроконтролерів BLE до 250–2500 мс для стільникових модемів, які відновлюють синхронізацію з базовою станцією.
2. **Фаза передачі корисного навантаження (`t_tx`, `I_tx`):** безпосереднє випромінювання радіохвилі вихідним підсилювачем потужності (PA). Тривалість фази прямо залежить від сумарної кількості бітів (корисне навантаження плюс службові заголовки MAC/PHY) та бітової швидкості модуляції:
```
t_tx = (Payload_bytes + Header_bytes) · 8 / Bitrate_bps
```
3. **Фаза прийому та квітування (`t_rx`, `I_rx`):** активне прослуховування ефіру. Для BLE це прийом короткого пакета ACK за 1 мс; для LoRaWAN — це відкриття двох приймальних вікон RX1 та RX2 через 1 та 2 секунди після передачі; для стільникових модулів — це утримання радіоканалу RRC Connected у режимі Discontinuous Reception (DRX) для отримання підтверджень на рівні протоколів TCP або CoAP.
4. **Фаза деініціалізації та засинання (`t_post`, `I_post`):** збереження криптографічних лічильників і параметрів з'єднання в Retention RAM або EEPROM, скидання буферів DMA та вимкнення живлення периферійних аналогових блоків.

Сумарний електричний заряд `Q_cycle`, витрачений вузлом на виконання одного повного циклу виходу на зв'язок, визначається сумою витрат кожної фази:

```
Q_cycle = I_prep · t_prep + I_tx · t_tx + I_rx · t_rx + I_post · t_post
```

Отримане значення виражається в міліампер-секундах (мА·с), що еквівалентно мілікулонам (мКл).

## Інтеграція споживання та саморозряд батареї

Якщо пристрій виконує один сеанс передачі з інтервалом у `T_period` секунд, а решту часу перебуває в режимі сну зі струмом `I_sleep` (який враховує струм сну радіомодуля, мікроконтролера, годинника RTC та струм витоку блокувальних конденсаторів), середній струм споживання схеми становить:

```
I_avg = (Q_cycle / T_period) + I_sleep
```

Для визначення тривалості життя батареї не можна просто поділити номінальну ємність `C_nom` на середній струм `I_avg`. Необхідно врахувати два нелінійні фактори деградації:
1. **Річний саморозряд хімічного джерела (`K_self` у %/рік):** у якісних літій-тіонілхлоридних батареях Li-SOCl₂ він становить 1–1.5% на рік, у літій-марганцевих Li-MnO₂ — близько 1.5–2.5% на рік, а в звичайних лужних елементах може сягати 5–10% на рік. Струм витоку від саморозряду додається до фонового струму споживання:
```
I_self = (C_nom · (K_self / 100)) / 8766 годин
```
2. **Коефіцієнт експлуатаційного запасу (`eta`):** запас на роботу при низьких температурах (до −20 °C), просідання напруги під імпульсним навантаженням та неможливість розрядити батарею до абсолютного нуля через мінімальну робочу напругу перетворювача. Для вуличних умов типове значення становить `eta = 0.70...0.85`.

Результуючий термін автономної роботи в роках обчислюється як:

```
T_years = (C_nom · eta) / ((I_avg + I_self) · 8766 годин)
```

## Реалізація калькулятора енергії

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    const char *name;
    float prep_time_s;       /* Час підготовки до передачі (с) */
    float prep_current_ma;   /* Струм підготовки (мА) */
    float tx_power_ma;       /* Струм випромінювача (мА) */
    float tx_speed_kbps;     /* Ефективна швидкість каналу (кбіт/с) */
    float header_bytes;      /* Службові заголовки протоколу (байти) */
    float rx_time_s;         /* Час очікування підтвердження / RX (с) */
    float rx_current_ma;     /* Струм приймача під час RX (мА) */
    float post_time_s;       /* Час переходу в сон (с) */
    float post_current_ma;   /* Струм переходу в сон (мА) */
    float sleep_current_ua;  /* Струм глибокого сну радіомодуля (мкА) */
} RadioProfile;

typedef struct {
    float battery_capacity_mah;  /* Номінальна ємність джерела живлення */
    float self_discharge_pct_yr; /* Річний саморозряд батареї (%) */
    float derating_factor;       /* Температурний/імпульсний коефіцієнт (0.7-0.9) */
    float system_sleep_ua;       /* Фоновий струм MCU та датчиків у сні (мкА) */
} PowerSource;

typedef struct {
    float cycle_charge_mas;      /* Заряд однієї передачі (мА*с) */
    float avg_current_ua;        /* Середній струм споживання (мкА) */
    float battery_life_years;    /* Очікуваний термін роботи (років) */
    float airtime_ms;            /* Чистий час у ефірі (мс) */
} EnergyResult;

bool evaluate_energy_profile(const RadioProfile *prof,
                             const PowerSource *pwr,
                             uint32_t payload_bytes,
                             uint32_t interval_seconds,
                             EnergyResult *out_res) {
    if (!prof || !pwr || !out_res || interval_seconds == 0) {
        return false;
    }

    float total_bytes = (float)payload_bytes + prof->header_bytes;
    float bits = total_bytes * 8.0f;
    float tx_time_s = (prof->tx_speed_kbps > 0.0f) 
                      ? (bits / (prof->tx_speed_kbps * 1000.0f)) 
                      : 0.001f;

    /* Обчислення заряду за фазами (мА * с) */
    float q_prep = prof->prep_current_ma * prof->prep_time_s;
    float q_tx   = prof->tx_power_ma * tx_time_s;
    float q_rx   = prof->rx_current_ma * prof->rx_time_s;
    float q_post = prof->post_current_ma * prof->post_time_s;
    float q_cycle_mas = q_prep + q_tx + q_rx + q_post;

    /* Струми у сні та середній струм */
    float total_sleep_ua = prof->sleep_current_ua + pwr->system_sleep_ua;
    float cycle_avg_ma = q_cycle_mas / (float)interval_seconds;
    float avg_current_ua = (cycle_avg_ma * 1000.0f) + total_sleep_ua;

    /* Врахування саморозряду батареї */
    float hours_in_year = 365.25f * 24.0f;
    float self_discharge_ma = (pwr->battery_capacity_mah * (pwr->self_discharge_pct_yr / 100.0f)) 
                              / hours_in_year;
    float self_discharge_ua = self_discharge_ma * 1000.0f;

    float effective_capacity_mah = pwr->battery_capacity_mah * pwr->derating_factor;
    float total_drain_ua = avg_current_ua + self_discharge_ua;

    float life_hours = (total_drain_ua > 0.0f) 
                       ? (effective_capacity_mah * 1000.0f / total_drain_ua) 
                       : 0.0f;
    float life_years = life_hours / hours_in_year;

    out_res->cycle_charge_mas   = q_cycle_mas;
    out_res->avg_current_ua     = avg_current_ua;
    out_res->battery_life_years = life_years;
    out_res->airtime_ms         = tx_time_s * 1000.0f;

    return true;
}

int main(void) {
    /* Базові профілі трансиверів для телеметрії */
    const RadioProfile profiles[] = {
        {
            .name = "BLE 5.0 (2 Mbps)",
            .prep_time_s = 0.0015f, .prep_current_ma = 4.0f,
            .tx_power_ma = 12.0f,   .tx_speed_kbps = 1400.0f,
            .header_bytes = 14.0f,
            .rx_time_s = 0.0010f,   .rx_current_ma = 8.0f,
            .post_time_s = 0.0005f, .post_current_ma = 2.0f,
            .sleep_current_ua = 1.2f
        },
        {
            .name = "LoRaWAN EU868 (SF7, BW125)",
            .prep_time_s = 0.0050f, .prep_current_ma = 6.0f,
            .tx_power_ma = 35.0f,   .tx_speed_kbps = 5.47f,
            .header_bytes = 13.0f,
            .rx_time_s = 0.0600f,   .rx_current_ma = 11.0f,
            .post_time_s = 0.0020f, .post_current_ma = 3.0f,
            .sleep_current_ua = 1.5f
        },
        {
            .name = "LoRaWAN EU868 (SF12, BW125)",
            .prep_time_s = 0.0050f, .prep_current_ma = 6.0f,
            .tx_power_ma = 35.0f,   .tx_speed_kbps = 0.29f,
            .header_bytes = 13.0f,
            .rx_time_s = 0.3500f,   .rx_current_ma = 11.0f,
            .post_time_s = 0.0020f, .post_current_ma = 3.0f,
            .sleep_current_ua = 1.5f
        },
        {
            .name = "NB-IoT (PSM Mode, 23 dBm)",
            .prep_time_s = 0.2500f, .prep_current_ma = 25.0f,
            .tx_power_ma = 180.0f,  .tx_speed_kbps = 32.0f,
            .header_bytes = 48.0f,
            .rx_time_s = 0.8000f,   .rx_current_ma = 40.0f,
            .post_time_s = 0.0500f, .post_current_ma = 15.0f,
            .sleep_current_ua = 3.5f
        },
        {
            .name = "LTE Cat-1 (Active / Disconnect)",
            .prep_time_s = 2.5000f, .prep_current_ma = 80.0f,
            .tx_power_ma = 260.0f,  .tx_speed_kbps = 1000.0f,
            .header_bytes = 90.0f,
            .rx_time_s = 1.5000f,   .rx_current_ma = 65.0f,
            .post_time_s = 0.3000f, .post_current_ma = 40.0f,
            .sleep_current_ua = 15.0f
        }
    };

    /* Літієва батарея Li-SOCl2 типорозміру AA (3.6 В, 2600 мА*год) */
    const PowerSource battery = {
        .battery_capacity_mah = 2600.0f,
        .self_discharge_pct_yr = 1.0f,
        .derating_factor = 0.85f,
        .system_sleep_ua = 2.0f
    };

    const uint32_t payload_len = 24;            /* 24 байти показів давачів */
    const uint32_t send_period = 3600;          /* 1 раз на годину */

    size_t count = sizeof(profiles) / sizeof(profiles[0]);
    for (size_t i = 0; i < count; ++i) {
        EnergyResult res;
        if (evaluate_energy_profile(&profiles[i], &battery, payload_len, send_period, &res)) {
            printf("[%s]\n", profiles[i].name);
            printf("  Час у ефірі: %.1f мс\n", res.airtime_ms);
            printf("  Заряд сеансу: %.3f мА*с\n", res.cycle_charge_mas);
            printf("  Середній струм: %.2f мкА\n", res.avg_current_ua);
            printf("  Автономність: %.2f років\n\n", res.battery_life_years);
        }
    }

    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <string_view>
#include <array>
#include <span>
#include <iomanip>
#include <cmath>

struct RadioProfile {
    std::string_view name;
    float prep_time_s;       // Час підготовки до передачі (с)
    float prep_current_ma;   // Струм підготовки (мА)
    float tx_power_ma;       // Струм випромінювача (мА)
    float tx_speed_kbps;     // Ефективна швидкість каналу (кбіт/с)
    float header_bytes;      // Службові заголовки протоколу (байти)
    float rx_time_s;         // Час очікування підтвердження / RX (с)
    float rx_current_ma;     // Струм приймача під час RX (мА)
    float post_time_s;       // Час переходу в сон (с)
    float post_current_ma;   // Струм переходу в сон (мА)
    float sleep_current_ua;  // Струм глибокого сну радіомодуля (мкА)
};

struct PowerSource {
    float battery_capacity_mah;  // Номінальна ємність джерела живлення
    float self_discharge_pct_yr; // Річний саморозряд батареї (%)
    float derating_factor;       // Температурний/імпульсний коефіцієнт (0.7-0.9)
    float system_sleep_ua;       // Фоновий струм MCU та датчиків у сні (мкА)
};

struct EnergyResult {
    float cycle_charge_mas{0.0f};   // Заряд однієї передачі (мА*с)
    float avg_current_ua{0.0f};     // Середній струм споживання (мкА)
    float battery_life_years{0.0f}; // Очікуваний термін роботи (років)
    float airtime_ms{0.0f};         // Чистий час у ефірі (мс)
};

class EnergyBudgetCalculator {
public:
    [[nodiscard]] static constexpr EnergyResult evaluate(
        const RadioProfile& prof,
        const PowerSource& pwr,
        uint32_t payload_bytes,
        uint32_t interval_seconds) noexcept {
        if (interval_seconds == 0) {
            return {};
        }

        const float total_bytes = static_cast<float>(payload_bytes) + prof.header_bytes;
        const float bits = total_bytes * 8.0f;
        const float tx_time_s = (prof.tx_speed_kbps > 0.0f)
                                ? (bits / (prof.tx_speed_kbps * 1000.0f))
                                : 0.001f;

        // Обчислення заряду за фазами транзакції (мА * с)
        const float q_prep = prof.prep_current_ma * prof.prep_time_s;
        const float q_tx   = prof.tx_power_ma * tx_time_s;
        const float q_rx   = prof.rx_current_ma * prof.rx_time_s;
        const float q_post = prof.post_current_ma * prof.post_time_s;
        const float q_cycle_mas = q_prep + q_tx + q_rx + q_post;

        // Струми у сні та середній струм системи
        const float total_sleep_ua = prof.sleep_current_ua + pwr.system_sleep_ua;
        const float cycle_avg_ma = q_cycle_mas / static_cast<float>(interval_seconds);
        const float avg_current_ua = (cycle_avg_ma * 1000.0f) + total_sleep_ua;

        // Розрахунок впливу саморозряду батареї
        constexpr float hours_in_year = 365.25f * 24.0f;
        const float self_discharge_ma = (pwr.battery_capacity_mah * (pwr.self_discharge_pct_yr / 100.0f))
                                        / hours_in_year;
        const float self_discharge_ua = self_discharge_ma * 1000.0f;

        const float effective_capacity_mah = pwr.battery_capacity_mah * pwr.derating_factor;
        const float total_drain_ua = avg_current_ua + self_discharge_ua;

        const float life_hours = (total_drain_ua > 0.0f)
                                 ? (effective_capacity_mah * 1000.0f / total_drain_ua)
                                 : 0.0f;
        const float life_years = life_hours / hours_in_year;

        return {
            .cycle_charge_mas = q_cycle_mas,
            .avg_current_ua = avg_current_ua,
            .battery_life_years = life_years,
            .airtime_ms = tx_time_s * 1000.0f
        };
    }
};

int main() {
    constexpr std::array profiles{
        RadioProfile{
            .name = "BLE 5.0 (2 Mbps)",
            .prep_time_s = 0.0015f, .prep_current_ma = 4.0f,
            .tx_power_ma = 12.0f,   .tx_speed_kbps = 1400.0f,
            .header_bytes = 14.0f,
            .rx_time_s = 0.0010f,   .rx_current_ma = 8.0f,
            .post_time_s = 0.0005f, .post_current_ma = 2.0f,
            .sleep_current_ua = 1.2f
        },
        RadioProfile{
            .name = "LoRaWAN EU868 (SF7, BW125)",
            .prep_time_s = 0.0050f, .prep_current_ma = 6.0f,
            .tx_power_ma = 35.0f,   .tx_speed_kbps = 5.47f,
            .header_bytes = 13.0f,
            .rx_time_s = 0.0600f,   .rx_current_ma = 11.0f,
            .post_time_s = 0.0020f, .post_current_ma = 3.0f,
            .sleep_current_ua = 1.5f
        },
        RadioProfile{
            .name = "LoRaWAN EU868 (SF12, BW125)",
            .prep_time_s = 0.0050f, .prep_current_ma = 6.0f,
            .tx_power_ma = 35.0f,   .tx_speed_kbps = 0.29f,
            .header_bytes = 13.0f,
            .rx_time_s = 0.3500f,   .rx_current_ma = 11.0f,
            .post_time_s = 0.0020f, .post_current_ma = 3.0f,
            .sleep_current_ua = 1.5f
        },
        RadioProfile{
            .name = "NB-IoT (PSM Mode, 23 dBm)",
            .prep_time_s = 0.2500f, .prep_current_ma = 25.0f,
            .tx_power_ma = 180.0f,  .tx_speed_kbps = 32.0f,
            .header_bytes = 48.0f,
            .rx_time_s = 0.8000f,   .rx_current_ma = 40.0f,
            .post_time_s = 0.0500f, .post_current_ma = 15.0f,
            .sleep_current_ua = 3.5f
        },
        RadioProfile{
            .name = "LTE Cat-1 (Active / Disconnect)",
            .prep_time_s = 2.5000f, .prep_current_ma = 80.0f,
            .tx_power_ma = 260.0f,  .tx_speed_kbps = 1000.0f,
            .header_bytes = 90.0f,
            .rx_time_s = 1.5000f,   .rx_current_ma = 65.0f,
            .post_time_s = 0.3000f, .post_current_ma = 40.0f,
            .sleep_current_ua = 15.0f
        }
    };

    constexpr PowerSource battery{
        .battery_capacity_mah = 2600.0f,
        .self_discharge_pct_yr = 1.0f,
        .derating_factor = 0.85f,
        .system_sleep_ua = 2.0f
    };

    constexpr uint32_t payload_len = 24;
    constexpr uint32_t send_period = 3600;

    std::cout << std::fixed << std::setprecision(2);
    for (const auto& prof : profiles) {
        const auto res = EnergyBudgetCalculator::evaluate(prof, battery, payload_len, send_period);
        std::cout << "[" << prof.name << "]\n";
        std::cout << "  Час у ефірі: " << res.airtime_ms << " мс\n";
        std::cout << "  Заряд сеансу: " << std::setprecision(3) << res.cycle_charge_mas << " мА*с\n";
        std::cout << "  Середній струм: " << std::setprecision(2) << res.avg_current_ua << " мкА\n";
        std::cout << "  Автономність: " << res.battery_life_years << " років\n\n";
    }

    return 0;
}
```
:::

## Інженерні пастки розрахунку автономності

1. **Імпульсне просідання напруги (IR-Drop):** Дискові елементи CR2032 та літій-тіонілхлоридні комірки Li-SOCl₂ мають високий внутрішній опір (10–30 Ом для CR2032 і до 5–15 Ом для пасивованої Li-SOCl₂). Імпульс струму 180–500 мА від стільникового передавача миттєво просаджує напругу живлення нижче порогу Brown-Out Reset (BOR) мікроконтролера. Без паралельного підключення гібридного імпульсного конденсатора (HPC) або суперконденсатора розрахункова ємність акумулятора виявляється недосяжною.
2. **Пасивація літію:** При тривалому зберіганні та роботі в мікрострумовому режимі (<10 мкА) на аноді Li-SOCl₂ наростає діелектрична плівка хлориду літію (LiCl). Перший сплеск струму після місяців сну викликає різке просідання напруги до 1.5–2.0 В на десятки мілісекунд, поки плівка не зруйнується. Прошивка повинна передбачати процедуру депасивації (короткі контрольовані імпульси струму перед запуском передавача).
3. **Температурний коефіцієнт:** При падінні температури до −20 °C ефективна віддача хімічних джерел падає на 30–50%, а внутрішній опір зростає в 3–5 разів. Закладання `derating_factor = 0.85` є оптимістичним для кімнатних умов; для вуличного встановлення в помірному кліматі слід використовувати коефіцієнт 0.55–0.65.
4. **Витоки через керамічні та електролітичні конденсатори:** Танталові та багатошарові керамічні конденсатори (MLCC) великої ємності (100–470 мкФ) у ланцюгах живлення модема мають струм витоку порядку 2–10 мкА при кімнатній температурі, який подвоюється на кожні 10 °C підвищення температури. Якщо схема споживає 2 мкА в режимі сну, а конденсатор витікає на 8 мкА, реальний термін служби батареї скорочується у п'ять разів. Необхідно обирати конденсатори з низьким струмом витоку або відсікати їх за допомогою P-канального польового транзистора (Power Gating).
5. **Методика інструментальної верифікації:** Теоретичні розрахунки обов'язково верифікують на реальному залізі за допомогою спеціалізованих вимірювальних приладів із динамічним діапазоном (Power Profiler Kit, Joulescope або прецизійний електрометр Keithley). Звичайний цифровий мультиметр непридатний для вимірювання струмового профілю вбудованих пристроїв, оскільки через власний внутрішній шунт він спотворює вимірювання в моменти переходу від наноамперів до сотень міліампер і викликає штучне перезавантаження схеми.
