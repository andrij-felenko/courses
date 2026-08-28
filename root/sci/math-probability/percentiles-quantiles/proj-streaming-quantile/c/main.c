#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    double p;           /* Цільовий квантиль (наприклад, 0.99) */
    int count;          /* Кількість отриманих спостережень */
    double q[5];        /* Висоти маркерів */
    int n[5];           /* Фактичні позиції маркерів */
    double n_prime[5];  /* Бажані позиції маркерів */
    double dn[5];       /* Приріст бажаних позицій на кожен крок */
} p2_quantile_t;

/* Ініціалізація структури квантиля */
void p2_init(p2_quantile_t *est, double p) {
    est->p = p;
    est->count = 0;
    est->dn[0] = 0.0;
    est->dn[1] = p / 2.0;
    est->dn[2] = p;
    est->dn[3] = (1.0 + p) / 2.0;
    est->dn[4] = 1.0;
}

/* Допоміжна функція сортування перших 5 елементів */
static void sort5(double arr[5]) {
    for (int i = 0; i < 4; ++i) {
        for (int j = i + 1; j < 5; ++j) {
            if (arr[i] > arr[j]) {
                double tmp = arr[i];
                arr[i] = arr[j];
                arr[j] = tmp;
            }
        }
    }
}

/* Параболічне зсунення маркера */
static double parabolic(const p2_quantile_t *est, int i, int d) {
    double q0 = est->q[i - 1], q1 = est->q[i], q2 = est->q[i + 1];
    int n0 = est->n[i - 1], n1 = est->n[i], n2 = est->n[i + 1];
    
    double term1 = (double)d / (n2 - n0);
    double term2 = (n1 - n0 + d) * (q2 - q1) / (n2 - n1);
    double term3 = (n2 - n1 - d) * (q1 - q0) / (n1 - n0);
    
    return q1 + term1 * (term2 + term3);
}

/* Лінійне зсунення маркера при втраті монотонності */
static double linear(const p2_quantile_t *est, int i, int d) {
    return est->q[i] + d * (est->q[i + d] - est->q[i]) / (est->n[i + d] - est->n[i]);
}

/* Додавання нового спостереження у потік */
void p2_update(p2_quantile_t *est, double x) {
    if (est->count < 5) {
        est->q[est->count++] = x;
        if (est->count == 5) {
            sort5(est->q);
            for (int i = 0; i < 5; ++i) {
                est->n[i] = i + 1;
                est->n_prime[i] = 1.0 + 4.0 * est->dn[i];
            }
        }
        return;
    }

    /* Знаходимо інтервал, у який потрапило x */
    int k = -1;
    if (x < est->q[0]) {
        est->q[0] = x;
        k = 0;
    } else if (x >= est->q[4]) {
        est->q[4] = x;
        k = 3;
    } else {
        for (int i = 1; i < 5; ++i) {
            if (x < est->q[i]) {
                k = i - 1;
                break;
            }
        }
    }

    /* Збільшуємо фактичні позиції наступних маркерів */
    for (int i = k + 1; i < 5; ++i) {
        est->n[i]++;
    }

    /* Оновлюємо ідеальні позиції */
    for (int i = 0; i < 5; ++i) {
        est->n_prime[i] += est->dn[i];
    }

    /* Коригуємо внутрішні маркери 1, 2, 3 */
    for (int i = 1; i <= 3; ++i) {
        double d = est->n_prime[i] - est->n[i];
        if ((d >= 1.0 && est->n[i + 1] - est->n[i] > 1) ||
            (d <= -1.0 && est->n[i - 1] - est->n[i] < -1)) {
            int step = (d >= 0.0) ? 1 : -1;
            double q_new = parabolic(est, i, step);
            
            if (est->q[i - 1] < q_new && q_new < est->q[i + 1]) {
                est->q[i] = q_new;
            } else {
                est->q[i] = linear(est, i, step);
            }
            est->n[i] += step;
        }
    }
}

/* Отримання поточної оцінки квантиля */
double p2_result(const p2_quantile_t *est) {
    if (est->count == 0) return 0.0;
    if (est->count <= 5) {
        double copy[5];
        for (int i = 0; i < est->count; ++i) copy[i] = est->q[i];
        sort5(copy);
        int idx = (int)(est->p * (est->count - 1));
        return copy[idx];
    }
    return est->q[2];
}
