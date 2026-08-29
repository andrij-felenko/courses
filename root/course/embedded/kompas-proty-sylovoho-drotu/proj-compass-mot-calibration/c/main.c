/* main.c — стендовий прогін Compass-Mot на моделі апарата.
 *
 * Замість плати тут крутиться модель стенда: газ → струм (з інерцією
 * силової частини) → поле на магнітометрі (з групою затримки дециматора)
 * плюс шум. Так видно і роботу автомата, і те, ЩО саме він виміряв:
 * істинні k_true нам відомі, тож наприкінці можна порівняти.
 *
 * На платі змінюється рівно одне: rig_* міняються на драйвери шунта,
 * магнітометра, ESC і EEPROM. Автомат і регресія лишаються ті самі.
 */
#include "calib_fsm.h"
#include "compass_mot.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define DT_MS        10u
#define DT_SEC       0.010f
#define CURRENT_LPF_HZ 12.0f     /* §5: нижче зрізу — нема тонких піків */
#define PARAM_FILE   "compass_mot.params"

/* ---------------------------------------------------------------- */
/* Модель стенда                                                     */
/* ---------------------------------------------------------------- */

typedef struct {
    float  throttle_pct;
    float  current_a;        /* фактичний струм силової шини        */
    vec3_t b_earth;          /* геомагнітне поле в місці стенда     */
    vec3_t k_true;           /* істинна чутливість, мкТл/А          */
    vec3_t b_lagged;         /* поле на виході дециматора компаса   */
    float  i_full_a;         /* струм при 100% газу                 */
    float  shunt_offset_a;   /* зсув нуля шунта                     */
    uint32_t rng;
} rig_t;

static float rig_noise(rig_t *r, float amp)
{
    r->rng = r->rng * 1664525u + 1013904223u;
    const float u = (float)((r->rng >> 8) & 0xFFFFu) / 65535.0f;
    return (u - 0.5f) * 2.0f * amp;
}

/* Один такт фізики стенда. */
static void rig_tick(rig_t *r)
{
    /* Тяга і струм ідуть за квадратом газу — звідси нелінійність по газу
     * і лінійність по струму, заради якої модель будують саме на I. */
    const float duty = r->throttle_pct / 100.0f;
    const float target = r->i_full_a * duty * duty;

    /* Інерція обертів і ємність силової шини: струм не стрибає миттєво. */
    r->current_a += 0.18f * (target - r->current_a);

    const vec3_t b_inst = {
        r->b_earth.x + r->k_true.x * r->current_a,
        r->b_earth.y + r->k_true.y * r->current_a,
        r->b_earth.z + r->k_true.z * r->current_a,
    };
    /* Магнітометр віддає усереднене за вікном дециматора значення —
     * саме через це фільтрувати струм доводиться теж. */
    r->b_lagged.x += 0.30f * (b_inst.x - r->b_lagged.x);
    r->b_lagged.y += 0.30f * (b_inst.y - r->b_lagged.y);
    r->b_lagged.z += 0.30f * (b_inst.z - r->b_lagged.z);
}

static vec3_t rig_read_field(void *ctx)
{
    rig_t *r = (rig_t *)ctx;
    return (vec3_t){
        r->b_lagged.x + rig_noise(r, 0.35f),
        r->b_lagged.y + rig_noise(r, 0.35f),
        r->b_lagged.z + rig_noise(r, 0.35f),
    };
}

static float rig_read_current(void *ctx)
{
    rig_t *r = (rig_t *)ctx;
    return r->current_a + r->shunt_offset_a + rig_noise(r, 0.4f);
}

static void rig_set_throttle(void *ctx, float pct)
{
    ((rig_t *)ctx)->throttle_pct = pct;
}

/* Місце EEPROM/FRAM: на столі це файл, на платі — сторінка флешу. */
static bool rig_save_params(void *ctx, vec3_t k)
{
    (void)ctx;
    FILE *f = fopen(PARAM_FILE, "w");
    if (f == NULL) {
        return false;
    }
    const int written = fprintf(f, "COMPASS_MOT_X %.6f\nCOMPASS_MOT_Y %.6f\nCOMPASS_MOT_Z %.6f\n",
                                (double)k.x, (double)k.y, (double)k.z);
    /* Помилка запису вилазить не на fprintf, а на fclose: доти дані
     * лежать у буфері. Пропустити цю перевірку — типовий спосіб
     * «зберегти» калібрування в нікуди. */
    const bool ok = (written > 0) && (fclose(f) == 0);
    return ok;
}

/* ---------------------------------------------------------------- */
/* Перевірка результату на свіжому прогоні                           */
/* ---------------------------------------------------------------- */

/* Проганяємо газ ще раз і міряємо, наскільки поле лишається сталим
 * до і після компенсації — це та сама горизонтальна крива з §5. */
