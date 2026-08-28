#include <cstdint>

#ifndef __WFI
#define __WFI() __asm volatile("wfi")
#endif

extern EventQueue<Event, 16> g_event_queue;
extern EvseController g_evse_controller;

int main() {
    // hardware_init();

    while (true) {
        if (auto evt = g_event_queue.pop()) {
            g_evse_controller.dispatch(static_cast<FsmEvent>(evt->id));
        } else {
            // Сон до спрацьовування будь-якого переривання
            __WFI();
        }
    }
}
