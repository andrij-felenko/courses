#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define INITIAL_N0 100000
#define NUM_STEPS  100
#define DT         0.1

/* Моделювання розпаду одиночного ізотопу */
void simulate_single_decay(double half_life) {
    double lambda = log(2.0) / half_life;
    double p_decay = 1.0 - exp(-lambda * DT);
    long current_N = INITIAL_N0;

    printf("=== Симуляція розпаду (C) ===\n");
    printf("T1/2 = %.2f с, lambda = %.4f с^-1, N0 = %d\n", half_life, lambda, INITIAL_N0);
    printf("Час (с) | Симуляція N(t) | Аналітичне N(t) | Похибка (%%)\n");
    printf("----------------------------------------------------------\n");

    for (int step = 0; step <= NUM_STEPS; step += 10) {
        double t = step * DT;
        double analytic_N = INITIAL_N0 * exp(-lambda * t);
        double err_pct = fabs(current_N - analytic_N) / analytic_N * 100.0;

        printf("%7.2f | %14ld | %15.1f | %10.3f\n", t, current_N, analytic_N, err_pct);

        /* Прокручуємо симуляцію на 10 кроків вперед */
        for (int sub = 0; sub < 10 && step + sub < NUM_STEPS; sub++) {
            long decayed_this_step = 0;
            for (long i = 0; i < current_N; i++) {
                double r = (double)rand() / RAND_MAX;
                if (r < p_decay) {
                    decayed_this_step++;
                }
            }
            current_N -= decayed_this_step;
        }
    }
}

/* Моделювання ланцюга розпаду A -> B -> C (утилізація пам'яті в стилі C) */
void simulate_decay_chain(double hl_A, double hl_B) {
    double lam_A = log(2.0) / hl_A;
    double lam_B = log(2.0) / hl_B;
    double p_A = 1.0 - exp(-lam_A * DT);
    double p_B = 1.0 - exp(-lam_B * DT);

    long n_A = INITIAL_N0;
    long n_B = 0;
    long n_C = 0;

    printf("\n=== Симуляція ланцюга A -> B -> C (C) ===\n");
    printf("T1/2(A) = %.1f с, T1/2(B) = %.1f с\n", hl_A, hl_B);
    printf("Час (с) | N_A (симул) | N_B (симул) | N_B (Бейтман)\n");
    printf("----------------------------------------------------\n");

    for (int step = 0; step <= NUM_STEPS; step++) {
        double t = step * DT;

        /* Аналітичне значення Бейтмана для N_B */
        double bateman_B = INITIAL_N0 * (lam_A / (lam_B - lam_A)) * 
                          (exp(-lam_A * t) - exp(-lam_B * t));

        if (step % 10 == 0) {
            printf("%7.1f | %11ld | %11ld | %13.1f\n", t, n_A, n_B, bateman_B);
        }

        /* Крок симуляції розпаду A */
        long decayed_A = 0;
        for (long i = 0; i < n_A; i++) {
            if (((double)rand() / RAND_MAX) < p_A) decayed_A++;
        }

        /* Крок симуляції розпаду B */
        long decayed_B = 0;
        for (long i = 0; i < n_B; i++) {
            if (((double)rand() / RAND_MAX) < p_B) decayed_B++;
        }

        n_A -= decayed_A;
        n_B += decayed_A - decayed_B;
        n_C += decayed_B;
    }
}

int main(void) {
    srand((unsigned int)time(NULL));
    simulate_single_decay(2.0);    /* T1/2 = 2.0 секунди */
    simulate_decay_chain(4.0, 1.0); /* T1/2(A)=4.0 с, T1/2(B)=1.0 с */
    return 0;
}
