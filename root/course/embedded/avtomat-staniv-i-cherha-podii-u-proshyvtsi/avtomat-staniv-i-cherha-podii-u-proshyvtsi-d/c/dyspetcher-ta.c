#include <stdint.h>
#include <stdbool.h>

// Макрос засинання для ARM Cortex-M
#ifndef __WFI
#define __WFI() __asm volatile("wfi")
#endif

extern EventQueue g_queue;
extern EvseController g_evse;

int main(void) {
    // Ініціалізація апаратних периферійних вузлів
    // hardware_init();
    // evse_fsm_init(&g_evse);
    event_queue_init(&g_queue);

    while (1) {
        Event evt;
        if (event_queue_pop(&g_queue, &evt)) {
            // Диспетчеризація події у відповідний автомат
            // evse_fsm_dispatch(&g_evse, (FsmEvent)evt.id);
        } else {
            // Черга порожня: засинаємо до наступного апаратного переривання
            __WFI();
        }
    }
}
