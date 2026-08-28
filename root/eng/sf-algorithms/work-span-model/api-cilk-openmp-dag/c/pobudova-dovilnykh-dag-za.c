#include <stdio.h>
#include <omp.h>

int compute_step_a(void);
int compute_step_b(void);
int combine_results(int a, int b);

int execute_dag_pipeline(void) {
    int res_a = 0, res_b = 0, res_c = 0;

    #pragma omp parallel
    {
        #pragma omp single
        {
            // Вершина 1: генерує значення res_a
            #pragma omp task depend(out: res_a)
            {
                res_a = compute_step_a();
            }

            // Вершина 2: генерує значення res_b (виконується паралельно з вершиною 1)
            #pragma omp task depend(out: res_b)
            {
                res_b = compute_step_b();
            }

            // Вершина 3: залежить від завершення задач 1 і 2
            #pragma omp task depend(in: res_a, res_b) depend(out: res_c)
            {
                res_c = combine_results(res_a, res_b);
            }

            #pragma omp taskwait
        }
    }
    return res_c;
}
