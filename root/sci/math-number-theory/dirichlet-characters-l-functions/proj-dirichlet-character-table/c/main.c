#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define PI 3.14159265358979323846

/* Структура для представлення комплексного числа */
typedef struct {
    double real;
    double imag;
} Complex;

Complex complex_make(double r, double i) {
    Complex c = {r, i};
    return c;
}

Complex complex_mul(Complex a, Complex b) {
    return complex_make(a.real * b.real - a.imag * b.imag,
                        a.real * b.imag + a.imag * b.real);
}

Complex complex_conj(Complex a) {
    return complex_make(a.real, -a.imag);
}

/* Алгоритм Евкліда для НСД */
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
        int dummy = phi_q;
        for (int p = 2; p * p <= dummy; ++p) {
            if (dummy % p == 0) {
                if (power_mod(g, phi_q / p, q) == 1) {
                    ok = false;
                    break;
                }
                while (dummy % p == 0) dummy /= p;
            }
        }
        if (dummy > 1 && ok) {
            if (power_mod(g, phi_q / dummy, q) == 1) ok = false;
        }
        if (ok) return g;
    }
    return -1;
}

/* Обчислення провідника (conductor) для характера */
int compute_conductor(int q, const int *coprimes, int phi_q, const Complex *char_vals) {
    for (int d = 1; d <= q; ++d) {
        if (q % d != 0) continue;
        bool is_conductor = true;
        for (int i = 0; i < phi_q; ++i) {
            int n = coprimes[i];
            if (n % d == 1 % d) {
                if (fabs(char_vals[i].real - 1.0) > 1e-6 || fabs(char_vals[i].imag) > 1e-6) {
                    is_conductor = false;
                    break;
                }
            }
        }
        if (is_conductor) return d;
    }
    return q;
}

int main(void) {
    int q = 5;
    int coprimes[5];
    int phi_q = 0;

    for (int i = 1; i < q; ++i) {
        if (gcd(i, q) == 1) {
            coprimes[phi_q++] = i;
        }
    }

    int g = find_primitive_root(q, phi_q);
    if (g == -1) {
        printf("Модуль q=%d не має єдиного первісного кореня.\n", q);
        return 1;
    }

    int *discrete_log = (int *)malloc(sizeof(int) * q);
    int curr = 1;
    for (int exp = 0; exp < phi_q; ++exp) {
        discrete_log[curr] = exp;
        curr = (curr * g) % q;
    }

    Complex **char_table = (Complex **)malloc(sizeof(Complex *) * phi_q);
    for (int k = 0; k < phi_q; ++k) {
        char_table[k] = (Complex *)malloc(sizeof(Complex) * phi_q);
        for (int i = 0; i < phi_q; ++i) {
            int n = coprimes[i];
            int idx = discrete_log[n];
            double angle = 2.0 * PI * k * idx / phi_q;
            char_table[k][i] = complex_make(cos(angle), sin(angle));
        }
    }

    printf("Таблиця характерів за модулем q = %d (g = %d):\n", q, g);
    for (int k = 0; k < phi_q; ++k) {
        int conductor = compute_conductor(q, coprimes, phi_q, char_table[k]);
        printf("χ_%d [провідник d=%d, %s]: ", k, conductor,
               (conductor == q) ? "первісний" : "індукований");
        for (int i = 0; i < phi_q; ++i) {
            printf("(%.2f, %.2f) ", char_table[k][i].real, char_table[k][i].imag);
        }
        printf("\n");
    }

    /* Перевірка ортогональності chi_1 та chi_2 */
    Complex sum = complex_make(0, 0);
    for (int i = 0; i < phi_q; ++i) {
        Complex term = complex_mul(char_table[1][i], complex_conj(char_table[2][i]));
        sum.real += term.real;
        sum.imag += term.imag;
    }
    printf("\nСкалярний добуток <χ_1, χ_2> = (%.2f, %.2f) [очікується (0.00, 0.00)]\n",
           sum.real, sum.imag);

    for (int k = 0; k < phi_q; ++k) free(char_table[k]);
    free(char_table);
    free(discrete_log);
    return 0;
}
