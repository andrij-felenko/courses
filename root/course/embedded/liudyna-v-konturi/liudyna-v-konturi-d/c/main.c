#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define SIM_TIME_SEC    5.0f
#define DT              0.002f  // Крок дискретизації 2 мс (500 Гц)
#define BUFFER_MAX_LEN  1000

// Кільцевий буфер чистої часової затримки
typedef struct {
    float buffer[BUFFER_MAX_LEN];
    int head;
    int delay_samples;
} DelayQueue;

void delay_queue_init(DelayQueue *q, float delay_sec, float dt) {
    q->head = 0;
    q->delay_samples = (int)(delay_sec / dt);
    if (q->delay_samples >= BUFFER_MAX_LEN) {
        q->delay_samples = BUFFER_MAX_LEN - 1;
    }
    if (q->delay_samples < 1) {
        q->delay_samples = 1;
    }
    for (int i = 0; i < BUFFER_MAX_LEN; ++i) {
        q->buffer[i] = 0.0f;
    }
}

float delay_queue_push_pop(DelayQueue *q, float in_val) {
    q->buffer[q->head] = in_val;
    int read_idx = q->head - q->delay_samples;
    if (read_idx < 0) {
        read_idx += BUFFER_MAX_LEN;
    }
    q->head = (q->head + 1) % BUFFER_MAX_LEN;
    return q->buffer[read_idx];
}

// Модель оператора Макруера: K_p, T_N (нервово-м'язова), T_L (випередження)
typedef struct {
    float K_p;          // Коефіцієнт підсилення пілота
    float T_N;          // Постійна часу м'язів (~0.1 с)
    float T_L;          // Час випередження (~0.2 с)
    float neuromuscular_state;
    float prev_error;
} OperatorModel;

void operator_init(OperatorModel *op, float K_p, float T_N, float T_L) {
    op->K_p = K_p;
    op->T_N = T_N;
    op->T_L = T_L;
    op->neuromuscular_state = 0.0f;
    op->prev_error = 0.0f;
}

float operator_update(OperatorModel *op, float error, float dt) {
    // Lead-компенсація (диференціювання похибки)
    float error_deriv = (error - op->prev_error) / dt;
    op->prev_error = error;
    float desired_cmd = op->K_p * (error + op->T_L * error_deriv);

    // Нервово-м'язовий фільтр 1-го порядку: d(u_nm)/dt = (desired_cmd - u_nm) / T_N
    float alpha = dt / (op->T_N + dt);
    op->neuromuscular_state += alpha * (desired_cmd - op->neuromuscular_state);

    // Обмеження фізичного ходу стіка (-1.0 .. +1.0)
    if (op->neuromuscular_state > 1.0f) op->neuromuscular_state = 1.0f;
    if (op->neuromuscular_state < -1.0f) op->neuromuscular_state = -1.0f;

    return op->neuromuscular_state;
}

// Динаміка кута нахилу апарата: I * d^2(theta)/dt^2 + b * d(theta)/dt = M
typedef struct {
    float angle_rad;        // Поточний кут
    float rate_rad_s;       // Кутова швидкість
    float inertia;          // Момент інерції I (кг*м^2)
    float damping;          // Коефіцієнт в'язкого тертя b
    float torque_gain;      // Ефективність моторів
} VehiclePlant;

void vehicle_init(VehiclePlant *veh, float inertia, float damping, float torque_gain) {
    veh->angle_rad = 0.0f;
    veh->rate_rad_s = 0.0f;
    veh->inertia = inertia;
    veh->damping = damping;
    veh->torque_gain = torque_gain;
}

void vehicle_step(VehiclePlant *veh, float control_torque, float disturbance, float dt) {
    float total_torque = (control_torque * veh->torque_gain) + disturbance - (veh->damping * veh->rate_rad_s);
    float angular_accel = total_torque / veh->inertia;

    veh->rate_rad_s += angular_accel * dt;
    veh->angle_rad += veh->rate_rad_s * dt;
}

