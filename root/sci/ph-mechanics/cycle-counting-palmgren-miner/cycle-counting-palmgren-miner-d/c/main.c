#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

/* Структура для збереження знайденого циклу */
typedef struct {
    double range;     /* розмах напруження: Delta sigma = |max - min| */
    double mean;      /* середнє напруження: sigma_m = (max + min) / 2 */
    double count;     /* кількість циклів (1.0 - повний цикл, 0.5 - напівцикл) */
} RainflowCycle;

/* Динамічний масив циклів */
typedef struct {
    RainflowCycle *data;
    size_t size;
    size_t capacity;
} CycleBuffer;

/* Параметри кривої втоми Басквіна та матеріалу */
typedef struct {
    double sigma_u;   /* межа міцності (тимчасовий опір), МПа */
    double sigma_ref; /* опорне напруження кривої Веллера, МПа */
    double n_ref;     /* опорна кількість циклів (наприклад, 1e6 або 2e6) */
    double m;         /* показник нахилу кривої Басквіна (m = -1/b) */
} FatigueProperties;

/* Ініціалізація буфера циклів */
static void cycle_buffer_init(CycleBuffer *cb) {
    cb->size = 0;
    cb->capacity = 64;
    cb->data = (RainflowCycle *)malloc(cb->capacity * sizeof(RainflowCycle));
}

/* Додавання циклу до буфера */
static void cycle_buffer_append(CycleBuffer *cb, double range, double mean, double count) {
    if (cb->size >= cb->capacity) {
        cb->capacity *= 2;
        cb->data = (RainflowCycle *)realloc(cb->data, cb->capacity * sizeof(RainflowCycle));
    }
    cb->data[cb->size].range = range;
    cb->data[cb->size].mean = mean;
    cb->data[cb->size].count = count;
    cb->size++;
}

/* Звільнення пам'яті буфера */
static void cycle_buffer_free(CycleBuffer *cb) {
    free(cb->data);
    cb->data = NULL;
    cb->size = 0;
    cb->capacity = 0;
}

/*
 * Крок 1: Фільтрація точок реверсу (екстремумів сигналу).
 * Відкидає всі проміжні відліки на монотонних ділянках.
 */
static size_t extract_reversals(const double *signal, size_t n, double **reversals_out) {
    if (n < 2) {
        *reversals_out = NULL;
        return 0;
    }
    
    double *rev = (double *)malloc(n * sizeof(double));
    size_t rev_count = 0;
    
    rev[rev_count++] = signal[0];
    
    for (size_t i = 1; i < n - 1; ++i) {
        double d1 = signal[i] - rev[rev_count - 1];
        double d2 = signal[i + 1] - signal[i];
        
        /* Пропуск плато (якщо напруження не змінилося) */
        if (fabs(d1) < 1e-9) {
            continue;
        }
        
        /* Якщо знаки нахилів протилежні - маємо точку реверсу */
        if ((d1 > 0.0 && d2 < 0.0) || (d1 < 0.0 && d2 > 0.0)) {
            rev[rev_count++] = signal[i];
        }
    }
    
    rev[rev_count++] = signal[n - 1];
    *reversals_out = rev;
    return rev_count;
}

/*
 * Крок 2: Чотириточковий алгоритм Rainflow за стандартом ASTM E1049.
 * Повертає буфер із повними циклами та обробленим залишком напівциклів.
 */
static CycleBuffer rainflow_astm_e1049(const double *reversals, size_t n) {
    CycleBuffer result;
    cycle_buffer_init(&result);
    
    if (n < 3) {
        return result;
    }
    
    /* Стек для зберігання точок реверсу */
    double *stack = (double *)malloc((n + 1) * sizeof(double));
    size_t top = 0;
    
    for (size_t i = 0; i < n; ++i) {
        stack[top++] = reversals[i];
        
        /* Поки в стеку є щонайменше 4 точки, перевіряємо умову замикання циклу */
        while (top >= 4) {
            double s_a = stack[top - 4];
            double s_b = stack[top - 3];
            double s_c = stack[top - 2];
            double s_d = stack[top - 1];
            
            double x1 = fabs(s_b - s_a);
            double y  = fabs(s_c - s_b);
            double x2 = fabs(s_d - s_c);
            
            /* Умова замикання циклу між точками B та C */
            if (y <= x1 && y <= x2) {
                double range = y;
                double mean  = 0.5 * (s_b + s_c);
                cycle_buffer_append(&result, range, mean, 1.0);
                
                /* Видаляємо точки B та C, зміщуючи точку D на позицію B */
                stack[top - 3] = stack[top - 1];
                top -= 2;
            } else {
                break;
            }
        }
    }
    
    /*
     * Крок 3: Обробка залишку (Residue) за стандартом ASTM E1049.
     * Усі незведені пари точок у стеку записуються як напівцикли (count = 0.5).
     */
    for (size_t i = 0; i + 1 < top; ++i) {
        double range = fabs(stack[i + 1] - stack[i]);
        double mean  = 0.5 * (stack[i] + stack[i + 1]);
        cycle_buffer_append(&result, range, mean, 0.5);
    }
    
    free(stack);
    return result;
}

