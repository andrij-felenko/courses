# ⚙️ Інженерний калькулятор підбору приводу та перевірки теплового балансу ровера

Проектування приводу всюдихода потребує одночасної перевірки трьох різних фізичних меж: механічної достатності крутного моменту для подолання підйому, межі зчеплення коліс із ґрунтом (щоб не буксувати) та теплового балансу електродвигуна (щоб не спалити обмотки за 30 секунд перевантаження). Цей модуль реалізує повний алгоритм розрахунку динаміки шасі, редуктора, електричних параметрів живлення та теплового нагріву двигуна мовами C та C++.

## Математична модель та архітектура розрахунку

Утиліта моделює взаємодію між механічною частиною платформи, кінематикою трансмісії та електротермічними процесами всередині безколекторного або колекторного двигуна постійного струму. Програма приймає вектор конфігурації шасі (`RoverChassisConfig`) та специфікацію силової установки (`MotorGearboxConfig`).

Розрахунковий конвеєр складається з п'яти послідовних фізичних фаз:

### 1. Декомпозиція сил опору в плямі контакту

На похилій поверхні з кутом `θ` вага машини `m · g` розкладається на нормальну складову притискання `N = m · g · cos(θ)` та тангенціальну складову скочування `F_slope = m · g · sin(θ)`. Опір коченню шини чи гусениці `F_rr` виникає внаслідок гістерезисних втрат у деформованому матеріалі та несиметричного зміщення точки реакції ґрунту вперед на плече `b`:

```
F_rr = C_rr · m · g · cos(θ)
```

Сила інерційного розгону враховує не лише поступальну масу корпусу й батареї, а й приведену обертову інерцію ротора двигуна та шестерень через емпіричний коефіцієнт обертових мас `δ_rot`:

```
F_accel = m · δ_rot · a
```

Сумарне тягове зусилля, необхідне для руху вперед з розгоном:

```
F_total = F_rr + F_slope + F_accel
```

### 2. Трансляція сил у крутний момент і кутову швидкість осі

Сумарна тяга рівномірно розподіляється між ведучими колесами `N_drive`. Необхідний момент на осі одного колеса масштабується на коефіцієнт безпеки `k_safety` (зазвичай `1.20 – 1.40`), що враховує нерівності мікрорельєфу та втрати в колісних маточинах:

```
T_wheel = (F_total / N_drive) · r_wheel · k_safety
```

Кутова швидкість обертання колеса `ω_wheel = v_target / r_wheel` переводиться в технічні оберти за хвилину:

```
RPM_wheel = (ω_wheel · 60) / (2 · π)
```

### 3. Редукція та узгодження робочої точки двигуна

Передавальне число редуктора `i` підвищує крутний момент і знижує необхідну швидкість обертання, проте механічні втрати в зачепленнях зменшують корисний вихід на величину ККД `η_gearbox`:

```
T_motor = T_wheel / (i · η_gearbox)
RPM_motor = RPM_wheel · i
ω_motor = ω_wheel · i
```

Механічна потужність на валу одного двигуна та сумарна потужність усіх приводів:

```
P_mech_single = T_motor · ω_motor
P_mech_total = P_mech_single · N_drive
```

### 4. Електротермічна модель: струм, втрати в міді та стала температура

Константа крутного моменту двигуна `k_T` (Н·м/А) обернено пропорційна константі швидкості `KV` (об/хв на вольт):

```
k_T = 60 / (KV · 2 · π)
```

Струм фази якоря, необхідний для створення моменту `T_motor`:

```
I_armature = T_motor / k_T
```

Втрати потужності на нагрівання активного опору фази `R_phase` (джоулеве тепло в мідних обмотках):

```
P_loss_copper = I_armature² · R_phase
```

У стаціонарному режимі тривалого руху надлишкове тепло розсіюється через корпус двигуна в повітря з тепловим опором `R_thermal` (°C/Вт). Стала температура обмоток визначається як:

```
T_winding_steady = T_ambient + P_loss_copper · R_thermal
```

### 5. Багаторівневий аналіз безпеки та крайових випадків

Програма автоматично верифікує чотири критичні інженерні критерії:
1. **Номінальний момент (Continuous S1 Limit):** чи не перевищує тривалий момент робочої точки паспорту допустимого мотора `T_motor ≤ T_rated`.
2. **Запас до стопора (Stall Margin):** робоча точка повинна знаходитися на безпечній відстані від струму стопора (`T_motor ≤ 0.70 · T_stall`), щоб двигун не заклинив при зустрічі з невеликим каменем.
3. **Межа зчеплення з поверхнею (Traction Envelope):** тягове зусилля на колесі не повинно перевищувати граничну силу тертя спокою `F_grip = μ · N_wheel`, інакше колесо зірветься в буксування.
4. **Термічна безпека ізоляції (Thermal Limit):** стала температура обмотки повинна бути нижчою за термостійкість класу ізоляції (130°C для класу B, 155°C для класу F).

