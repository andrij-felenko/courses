#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Комплексне число та базова арифметика */
typedef struct {
    double re;
    double im;
} Cplx;

static inline Cplx cplx_make(double re, double im) {
    Cplx z = { re, im };
    return z;
}

static inline Cplx cplx_add(Cplx a, Cplx b) {
    return cplx_make(a.re + b.re, a.im + b.im);
}

static inline Cplx cplx_sub(Cplx a, Cplx b) {
    return cplx_make(a.re - b.re, a.im - b.im);
}

static inline Cplx cplx_mul(Cplx a, Cplx b) {
    return cplx_make(a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re);
}

static inline Cplx cplx_scale(Cplx a, double s) {
    return cplx_make(a.re * s, a.im * s);
}

static inline Cplx cplx_conj(Cplx a) {
    return cplx_make(a.re, -a.im);
}

static inline double cplx_norm_sqr(Cplx a) {
    return a.re * a.re + a.im * a.im;
}

static inline Cplx cplx_exp_i(double theta) {
    return cplx_make(cos(theta), sin(theta));
}

/* Опис факторизації скінченної абелевої групи */
#define MAX_FACTORS 8

typedef struct {
    int num_factors;
    int orders[MAX_FACTORS];
    int strides[MAX_FACTORS];
    int total_order;
} FiniteAbelianGroup;

/* Ініціалізація структури групи */
void group_init(FiniteAbelianGroup* g, const int* orders, int num_factors) {
    g->num_factors = num_factors;
    g->total_order = 1;
    for (int i = 0; i < num_factors; i++) {
        g->orders[i] = orders[i];
        g->total_order *= orders[i];
    }
    g->strides[num_factors - 1] = 1;
    for (int i = num_factors - 2; i >= 0; i--) {
        g->strides[i] = g->strides[i + 1] * g->orders[i + 1];
    }
}

/* Перехід: лінійний індекс -> вектор координат */
void group_decode_index(const FiniteAbelianGroup* g, int idx, int* coords_out) {
    int rem = idx;
    for (int i = 0; i < g->num_factors; i++) {
        coords_out[i] = rem / g->strides[i];
        rem %= g->strides[i];
    }
}

/* Перехід: вектор координат -> лінійний індекс */
int group_encode_coords(const FiniteAbelianGroup* g, const int* coords) {
    int idx = 0;
    for (int i = 0; i < g->num_factors; i++) {
        idx += coords[i] * g->strides[i];
    }
    return idx;
}

/* Обчислення фази характеру: chi_y(x) */
Cplx group_eval_character(const FiniteAbelianGroup* g, int x_idx, int y_idx) {
    int x[MAX_FACTORS], y[MAX_FACTORS];
    group_decode_index(g, x_idx, x);
    group_decode_index(g, y_idx, y);

    double total_phase = 0.0;
    for (int i = 0; i < g->num_factors; i++) {
        total_phase += 2.0 * M_PI * ((double)(x[i] * y[i])) / (double)g->orders[i];
    }
    return cplx_exp_i(total_phase);
}

/* Пряме перетворення Фур'є на групі (GDFT) */
void group_fourier_transform(const FiniteAbelianGroup* g, const Cplx* input, Cplx* output) {
    int N = g->total_order;
    double scale = 1.0 / sqrt((double)N);

    for (int y = 0; y < N; y++) {
        Cplx sum = cplx_make(0.0, 0.0);
        for (int x = 0; x < N; x++) {
            Cplx chi = group_eval_character(g, x, y);
            Cplx term = cplx_mul(input[x], cplx_conj(chi));
            sum = cplx_add(sum, term);
        }
        output[y] = cplx_scale(sum, scale);
    }
}

/* Обернене перетворення Фур'є на групі (IGDFT) */
void group_inverse_fourier_transform(const FiniteAbelianGroup* g, const Cplx* input, Cplx* output) {
    int N = g->total_order;
    double scale = 1.0 / sqrt((double)N);

    for (int x = 0; x < N; x++) {
        Cplx sum = cplx_make(0.0, 0.0);
        for (int y = 0; y < N; y++) {
            Cplx chi = group_eval_character(g, x, y);
            Cplx term = cplx_mul(input[y], chi);
            sum = cplx_add(sum, term);
        }
        output[x] = cplx_scale(sum, scale);
    }
}

