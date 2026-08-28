#include <iostream>
#include <omp.h>

int compute_step_a();
int compute_step_b();
int combine_results(int a, int b);

int execute_dag_pipeline() {
    int res_a = 0;
    int res_b = 0;
    int res_c = 0;

    #pragma omp parallel
    {
        #pragma omp single
        {
            #pragma omp task depend(out: res_a)
            {
                res_a = compute_step_a();
            }

            #pragma omp task depend(out: res_b)
            {
                res_b = compute_step_b();
            }

            #pragma omp task depend(in: res_a, res_b) depend(out: res_c)
            {
                res_c = combine_results(res_a, res_b);
            }

            #pragma omp taskwait
        }
    }
    return res_c;
}
