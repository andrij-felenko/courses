# ⚙️ Калькулятор маневреності та параметрів звалювання крила

Бортовий комп'ютер сучасного безпілотного літального апарата або пілотажно-навігаційний комплекс пілотованого літака мусить у реальному часі контролювати межі безпечного польоту. Щойно апарат виконує різкий маневр ухилення, крутий віраж над ціллю чи заходить на посадку за шквального бічного вітру, запас до звалювання (англ. *stall margin*) стрімко скорочується через зростання нормального перевантаження `n_z` та зміну місцевої густини повітря `ρ`.

Щоб автопілот не вивів літак на закритичний кут атаки й водночас не зруйнував конструкцію надмірним зусиллям на кермі висоти, алгоритм польотного контролера обчислює польотний конверт (діаграму маневреності V-n), миттєву швидкість звалювання у віражі та динамічний приріст навантаження від вертикальних поривів вітру.

## Архітектура розрахункового модуля

Програмний модуль розв'язує комплекс із п'яти взаємопов'язаних інженерних задач, кожна з яких моделює реальну фізику взаємодії крила з набігаючим потоком повітря:

### 1. Модель стандартної атмосфери (ISA)
Густина повітря монотонно спадає з висотою, тому швидкість звалювання за істинною повітряною швидкістю (англ. *True Airspeed*, TAS) безперервно зростає. Модуль розраховує термодинамічні параметри атмосфери за міжнародним стандартом ISA (англ. *International Standard Atmosphere*) для висот тропосфери (від 0 до 11 000 метрів):

```
T(h) = T₀ − L · h                          [температура повітря на висоті h]
p(h) = p₀ · (1 − L·h / T₀)^{g / (R·L)}     [статичний барометричний тиск]
ρ(h) = p(h) / (R_air · T(h))               [густина повітря за законом Менделєєва–Клапейрона]
```

Константи стандарту: температура на рівні моря `T₀ = 288.15 К` (+15 °C), статичний тиск `p₀ = 101325 Па`, вертикальний температурний градієнт `L = 0.0065 К/м`, питома газова стала сухого повітря `R_air = 287.058 Дж/(кг·К)`.

### 2. Питоме навантаження на крило та базова швидкість звалювання
Питоме навантаження на крило `W/S` визначає силу тяжіння, яку мусить урівноважувати кожен квадратний метр площі крила в усталеному горизонтальному польоті. Мінімальна швидкість звалювання `v_s0` на рівні моря та `v_s(h)` на робочій висоті виводяться з умови рівноваги повної підйомної сили та ваги апарата `L = W = m·g`:

```
W/S = (m · g) / S                          [питоме навантаження на крило, Па = Н/м²]
v_s0 = √( 2 · (W/S) / (ρ₀ · C_L,max) )     [швидкість звалювання на рівні моря]
v_s(h) = √( 2 · (W/S) / (ρ(h) · C_L,max) ) [істинна швидкість звалювання на висоті h]
```

### 3. Кінематика та баланс сил у координованому віражі
У правильному горизонтальному розвороті без внутрішнього або зовнішнього ковзання (англ. *coordinated turn*) вектор підйомної сили нахиляється на кут крену `φ`. Її вертикальна складова утримує вагу апарата `L·cos φ = m·g`, а горизонтальна складова забезпечує доцентрову силу для викривлення траєкторії `L·sin φ = m·v²/R`. Звідси нормальне перевантаження, швидкість звалювання, радіус віражу та кутова швидкість розвороту становлять:

```
n_z = 1 / cos φ                            [нормальне аеродинамічне перевантаження]
v_stall(φ) = v_s · √(n_z) = v_s / √(cos φ) [швидкість звалювання за крену φ]
R_turn = v² / (g · tg φ)                   [геометричний радіус розвороту]
ω_turn = (g · tg φ) / v                    [кутова швидкість розвороту в горизонтальній площині]
```

