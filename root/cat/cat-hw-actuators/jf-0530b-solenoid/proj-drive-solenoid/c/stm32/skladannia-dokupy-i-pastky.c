// ── Повний драйвер JF-0530B на STM32 HAL: клацання АБО «втягнути-й-тримати» ─
extern TIM_HandleTypeDef htim3;     // TIM3_CH1 на ніжці соленоїда, ARR = 255

#define SOL_CH      TIM_CHANNEL_1
#define PEAK_MS     60              // повний струм на втягування
#define HOLD_DUTY   90              // ШІМ-утримання (0..255), добрати під примірник
#define REARM_MS    200             // мертвий час між клацаннями (дребезг + фізика + тепло)
#define MAX_ON_MS   30000           // абсолютна стеля утримання (страхувальник від бага)

typedef enum { SOL_IDLE, SOL_PEAK, SOL_HOLD } SolState;
static SolState solState   = SOL_IDLE;
static uint32_t solStart   = 0;     // мить старту поточного вмикання
static uint32_t solLastEnd = 0;     // мить кінця останнього вмикання
static bool     holdMode   = false; // true → після PEAK лишаємось у HOLD

static void Sol_Duty(uint32_t duty) {           // 256 (> ARR) = 100%, 0 = вимкнено
    __HAL_TIM_SET_COMPARE(&htim3, SOL_CH, duty);
}

void Solenoid_Setup(void) {
    Sol_Duty(0);
    HAL_TIM_PWM_Start(&htim3, SOL_CH);          // канал крутиться завжди, керуємо CCR
}

static bool Sol_Begin(bool hold) {  // спільний старт обох режимів
    if (solState != SOL_IDLE) return false;
    if (HAL_GetTick() - solLastEnd < REARM_MS) return false;
    Sol_Duty(256);                  // повний кидок
    solState = SOL_PEAK; holdMode = hold; solStart = HAL_GetTick();
    return true;
}

bool Solenoid_Pulse(void) { return Sol_Begin(false); }  // одиночне клацання
bool Solenoid_Hold(void)  { return Sol_Begin(true);  }  // втягнути й ТРИМАТИ

void Solenoid_Release(void) {
    Sol_Duty(0);
    if (solState != SOL_IDLE) solLastEnd = HAL_GetTick();
    solState = SOL_IDLE;
}

void Solenoid_Update(void) {        // кликати щопрохід головного циклу
    switch (solState) {
        case SOL_PEAK:
            if (HAL_GetTick() - solStart >= PEAK_MS) {
                if (holdMode) { Sol_Duty(HOLD_DUTY); solState = SOL_HOLD; }
                else          { Solenoid_Release(); }     // одиночний клац завершено
            }
            break;
        case SOL_HOLD:
            if (HAL_GetTick() - solStart >= MAX_ON_MS)    // стеля: тримають задовго — рубаємо
                Solenoid_Release();
            break;
        default: break;
    }
}
