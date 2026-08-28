#define MAX_ON_MS  3000              // ГРАНИЦЯ: довше 3 с під струмом не тримаємо НІКОЛИ

static bool     solOn    = false;
static uint32_t solStart = 0;

void Solenoid_On(void) {             // «тримати ввімкненим» (напр. утримувати засувку)
    if (!solOn) {                    // фіксуємо мить старту лише на першому вмиканні
        HAL_GPIO_WritePin(SOL_GPIO_Port, SOL_Pin, GPIO_PIN_SET);
        solStart = HAL_GetTick();
        solOn    = true;
    }
}

void Solenoid_Off(void) {
    HAL_GPIO_WritePin(SOL_GPIO_Port, SOL_Pin, GPIO_PIN_RESET);
    solOn = false;
}

void Solenoid_Update(void) {         // страхувальник: рубає струм, якщо тримають задовго
    if (solOn && (HAL_GetTick() - solStart >= MAX_ON_MS)) {
        Solenoid_Off();              // стеля вичерпана — гасимо примусово
        // тут доречно підняти прапорець помилки / моргнути світлодіодом:
        // хтось тримає соленоїд надто довго — це майже завжди баг логіки
    }
}
