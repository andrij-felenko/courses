#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "guidance.h"

/* SIL-перевірка замкненого контуру на синтетичній сходинці.
 *
 * Модель: ціль стрибком з'являється під кутом +15°, апарат стоїть нерухомо.
 * Камера знімає на 30 Гц, кадр доходить до контролера через 100 мс (черга
 * затримки), контур крутиться на 100 Гц, динаміка апарата рахується з кроком
 * 1 мс. Критерії — час установлення, перерегулювання і відсутність
 * автоколивань — узяті з розділу перевірки. */

#define SIM_DT        0.001f      /* крок динаміки, с */
#define CONTROL_EVERY 10          /* контур — кожні 10 кроків, тобто 100 Гц */
#define FRAME_PERIOD_US 33333u    /* 30 кадрів на секунду */
#define CAM_DELAY_US    100000u   /* транспортна затримка кадру */
#define SIM_TIME_S    3.0f

#define STEP_RAD      0.2618f     /* +15° */
#define SETTLE_BAND   (0.05f * STEP_RAD)
#define LIMIT_CYCLE_BAND (0.01f * STEP_RAD)

/* Черга затримки кадрів: N = T_delay / dt_контуру = 100 мс / 10 мс = 10 кроків,
 * місткість із запасом. */
#define DELAY_SLOTS 16u

typedef struct {
    TargetDetection det;
    uint64_t        ready_us;
} DelayedFrame;

typedef struct {
    DelayedFrame slots[DELAY_SLOTS];
    unsigned     head;
    unsigned     tail;
} DelayLine;

static bool delay_push(DelayLine *dl, const TargetDetection *det, uint64_t ready_us)
{
    if (dl->tail - dl->head >= DELAY_SLOTS) {
        return false;
    }
    dl->slots[dl->tail % DELAY_SLOTS].det = *det;
    dl->slots[dl->tail % DELAY_SLOTS].ready_us = ready_us;
    dl->tail++;
    return true;
}

static bool delay_pop_ready(DelayLine *dl, uint64_t now, TargetDetection *out)
{
    if (dl->head == dl->tail) {
        return false;
    }
    const DelayedFrame *f = &dl->slots[dl->head % DELAY_SLOTS];
    if (f->ready_us > now) {
        return false;
    }
    *out = f->det;
    dl->head++;
    return true;
}

/* Детермінований шум детектора: той самий прогін має давати те саме число. */
static uint32_t rng_state = 12345u;

static float pixel_noise(float sigma_px)
{
    rng_state = rng_state * 1664525u + 1013904223u;
    const float a = (float)((rng_state >> 8) & 0xFFFFu) / 65535.0f;
    rng_state = rng_state * 1664525u + 1013904223u;
    const float b = (float)((rng_state >> 8) & 0xFFFFu) / 65535.0f;
    /* сума двох рівномірних — груба, але дешева заміна нормальному */
    return sigma_px * 2.0f * (a + b - 1.0f);
}