// Бортовий контролер: режим Rate або Angle
typedef enum {
    MODE_RATE,
    MODE_ANGLE
} ControlMode;

typedef struct {
    ControlMode mode;
    float kp_angle;
    float kp_rate;
} FlightController;

float fc_update(FlightController *fc, float stick_input, float current_angle, float current_rate) {
    if (fc->mode == MODE_RATE) {
        // У режимі Rate стік задає бажану кутову швидкість (до +-200 град/с)
        float target_rate = stick_input * 3.5f;
        float rate_err = target_rate - current_rate;
        return fc->kp_rate * rate_err;
    } else {
        // У режимі Angle стік задає кут нахилу (до +-30 град)
        float target_angle = stick_input * 0.52f;
        float angle_err = target_angle - current_angle;
        float target_rate = fc->kp_angle * angle_err;
        float rate_err = target_rate - current_rate;
        return fc->kp_rate * rate_err;
    }
}

int main(void) {
    // Тестуємо дві конфігурації:
    // 1. Мала затримка (50 мс) у режимі Rate -> Стійка система
    // 2. Критична затримка (250 мс) у режимі Rate -> PIO розкачка
    const float delays[2] = {0.050f, 0.250f};

    for (int run = 0; run < 2; ++run) {
        float delay_sec = delays[run];
        printf("=== Симуляція: затримка лінка = %.0f мс, режим RATE ===\n", delay_sec * 1000.0f);

        DelayQueue video_delay, rc_delay;
        delay_queue_init(&video_delay, delay_sec * 0.7f, DT); // Відео забирає 70% лагу
        delay_queue_init(&rc_delay, delay_sec * 0.3f, DT);    // RC-лінк забирає 30%

        OperatorModel operator;
        operator_init(&operator, 2.5f, 0.10f, 0.15f);

        VehiclePlant vehicle;
        vehicle_init(&vehicle, 0.02f, 0.05f, 1.2f);

        FlightController fc = { .mode = MODE_RATE, .kp_angle = 6.0f, .kp_rate = 0.4f };

        int total_steps = (int)(SIM_TIME_SEC / DT);
        float max_angle = 0.0f;

        for (int step = 0; step < total_steps; ++step) {
            float t = step * DT;
            // Імпульсне збурення вітру на 0.5 с
            float disturbance = (t >= 0.5f && t <= 0.6f) ? 0.8f : 0.0f;

            // 1. Борт відправляє кут у відеотракт
            float delayed_angle_view = delay_queue_push_pop(&video_delay, vehicle.angle_rad);

            // 2. Оператор бачить помилку на екрані (уставка цілі r = 0)
            float error = 0.0f - delayed_angle_view;
            float stick_cmd = operator_update(&operator, error, DT);

            // 3. Команда стіка летить через RC-лінк
            float delayed_stick_rc = delay_queue_push_pop(&rc_delay, stick_cmd);

            // 4. Політний контролер обчислює момент моторів
            float motor_torque = fc_update(&fc, delayed_stick_rc, vehicle.angle_rad, vehicle.rate_rad_s);

            // 5. Крок фізики апарата
            vehicle_step(&vehicle, motor_torque, disturbance, DT);

            if (fabsf(vehicle.angle_rad) > max_angle) {
                max_angle = fabsf(vehicle.angle_rad);
            }

            if (step % 250 == 0) {
                printf("  Час %4.2f c | Кут: %6.2f град | Стік: %5.2f\n",
                       t, vehicle.angle_rad * 57.295f, stick_cmd);
            }
        }

        if (max_angle > 1.2f) {
            printf("  -> РЕЗУЛЬТАТ: ВИНИКЛА РОЗКАЧКА PIO! Макс нахил: %.1f град.\n\n", max_angle * 57.295f);
        } else {
            printf("  -> РЕЗУЛЬТАТ: Контур стійкий. Коливання згасли.\n\n");
        }
    }

    return 0;
}
