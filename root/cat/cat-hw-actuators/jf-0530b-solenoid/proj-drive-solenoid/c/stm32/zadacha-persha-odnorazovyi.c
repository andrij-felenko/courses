#define PULSE_MS  60

static bool     solOn    = false;    // чи зараз соленоїд під струмом
static uint32_t solStart = 0;        // мить увімкнення (HAL_GetTick)

void Solenoid_Start(void) {          // почати клацання — не чекаючи його кінця
    HAL_GPIO_WritePin(SOL_GPIO_Port, SOL_Pin, GPIO_PIN_SET);
    solOn    = true;
    solStart = HAL_GetTick();
}

void Solenoid_Update(void) {         // кликати щопрохід циклу: вимкне, коли настане час
    if (solOn && (HAL_GetTick() - solStart >= PULSE_MS)) {
        HAL_GPIO_WritePin(SOL_GPIO_Port, SOL_Pin, GPIO_PIN_RESET);
        solOn = false;
    }
}

int main(void) {
    HAL_Init();
    MX_GPIO_Init();
    while (1) {
        // ... читаємо кнопки, крутимо логіку, миготимо світлом ...
        if (ButtonPressed())
            Solenoid_Start();        // клац — і одразу далі, без застигання
        Solenoid_Update();           // а вимкнеться саме собою за 60 мс
        // ... решта циклу крутиться весь час, соленоїд їй не заважає ...
    }
}
