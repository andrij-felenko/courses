#include <stdint.h>
#include <stdbool.h>

typedef enum {
    STATE_OPEN,
    STATE_APPROACH,
    STATE_CONTACT_DETECT,
    STATE_SQUEEZE,
    STATE_HOLD,
    STATE_STALL_ERROR
} GripperState;

typedef struct {
    GripperState state;
    float current_angle;
    float target_force_n;
    uint32_t state_timer_ms;
} GripperFSM;

// Зовнішні апаратні функції
extern void servo_write_angle(float angle_deg);
extern void servo_detach(void);
extern uint16_t get_filtered_current_ma(void);
extern int16_t get_current_derivative_ma_ms(void);
extern float calculate_force_from_current(float angle, uint16_t current_ma);

#define ANGLE_OPEN_DEG         10.0f
#define ANGLE_MAX_CLOSE_DEG    80.0f
#define STEP_ANGLE_DEG         0.5f
#define BLANKING_TIME_MS       30
#define SQUEEZE_TIMEOUT_MS     350
#define STALL_CURRENT_MAX_MA   750
#define DERIV_THRESHOLD_MA_MS  30

void gripper_fsm_init(GripperFSM *fsm) {
    fsm->state = STATE_OPEN;
    fsm->current_angle = ANGLE_OPEN_DEG;
    fsm->target_force_n = 3.0f; // Номінальне цільове зусилля 3 Ньютони
    fsm->state_timer_ms = 0;
    servo_write_angle(fsm->current_angle);
}

void gripper_start_grasp(GripperFSM *fsm, float force_n) {
    if (fsm->state == STATE_OPEN || fsm->state == STATE_HOLD) {
        fsm->target_force_n = force_n;
        fsm->state = STATE_APPROACH;
        fsm->state_timer_ms = 0;
    }
}

// Викликається у головному циклі кожні 10 мс
void gripper_fsm_update(GripperFSM *fsm, uint32_t dt_ms) {
    fsm->state_timer_ms += dt_ms;
    uint16_t current_ma = get_filtered_current_ma();
    int16_t di_dt = get_current_derivative_ma_ms();

    // Загальний захист від заклинювання для всіх активних станів
    if (fsm->state != STATE_OPEN && fsm->state != STATE_STALL_ERROR) {
        if (current_ma >= STALL_CURRENT_MAX_MA) {
            fsm->state = STATE_STALL_ERROR;
            fsm->current_angle -= 5.0f; // Безпечний відкат
            servo_write_angle(fsm->current_angle);
            servo_detach();
            return;
        }
    }

    switch (fsm->state) {
        case STATE_OPEN:
            // Очікування зовнішньої команди запуску
            break;

        case STATE_APPROACH:
            // Швидкий рух до початкової зони об'єкта
            fsm->current_angle += 2.0f;
            servo_write_angle(fsm->current_angle);
            if (fsm->state_timer_ms >= BLANKING_TIME_MS) {
                fsm->state = STATE_CONTACT_DETECT;
            }
            break;

        case STATE_CONTACT_DETECT:
            // Зближення з контролем похідної струму
            fsm->current_angle += 1.0f;
            servo_write_angle(fsm->current_angle);

            if (di_dt >= DERIV_THRESHOLD_MA_MS) {
                // Зафіксовано початкове торкання деталі
                fsm->state = STATE_SQUEEZE;
                fsm->state_timer_ms = 0;
            } else if (fsm->current_angle >= ANGLE_MAX_CLOSE_DEG) {
                // Предмет не знайдено, губки повністю закрилися
                fsm->state = STATE_OPEN;
                fsm->current_angle = ANGLE_OPEN_DEG;
                servo_write_angle(fsm->current_angle);
            }
            break;

        case STATE_SQUEEZE: {
            // Плавне дотискання дрібними кроками
            fsm->current_angle += STEP_ANGLE_DEG;
            servo_write_angle(fsm->current_angle);

            float current_force = calculate_force_from_current(fsm->current_angle, current_ma);
            if (current_force >= fsm->target_force_n) {
                // Досягнуто цільового зусилля утримання
                fsm->state = STATE_HOLD;
                // Застосування безпечного відкату для розвантаження двигуна
                fsm->current_angle -= 0.8f;
                servo_write_angle(fsm->current_angle);
            } else if (fsm->state_timer_ms >= SQUEEZE_TIMEOUT_MS) {
                // Тайм-аут дотискання — перехід в аварію
                fsm->state = STATE_STALL_ERROR;
                servo_detach();
            }
            break;
        }

        case STATE_HOLD:
            // Стабільне енергоощадне утримання
            // При потребі відкриття за зовнішньою командою повертається в STATE_OPEN
            break;

        case STATE_STALL_ERROR:
            // Блокування до скидання помилки оператором
            break;
    }
}
