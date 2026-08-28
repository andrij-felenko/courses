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
