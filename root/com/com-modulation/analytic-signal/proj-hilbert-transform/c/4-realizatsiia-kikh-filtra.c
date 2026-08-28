#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура потокового КІХ-фільтра Гільберта */
typedef struct {
    double *taps;        /* Масив коефіцієнтів фільтра */
    double *delay_line;  /* Кільцевий буфер для вхідних відліків */
    size_t length;        /* Загальна довжина фільтра M (непарне число) */
    size_t head;          /* Поточна позиція запису в кільцевому буфері */
    size_t delay;         /* Гропова затримка (M - 1) / 2 */
} fir_hilbert_t;

/* Створення та ініціалізація КІХ-фільтра Гільберта з вікном Хеммінга */
fir_hilbert_t* fir_hilbert_create(size_t num_taps) {
    if (num_taps % 2 == 0) num_taps++; /* Гарантуємо непарну довжину */

    fir_hilbert_t *filter = (fir_hilbert_t*)malloc(sizeof(fir_hilbert_t));
    if (!filter) return NULL;

    filter->length = num_taps;
    filter->delay = (num_taps - 1) / 2;
    filter->head = 0;

    filter->taps = (double*)calloc(num_taps, sizeof(double));
    filter->delay_line = (double*)calloc(num_taps, sizeof(double));

    if (!filter->taps || !filter->delay_line) {
        free(filter->taps);
        free(filter->delay_line);
        free(filter);
        return NULL;
    }

    /* Обчислення коефіцієнтів фільтра з вікном Хеммінга */
    int half = (int)filter->delay;
    for (int i = -half; i <= half; i++) {
        size_t idx = (size_t)(i + half);
        if (i % 2 != 0) {
            /* Віконна функція Хеммінга */
            double w = 0.54 + 0.46 * cos(M_PI * (double)i / (double)half);
            filter->taps[idx] = (2.0 / (M_PI * (double)i)) * w;
        } else {
            filter->taps[idx] = 0.0; /* Парні коефіцієнти строго 0 */
        }
    }

    return filter;
}

void fir_hilbert_free(fir_hilbert_t *filter) {
    if (filter) {
        free(filter->taps);
        free(filter->delay_line);
        free(filter);
    }
}

/* Обробка одного відліку сигналу в реальному часі */
void fir_hilbert_process(fir_hilbert_t *filter, double sample_in, double *i_out, double *q_out) {
    /* Запис нового відліку в кільцевий буфер */
    filter->delay_line[filter->head] = sample_in;

    /* 1. Обчислення Q(t) через дискретну згортку */
    double q_acc = 0.0;
    size_t idx = filter->head;

    for (size_t k = 0; k < filter->length; k++) {
        q_acc += filter->taps[k] * filter->delay_line[idx];
        if (idx == 0) {
            idx = filter->length - 1;
        } else {
            idx--;
        }
    }

    /* 2. Отримання I(t) з лінії затримки для компенсації фазового зсуву */
    size_t delayed_idx = (filter->head + filter->length - filter->delay) % filter->length;
    *i_out = filter->delay_line[delayed_idx];
    *q_out = q_acc;

    /* Зсув вказівника кільцевого буфера */
    filter->head = (filter->head + 1) % filter->length;
}

int main(void) {
    fir_hilbert_t *hilbert = fir_hilbert_create(31);
    if (!hilbert) return 1;

    printf("Sample \t Input \t\t I (Delayed) \t Q (Hilbert) \t Envelope\n");
    printf("----------------------------------------------------------------\n");

    for (int n = 0; n < 40; n++) {
        double in = cos(2.0 * M_PI * 0.1 * n);
        double i_val, q_val;
        fir_hilbert_process(hilbert, in, &i_val, &q_val);
        double env = sqrt(i_val * i_val + q_val * q_val);

        if (n >= 15) { /* Пропускаємо заповнення лінії затримки фільтра */
            printf("%2d \t %+.4f \t %+.4f \t %+.4f \t %.4f\n", n, in, i_val, q_val, env);
        }
    }

    fir_hilbert_free(hilbert);
    return 0;
}