static void validate(rig_t *r, vec3_t k)
{
    compass_mot_t cm;
    compass_mot_init(&cm, k, DT_SEC, CURRENT_LPF_HZ, 200.0f);

    double err_raw = 0.0, err_clean = 0.0;
    uint32_t n = 0;

    for (int step = 0; step <= 8; step++) {
        r->throttle_pct = (float)step * 10.0f;
        for (int t = 0; t < 120; t++) {   /* 1.2 с на сходинку */
            rig_tick(r);
            const vec3_t raw = rig_read_field(r);
            const float i = rig_read_current(r);
            const vec3_t clean = compass_mot_apply(&cm, raw, i);

            const float dr[3] = {raw.x - r->b_earth.x, raw.y - r->b_earth.y, raw.z - r->b_earth.z};
            const float dc[3] = {clean.x - r->b_earth.x, clean.y - r->b_earth.y, clean.z - r->b_earth.z};
            if (t < 40) {
                continue;   /* перехідний процес не рахуємо */
            }
            err_raw   += (double)(dr[0]*dr[0] + dr[1]*dr[1] + dr[2]*dr[2]);
            err_clean += (double)(dc[0]*dc[0] + dc[1]*dc[1] + dc[2]*dc[2]);
            n++;
        }
    }
    r->throttle_pct = 0.0f;

    if (n == 0) {
        return;
    }
    printf("\nКонтрольний прогін (%u вибірок):\n", n);
    printf("  відхилення поля до компенсації : %.2f мкТл (RMS)\n", sqrt(err_raw / n));
    printf("  відхилення поля після          : %.2f мкТл (RMS)\n", sqrt(err_clean / n));
}

/* ---------------------------------------------------------------- */

int main(void)
{
    rig_t rig = {
        .b_earth = {21.5f, 1.2f, 43.8f},     /* типовий вектор для наших широт */
        .k_true  = {-0.128f, 0.061f, -0.212f},
        .i_full_a = 118.0f,
        .shunt_offset_a = 0.0f,              /* спробуйте 3.0f — прогін впаде */
        .rng = 20260829u,
    };

    cm_io_t io = {
        .read_field   = rig_read_field,
        .read_current = rig_read_current,
        .set_throttle = rig_set_throttle,
        .save_params  = rig_save_params,
        .ctx = &rig,
    };

    cm_calib_t calib;
    uint32_t now = 0;
    cm_calib_start(&calib, &io, now);

    cm_state_t prev = calib.state;
    float prev_throttle = calib.throttle_pct;

    /* 30 с стелі на весь регламент — довше стенд тримати нема сенсу. */
    for (uint32_t tick = 0; tick < 3000u; tick++, now += DT_MS) {
        rig_tick(&rig);
        const cm_state_t st = cm_calib_step(&calib, now);

        if (st != prev) {
            printf("[%6.2f с] %-10s → %-10s  газ %.0f%%  I=%.1f А\n",
                   now / 1000.0, cm_state_name(prev), cm_state_name(st),
                   (double)calib.throttle_pct, (double)rig.current_a);
            prev = st;
            prev_throttle = calib.throttle_pct;
        } else if (calib.throttle_pct != prev_throttle) {
            printf("[%6.2f с] %-10s     газ %.0f%%  I=%.1f А  вибірок %u\n",
                   now / 1000.0, cm_state_name(st),
                   (double)calib.throttle_pct, (double)rig.current_a, calib.ols.n);
            prev_throttle = calib.throttle_pct;
        }

        if (st == CM_DONE || st == CM_FAILED) {
            break;
        }
    }

    if (calib.state != CM_DONE) {
        fprintf(stderr, "\nКалібрування не завершилося: %s\n",
                calib.fail_reason ? calib.fail_reason : "вичерпано час прогону");
        rig_set_throttle(&rig, 0.0f);
        return EXIT_FAILURE;
    }

    const compass_mot_fit_t *f = &calib.fit;
    printf("\nВибірок у регресії: %u (відкинуто %u)\n", f->samples, calib.ols.rejected);
    printf("k       = [ %+.4f  %+.4f  %+.4f ] мкТл/А\n",
           (double)f->k.x, (double)f->k.y, (double)f->k.z);
    printf("істина  = [ %+.4f  %+.4f  %+.4f ] мкТл/А\n",
           (double)rig.k_true.x, (double)rig.k_true.y, (double)rig.k_true.z);
    printf("R²      = [ %.4f  %.4f  %.4f ]\n",
           (double)f->r2[0], (double)f->r2[1], (double)f->r2[2]);
    printf("завада  = %.1f%% при I_max = %.1f А — %s\n",
           (double)f->interference_pct, (double)f->i_max,
           compass_mot_verdict(f->interference_pct));
    printf("параметри записано у " PARAM_FILE "\n");

    validate(&rig, f->k);
    return EXIT_SUCCESS;
}