/* Обчислення згортки двох сигналів на групі */
void group_convolve(const FiniteAbelianGroup* g, const Cplx* f, const Cplx* h, Cplx* out) {
    int N = g->total_order;
    int x_coords[MAX_FACTORS], z_coords[MAX_FACTORS], diff_coords[MAX_FACTORS];

    for (int x = 0; x < N; x++) {
        group_decode_index(g, x, x_coords);
        Cplx sum = cplx_make(0.0, 0.0);

        for (int z = 0; z < N; z++) {
            group_decode_index(g, z, z_coords);
            for (int i = 0; i < g->num_factors; i++) {
                diff_coords[i] = (x_coords[i] - z_coords[i] + g->orders[i]) % g->orders[i];
            }
            int diff_idx = group_encode_coords(g, diff_coords);
            sum = cplx_add(sum, cplx_mul(f[z], h[diff_idx]));
        }
        out[x] = sum;
    }
}

/* Пошук анулятора підгрупи, заданої генераторами */
int group_find_annihilator(const FiniteAbelianGroup* g, const int* gen_indices, int num_gens, int* ann_out) {
    int N = g->total_order;
    int count = 0;
    const double eps = 1e-6;

    for (int y = 0; y < N; y++) {
        int is_ann = 1;
        for (int k = 0; k < num_gens; k++) {
            Cplx chi = group_eval_character(g, gen_indices[k], y);
            if (fabs(chi.re - 1.0) > eps || fabs(chi.im) > eps) {
                is_ann = 0;
                break;
            }
        }
        if (is_ann) {
            ann_out[count++] = y;
        }
    }
    return count;
}

int main(void) {
    /* Приклад: група G = Z_2 x Z_4 (порядок 8) */
    int factors[] = { 2, 4 };
    FiniteAbelianGroup G;
    group_init(&G, factors, 2);

    printf("Група G = Z_2 x Z_4, загальний порядок |G| = %d\n", G.total_order);

    /* Тестовий сигнал */
    Cplx signal[8];
    for (int i = 0; i < 8; i++) {
        signal[i] = cplx_make((double)(i + 1), 0.0);
    }

    Cplx spectrum[8];
    Cplx reconstructed[8];

    group_fourier_transform(&G, signal, spectrum);
    group_inverse_fourier_transform(&G, spectrum, reconstructed);

    printf("\nПеревірка відновлення сигналу (GDFT -> IGDFT):\n");
    double total_err = 0.0;
    for (int i = 0; i < 8; i++) {
        double err = fabs(signal[i].re - reconstructed[i].re) + fabs(signal[i].im - reconstructed[i].im);
        total_err += err;
        printf("  x=%d: початковий=(%.1f, %.1f) -> відновлений=(%.4f, %.4f)\n",
               i, signal[i].re, signal[i].im, reconstructed[i].re, reconstructed[i].im);
    }
    printf("Сумарна похибка відновлення: %.2e\n", total_err);

    /* Перевірка анулятора підгрупи H = <(0, 2)> */
    int gen_coords[] = { 0, 2 };
    int gen_idx = group_encode_coords(&G, gen_coords);
    int annihilator[8];
    int ann_size = group_find_annihilator(&G, &gen_idx, 1, annihilator);

    printf("\nПідгрупа H породжена елементом (0, 2) [лінійний індекс %d]\n", gen_idx);
    printf("Анулятор H^perp має розмір %d (очікувано 4):\n", ann_size);
    for (int i = 0; i < ann_size; i++) {
        int coords[2];
        group_decode_index(&G, annihilator[i], coords);
        printf("  chi_%d: частоти (%d, %d)\n", annihilator[i], coords[0], coords[1]);
    }

    return 0;
}
