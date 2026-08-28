/* mini-update.c — дві копії екрана й три способи звести першу до другої.
   cc -std=c11 -O2 -Wall mini-update.c -o mini-update */
#include <stdint.h>
#include <stdio.h>

#define ROWS 24
#define COLS 80

/* Комірка — знак і ознаки разом. attr: біти 0…2 — колір тексту (0…7),
   біт 3 — жирний. Один байт на знак, тому в кадрі тільки ASCII. */
typedef struct { unsigned char ch, attr; } Cell;
typedef struct { Cell c[ROWS][COLS]; } Screen;

static int cell_eq(Cell a, Cell b) { return a.ch == b.ch && a.attr == b.attr; }

/* «Дріт»: рахує байти, а за emit == 1 ще й справді їх друкує. */
typedef struct {
        size_t bytes;
        int    emit;
        int    cy, cx;   /* де стоїть курсор; cx < 0 — «не знаємо» */
        int    attr;     /* які ознаки ввімкнені; < 0 — «не знаємо» */
} Wire;

static void put(Wire *w, const char *s, size_t n)
{
        w->bytes += n;
        if (w->emit)
                fwrite(s, 1, n, stdout);
}

static int cup_len(int y, int x)                 /* скільки важить стрибок туди */
{
        char b[16];
        return snprintf(b, sizeof b, "\033[%d;%dH", y + 1, x + 1);
}

static void cup(Wire *w, int y, int x)
{
        char b[16];
        int n = snprintf(b, sizeof b, "\033[%d;%dH", y + 1, x + 1);

        put(w, b, (size_t) n);
        w->cy = y;
        w->cx = x;
}

static int sgr_len(int a) { return a == 0 ? 3 : (a & 8) ? 9 : 7; }

static void sgr(Wire *w, int a)
{
        char b[16];
        int n;

        if (a == w->attr)
                return;                          /* уже ввімкнене вдруге не вмикаємо */
        if (a == 0)
                n = snprintf(b, sizeof b, "\033[m");
        else
                n = snprintf(b, sizeof b, "\033[0;%s3%dm", (a & 8) ? "1;" : "", a & 7);
        put(w, b, (size_t) n);
        w->attr = a;
}

static void emit_cell(Wire *w, Cell c)
{
        sgr(w, c.attr);
        put(w, (const char *) &c.ch, 1);
        if (++w->cx == COLS)
                w->cx = -1;      /* останню колонку кожен термінал доводить по-своєму */
}

/* Перед кожним виміром про курсор і ознаки термінала ми знову нічого не знаємо. */
static void begin(Wire *w) { w->bytes = 0; w->cy = 0; w->cx = -1; w->attr = -1; }
