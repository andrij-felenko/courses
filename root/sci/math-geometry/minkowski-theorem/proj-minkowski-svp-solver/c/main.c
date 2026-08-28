#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define MAX_DIM 16

/* Структура представлення ґратки та її ортогоналізованого базису */
typedef struct {
    int n;
    double b[MAX_DIM][MAX_DIM];     /* Вихідні вектори базису b[i][j] */
    double b_star[MAX_DIM][MAX_DIM];/* Ортогональні вектори Gram-Schmidt */
    double mu[MAX_DIM][MAX_DIM];    /* Коефіцієнти проекції mu[i][j] */
    double b_star_sq[MAX_DIM];      /* Квадрати довжин ||b_star[i]||^2 */
    double det;                     /* Визначник ґратки det(L) */
    double minkowski_radius;        /* Радіус Мінковського R_M */
} Lattice;

/* Обчислення евклідового скалярного добутку векторів */
static double dot_product(const double *u, const double *v, int n) {
    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        sum += u[i] * v[i];
    }
    return sum;
}

/* Ортогоналізація Грама-Шмідта над дійсними числами */
void lattice_orthogonalize(Lattice *lat) {
    int n = lat->n;
    lat->det = 1.0;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            lat->b_star[i][j] = lat->b[i][j];
        }
        for (int j = 0; j < i; j++) {
            double num = dot_product(lat->b[i], lat->b_star[j], n);
            lat->mu[i][j] = num / lat->b_star_sq[j];
            for (int k = 0; k < n; k++) {
                lat->b_star[i][k] -= lat->mu[i][j] * lat->b_star[j][k];
            }
        }
        lat->b_star_sq[i] = dot_product(lat->b_star[i], lat->b_star[i], n);
        lat->det *= sqrt(lat->b_star_sq[i]);
    }

    /* Теоретична верхня межа Мінковського R_M = sqrt(n) * (det(L))^(1/n) */
    lat->minkowski_radius = sqrt((double)n) * pow(lat->det, 1.0 / (double)n);
}

/* Стан процесу перебору у кулі */
typedef struct {
    double best_norm_sq;
    int best_z[MAX_DIM];
    double best_v[MAX_DIM];
    long long visited_nodes;
} SdpState;

/* Рекурсивний крок перебору рівня k за схемою Шнорра-Ейхнера */
static void enumerate_layer(const Lattice *lat, SdpState *st, int k,
                            int z[MAX_DIM], double l[MAX_DIM + 1]) {
    int n = lat->n;
    st->visited_nodes++;

    /* Досягнуто листка дерева: знайдено повний вектор */
    if (k < 0) {
        bool is_zero = true;
        for (int i = 0; i < n; i++) {
            if (z[i] != 0) { is_zero = false; break; }
        }
        if (!is_zero && l[0] < st->best_norm_sq) {
            st->best_norm_sq = l[0];
            for (int i = 0; i < n; i++) {
                st->best_z[i] = z[i];
            }
            /* Обчислення вихідних координат вектора v = sum(z_i * b_i) */
            for (int j = 0; j < n; j++) {
                st->best_v[j] = 0.0;
                for (int i = 0; i < n; i++) {
                    st->best_v[j] += (double)z[i] * lat->b[i][j];
                }
            }
        }
        return;
    }

    /* Розрахунок центру проекції c_k */
    double c_k = 0.0;
    for (int j = k + 1; j < n; j++) {
        c_k -= lat->mu[j][k] * (double)z[j];
    }

    int center_z = (int)round(c_k);
    int step = 0;

    while (1) {
        /* Зигзаг Шнорра-Ейхнера: 0, +1, -1, +2, -2, +3, ... */
        int cur_z;
        if (step == 0) {
            cur_z = center_z;
        } else if (step % 2 == 1) {
            cur_z = center_z + (step + 1) / 2;
        } else {
            cur_z = center_z - step / 2;
        }

        double diff = (double)cur_z - c_k;
        double new_l = l[k + 1] + diff * diff * lat->b_star_sq[k];

        /* Відсікання гілки: часткова норма вже перевищує поточний радіус */
        if (new_l >= st->best_norm_sq) {
            if (step > 1) break;
            step++;
            continue;
        }

        z[k] = cur_z;
        l[k] = new_l;
        enumerate_layer(lat, st, k - 1, z, l);
        step++;
    }
}

/* Інтерфейс точного пошуку найкоротшого вектора SVP */
bool lattice_find_svp(Lattice *lat, double *out_norm, double *out_v, long long *nodes) {
    lattice_orthogonalize(lat);

    SdpState st;
    /* Початковий радіус пошуку - верхня межа Мінковського */
    st.best_norm_sq = lat->minkowski_radius * lat->minkowski_radius;
    st.visited_nodes = 0;
    for (int i = 0; i < lat->n; i++) {
        st.best_z[i] = 0;
        st.best_v[i] = 0.0;
    }

    int z[MAX_DIM] = {0};
    double l[MAX_DIM + 1] = {0.0};

    enumerate_layer(lat, &st, lat->n - 1, z, l);

    if (st.best_norm_sq < lat->minkowski_radius * lat->minkowski_radius) {
        *out_norm = sqrt(st.best_norm_sq);
        for (int i = 0; i < lat->n; i++) out_v[i] = st.best_v[i];
        if (nodes) *nodes = st.visited_nodes;
        return true;
    }
    return false;
}

int main(void) {
    /* 4-вимірна тестова ґратка (q-арна підґратка) */
    Lattice lat = {
        .n = 4,
        .b = {
            { 17.0,  0.0,  0.0,  0.0 },
            {  3.0,  1.0,  0.0,  0.0 },
            {  7.0,  0.0,  1.0,  0.0 },
            {  5.0,  0.0,  0.0,  1.0 }
        }
    };

    double shortest_norm = 0.0;
    double shortest_v[MAX_DIM] = {0.0};
    long long nodes = 0;

    bool found = lattice_find_svp(&lat, &shortest_norm, shortest_v, &nodes);

    printf("=== Перевірка теореми Мінковського для ґратки в R^4 ===\n");
    printf("Визначник ґратки det(L): %.4f\n", lat.det);
    printf("Теоретична межа Мінковського R_M: %.4f\n", lat.minkowski_radius);

    if (found) {
        printf("Знайдено найкоротший вектор v: [ ");
        for (int i = 0; i < lat.n; i++) printf("%.1f ", shortest_v[i]);
        printf("]\n");
        printf("Фактична довжина ||v|| = lambda_1(L): %.4f\n", shortest_norm);
        printf("Нерівність Мінковського (lambda_1 <= R_M): %.4f <= %.4f (%s)\n",
               shortest_norm, lat.minkowski_radius,
               shortest_norm <= lat.minkowski_radius ? "ПІДТВЕРДЖЕНО" : "ПОМИЛКА");
        printf("Кількість відвіданих вузлів дерева: %lld\n", nodes);
    } else {
        printf("Помилка: вектор не знайдено в кулі Мінковського.\n");
    }

    return 0;
}
