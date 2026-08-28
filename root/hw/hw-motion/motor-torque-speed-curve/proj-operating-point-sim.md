# ⚙️ Програмний розрахунок робочої точки та підбір редуктора

<preknowlist>
- [Крива момент–оберти мотора](root:hw-motion/motor-torque-speed-curve) — розуміння лінійної характеристики, робочої точки та зон S1/Peak.
- [Мотор-редуктор](root:hw-motion/gearmotor) — передавальне відношення, ККД передачі та трансформація моменту й швидкості.
- [Заклинювання й нагрів мотора](root:hw-motion/motor-current-stall-heat) — середньоквадратичний струм I_RMS та теплові обмеження обмоток.
</preknowlist>

При проектуванні автоматизованого приводу інженер постає перед потрійною задачею: визначити дійсну робочу точку двигуна під комбінованим навантаженням, перевірити тепловий баланс у циклічному режимі за середньоквадратичним еквівалентним моментом (`M_RMS ≤ M_N`) та підібрати передавальне число редуктора, яке узгоджує інерцію виконавчого механізму з інерцією ротора.

У простих навчальних задачах навантаження вважають суто постійним, і робочу точку знаходять за лінійною формулою. Проте в реальних мехатронних системах — від роботизованих шарнірів до приводів гребних гвинтів та конвеєрів — момент опору є сумою сухого тертя, в'язкого опору мастила та квадратичного аеродинамічного чи гідродинамічного опору середовища:

```
M_load(ω) = M_static + B_viscous · ω + C_aero · ω²
```

Оскільки це рівняння містить квадратичний доданок, аналітичний розв'язок у замкненій формі вимагає обчислення дискримінанту, а в разі додавання обмежень драйвера за струмом або нелінійного спаду напруги живлення система потребує універсального чисельного розв'язувача.

### Чисельний розв'язувач робочої точки: метод Ньютона–Рафсона

Для знаходження усталеної швидкості `ω_op` необхідно розв'язати нелінійне рівняння рівноваги моментів:

```
F(ω) = M_motor(ω) − M_load(ω) = 0
```

де електромагнітний момент двигуна під напругою `U` дорівнює:

```
M_motor(ω) = (k_t / R) · (U − k_e · ω)
```

Функція нев'язки має вигляд:

```
F(ω) = (k_t / R) · (U − k_e · ω) − (M_static + B_viscous · ω + C_aero · ω²)
```

Похідна нев'язки за кутовою швидкістю:

```
dF / dω = −(k_t · k_e) / R − B_viscous − 2 · C_aero · ω
```

Оскільки всі коефіцієнти `k_t, k_e, R, B_viscous, C_aero` є додатними фізичними величинами, похідна `dF / dω` строго від'ємна для будь-яких `ω ≥ 0`. Це гарантує монотонне спадання функції `F(ω)` та швидку збіжність ітераційного процесу Ньютона–Рафсона за 3–5 ітерацій:

```
ω_(n+1) = ω_n − F(ω_n) / (dF / dω | ω_n)
```

### Тепловий розрахунок за стандартом IEC 60034-1: еквівалентний момент RMS

Реальні механізми рідко працюють на фіксованій швидкості безперервно. Типовий профіль руху складається з ділянок розгону, руху з постійною швидкістю, динамічного гальмування та технологічної паузи (трапецеїдальний профіль швидкості).

На етапі прискорення двигун розвиває піковий момент `M_accel`, який значно перевищує номінальний тривалий момент `M_N` зони S1. Щоб перевірити, чи не перегріється ізоляція обмоток, обчислюють середньоквадратичний еквівалентний момент за повний цикл руху тривалістю `T_cycle`:

```
M_RMS = sqrt( (1 / T_cycle) · ∑ (M_i² · t_i) )
```

