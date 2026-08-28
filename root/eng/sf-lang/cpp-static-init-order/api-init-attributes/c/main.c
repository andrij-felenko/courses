#include <stdio.h>

/* Виконується до main() у порядку зростання пріоритетів (150 -> 200) */
void __attribute__((constructor(150))) init_hardware_bus(void) {
    printf("[C HW] Активація системної шини периферії\n");
}

/* Виконується після exit() у порядку спадання пріоритетів (200 -> 150) */
void __attribute__((destructor(150))) shutdown_hardware_bus(void) {
    printf("[C HW] Вимкнення системної шини периферії\n");
}