---

## Програмна реалізація: C та C++

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define PI 3.14159265358979323846
#define GRAVITY 9.80665

typedef struct {
    double mass_kg;             // Повна маса ровера з корисним вантажем
    double wheel_radius_m;      // Радіус колеса
    int    total_wheels;        // Загальна кількість коліс
    int    drive_wheels;        // Кількість тягових коліс (ведучих)
    double c_rr;                // Коефіцієнт опору коченню
    double mu_traction;         // Коефіцієнт зчеплення з поверхнею
    double slope_deg;           // Кут схилу в градусах
    double target_speed_mps;    // Максимальна робоча швидкість
    double target_accel_mps2;   // Лінійне прискорення розгону
    double safety_factor;       // Коефіцієнт інженерного запасу
} RoverChassisConfig;

typedef struct {
    double gear_ratio;          // Передавальне число редуктора i
    double gearbox_efficiency;  // ККД редуктора eta (0.0 .. 1.0)
    double kv_rpm_per_volt;     // Константа швидкості двигуна KV
    double phase_resistance_ohm;// Опір обмотки фази R
    double rated_torque_nm;     // Номінальний тривалий момент двигуна
    double stall_torque_nm;     // Пусковий / стопорний момент двигуна
    double thermal_res_c_per_w; // Тепловий опір корпус-середовище (°C/Вт)
    double max_winding_temp_c;  // Гранична температура ізоляції обмотки
    double ambient_temp_c;      // Температура навколишнього середовища
} MotorGearboxConfig;

typedef struct {
    double f_rr_n;
    double f_slope_n;
    double f_accel_n;
    double f_total_n;
    double t_wheel_nm;
    double t_motor_nm;
    double wheel_rpm;
    double motor_rpm;
    double p_mech_per_motor_w;
    double p_mech_total_w;
    double est_current_a;
    double copper_loss_w;
    double steady_temp_c;
    double max_grip_force_n;
    bool   torque_ok;
    bool   stall_margin_ok;
    bool   traction_ok;
    bool   thermal_ok;
} SizingResult;

SizingResult calculate_rover_drive(const RoverChassisConfig *chassis, 
                                  const MotorGearboxConfig *motor) {
    SizingResult res = {0};
    
    double theta_rad = chassis->slope_deg * (PI / 180.0);
    double cos_theta = cos(theta_rad);
    double sin_theta = sin(theta_rad);
    
    // 1. Розрахунок сил
    res.f_rr_n    = chassis->c_rr * chassis->mass_kg * GRAVITY * cos_theta;
    res.f_slope_n = chassis->mass_kg * GRAVITY * sin_theta;
    
    // Врахування еквівалентної інерції обертання (~1.20 для типових роверів)
    double rot_factor = 1.20;
    res.f_accel_n = chassis->mass_kg * rot_factor * chassis->target_accel_mps2;
    res.f_total_n = res.f_rr_n + res.f_slope_n + res.f_accel_n;
    
    // 2. Момент і швидкість колеса
    double force_per_wheel = res.f_total_n / chassis->drive_wheels;
    res.t_wheel_nm = force_per_wheel * chassis->wheel_radius_m * chassis->safety_factor;
    
    double omega_wheel = chassis->target_speed_mps / chassis->wheel_radius_m;
    res.wheel_rpm = (omega_wheel * 60.0) / (2.0 * PI);
    
    // 3. Вимоги до двигуна через редуктор
    res.t_motor_nm = res.t_wheel_nm / (motor->gear_ratio * motor->gearbox_efficiency);
    res.motor_rpm  = res.wheel_rpm * motor->gear_ratio;
    double omega_motor = omega_wheel * motor->gear_ratio;
    
    res.p_mech_per_motor_w = res.t_motor_nm * omega_motor;
    res.p_mech_total_w     = res.p_mech_per_motor_w * chassis->drive_wheels;
    
    // 4. Електричні втрати та температура
    double kt = 60.0 / (motor->kv_rpm_per_volt * 2.0 * PI);
    res.est_current_a = res.t_motor_nm / kt;
    
    res.copper_loss_w  = res.est_current_a * res.est_current_a * motor->phase_resistance_ohm;
    res.steady_temp_c  = motor->ambient_temp_c + (res.copper_loss_w * motor->thermal_res_c_per_w);
    
    // 5. Перевірка зчеплення з ґрунтом
    double normal_per_wheel = (chassis->mass_kg * GRAVITY * cos_theta) / chassis->total_wheels;
    res.max_grip_force_n    = chassis->mu_traction * normal_per_wheel;
    
    res.torque_ok       = (res.t_motor_nm <= motor->rated_torque_nm);
    res.stall_margin_ok = (res.t_motor_nm <= 0.70 * motor->stall_torque_nm);
    res.traction_ok     = (force_per_wheel <= res.max_grip_force_n);
    res.thermal_ok      = (res.steady_temp_c < motor->max_winding_temp_c);
    
    return res;
}

