#define PERIOD 500U                  // мс
static uint32_t last = 0;
static bool on = false;

while (1) {                          // головний цикл main()
    uint32_t now = HAL_GetTick();
    if (now - last >= PERIOD) {      // настав час?
        last = now;                  // оновили мітку (саме now, не новий виклик)
        on = !on;
        HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, on ? GPIO_PIN_SET : GPIO_PIN_RESET);
    }
    // ... тут крутиться решта коду, нічого не чекаючи ...
}
