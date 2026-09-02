#include "kalman.h"

#include <math.h>

void kalman_axis_init(KalmanAxis *k, float q_bearing, float q_rate, float r_meas)
{
    k->q_bearing = q_bearing;
    k->q_rate = q_rate;
    k->r_meas = r_meas;
    k->gate2 = 9.0f;          /* три сигми */
    k->body_angle = 0.0f;
    kalman_axis_acquire(k);
}

void kalman_axis_acquire(KalmanAxis *k)
{
    k->bearing = 0.0f;
    k->rate = 0.0f;
    k->P[0][0] = 0.1f;        /* до першого кадру про ціль не відомо нічого */
    k->P[0][1] = 0.0f;
    k->P[1][0] = 0.0f;
    k->P[1][1] = 1.0f;
    k->rejects = 0;
    k->primed = false;
}

void kalman_axis_predict(KalmanAxis *k, float dt, float gyro_rate)
{
    /* Зрив таймера чи стрибок годинника — крок пропускаємо цілком: інакше
     * dt у кілька секунд рознесе коваріацію так, що фільтр повірить першому
     * ж хибному кадру. */
    if (!(dt > 0.0f) || dt > 0.5f) {
        return;
    }

    if (isfinite(gyro_rate)) {
        k->body_angle += gyro_rate * dt;
    }

    if (!k->primed) {
        return;
    }

    /* Модель сталої швидкості: x = F·x, F = [[1, dt], [0, 1]] */
    k->bearing += k->rate * dt;

    /* P = F·P·Fᵀ + Q·dt */
    const float p00 = k->P[0][0] + dt * (k->P[1][0] + k->P[0][1])
                    + dt * dt * k->P[1][1] + k->q_bearing * dt;
    const float p01 = k->P[0][1] + dt * k->P[1][1];
    const float p10 = k->P[1][0] + dt * k->P[1][1];
    const float p11 = k->P[1][1] + k->q_rate * dt;

    k->P[0][0] = p00;
    k->P[0][1] = p01;
    k->P[1][0] = p10;
    k->P[1][1] = p11;
}

bool kalman_axis_update(KalmanAxis *k, float los_angle, float body_at_capture, float latency_s)
{
    if (!isfinite(los_angle) || !isfinite(body_at_capture)) {
        return false;
    }

    /* Кут візування плюс ракурс апарата на момент експозиції = пеленг цілі
     * у нерухомій рамці. Далі фільтр працює з величиною, яка від маневрів
     * самого апарата не залежить узагалі. */
    const float z = los_angle + body_at_capture;

    if (!k->primed) {
        k->bearing = z;
        k->rate = 0.0f;
        k->primed = true;
        k->rejects = 0;
        return true;
    }

    /* Стан стоїть на «тепер», а кадр знято latency_s тому: інновацію рахуємо
     * проти стану, відкоченого назад на затримку. */
    if (!(latency_s > 0.0f) || latency_s > 1.0f) {
        latency_s = 0.0f;
    }
    const float prior = k->bearing - k->rate * latency_s;
    const float y = z - prior;

    const float S = k->P[0][0] + k->r_meas;
    if (!(S > 1e-9f)) {
        return false;
    }

    /* Гейт інновації. Детектор час від часу перестрибує на сусідній об'єкт;
     * такий кадр ламає і оцінку швидкості, і похідну регулятора. Але коли
     * промахів набралося поспіль — помиляється не детектор, а фільтр: ціль
     * маневрувала, і оцінку треба засівати наново. */
    if (y * y > k->gate2 * S) {
        if (++k->rejects >= 5) {
            k->bearing = z;
            k->rate = 0.0f;
            k->P[0][0] = 0.1f;
            k->P[0][1] = 0.0f;
            k->P[1][0] = 0.0f;
            k->P[1][1] = 1.0f;
            k->rejects = 0;
        }
        return false;
    }
    k->rejects = 0;

    const float k0 = k->P[0][0] / S;
    const float k1 = k->P[1][0] / S;

    k->bearing += k0 * y;
    k->rate += k1 * y;

    /* P = (I − K·H)·P, H = [1 0] */
    const float p00 = (1.0f - k0) * k->P[0][0];
    const float p01 = (1.0f - k0) * k->P[0][1];
    const float p10 = k->P[1][0] - k1 * k->P[0][0];
    const float p11 = k->P[1][1] - k1 * k->P[0][1];

    k->P[0][0] = p00;
    k->P[0][1] = p01;
    k->P[1][0] = p10;
    k->P[1][1] = p11;
    return true;
}

float kalman_axis_extrapolate(const KalmanAxis *k, float lead_s)
{
    /* Назад у рамку тіла: пеленг мінус поточний ракурс апарата. */
    return (k->bearing + k->rate * lead_s) - k->body_angle;
}

float kalman_axis_body_angle(const KalmanAxis *k)
{
    return k->body_angle;
}

float kalman_axis_rate(const KalmanAxis *k)
{
    return k->rate;
}