void print_sizing_report(const SizingResult *r) {
    printf("============================================================\n");
    printf("         ЗВІТ РОЗРАХУНКУ ПРИВОДУ РОВЕРА                    \n");
    printf("============================================================\n");
    printf("Сила опору коченню F_rr:      %7.2f Н\n", r->f_rr_n);
    printf("Сила подолання схилу F_slope:  %7.2f Н\n", r->f_slope_n);
    printf("Динамічна сила розгону F_acc: %7.2f Н\n", r->f_accel_n);
    printf("СУМАРНА ПОТРІБНА ТЯГА:        %7.2f Н\n", r->f_total_n);
    printf("------------------------------------------------------------\n");
    printf("Момент на 1 колесі:           %7.3f Н·м  (%5.1f RPM)\n", r->t_wheel_nm, r->wheel_rpm);
    printf("Потрібний момент мотора:      %7.4f Н·м  (%5.0f RPM)\n", r->t_motor_nm, r->motor_rpm);
    printf("Механічна потужність (1 двиг):%7.2f Вт\n", r->p_mech_per_motor_w);
    printf("Механічна потужність (сумарна):%6.2f Вт\n", r->p_mech_total_w);
    printf("------------------------------------------------------------\n");
    printf("Оціночний струм фази:         %7.2f А\n", r->est_current_a);
    printf("Теплові втрати в міді I²·R:   %7.2f Вт\n", r->copper_loss_w);
    printf("Стала температура обмотки:    %7.1f °C\n", r->steady_temp_c);
    printf("------------------------------------------------------------\n");
    printf("ПЕРЕВІРКИ БЕЗПЕКИ ТА ПРАЦЕЗДАТНОСТІ:\n");
    printf(" [ %s ] Номінальний момент мотора  (T_req <= T_rated)\n", r->torque_ok ? "OK" : "ПЕРЕВАНТАЖЕННЯ");
    printf(" [ %s ] Запас до стопора (>30%%)    (T_req <= 0.70*T_stall)\n", r->stall_margin_ok ? "OK" : "НЕБЕЗПЕКА СТОПОРА");
    printf(" [ %s ] Зчеплення з ґрунтом        (F_req <= F_grip_max)\n", r->traction_ok ? "OK" : "ПРОБУКСОВУВАННЯ");
    printf(" [ %s ] Тепловий режим обмотки     (T_steady < T_max)\n", r->thermal_ok ? "OK" : "ПЕРЕГРІВ");
    printf("============================================================\n");
}

