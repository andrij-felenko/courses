extern TIM_HandleTypeDef htim3;    // канал ШІМ на ніжці соленоїда, ARR = 255

#define SOL_CH     TIM_CHANNEL_1
#define PEAK_MS    60              // повний струм: тривалість кидка на втягування
#define HOLD_DUTY  90              // утримання: шпаруватість 0..255 (~35% повного струму)

typedef enum { SOL_IDLE, SOL_PEAK, SOL_HOLD } SolState;
static SolState solState = SOL_IDLE;
static uint32_t solStart = 0;

static void Sol_Duty(uint32_t duty) {          // 256 (> ARR) — суцільний рівень, 0 — вимкнено
    __HAL_TIM_SET_COMPARE(&htim3, SOL_CH, duty);
}

void Solenoid_Engage(void) {       // почати «втягнути й тримати»
    Sol_Duty(256);                 // ФАЗА 1: повний струм — рвемо осердя через щілину
    solState = SOL_PEAK;
    solStart = HAL_GetTick();
}

void Solenoid_Release(void) {      // відпустити зовсім
    Sol_Duty(0);
    solState = SOL_IDLE;
}

void Solenoid_Update(void) {
    if (solState == SOL_PEAK && (HAL_GetTick() - solStart >= PEAK_MS)) {
        Sol_Duty(HOLD_DUTY);       // ФАЗА 2: осердя втягнуте — переходимо на знижений струм
        solState = SOL_HOLD;       // тепер тримаємо холодно, скільки треба
    }
}