де `M_i` — крутний момент на `i`-му сегменті профілю руху тривалістю `t_i`. Двигун гарантовано працюватиме без теплового перевантаження, якщо виконуються дві умови:
1. Середньоквадратичний момент не перевищує номінального неперервного моменту: `M_RMS ≤ M_N`.
2. Піковий момент розгону не перевищує допустимого пікового моменту: `M_accel ≤ M_peak`.

### Оптимальне узгодження інерції (Inertia Ratio Matching)

При підборі механічної передачі передавальне відношення `i = ω_motor / ω_load` впливає на дві характеристики:
- Статичний момент, необхідний для подолання опору навантаження, зменшується пропорційно `i`: `M_req_motor = M_load / (i · η_gear)`.
- Динамічний момент інерції навантаження, приведений до вала ротора, зменшується пропорційно квадрату `i`: `J_reflected = J_load / i²`.

Повний динамічний момент, який двигун повинен розвинути для забезпечення кутового прискорення навантаження `α_load`:

```
M_accel = (J_rotor + J_load / (i² · η_gear)) · (α_load · i) + M_load_static / (i · η_gear)
```

Для максимізації кутового прискорення `α_load` при фіксованому піковому моменті двигуна `M_peak` оптимальне передавальне число визначається умовою узгодження інерції:

```
i_opt = sqrt( J_load / J_rotor )
```

В інженерній практиці робототехніки співвідношення приведеної інерції до інерції ротора `J_reflected / J_rotor` обирають у діапазоні:
- `1 : 1` — для високодинамічних сервоприводів із граничним прискоренням (дельта-роботи, станки для лазерного різання);
- `3 : 1 ... 5 : 1` — оптимальний компроміс для більшості шарнірів промислових маніпуляторів та колісних роботів;
- `до 10 : 1` — допустимо для приводів із повільною динамікою, де пріоритетом є мінімізація габаритів двигуна.

### Крайові випадки та обмеження драйвера

При практичному розрахунку слід враховувати два критичні крайові стани:

1. **Струмове обмеження драйвера (Current Limiting)**: силовий міст драйвера часто має апаратний ліміт струму `I_max_driver < I_stall`. Якщо навантаження вимагає моменту `M > k_t · I_max_driver`, двигун переходить із лінійної характеристики на ділянку обмеження моменту зі спадом швидкості до нуля.
2. **Несумісність вимог механізму (`is_feasible == false`)**: коли розраховане мінімальне передавальне число за моментом `i_min_continuous` вимагає від мотора швидкості, що перевищує його механічний ліміт `ω_max`, мотор не здатний забезпечити комбінацію вимог швидкості та зусилля. У цьому випадку алгоритм повертає прапорець неможливості реалізації, сигналізуючи про необхідність вибору більш габаритного або потужного двигуна.

### Інженерна реалізація розрахунку приводу

Нижче наведено закінчену бібліотеку інженерного розрахунку на мовах C та C++, яка реалізує розв'язання нелінійної робочої точки методом Ньютона–Рафсона, оцінку теплового еквівалента за довільним профілем навантаження та оптимізацію редуктора.

:::tabs