Алгоритм використовує ці співвідношення для обчислення динамічного запасу швидкості: автопілот відстежує відношення поточної швидкості до поточної швидкості звалювання `Margin = v / v_stall(φ)` і блокує збільшення крену, якщо запас падає нижче безпечного порога (зазвичай 1.25–1.30).

### 4. Розрахунок діаграми маневреності V-n (Flight Envelope)
Діаграма маневреності описує безпечний простір станів літального апарата в осях «повітряна швидкість `v` — нормальне перевантаження `n`». Конверт обмежений чотирма фізичними та міцнісними бар'єрами:
- **Параболічна межа додатного аеродинамічного зриву:** крива `n_max,aero(v) = ½·ρ·v²·C_L,max / (W/S)`.
- **Параболічна межа від'ємного аеродинамічного зриву:** крива `n_min,aero(v) = −½·ρ·v²·|C_L,min| / (W/S)`.
- **Конструктивні межі міцності лонжеронів:** горизонтальні лінії `+n_max,struct` та `−n_max,struct`.
- **Швидкість маневрування `V_A` (Corner Speed):** критична швидкість перетину кривої максимального коефіцієнта підйому `C_L,max` та лінії граничного додатного перевантаження `+n_max,struct`:
  ```
  V_A = v_s0 · √(n_max,struct)             [швидкість маневрування]
  ```
  Ця точка має вирішальне значення для безпеки керування: на швидкостях `v ≤ V_A` максимальне миттєве відхилення керма висоти спричиняє лише аеродинамічний зрив потоку (крило самостійно «скидає» зайве навантаження), захищаючи силовий набір від руйнування. На швидкостях `v > V_A` потік не зривається завчасно, і різкий маневр створює перевантаження `n > n_max`, що загрожує пластичними деформаціями або відривом консолей крила.

### 5. Оцінка навантаження від вертикального пориву вітру (Формула Пратта)
Під час польоту в турбулентній атмосфері літак перетинає висхідні та низхідні пориви повітря зі швидкістю `w_gust`. Це створює миттєву зміну ефективного кута атаки `Δα ≈ w_gust / v`. За авіаційними нормами FAR-23/25 та CS-VLA приріст перевантаження розраховують з урахуванням безрозмірного коефіцієнта маси літака `μ_g` та коефіцієнта послаблення пориву за Праттом `K_g`:

```
μ_g = 2 · (m / S) / (ρ · c_mac · a)        [безрозмірний коефіцієнт маси літака]
K_g = (0.88 · μ_g) / (5.3 + μ_g)           [коефіцієнт послаблення пориву за Праттом]
Δn_gust = (K_g · ρ · v · a · w_gust) / (2 · (W/S)) [приріст нормального перевантаження]
```

де `c_mac` — середня аеродинамічна хорда крила (англ. *Mean Aerodynamic Chord*, MAC), `a = dC_L/dα` — нахил кривої підйомної сили літака в радіанній мірі (типово `4.8 ... 5.6 рад⁻¹`).

## Програмна реалізація

Нижче наведено модулі мовами C та C++. У вкладці C реалізовано процедурний інтерфейс з фіксованими структурами даних та контролем кодів повернення. У вкладці C++ реалізовано об'єктний калькулятор з використанням методів стандартної бібліотеки, безпечних типів `std::optional`, `std::string_view` та математичних констант `std::numbers`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define GRAVITY_G 9.80665
#define ISA_T0 288.15
#define ISA_P0 101325.0
#define ISA_LAPSE_RATE 0.0065
#define ISA_R_AIR 287.058
#define DEG_TO_RAD (3.14159265358979323846 / 180.0)
#define RAD_TO_DEG (180.0 / 3.14159265358979323846)

