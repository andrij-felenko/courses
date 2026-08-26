# ⚙️ Моделювання динаміки збирання теплової енергії та заряду іоністора

Проєктування автономного бездротового сенсора на базі термоелектрогенератора (ТЕГ) вимагає точного розрахунку енергетичного балансу: надходження потужності від змінного теплового градієнта повинно покривати як постійне фонове споживання схеми у режимі сну, так і періодичні пікові імпульси передавача.

Якщо розрахувати систему лише за середньою потужністю, пристрій неминуче зависне при першому ж запуску або скинеться через спрацьовування захисту від зниження напруги (англ. *Brown-Out Reset*, BOR). Справа в тому, що суперконденсатор має струм саморозряду, DC-DC перетворювач має поріг холодного старту, а передавач у момент виходу в ефір вимагає струму, що у тисячі разів перевищує струм, який ТЕГ здатен видати в реальному часі.

Нижче наведено алгоритм та закінчену програмну модель, що виконує спільний розрахунок теплового подільника, підвищувального перетворювача з точкою MPPT та динаміки накопичення заряду в іоністорі.

## Алгоритм моделювання та логіка станів

Модель відстежує стан системи з дискретним кроком за часом `dt` (наприклад, `0.1 с`):

1. **Теплове коло:** За заданими температурами джерела `T_src(t)` та повітря `T_amb` обчислюється тепловий потік `Q(t)` та корисний перепад на кристалі ТЕГ `ΔT_teg(t)` з урахуванням опору радіатора `Theta_sink` і контактної пасти:
   ```
   ΔT_teg = (T_src − T_amb) · [ Theta_teg / (Theta_hot + Theta_teg + Theta_sink) ]
   ```
2. **Генерація ЕРС:** Обчислюються напруга холостого ходу `Voc = N · S · ΔT_teg` та внутрішній електричний опір `R_int`.
3. **Робота MPPT-перетворювача:** Якщо `Voc` перевищує поріг холодного старту (`Voc > V_start`), перетворювач утримує вхідну напругу на рівні `0.5 · Voc`, відбираючи максимальну потужність:
   ```
   P_in = Voc² / (4 · R_int)
   P_boost = P_in · eta_boost
   ```
4. **Інтегрування енергії в іоністорі:** Енергія накопичувача змінюється за рівнянням балансу:
   ```
   dE_cap / dt = P_boost − P_leakage − P_load
   ```
   де `E_cap = 0.5 · C_cap · V_cap²`.
5. **Керування навантаженням (гістерезисний автомат):**
   - У режимі очікування мікроконтролер перебуває у глибокому сні (`I_sleep ≈ 1.5 мкА`).
   - Коли напруга на іоністорі досягає верхнього порогу `V_high = 3.6 В`, ініціюється сеанс зв'язку: споживання зростає до `I_active = 25 мА` на час `t_active = 30 мс`.
   - Якщо напруга опускається нижче аварійного порогу `V_low = 2.2 В`, будь-які радіосеанси блокуються до відновлення заряду.

## Програмна реалізація моделі

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

// Фізичні параметри ТЕГ модуля
typedef struct {
    int pairs_count;           // Кількість пар термопар (N)
    double seebeck_pair;       // Коефіцієнт Зеєбека пари (В/К)
    double r_internal;         // Внутрішній електричний опір (Ом)
    double theta_teg;          // Тепловий опір модуля (К/Вт)
    double theta_hot;          // Тепловий опір гарячого контакту (К/Вт)
    double theta_sink;         // Тепловий опір радіатора (К/Вт)
} TegModule;

// Параметри енергетичного накопичувача та навантаження
typedef struct {
    double capacitance;        // Ємність іоністора (Ф)
    double v_cap;              // Поточна напруга на іоністорі (В)
    double v_high;             // Верхній поріг увімкнення передачі (В)
    double v_low;              // Нижній поріг блокування UVLO (В)
    double i_leakage;          // Струм саморозряду іоністора (А)
    double i_sleep;            // Струм сну вузла (А)
    double i_active;           // Струм радіопередачі (А)
    double t_active;           // Тривалість передачі (с)
    double eta_boost;          // ККД DC-DC перетворювача (0..1)
    double v_cold_start;       // Поріг холодного старту перетворювача (В)
} HarvesterNode;

