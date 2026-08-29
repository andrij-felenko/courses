#ifndef REPORT_H
#define REPORT_H

#include <stddef.h>

#include "loading.h"

/* Рядок таблиці статичних параметрів протоколу верифікації (DC Table). */
typedef struct {
    const char *name;
    const char *unit;
    double calc;     /* розрахункове значення */
    double meas;     /* виміряне значення */
    double tol_pct;  /* допуск рядка, % */
} dc_row_t;

/* Статус рядка; err_pct_out (може бути NULL) отримує відносну похибку. */
verdict_t dc_row_verdict(const dc_row_t *row, double *err_pct_out);

void dc_table_print(const dc_row_t *rows, size_t count);

/* Загальний вердикт протоколу — найгірший зі своїх рядків. */
verdict_t dc_table_verdict(const dc_row_t *rows, size_t count);

/* Вирівнювання написів: printf рахує ширину поля в БАЙТАХ, а українська
   літера в UTF-8 займає два — через це %-20s ламає колонки таблиці. */
void report_put_left(const char *s, size_t width);
void report_put_right(const char *s, size_t width);

#endif /* REPORT_H */
