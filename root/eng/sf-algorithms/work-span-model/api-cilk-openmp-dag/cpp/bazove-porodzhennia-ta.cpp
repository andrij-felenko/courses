#include <iostream>
#include <omp.h>

void process_subtask(int id);

void parallel_tree_execution() {
    #pragma omp parallel
    {
        #pragma omp single
        {
            #pragma omp task
            {
                process_subtask(1);
            }

            #pragma omp task
            {
                process_subtask(2);
            }

            #pragma omp taskwait
        }
    }
}
