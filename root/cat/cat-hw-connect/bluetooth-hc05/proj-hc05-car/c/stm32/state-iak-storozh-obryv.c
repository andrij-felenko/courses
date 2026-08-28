#include "main.h"               // STATE модуля → PA0: у CubeMX GPIO_Input, Pull-down
#include <stdbool.h>

#define STATE_PORT  GPIOA
#define STATE_PIN   GPIO_PIN_0

static bool wasConnected = false;

static void statePoll(void) {   // виклик у головному циклі while(1)
    // 1 = є з'єднання, 0 = немає
    bool connected = (HAL_GPIO_ReadPin(STATE_PORT, STATE_PIN) == GPIO_PIN_SET);

    if (wasConnected && !connected) {
        // зв'язок ЩОЙНО обірвався — аварійний стоп
        applyDrive(0, 0);
        printf("Зв'язок втрачено — мотори зупинено.\r\n");   // консоль налагодження
    }
    wasConnected = connected;
}
