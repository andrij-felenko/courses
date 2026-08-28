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
