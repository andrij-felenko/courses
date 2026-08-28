#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Параметри джерела мікроенергії */
typedef struct {
    double power_uW;       /* Середня потужність джерела (мкВт) */
    double mpp_voltage_V;   /* Напруга в точці максимальної потужності (В) */
} HarvesterSource;

/* Параметри накопичувача та навантаження */
typedef struct {
    double cap_uF;         /* Ємність накопичувального конденсатора (мкФ) */
    double v_chg_V;        /* Поріг увімкнення PMIC (В) */
    double v_dis_V;        /* Поріг відсічки UVLO (В) */
    double i_leak_uA;      /* Струм витоку конденсатора та PMIC (мкА) */
    double i_sleep_uA;     /* Струм системи у глибокому сні (мкА) */
    double i_active_mA;    /* Струм активної радіопередачі (мА) */
    double t_active_ms;    /* Тривалість активного вікна передачі (мс) */
} NodeEnergyProfile;

/* Результат моделювання енергобалансу */
typedef struct {
    double usable_energy_uJ; /* Корисна енергія конденсатора (мкДж) */
    double active_energy_uJ; /* Енергія одного імпульсу передачі (мкДж) */
    double recharge_time_s;  /* Необхідний час дозаряджання (с) */
    bool is_sustainable;     /* Чи сходиться баланс потужності */
} SimulationResult;

SimulationResult simulate_energy_cycle(const HarvesterSource *src, 
                                      const NodeEnergyProfile *node) {
    SimulationResult res;
    
    /* 1. Розрахунок запасу корисної енергії конденсатора */
    double v_delta_sq = (node->v_chg_V * node->v_chg_V) - 
                        (node->v_dis_V * node->v_dis_V);
    res.usable_energy_uJ = 0.5 * node->cap_uF * v_delta_sq;
    
    /* 2. Енергія одного сеансу вимірювання та радіопередачі */
    double v_avg = 0.5 * (node->v_chg_V + node->v_dis_V);
    res.active_energy_uJ = v_avg * node->i_active_mA * node->t_active_ms;
    
    /* Перевірка достатності ємності для покриття імпульсу */
    if (res.usable_energy_uJ < res.active_energy_uJ) {
        res.is_sustainable = false;
        res.recharge_time_s = -1.0;
        return res;
    }
    
    /* 3. Середній корисний струм заряду конденсатора у фазі сну */
    double pmic_efficiency = 0.85; /* ККД бустера PMIC */
    double i_harv_avg_uA = (src->power_uW * pmic_efficiency) / v_avg;
    double i_net_charge_uA = i_harv_avg_uA - node->i_sleep_uA - node->i_leak_uA;
    
    if (i_net_charge_uA <= 0.0) {
        res.is_sustainable = false;
        res.recharge_time_s = -1.0;
        return res;
    }
    
    /* 4. Час поповнення витраченого електричного заряду */
    double delta_q_uC = node->cap_uF * (node->v_chg_V - node->v_dis_V);
    res.recharge_time_s = delta_q_uC / i_net_charge_uA;
    res.is_sustainable = true;
    
    return res;
}

int main(void) {
    /* Джерело 1: Кімнатний a-Si фотоелемент 4x4 см під LED 300 люкс */
    HarvesterSource solar_indoor = { .power_uW = 280.0, .mpp_voltage_V = 2.4 };
    
    /* Джерело 2: Wi-Fi RF-ректена на відстані 2 м (-22 дБм) */
    HarvesterSource rf_ambient = { .power_uW = 3.5, .mpp_voltage_V = 0.45 };
    
    /* Профіль вузла: MCU + BLE 5.0 передавач */
    NodeEnergyProfile node = {
        .cap_uF = 470.0,
        .v_chg_V = 3.3,
        .v_dis_V = 2.4,
        .i_leak_uA = 0.8,
        .i_sleep_uA = 0.9,
        .i_active_mA = 16.0,
        .t_active_ms = 10.0
    };
    
    SimulationResult sim_solar = simulate_energy_cycle(&solar_indoor, &node);
    SimulationResult sim_rf = simulate_energy_cycle(&rf_ambient, &node);
    
    printf("=== ЕНЕРГЕТИЧНИЙ БАЛАНС БЕЗБАТАРЕЙНОГО ВУЗЛА ===\n");
    printf("Запас енергії конденсатора 470 мкФ: %.1f мкДж\n", sim_solar.usable_energy_uJ);
    printf("Витрати одного пакета BLE:        %.1f мкДж\n\n", sim_solar.active_energy_uJ);
    
    if (sim_solar.is_sustainable) {
        printf("Кімнатний фотоелемент a-Si (280 мкВт):\n");
        printf("  -> Період передачі: кожні %.2f с (%.1f пакетів/хв)\n", 
               sim_solar.recharge_time_s, 60.0 / sim_solar.recharge_time_s);
    }
    
    if (sim_rf.is_sustainable) {
        printf("Розсіяний Wi-Fi ефір (3.5 мкВт):\n");
        printf("  -> Період передачі: кожні %.1f с (%.2f пакетів/хв)\n", 
               sim_rf.recharge_time_s, 60.0 / sim_rf.recharge_time_s);
    } else {
        printf("Розсіяний Wi-Fi ефір: недостатньо енергії для компенсації витоків!\n");
    }
    
    return 0;
}
