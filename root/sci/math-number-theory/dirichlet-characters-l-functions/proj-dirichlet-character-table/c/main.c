#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <string.h>

#define PI 3.14159265358979323846
#define EPSILON 1e-6

/* Структура для представлення комплексного числа */
typedef struct {
    double real;
    double imag;
} Complex;

Complex complex_make(double r, double i) {
    Complex c;
    c.real = r;
    c.imag = i;
    return c;
}

Complex complex_add(Complex a, Complex b) {
    return complex_make(a.real + b.real, a.imag + b.imag);
}

Complex complex_sub(Complex a, Complex b) {
    return complex_make(a.real - b.real, a.imag - b.imag);
}

Complex complex_mul(Complex a, Complex b) {
    return complex_make(a.real * b.real - a.imag * b.imag,
                        a.real * b.imag + a.imag * b.real);
}

Complex complex_conj(Complex a) {
    return complex_make(a.real, -a.imag);
}

double complex_abs(Complex a) {
    return sqrt(a.real * a.real + a.imag * a.imag);
}

Complex complex_polar(double r, double theta) {
    return complex_make(r * cos(theta), r * sin(theta));
}

/* Алгоритм Евкліда для обчислення найбільшого спільного дільника */
int gcd(int a, int b) {
    while (b != 0) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

/* Швидке бінарне піднесення до степеня за модулем */
int power_mod(int base, int exp, int mod) {
    int res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (res * base) % mod;
        base = (base * base) % mod;
        exp /= 2;
    }
    return res;
}

/* Пошук найменшого первісного кореня за модулем q */
int find_primitive_root(int q, int phi_q) {
    if (q == 2) return 1;
    for (int g = 2; g < q; ++g) {
        if (gcd(g, q) != 1) continue;
        bool ok = true;
        int temp = phi_q;
        for (int p = 2; p * p <= temp; ++p) {
            if (temp % p == 0) {
                if (power_mod(g, phi_q / p, q) == 1) {
                    ok = false;
                    break;
                }
                while (temp % p == 0) temp /= p;
            }
        }
        if (temp > 1 && ok) {
            if (power_mod(g, phi_q / temp, q) == 1) ok = false;
        }
        if (ok) return g;
    }
    return -1;
}

/* Структура для повної таблиці характерів Діріхле */
typedef struct {
    int q;
    int phi_q;
    int *coprimes;
    int *discrete_log;
    Complex **table;
} DirichletTable;

DirichletTable *create_dirichlet_table(int q) {
    DirichletTable *dt = (DirichletTable *)malloc(sizeof(DirichletTable));
    if (!dt) return NULL;
    dt->q = q;
    dt->phi_q = 0;

    int *temp_coprimes = (int *)malloc(sizeof(int) * q);
    for (int i = 1; i < q; ++i) {
        if (gcd(i, q) == 1) {
            temp_coprimes[dt->phi_q++] = i;
        }
    }
    dt->coprimes = (int *)malloc(sizeof(int) * dt->phi_q);
    memcpy(dt->coprimes, temp_coprimes, sizeof(int) * dt->phi_q);
    free(temp_coprimes);

    int g = find_primitive_root(q, dt->phi_q);
    if (g == -1) {
        free(dt->coprimes);
        free(dt);
        return NULL;
    }

    dt->discrete_log = (int *)malloc(sizeof(int) * q);
    int curr = 1;
    for (int exp = 0; exp < dt->phi_q; ++exp) {
        dt->discrete_log[curr] = exp;
        curr = (curr * g) % q;
    }

    dt->table = (Complex **)malloc(sizeof(Complex *) * dt->phi_q);
    for (int k = 0; k < dt->phi_q; ++k) {
        dt->table[k] = (Complex *)malloc(sizeof(Complex) * dt->phi_q);
        for (int i = 0; i < dt->phi_q; ++i) {
            int n = dt->coprimes[i];
            int idx = dt->discrete_log[n];
            double angle = 2.0 * PI * k * idx / dt->phi_q;
            dt->table[k][i] = complex_polar(1.0, angle);
        }
    }
    return dt;
}

void free_dirichlet_table(DirichletTable *dt) {
    if (!dt) return;
    for (int k = 0; k < dt->phi_q; ++k) {
        free(dt->table[k]);
    }
    free(dt->table);
    free(dt->discrete_log);
    free(dt->coprimes);
    free(dt);
}

/* Обчислення провідника (conductor) для характеру */
int compute_conductor(const DirichletTable *dt, int char_idx) {
    for (int d = 1; d <= dt->q; ++d) {
        if (dt->q % d != 0) continue;
        bool is_conductor = true;
        for (int i = 0; i < dt->phi_q; ++i) {
            int n = dt->coprimes[i];
            if (n % d == 1 % d) {
                if (fabs(dt->table[char_idx][i].real - 1.0) > EPSILON ||
                    fabs(dt->table[char_idx][i].imag) > EPSILON) {
                    is_conductor = false;
                    break;
                }
            }
        }
        if (is_conductor) return d;
    }
    return dt->q;
}