typedef struct {
    double mass_kg;          /* злітна маса апарата, кг */
    double wing_area_m2;     /* площа крила, м² */
    double mac_m;            /* середня аеродинамічна хорда, м */
    double cl_max_pos;       /* максимальний коефіцієнт підйому C_L,max */
    double cl_max_neg;       /* максимальний від'ємний коефіцієнт C_L,min (за модулем) */
    double dcl_dalpha_rad;   /* нахил кривої підйомної сили dC_L/dα (рад⁻¹) */
    double n_max_pos;        /* граничне експлуатаційне додатне перевантаження */
    double n_max_neg;        /* граничне експлуатаційне від'ємне перевантаження */
    double v_ne_ms;          /* гранично допустима швидкість V_NE, м/с */
} AircraftSpecs;

typedef struct {
    double altitude_m;
    double temperature_k;
    double pressure_pa;
    double density_kg_m3;
} AtmosphereState;

typedef struct {
    double bank_deg;
    double load_factor_g;
    double stall_speed_ms;
    double turn_radius_m;
    double turn_rate_deg_s;
} BankAnalysisPoint;

typedef struct {
    double wing_loading_n_m2;    /* питоме навантаження W/S, Н/м² */
    double wing_loading_kg_m2;   /* питоме навантаження m/S, кг/м² */
    double v_stall_0_ms;         /* швидкість звалювання 1g на рівні моря, м/с */
    double v_stall_alt_ms;       /* швидкість звалювання 1g на розрахунковій висоті, м/с */
    double v_maneuver_va_ms;     /* швидкість маневрування V_A (Corner Speed), м/с */
    double v_maneuver_va_neg_ms; /* швидкість маневрування на від'ємне перевантаження, м/с */
} FlightEnvelopeSummary;

typedef struct {
    double gust_speed_ms;        /* швидкість вертикального пориву, м/с */
    double flight_speed_ms;      /* швидкість польоту літака, м/с */
    double mass_ratio_mu_g;      /* безрозмірний коефіцієнт маси μ_g */
    double gust_alleviation_kg;  /* коефіцієнт послаблення пориву K_g */
    double delta_n_g;            /* приріст перевантаження Δn від пориву */
    double total_n_g;            /* сумарне нормальне перевантаження 1 + Δn */
} GustAnalysis;

/* Розрахунок параметрів стандартної атмосфери ISA */
AtmosphereState calculate_isa_atmosphere(double altitude_m) {
    AtmosphereState atmo;
    atmo.altitude_m = altitude_m;
    if (altitude_m < 0.0) altitude_m = 0.0;
    if (altitude_m > 11000.0) altitude_m = 11000.0; /* межа тропосфери */

    atmo.temperature_k = ISA_T0 - ISA_LAPSE_RATE * altitude_m;
    double exponent = GRAVITY_G / (ISA_R_AIR * ISA_LAPSE_RATE);
    atmo.pressure_pa = ISA_P0 * pow(atmo.temperature_k / ISA_T0, exponent);
    atmo.density_kg_m3 = atmo.pressure_pa / (ISA_R_AIR * atmo.temperature_k);
    return atmo;
}

/* Розрахунок ключових точок польотного конверта */
FlightEnvelopeSummary calculate_flight_envelope(const AircraftSpecs *ac, double altitude_m) {
    FlightEnvelopeSummary env;
    double weight_n = ac->mass_kg * GRAVITY_G;
    env.wing_loading_n_m2 = weight_n / ac->wing_area_m2;
    env.wing_loading_kg_m2 = ac->mass_kg / ac->wing_area_m2;

    AtmosphereState atmo_sea = calculate_isa_atmosphere(0.0);
    AtmosphereState atmo_alt = calculate_isa_atmosphere(altitude_m);

    /* v_s0 = sqrt(2 * (W/S) / (rho * C_L_max)) */
    env.v_stall_0_ms = sqrt(2.0 * env.wing_loading_n_m2 / (atmo_sea.density_kg_m3 * ac->cl_max_pos));
    env.v_stall_alt_ms = sqrt(2.0 * env.wing_loading_n_m2 / (atmo_alt.density_kg_m3 * ac->cl_max_pos));

    /* V_A = v_s0 * sqrt(n_max) */
    env.v_maneuver_va_ms = env.v_stall_0_ms * sqrt(ac->n_max_pos);

    /* V_A_neg = v_s0_neg * sqrt(|n_max_neg|) */
    double v_stall_neg = sqrt(2.0 * env.wing_loading_n_m2 / (atmo_sea.density_kg_m3 * ac->cl_max_neg));
    env.v_maneuver_va_neg_ms = v_stall_neg * sqrt(fabs(ac->n_max_neg));

    return env;
}

