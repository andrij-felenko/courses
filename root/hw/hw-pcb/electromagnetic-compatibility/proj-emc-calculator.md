# ⚙️ Інженерний калькулятор параметрів зв'язку та випромінювання

<preknowlist>
- [Джерело, шлях, жертва: чотири шляхи завади](root:hw-pcb/electromagnetic-compatibility) — чотири механізми перенесення енергії завади.
- [Виведення випромінюваного поля](root:hw-pcb/electromagnetic-compatibility/math-radiated-emissions.md) — математичні моделі магнітного та електричного диполів.
- [Стандарти та ліміти ЕМС](root:hw-pcb/electromagnetic-compatibility/api-emc-standards.md) — нормативні ліміти випромінюваної емісії CISPR 32.
</preknowlist>

Оцінка рівнів наведених завад на етапі трасування друкованої плати дозволяє уникнути дорогих ітерацій перерозведення шарів та несподіваних провалів під час сертифікації в акредитованій лабораторії. Повний тривимірний електродинамічний аналіз (3D Field Solver) вимагає значних обчислювальних ресурсів і годин моделювання, проте базові інженерні формули дають змогу за частки секунди оцінити амплітуди перехресних зв'язків та напруженість поля випромінювання на етапі компонування плати.

Нижче наведено практичну інженерну утиліту для швидкої кількісної оцінки чотирьох ключових параметрів ЕМС на мовах C та ідіоматичному C++.

### Фізико-математичні моделі калькулятора

Програма реалізує чотири незалежні розрахункові модулі:

1. **Модуль ємнісного наведення (Capacitive Crosstalk):**
   - Розраховує струм зміщення i = C_M · (dV/dt), що впорскується крізь розподілену міжелектродну ємність C_M між лінією-агресором та лінією-жертвою;
   - Обчислює падіння напруги на еквівалентному вхідному опорі навантаження жертви: V_noise = i · R_victim;
   - Застосовується для аналізу високоомних шин (I2C, Reset, лінії аналогових датчиків), розташованих паралельно до швидких тактових трас.

2. **Модуль індуктивного наведення (Inductive Crosstalk):**
   - Обчислює електрорушійну силу взаємної індукції v = M · (dI/dt), наведену змінним магнітним потоком агресора в замкненому контурі жертви;
   - Використовується для аналізу впливу силових ключів перетворювачів DC-DC, H-містків моторів та вихідних каскадів драйверів на прилеглі сигнальні петлі.

3. **Модуль зсуву опорного нуля (Ground Bounce / Common Impedance):**
   - Оцінює стрибок потенціалу землі за формулою ΔV_GND = I_pulse · R_common + L_common · (dI_pulse / dt);
   - Враховує як активний опір мідної ділянки спільної землі, так і її власну паразитну індуктивність (приблизно 1 нГн/мм);
   - Дозволяє визначити, чи не перевищить зсув опорного потенціалу допустимий запас завадостійкості цифрових логічних рівнів (Noise Margin).

4. **Модуль випромінюваної емісії в дальньому полі (Radiated Emissions):**
   - **Диференційний контур (Differential Mode, DM):** модель малого магнітного диполя з урахуванням подвоєння поля відбиттям від провідної підлоги випробувальної камери: E_DM = (2.632·10⁻¹⁴ · f² · I_DM · A) / r (у В/м);
   - **Синфазний кабель (Common Mode, CM):** модель короткого симетричного електричного диполя над землею: E_CM = (1.257·10⁻⁶ · f · I_CM · L) / r (у В/м);
   - Переводить напруженість поля в логарифмічні одиниці дБмкВ/м за формулою E_dB = 20 · lg(E_мкВ/м) та автоматично зіставляє результат із нормативним лімітом CISPR 32 Class B на дистанції 3 м (40 дБмкВ/м у діапазоні 30–230 МГц).

### Межі застосовності та інженерні допущення