```c
/* motor_sizing.h / motor_sizing.c — Розрахунок електромеханічного приводу */
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double u_nom;       /* Номінальна напруга живлення, В */
    double r_arm;       /* Активний опір обмотки якоря, Ом */
    double k_t;         /* Стала крутного моменту, Н·м/А */
    double k_e;         /* Стала протиЕРС, В·с/рад (у системі SI k_e = k_t) */
    double i_0;         /* Струм холостого ходу, А */
    double m_cont;      /* Номінальний неперервний момент S1, Н·м */
    double m_peak;      /* Граничний піковий момент, Н·м */
    double omega_max;   /* Максимальна механічна швидкість, рад/с */
    double j_rotor;     /* Момент інерції ротора, кг·м² */
} MotorParams;

typedef struct {
    double m_static;    /* Постійний момент опору (тертя, вантаж), Н·м */
    double b_viscous;   /* Коефіцієнт в'язкого тертя, Н·м·с/рад */
    double c_aero;      /* Коефіцієнт аеродинамічного навантаження, Н·м·с²/рад² */
} LoadCharacteristics;

typedef struct {
    double omega_op;    /* Усталена кутова швидкість, рад/с */
    double rpm_op;      /* Швидкість обертання, об/хв */
    double torque_op;   /* Робочий крутний момент, Н·м */
    double current_op;  /* Струм якоря в робочій точці, А */
    double p_mech;      /* Корисна механічна потужність, Вт */
    double p_loss;      /* Джоулеві теплові втрати в обмотці (I²R), Вт */
    double efficiency;  /* Електромеханічний ККД (P_mech / P_elec) */
    bool is_s1_safe;    /* Чи лежить режим у межах безпечної зони S1 */
} OperatingPoint;

typedef struct {
    double target_omega_load;   /* Необхідна кутова швидкість навантаження, рад/с */
    double target_torque_load;  /* Необхідний тривалий момент навантаження, Н·м */
    double j_load;              /* Момент інерції навантаження, кг·м² */
    double accel_time;          /* Бажаний час розгону до target_omega, с */
    double gear_efficiency;     /* ККД редуктора (0.75 - 0.95) */
} MechanismRequirements;

typedef struct {
    double i_optimal_inertia;   /* Оптимальне передавальне число за інерцією */
    double i_min_continuous;    /* Мінімальне передавальне число за моментом S1 */
    double i_selected;          /* Рекомендоване передавальне число */
    double motor_req_torque;    /* Необхідний тривалий момент від мотора, Н·м */
    double motor_accel_torque;  /* Піковий момент мотора під час розгону, Н·м */
    bool is_feasible;           /* Чи задовольняє мотор вимогам механізму */
} GearboxSelectionResult;

/* Знаходження робочої точки чисельним методом Ньютона-Рафсона */
OperatingPoint motor_solve_operating_point(const MotorParams *m,
                                          const LoadCharacteristics *load,
                                          double u_applied)
{
    OperatingPoint pt = {0};
    double omega_0 = u_applied / m->k_e;

    /* Початкове наближення для швидкості */
    double omega = omega_0 * 0.7;

    for (int iter = 0; iter < 100; ++iter) {
        /* Момент мотора: M_m = (k_t / R) * (U - k_e * omega) */
        double m_motor = m->k_t * (u_applied - m->k_e * omega) / m->r_arm;
        /* Момент навантаження: M_l = M_s + B * omega + C * omega² */
        double m_load = load->m_static + load->b_viscous * omega + load->c_aero * omega * omega;

        double f = m_motor - m_load;
        if (fabs(f) < 1e-7) {
            break;
        }

        /* Похідна dF/d_omega = -k_t * k_e / R - B - 2 * C * omega */
        double df = -(m->k_t * m->k_e) / m->r_arm - load->b_viscous - 2.0 * load->c_aero * omega;
        omega = omega - f / df;

        if (omega < 0.0) {
            omega = 0.0;
            break;
        }
        if (omega > omega_0) {
            omega = omega_0;
        }
    }

    pt.omega_op = omega;
    pt.rpm_op = omega * (60.0 / (2.0 * M_PI));
    pt.torque_op = m->k_t * (u_applied - m->k_e * omega) / m->r_arm;
    if (pt.torque_op < 0.0) pt.torque_op = 0.0;

    pt.current_op = m->i_0 + pt.torque_op / m->k_t;
    pt.p_mech = pt.torque_op * pt.omega_op;
    pt.p_loss = pt.current_op * pt.current_op * m->r_arm;

    double p_elec = u_applied * pt.current_op;
    pt.efficiency = (p_elec > 1e-6) ? (pt.p_mech / p_elec) : 0.0;
    pt.is_s1_safe = (pt.torque_op <= m->m_cont) && (pt.omega_op <= m->omega_max);

    return pt;
}

/* Підбір редуктора та перевірка динаміки розгону */
GearboxSelectionResult motor_select_gearbox(const MotorParams *m,
                                            const MechanismRequirements *req)
{
    GearboxSelectionResult res = {0};

    /* 1. Оптимальне передавальне число за узгодженням інерції: i = sqrt(J_load / J_rotor) */
    res.i_optimal_inertia = sqrt(req->j_load / m->j_rotor);

    /* 2. Мінімальне передавальне число за тривалим моментом S1: i >= M_req / (M_cont * eta) */
    res.i_min_continuous = req->target_torque_load / (m->m_cont * req->gear_efficiency);

    /* Обираємо більше значення, щоб гарантувати тривалу роботу в зоні S1 */
    res.i_selected = (res.i_optimal_inertia > res.i_min_continuous)
                     ? res.i_optimal_inertia
                     : res.i_min_continuous;

    /* Перевірка швидкості мотора при обраному i */
    double omega_motor_req = req->target_omega_load * res.i_selected;
    if (omega_motor_req > m->omega_max) {
        /* Зменшуємо i до гранично допустимого за швидкістю */
        res.i_selected = m->omega_max / req->target_omega_load;
    }

    res.motor_req_torque = req->target_torque_load / (res.i_selected * req->gear_efficiency);

    /* 3. Розрахунок прискорення та пікового моменту під час розгону */
    double alpha_load = req->target_omega_load / req->accel_time;
    double alpha_motor = alpha_load * res.i_selected;
    double j_reflected = req->j_load / (res.i_selected * res.i_selected);

    /* M_accel = (J_rotor + J_reflected / eta) * alpha_motor + M_req */
    double j_total_motor_side = m->j_rotor + j_reflected / req->gear_efficiency;
    res.motor_accel_torque = j_total_motor_side * alpha_motor + res.motor_req_torque;

    res.is_feasible = (res.motor_req_torque <= m->m_cont) &&
                      (res.motor_accel_torque <= m->m_peak) &&
                      (omega_motor_req <= m->omega_max);

    return res;
}

/* Обчислення середньоквадратичного моменту M_RMS для перевірки теплового режиму */
double motor_compute_rms_torque(const double *torques, const double *durations, size_t count)
{
    if (!torques || !durations || count == 0) return 0.0;
    double sum_sq = 0.0;
    double total_time = 0.0;
    for (size_t i = 0; i < count; ++i) {
        sum_sq += torques[i] * torques[i] * durations[i];
        total_time += durations[i];
    }
    return (total_time > 0.0) ? sqrt(sum_sq / total_time) : 0.0;
}
```

