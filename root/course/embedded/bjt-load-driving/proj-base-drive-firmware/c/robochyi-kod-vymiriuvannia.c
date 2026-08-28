#include <stdint.h>
#include <stdbool.h>

// ── Залізо: один таймер лічить із відомою частотою; канал 1 — захоплення
//    фронту з вузла колектора (через дільник/компаратор). ──
#define MEAS_TIMER_HZ   84000000u   // частота лічби таймера, Гц (напр. 84 МГц)
#define MEAS_ARR        0xFFFFu     // 16-біт лічильник

// База ключа керується окремим GPIO (тут — прямий вивід через Rb).
#define BASE_PORT       GPIOB
#define BASE_PIN        GPIO_PIN_5

extern uint32_t now_cnt(void);          // читання TIMx->CNT (лічильник таймера)
extern void     base_drive(bool on);    // виставити рівень бази (через Rb)

static volatile uint16_t g_t_cap   = 0;     // защіпнутий час фронту колектора
static volatile bool     g_captured = false;

// Переривання захоплення: колектор злетів угору (струм зник) — фіксуємо час.
void MEAS_CC_IRQHandler(void)
{
    if (!(MEAS_TIM->SR & TIM_SR_CC1IF)) return;
    g_t_cap    = (uint16_t)MEAS_TIM->CCR1;  // апаратний знімок (знімає й прапор)
    g_captured = true;
}
