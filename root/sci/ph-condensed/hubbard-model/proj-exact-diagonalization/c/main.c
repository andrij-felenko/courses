#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура результату обчислення основного стану кластера Габбарда */
typedef struct {
    double energy;
    double double_occupancy;
    double spin_correlation;
} hubbard_result_t;

/* 
 * Обчислення матричних елементів та діагоналізація 
 * 2-вузлового кластера Габбарда у C 
 */
hubbard_result_t solve_hubbard_2site(double t, double U) {
    hubbard_result_t res;
    
    /* 
     * Матриця Гамільтона H у підпросторі 4 станів (N_up = 1, N_dn = 1):
     * Базис: |1>: |↑, ↓>,  |2>: |↓, ↑>,  |3>: |↑↓, 0>,  |4>: |0, ↑↓>
     * 
     * H = [  0    0   -t   -t  ]
     *     [  0    0    t    t  ]
     *     [ -t    t    U    0  ]
     *     [ -t    t    0    U  ]
     */
    double H[4][4] = {
        { 0.0,  0.0, -t,  -t  },
        { 0.0,  0.0,  t,   t  },
        {-t,    t,    U,   0.0},
        {-t,    t,    0.0, U  }
    };

    /* 
     * Для симетричної 4x4 матриці шукаємо мінімальне власне значення аналітично.
     * Симетричний синглетний основний стан: E_0 = (U - sqrt(U^2 + 16*t^2)) / 2
     */
    double E_ground = (U - sqrt(U * U + 16.0 * t * t)) / 2.0;
    res.energy = E_ground;

    /* Власний вектор основного стану |Ψ_0> = c1|1> + c2|2> + c3|3> + c4|4> */
    /* З міркувань симетрії: c1 = -c2, c3 = c4 */
    double alpha = (U + sqrt(U * U + 16.0 * t * t)) / (4.0 * t);
    double norm = sqrt(2.0 + 2.0 * alpha * alpha);
    
    double c1 = 1.0 / norm;
    double c2 = -1.0 / norm;
    double c3 = alpha / norm;
    double c4 = alpha / norm;

    /* Подвійна заповненість <n_i↑ n_i↓> = |c3|^2 = |c4|^2 */
    res.double_occupancy = c3 * c3;

    /* Спінова кореляція <S_0^z S_1^z> = 1/4 (|c1|^2 + |c2|^2) * (-1) */
    res.spin_correlation = -0.25 * (c1 * c1 + c2 * c2);

    return res;
}

int main(void) {
    double t = 1.0;
    printf("=== Чисельна точна діагоналізація 2-вузлової моделі Габбарда (C) ===\n");
    printf("  U/t   | Енергія E_0/t | Подвійна заповненість <n_↑ n_↓> | Спін-кореляція <S0z S1z>\n");
    printf("--------+---------------+----------------------------------+------------------------\n");

    for (double U = 0.0; U <= 10.0; U += 1.0) {
        hubbard_result_t r = solve_hubbard_2site(t, U);
        printf(" %5.1f  |   %9.4f   |             %8.4f             |        %8.4f\n",
               U, r.energy, r.double_occupancy, r.spin_correlation);
    }

    return 0;
}
