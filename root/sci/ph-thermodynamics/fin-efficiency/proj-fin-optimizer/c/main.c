#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Структура геометричних та теплових параметрів радіатора */
typedef struct {
    double w_base;      /* Ширина основи радіатора, м */
    double l_base;      /* Довжина основи вздовж потоку, м */
    double h_fin;       /* Висота ребер, м */
    double k_metal;     /* Теплопровідність металу, Вт/(м·К) */
    double h_conv;      /* Коефіцієнт тепловіддачі, Вт/(м²·К) */
    double t_amb;       /* Температура повітря, °C */
    double p_heat;      /* Розсіювана потужність, Вт */
    double s_min;       /* Мінімальний аеродинамічний зазор між ребрами, м */
} heatsink_config_t;

/* Структура результату розрахунку */
typedef struct {
    int num_fins;       /* Оптимальна кількість ребер */
    double fin_thick;   /* Оптимальна товщина ребра, м */
    double gap;         /* Зазор між ребрами, м */
    double m_param;     /* Параметр згасання m, 1/м */
    double eta_f;       /* Ефективність окремого ребра η_f (0..1) */
    double eta_o;       /* Загальна ефективність радіатора η_o (0..1) */
    double r_th;        /* Тепловий опір радіатора R_th, °C/Вт */
    double t_base;      /* Температура основи T_base, °C */
    double total_area;  /* Сумарна площа поверхні, м² */
} heatsink_result_t;

/* Обчислення теплових параметрів для конкретної конфігурації (N, t) */
bool calculate_heatsink(const heatsink_config_t *cfg, int n_fins, double t_fin, heatsink_result_t *res) {
    if (n_fins < 2 || t_fin <= 0.0) return false;
    
    /* Розрахунок зазору між ребрами */
    double total_fin_thick = n_fins * t_fin;
    if (total_fin_thick >= cfg->w_base) return false;
    
    double gap = (cfg->w_base - total_fin_thick) / (n_fins - 1);
    if (gap < cfg->s_min) return false; /* Обмеження на аеродинамічний зазор */
    
    /* Площа перерізу та периметр одного ребра */
    double a_c = cfg->l_base * t_fin;
    double p_perim = 2.0 * (cfg->l_base + t_fin);
    
    /* Скоригована висота ребра з урахуванням торця */
    double h_c = cfg->h_fin + (t_fin / 2.0);
    
    /* Площі поверхонь */
    double a_f_single = 2.0 * cfg->l_base * h_c;
    double a_f_total = n_fins * a_f_single;
    double a_u = (n_fins - 1) * gap * cfg->l_base;
    double a_total = a_u + a_f_total;
    
    /* Розрахунок параметра m та ефективностей */
    double m_param = sqrt((cfg->h_conv * p_perim) / (cfg->k_metal * a_c));
    double m_hc = m_param * h_c;
    double eta_f = tanh(m_hc) / m_hc;
    
    double eta_o = 1.0 - (a_f_total / a_total) * (1.0 - eta_f);
    double r_th = 1.0 / (eta_o * cfg->h_conv * a_total);
    double t_base = cfg->t_amb + cfg->p_heat * r_th;
    
    /* Запис результатів */
    res->num_fins = n_fins;
    res->fin_thick = t_fin;
    res->gap = gap;
    res->m_param = m_param;
    res->eta_f = eta_f;
    res->eta_o = eta_o;
    res->r_th = r_th;
    res->t_base = t_base;
    res->total_area = a_total;
    
    return true;
}

/* Пошук оптимальної геометрії радіатора двовимірним перебором */
bool optimize_heatsink(const heatsink_config_t *cfg, heatsink_result_t *best_res) {
    double min_r_th = 1e9;
    bool found = false;
    
    /* Перебір товщини ребра від 0.5 мм до 4.0 мм із кроком 0.1 мм */
    for (double t = 0.0005; t <= 0.0040; t += 0.0001) {
        /* Перебір кількості ребер від 3 до 60 */
        for (int n = 3; n <= 60; n++) {
            heatsink_result_t cur;
            if (calculate_heatsink(cfg, n, t, &cur)) {
                if (cur.r_th < min_r_th) {
                    min_r_th = cur.r_th;
                    *best_res = cur;
                    found = true;
                }
            }
        }
    }
    
    return found;
}

int main(void) {
    /* Конфігурація охолодження алюмінієвого радіатора процесора */
    heatsink_config_t cfg = {
        .w_base = 0.080,   /* Ширина основи 80 мм */
        .l_base = 0.060,   /* Довжина основи 60 мм */
        .h_fin = 0.035,    /* Висота ребер 35 мм */
        .k_metal = 200.0,  /* Алюміній 6063: k = 200 Вт/(м·К) */
        .h_conv = 45.0,    /* Вимушена конвекція кулера: h = 45 Вт/(м²·К) */
        .t_amb = 25.0,     /* Повітря 25 °C */
        .p_heat = 65.0,    /* Потужність процесора 65 Вт */
        .s_min = 0.0015    /* Мінімальний зазор 1.5 мм */
    };
    
    heatsink_result_t opt;
    printf("=== ОПТИМІЗАЦІЯ ГЕОМЕТРІЇ АЛЮМІНІЄВОГО РАДІАТОРА (C99) ===\n\n");
    
    if (optimize_heatsink(&cfg, &opt)) {
        printf("Знайдено оптимальну геометрію радіатора:\n");
        printf("  • Кількість ребер N    : %d шт.\n", opt.num_fins);
        printf("  • Товщина ребра t     : %.2f мм\n", opt.fin_thick * 1000.0);
        printf("  • Зазор між ребрами S  : %.2f мм\n", opt.gap * 1000.0);
        printf("  • Повна площа поверхні  : %.4f м²\n", opt.total_area);
        printf("  • Параметр згасання m  : %.2f 1/м\n", opt.m_param);
        printf("  • Ефективність ребра η_f: %.2f%%\n", opt.eta_f * 100.0);
        printf("  • Ефективність масиву η_o: %.2f%%\n", opt.eta_o * 100.0);
        printf("  • Тепловий опір R_th   : %.3f °C/Вт\n", opt.r_th);
        printf("  • Температура основи T : %.1f °C\n", opt.t_base);
    } else {
        printf("Помилка: Не вдалося знайти допустиму геометрію за вказаних обмежень.\n");
    }
    
    return 0;
}
