#include "report.h"

#include <math.h>
#include <stdio.h>

#define TABLE_WIDTH 92

static size_t utf8_glyphs(const char *s)
{
    size_t n = 0;
    const unsigned char *p;

    for (p = (const unsigned char *)s; *p != '\0'; ++p) {
        /* Продовжувальні байти 10xxxxxx окремої літери не утворюють. */
        if ((*p & 0xC0) != 0x80) {
            ++n;
        }
    }
    return n;
}

void report_put_left(const char *s, size_t width)
{
    size_t w;

    if (s == NULL) {
        s = "";
    }
    fputs(s, stdout);
    for (w = utf8_glyphs(s); w < width; ++w) {
        putchar(' ');
    }
}

void report_put_right(const char *s, size_t width)
{
    size_t w;

    if (s == NULL) {
        s = "";
    }
    for (w = utf8_glyphs(s); w < width; ++w) {
        putchar(' ');
    }
    fputs(s, stdout);
}

verdict_t dc_row_verdict(const dc_row_t *row, double *err_pct_out)
{
    double err = 0.0;
    double dev;
    verdict_t v;

    if (row == NULL) {
        if (err_pct_out != NULL) {
            *err_pct_out = 0.0;
        }
        return V_FAIL;
    }

    if (fabs(row->calc) < 1e-12) {
        /* Розрахунковий нуль: відносної похибки не існує, судимо абсолютно. */
        v = (fabs(row->meas) < 1e-12) ? V_PASS : V_FAIL;
    } else {
        err = (row->meas - row->calc) / row->calc * 100.0;
        dev = fabs(err);
        if (dev <= row->tol_pct) {
            v = V_PASS;
        } else if (dev <= 5.0 * row->tol_pct) {
            /* Такий порядок відхилення ще пояснюється навантаженням
               приладу — рядок вимагає корекції, а не пошуку дефекту. */
            v = V_WARN;
        } else {
            v = V_FAIL;
        }
    }

    if (err_pct_out != NULL) {
        *err_pct_out = err;
    }
    return v;
}

void dc_table_print(const dc_row_t *rows, size_t count)
{
    size_t i;

    if (rows == NULL) {
        return;
    }

    report_put_left("Параметр", 36);
    report_put_left("Од.", 5);
    report_put_right("Розрах.", 11);
    report_put_right("Виміряно", 12);
    report_put_right("Δ", 11);
    report_put_right("δ, %", 9);
    printf("  Статус\n");

    for (i = 0; i < TABLE_WIDTH; ++i) {
        putchar('-');
    }
    putchar('\n');

    for (i = 0; i < count; ++i) {
        double err;
        verdict_t v = dc_row_verdict(&rows[i], &err);

        report_put_left(rows[i].name, 36);
        report_put_left(rows[i].unit, 5);
        printf("%11.4f%12.4f%11.4f%9.2f  %s\n",
               rows[i].calc,
               rows[i].meas,
               rows[i].meas - rows[i].calc,
               err,
               verdict_text(v));
    }
}

verdict_t dc_table_verdict(const dc_row_t *rows, size_t count)
{
    verdict_t worst = V_PASS;
    size_t i;

    if (rows == NULL) {
        return V_FAIL;
    }
    for (i = 0; i < count; ++i) {
        verdict_t v = dc_row_verdict(&rows[i], NULL);
        if (v > worst) {
            worst = v;
        }
    }
    return worst;
}