/* Розрахунок параметрів віражу за заданого крену */
bool calculate_bank_turn(const AircraftSpecs *ac, double altitude_m, double bank_deg,
                         double true_airspeed_ms, BankAnalysisPoint *out_point) {
    if (!ac || !out_point || bank_deg < 0.0 || bank_deg >= 85.0) {
        return false;
    }

    AtmosphereState atmo = calculate_isa_atmosphere(altitude_m);
    double weight_n = ac->mass_kg * GRAVITY_G;
    double ws = weight_n / ac->wing_area_m2;
    double bank_rad = bank_deg * DEG_TO_RAD;
    double cos_phi = cos(bank_rad);

    out_point->bank_deg = bank_deg;
    out_point->load_factor_g = 1.0 / cos_phi;

    /* Швидкість звалювання у віражі */
    out_point->stall_speed_ms = sqrt(2.0 * ws * out_point->load_factor_g / (atmo.density_kg_m3 * ac->cl_max_pos));

    /* Радіус та кутова швидкість */
    if (bank_deg < 0.1) {
        out_point->turn_radius_m = 1e9; /* прямолінійний політ */
        out_point->turn_rate_deg_s = 0.0;
    } else {
        double tan_phi = tan(bank_rad);
        out_point->turn_radius_m = (true_airspeed_ms * true_airspeed_ms) / (GRAVITY_G * tan_phi);
        out_point->turn_rate_deg_s = (GRAVITY_G * tan_phi / true_airspeed_ms) * RAD_TO_DEG;
    }

    return true;
}

/* Оцінка навантаження від вертикального пориву вітру за формулою Пратта */
GustAnalysis calculate_gust_response(const AircraftSpecs *ac, double altitude_m,
                                     double airspeed_ms, double gust_speed_ms) {
    GustAnalysis g;
    AtmosphereState atmo = calculate_isa_atmosphere(altitude_m);
    double ws_kg_m2 = ac->mass_kg / ac->wing_area_m2;
    double ws_n_m2 = ws_kg_m2 * GRAVITY_G;

    g.gust_speed_ms = gust_speed_ms;
    g.flight_speed_ms = airspeed_ms;

    /* Безрозмірний коефіцієнт маси: mu_g = 2 * (m/S) / (rho * c_mac * a) */
    g.mass_ratio_mu_g = (2.0 * ws_kg_m2) / (atmo.density_kg_m3 * ac->mac_m * ac->dcl_dalpha_rad);

    /* Коефіцієнт послаблення Пратта: K_g = (0.88 * mu_g) / (5.3 + mu_g) */
    g.gust_alleviation_kg = (0.88 * g.mass_ratio_mu_g) / (5.3 + g.mass_ratio_mu_g);

    /* Приріст перевантаження: Delta_n = (K_g * rho * v * a * w) / (2 * W/S) */
    g.delta_n_g = (g.gust_alleviation_kg * atmo.density_kg_m3 * airspeed_ms *
                   ac->dcl_dalpha_rad * gust_speed_ms) / (2.0 * ws_n_m2);
    g.total_n_g = 1.0 + g.delta_n_g;

    return g;
}

