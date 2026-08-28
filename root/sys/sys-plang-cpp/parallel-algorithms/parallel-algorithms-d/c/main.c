/* Еквівалент мовою C: ручне потокове виконання з поверненням кодів помилок */
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

typedef struct {
    int id;
    double value;
    int has_value;
    char error_message[64];
} ProcessResultC;

typedef struct {
    const int* inputs;
    ProcessResultC* outputs;
    size_t start;
    size_t end;
} WorkerTask;

void* worker_func(void* arg) {
    WorkerTask* task = (WorkerTask*)arg;
    for (size_t i = task->start; i < task->end; ++i) {
        int x = task->inputs[i];
        task->outputs[i].id = x;
        if (x < 0) {
            task->outputs[i].has_value = 0;
            snprintf(task->outputs[i].error_message, 64, "Від'ємне значення неприпустиме");
        } else if (x == 0) {
            task->outputs[i].has_value = 0;
            snprintf(task->outputs[i].error_message, 64, "Ділення на нуль");
        } else {
            task->outputs[i].value = 100.0 / x;
            task->outputs[i].has_value = 1;
            task->outputs[i].error_message[0] = '\0';
        }
    }
    return NULL;
}
