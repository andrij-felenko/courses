#include "driver/ledc.h"

#define PEAK_MS    60              // повний струм: тривалість кидка на втягування
#define HOLD_DUTY  90              // утримання: шпаруватість 0..255 (~35% повного струму)

typedef enum { SOL_IDLE, SOL_PEAK, SOL_HOLD } sol_state_t;
static sol_state_t sol_state = SOL_IDLE;
static uint32_t    sol_start = 0;

static void sol_duty(uint32_t duty) {          // канал LEDC уже налаштовано, шкала 0..255
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

void solenoid_engage(void) {       // почати «втягнути й тримати»
    sol_duty(255);                 // ФАЗА 1: повний струм — рвемо осердя через щілину
    sol_state = SOL_PEAK;
    sol_start = now_ms();
}

void solenoid_release(void) {      // відпустити зовсім
    sol_duty(0);
    sol_state = SOL_IDLE;
}

void solenoid_update(void) {
    if (sol_state == SOL_PEAK && (now_ms() - sol_start >= PEAK_MS)) {
        sol_duty(HOLD_DUTY);       // ФАЗА 2: осердя втягнуте — переходимо на знижений струм
        sol_state = SOL_HOLD;      // тепер тримаємо холодно, скільки треба
    }
}