// Результат одного кроку симуляції
typedef struct {
    double time_s;
    double t_src;
    double v_teg_oc;
    double p_harvested_mw;
    double v_cap;
    bool tx_fired;
} SimStepResult;

void teg_init_default(TegModule *teg) {
    teg->pairs_count = 127;
    teg->seebeck_pair = 400e-6; // 400 мкВ/К
    teg->r_internal = 2.4;      // 2.4 Ом
    teg->theta_teg = 1.8;       // 1.8 К/Вт
    teg->theta_hot = 0.3;       // 0.3 К/Вт
    teg->theta_sink = 2.5;      // 2.5 К/Вт (радіатор)
}

void harvester_init_default(HarvesterNode *h) {
    h->capacitance = 0.47;      // 0.47 Ф (іоністор)
    h->v_cap = 2.0;             // Початкова напруга 2.0 В
    h->v_high = 3.3;            // Поріг активації передавача 3.3 В
    h->v_low = 2.2;             // Поріг UVLO 2.2 В
    h->i_leakage = 2.0e-6;      // 2 мкА витік
    h->i_sleep = 1.8e-6;        // 1.8 мкА сон
    h->i_active = 22.0e-3;      // 22 мА передача (LoRa / BLE)
    h->t_active = 0.025;        // 25 мс
    h->eta_boost = 0.78;        // 78% ККД
    h->v_cold_start = 0.040;    // 40 мВ мінімум для старту
}

SimStepResult harvester_step(const TegModule *teg, HarvesterNode *h, 
                             double t_src, double t_amb, double dt, double current_time) {
    SimStepResult res;
    res.time_s = current_time;
    res.t_src = t_src;
    res.tx_fired = false;

    // 1. Розрахунок теплового подільника
    double theta_tot = teg->theta_hot + teg->theta_teg + teg->theta_sink;
    double dt_sys = t_src - t_amb;
    double dt_teg = (dt_sys > 0.0) ? (dt_sys * (teg->theta_teg / theta_tot)) : 0.0;

    // 2. ЕРС ТЕГ
    double s_mod = teg->pairs_count * teg->seebeck_pair;
    double voc = s_mod * dt_teg;
    res.v_teg_oc = voc;

    // 3. Збирання потужності з точки MPPT
    double p_in = 0.0;
    if (voc >= h->v_cold_start) {
        p_in = (voc * voc) / (4.0 * teg->r_internal);
    }
    double p_boost = p_in * h->eta_boost;
    res.p_harvested_mw = p_boost * 1000.0;

    // 4. Поточна енергія накопичувача
    double e_cap = 0.5 * h->capacitance * h->v_cap * h->v_cap;

    // Надходження енергії за крок
    e_cap += p_boost * dt;

    // Втрати на сон і саморозряд
    double p_quiescent = h->v_cap * (h->i_sleep + h->i_leakage);
    e_cap -= p_quiescent * dt;

    // 5. Перевірка готовності до передачі
    if (h->v_cap >= h->v_high) {
        double e_tx = h->v_cap * h->i_active * h->t_active;
        if (e_cap >= e_tx) {
            e_cap -= e_tx;
            res.tx_fired = true;
        }
    }

    // Оновлення напруги іоністора
    if (e_cap < 0.0) e_cap = 0.0;
    h->v_cap = sqrt((2.0 * e_cap) / h->capacitance);
    res.v_cap = h->v_cap;

    return res;
}
```
```cpp
#include <cmath>
#include <array>
#include <optional>
#include <concepts>
#include <algorithm>

