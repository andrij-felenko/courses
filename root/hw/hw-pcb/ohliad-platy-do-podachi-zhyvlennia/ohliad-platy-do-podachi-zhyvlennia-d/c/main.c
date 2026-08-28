#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_NAME 32
#define MAX_RAILS 8

typedef enum {
    RAIL_HIGH_VOLTAGE = 0,
    RAIL_DIGITAL_IO,
    RAIL_MEMORY_VDDQ,
    RAIL_CORE_LOGIC,
    RAIL_ANALOG_VDDA
} RailCategory;

typedef struct {
    char name[MAX_NAME];
    double v_nom;       // Номінальна напруга, В
    double i_max;       // Максимальний струм, А
    double c_uf;        // Ємність фільтра, мкФ
    RailCategory cat;
    double r_min_limit; // Мінімальний безпечний опір спокою, Ом
} RailDescriptor;

typedef struct {
    double r_fwd;       // Прямий вимір (плюс на рейку), Ом
    double r_rev;       // Зворотний вимір (плюс на GND), Ом
    bool is_hard_short;
    bool is_within_spec;
} RailMeasurement;

void init_rail(RailDescriptor *rail, const char *name, double v, double i, double c, RailCategory cat) {
    strncpy(rail->name, name, MAX_NAME - 1);
    rail->name[MAX_NAME - 1] = '\0';
    rail->v_nom = v;
    rail->i_max = i;
    rail->c_uf = c;
    rail->cat = cat;

    double k_leak = 0.001;
    switch (cat) {
        case RAIL_HIGH_VOLTAGE: k_leak = 0.0001; break;
        case RAIL_DIGITAL_IO:   k_leak = 0.002;  break;
        case RAIL_MEMORY_VDDQ:  k_leak = 0.02;   break;
        case RAIL_CORE_LOGIC:   k_leak = 0.10;   break;
        case RAIL_ANALOG_VDDA:  k_leak = 0.001;  break;
    }
    rail->r_min_limit = v / (k_leak * i);
    if (cat == RAIL_HIGH_VOLTAGE && rail->r_min_limit < 10000.0) rail->r_min_limit = 10000.0;
    if (cat == RAIL_CORE_LOGIC && rail->r_min_limit < 0.15) rail->r_min_limit = 0.15;
}

void verify_rail(const RailDescriptor *desc, double r_fwd, double r_rev, RailMeasurement *meas) {
    meas->r_fwd = r_fwd;
    meas->r_rev = r_rev;
    meas->is_hard_short = (r_fwd < 0.05 || r_rev < 0.05);
    meas->is_within_spec = (!meas->is_hard_short && r_fwd >= desc->r_min_limit);
}

int main(void) {
    RailDescriptor rails[MAX_RAILS];
    RailMeasurement results[MAX_RAILS];

    init_rail(&rails[0], "V_IN_12V",  12.0, 3.0,  220.0, RAIL_HIGH_VOLTAGE);
    init_rail(&rails[1], "V_IO_3V3",   3.3, 2.0,  150.0, RAIL_DIGITAL_IO);
    init_rail(&rails[2], "VDDQ_1V2",   1.2, 5.0,  680.0, RAIL_MEMORY_VDDQ);
    init_rail(&rails[3], "VCORE_0V9",  0.9, 20.0, 1500.0, RAIL_CORE_LOGIC);

    verify_rail(&rails[0], 48000.0, 52000.0, &results[0]);
    verify_rail(&rails[1],  2100.0,  2300.0, &results[1]);
    verify_rail(&rails[2],    34.0,    38.0, &results[2]);
    verify_rail(&rails[3],     0.78,    0.82, &results[3]); // 0.78 Ом - норма для ядра 20А!

    printf("ПЕРЕВІРКА РЕЙОК ЖИВЛЕННЯ ПЕРЕД ВВІМКНЕННЯМ:\n");
    for (int i = 0; i < 4; i++) {
        printf("Рейка %-10s: V_nom=%4.1fВ, Поріг=%7.2f Ом, Вимір=%7.2f Ом -> %s\n",
               rails[i].name, rails[i].v_nom, rails[i].r_min_limit, results[i].r_fwd,
               results[i].is_within_spec ? "НОРМА (PASS)" : "АВАРІЯ / КЗ (FAIL)");
    }
    return 0;
}
