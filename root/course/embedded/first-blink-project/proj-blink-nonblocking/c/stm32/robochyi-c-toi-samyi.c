#include <stdbool.h>
#include "main.h"                    // LED_GPIO_Port / LED_Pin з CubeMX

#define INTERVAL 200                 // період перемикання, мілісекунди

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();                  // ніжка на вихід — один раз, у генерованому коді

    uint32_t lastToggle = 0;         // мітка часу останнього перемикання
    bool ledOn = false;              // нинішній стан світлодіода

    while (1) {
        uint32_t now = HAL_GetTick();   // «зиркнули на годинник» — раз за оберт

        if (now - lastToggle >= INTERVAL) {
            lastToggle = now;        // ПЕРЕСУНУЛИ мітку на теперішній час
            ledOn = !ledOn;          // перемкнули логічний стан
            HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin,
                              ledOn ? GPIO_PIN_SET : GPIO_PIN_RESET);
        }

        // сюди керування доходить ЩОРАЗУ — і між перемиканнями теж.
        // тут можна робити будь-що інше: читати кнопку, опитувати давач…
    }
}
