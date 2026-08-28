#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ROWS 12
#define COLS 8
#define MAX_TOUCHES 5

/* Пороги в одиницях АЦП, підібрані під конкретне скло */
#define THR_FINGER_ON   120   /* поріг появи дотику            */
#define THR_FINGER_OFF   70   /* поріг зникнення (гістереза)   */
#define THR_GLOVE_ON     35   /* слабкий, але стійкий сигнал   */
#define THR_SELF_GND     60   /* self-підтвердження заземлення */
#define BASE_SLEW         2   /* швидкість повзання опори      */
#define WATER_PEAK_NUM    3   /* пік/сума: палець > 3/16       */
#define WATER_PEAK_DEN   16
#define GLOVE_ENTER_FRAMES 6

typedef enum { BLOB_FINGER, BLOB_WATER, BLOB_PALM } BlobKind;

typedef struct {
    int16_t  x_q4, y_q4;      /* центр у 1/16 кроку сітки */
    int32_t  sum;             /* сумарний Δ по плямі      */
    int16_t  peak;            /* максимум Δ               */
    uint8_t  cells;           /* скільки перетинів у плямі*/
    uint8_t  r_peak, c_peak;
    BlobKind kind;
} Blob;

typedef struct {
    int16_t baseline[ROWS][COLS];
    int16_t delta[ROWS][COLS];
    int16_t self_row[ROWS], self_col[COLS];
    bool    glove_mode;
    uint8_t weak_streak;      /* скільки кадрів поспіль слабка пляма */
    uint8_t active_count;     /* дотиків у попередньому кадрі        */
} TouchEngine;

/* --- 1. Різницевий кадр ------------------------------------------------ */
static void frame_delta(TouchEngine *e, const int16_t raw[ROWS][COLS])
{
    for (uint8_t r = 0; r < ROWS; ++r)
        for (uint8_t c = 0; c < COLS; ++c)
            e->delta[r][c] = e->baseline[r][c] - raw[r][c];
}

/* --- 2. Пошук плями навколо локального максимуму ----------------------- */
static bool grow_blob(const TouchEngine *e, uint8_t r0, uint8_t c0,
                      int16_t thr, bool used[ROWS][COLS], Blob *b)
{
    /* Проста заливка по 4 сусідах, глибина обмежена розміром пальця */
    int32_t sum = 0, wx = 0, wy = 0;
    uint8_t stack_r[64], stack_c[64], top = 0, cells = 0;
    int16_t peak = 0;

    stack_r[top] = r0; stack_c[top] = c0; ++top;
    used[r0][c0] = true;

    while (top > 0 && cells < 64) {
        --top;
        uint8_t r = stack_r[top], c = stack_c[top];
        int16_t d = e->delta[r][c];
        sum += d;  wx += (int32_t)d * c;  wy += (int32_t)d * r;
        if (d > peak) { peak = d; b->r_peak = r; b->c_peak = c; }
        ++cells;

        const int8_t dr[4] = { -1, 1, 0, 0 }, dc[4] = { 0, 0, -1, 1 };
        for (uint8_t k = 0; k < 4 && top < 62; ++k) {
            int8_t nr = (int8_t)r + dr[k], nc = (int8_t)c + dc[k];
            if (nr < 0 || nc < 0 || nr >= ROWS || nc >= COLS) continue;
            if (used[nr][nc] || e->delta[nr][nc] < thr / 3) continue;
            used[nr][nc] = true;
            stack_r[top] = (uint8_t)nr; stack_c[top] = (uint8_t)nc; ++top;
        }
    }
    if (sum <= 0) return false;

    b->sum   = sum;
    b->peak  = peak;
    b->cells = cells;
    b->x_q4  = (int16_t)((wx * 16) / sum);   /* центр ваги, 1/16 кроку */
    b->y_q4  = (int16_t)((wy * 16) / sum);
    return true;
}

/* --- 3. Класифікація: палець, вода чи долоня --------------------------- */
static BlobKind classify(const TouchEngine *e, const Blob *b)
{
    /* Пласка широка пляма з низьким піком — розлита вода або долоня */
    bool flat = ((int32_t)b->peak * WATER_PEAK_DEN) <
                (b->sum * WATER_PEAK_NUM);

    /* Заземлення: чи підтверджує self-скан рядок і стовпець піка */
    bool grounded = (e->self_row[b->r_peak] > THR_SELF_GND) &&
                    (e->self_col[b->c_peak] > THR_SELF_GND);

    if (!grounded) return BLOB_WATER;         /* плаває — не палець   */
    if (flat && b->cells > 12) return BLOB_PALM;
    return BLOB_FINGER;
}

/* --- 4. Умовне оновлення опорної картини ------------------------------- */
static void update_baseline(TouchEngine *e, const bool touched[ROWS][COLS])
{
    for (uint8_t r = 0; r < ROWS; ++r)
        for (uint8_t c = 0; c < COLS; ++c) {
            if (touched[r][c]) continue;              /* під пальцем — ні! */
            int16_t d = e->delta[r][c];
            if (d >  BASE_SLEW) e->baseline[r][c] -= BASE_SLEW;
            else if (d < -BASE_SLEW) e->baseline[r][c] += BASE_SLEW;
            else e->baseline[r][c] -= d;              /* дрібницю — одразу */
        }
}

/* --- 5. Кадр цілком ---------------------------------------------------- */
uint8_t touch_process(TouchEngine *e, const int16_t raw[ROWS][COLS],
                      Blob out[MAX_TOUCHES])
{
    frame_delta(e, raw);

    int16_t thr_on  = e->glove_mode ? THR_GLOVE_ON : THR_FINGER_ON;
    int16_t thr_off = e->glove_mode ? (THR_GLOVE_ON * 2 / 3) : THR_FINGER_OFF;
    int16_t thr = (e->active_count > 0) ? thr_off : thr_on;

    bool used[ROWS][COLS];    memset(used, 0, sizeof used);
    bool touched[ROWS][COLS]; memset(touched, 0, sizeof touched);

    uint8_t n = 0;
    bool weak_seen = false;

    for (uint8_t r = 0; r < ROWS && n < MAX_TOUCHES; ++r)
        for (uint8_t c = 0; c < COLS && n < MAX_TOUCHES; ++c) {
            if (used[r][c] || e->delta[r][c] < thr) {
                if (!e->glove_mode && e->delta[r][c] >= THR_GLOVE_ON)
                    weak_seen = true;        /* кандидат на рукавицю */
                continue;
            }
            Blob b = {0};
            if (!grow_blob(e, r, c, thr, used, &b)) continue;
            b.kind = classify(e, &b);
            if (b.kind != BLOB_FINGER) continue;      /* вода й долоня — геть */

            /* перетини під справжнім пальцем виключаємо з оновлення опори */
            for (uint8_t rr = 0; rr < ROWS; ++rr)
                for (uint8_t cc = 0; cc < COLS; ++cc)
                    if (used[rr][cc]) touched[rr][cc] = true;

            out[n++] = b;
        }

    /* Гістерезний автомат режиму рукавиці */
    if (n == 0 && weak_seen) {
        if (++e->weak_streak >= GLOVE_ENTER_FRAMES) e->glove_mode = true;
    } else {
        e->weak_streak = 0;
        if (n > 0 && out[0].peak > THR_FINGER_ON * 2) e->glove_mode = false;
    }

    update_baseline(e, touched);
    e->active_count = n;
    return n;
}