/* Перевірка парності характеру: chi(-1) = 1 (парний) або -1 (непарний) */
bool is_character_even(const DirichletTable *dt, int char_idx) {
    int minus_one_val = dt->q - 1;
    for (int i = 0; i < dt->phi_q; ++i) {
        if (dt->coprimes[i] == minus_one_val) {
            return (dt->table[char_idx][i].real > 0.0);
        }
    }
    return true;
}

/* Перевірка дійсності характеру (знаковий характер) */
bool is_character_real(const DirichletTable *dt, int char_idx) {
    for (int i = 0; i < dt->phi_q; ++i) {
        if (fabs(dt->table[char_idx][i].imag) > EPSILON) return false;
    }
    return true;
}

/* Перше співвідношення ортогональності: скалярний добуток рядків */
Complex verify_row_orthogonality(const DirichletTable *dt, int a, int b) {
    Complex sum = complex_make(0.0, 0.0);
    for (int i = 0; i < dt->phi_q; ++i) {
        Complex term = complex_mul(dt->table[a][i], complex_conj(dt->table[b][i]));
        sum = complex_add(sum, term);
    }
    return sum;
}

/* Друге співвідношення ортогональності: сума за всіма характерами для стовпчиків */
Complex verify_col_orthogonality(const DirichletTable *dt, int elem_m_idx, int elem_n_idx) {
    Complex sum = complex_make(0.0, 0.0);
    for (int k = 0; k < dt->phi_q; ++k) {
        Complex term = complex_mul(dt->table[k][elem_m_idx],
                                   complex_conj(dt->table[k][elem_n_idx]));
        sum = complex_add(sum, term);
    }
    return sum;
}

/* Відновлення дельта-функції класу залишків delta(n == a mod q) */
Complex fourier_delta_filter(const DirichletTable *dt, int a_idx, int n_idx) {
    Complex sum = complex_make(0.0, 0.0);
    for (int k = 0; k < dt->phi_q; ++k) {
        Complex term = complex_mul(complex_conj(dt->table[k][a_idx]),
                                   dt->table[k][n_idx]);
        sum = complex_add(sum, term);
    }
    return complex_make(sum.real / dt->phi_q, sum.imag / dt->phi_q);
}

int main(void) {
    int q = 5;
    DirichletTable *dt = create_dirichlet_table(q);
    if (!dt) {
        printf("Помилка побудови таблиці характерів за модулем q = %d\n", q);
        return 1;
    }

    printf("Таблиця характерів Діріхле за модулем q = %d (φ(q) = %d):\n", dt->q, dt->phi_q);
    printf("----------------------------------------------------------------------\n");
    for (int k = 0; k < dt->phi_q; ++k) {
        int cond = compute_conductor(dt, k);
        bool even = is_character_even(dt, k);
        bool real_char = is_character_real(dt, k);

        printf("χ_%d [cond=%d, %s, %s, %s]:\n  ",
               k, cond,
               (cond == dt->q) ? "первісний" : "індукований",
               even ? "парний" : "непарний",
               real_char ? "дійсний" : "комплексний");

        for (int i = 0; i < dt->phi_q; ++i) {
            printf("n=%d:(%+.2f,%+.2f) ",
                   dt->coprimes[i], dt->table[k][i].real, dt->table[k][i].imag);
        }
        printf("\n");
    }

    printf("\n--- Перевірка першого співвідношення ортогональності (за рядками) ---\n");
    Complex dot_1_2 = verify_row_orthogonality(dt, 1, 2);
    Complex dot_2_2 = verify_row_orthogonality(dt, 2, 2);
    printf("⟨χ_1, χ_2⟩ = (%.2f, %.2f)  [очікується (0.00, 0.00)]\n", dot_1_2.real, dot_1_2.imag);
    printf("⟨χ_2, χ_2⟩ = (%.2f, %.2f)  [очікується (%.2f, 0.00)]\n", dot_2_2.real, dot_2_2.imag, (double)dt->phi_q);

    printf("\n--- Перевірка другого співвідношення ортогональності (за стовпчиками) ---\n");
    Complex col_1_3 = verify_col_orthogonality(dt, 0, 2);
    Complex col_3_3 = verify_col_orthogonality(dt, 2, 2);
    printf("∑_χ χ(1)·χ̄(3) = (%.2f, %.2f)  [очікується (0.00, 0.00)]\n", col_1_3.real, col_1_3.imag);
    printf("∑_χ χ(3)·χ̄(3) = (%.2f, %.2f)  [очікується (%.2f, 0.00)]\n", col_3_3.real, col_3_3.imag, (double)dt->phi_q);

    printf("\n--- Спектральне відновлення дельта-фільтра δ(n ≡ 3 mod 5) ---\n");
    for (int i = 0; i < dt->phi_q; ++i) {
        Complex delta = fourier_delta_filter(dt, 2, i);
        printf("δ(%d ≡ 3 mod 5) = %.2f\n", dt->coprimes[i], delta.real);
    }

    free_dirichlet_table(dt);
    return 0;
}
