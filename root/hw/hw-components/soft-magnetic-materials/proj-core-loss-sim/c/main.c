#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Опис характеристик магнітного матеріалу */
typedef struct {
    const char *name;
    double b_sat_25c;   /* Індукція насичення при 25 °C (Тл) */
    double b_sat_100c;  /* Індукція насичення при 100 °C (Тл) */
    double cm;          /* Коефіцієнт Штейнмеца Cm (Вт/(м³·Гц^α·Тл^β)) */
    double alpha;       /* Показник степеня частоти */
    double beta;        /* Показник степеня індукції */
    double curie_temp;  /* Точка Кюрі (°C) */
} MagneticMaterial;

/* Геометричні параметри магнітопроводу */
typedef struct {
    const char *part_number;
    double a_e;         /* Ефективна площа перерізу магнітного шляху (м²) */
    double l_e;         /* Ефективна довжина магнітної лінії (м) */
    double v_e;         /* Ефективний магнітний об'єм (м³) */
    double a_surface;   /* Площа зовнішньої поверхні (см²) для тепловідводу */
} CoreGeometry;

/* Робочі параметри схеми перетворювача */
typedef struct {
    double v_in;        /* Вхідна постійна напруга (В) */
    double v_out;       /* Вихідна стабілізована напруга (В) */
    double i_out;       /* Середній струм навантаження (А) */
    double f_sw;        /* Частота комутації силових ключів (Гц) */
    double l_val;       /* Номінальна індуктивність дроселя (Гн) */
    int turns;          /* Кількість витків обмотки */
    double r_wire;      /* Активний опір обмотки постійному струму (Ом) */
    double t_ambient;   /* Температура навколишнього середовища (°C) */
} OperatingCondition;

/* Результати комплексного аналізу */
typedef struct {
    double duty_cycle;
    double delta_i;
    double i_peak;
    double i_rms;
    double b_ac;
    double b_dc;
    double b_peak;
    double p_core;
    double p_copper;
    double p_total;
    double delta_temp;
    double final_temp;
    bool is_saturated;
    bool is_overheated;
} SimulationResult;

/* Обчислювальне ядро аналізу магнітного компонента */
SimulationResult evaluate_magnetic_inductor(
    const MagneticMaterial *mat,
    const CoreGeometry *core,
    const OperatingCondition *op
) {
    SimulationResult res;
    
    /* 1. Розрахунок комутаційного режиму */
    res.duty_cycle = op->v_out / op->v_in;
    double t_on = res.duty_cycle / op->f_sw;
    res.delta_i = (op->v_in - op->v_out) * t_on / op->l_val;
    res.i_peak = op->i_out + res.delta_i / 2.0;
    res.i_rms = sqrt(op->i_out * op->i_out + (res.delta_i * res.delta_i) / 12.0);
    
    /* 2. Розрахунок магнітного поля в осерді */
    double delta_b = (op->l_val * res.delta_i) / (op->turns * core->a_e);
    res.b_ac = delta_b / 2.0;
    res.b_dc = (op->l_val * op->i_out) / (op->turns * core->a_e);
    res.b_peak = res.b_dc + res.b_ac;
    
    /* 3. Оцінка втрат в осерді за рівнянням Штейнмеца */
    double p_v = mat->cm * pow(op->f_sw, mat->alpha) * pow(res.b_ac, mat->beta);
    res.p_core = p_v * core->v_e;
    
    /* 4. Оцінка джоулевих втрат в обмотці */
    res.p_copper = res.i_rms * res.i_rms * op->r_wire;
    res.p_total = res.p_core + res.p_copper;
    
    /* 5. Тепловий розрахунок перегріву */
    double r_th = 40.0 / sqrt(core->a_surface); /* Термічний опір °C/Вт */
    res.delta_temp = res.p_total * r_th;
    res.final_temp = op->t_ambient + res.delta_temp;
    
    /* 6. Діагностика граничних станів */
    double b_sat_limit = (res.final_temp >= 100.0) ? mat->b_sat_100c : mat->b_sat_25c;
    res.is_saturated = (res.b_peak >= b_sat_limit);
    res.is_overheated = (res.final_temp >= mat->curie_temp - 30.0 || res.final_temp > 125.0);
    
    return res;
}

