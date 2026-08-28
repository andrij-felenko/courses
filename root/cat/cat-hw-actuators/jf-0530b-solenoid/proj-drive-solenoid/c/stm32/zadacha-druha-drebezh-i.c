#define PULSE_MS  60               // тривалість самого клацання
#define REARM_MS  200              // мертвий час: раніше — не клацаємо повторно

static bool     solOn      = false;
static uint32_t solStart   = 0;
static uint32_t solLastEnd = 0;    // коли завершилося останнє клацання

// повертає true, якщо клацання прийнято; false — якщо відкинуто (ще рано)
bool Solenoid_TryFire(void) {
    if (solOn) return false;                               // уже клацаємо — не чіпати
    if (HAL_GetTick() - solLastEnd < REARM_MS) return false; // ще не перезарядилися
    HAL_GPIO_WritePin(SOL_GPIO_Port, SOL_Pin, GPIO_PIN_SET);
    solOn    = true;
    solStart = HAL_GetTick();
    return true;
}

void Solenoid_Update(void) {
    if (solOn && (HAL_GetTick() - solStart >= PULSE_MS)) {
        HAL_GPIO_WritePin(SOL_GPIO_Port, SOL_Pin, GPIO_PIN_RESET);
        solOn      = false;
        solLastEnd = HAL_GetTick();  // запускаємо відлік перезарядки
    }
}
