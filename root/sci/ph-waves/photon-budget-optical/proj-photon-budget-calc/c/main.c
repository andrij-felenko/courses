#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define CONST_H 6.62607015e-34  /* Стала Планка, Дж·с */
#define CONST_C 299792458.0     /* Швидкість світла, м/с */
#define CONST_E 1.602176634e-19 /* Заряд електрона, Кл */
#define CONST_KB 1.380649e-23   /* Стала Больцмана, Дж/К */

/* Оптичний елемент каскаду */
typedef struct {
    const char* name;
    double transmittance; /* Коефіцієнт пропускання (0.0 .. 1.0) */
} OpticalElement;

/* Вхідні параметри оптичної системи */
typedef struct {
    double wavelength_m;   /* Довжина хвилі, м */
    double power_tx_w;     /* Потужність передавача, Вт */
    double distance_m;     /* Відстань каналу, м */
    double atten_db_per_km;/* Згасання в середовищі, дБ/км */
    double divergence_rad; /* Кут розбіжності променя, рад */
    double beam_waist_m;   /* Початковий радіус пучка, м */
    double rx_aperture_m;  /* Діаметр приймальної лінзи, м */
    
    double quantum_eff;    /* Квантова ефективність детектора (0.0 .. 1.0) */
    double dark_current_a; /* Темновий струм детектора, А */
    double load_resistor_ohm; /* Опір навантаження приймача, Ом */
    double temperature_k;  /* Абсолютна температура, К */
    double bandwidth_hz;   /* Смуга частот приймача, Гц */

    const OpticalElement* elements;
    size_t element_count;
} PhotonBudgetConfig;

/* Результати розрахунку фотонного бюджету */
typedef struct {
    double photon_energy_j;
    double tx_photon_rate;
    double rx_power_w;
    double rx_power_dbm;
    double rx_photon_rate;
    double photoelectrons_per_bit;
    
    double sigma_shot_e;
    double sigma_dark_e;
    double sigma_thermal_e;
    double sigma_total_e;
    
    double snr_linear;
    double snr_db;
    double link_margin_db;
} PhotonBudgetResult;

PhotonBudgetResult calculate_photon_budget(const PhotonBudgetConfig* cfg, double required_snr_db) {
    PhotonBudgetResult res = {0};
    
    /* 1. Енергія фотона */
    res.photon_energy_j = (CONST_H * CONST_C) / cfg->wavelength_m;
    res.tx_photon_rate = cfg->power_tx_w / res.photon_energy_j;
    
    /* 2. Проходження крізь каскад оптичних елементів */
    double cascade_transmittance = 1.0;
    for (size_t i = 0; i < cfg->element_count; ++i) {
        cascade_transmittance *= cfg->elements[i].transmittance;
    }
    
    /* 3. Згасання у середовищі каналу */
    double dist_km = cfg->distance_m / 1000.0;
    double channel_loss_db = cfg->atten_db_per_km * dist_km;
    double channel_transmittance = pow(10.0, -channel_loss_db / 10.0);
    
    /* 4. Геометричні втрати через розбіжність променя */
    double spot_radius = cfg->beam_waist_m + cfg->distance_m * tan(cfg->divergence_rad);
    double spot_area = M_PI * spot_radius * spot_radius;
    double rx_radius = cfg->rx_aperture_m / 2.0;
    double rx_area = M_PI * rx_radius * rx_radius;
    double geom_efficiency = (rx_area < spot_area) ? (rx_area / spot_area) : 1.0;
    
    /* 5. Підсумкова приймана потужність та потік фотонів */
    res.rx_power_w = cfg->power_tx_w * cascade_transmittance * channel_transmittance * geom_efficiency;
    res.rx_power_dbm = 10.0 * log10(res.rx_power_w / 1e-3);
    res.rx_photon_rate = res.rx_power_w / res.photon_energy_j;
    
    /* 6. Кількість фотоелектронів за бітовий інтервал Δt = 1 / (2*B) */
    double dt = 1.0 / (2.0 * cfg->bandwidth_hz);
    double rx_photons_per_bit = res.rx_photon_rate * dt;
    res.photoelectrons_per_bit = cfg->quantum_eff * rx_photons_per_bit;
    
    /* 7. Шумовий розрахунок (у числах електронів за біт) */
    res.sigma_shot_e = sqrt(res.photoelectrons_per_bit);
    
    double dark_electrons = (cfg->dark_current_a * dt) / CONST_E;
    res.sigma_dark_e = sqrt(dark_electrons);
    
    double thermal_noise_current_sq = (4.0 * CONST_KB * cfg->temperature_k * cfg->bandwidth_hz) / cfg->load_resistor_ohm;
    double thermal_current_rms = sqrt(thermal_noise_current_sq);
    res.sigma_thermal_e = (thermal_current_rms * dt) / CONST_E;
    
    res.sigma_total_e = sqrt(res.sigma_shot_e * res.sigma_shot_e + 
                             res.sigma_dark_e * res.sigma_dark_e + 
                             res.sigma_thermal_e * res.sigma_thermal_e);
                             
    /* 8. Сигнал/Шум та запас лінії */
    res.snr_linear = res.photoelectrons_per_bit / res.sigma_total_e;
    res.snr_db = 20.0 * log10(res.snr_linear);
    res.link_margin_db = res.snr_db - required_snr_db;
    
    return res;
}

int main(void) {
    OpticalElement cascade[] = {
        {"Лінза коліматора AR", 0.98},
        {"Bandpass фільтр 1550нм", 0.85},
        {"Дихроїчне дзеркало", 0.95}
    };

    PhotonBudgetConfig cfg = {
        .wavelength_m = 1550e-9,
        .power_tx_w = 0.050,         /* 50 мВт */
        .distance_m = 2000.0,        /* 2 км */
        .atten_db_per_km = 2.5,      /* 2.5 дБ/км */
        .divergence_rad = 0.0015,    /* 1.5 мрад */
        .beam_waist_m = 0.005,       /* 5 мм */
        .rx_aperture_m = 0.100,      /* 100 мм */
        .quantum_eff = 0.85,
        .dark_current_a = 2e-9,      /* 2 нА */
        .load_resistor_ohm = 50.0,   /* 50 Ом */
        .temperature_k = 300.0,      /* 300 К */
        .bandwidth_hz = 125e6,       /* 125 МГц */
        .elements = cascade,
        .element_count = sizeof(cascade) / sizeof(cascade[0])
    };

    PhotonBudgetResult res = calculate_photon_budget(&cfg, 15.6);

    printf("=== ФОТОННИЙ БЮДЖЕТ ОПТИЧНОЇ СИСТЕМИ (C) ===\n");
    printf("Енергія фотона:             %.3e Дж\n", res.photon_energy_j);
    printf("Приймана потужність:        %.3f мкВт (%.2f дБм)\n", res.rx_power_w * 1e6, res.rx_power_dbm);
    printf("Сигнал на біт:              %.0f e-\n", res.photoelectrons_per_bit);
    printf("Дробовий шум:               %.1f e-\n", res.sigma_shot_e);
    printf("Тепловий шум:               %.1f e-\n", res.sigma_thermal_e);
    printf("Сумарний шум:               %.1f e-\n", res.sigma_total_e);
    printf("Відношення Сигнал/Шум (SNR): %.2f дБ (лінійне: %.1f)\n", res.snr_db, res.snr_linear);
    printf("Запас лінії (Link Margin):  %+ .2f дБ\n", res.link_margin_db);

    return 0;
}
