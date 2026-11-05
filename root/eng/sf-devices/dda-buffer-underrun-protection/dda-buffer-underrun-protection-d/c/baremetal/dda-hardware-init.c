#include <stdint.h>
#include <stdbool.h>

// Апаратні регістри таймера мікроконтролера
typedef struct {
    volatile uint32_t CR1;   // Керування 1 (біт 7 ARPE: буферизація ARR)
    volatile uint32_t DIER;  // Дозвіл переривань (UIE)
    volatile uint32_t SR;    // Статус прапорців (UIF)
    volatile uint32_t EGR;   // Генерація програмних подій (UEV)
    volatile uint32_t CNT;   // Лічильний регістр
    volatile uint32_t PSC;   // Попередній подільник частоти
    volatile uint32_t ARR;   // Буферизований регістр перезавантаження періоду
    volatile uint32_t CCR1;  // Порівняння каналу 1 (активний імпульс STEP)
} HardwareTimerRegs;

#define TIM_CR1_CEN   (1U << 0)
#define TIM_CR1_ARPE  (1U << 7)
#define TIM_DIER_UIE  (1U << 0)
#define TIM_SR_UIF    (1U << 0)

#define DDA_QUEUE_CAPACITY 64U
#define DDA_QUEUE_MASK     (DDA_QUEUE_CAPACITY - 1U)

typedef struct {
    uint32_t step_interval_ticks;
    uint32_t duration_us;
    uint8_t  dir_bits;
    bool     is_terminal;
} DdaStepPacket;

typedef enum {
    DDA_PROT_IDLE = 0,
    DDA_PROT_NORMAL,
    DDA_PROT_WARNING,
    DDA_PROT_DECELERATING,
    DDA_PROT_UNDERRUN_STOP
} DdaProtectionState;

typedef struct {
    HardwareTimerRegs* timer;
    DdaStepPacket queue[DDA_QUEUE_CAPACITY];
    volatile uint32_t head;
    volatile uint32_t tail;
    volatile uint32_t total_time_avail_us;
    volatile DdaProtectionState state;
    uint32_t warning_threshold_us;
    uint32_t decel_threshold_us;
    uint32_t decel_step_index;
    uint32_t last_period_ticks;
} DdaHardwareDriver;

// Таблиця констант K_Q16 = round((2 / (4*n + 1)) * 65536) для n від 1 до 16
static const uint16_t K_Q16_TAYLOR_TABLE[16] = {
    26214, 14564, 10082, 7710, 6242, 5243, 4520, 3972,
    3542,  3197,  2913,  2675, 2473, 2300, 2149, 2017
};

void dda_hardware_init(DdaHardwareDriver* drv, HardwareTimerRegs* tim, uint32_t psc) {
    drv->timer = tim;
    drv->head = 0;
    drv->tail = 0;
    drv->total_time_avail_us = 0;
    drv->state = DDA_PROT_IDLE;
    drv->warning_threshold_us = 8000;
    drv->decel_threshold_us   = 3000;
    drv->decel_step_index = 0;
    drv->last_period_ticks = 2000;

    tim->CR1 &= ~TIM_CR1_CEN;
    tim->PSC = psc;
    tim->ARR = 2000;
    tim->CCR1 = 50;           // Тривалість імпульсу STEP 2.5 мкс
    tim->CR1 |= TIM_CR1_ARPE; // Активація тіньового регістра ARR
    tim->DIER |= TIM_DIER_UIE;
    tim->EGR |= 1U;           // Примусова генерація UEV для оновлення тіні
}

void dda_timer_update_isr(DdaHardwareDriver* drv) {
    HardwareTimerRegs* tim = drv->timer;
    tim->SR &= ~TIM_SR_UIF;

    if (drv->state == DDA_PROT_UNDERRUN_STOP || drv->state == DDA_PROT_IDLE) {
        tim->CR1 &= ~TIM_CR1_CEN;
        return;
    }

    if (drv->state == DDA_PROT_DECELERATING) {
        if (drv->decel_step_index < 16) {
            uint32_t k = K_Q16_TAYLOR_TABLE[drv->decel_step_index++];
            uint32_t delta = (drv->last_period_ticks * k) >> 16;
            drv->last_period_ticks += delta;
            tim->ARR = drv->last_period_ticks; // Запис у буферизований ARR
        } else {
            drv->state = DDA_PROT_UNDERRUN_STOP;
            tim->CR1 &= ~TIM_CR1_CEN;
        }
        return;
    }

    uint32_t current_tail = drv->tail;
    if (drv->head != current_tail) {
        DdaStepPacket pkt = drv->queue[current_tail];
        drv->tail = (current_tail + 1U) & DDA_QUEUE_MASK;

        drv->total_time_avail_us = (drv->total_time_avail_us >= pkt.duration_us) ?
                                   (drv->total_time_avail_us - pkt.duration_us) : 0;

        drv->last_period_ticks = pkt.step_interval_ticks;
        tim->ARR = pkt.step_interval_ticks;

        if (drv->total_time_avail_us <= drv->decel_threshold_us) {
            drv->state = DDA_PROT_DECELERATING;
            drv->decel_step_index = 0;
        } else if (drv->total_time_avail_us <= drv->warning_threshold_us) {
            drv->state = DDA_PROT_WARNING;
        } else {
            drv->state = DDA_PROT_NORMAL;
        }
    } else {
        drv->state = DDA_PROT_DECELERATING;
        drv->decel_step_index = 0;
    }
}
