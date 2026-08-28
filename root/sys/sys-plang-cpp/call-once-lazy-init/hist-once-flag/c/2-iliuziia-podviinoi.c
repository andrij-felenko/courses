/* Наївний патерн DCLP мовою C (історичний небезпечний антипатерн) */
#include <pthread.h>
#include <stdlib.h>

typedef struct {
    int coefficients[256];
} MatrixFilter;

MatrixFilter* g_filter = NULL;
pthread_mutex_t g_filter_mtx = PTHREAD_MUTEX_INITIALIZER;

MatrixFilter* get_matrix_filter_broken(void) {
    if (g_filter == NULL) { /* Перша перевірка (без блокування) */
        pthread_mutex_lock(&g_filter_mtx);
        if (g_filter == NULL) { /* Друга перевірка (під замком) */
            MatrixFilter* tmp = (MatrixFilter*)malloc(sizeof(MatrixFilter));
            if (tmp) {
                tmp->coefficients[0] = 100;
                /* Небезпечний запис: процесор може зробити g_filter видимим */
                /* раніше, ніж заповняться дані в структурі tmp! */
                g_filter = tmp;
            }
        }
        pthread_mutex_unlock(&g_filter_mtx);
    }
    return g_filter;
}
