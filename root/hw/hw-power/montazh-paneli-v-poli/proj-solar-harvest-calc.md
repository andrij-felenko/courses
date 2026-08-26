# ⚙️ Розрахунок річної енерговиробки автономної панелі на C та C++

Цей модуль реалізує алгоритм моделювання щоденної та погодинної енерговиробки сонячної панелі для автономного мікроконтролерного вузла. Алгоритм враховує географічну широту точки монтажу, кут нахилу модуля, втрати від забруднення пилом (soiling factor) і температурний коефіцієнт потужності напівпровідникового кристала.

## Математична структура алгоритму симуляції

Оцінка сонячної генерації в польових умовах вимагає інтегрування миттєвої потужності протягом світлового дня. Моделювання виконується з кроком у одну годину для кожного з 365 днів календарного року.

На кожному часовому кроці обчислювальний конвеєр виконує такі послідовні перетворення:

1. **Розрахунок сонячного схилення:** за порядковим номером дня року `day ∈ [1, 365]` обчислюється кут схилення `δ` за формулою Купера.
2. **Визначення положення Сонця:** для кожної години доби `h ∈ [0, 23]` розраховується годинний кут `ω = (h + 0.5 - 12) · 15°` (середина інтервалу) та синус висоти Сонця над горизонтом `sin(h_elev) = sin(φ)·sin(δ) + cos(φ)·cos(δ)·cos(ω)`. Якщо `sin(h_elev) ≤ 0`, Сонце знаходиться за горизонтом, і генерація приймається рівною нулю.
3. **Оптична маса атмосфери (Air Mass):** для променів, що проходять крізь товщу атмосфери під кутом `h_elev`, коефіцієнт оптичної маси розраховується за наближенням Кастена: `AM = 1 / (sin(h_elev) + 0.0001)`. Добавка `0.0001` унеможливлює ділення на нуль біля лінії горизонту.
4. **Пряма та дифузна радіація:** прямий нормальний потік визначається за моделлю Мейнела: `G_dir = 1361 · 0.7^(AM^0.678)`. Дифузна компонента чистого неба оцінюється як 12% від прямої радіації: `G_dif = 0.12 · G_dir`.
5. **Проєкція на похилу площину модуля:** обчислюється косинус кута падіння `cos(θ_inc)` з урахуванням азимута модуля `γ_m` та кута нахилу `β`. Якщо `cos(θ_inc) < 0` (Сонце світить у спину панелі), пряма складова скидається в 0. Сумарна інсоляція на похилу поверхню становить: `G_tilt = G_dir · cos(θ_inc) + G_dif · ((1 + cos β) / 2)`.
6. **Теплове моделювання комірки:** робоча температура кремнію `T_cell` перевищує температуру навколишнього повітря `T_amb` через нагрів від поглинених квантів світла: `T_cell = T_amb + G_tilt · ((NOCT - 20) / 800)`. Параметр NOCT (Normal Operating Cell Temperature) береться з паспорта панелі (типово 45 °C при освітленості 800 Вт/м² та температурі повітря 20 °C).
7. **Температурна деградація:** кремнієві p-n переходи мають негативний температурний коефіцієнт потужності `γ_Pmp ≈ -0.38 %/°C`. Зниження напруги холостого ходу зі зростанням температури зменшує віддавану потужність: `k_temp = 1 + (γ_Pmp / 100) · (T_cell - 25)`. У морозні зимові дні при `T_cell = -10 °C` цей коефіцієнт перевищує одиницю (`k_temp ≈ 1.133`), забезпечуючи додатковий приріст потужності на 13.3%.
8. **Втрати від забруднення:** емпіричний фактор `k_soil = 1 - soiling_ratio` зменшує вхідний світловий потік на 3–15% залежно від сезону та кута нахилу.

## Енергетичний баланс автономного вузла

Отримана з моделі сонячна енергія `E_harvest` (Вт·год/добу) не потрапляє до навантаження у повному обсязі. Для коректного визначення автономності системи необхідно враховувати коефіцієнти корисної дії проміжних перетворювачів:

```
E_usable = E_harvest · η_mppt · η_batt_coulomb · η_dc_dc
```

де:
- `η_mppt` — коефіцієнт корисної дії MPPT-перетворювача (типово 0.94–0.97 для синхронних понижувальних перетворювачів на польових транзисторах);
- `η_batt_coulomb` — кулонівська ефективність акумулятора (для літій-залізо-фосфатних акумуляторів LiFePO4 становить 0.95–0.98, для свинцево-кислотних AGM/GEL падає до 0.80–0.85);
- `η_dc_dc` — ККД вихідного імпульсного стабілізатора живлення мікроконтролера та радіотракту (0.88–0.93).

