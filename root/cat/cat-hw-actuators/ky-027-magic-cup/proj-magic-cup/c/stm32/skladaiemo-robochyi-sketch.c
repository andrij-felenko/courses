// ── «Магічна чаша» на парі KY-027, STM32 HAL (ШІМ — два канали TIM3) ──
// TIM3 налаштовано в CubeMX: Prescaler під 5 кГц, ARR = 255 → CCR = 0..255.
#include "main.h"
#include <stdbool.h>

extern TIM_HandleTypeDef htim3;

#define PORT_S_A  GPIOA          // вихід вимикача чаші A (цифровий вхід)
#define PIN_S_A   GPIO_PIN_0
#define PORT_S_B  GPIOA          // вихід вимикача чаші B
#define PIN_S_B   GPIO_PIN_1
#define CH_L_A    TIM_CHANNEL_1  // світлодіод чаші A — PA6 (TIM3_CH1)
#define CH_L_B    TIM_CHANNEL_2  // світлодіод чаші B — PA7 (TIM3_CH2)

// Який рівень на піні S означає «нахилено»: замкнений вимикач тягне S до землі.
#define TILTED    false

// ── згасання брязкоту (див. вище) ──
typedef struct { GPIO_TypeDef *port; uint16_t pin; bool stable, last_raw; uint32_t changed_at; } Debounced;
#define DEBOUNCE_MS 25u

static void DebounceBegin(Debounced *d, GPIO_TypeDef *port, uint16_t pin) {
    d->port = port; d->pin = pin;
    d->stable = (HAL_GPIO_ReadPin(port, pin) == GPIO_PIN_SET);
    d->last_raw = d->stable; d->changed_at = HAL_GetTick();
}
static bool DebounceRead(Debounced *d) {
    bool raw = (HAL_GPIO_ReadPin(d->port, d->pin) == GPIO_PIN_SET);
    if (raw != d->last_raw) { d->last_raw = raw; d->changed_at = HAL_GetTick(); }
    if (raw != d->stable && (HAL_GetTick() - d->changed_at) >= DEBOUNCE_MS) d->stable = raw;
    return d->stable;
}

// ── спільний рівень переливу ──
static uint8_t level = 128;
#define STEP 3
static void Nudge(int dir) {
    int next = (int)level + dir * STEP;
    if (next < 0) next = 0;
    if (next > 255) next = 255;
    level = (uint8_t)next;
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();               // S обох плат — входи без підтяжки (вона на платі)
    MX_TIM3_Init();

    Debounced swA, swB;
    DebounceBegin(&swA, PORT_S_A, PIN_S_A);
    DebounceBegin(&swB, PORT_S_B, PIN_S_B);
    HAL_TIM_PWM_Start(&htim3, CH_L_A);
    HAL_TIM_PWM_Start(&htim3, CH_L_B);

    while (1) {
        // 1. Чисті стани обох вимикачів (уже без брязкоту).
        bool tiltA = (DebounceRead(&swA) == TILTED);
        bool tiltB = (DebounceRead(&swB) == TILTED);

        // 2. Посунути спільний рівень за нахилом; обидві або жодна → стоїмо.
        if (tiltA && !tiltB)      Nudge(+1);
        else if (tiltB && !tiltA) Nudge(-1);

        // 3. Вивести рівень у порівняльні регістри: сума яскравостей завжди 255.
        __HAL_TIM_SET_COMPARE(&htim3, CH_L_A, level);
        __HAL_TIM_SET_COMPARE(&htim3, CH_L_B, 255 - level);

        HAL_Delay(4);   // такт ≈4 мс → повний перелив за ~340 мс утримання
    }
}