- Модель малого контуру (магнітного диполя) є фізично коректною, поки максимальний розмір петлі d не перевищує десятої частини довжини хвилі (d < λ / 10). Для частоти 100 МГц (λ = 3 м) лінійний розмір контуру повинен бути меншим за 30 см;
- Модель короткого кабелю (електричного диполя) передбачає L < λ / 4. Якщо довжина кабелю наближається до чверті довжини хвилі (чвертьхвильовий резонанс), випромінювальна здатність різко зростає через резонансне зростання струму на відкритому кінці;
- Логарифмічні перетворення захищені від ділення на нуль та від'ємних значень нижнім числовим порогом (Clamp Guard).

:::tabs
```c tab="C"
#include <stdio.h>
#include <math.h>

#define CISPR32_CLASS_B_3M_DBUV 40.0

typedef struct {
    double mutual_capacitance_pf; // Паразитна ємність (пФ)
    double aggressor_dv;          // Перепад напруги (В)
    double rise_time_ns;          // Час наростання фронту (нс)
    double victim_impedance_ohm;   // Вхідний опір жертви (Ом)
} CapacitiveCouplingParams;

typedef struct {
    double mutual_inductance_nh;  // Взаємна індуктивність (нГн)
    double aggressor_di;          // Перепад струму (А)
    double rise_time_ns;          // Час наростання фронту (нс)
} InductiveCouplingParams;

typedef struct {
    double common_resistance_mohm; // Активний опір спільної ділянки (мОм)
    double common_inductance_nh;   // Паразитна індуктивність ділянки (нГн)
    double pulse_current_a;        // Амплітуда імпульсу струму (А)
    double rise_time_ns;          // Час наростання (нс)
} GroundBounceParams;

typedef struct {
    double frequency_mhz;         // Частота гармоніки (МГц)
    double loop_area_cm2;         // Площа сигнального контуру (см²)
    double diff_current_ma;       // Диференційний струм (мА)
    double cable_length_m;        // Довжина кабелю (м)
    double common_mode_current_ua; // Синфазний струм (мкА)
    double distance_m;            // Відстань до антени (м)
} RadiationParams;

double calculate_capacitive_noise(const CapacitiveCouplingParams *p, double *injected_current_ma) {
    double c_farads = p->mutual_capacitance_pf * 1e-12;
    double dt_sec = p->rise_time_ns * 1e-9;
    double dv_dt = p->aggressor_dv / dt_sec;
    double current_a = c_farads * dv_dt;

    if (injected_current_ma) {
        *injected_current_ma = current_a * 1e3;
    }
    return current_a * p->victim_impedance_ohm;
}

double calculate_inductive_noise(const InductiveCouplingParams *p) {
    double m_henry = p->mutual_inductance_nh * 1e-9;
    double dt_sec = p->rise_time_ns * 1e-9;
    double di_dt = p->aggressor_di / dt_sec;
    return m_henry * di_dt;
}

double calculate_ground_bounce(const GroundBounceParams *p) {
    double r_ohm = p->common_resistance_mohm * 1e-3;
    double l_henry = p->common_inductance_nh * 1e-9;
    double dt_sec = p->rise_time_ns * 1e-9;
    double di_dt = p->pulse_current_a / dt_sec;

    double v_resistive = p->pulse_current_a * r_ohm;
    double v_inductive = l_henry * di_dt;
    return v_resistive + v_inductive;
}

void calculate_radiated_field(const RadiationParams *p, double *e_dm_dbuv, double *e_cm_dbuv) {
    double f_hz = p->frequency_mhz * 1e6;
    double a_m2 = p->loop_area_cm2 * 1e-4;
    double i_dm_a = p->diff_current_ma * 1e-3;
    double i_cm_a = p->common_mode_current_ua * 1e-6;

    // Диференційне випромінювання контуру з відбиттям: E_DM = (2.632e-14 * f^2 * I * A) / r
    double e_dm_vm = (2.632e-14 * f_hz * f_hz * i_dm_a * a_m2) / p->distance_m;
    double e_dm_uvm = e_dm_vm * 1e6;
    *e_dm_dbuv = 20.0 * log10(e_dm_uvm > 1e-9 ? e_dm_uvm : 1e-9);

    // Синфазне випромінювання кабелю з відбиттям: E_CM = (1.257e-6 * f * I * L) / r
    double e_cm_vm = (1.257e-6 * f_hz * i_cm_a * p->cable_length_m) / p->distance_m;
    double e_cm_uvm = e_cm_vm * 1e6;
    *e_cm_dbuv = 20.0 * log10(e_cm_uvm > 1e-9 ? e_cm_uvm : 1e-9);
}

int main(void) {
    printf("=== Інженерний розрахунок параметрів ЕМС ===\n\n");

    CapacitiveCouplingParams cap = { .mutual_capacitance_pf = 3.0, .aggressor_dv = 3.3, .rise_time_ns = 1.0, .victim_impedance_ohm = 10000.0 };
    double inj_ma = 0.0;
    double v_cap = calculate_capacitive_noise(&cap, &inj_ma);
    printf("1. Ємнісний зв'язок:\n");
    printf("   Паразитна ємність: %.1f пФ, фронт: %.1f нс, навантаження: %.1f кОм\n", cap.mutual_capacitance_pf, cap.rise_time_ns, cap.victim_impedance_ohm / 1000.0);
    printf("   Впорснутий струм: %.3f мА -> Наведена напруга на жертві: %.3f В\n\n", inj_ma, v_cap);

    InductiveCouplingParams ind = { .mutual_inductance_nh = 4.5, .aggressor_di = 2.0, .rise_time_ns = 5.0 };
    double v_ind = calculate_inductive_noise(&ind);
    printf("2. Індуктивний зв'язок:\n");
    printf("   Взаємна індуктивність: %.1f нГн, струм: %.1f А за %.1f нс\n", ind.mutual_inductance_nh, ind.aggressor_di, ind.rise_time_ns);
    printf("   Наведена напруга: %.3f В (%.1f мВ)\n\n", v_ind, v_ind * 1e3);

    GroundBounceParams gb = { .common_resistance_mohm = 5.0, .common_inductance_nh = 2.5, .pulse_current_a = 4.0, .rise_time_ns = 2.0 };
    double v_gb = calculate_ground_bounce(&gb);
    printf("3. Зсув опорного нуля (Ground Bounce):\n");
    printf("   Спільна земля: %.1f мОм, %.1f нГн, імпульс: %.1f А за %.1f нс\n", gb.common_resistance_mohm, gb.common_inductance_nh, gb.pulse_current_a, gb.rise_time_ns);
    printf("   Стрибок потенціалу землі: %.3f В (%.1f мВ)\n\n", v_gb, v_gb * 1e3);

    RadiationParams rad = { .frequency_mhz = 100.0, .loop_area_cm2 = 1.5, .diff_current_ma = 25.0, .cable_length_m = 1.2, .common_mode_current_ua = 8.0, .distance_m = 3.0 };
    double e_dm_db = 0.0, e_cm_db = 0.0;
    calculate_radiated_field(&rad, &e_dm_db, &e_cm_db);
    printf("4. Випромінюване поле на частоті %.1f МГц (дистанція %.1f м):\n", rad.frequency_mhz, rad.distance_m);
    printf("   Контур (DM): струм %.1f мА, площа %.2f см² -> Поле: %.1f дБмкВ/м (Ліміт CISPR-B: %.1f)\n", rad.diff_current_ma, rad.loop_area_cm2, e_dm_db, CISPR32_CLASS_B_3M_DBUV);
    printf("   Кабель (CM): струм %.1f мкА, довжина %.1f м -> Поле: %.1f дБмкВ/м (Ліміт CISPR-B: %.1f)\n", rad.common_mode_current_ua, rad.cable_length_m, e_cm_db, CISPR32_CLASS_B_3M_DBUV);

    return 0;
}
```
```cpp tab="C++"
#include <iostream>
#include <iomanip>
#include <cmath>
#include <span>
#include <vector>
#include <string_view>

namespace emc {

constexpr double Cispr32ClassB3mLimitDbuv = 40.0;

struct CapacitiveCouplingParams {
    double mutual_capacitance_pf{3.0};
    double aggressor_dv{3.3};
    double rise_time_ns{1.0};
    double victim_impedance_ohm{10000.0};
};

struct InductiveCouplingParams {
    double mutual_inductance_nh{4.5};
    double aggressor_di{2.0};
    double rise_time_ns{5.0};
};

struct GroundBounceParams {
    double common_resistance_mohm{5.0};
    double common_inductance_nh{2.5};
    double pulse_current_a{4.0};
    double rise_time_ns{2.0};
};

struct RadiationParams {
    double frequency_mhz{100.0};
    double loop_area_cm2{1.5};
    double diff_current_ma{25.0};
    double cable_length_m{1.2};
    double common_mode_current_ua{8.0};
    double distance_m{3.0};
};

struct RadiationResult {
    double dm_field_dbuv{0.0};
    double cm_field_dbuv{0.0};
    bool passes_dm{true};
    bool passes_cm{true};
};

[[nodiscard]] auto calculate_capacitive_noise(const CapacitiveCouplingParams& p) noexcept {
    const double c_farads = p.mutual_capacitance_pf * 1e-12;
    const double dt_sec = p.rise_time_ns * 1e-9;
    const double dv_dt = p.aggressor_dv / dt_sec;
    const double current_a = c_farads * dv_dt;
    const double voltage_drop = current_a * p.victim_impedance_ohm;
    return std::pair{current_a * 1e3, voltage_drop}; // {мА, В}
}

[[nodiscard]] constexpr double calculate_inductive_noise(const InductiveCouplingParams& p) noexcept {
    const double m_henry = p.mutual_inductance_nh * 1e-9;
    const double dt_sec = p.rise_time_ns * 1e-9;
    const double di_dt = p.aggressor_di / dt_sec;
    return m_henry * di_dt;
}

[[nodiscard]] constexpr double calculate_ground_bounce(const GroundBounceParams& p) noexcept {
    const double r_ohm = p.common_resistance_mohm * 1e-3;
    const double l_henry = p.common_inductance_nh * 1e-9;
    const double dt_sec = p.rise_time_ns * 1e-9;
    const double di_dt = p.pulse_current_a / dt_sec;
    return (p.pulse_current_a * r_ohm) + (l_henry * di_dt);
}

[[nodiscard]] auto calculate_radiated_field(const RadiationParams& p) noexcept {
    const double f_hz = p.frequency_mhz * 1e6;
    const double a_m2 = p.loop_area_cm2 * 1e-4;
    const double i_dm_a = p.diff_current_ma * 1e-3;
    const double i_cm_a = p.common_mode_current_ua * 1e-6;

    const double e_dm_vm = (2.632e-14 * f_hz * f_hz * i_dm_a * a_m2) / p.distance_m;
    const double e_dm_uvm = e_dm_vm * 1e6;
    const double e_dm_db = 20.0 * std::log10(e_dm_uvm > 1e-9 ? e_dm_uvm : 1e-9);

    const double e_cm_vm = (1.257e-6 * f_hz * i_cm_a * p.cable_length_m) / p.distance_m;
    const double e_cm_uvm = e_cm_vm * 1e6;
    const double e_cm_db = 20.0 * std::log10(e_cm_uvm > 1e-9 ? e_cm_uvm : 1e-9);

    return RadiationResult{
        .dm_field_dbuv = e_dm_db,
        .cm_field_dbuv = e_cm_db,
        .passes_dm = (e_dm_db <= Cispr32ClassB3mLimitDbuv),
        .passes_cm = (e_cm_db <= Cispr32ClassB3mLimitDbuv)
    };
}

} // namespace emc

int main() {
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== Інженерний розрахунок параметрів ЕМС (C++) ===\n\n";

    emc::CapacitiveCouplingParams cap{};
    auto [inj_ma, v_cap] = emc::calculate_capacitive_noise(cap);
    std::cout << "1. Ємнісний зв'язок:\n"
              << "   Паразитна ємність: " << cap.mutual_capacitance_pf << " пФ, фронт: " << cap.rise_time_ns << " нс\n"
              << "   Впорснутий струм: " << inj_ma << " мА -> Напруга: " << v_cap << " В\n\n";

    emc::InductiveCouplingParams ind{};
    double v_ind = emc::calculate_inductive_noise(ind);
    std::cout << "2. Індуктивний зв'язок:\n"
              << "   Взаємна індуктивність: " << ind.mutual_inductance_nh << " нГн, струм: " << ind.aggressor_di << " А\n"
              << "   Наведена напруга: " << v_ind << " В (" << v_ind * 1e3 << " мВ)\n\n";

    emc::GroundBounceParams gb{};
    double v_gb = emc::calculate_ground_bounce(gb);
    std::cout << "3. Зсув опорного нуля (Ground Bounce):\n"
              << "   Спільна земля: " << gb.common_resistance_mohm << " мОм, " << gb.common_inductance_nh << " нГн\n"
              << "   Стрибок потенціалу землі: " << v_gb << " В (" << v_gb * 1e3 << " мВ)\n\n";

    emc::RadiationParams rad{};
    auto res = emc::calculate_radiated_field(rad);
    std::cout << "4. Випромінюване поле на частоті " << rad.frequency_mhz << " МГц (дистанція " << rad.distance_m << " м):\n"
              << "   Контур (DM): " << res.dm_field_dbuv << " дБмкВ/м [" << (res.passes_dm ? "ПРОЙДЕНО" : "ПЕРЕВИЩЕННЯ") << "]\n"
              << "   Кабель (CM): " << res.cm_field_dbuv << " дБмкВ/м [" << (res.passes_cm ? "ПРОЙДЕНО" : "ПЕРЕВИЩЕННЯ") << "]\n";

    return 0;
}
```
:::

