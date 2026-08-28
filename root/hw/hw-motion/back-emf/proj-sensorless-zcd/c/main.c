#include <stdint.h>
#include <stdbool.h>

#define NUM_COMM_STEPS 6

typedef enum {
    MOTOR_STATE_IDLE = 0,
    MOTOR_STATE_ALIGN,
    MOTOR_STATE_OPEN_LOOP_RAMP,
    MOTOR_STATE_CLOSED_LOOP
} MotorState;

typedef enum {
    ZCD_EDGE_RISING = 0,
    ZCD_EDGE_FALLING
} ZcdEdge;

// Конфігурація 6 кроків комутації (який міст активний, яка фаза вільна)
typedef struct {
    uint8_t high_side_pin;   // Фаза, підтягнута до Vbus (ШІМ)
    uint8_t low_side_pin;    // Фаза, підтягнута до GND
    uint8_t floating_phase;  // Вільна фаза (0=U, 1=V, 2=W)
    ZcdEdge expected_edge;   // Очікуваний напрям перетину нуля
} StepConfig;

static const StepConfig SIX_STEP_TABLE[NUM_COMM_STEPS] = {
    {0, 1, 2, ZCD_EDGE_RISING},   // Крок 0: U+, V-, W вільна (наростання)
    {0, 2, 1, ZCD_EDGE_FALLING},  // Крок 1: U+, W-, V вільна (спад)
    {1, 2, 0, ZCD_EDGE_RISING},   // Крок 2: V+, W-, U вільна (наростання)
    {1, 0, 2, ZCD_EDGE_FALLING},  // Крок 3: V+, U-, W вільна (спад)
    {2, 0, 1, ZCD_EDGE_RISING},   // Крок 4: W+, U-, V вільна (наростання)
    {2, 1, 0, ZCD_EDGE_FALLING}   // Крок 5: W+, V-, U вільна (спад)
};

typedef struct {
    MotorState state;
    uint8_t current_step;
    uint32_t last_comm_time_us;     // Час останнього перемикання ключів
    uint32_t step_duration_us;       // Тривалість останнього кроку 60°
    uint32_t blanking_time_us;      // Час маскування викиду індуктивності
    bool zcd_detected;
    uint16_t zcd_valid_count;
    uint32_t open_loop_delay_us;
} BldcController;

// Апаратні заглушки під платформу (STM32 / ESP32)
void hw_set_inverter_step(uint8_t step);
void hw_set_pwm_duty(uint16_t duty);
void hw_select_comparator_phase(uint8_t phase_index);
void hw_schedule_timer_interrupt(uint32_t delay_us);
uint32_t hw_get_micros(void);

void bldc_init(BldcController *ctrl) {
    ctrl->state = MOTOR_STATE_IDLE;
    ctrl->current_step = 0;
    ctrl->last_comm_time_us = 0;
    ctrl->step_duration_us = 2000;
    ctrl->blanking_time_us = 400;
    ctrl->zcd_detected = false;
    ctrl->zcd_valid_count = 0;
    ctrl->open_loop_delay_us = 5000;
}

// Запуск розгону мотора
void bldc_start(BldcController *ctrl) {
    ctrl->state = MOTOR_STATE_ALIGN;
    ctrl->current_step = 0;
    hw_set_pwm_duty(300); // 30% струму для початкової фіксації
    hw_set_inverter_step(0);
    hw_schedule_timer_interrupt(50000); // 50 мс на вирівнювання ротора
}

// Перемикання на наступний сектор 60°
void bldc_advance_commutation(BldcController *ctrl) {
    uint32_t now = hw_get_micros();
    ctrl->step_duration_us = now - ctrl->last_comm_time_us;
    ctrl->last_comm_time_us = now;

    // Перехід на наступний крок таблиці
    ctrl->current_step = (ctrl->current_step + 1) % NUM_COMM_STEPS;
    hw_set_inverter_step(ctrl->current_step);

    // Маскування комутаційного викиду: перші 20% часу кроку
    ctrl->blanking_time_us = ctrl->step_duration_us / 5;
    if (ctrl->blanking_time_us < 20) {
        ctrl->blanking_time_us = 20; // Мінімум 20 мкс на спад струму діода
    }

    ctrl->zcd_detected = false;

    // Підключення компаратора до нової вільної фази
    uint8_t free_phase = SIX_STEP_TABLE[ctrl->current_step].floating_phase;
    hw_select_comparator_phase(free_phase);
}

// Обробник переривання апаратного компаратора / детектора нуля
void bldc_on_comparator_event(BldcController *ctrl) {
    if (ctrl->state != MOTOR_STATE_CLOSED_LOOP) {
        return;
    }

    uint32_t elapsed = hw_get_micros() - ctrl->last_comm_time_us;

    // Захист: ігноруємо події всередині вікна маскування демагнетизації
    if (elapsed < ctrl->blanking_time_us) {
        return;
    }

    if (!ctrl->zcd_detected) {
        ctrl->zcd_detected = true;

        // Затримка 30° електричних: половина тривалості поточного сектора
        uint32_t delay_30deg_us = elapsed; // Час від початку кроку до ZCD і є ~30°
        if (delay_30deg_us > 10) {
            // Компенсація фазової затримки RC-фільтра (~15 мкс)
            uint32_t rc_filter_lag_us = 15;
            if (delay_30deg_us > rc_filter_lag_us) {
                delay_30deg_us -= rc_filter_lag_us;
            }
            hw_schedule_timer_interrupt(delay_30deg_us);
        } else {
            bldc_advance_commutation(ctrl);
        }
    }
}

// Періодичний таймер керування станом мотора
void bldc_on_timer_callback(BldcController *ctrl) {
    switch (ctrl->state) {
        case MOTOR_STATE_ALIGN:
            ctrl->state = MOTOR_STATE_OPEN_LOOP_RAMP;
            ctrl->open_loop_delay_us = 4000;
            bldc_advance_commutation(ctrl);
            hw_schedule_timer_interrupt(ctrl->open_loop_delay_us);
            break;

        case MOTOR_STATE_OPEN_LOOP_RAMP:
            bldc_advance_commutation(ctrl);
            // Прискорення розгону наосліп
            if (ctrl->open_loop_delay_us > 800) {
                ctrl->open_loop_delay_us -= 100;
                hw_schedule_timer_interrupt(ctrl->open_loop_delay_us);
            } else {
                // Перехід у замкнений контур
                ctrl->state = MOTOR_STATE_CLOSED_LOOP;
                ctrl->last_comm_time_us = hw_get_micros();
            }
            break;

        case MOTOR_STATE_CLOSED_LOOP:
            // Спрацював таймер 30° затримки після ZCD -> час комутації
            bldc_advance_commutation(ctrl);
            break;

        default:
            break;
    }
}
