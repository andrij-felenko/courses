#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define NIS_WINDOW_SIZE 32

/* Результат перевірки інновації */
typedef enum {
    GATE_ACCEPTED = 0,     /* Вимір валідний, стандартне оновлення */
    GATE_SOFT_SCALED,      /* Вимір у зоні сумніву, шум R масштабовано */
    GATE_REJECTED_OUTLIER, /* Вимір відкинуто як грубий викид */
    GATE_DIVERGENCE_ALARM  /* Критична розбіжність фільтра (потрібен ресет) */
} GatingStatus;

/* Структура конфігурації та стану брами інновацій для 2D вимірів */
typedef struct {
    float gamma_1;               /* Нижній поріг довіри (chi2 95%, зазвичай 5.99) */
    float gamma_2;               /* Верхній поріг відсікання (chi2 99.7%, зазвичай 11.83) */
    uint8_t consecutive_rejects; /* Лічильник послідовних викидів */
    uint8_t max_allowed_rejects; /* Максимум викидів до спрацювання аварії (наприклад, 10) */
    
    /* Кільцевий буфер для моніторингу консистентності NIS */
    float nis_history[NIS_WINDOW_SIZE];
    uint8_t history_idx;
    uint8_t history_count;
    float nis_window_sum;
} InnovationGate2D;

/* Ініціалізація брами */
void innovation_gate_init(InnovationGate2D *gate, float gamma_1, float gamma_2, uint8_t max_rejects) {
    gate->gamma_1 = gamma_1;
    gate->gamma_2 = gamma_2;
    gate->consecutive_rejects = 0;
    gate->max_allowed_rejects = max_rejects;
    gate->history_idx = 0;
    gate->history_count = 0;
    gate->nis_window_sum = 0.0f;
    memset(gate->nis_history, 0, sizeof(gate->nis_history));
}

/*
 * Валідація 2D вимірювання:
 * y       - [вхід] вектор нев'язки (2 елементи: y[0], y[1])
 * S       - [вхід] матриця коваріації нев'язки 2x2: [S00, S01; S10, S11] (S01 == S10)
 * d2_out  - [вихід] обчислений квадрат відстані Махаланобіса
 * s_scale - [вихід] коефіцієнт масштабування шуму R (1.0 якщо масштабування непотрібне)
 */
GatingStatus innovation_gate_validate_2d(
    InnovationGate2D *gate,
    const float y[2],
    const float S[2][2],
    float *d2_out,
    float *s_scale
) {
    /* 1. Аналітичне обчислення детермінанта матриці S 2x2 */
    const float det = S[0][0] * S[1][1] - S[0][1] * S[1][0];
    
    /* Захист від виродженої або від'ємно визначеної матриці */
    if (det <= 1e-12f) {
        *d2_out = 1e6f;
        *s_scale = 1.0f;
        gate->consecutive_rejects++;
        if (gate->consecutive_rejects >= gate->max_allowed_rejects) {
            return GATE_DIVERGENCE_ALARM;
        }
        return GATE_REJECTED_OUTLIER;
    }

    /* 2. Обчислення аналітичної оберненої матриці S_inv = adj(S) / det */
    const float inv_det = 1.0f / det;
    const float S_inv[2][2] = {
        {  S[1][1] * inv_det, -S[0][1] * inv_det },
        { -S[1][0] * inv_det,  S[0][0] * inv_det }
    };

    /* 3. Обчислення нормованого квадрата Махаланобіса d² = yᵀ * S⁻¹ * y */
    const float temp0 = S_inv[0][0] * y[0] + S_inv[0][1] * y[1];
    const float temp1 = S_inv[1][0] * y[0] + S_inv[1][1] * y[1];
    const float d2 = y[0] * temp0 + y[1] * temp1;

    *d2_out = d2;

    /* 4. Оновлення ковзного вікна NIS (додаємо лише значення валідного масштабу) */
    const float bounded_d2 = (d2 < gate->gamma_2 * 2.0f) ? d2 : (gate->gamma_2 * 2.0f);
    gate->nis_window_sum -= gate->nis_history[gate->history_idx];
    gate->nis_history[gate->history_idx] = bounded_d2;
    gate->nis_window_sum += bounded_d2;
    
    gate->history_idx = (gate->history_idx + 1) % NIS_WINDOW_SIZE;
    if (gate->history_count < NIS_WINDOW_SIZE) {
        gate->history_count++;
    }

    /* 5. Тризонна перевірка статистичного критерію */
    if (d2 <= gate->gamma_1) {
        /* Зона повної довіри: вимір чистий */
        gate->consecutive_rejects = 0;
        *s_scale = 1.0f;
        return GATE_ACCEPTED;
    } 
    else if (d2 <= gate->gamma_2) {
        /* Зона сумніву: м'яке зважування (Huber-подібне роздування R) */
        gate->consecutive_rejects = 0;
        *s_scale = d2 / gate->gamma_1;
        return GATE_SOFT_SCALED;
    } 
    else {
        /* Зона грубого викиду: повне відсікання */
        *s_scale = 1.0f;
        gate->consecutive_rejects++;

        /* Перевірка чи не є це хронічною розбіжністю фільтра */
        if (gate->consecutive_rejects >= gate->max_allowed_rejects) {
            return GATE_DIVERGENCE_ALARM;
        }

        /* Перевірка середнього рівня NIS у вікні */
        if (gate->history_count >= NIS_WINDOW_SIZE) {
            const float mean_nis = gate->nis_window_sum / (float)(NIS_WINDOW_SIZE * 2); /* m = 2 */
            if (mean_nis > 2.5f) {
                return GATE_DIVERGENCE_ALARM;
            }
        }

        return GATE_REJECTED_OUTLIER;
    }
}
