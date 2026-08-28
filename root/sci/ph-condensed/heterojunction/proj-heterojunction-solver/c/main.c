#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define N 200            /* Кількість вузлів сітки */
#define MAX_ITER 4000    /* Максимальна кількість ітерацій */
#define TOL 1e-6         /* Точність збіжності за потенціалом (В) */

/* Фундаментальні фізичні константи в системі СІ */
static const double Q_E = 1.60217663e-19;     /* Заряд електрона (Кл) */
static const double KB = 1.380649e-23;        /* Константа Больцмана (Дж/К) */
static const double EPS0 = 8.85418781e-12;    /* Діелектрична стала вакууму (Ф/м) */

/* Структура параметрів напівпровідникового матеріалу */
typedef struct {
    double eg;       /* Ширина забороненої зони (еВ) */
    double chi;      /* Спорідненість до електрона (еВ) */
    double epsr;     /* Відносна діелектрична проникність */
    double nc;       /* Ефективна щільність станів у зоні провідності (м^-3) */
    double nd;       /* Концентрація донорів (м^-3) */
} Material;

/* Структура сіткової моделі гетеропереходу */
typedef struct {
    double dz;              /* Крок сітки (м) */
    int k_int;              /* Індекс металургійної межі гетеропереходу */
    double phi[N];          /* Електростатичний потенціал (В) */
    double ec[N];           /* Дно зони провідності E_c (еВ) */
    double n[N];            /* Концентрація електронів (м^-3) */
    double eps[N];          /* Діелектрична проникність у вузлах (Ф/м) */
    double nd[N];           /* Профіль донорного легування (м^-3) */
} HeteroGrid;

/* Ініціалізація фізичних профілів сітки n-AlGaAs / i-GaAs */
int init_grid(HeteroGrid *grid, Material mat1, Material mat2, double total_len_nm) {
    if (!grid) return -1;
    grid->dz = (total_len_nm * 1e-9) / (N - 1);
    grid->k_int = N / 2;

    for (int i = 0; i < N; i++) {
        Material m = (i < grid->k_int) ? mat1 : mat2;
        grid->eps[i] = m.epsr * EPS0;
        grid->nd[i] = m.nd;
        grid->phi[i] = 0.0;
        grid->ec[i] = -m.chi;
        grid->n[i] = 0.0;
    }
    return 0;
}

/* Обчислення інтегрального поверхневого заряду 2DEG (см^-2) */
double compute_2deg_density(const HeteroGrid *grid) {
    double ns_m2 = 0.0;
    for (int i = grid->k_int; i < N; i++) {
        ns_m2 += grid->n[i] * grid->dz;
    }
    return ns_m2 * 1e-4; /* Переведення з м^-2 в см^-2 */
}

/* Розв'язання нелінійного рівняння Пуассона методам Гаусса — Зайделя з релаксацією */
int solve_poisson(HeteroGrid *grid, Material mat1, Material mat2, double temp_k) {
    double vt = (KB * temp_k) / Q_E; /* Тепловий потенціал V_t ≈ 0.0259 В */
    double alpha = 0.08;             /* Коефіцієнт релаксації для стійкості */

    for (int iter = 0; iter < MAX_ITER; iter++) {
        double max_change = 0.0;

        /* Оновлення концентрації електронів n[i] за больцманівським розподілом */
        for (int i = 0; i < N; i++) {
            Material m = (i < grid->k_int) ? mat1 : mat2;
            double ec0 = -m.chi;
            grid->ec[i] = ec0 - grid->phi[i];
            grid->n[i] = m.nc * exp(-grid->ec[i] / vt);
        }

        /* Ітераційний перерахунок потенціалу у внутрішніх вузлах */
        for (int i = 1; i < N - 1; i++) {
            double eps_p = 0.5 * (grid->eps[i] + grid->eps[i + 1]);
            double eps_m = 0.5 * (grid->eps[i] + grid->eps[i - 1]);
            double rho = Q_E * (grid->nd[i] - grid->n[i]);

            double phi_new = (eps_p * grid->phi[i + 1] + eps_m * grid->phi[i - 1] + rho * grid->dz * grid->dz) / (eps_p + eps_m);
            double diff = fabs(phi_new - grid->phi[i]);
            if (diff > max_change) max_change = diff;

            /* Демпфування релаксацією */
            grid->phi[i] = (1.0 - alpha) * grid->phi[i] + alpha * phi_new;
        }

        if (max_change < TOL) {
            printf("Збіжність розв'язку досягнута за %d ітерацій.\n", iter);
            return 0;
        }
    }
    return -2; /* Перевищено ліміт ітерацій */
}

int main(void) {
    /* Параметри матеріалів: N-Al0.3Ga0.7As (широкозонний) та i-GaAs (вузькозонний) */
    Material algaas = { .eg = 1.80, .chi = 3.74, .epsr = 12.2, .nc = 1.5e23, .nd = 1e24 };
    Material gaas   = { .eg = 1.42, .chi = 4.07, .epsr = 13.1, .nc = 4.7e23, .nd = 1e20 };

    HeteroGrid grid;
    if (init_grid(&grid, algaas, gaas, 100.0) != 0) {
        fprintf(stderr, "Помилка ініціалізації сіткової моделі.\n");
        return 1;
    }

    if (solve_poisson(&grid, algaas, gaas, 300.0) != 0) {
        fprintf(stderr, "Помилка: ітераційний процес не збігся.\n");
        return 1;
    }

    double ns_2deg = compute_2deg_density(&grid);

    printf("\n=======================================================\n");
    printf("  Чисельний розрахунок гетеропереходу N-AlGaAs / i-GaAs\n");
    printf("=======================================================\n");
    printf("Поверхнева густина 2DEG каналу (n_s): %.3e см^-2\n\n", ns_2deg);
    printf("z (нм)\t\tEc (еВ)\t\tПотенціал (В)\tn (см^-3)\n");
    printf("-------------------------------------------------------\n");

    for (int i = 0; i < N; i += 15) {
        double z_nm = i * (grid.dz * 1e9);
        printf("%.1f нм\t\t%.3f еВ\t\t%.3f В\t\t%.2e см^-3\n", z_nm, grid.ec[i], grid.phi[i], grid.n[i] * 1e-6);
    }

    return 0;
}