### Практична інтерпретація результатів розрахунку

1. **Якщо синфазне випромінювання (CM) перевищує ліміт:**
   - Необхідно встановити синфазний дросель (Common Mode Choke) або феритовий фільтр безпосередньо біля вихідного роз'єму кабелю;
   - Забезпечити безпосередній контакт екрана кабелю з металевим шасі або землею плати по повному колу 360° (без довгих заземлюючих виводів "Pigtail", які самі працюють як антени);
   - Зшити площини цифрової землі та шасі високочастотними конденсаторами або прямими металевими стійками.

2. **Якщо ємнісне наведення перевищує допустимий поріг:**
   - Збільшити просторовий зазор між паралельними трасами згідно з правилом 3W або 4W;
   - Прокласти між агресором і жертвою заземлену екрануючу доріжку (Guard Trace) з перехідними отворами на шар землі через кожні 3–5 мм;
   - Зменшити опір підтяжки лінії-жертви (наприклад, зменшити резистор підтяжки I2C з 10 кОм до 2.2 кОм), що зменшить амплітуду наведеної напруги за рахунок меншого імпедансу навантаження.

3. **Якщо індуктивне наведення загрожує чутливим колам:**
   - Зменшити площу контуру агресора шляхом розміщення конденсаторів декупування впритул до виводів комутуючих ключів;
   - Зменшити площу петлі жертви (трасувати сигнальну лінію безпосередньо над суцільною площиною землі або використовувати звиту диференційну пару);
   - Розташувати площини контурів агресора та жертви взаємно перпендикулярно (ортогонально), що мінімізує коефіцієнт взаємної індуктивності M практично до нуля.

4. **Якщо зсув опорного нуля (Ground Bounce) загрожує цифровим рівням:**
   - Замінити одиночні земляні доріжки на суцільний полігон землі (Solid Ground Plane), активний опір якого вимірюється частками міліома на квадрат, а індуктивність розподілена рівномірно;
   - Збільшити кількість перехідних отворів землі біля виводів живлення мікросхем (масив паралельних отворів пропорційно ділить еквівалентну індуктивність);
   - Розділити точки підключення силової та сигнальної землі за топологією «зірка» (Star Grounding), щоб потужні імпульси силових ключів не мали спільного провідника з опорним нулем контролера.