Для надійної цілорічної роботи автономного приладу в помірних широтах України мінімальна добова зимова генерація `E_harvest_min` повинна перевищувати добове споживання системи `E_load_day = P_avg · 24 год` щонайменше у 1.3–1.5 раза з урахуванням втрат у конверторах. Це вимагає вибору номінальної потужності сонячної панелі `P_stc` у 15–25 разів більшої за середнє споживання вузла `P_avg`. Наприклад, для сенсора із середньодобовим споживанням 2 Вт потрібна панель номінальною потужністю не менше 30–50 Вт при куті нахилу 60°.

## Реалізація на C та C++

У реалізації мовою C структури даних організовані у вигляді простих конфігураційних блоків для вбудованих систем без динамічного виділення пам'яті. У версії C++20 застосовано строгу типізацію, простори імен, стандартні математичні константи `<numbers>`, алгоритми `<algorithm>` та атрибути `[[nodiscard]]`.

:::tabs
```c
#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define DEG_TO_RAD(d) ((d) * (M_PI / 180.0))
#define RAD_TO_DEG(r) ((r) * (180.0 / M_PI))

typedef struct {
    double p_stc;         /* Номінальна потужність панелі за STC (Вт) */
    double gamma_pmp;     /* Температурний коефіцієнт Pmax (%/°C, наприклад -0.38) */
    double noct;          /* Нормальна робоча температура комірки (°C, типово 45.0) */
    double tilt_deg;      /* Кут нахилу панелі до горизонту (градуси) */
    double azimuth_deg;   /* Азимут панелі (0 = Південь, +90 = Захід, -90 = Схід) */
    double soiling_ratio; /* Втрати від забруднення (наприклад 0.05 = 5% втрат) */
} SolarPanelConfig;

typedef struct {
    double daily_kwh[365];
    double annual_kwh;
    double min_day_kwh;
    double max_day_kwh;
    int worst_day_idx;
} SolarHarvestSummary;

/* Розрахунок сонячного схилення (радіани) для порядкового дня року n (1..365) */
static double solar_declination_rad(int day_of_year) {
    return DEG_TO_RAD(23.45 * sin(DEG_TO_RAD(360.0 * (284 + day_of_year) / 365.0)));
}

/* Оцінка інсоляції на похилу площину та миттєвої генерації (Вт) */
double calculate_instant_power(const SolarPanelConfig *panel, double lat_deg,
                               int day_of_year, double solar_hour, double t_ambient_c) {
    double lat_rad = DEG_TO_RAD(lat_deg);
    double tilt_rad = DEG_TO_RAD(panel->tilt_deg);
    double decl_rad = solar_declination_rad(day_of_year);
    
    /* Годинний кут сонця omega: 12:00 = 0 рад, 1 година = 15 градусів */
    double hour_angle_rad = DEG_TO_RAD((solar_hour - 12.0) * 15.0);
    
    /* Синус висоти сонця над горизонтом (cos z) */
    double sin_elevation = sin(lat_rad) * sin(decl_rad) + 
                           cos(lat_rad) * cos(decl_rad) * cos(hour_angle_rad);
    
    if (sin_elevation <= 0.0) {
        return 0.0; /* Сонце за горизонтом */
    }
    
    /* Кут падіння прямих променів на орієнтовану на південь панель */
    double cos_theta_inc = sin(decl_rad) * sin(lat_rad) * cos(tilt_rad) -
                           sin(decl_rad) * cos(lat_rad) * sin(tilt_rad) * cos(DEG_TO_RAD(panel->azimuth_deg)) +
                           cos(decl_rad) * cos(lat_rad) * cos(tilt_rad) * cos(hour_angle_rad) +
                           cos(decl_rad) * sin(lat_rad) * sin(tilt_rad) * cos(DEG_TO_RAD(panel->azimuth_deg)) * cos(hour_angle_rad) +
                           cos(decl_rad) * sin(tilt_rad) * sin(DEG_TO_RAD(panel->azimuth_deg)) * sin(hour_angle_rad);
    
    if (cos_theta_inc < 0.0) {
        cos_theta_inc = 0.0; /* Промені падають з тильного боку */
    }
    
    /* Модель прямої радіації в атмосфері за Meinel */
    double air_mass = 1.0 / (sin_elevation + 0.0001);
    double g_direct = 1361.0 * pow(0.7, pow(air_mass, 0.678));
    double g_diffuse = 0.12 * g_direct;
    
    /* Інсоляція на похилу площину */
    double g_tilt = g_direct * cos_theta_inc + g_diffuse * ((1.0 + cos(tilt_rad)) / 2.0);
    if (g_tilt <= 0.0) {
        return 0.0;
    }
    
    /* Робоча температура фотоелемента */
    double t_cell = t_ambient_c + g_tilt * ((panel->noct - 20.0) / 800.0);
    
    /* Температурний коефіцієнт (gamma_pmp заданий у %/°C, ділимо на 100) */
    double temp_derate = 1.0 + (panel->gamma_pmp / 100.0) * (t_cell - 25.0);
    if (temp_derate < 0.2) temp_derate = 0.2;
    
    /* Втрати від бруду */
    double soiling_derate = 1.0 - panel->soiling_ratio;
    
    /* Вихідна електрична потужність */
    double p_out = panel->p_stc * (g_tilt / 1000.0) * temp_derate * soiling_derate;
    return p_out > 0.0 ? p_out : 0.0;
}

/* Симуляція річної генерації з погодинною інтеграцією */
SolarHarvestSummary simulate_annual_harvest(const SolarPanelConfig *panel, double lat_deg) {
    SolarHarvestSummary summary = {0};
    summary.min_day_kwh = 1e9;
    summary.max_day_kwh = 0.0;
    
    for (int day = 1; day <= 365; ++day) {
        double day_watt_hours = 0.0;
        
        /* Спрощений синусоїдальний річний профіль середньодобової температури для України */
        double t_avg = 10.0 - 12.0 * cos(DEG_TO_RAD(360.0 * (day - 15) / 365.0));
        
        for (int h = 0; h < 24; ++h) {
            double solar_hour = h + 0.5; /* Середина годинного інтервалу */
            double power = calculate_instant_power(panel, lat_deg, day, solar_hour, t_avg);
            day_watt_hours += power * 1.0; /* 1 година = 1 Вт·год на 1 Вт */
        }
        
        double day_kwh = day_watt_hours / 1000.0;
        summary.daily_kwh[day - 1] = day_kwh;
        summary.annual_kwh += day_kwh;
        
        if (day_kwh < summary.min_day_kwh) {
            summary.min_day_kwh = day_kwh;
            summary.worst_day_idx = day;
        }
        if (day_kwh > summary.max_day_kwh) {
            summary.max_day_kwh = day_kwh;
        }
    }
    return summary;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <numeric>
#include <span>

struct SolarPanel {
    double p_stc_w{100.0};       // Номінальна потужність за STC (Вт)
    double gamma_pmp{-0.38};      // Температурний коефіцієнт Pmax (%/°C)
    double noct_c{45.0};          // Нормальна робоча температура комірки (°C)
    double tilt_deg{60.0};        // Кут нахилу панелі до горизонту (°)
    double azimuth_deg{0.0};      // Азимут (0° = суворо на Південь)
    double soiling_factor{0.05};  // Коефіцієнт втрат від бруду (5%)
};

struct HarvestMetrics {
    std::vector<double> daily_kwh;
    double annual_kwh{0.0};
    double min_day_kwh{0.0};
    double max_day_kwh{0.0};
    int worst_day{1};
};

class SolarSimulator {
public:
    explicit SolarSimulator(double latitude_deg) : latitude_deg_{latitude_deg} {}

    [[nodiscard]] HarvestMetrics simulate(const SolarPanel& panel) const {
        HarvestMetrics result;
        result.daily_kwh.resize(365, 0.0);

        for (int day = 1; day <= 365; ++day) {
            double daily_wh = 0.0;
            const double t_ambient = estimate_ambient_temp(day);

            for (int h = 0; h < 24; ++h) {
                const double hour = h + 0.5;
                daily_wh += instant_power(panel, day, hour, t_ambient);
            }

            const double kwh = daily_wh / 1000.0;
            result.daily_kwh[day - 1] = kwh;
            result.annual_kwh += kwh;
        }

        auto [min_it, max_it] = std::minmax_element(result.daily_kwh.begin(), result.daily_kwh.end());
        result.min_day_kwh = *min_it;
        result.max_day_kwh = *max_it;
        result.worst_day = static_cast<int>(std::distance(result.daily_kwh.begin(), min_it) + 1);

        return result;
    }

private:
    double latitude_deg_{50.45};

    static constexpr double to_rad(double deg) noexcept {
        return deg * (std::numbers::pi / 180.0);
    }

    static double estimate_ambient_temp(int day_of_year) noexcept {
        return 10.0 - 12.0 * std::cos(to_rad(360.0 * (day_of_year - 15) / 365.0));
    }

    [[nodiscard]] double instant_power(const SolarPanel& panel, int day, double hour, double t_amb) const {
        const double lat_rad = to_rad(latitude_deg_);
        const double tilt_rad = to_rad(panel.tilt_deg);
        const double decl_rad = to_rad(23.45 * std::sin(to_rad(360.0 * (284 + day) / 365.0)));
        const double hour_rad = to_rad((hour - 12.0) * 15.0);

        const double sin_elev = std::sin(lat_rad) * std::sin(decl_rad) +
                                std::cos(lat_rad) * std::cos(decl_rad) * std::cos(hour_rad);
        if (sin_elev <= 0.0) return 0.0;

        const double az_rad = to_rad(panel.azimuth_deg);
        const double cos_inc = std::sin(decl_rad) * std::sin(lat_rad) * std::cos(tilt_rad) -
                               std::sin(decl_rad) * std::cos(lat_rad) * std::sin(tilt_rad) * std::cos(az_rad) +
                               std::cos(decl_rad) * std::cos(lat_rad) * std::cos(tilt_rad) * std::cos(hour_rad) +
                               std::cos(decl_rad) * std::sin(lat_rad) * std::sin(tilt_rad) * std::cos(az_rad) * std::cos(hour_rad) +
                               std::cos(decl_rad) * std::sin(tilt_rad) * std::sin(az_rad) * std::sin(hour_rad);
        if (cos_inc <= 0.0) return 0.0;

        const double am = 1.0 / (sin_elev + 0.0001);
        const double g_dir = 1361.0 * std::pow(0.7, std::pow(am, 0.678));
        const double g_dif = 0.12 * g_dir;
        const double g_tilt = g_dir * cos_inc + g_dif * ((1.0 + std::cos(tilt_rad)) / 2.0);

        const double t_cell = t_amb + g_tilt * ((panel.noct_c - 20.0) / 800.0);
        const double temp_derate = std::max(0.2, 1.0 + (panel.gamma_pmp / 100.0) * (t_cell - 25.0));
        const double soil_derate = 1.0 - panel.soiling_factor;

        return panel.p_stc_w * (g_tilt / 1000.0) * temp_derate * soil_derate;
    }
};
```
:::

