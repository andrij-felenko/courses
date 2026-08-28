#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define MAX_SOURCES 64
#define M_PI_VAL 3.14159265358979323846

/* Коди помилок та статуси розрахунку */
typedef enum {
    SOLVER_OK = 0,
    SOLVER_ERR_INVALID_PARAM = -1,
    SOLVER_ERR_NO_MEMORY = -2,
    SOLVER_WARN_NONLINEAR_SATURATION = 1
} SolverStatus;

/* Структура точкового джерела поля (електричного або гравітаційного) */
typedef struct {
    double x, y;        /* Позиція джерела у метрах */
    double charge;      /* Величина заряду / маси / інтенсивності */
} FieldSourceC;

/* Структура результату розрахунку поля у точці */
typedef struct {
    double Ex, Ey;      /* Компоненти результуючого вектора напруженості */
    double potential;   /* Скалярний потенціал */
} FieldResultC;

/* Структура дискретного рушія імпульсного відгуку (Функції Гріна) */
typedef struct {
    double *h;          /* Масив імпульсної характеристики h[n] */
    size_t h_len;       /* Довжина імпульсної характеристики */
    double max_linear_amp; /* Поріг лінійності */
} GreenEngineC;

/* Ініціалізація рушія функцій Гріна */
SolverStatus green_engine_init(GreenEngineC *eng, const double *impulse_response, size_t len, double max_amp) {
    if (!eng || !impulse_response || len == 0) return SOLVER_ERR_INVALID_PARAM;
    
    eng->h = (double*)malloc(len * sizeof(double));
    if (!eng->h) return SOLVER_ERR_NO_MEMORY;
    
    for (size_t i = 0; i < len; ++i) {
        eng->h[i] = impulse_response[i];
    }
    eng->h_len = len;
    eng->max_linear_amp = max_amp;
    return SOLVER_OK;
}

/* Звільнення ресурсів */
void green_engine_free(GreenEngineC *eng) {
    if (eng && eng->h) {
        free(eng->h);
        eng->h = NULL;
        eng->h_len = 0;
    }
}

/* Обчислення суперпозиції полів від N джерел у точці (px, py) */
SolverStatus calculate_field_superposition(const FieldSourceC *sources, size_t num_sources,
                                            double px, double py,
                                            FieldResultC *out_result) {
    if (!sources || !out_result || num_sources == 0) return SOLVER_ERR_INVALID_PARAM;

    out_result->Ex = 0.0;
    out_result->Ey = 0.0;
    out_result->potential = 0.0;

    for (size_t i = 0; i < num_sources; ++i) {
        double dx = px - sources[i].x;
        double dy = py - sources[i].y;
        double r2 = dx * dx + dy * dy;
        double r = sqrt(r2);

        /* Запобігання діленню на нуль у точці джерела (регуляризація) */
        if (r < 1e-9) r = 1e-9;

        /* Закон Кулона / Ньютона: E = q / r^2, V = q / r */
        double E_mag = sources[i].charge / (r2);
        out_result->Ex += E_mag * (dx / r);
        out_result->Ey += E_mag * (dy / r);
        out_result->potential += sources[i].charge / r;
    }

    return SOLVER_OK;
}

/* Обчислення дискретної згортки (неперервна суперпозиція в часі) */
SolverStatus process_convolution_superposition(const GreenEngineC *eng,
                                               const double *input, size_t in_len,
                                               double *output, size_t out_len) {
    if (!eng || !input || !output || in_len == 0 || out_len < in_len + eng->h_len - 1) {
        return SOLVER_ERR_INVALID_PARAM;
    }

    /* Очищення вихідного масиву */
    for (size_t n = 0; n < out_len; ++n) {
        output[n] = 0.0;
    }

    bool saturated = false;

    /* Дискретна суперпозиція: y[n] = sum_k x[k] * h[n - k] */
    for (size_t n = 0; n < in_len + eng->h_len - 1; ++n) {
        double sum = 0.0;
        for (size_t k = 0; k < in_len; ++k) {
            if (n >= k && (n - k) < eng->h_len) {
                sum += input[k] * eng->h[n - k];
            }
        }
        output[n] = sum;
        if (fabs(sum) > eng->max_linear_amp) {
            saturated = true;
        }
    }

    return saturated ? SOLVER_WARN_NONLINEAR_SATURATION : SOLVER_OK;
}

int main(void) {
    printf("=== Симулятор суперпозиції (C Implementation) ===\n\n");

    /* 1. Розрахунок суперпозиції електричних полів 3 джерел */
    FieldSourceC sources[3] = {
        { .x = -2.0, .y = 0.0, .charge = 5.0 },
        { .x =  2.0, .y = 0.0, .charge = -3.0 },
        { .x =  0.0, .y = 3.0, .charge = 2.0 }
    };

    FieldResultC field_res;
    if (calculate_field_superposition(sources, 3, 0.0, 0.0, &field_res) == SOLVER_OK) {
        printf("[Електростатика C] Поле у точці (0,0):\n");
        printf("  Ex        = %8.4f у.о.\n", field_res.Ex);
        printf("  Ey        = %8.4f у.о.\n", field_res.Ey);
        printf("  Потенціал = %8.4f у.о.\n\n", field_res.potential);
    }

    /* 2. Дискретна суперпозиція (згортка з функцією Гріна) */
    double h[5] = { 1.0, 0.5, 0.25, 0.125, 0.0625 }; /* Загасаючий імпульсний відгук */
    GreenEngineC engine;
    if (green_engine_init(&engine, h, 5, 10.0) != SOLVER_OK) {
        fprintf(stderr, "Помилка ініціалізації рушія!\n");
        return 1;
    }

    double input[8] = { 1.0, 2.0, 1.5, 0.0, -1.0, 0.5, 0.0, 0.0 };
    size_t out_len = 8 + 5 - 1;
    double *output = (double*)malloc(out_len * sizeof(double));

    SolverStatus status = process_convolution_superposition(&engine, input, 8, output, out_len);
    
    printf("[DSP / Згортка C] Суперпозиція імпульсних відгуків y[n]:\n");
    for (size_t i = 0; i < out_len; ++i) {
        printf("  y[%2zu] = %7.4f\n", i, output[i]);
    }

    if (status == SOLVER_WARN_NONLINEAR_SATURATION) {
        printf("УВАГА: Сигнал перевищив поріг лінійності!\n");
    } else {
        printf("Статус: Сигнал у межах лінійного режиму.\n");
    }

    free(output);
    green_engine_free(&engine);
    return 0;
}