int main(void)
{
    const CameraIntrinsics cam = {
        .fx = 800.0f, .fy = 800.0f,
        .cx = 320.0f, .cy = 240.0f,
        .img_width = 640.0f, .img_height = 480.0f,
    };

    VisualGuidance g;
    visual_guidance_init(&g, &cam);

    DelayLine delay = { .head = 0u, .tail = 0u };

    /* Динаміка апарата за рисканням: внутрішній контур відпрацьовує уставку
     * кутової швидкості моментом, аеродинаміка гальмує. */
    const float J = 0.02f;          /* момент інерції, кг·м² */
    const float k_inner = 8.0f;     /* коефіцієнт внутрішнього контуру, 1/с */
    const float d_aero = 0.8f;      /* аеродинамічне демпфування, 1/с */

    float drone_angle = 0.0f;       /* курс апарата, рад */
    float drone_rate = 0.0f;        /* кутова швидкість апарата, рад/с */
    const float target_bearing = STEP_RAD;

    float cmd_rate = 0.0f;
    uint64_t next_frame_us = 0u;
    uint64_t t_us = 0u;

    float settle_time_s = -1.0f;
    float max_angle = 0.0f;
    float tail_min = 1e9f;
    float tail_max = -1e9f;
    unsigned frames_sent = 0u;

    const int steps = (int)(SIM_TIME_S / SIM_DT);
    for (int step = 0; step < steps; ++step) {
        t_us = (uint64_t)step * 1000u;
        const float t_s = (float)step * SIM_DT;
        const float los = target_bearing - drone_angle;

        /* Камера: експозиція кадру, кадр лягає в чергу затримки. */
        if (t_us >= next_frame_us) {
            next_frame_us += FRAME_PERIOD_US;
            const float u = cam.cx + cam.fx * tanf(los) + pixel_noise(1.2f);
            const float v = cam.cy + pixel_noise(1.2f);
            if (u >= 0.0f && u <= cam.img_width) {
                const TargetDetection det = {
                    .u = u, .v = v,
                    .width = 80.0f, .height = 80.0f,
                    .t_capture_us = t_us,
                };
                delay_push(&delay, &det, t_us + CAM_DELAY_US);
                frames_sent++;
            }
            /* Виїзд цілі за край кадру — легітимна відмова детектора:
             * контролер має дожити до таймаута, а не зламатися. */
        }

        /* Доставка кадрів, у яких вийшла затримка. */
        TargetDetection ready;
        while (delay_pop_ready(&delay, t_us, &ready)) {
            visual_guidance_on_detection(&g, &ready);
        }

        /* Крок контуру керування на 100 Гц. */
        if (step % CONTROL_EVERY == 0) {
            GuidanceSetpoints sp;
            visual_guidance_update(&g, t_us, drone_rate, 0.0f, &sp);
            cmd_rate = sp.target_acquired ? sp.yaw_rate_rad_s : 0.0f;
        }

        /* Динаміка: момент від внутрішнього контуру, демпфування, інтегрування. */
        const float torque = J * k_inner * (cmd_rate - drone_rate);
        drone_rate += (torque / J - d_aero * drone_rate) * SIM_DT;
        drone_angle += drone_rate * SIM_DT;

        if (drone_angle > max_angle) {
            max_angle = drone_angle;
        }
        if (fabsf(los) > SETTLE_BAND) {
            settle_time_s = -1.0f;          /* вибили з коридору — відлік наново */
        } else if (settle_time_s < 0.0f) {
            settle_time_s = t_s;
        }
        if (t_s > SIM_TIME_S - 1.0f) {      /* остання секунда — стаціонарний режим */
            if (drone_angle < tail_min) tail_min = drone_angle;
            if (drone_angle > tail_max) tail_max = drone_angle;
        }
    }

    const float overshoot = 100.0f * (max_angle - target_bearing) / target_bearing;
    const float peak_to_peak = tail_max - tail_min;

    const bool ok_settle = (settle_time_s >= 0.0f && settle_time_s < 0.75f);
    const bool ok_overshoot = (overshoot < 12.0f);
    const bool ok_limit = (peak_to_peak < LIMIT_CYCLE_BAND);

    printf("кадрів віддано:      %u (використано %u, відкинуто %u)\n",
           frames_sent, g.frames_used, g.frames_rejected);
    printf("час установлення:    %.3f с   (норма < 0.75)  %s\n",
           (double)settle_time_s, ok_settle ? "ГАРАЗД" : "ЗАВАЛЕНО");
    printf("перерегулювання:     %.2f %%    (норма < 12)    %s\n",
           (double)overshoot, ok_overshoot ? "ГАРАЗД" : "ЗАВАЛЕНО");
    printf("розмах в кінці:      %.5f рад (норма < %.5f) %s\n",
           (double)peak_to_peak, (double)LIMIT_CYCLE_BAND,
           ok_limit ? "ГАРАЗД" : "АВТОКОЛИВАННЯ");

    return (ok_settle && ok_overshoot && ok_limit) ? EXIT_SUCCESS : EXIT_FAILURE;
}