int main(void) {
    RoverChassisConfig chassis = {
        .mass_kg           = 16.0,
        .wheel_radius_m    = 0.075,
        .total_wheels      = 4,
        .drive_wheels      = 4,
        .c_rr              = 0.08,
        .mu_traction       = 0.55,
        .slope_deg         = 20.0,
        .target_speed_mps  = 1.5,
        .target_accel_mps2 = 0.75,
        .safety_factor     = 1.25
    };
    
    MotorGearboxConfig motor = {
        .gear_ratio           = 36.0,
        .gearbox_efficiency   = 0.80,
        .kv_rpm_per_volt      = 520.0,
        .phase_resistance_ohm = 0.28,
        .rated_torque_nm      = 0.12,
        .stall_torque_nm      = 0.45,
        .thermal_res_c_per_w  = 2.4,
        .max_winding_temp_c   = 130.0,
        .ambient_temp_c       = 25.0
    };
    
    SizingResult res = calculate_rover_drive(&chassis, &motor);
    print_sizing_report(&res);
    
    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <numbers>
#include <cmath>
#include <string_view>

namespace rover {

inline constexpr double Gravity = 9.80665;

struct ChassisConfig {
    double mass_kg{16.0};
    double wheel_radius_m{0.075};
    int    total_wheels{4};
    int    drive_wheels{4};
    double c_rr{0.08};
    double mu_traction{0.55};
    double slope_deg{20.0};
    double target_speed_mps{1.5};
    double target_accel_mps2{0.75};
    double safety_factor{1.25};
};

struct DrivetrainConfig {
    double gear_ratio{36.0};
    double gearbox_efficiency{0.80};
    double kv_rpm_per_volt{520.0};
    double phase_resistance_ohm{0.28};
    double rated_torque_nm{0.12};
    double stall_torque_nm{0.45};
    double thermal_res_c_per_w{2.4};
    double max_winding_temp_c{130.0};
    double ambient_temp_c{25.0};
};

struct CalculationResult {
    double f_rr_n{0.0};
    double f_slope_n{0.0};
    double f_accel_n{0.0};
    double f_total_n{0.0};
    double t_wheel_nm{0.0};
    double t_motor_nm{0.0};
    double wheel_rpm{0.0};
    double motor_rpm{0.0};
    double p_mech_per_motor_w{0.0};
    double p_mech_total_w{0.0};
    double est_current_a{0.0};
    double copper_loss_w{0.0};
    double steady_temp_c{0.0};
    double max_grip_force_n{0.0};
    bool   torque_ok{false};
    bool   stall_margin_ok{false};
    bool   traction_ok{false};
    bool   thermal_ok{false};
};

class DriveSizingCalculator {
public:
    [[nodiscard]] static constexpr CalculationResult evaluate(
        const ChassisConfig& chassis,
        const DrivetrainConfig& drive) noexcept 
    {
        CalculationResult res{};
        
        const double theta_rad = chassis.slope_deg * (std::numbers::pi / 180.0);
        const double cos_theta = std::cos(theta_rad);
        const double sin_theta = std::sin(theta_rad);
        
        res.f_rr_n    = chassis.c_rr * chassis.mass_kg * Gravity * cos_theta;
        res.f_slope_n = chassis.mass_kg * Gravity * sin_theta;
        
        constexpr double rot_factor = 1.20;
        res.f_accel_n = chassis.mass_kg * rot_factor * chassis.target_accel_mps2;
        res.f_total_n = res.f_rr_n + res.f_slope_n + res.f_accel_n;
        
        const double force_per_wheel = res.f_total_n / chassis.drive_wheels;
        res.t_wheel_nm = force_per_wheel * chassis.wheel_radius_m * chassis.safety_factor;
        
        const double omega_wheel = chassis.target_speed_mps / chassis.wheel_radius_m;
        res.wheel_rpm = (omega_wheel * 60.0) / (2.0 * std::numbers::pi);
        
        res.t_motor_nm = res.t_wheel_nm / (drive.gear_ratio * drive.gearbox_efficiency);
        res.motor_rpm  = res.wheel_rpm * drive.gear_ratio;
        const double omega_motor = omega_wheel * drive.gear_ratio;
        
        res.p_mech_per_motor_w = res.t_motor_nm * omega_motor;
        res.p_mech_total_w     = res.p_mech_per_motor_w * chassis.drive_wheels;
        
        const double kt = 60.0 / (drive.kv_rpm_per_volt * 2.0 * std::numbers::pi);
        res.est_current_a = res.t_motor_nm / kt;
        
        res.copper_loss_w  = res.est_current_a * res.est_current_a * drive.phase_resistance_ohm;
        res.steady_temp_c  = drive.ambient_temp_c + (res.copper_loss_w * drive.thermal_res_c_per_w);
        
        const double normal_per_wheel = (chassis.mass_kg * Gravity * cos_theta) / chassis.total_wheels;
        res.max_grip_force_n    = chassis.mu_traction * normal_per_wheel;
        
        res.torque_ok       = (res.t_motor_nm <= drive.rated_torque_nm);
        res.stall_margin_ok = (res.t_motor_nm <= 0.70 * drive.stall_torque_nm);
        res.traction_ok     = (force_per_wheel <= res.max_grip_force_n);
        res.thermal_ok      = (res.steady_temp_c < drive.max_winding_temp_c);
        
        return res;
    }
};

void print_report(const CalculationResult& r) {
    auto status_str = [](bool ok, std::string_view fail_msg) -> std::string_view {
        return ok ? "OK" : fail_msg;
    };

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "============================================================\n"
              << "         ЗВІТ РОЗРАХУНКУ ПРИВОДУ РОВЕРА (C++20)             \n"
              << "============================================================\n"
              << "Сила опору коченню F_rr:      " << std::setw(7) << r.f_rr_n << " Н\n"
              << "Сила подолання схилу F_slope:  " << std::setw(7) << r.f_slope_n << " Н\n"
              << "Динамічна сила розгону F_acc: " << std::setw(7) << r.f_accel_n << " Н\n"
              << "СУМАРНА ПОТРІБНА ТЯГА:        " << std::setw(7) << r.f_total_n << " Н\n"
              << "------------------------------------------------------------\n"
              << "Момент на 1 колесі:           " << std::setw(7) << r.t_wheel_nm << " Н·м  (" << r.wheel_rpm << " RPM)\n"
              << "Потрібний момент мотора:      " << std::setw(7) << r.t_motor_nm << " Н·м  (" << r.motor_rpm << " RPM)\n"
              << "Механічна потужність (1 двиг):" << std::setw(7) << r.p_mech_per_motor_w << " Вт\n"
              << "Механічна потужність (сумарна):" << std::setw(6) << r.p_mech_total_w << " Вт\n"
              << "------------------------------------------------------------\n"
              << "Оціночний струм фази:         " << std::setw(7) << r.est_current_a << " А\n"
              << "Теплові втрати в міді I²·R:   " << std::setw(7) << r.copper_loss_w << " Вт\n"
              << "Стала температура обмотки:    " << std::setw(7) << r.steady_temp_c << " °C\n"
              << "------------------------------------------------------------\n"
              << "ПЕРЕВІРКИ БЕЗПЕКИ ТА ПРАЦЕЗДАТНОСТІ:\n"
              << " [ " << status_str(r.torque_ok, "ПЕРЕВАНТАЖЕННЯ") << " ] Номінальний момент мотора\n"
              << " [ " << status_str(r.stall_margin_ok, "НЕБЕЗПЕКА СТОПОРА") << " ] Запас до стопора (>30%)\n"
              << " [ " << status_str(r.traction_ok, "ПРОБУКСОВУВАННЯ") << " ] Зчеплення з ґрунтом\n"
              << " [ " << status_str(r.thermal_ok, "ПЕРЕГРІВ") << " ] Тепловий режим обмотки\n"
              << "============================================================\n";
}

} // namespace rover

int main() {
    rover::ChassisConfig chassis{};
    rover::DrivetrainConfig drive{};
    
    const auto result = rover::DriveSizingCalculator::evaluate(chassis, drive);
    rover::print_report(result);
    
    return 0;
}
```
:::

## Інженерний аналіз результатів та типові сценарії підбору

За результатами виконання програми інженер отримує чітку картину сумісності компонентів. Розглянемо, як інтерпретувати типові діагностичні повідомлення калькулятора та які корективи вносити в конструкцію:

1. **Помилка `ПЕРЕВАНТАЖЕННЯ` (T_motor > T_rated):**
   Робоча точка вимагає від мотора моменту, що перевищує його довготривалий паспортний ліміт. Це означає, що або передавальне число `i` занадто мале (двигун не встигає набрати оберти для розвитку проти-ЕРС), або сам двигун має недостатній габарит статора. Розв'язок: збільшити передавальне число редуктора (наприклад, з 36:1 до 50:1) або обрати мотор із більшим діаметром магнітного кільця (більший `k_T`).

2. **Помилка `ПРОБУКСОВУВАННЯ` (F_wheel > F_grip_max):**
   Привід намагається передати на колесо силу, що перевищує максимальну силу тертя спокою. Збільшення потужності мотора тут не дасть жодного ефекту — колеса просто будуть буксувати на місці. Розв'язок: збільшити діаметр або ширину коліс для зниження контактного тиску, перейти з моноприводу на повний привід (4WD/6WD) для розподілу тяги на більшу кількість плям контакту, або використати шини з агресивним ґрунтозачіпним протектором.

3. **Помилка `ПЕРЕГРІВ` (T_steady > T_max):**
   При поточному струмі втрати `I² · R` настільки великі, що природне охолодження не здатне розсіяти тепло. Якщо перевантаження триватиме понад 1–2 хвилини, ізоляція обмоток деградує. Розв'язок: встановити алюмінієві радіатори з термопастою на корпус мотора, перевести систему на вищу напругу живлення (наприклад, з 12 В на 24 В чи 36 В) для пропорційного зменшення струму при тій самій потужності, або використати двигун із товстішим дротом обмоток (менший опір `R_phase`).
