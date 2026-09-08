#include "PowerMonitor.h"

int main() {
    // Пін D3 — зумер тривоги, D4 — керування затвором MOSFET
    PowerMonitor monitor(3, 4, 450.0f, 5.5f);
    monitor.begin();

    uint32_t simulated_clock_ms = 0;

    // Головний цикл супервізора живлення MB102
    while (simulated_clock_ms < 1000) {
        monitor.update(simulated_clock_ms);

        if (monitor.getState() == ProtectionState::TrippedOverCurrent) {
            // Аварійне повідомлення та очікування скидання
            break;
        }

        simulated_clock_ms += 10;
    }

    return 0;
}
