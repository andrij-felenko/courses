#include <stdint.h>
#include <stdbool.h>

/* Структура регістрів базового таймера STM32 (CMSIS-сумісна) */
typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMCR;
    volatile uint32_t DIER;
    volatile uint32_t SR;
    volatile uint32_t EGR;
    volatile uint32_t CCMR1;
    volatile uint32_t CCMR2;
    volatile uint32_t CCER;
    volatile uint32_t CNT;
    volatile uint32_t PSC;
    volatile uint32_t ARR;
} TimerRegs;

/* Конфігурація та стан драйвера енкодера */
typedef struct {
    TimerRegs* tim;
    uint32_t ppr;               /* Кількість ліній на оберт (Pulses Per Revolution) */
    uint32_t counts_per_rev;    /* PPR * 4 для режиму X4 */
    uint16_t last_cnt;          /* Попереднє значення апаратного CNT */
    int64_t total_position;     /* Накопичена 64-бітна абсолютна позиція */
    float velocity_rad_s;       /* Фільтрована кутова швидкість у рад/с */
    float lpf_alpha;            /* Коефіцієнт експоненційного фільтра швидкості */
} EncoderDriverC;

/* Ініціалізація таймера в апаратному квадратурному режимі X4 */
void encoder_init(EncoderDriverC* enc, TimerRegs* tim, uint32_t ppr, float cutoff_hz, float dt) {
    enc->tim = tim;
    enc->ppr = ppr;
    enc->counts_per_rev = ppr * 4;
    enc->last_cnt = 0;
    enc->total_position = 0;
    enc->velocity_rad_s = 0.0f;

    /* Розрахунок коефіцієнта фільтра низьких частот: alpha = dt / (dt + RC) */
    if (cutoff_hz > 0.0f) {
        float rc = 1.0f / (2.0f * 3.1415926535f * cutoff_hz);
        enc->lpf_alpha = dt / (dt + rc);
    } else {
        enc->lpf_alpha = 1.0f;
    }

    /* 1. Вимикаємо таймер перед налаштуванням */
    tim->CR1 = 0;

    /* 2. Конфігурація вхідних каналів у регістрі CCMR1:
     *    CC1S = 01 (вхід TI1 підключено до IC1)
     *    CC2S = 01 (вхід TI2 підключено до IC2)
     *    IC1F = 0011 (цифровий фільтр: 8 вибірок f_CK_INT)
     *    IC2F = 0011 (цифровий фільтр: 8 вибірок f_CK_INT)
     */
    tim->CCMR1 = (0x1 << 0) | (0x3 << 4) | (0x1 << 8) | (0x3 << 12);

    /* 3. Полярність вхідних сигналів у CCER:
     *    CC1P = 0, CC1NP = 0 (неінвертований, наростання)
     *    CC2P = 0, CC2NP = 0 (неінвертований, наростання)
     */
    tim->CCER = 0;

    /* 4. Конфігурація веденого режиму в SMCR:
     *    SMS[2:0] = 011 (Encoder Mode 3: рахунок по всіх фронтах TI1 та TI2 — X4)
     */
    tim->SMCR = (0x3 << 0);

    /* 5. Максимальний діапазон рахунку: ARR = 0xFFFF (для 16-бітного таймера) */
    tim->ARR = 0xFFFF;
    tim->PSC = 0; // Передільник вимкнено (коефіцієнт 1)
    tim->CNT = 0;

    /* 6. Запуск таймера: CEN = 1 */
    tim->CR1 |= (1 << 0);
    enc->last_cnt = (uint16_t)tim->CNT;
}

/* Періодичне опитування стану (викликається у високопріоритетному циклі з фіксованим dt) */
void encoder_update(EncoderDriverC* enc, float dt) {
    uint16_t current_cnt = (uint16_t)(enc->tim->CNT);

    /* Обчислення знакового приросту за властивостями доповняльного коду int16_t */
    int16_t delta = (int16_t)(current_cnt - enc->last_cnt);
    enc->last_cnt = current_cnt;

    /* Накопичення 64-бітної координати */
    enc->total_position += delta;

    /* Миттєва швидкість: відліки -> радіани за секунду */
    float instant_velocity = ((float)delta / (float)enc->counts_per_rev) * (2.0f * 3.1415926535f) / dt;

    /* Експоненційне згладжування шуму квантування */
    enc->velocity_rad_s += enc->lpf_alpha * (instant_velocity - enc->velocity_rad_s);
}

/* Отримання поточної абсолютної позиції в радіанах */
float encoder_get_angle_rad(const EncoderDriverC* enc) {
    return ((float)enc->total_position / (float)enc->counts_per_rev) * (2.0f * 3.1415926535f);
}

/* Отримання поточного напрямку безпосередньо з апаратного біта DIR */
bool encoder_is_reversing(const EncoderDriverC* enc) {
    return (enc->tim->CR1 & (1 << 4)) != 0; // Біт 4: DIR
}