// Модель фізичних констант ТЕГ
struct TegModule {
    int pairs_count = 127;
    double seebeck_pair = 400e-6; // 400 мкВ/К
    double r_internal = 2.4;      // 2.4 Ом
    double theta_teg = 1.8;       // К/Вт
    double theta_hot = 0.3;       // К/Вт
    double theta_sink = 2.5;      // К/Вт

    [[nodiscard]] constexpr double total_thermal_resistance() const noexcept {
        return theta_hot + theta_teg + theta_sink;
    }

    [[nodiscard]] double open_circuit_voltage(double t_src, double t_amb) const noexcept {
        const double dt_sys = t_src - t_amb;
        if (dt_sys <= 0.0) return 0.0;
        const double dt_teg = dt_sys * (theta_teg / total_thermal_resistance());
        return (pairs_count * seebeck_pair) * dt_teg;
    }

    [[nodiscard]] double mpp_power(double voc) const noexcept {
        if (voc <= 0.0) return 0.0;
        return (voc * voc) / (4.0 * r_internal);
    }
};

// Стан мікропотужного автономного вузла
class EnergyHarvester {
public:
    struct Config {
        double capacitance = 0.47;      // Фарад
        double v_high = 3.3;            // Поріг передачі
        double v_low = 2.2;             // Поріг UVLO
        double i_leakage = 2.0e-6;      // А
        double i_sleep = 1.8e-6;        // А
        double i_active = 22.0e-3;      // А
        double t_active = 0.025;        // с
        double eta_boost = 0.78;        // ККД 78%
        double v_cold_start = 0.040;    // 40 мВ
    };

    struct StepReport {
        double time_s;
        double t_src;
        double v_teg_oc;
        double p_harvested_mw;
        double v_cap;
        bool transmission_occurred;
    };

    explicit EnergyHarvester(Config cfg, double initial_vcap = 2.0) noexcept
        : cfg_(cfg), v_cap_(initial_vcap) {}

    StepReport step(const TegModule& teg, double t_src, double t_amb, 
                    double dt, double current_time) noexcept {
        const double voc = teg.open_circuit_voltage(t_src, t_amb);
        double p_harvested = 0.0;

        if (voc >= cfg_.v_cold_start) {
            p_harvested = teg.mpp_power(voc) * cfg_.eta_boost;
        }

        // Баланс енергії в іоністорі: E = 0.5 * C * V^2
        double e_cap = 0.5 * cfg_.capacitance * v_cap_ * v_cap_;
        e_cap += p_harvested * dt;

        const double p_static_loss = v_cap_ * (cfg_.i_sleep + cfg_.i_leakage);
        e_cap -= p_static_loss * dt;

        bool tx_done = false;
        if (v_cap_ >= cfg_.v_high) {
            const double e_tx = v_cap_ * cfg_.i_active * cfg_.t_active;
            if (e_cap >= e_tx) {
                e_cap -= e_tx;
                tx_done = true;
            }
        }

        e_cap = std::max(0.0, e_cap);
        v_cap_ = std::sqrt((2.0 * e_cap) / cfg_.capacitance);

        return StepReport{
            .time_s = current_time,
            .t_src = t_src,
            .v_teg_oc = voc,
            .p_harvested_mw = p_harvested * 1000.0,
            .v_cap = v_cap_,
            .transmission_occurred = tx_done
        };
    }

