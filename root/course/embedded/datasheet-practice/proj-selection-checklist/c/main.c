#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>

/* Корпуси; лише перші три паяються вручну — решту фільтр відкине. */
typedef enum { PKG_TO220, PKG_DPAK, PKG_SOT223, PKG_SOIC, PKG_QFN } Package;

/* Рядок бази: один прилад із його граничними параметрами. */
typedef struct {
    const char *name;
    int32_t v_max_mv;   /* абсолютний максимум по напрузі, мВ    */
    int32_t i_max_ma;   /* гранично допустимий струм, мА          */
    int32_t tj_max_c;   /* макс. температура кристала, °C         */
    Package pkg;
    int32_t price;      /* ціна, грн                              */
    int32_t deficit;    /* 0 — на складі … 100 — не дістати       */
    int      eol;       /* 1 — знято з виробництва (end-of-life)  */
} Part;

/* Жорсткі пороги: нижче них кандидата навіть не розглядаємо. */
typedef struct {
    int32_t v_min_mv;
    int32_t i_min_ma;
    int32_t tj_min_c;
} Hard;

/* Крок 1–2: розмиті вимоги схеми → жорсткі пороги із запасом.
   Множимо ДО ділення (×3/2 = ×1.5), щоб не втратити точності на
   цілих; для реальних напруг int32 не переповнюється. */
static Hard make_hard(int32_t work_v_mv, int32_t work_i_ma, int32_t t_amb_c)
{
    Hard h;
    h.v_min_mv = work_v_mv * 3 / 2;   /* ×1.5 запас по напрузі    */
    h.i_min_ma = work_i_ma * 2;       /* ×2  запас по струму      */
    h.tj_min_c = t_amb_c + 40;        /* +40 °C запас по кристалу  */
    return h;
}

static int solderable_by_hand(Package p)
{
    return p == PKG_TO220 || p == PKG_DPAK || p == PKG_SOT223;
}

/* Крок 3: фільтр. Один провалений поріг — і кандидат вибуває,
   хай би якими блискучими були решта параметрів (це AND, не OR). */
static int passes(const Part *p, const Hard *h)
{
    if (p->v_max_mv < h->v_min_mv)   return 0;   /* не тримає напругу   */
    if (p->i_max_ma < h->i_min_ma)   return 0;   /* не тримає струм     */
    if (p->tj_max_c < h->tj_min_c)   return 0;   /* перегріється        */
    if (!solderable_by_hand(p->pkg)) return 0;   /* не той корпус       */
    if (p->eol)                      return 0;   /* знято з виробництва */
    return 1;
}

/* Вузьке місце запасу — менший із двох коефіцієнтів, у відсотках.
   64-бітний проміжок множення страхує від переповнення. */
static int32_t margin_pct(const Part *p, const Hard *h)
{
    int32_t mv = (int32_t)((int64_t)p->v_max_mv * 100 / h->v_min_mv);
    int32_t mi = (int32_t)((int64_t)p->i_max_ma * 100 / h->i_min_ma);
    return mv < mi ? mv : mi;
}

/* Оцінна функція: більший запас — краще, ціна й дефіцит — гірше.
   Малий запас окремо не штрафуємо: його вже закладено в пороги
   make_hard. Ваги — цілі, під ваш пріоритет. */
static int32_t score(const Part *p, const Hard *h)
{
    enum { W_MARGIN = 1, W_PRICE = 1, W_DEFICIT = 2 };
    return W_MARGIN  * margin_pct(p, h)
         - W_PRICE   * p->price
         - W_DEFICIT * p->deficit;
}

/* Кандидат, що пройшов фільтр, із уже порахованою оцінкою —
   так компаратор сортування не потребує доступу до Hard. */
typedef struct { const Part *part; int32_t score; } Ranked;

static int by_score_desc(const void *a, const void *b)
{
    int32_t sa = ((const Ranked *)a)->score;
    int32_t sb = ((const Ranked *)b)->score;
    return (sb > sa) - (sb < sa);   /* спадання, без ризику переповнення */
}

/* Фільтр (O(n)) → оцінка → сортування тих, хто пройшов (O(m·log m)).
   cand/cap — буфер кандидатів (для повної бази його розмір беруть
   динамічно; тут вистачає статичного). Повертає m — скільки пройшло. */
static size_t select_parts(const Part *base, size_t n, const Hard *h,
                           Ranked *cand, size_t cap)
{
    size_t m = 0;
    for (size_t i = 0; i < n; ++i) {          /* крок 3: один прохід  */
        if (!passes(&base[i], h))
            continue;
        if (m < cap) {                        /* крок 4: одразу score */
            cand[m].part  = &base[i];
            cand[m].score = score(&base[i], h);
            ++m;
        }
    }
    qsort(cand, m, sizeof cand[0], by_score_desc);
    return m;                                  /* верхівка cand[0..2]  */
}

int main(void)
{
    /* Вимоги схеми: робочі 12 В, 0.8 А, довкола до 70 °C. */
    Hard h = make_hard(12000, 800, 70);  /* → Vmax≥18 В, Imax≥1.6 А, Tj≥110 °C */

    static const Part base[] = {
        /* name         Vmax   Imax  Tj   корпус       грн  деф eol */
        { "A 40V/2A",   40000, 2000, 150, PKG_TO220,   18,  0, 0 },
        { "B 30V/3A",   30000, 3000, 150, PKG_DPAK,    25, 10, 0 },
        { "C 20V/1A",   20000, 1000, 125, PKG_SOT223,  12,  0, 0 }, /* струм < 1.6 А */
        { "D 18V/1.6A", 18000, 1600, 150, PKG_TO220,    9,  0, 0 }, /* упритул       */
        { "E 60V/2A",   60000, 2000, 175, PKG_QFN,     15,  0, 0 }, /* корпус        */
        { "F 60V/4A",   60000, 4000, 150, PKG_DPAK,    30, 50, 0 },
        { "G 40V/2A",   40000, 2000, 150, PKG_TO220,   17,  0, 1 }, /* знято з випуску */
    };
    enum { N = sizeof base / sizeof base[0] };

    Ranked cand[N];
    size_t m = select_parts(base, N, &h, cand, N);

    size_t top = m < 3 ? m : 3;
    for (size_t i = 0; i < top; ++i)
        printf("%zu. %-10s  score=%ld\n",
               i + 1, cand[i].part->name, (long)cand[i].score);
    return 0;
}
