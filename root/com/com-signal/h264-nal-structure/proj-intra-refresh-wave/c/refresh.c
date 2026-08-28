/* refresh.c — планувальник хвилі intra refresh.
   Уся арифметика цілочислова; стан між кадрами — чотири числа. */

#include <stdbool.h>

#define MV_GUARD_PX 8   /* 3 px шестивідвідний фільтр + 3 px згладжування, із запасом */

typedef struct {
    int mb_w, mb_h;   /* розмір кадру в макроблоках                  */
    int stripe;       /* ширина смуги, макроблоків за кадр           */
    int wave;         /* ліва колонка смуги цього кадру              */
    int clean;        /* чиста ширина ОПОРИ, макроблоків             */
} refresh_t;

typedef struct {
    int first_col;    /* [first_col, last_col) — форсувати intra     */
    int last_col;
    int recovery_cnt; /* поле SEI recovery_point, або -1 — не треба  */
} refresh_plan_t;

void refresh_init(refresh_t *r, int w_px, int h_px, int period_frames)
{
    r->mb_w   = (w_px + 15) / 16;
    r->mb_h   = (h_px + 15) / 16;
    r->stripe = (r->mb_w + period_frames - 1) / period_frames;
    if (r->stripe < 1) r->stripe = 1;
    r->wave   = 0;
    r->clean  = 0;
}

/* Відкотити хвилю на початок: відповідь на PLI від приймача. */
void refresh_restart(refresh_t *r)
{
    r->wave  = 0;
    r->clean = 0;
}

refresh_plan_t refresh_begin_frame(refresh_t *r)
{
    refresh_plan_t p;
    int cycle = (r->mb_w + r->stripe - 1) / r->stripe;

    r->clean       = r->wave;            /* опора чиста рівно доти, куди дійшла хвиля */
    p.first_col    = r->wave;
    p.last_col     = r->wave + r->stripe;
    if (p.last_col > r->mb_w) p.last_col = r->mb_w;
    p.recovery_cnt = (r->wave == 0) ? cycle - 1 : -1;
    return p;
}

void refresh_end_frame(refresh_t *r)
{
    r->wave += r->stripe;
    if (r->wave >= r->mb_w) r->wave = 0;  /* цикл безперервний */
}

/* Чи взагалі обмежувати рух цього блока. Брудній зоні все одно. */
bool refresh_mv_constrained(const refresh_t *r, int mb_x)
{
    return mb_x < r->clean;
}

/* Стеля горизонтальної складової вектора, у чвертьпікселях.
   Від'ємною виходить лише в останній чистій колонці — там блок
   не має права дивитися праворуч навіть на нуль пікселів. */
int refresh_mv_x_limit(const refresh_t *r, int mb_x)
{
    int limit = r->clean * 16 - (mb_x + 1) * 16 - MV_GUARD_PX;
    return limit < 0 ? 0 : limit * 4;
}
