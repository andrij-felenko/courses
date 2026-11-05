#include <stdio.h>
#include <stdint.h>

static uint32_t simulated_primask = 0;

uint32_t enter_critical_section(void) {
    uint32_t old_primask = simulated_primask;
    simulated_primask = 1; // Simulate __disable_irq() / CPSID i
    return old_primask;
}

void exit_critical_section(uint32_t saved_primask) {
    simulated_primask = saved_primask; // Restore __set_PRIMASK(saved_primask)
}

int main(void) {
    printf("=== Bare-metal & RTOS Critical Section Management (C) ===\n");

    uint32_t saved = enter_critical_section();
    printf("Critical Section Entered (PRIMASK=%u)\n", simulated_primask);

    // Protected operations on hardware registers
    printf("Modifying shared hardware registers safely...\n");

    exit_critical_section(saved);
    printf("Critical Section Exited (PRIMASK=%u)\n", simulated_primask);

    return 0;
}