```cpp
// motor_sizing.hpp / motor_sizing.cpp — Ідіоматичний C++20 розрахунок приводу
#include <iostream>
#include <cmath>
#include <numbers>
#include <span>
#include <vector>
#include <algorithm>

namespace motor_sim {

struct MotorParams {
    double u_nom{24.0};       // Номінальна напруга живлення, В
    double r_arm{1.2};        // Активний опір обмотки якоря, Ом
    double k_t{0.038};        // Стала крутного моменту, Н·м/А
    double k_e{0.038};        // Стала протиЕРС, В·с/рад
    double i_0{0.15};         // Струм холостого ходу, А
    double m_cont{0.12};      // Номінальний неперервний момент S1, Н·м
    double m_peak{0.45};      // Граничний піковий момент, Н·м
    double omega_max{650.0};  // Максимальна механічна швидкість, рад/с (~6200 RPM)
    double j_rotor{2.5e-5};   // Момент інерції ротора, кг·м²
};

struct LoadCharacteristics {
    double m_static{0.05};    // Постійний момент опору, Н·м
    double b_viscous{1e-4};   // Коефіцієнт в'язкого тертя, Н·м·с/рад
    double c_aero{2e-6};      // Коефіцієнт аеродинамічного опору, Н·м·с²/рад²
};

struct OperatingPoint {
    double omega_op{0.0};     // Кутова швидкість, рад/с
    double rpm_op{0.0};       // Швидкість, об/хв
    double torque_op{0.0};    // Момент на валу, Н·м
    double current_op{0.0};   // Струм якоря, А
    double p_mech{0.0};       // Корисна механічна потужність, Вт
    double p_loss{0.0};       // Джоулеві втрати I²R, Вт
    double efficiency{0.0};   // ККД
    bool is_s1_safe{false};   // Безпека неперервної роботи S1
};

struct MechanismRequirements {
    double target_omega_load{20.94}; // 200 RPM на навантаженні, рад/с
    double target_torque_load{1.8};  // 1.8 Н·м на виході
    double j_load{1.5e-3};           // Інерція навантаження, кг·м²
    double accel_time{0.15};         // Час розгону 150 мс
    double gear_efficiency{0.85};    // ККД редуктора
};

struct GearboxSelectionResult {
    double i_optimal_inertia{0.0};
    double i_min_continuous{0.0};
    double i_selected{0.0};
    double motor_req_torque{0.0};
    double motor_accel_torque{0.0};
    bool is_feasible{false};
};

class DriveCalculator {
public:
    static OperatingPoint solve_operating_point(const MotorParams& m,
                                                const LoadCharacteristics& load,
                                                double u_applied) noexcept
    {
        OperatingPoint pt;
        const double omega_0 = u_applied / m.k_e;
        double omega = omega_0 * 0.7;

        for (int iter = 0; iter < 100; ++iter) {
            const double m_motor = m.k_t * (u_applied - m.k_e * omega) / m.r_arm;
            const double m_load = load.m_static + load.b_viscous * omega + load.c_aero * omega * omega;

            const double f = m_motor - m_load;
            if (std::abs(f) < 1e-7) {
                break;
            }

            const double df = -(m.k_t * m.k_e) / m.r_arm - load.b_viscous - 2.0 * load.c_aero * omega;
            omega -= f / df;

            if (omega < 0.0) { omega = 0.0; break; }
            if (omega > omega_0) { omega = omega_0; }
        }

        pt.omega_op = omega;
        pt.rpm_op = omega * (30.0 / std::numbers::pi);
        pt.torque_op = std::max(0.0, m.k_t * (u_applied - m.k_e * omega) / m.r_arm);
        pt.current_op = m.i_0 + pt.torque_op / m.k_t;
        pt.p_mech = pt.torque_op * pt.omega_op;
        pt.p_loss = pt.current_op * pt.current_op * m.r_arm;

        const double p_elec = u_applied * pt.current_op;
        pt.efficiency = (p_elec > 1e-6) ? (pt.p_mech / p_elec) : 0.0;
        pt.is_s1_safe = (pt.torque_op <= m.m_cont) && (pt.omega_op <= m.omega_max);

        return pt;
    }

    static GearboxSelectionResult select_gearbox(const MotorParams& m,
                                                 const MechanismRequirements& req) noexcept
    {
        GearboxSelectionResult res;

        // 1. Оптимальне i за узгодженням інерції
        res.i_optimal_inertia = std::sqrt(req.j_load / m.j_rotor);

        // 2. Мінімальне i за неперервним моментом S1
        res.i_min_continuous = req.target_torque_load / (m.m_cont * req.gear_efficiency);

        res.i_selected = std::max(res.i_optimal_inertia, res.i_min_continuous);

        const double omega_motor_req = req.target_omega_load * res.i_selected;
        if (omega_motor_req > m.omega_max) {
            res.i_selected = m.omega_max / req.target_omega_load;
        }

        res.motor_req_torque = req.target_torque_load / (res.i_selected * req.gear_efficiency);

        const double alpha_load = req.target_omega_load / req.accel_time;
        const double alpha_motor = alpha_load * res.i_selected;
        const double j_reflected = req.j_load / (res.i_selected * res.i_selected);

        const double j_total_motor = m.j_rotor + j_reflected / req.gear_efficiency;
        res.motor_accel_torque = j_total_motor * alpha_motor + res.motor_req_torque;

        res.is_feasible = (res.motor_req_torque <= m.m_cont) &&
                          (res.motor_accel_torque <= m.m_peak) &&
                          (omega_motor_req <= m.omega_max);

        return res;
    }

    // Розрахунок середньоквадратичного моменту за профільним циклом
    static double compute_rms_torque(std::span<const double> torques,
                                     std::span<const double> durations) noexcept
    {
        if (torques.empty() || torques.size() != durations.size()) {
            return 0.0;
        }
        double sum_sq = 0.0;
        double total_time = 0.0;
        for (std::size_t i = 0; i < torques.size(); ++i) {
            sum_sq += torques[i] * torques[i] * durations[i];
            total_time += durations[i];
        }
        return (total_time > 0.0) ? std::sqrt(sum_sq / total_time) : 0.0;
    }
};

} // namespace motor_sim
```