int main(void) {
    /* База даних матеріалів */
    MagneticMaterial sendust = {
        .name = "Sendust (Kool Mu 60u, Fe-Si-Al)",
        .b_sat_25c = 1.05,
        .b_sat_100c = 0.95,
        .cm = 32.5,
        .alpha = 1.45,
        .beta = 2.15,
        .curie_temp = 500.0
    };
    
    MagneticMaterial high_flux = {
        .name = "High Flux (60u, Ni-Fe 50/50)",
        .b_sat_25c = 1.50,
        .b_sat_100c = 1.40,
        .cm = 45.0,
        .alpha = 1.40,
        .beta = 2.10,
        .curie_temp = 480.0
    };
    
    MagneticMaterial mnzn_ferrite = {
        .name = "MnZn Ferrite (N87 без зазору)",
        .b_sat_25c = 0.49,
        .b_sat_100c = 0.39,
        .cm = 10.2,
        .alpha = 1.64,
        .beta = 2.68,
        .curie_temp = 210.0
    };
    
    /* Геометрія серійного тороїдального осердя T106 (зовнішній діаметр 27 мм) */
    CoreGeometry core_t106 = {
        .part_number = "Toroid T106",
        .a_e = 65.3e-6,      /* 65.3 мм² */
        .l_e = 65.4e-3,      /* 65.4 мм */
        .v_e = 4.27e-6,      /* 4.27 см³ */
        .a_surface = 35.0    /* 35.0 см² */
    };
    
    /* Параметри силового перетворювача 48 В -> 12 В, 6 А, 100 кГц */
    OperatingCondition op = {
        .v_in = 48.0,
        .v_out = 12.0,
        .i_out = 6.0,
        .f_sw = 100000.0,    /* 100 кГц */
        .l_val = 33.0e-6,    /* 33 мкГн */
        .turns = 32,
        .r_wire = 0.045,     /* 45 мОм */
        .t_ambient = 25.0
    };
    
    printf("=================================================================\n");
    printf("        СИМУЛЯТОР РОБОЧОЇ ТОЧКИ МАГНІТНОГО ОСЕРДЯ ДРОСЕЛЯ        \n");
    printf("=================================================================\n\n");
    
    MagneticMaterial materials[] = { sendust, high_flux, mnzn_ferrite };
    int count = sizeof(materials) / sizeof(materials[0]);
    
    for (int i = 0; i < count; ++i) {
        SimulationResult r = evaluate_magnetic_inductor(&materials[i], &core_t106, &op);
        
        printf("Матеріал осердя: %s\n", materials[i].name);
        printf("-----------------------------------------------------------------\n");
        printf("  Шпаруватість D:        %.3f\n", r.duty_cycle);
        printf("  Пульсація струму ΔI:   %.2f A (Піковий: %.2f A, RMS: %.2f A)\n", 
               r.delta_i, r.i_peak, r.i_rms);
        printf("  Змінна індукція Bac:   %.3f Тл\n", r.b_ac);
        printf("  Постійна індукція Bdc: %.3f Тл\n", r.b_dc);
        printf("  Пікова індукція Bpk:   %.3f Тл\n", r.b_peak);
        printf("  Втрати в осерді Pcore: %.3f Вт\n", r.p_core);
        printf("  Джоулеві втрати Pcu:   %.3f Вт\n", r.p_copper);
        printf("  Сумарні втрати Ptotal: %.3f Вт\n", r.p_total);
        printf("  Перегрів конструкції:  +%.1f °C  (Температура: %.1f °C)\n", 
               r.delta_temp, r.final_temp);
        printf("  Стан насичення:        [%s]\n", 
               r.is_saturated ? "АВАРІЯ: МАТЕРІАЛ НАСИЧЕНО" : "НОРМА: ІНДУКЦІЯ В МЕЖАХ");
        printf("  Стан перегріву:        [%s]\n\n", 
               r.is_overheated ? "АВАРІЯ: ТЕПЛОВИЙ ПЕРЕГРІВ" : "НОРМА: ТЕМПЕРАТУРА СТАБІЛЬНА");
    }
    
    return 0;
}
