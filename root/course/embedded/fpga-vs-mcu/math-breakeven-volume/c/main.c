#include <stdio.h>
#include <math.h>

/* Один варіант рішення: разова розробка (NRE) і ціна за штуку.
   ВАЖЛИВО: будь-яку разову суму (ліцензію, прилад, ризик P·вартість)
   заздалегідь клади в nre; в unit — лише те, що множиться на КОЖЕН виріб. */
typedef struct {
    const char *name;
    double nre;        /* разова вартість розробки, у грошах */
    double unit;       /* ціна за одну штуку */
} Variant;

/* Сумарна вартість партії з q штук: пряма NRE + unit·q. */
static double batch_cost(Variant v, double q) {
    return v.nre + v.unit * q;
}

/* Точка беззбитковості двох варіантів.
   Повертає 1, якщо перетин існує при скінченному Q; 0 — прямі паралельні. */
static int breakeven(Variant a, Variant b, double *q_star) {
    double den = a.unit - b.unit;          /* різниця цін за штуку */
    if (fabs(den) < 1e-9) return 0;        /* однаковий нахил -> перетину немає */
    *q_star = (b.nre - a.nre) / den;       /* (NRE_B − NRE_A)/(ціна_A − ціна_B) */
    return 1;
}

static void report(Variant a, Variant b) {
    printf("== %s  проти  %s ==\n", a.name, b.name);
    printf("  %-8s: NRE %8.0f, ціна/шт %6.2f\n", a.name, a.nre, a.unit);
    printf("  %-8s: NRE %8.0f, ціна/шт %6.2f\n", b.name, b.nre, b.unit);

    double q;
    if (!breakeven(a, b, &q)) {
        /* Паралельні прямі: ціни за штуку рівні, тож різницю дає лише разова
           частина. Дешевший назавжди той, у кого нижча NRE. */
        const char *win = (a.nre <= b.nre) ? a.name : b.name;
        printf("  Ціни за штуку рівні -> прямі паралельні, перетину немає.\n");
        printf("  ВИРОК: %s дешевший на будь-якому тиражі (нижча NRE).\n\n", win);
        return;
    }

    /* Хто дешевший на малому тиражі (при Q->0, тобто за NRE), а хто на великому. */
    const char *low  = (a.nre < b.nre) ? a.name : b.name;   /* виграє нижче точки */
    const char *high = (a.nre < b.nre) ? b.name : a.name;   /* виграє вище точки  */

    if (q <= 0.0) {
        /* Точка ліворуч від нуля: уся дійсна вісь Q>=0 по один бік.
           "Великосерійний" варіант насправді дорожчий скрізь -> вирок. */
        printf("  Q* = %.1f  (від'ємна)\n", q);
        printf("  ВИРОК: %s дорожчий і по NRE, і по одиниці -> програє на БУДЬ-ЯКОМУ тиражі.\n", high);
        printf("  Рахувати тираж не треба: бери %s.\n\n", low);
        return;
    }

    long qi = (long)ceil(q);   /* найменший цілий тираж, з якого виграє великосерійний */
    printf("  Q* = %.1f шт  (беззбитковість)\n", q);
    printf("  Q <  %ld  -> дешевший %s\n", qi, low);
    printf("  Q >= %ld  -> дешевший %s\n", qi, high);
    printf("  (перевірка при Q*: %.0f = %.0f)\n\n",
           batch_cost(a, q), batch_cost(b, q));
}

int main(void) {
    /* Приклад 1: FPGA поглинає кілька мікросхем -> дешевша одиниця, дорога розробка.
       (NRE вже містить ризик P·вартість: A 200, B 1800.) */
    report((Variant){ "МК+обвяз", 2200.0, 18.00 },
           (Variant){ "FPGA",     13400.0, 15.00 });

    /* Приклад 2: ліцензія в NRE тягне B дорожчою і по NRE, і по одиниці -> вирок. */
    report((Variant){ "МК",   1500.0,  6.00 },
           (Variant){ "FPGA", 12000.0, 17.50 });

    /* Приклад 3: однакова ціна за штуку -> паралельні прямі, вирішує сама NRE. */
    report((Variant){ "варА", 1000.0, 10.00 },
           (Variant){ "варБ", 4000.0, 10.00 });
    return 0;
}
