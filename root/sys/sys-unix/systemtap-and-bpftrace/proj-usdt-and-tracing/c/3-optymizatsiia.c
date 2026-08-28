/* Оптимізована підготовка аргументів мовою C */
#include <sys/sdt.h>
#include <stdlib.h>

unsigned short workpool_task_start_semaphore __attribute__ ((unused)) = 0;

void process_complex_task(int task_id) {
    if (STAP_PROBE_INPUT_ENABLED(workpool, task_start)) {
        /* Обчислюємо дорогі аргументи лише якщо проба активована */
        char *payload = generate_expensive_diagnostics();
        STAP_PROBE1(workpool, task_start, payload);
        free(payload);
    }
}