int main(void) {
    /* Параметри типового тактичного розвідувального БПЛА літакового типу */
    AircraftSpecs uav = {
        .mass_kg = 18.5,
        .wing_area_m2 = 0.85,
        .mac_m = 0.35,
        .cl_max_pos = 1.45,
        .cl_max_neg = 0.85,
        .dcl_dalpha_rad = 5.2,
        .n_max_pos = 4.5,
        .n_max_neg = -2.0,
        .v_ne_ms = 48.0
    };

    printf("=== РОЗРАХУНОК ПОЛЬОТНОГО КОНВЕРТА БПЛА ===\n");
    FlightEnvelopeSummary env = calculate_flight_envelope(&uav, 1500.0);
    printf("Питоме навантаження на крило W/S: %.2f Н/м² (%.2f кг/м²)\n",
           env.wing_loading_n_m2, env.wing_loading_kg_m2);
    printf("Швидкість звалювання 1g (H=0 м):  %.2f м/с (%.1f км/год)\n",
           env.v_stall_0_ms, env.v_stall_0_ms * 3.6);
    printf("Швидкість звалювання 1g (H=1500 м): %.2f м/с (%.1f км/год)\n",
           env.v_stall_alt_ms, env.v_stall_alt_ms * 3.6);
    printf("Швидкість маневрування V_A (Corner): %.2f м/с (%.1f км/год)\n\n",
           env.v_maneuver_va_ms, env.v_maneuver_va_ms * 3.6);

    printf("=== ЗМІНА ШВИДКОСТІ ЗВАЛЮВАННЯ ТА ПЕРЕВАНТАЖЕННЯ У ВІРАЖІ (v = 28 м/с) ===\n");
    printf("  Крен φ  |  Перевантаження n_z  |  v_зв (м/с)  |  Радіус R (м)  |  Омега (град/с)\n");
    printf("----------+----------------------+--------------+----------------+----------------\n");
    double bank_angles[] = {0.0, 15.0, 30.0, 45.0, 60.0, 70.0, 75.0};
    for (size_t i = 0; i < sizeof(bank_angles)/sizeof(bank_angles[0]); ++i) {
        BankAnalysisPoint pt;
        if (calculate_bank_turn(&uav, 500.0, bank_angles[i], 28.0, &pt)) {
            printf("   %2.0f°    |       %4.2f g        |    %5.2f     |     %6.1f     |     %5.1f\n",
                   pt.bank_deg, pt.load_factor_g, pt.stall_speed_ms, pt.turn_radius_m, pt.turn_rate_deg_s);
        }
    }

    printf("\n=== ОЦІНКА ВЕРТИКАЛЬНОГО ПОРИВУ ВІТРУ (H=500 м, v=30 м/с, w=7 м/с) ===\n");
    GustAnalysis gust = calculate_gust_response(&uav, 500.0, 30.0, 7.0);
    printf("Коефіцієнт маси μ_g:         %.2f\n", gust.mass_ratio_mu_g);
    printf("Коефіцієнт послаблення K_g:  %.3f\n", gust.gust_alleviation_kg);
    printf("Приріст перевантаження Δn:   +%.2f g\n", gust.delta_n_g);
    printf("Сумарне перевантаження n:    %.2f g (допустиме n_max = %.1f g)\n",
           gust.total_n_g, uav.n_max_pos);

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <numbers>
#include <optional>
#include <stdexcept>

namespace aero {

constexpr double g_accel = 9.80665;
constexpr double isa_t0 = 288.15;
constexpr double isa_p0 = 101325.0;
constexpr double isa_lapse_rate = 0.0065;
constexpr double isa_r_air = 287.058;

struct AtmosphereState {
    double altitude_m{0.0};
    double temperature_k{isa_t0};
    double pressure_pa{isa_p0};
    double density_kg_m3{1.225};
};

struct AircraftSpecs {
    double mass_kg;          // злітна маса, кг
    double wing_area_m2;     // площа крила, м²
    double mac_m;            // середня аеродинамічна хорда, м
    double cl_max_pos;       // C_L,max
    double cl_max_neg;       // C_L,min (за модулем)
    double dcl_dalpha_rad;   // dC_L/dα (рад⁻¹)
    double n_max_pos;        // +n_max
    double n_max_neg;        // -n_max
    double v_ne_ms;          // V_NE, м/с
};

struct FlightEnvelopeSummary {
    double wing_loading_n_m2;
    double wing_loading_kg_m2;
    double v_stall_0_ms;
    double v_stall_alt_ms;
    double v_maneuver_va_ms;
    double v_maneuver_va_neg_ms;
};

struct BankTurnResult {
    double bank_deg;
    double load_factor_g;
    double stall_speed_ms;
    double turn_radius_m;
    double turn_rate_deg_s;
};

struct GustResult {
    double gust_speed_ms;
    double flight_speed_ms;
    double mass_ratio_mu_g;
    double gust_alleviation_kg;
    double delta_n_g;
    double total_n_g;
};

class FlightDynamicsCalculator {
public:
    explicit FlightDynamicsCalculator(AircraftSpecs specs)
        : specs_(std::move(specs)) {
        if (specs_.mass_kg <= 0.0 || specs_.wing_area_m2 <= 0.0 || specs_.cl_max_pos <= 0.0) {
            throw std::invalid_argument("Некоректні геометричні або масові параметри ЛА");
        }
    }

    [[nodiscard]] static AtmosphereState get_isa_atmosphere(double altitude_m) noexcept {
        AtmosphereState atmo;
        atmo.altitude_m = std::clamp(altitude_m, 0.0, 11000.0);
        atmo.temperature_k = isa_t0 - isa_lapse_rate * atmo.altitude_m;
        const double exponent = g_accel / (isa_r_air * isa_lapse_rate);
        atmo.pressure_pa = isa_p0 * std::pow(atmo.temperature_k / isa_t0, exponent);
        atmo.density_kg_m3 = atmo.pressure_pa / (isa_r_air * atmo.temperature_k);
        return atmo;
    }

    [[nodiscard]] FlightEnvelopeSummary compute_envelope(double altitude_m) const noexcept {
        const double weight_n = specs_.mass_kg * g_accel;
        const double ws_n = weight_n / specs_.wing_area_m2;
        const double ws_kg = specs_.mass_kg / specs_.wing_area_m2;

        const auto atmo_sea = get_isa_atmosphere(0.0);
        const auto atmo_alt = get_isa_atmosphere(altitude_m);

        const double vs0 = std::sqrt(2.0 * ws_n / (atmo_sea.density_kg_m3 * specs_.cl_max_pos));
        const double vs_alt = std::sqrt(2.0 * ws_n / (atmo_alt.density_kg_m3 * specs_.cl_max_pos));
        const double va = vs0 * std::sqrt(specs_.n_max_pos);

        const double vs_neg = std::sqrt(2.0 * ws_n / (atmo_sea.density_kg_m3 * specs_.cl_max_neg));
        const double va_neg = vs_neg * std::sqrt(std::abs(specs_.n_max_neg));

        return {
            .wing_loading_n_m2 = ws_n,
            .wing_loading_kg_m2 = ws_kg,
            .v_stall_0_ms = vs0,
            .v_stall_alt_ms = vs_alt,
            .v_maneuver_va_ms = va,
            .v_maneuver_va_neg_ms = va_neg
        };
    }

    [[nodiscard]] std::optional<BankTurnResult> compute_bank_turn(
        double altitude_m, double bank_deg, double true_airspeed_ms) const noexcept {
        if (bank_deg < 0.0 || bank_deg >= 85.0 || true_airspeed_ms <= 0.0) {
            return std::nullopt;
        }

        const auto atmo = get_isa_atmosphere(altitude_m);
        const double ws_n = (specs_.mass_kg * g_accel) / specs_.wing_area_m2;
        const double bank_rad = bank_deg * std::numbers::pi / 180.0;
        const double cos_phi = std::cos(bank_rad);
        const double nz = 1.0 / cos_phi;

        const double v_stall_turn = std::sqrt(2.0 * ws_n * nz / (atmo.density_kg_m3 * specs_.cl_max_pos));

        double radius = 1e9;
        double omega_deg_s = 0.0;
        if (bank_deg >= 0.1) {
            const double tan_phi = std::tan(bank_rad);
            radius = (true_airspeed_ms * true_airspeed_ms) / (g_accel * tan_phi);
            omega_deg_s = (g_accel * tan_phi / true_airspeed_ms) * (180.0 / std::numbers::pi);
        }

        return BankTurnResult{
            .bank_deg = bank_deg,
            .load_factor_g = nz,
            .stall_speed_ms = v_stall_turn,
            .turn_radius_m = radius,
            .turn_rate_deg_s = omega_deg_s
        };
    }

    [[nodiscard]] GustResult compute_gust(double altitude_m, double airspeed_ms, double gust_ms) const noexcept {
        const auto atmo = get_isa_atmosphere(altitude_m);
        const double ws_kg = specs_.mass_kg / specs_.wing_area_m2;
        const double ws_n = ws_kg * g_accel;

        const double mu_g = (2.0 * ws_kg) / (atmo.density_kg_m3 * specs_.mac_m * specs_.dcl_dalpha_rad);
        const double k_g = (0.88 * mu_g) / (5.3 + mu_g);
        const double delta_n = (k_g * atmo.density_kg_m3 * airspeed_ms * specs_.dcl_dalpha_rad * gust_ms) / (2.0 * ws_n);

        return {
            .gust_speed_ms = gust_ms,
            .flight_speed_ms = airspeed_ms,
            .mass_ratio_mu_g = mu_g,
            .gust_alleviation_kg = k_g,
            .delta_n_g = delta_n,
            .total_n_g = 1.0 + delta_n
        };
    }

private:
    AircraftSpecs specs_;
};

} // namespace aero

int main() {
    using namespace aero;

    const AircraftSpecs uav{
        .mass_kg = 18.5,
        .wing_area_m2 = 0.85,
        .mac_m = 0.35,
        .cl_max_pos = 1.45,
        .cl_max_neg = 0.85,
        .dcl_dalpha_rad = 5.2,
        .n_max_pos = 4.5,
        .n_max_neg = -2.0,
        .v_ne_ms = 48.0
    };

    const FlightDynamicsCalculator calc(uav);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== РОЗРАХУНОК ПОЛЬОТНОГО КОНВЕРТА БПЛА (C++20) ===\n";
    const auto env = calc.compute_envelope(1500.0);
    std::cout << "Питоме навантаження W/S: " << env.wing_loading_n_m2 << " Н/м² ("
              << env.wing_loading_kg_m2 << " кг/м²)\n";
    std::cout << "Швидкість звалювання 1g (H=0 м):   " << env.v_stall_0_ms << " м/с ("
              << env.v_stall_0_ms * 3.6 << " км/год)\n";
    std::cout << "Швидкість звалювання 1g (H=1500 м): " << env.v_stall_alt_ms << " м/с ("
              << env.v_stall_alt_ms * 3.6 << " км/год)\n";
    std::cout << "Швидкість маневрування V_A:         " << env.v_maneuver_va_ms << " м/с ("
              << env.v_maneuver_va_ms * 3.6 << " км/год)\n\n";

    std::cout << "=== ЗМІНА ШВИДКОСТІ ЗВАЛЮВАННЯ ТА ПЕРЕВАНТАЖЕННЯ У ВІРАЖІ (v = 28 м/с) ===\n";
    std::cout << "  Крен φ  |  Перевантаження n_z  |  v_зв (м/с)  |  Радіус R (м)  |  Омега (град/с)\n";
    std::cout << "----------+----------------------+--------------+----------------+----------------\n";

    const std::vector<double> bank_angles{0.0, 15.0, 30.0, 45.0, 60.0, 70.0, 75.0};
    for (const double bank : bank_angles) {
        if (const auto pt = calc.compute_bank_turn(500.0, bank, 28.0); pt.has_value()) {
            std::cout << "   " << std::setw(2) << static_cast<int>(pt->bank_deg) << "°    |       "
                      << std::setw(4) << pt->load_factor_g << " g        |    "
                      << std::setw(5) << pt->stall_speed_ms << "     |     "
                      << std::setw(6) << pt->turn_radius_m << "     |     "
                      << std::setw(5) << pt->turn_rate_deg_s << "\n";
        }
    }

    std::cout << "\n=== ОЦІНКА ВЕРТИКАЛЬНОГО ПОРИВУ ВІТРУ (H=500 м, v=30 м/с, w=7 м/с) ===\n";
    const auto gust = calc.compute_gust(500.0, 30.0, 7.0);
    std::cout << "Коефіцієнт маси μ_g:         " << gust.mass_ratio_mu_g << "\n";
    std::cout << "Коефіцієнт послаблення K_g:  " << std::setprecision(3) << gust.gust_alleviation_kg << "\n";
    std::cout << "Приріст перевантаження Δn:   +" << std::setprecision(2) << gust.delta_n_g << " g\n";
    std::cout << "Сумарне перевантаження n:    " << gust.total_n_g << " g (допустиме n_max = "
              << uav.n_max_pos << " g)\n";

    return 0;
}
```
:::

## Інженерні пастки та крайові випадки в алгоритмах

1. **Тригонометрична сингулярність віражу:** при наближенні кута крену `φ → 90°` величина `cos φ → 0`, тому теоретичне перевантаження та радіус прямують до нескінченності. Програмний код мусить жорстко обмежувати кут крену (`bank_deg < 85°`), щоб уникнути ділення на нуль і переповнення чисел з рухомою комою.
2. **Розбіжність між приладовою (IAS) та істинною (TAS) швидкостями:** на висоті 10 000 м густина повітря становить лише ~0.41 кг/м³. Істинна швидкість звалювання `v_stall,TAS` зростає у `√(1.225 / 0.41) ≈ 1.73` раза. Якщо бортовий алгоритм використовує для розрахунку кутової швидкості або радіуса віражу покази трубки Піто без поправки на густину, похибка в оцінці просторової траєкторії перевищить 70%.
3. **Асиметрія від'ємного зриву:** аеродинамічний профіль зі значною позитивною кривизною має `|C_L,min|` майже вдвічі менший, ніж `C_L,max`. Звалювання під час створення від'ємного перевантаження настає на істотно вищій швидкості, що вимагає окремого розрахунку лівої нижньої гілки діаграми V-n.
4. **Масштабні ефекти малих чисел Рейнольдса для БПЛА:** для малорозмірних дронів з хордою менше ніж 0.2 м робоче число Рейнольдса опускається нижче `Re < 150 000`. На таких режимах через ранній ламінарний відрив реальний `C_L,max` падає на 20–35%, а критичний кут атаки зміщується вліво. Нехтування низькорейнольдсовою деградацією призводить до заниження розрахункової швидкості звалювання на 15–20%.
5. **Динамічний приріст навантаження в контурах автопілота:** при різкому виході з пікірування або відбитті пориву вітру швидкість наростання кута атаки `dα/dt` може тимчасово збільшити підйомну силу вище статичного `C_L,max` (ефект динамічного звалювання, англ. *dynamic stall*). Алгоритм системи управління польотом повинен мати фільтри за кутовою швидкістю тангажу, щоб запобігти короткочасному перевантаженню силових елементів кріплення консолей.