/*
 * Розрахунок еквівалентної амплітуди за моделлю Гудмана (R = -1)
 */
static double goodman_equivalent_amplitude(double amplitude, double mean, double sigma_u) {
    if (mean <= 0.0) {
        /* Стискальне середнє напруження: розрахунок у запас міцності */
        return amplitude;
    }
    if (mean >= sigma_u) {
        /* Середнє напруження перевищує межу міцності */
        return 1e9;
    }
    return amplitude / (1.0 - mean / sigma_u);
}

/*
 * Розрахунок граничного числа циклів до руйнування за Басквіном
 */
static double basquin_life(double equivalent_amplitude, const FatigueProperties *props) {
    if (equivalent_amplitude <= 0.0) {
        return 1e30;
    }
    return props->n_ref * pow(props->sigma_ref / equivalent_amplitude, props->m);
}

/*
 * Розрахунок сумарного накопиченого пошкодження за Пальмгреном - Майнером
 */
static double calculate_palmgren_miner_damage(const CycleBuffer *cycles, const FatigueProperties *props) {
    double total_damage = 0.0;
    
    for (size_t i = 0; i < cycles->size; ++i) {
        double amplitude = cycles->data[i].range * 0.5;
        double mean = cycles->data[i].mean;
        double count = cycles->data[i].count;
        
        double eq_amp = goodman_equivalent_amplitude(amplitude, mean, props->sigma_u);
        double n_fail = basquin_life(eq_amp, props);
        
        if (n_fail > 0.0) {
            total_damage += count / n_fail;
        }
    }
    
    return total_damage;
}

int main(void) {
    /* Синтетичний сигнал напружень із датчика (МПа) */
    const double stress_signal[] = {
        0.0, 120.0, -40.0, 180.0, 40.0, 140.0, 
        20.0, 260.0, -80.0, 200.0, 60.0, 160.0, 0.0
    };
    const size_t signal_len = sizeof(stress_signal) / sizeof(stress_signal[0]);
    
    /* Параметри матеріалу (авіаційний дюралюміній D16T / 2024-T3) */
    FatigueProperties props = {
        .sigma_u   = 470.0,   /* межа міцності 470 МПа */
        .sigma_ref = 180.0,   /* опорна амплітуда 180 МПа */
        .n_ref     = 1.0e6,   /* база 1 000 000 циклів */
        .m         = 6.5      /* показник нахилу Басквіна */
    };
    
    /* 1. Фільтрація точок реверсу */
    double *reversals = NULL;
    size_t num_revs = extract_reversals(stress_signal, signal_len, &reversals);
    
    /* 2. Підрахунок циклів Rainflow */
    CycleBuffer cycles = rainflow_astm_e1049(reversals, num_revs);
    
    /* 3. Розрахунок пошкодження за Майнером */
    double damage_per_block = calculate_palmgren_miner_damage(&cycles, &props);
    double blocks_to_failure = (damage_per_block > 0.0) ? (1.0 / damage_per_block) : 1e30;
    
    printf("=== Результати Rainflow та розрахунку ресурсу (C99) ===\n");
    printf("Відліків сигналу: %zu | Точок реверсу: %zu\n", signal_len, num_revs);
    printf("Виявлено циклів та напівциклів: %zu\n", cycles.size);
    printf("Пошкодження за один блок D: %.6e\n", damage_per_block);
    printf("Прогнозований ресурс: %.1f блоків навантаження\n", blocks_to_failure);
    
    free(reversals);
    cycle_buffer_free(&cycles);
    return 0;
}