:::

### Практичний приклад розрахунку приводу маніпулятора

Розгляньмо задачу підбору комплекту «мотор + редуктор» для ліктьового суглоба робота-маніпулятора:
- Необхідна кутова швидкість у суглобі: `ω_load = 20.94 рад/с` (200 RPM).
- Постійний момент сили тяжіння та корисного вантажу: `M_load = 1.8 Н·м`.
- Момент інерції ланки з вантажем: `J_load = 1.5 · 10⁻³ кг·м²`.
- Час розгону до максимальної швидкості: `t_accel = 0.15 с`.
- Доступний безколекторний двигун: `U = 24 В`, `R = 1.2 Ом`, `k_t = 0.038 Н·м/А`, `M_cont = 0.12 Н·м`, `M_peak = 0.45 Н·м`, `J_rotor = 2.5 · 10⁻⁵ кг·м²`, `ω_max = 650 рад/с` (~6200 RPM). Редуктор хвильовий або планетарний із ККД `η = 85%`.

Застосувавши вищенаведений розрахунок:
1. `i_optimal_inertia = sqrt(1.5 · 10⁻³ / 2.5 · 10⁻⁵) = 7.75`.
2. `i_min_continuous = 1.8 / (0.12 · 0.85) = 17.65`.
3. Обираємо стандартний редуктор `i = 18.0`.
4. Швидкість мотора під час руху: `ω_motor = 20.94 · 18 = 376.9 рад/с` (3600 RPM), що не перевищує ліміт `650 рад/с`.
5. Тривалий момент на валу мотора: `M_motor_req = 1.8 / (18 · 0.85) = 0.118 Н·м < 0.12 Н·м` (безпечна тривала робота в зоні S1).
6. Піковий момент розгону: приведена інерція `J_reflected = 1.5 · 10⁻³ / 18² = 4.63 · 10⁻⁶ кг·м²`. Сумарна інерція на валу мотора: `J_total = 2.5 · 10⁻⁵ + 4.63 · 10⁻⁶ / 0.85 = 3.04 · 10⁻⁵ кг·м²`. Кутове прискорення вала мотора: `α_motor = (20.94 / 0.15) · 18 = 2512.8 рад/с²`.
   Динамічний момент розгону: `M_accel = 3.04 · 10⁻⁵ · 2512.8 + 0.118 = 0.076 + 0.118 = 0.194 Н·м`.
   Оскільки `0.194 Н·м << M_peak = 0.45 Н·м`, двигун має більш ніж двократний запас динамічного моменту для швидкого позиціонування.

Розрахунок доводить, що обрана комбінація двигуна та редуктора повністю задовольняє вимогам як за тривалою потужністю (S1), так і за динамічною швидкодією.
