#include <stdio.h>
#include <omp.h>

void process_subtask(int id);

void parallel_tree_execution(void) {
    #pragma omp parallel
    {
        #pragma omp single
        {
            // Створення лівої вершини DAG
            #pragma omp task
            {
                process_subtask(1);
            }

            // Створення правої вершини DAG
            #pragma omp task
            {
                process_subtask(2);
            }

            // Точка синхронізації (join-ребро) для прямих дочірніх задач
            #pragma omp taskwait
        }
    }
}