## Крайові випадки та числові пастки моделювання

При реалізації сонячного калькулятора на вбудованих платформах слід враховувати такі крайові умови:

1. **Низьке положення Сонця над горизонтом (`h_elev < 5°`):** на світанку та заході формула Мейнела дає завищені значення атмосферної маси `AM > 10`. Додатковий поріг `sin_elevation > 0.087` (висота > 5°) запобігає аномальним розрахункам при затіненні місцевим рельєфом.
2. **Перегрів у літній полудень:** при високій температурі повітря (+35 °C) та сильній інсоляції (1000 Вт/м²) температура кристала сягає `T_cell = 35 + 1000 · (25 / 800) = 66.25 °C`. Температурний коефіцієнт `k_temp = 1 + (-0.0038) · (66.25 - 25) = 1 - 0.1567 = 0.843`, тобто панель втрачає понад 15.6% паспортної потужності лише через нагрів.
3. **Зимове підвищення ККД:** при зимовій температурі -15 °C та інсоляції 800 Вт/м² температура комірки становить `T_cell = -15 + 800 · (25 / 800) = +10 °C`. Коефіцієнт `k_temp = 1 + (-0.0038) · (10 - 25) = 1 + 0.057 = 1.057`, що частково компенсує низьку висоту Сонця над горизонтом.
4. **Обмеження струму MPPT-контролера:** якщо потужність панелі перевищує допустимий вхідний струм перетворювача, контролер зміщує робочу точку праворуч за кривою ВАХ у бік напруги холостого ходу `V_oc`, штучно обмежуючи споживану потужність (clipping).
5. **Динамічне керування періодом сну (Duty Cycling):** прошивка автономного контролера може використовувати результати добового моделювання для адаптивного регулювання активності: якщо розрахункова зимова генерація падає нижче критичного порогу, контролер автоматично збільшує інтервал опитування датчиків із 1 хвилини до 15 хвилин, зберігаючи заряд батареї до весни.