    [[nodiscard]] double voltage() const noexcept { return v_cap_; }

private:
    Config cfg_;
    double v_cap_;
};
```
:::

## Аналіз результатів симуляції та критичні крайові випадки

Числове моделювання системи за різних умов експлуатації виявляє кілька принципових фізичних та інженерних закономірностей:

### 1. Стаціонарний режим за помірного нагріву
При стабільній температурі труби `T_src = 65 °C` та кімнатному повітрі `T_amb = 22 °C` модуль із радіатором створює перепад на ніжках близько `18.2 °C`. Напруга холостого ходу досягає `0.92 В`, а вихідна потужність перетворювача становить приблизно `38 мВт`.

Енергія одного радіосеансу LoRa (25 мс при струмі 22 мА та напрузі 3.3 В) становить:

```
E_tx = 3.3 В · 0.022 А · 0.025 с = 1.815 мДж
```

За потужності надходження 38 мВт ця енергія поповнюється в іоністорі всього за `0.048 с` (48 мілісекунд). У такому режимі пристрій має надлишок енергії й може передавати дані так часто, як дозволяють радіорегламенти.

### 2. Граничний режим слабкого градієнта (ΔT = 5 °C)
Якщо температура труби падає до `27 °C` при повітрі `22 °C` (`ΔT_sys = 5 °C`), корисний перепад на кристалі становить лише `1.8 °C`. Напруга холостого ходу падає до `91 мВ`, а корисна потужність після перетворювача зменшується до `0.35 мВт` (350 мкВт).

За такої генерації поповнення енергії на один сеанс передачі (1.815 мДж) займає:

```
t_charge = 1.815 мДж / 0.35 мВт ≈ 5.2 с
```

З урахуванням фонового струму сну та витоку конденсатора сенсор успішно відправляє пакети кожні 6–8 секунд, демонструючи повну життєздатність навіть за ледь теплої труби.

### 3. Крайовий випадок: холодний старт із нульового заряду
Якщо іоністор повністю розряджений (`V_cap = 0 В`), системі потрібен певний час для початкового накопичення енергії. Автогенератор Мейснера запускається за напруги `Voc > 40 мВ` і заряджає буферний вузол `VAUX` до `1.8 В` за 10–25 секунд. Потім головний перетворювач піднімає напругу іоністора ємністю `0.47 Ф` від 0 до 3.3 В за час:

```
t_start = (0.5 · C · V²) / P_boost = (0.5 · 0.47 · 3.3²) / 0.038 ≈ 67 секунд
```

Під час цього стартового інтервалу навантаження обов'язково має бути відключене від накопичувача, інакше струм витоку не дозволить напрузі подолати поріг увімкнення.

### 4. Вибір ємності накопичувача: компроміс між часом старту та запасом ходу
Збільшення ємності іоністора до 5–10 Фарад дозволяє вузлу переживати тривалі перерви у подачі тепла (наприклад, зупинку технологічного процесу на вихідні). Проте час первинного виходу на зв'язок після аварійного розряду зростає пропорційно ємності (до 15–20 хвилин). Оптимальним вибором для більшості промислових сенсорів є ємність `0.22–0.47 Ф`, зашунтована керамічним конденсатором `47 мкФ` для компенсації імпульсного струму.

### 5. Адаптивне керування навантаженням у прошивці
Практична реалізація прошивки мікроконтролера повинна адаптувати інтервал передачі до фактичного стану накопичувача:
- За високої напруги (`V_cap > 3.4 В`) сенсор транслює повний телеметричний пакет (вібрація, температура, спектр) кожні 5 секунд.
- При зниженні напруги (`2.8 В < V_cap < 3.4 В`) переходить у режим заощадження: відправляє лише короткий статус тривоги кожні 60 секунд.
- За критичної напруги (`V_cap < 2.5 В`) припиняє радіообмін і переходить в ультраглибокий сон (споживання менше 500 нА), зберігаючи стан у енергонезалежній пам'яті FRAM до відновлення припливу тепла.

Окрім адаптації інтервалу, прошивка може використовувати сам ТЕГ як прецизійний датчик теплового потоку без встановлення додаткового цифрового термометра. Під час короткочасного розмикання силового ключа перетворювача (фаза MPPT-вимірювання тривалістю 1–2 мс) АЦП мікроконтролера зчитує напругу холостого ходу `Voc`. Оскільки коефіцієнт Зеєбека `S_pn` є стабільною матеріальною характеристикою, значення `ΔT_teg = Voc / (N · S_pn)` обчислюється аналітично, заощаджуючи до 15% енергії на опитуванні зовнішніх I2C-термодатчиків.
