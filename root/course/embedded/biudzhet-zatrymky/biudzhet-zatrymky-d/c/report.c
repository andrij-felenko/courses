#include <stdio.h>
#include "report.h"

#define NAME_COL 30

/* printf рахує ширину в БАЙТАХ, а кирилиця в UTF-8 займає по два.
   Через це "%-30s" з українськими назвами розвалює таблицю: колонки
   зсуваються рівно на кількість не-ASCII символів. Тому доповнюємо самі,
   рахуючи кодові позиції — байти-продовження мають старші біти 10xxxxxx. */
static size_t u8_len(const char *s)
{
    size_t n = 0u;
    for (; *s != '\0'; s++) {
        if (((unsigned char)*s & 0xC0u) != 0x80u) {
            n++;
        }
    }
    return n;
}

static void u8_pad(const char *s, size_t width)
{
    size_t n = u8_len(s);
    fputs(s, stdout);
    for (; n < width; n++) {
        putchar(' ');
    }
}

static const char *kind_label(const lat_stage *st)
{
    switch (st->kind) {
    case LAT_FIXED:    return "стала";
    case LAT_PERIODIC: return st->synced ? "такт+фаза" : "такт";
    case LAT_BAND:     return "вилка";
    }
    return "?";
}

static void rule(char c, size_t n)
{
    size_t i;
    for (i = 0u; i < n; i++) {
        putchar(c);
    }
    putchar('\n');
}

void rep_pipeline(const lat_pipeline *p)
{
    const lat_budget b = lat_budget_of(p);
    const lat_stage *worst = NULL;
    double share = 0.0;
    size_t i;

    rule('=', 72u);
    printf(" БЮДЖЕТ ЗАТРИМКИ: %s\n", p->title);
    rule('-', 72u);
    u8_pad("Ланка тракту", NAME_COL);
    printf("  %9s %9s %9s  %-10s\n", "min, мс", "typ, мс", "max, мс", "тип");
    rule('-', 72u);

    for (i = 0u; i < p->count; i++) {
        const lat_stage *st = &p->stages[i];
        u8_pad(st->name, NAME_COL);
        printf("  %9.3f %9.3f %9.3f  %-10s%s\n",
               st->min_ms, st->typ_ms, st->max_ms, kind_label(st),
               (st->domain == LAT_PHYSICAL) ? " [фізика]" : "");
    }

    rule('-', 72u);
    u8_pad("РАЗОМ", NAME_COL);
    printf("  %9.3f %9.3f %9.3f\n", b.min_ms, b.typ_ms, b.max_ms);
    u8_pad("  з них електроніка (typ)", NAME_COL);
    printf("  %9s %9.3f\n", "", b.electronic_typ_ms);
    u8_pad("  з них фізика (typ)", NAME_COL);
    printf("  %9s %9.3f\n", "", b.physical_typ_ms);
    u8_pad("ДЖИТЕР (max - min)", NAME_COL);
    printf("  %9s %9s %9.3f\n", "", "", b.jitter_ms);

    if (lat_bottleneck(p, &worst, &share) == LAT_OK) {
        printf(" Найтовща ланка: %s — %.3f мс, %.0f%% найгіршого випадку\n",
               worst->name, worst->max_ms, share * 100.0);
    }
    if (lat_worst_quantum(p, &worst) == LAT_OK) {
        printf(" Найбільший такт: %s — T = %.3f мс%s\n",
               worst->name, worst->period_ms,
               worst->synced ? " (зафазовано, квант згорнуто)" : "");
    } else {
        printf(" Тактових ланок у тракті немає — квантування не додається\n");
    }
    rule('=', 72u);
    putchar('\n');
}

void rep_dynamics(const char *label, lat_budget b, double control_hz, double speed_mps)
{
    const double phase_typ = lat_phase_shift_deg(b.typ_ms, control_hz);
    const double phase_max = lat_phase_shift_deg(b.max_ms, control_hz);

    printf(" ДИНАМІКА: %s (маневрування %.1f Гц, швидкість %.0f м/с)\n",
           label, control_hz, speed_mps);
    printf("   затримка typ %.1f мс -> фаза %6.1f°  %s\n",
           b.typ_ms, phase_typ, lat_pio_text(lat_pio_verdict(phase_typ)));
    printf("   затримка max %.1f мс -> фаза %6.1f°  %s\n",
           b.max_ms, phase_max, lat_pio_text(lat_pio_verdict(phase_max)));
    printf("   сліпий шлях: %.2f м (typ), %.2f м (max)\n",
           lat_blind_distance_m(b.typ_ms, speed_mps),
           lat_blind_distance_m(b.max_ms, speed_mps));
    putchar('\n');
}

void rep_compare(const char *heading, const lat_pipeline *const *pipes, size_t count)
{
    size_t i;

    rule('=', 72u);
    printf(" %s\n", heading);
    rule('-', 72u);
    u8_pad("Конфігурація", NAME_COL);
    printf("  %9s %9s %9s  %s\n", "typ, мс", "max, мс", "джитер", "пляшкове горло");
    rule('-', 72u);

    for (i = 0u; i < count; i++) {
        const lat_budget b = lat_budget_of(pipes[i]);
        const lat_stage *worst = NULL;

        u8_pad(pipes[i]->title, NAME_COL);
        printf("  %9.2f %9.2f %9.2f  ", b.typ_ms, b.max_ms, b.jitter_ms);
        if (lat_bottleneck(pipes[i], &worst, NULL) == LAT_OK) {
            printf("%s\n", worst->name);
        } else {
            printf("%s\n", lat_strerror(LAT_ERR_EMPTY));
        }
    }
    rule('=', 72u);
    putchar('\n');
}
