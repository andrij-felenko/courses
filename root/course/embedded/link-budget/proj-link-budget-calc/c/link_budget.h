#ifndef LINK_BUDGET_H
#define LINK_BUDGET_H

#include <stdbool.h>
#include <stddef.h>

/* Вхідні параметри радіолінії */
typedef struct {
    double freq_mhz;      /* Частота в МГц (наприклад, 868.0 або 2400.0) */
    double distance_km;   /* Відстань між вузлами в км */
    double tx_power_dbm;  /* Потужність передавача в дБм */
    double tx_gain_dbi;   /* Підсилення антени передавача в дБі */
    double tx_loss_db;    /* Втрати в кабелях/роз'ємах передавача в дБ */
    double rx_gain_dbi;   /* Підсилення антени приймача в дБі */
    double rx_loss_db;    /* Втрати в кабелях/роз'ємах приймача в дБ */
    double rx_sens_dbm;   /* Чутливість приймача в дБм (наприклад, -120.0) */
} link_params_t;

/* Результати розрахунку енергетичного бюджету */
typedef struct {
    double fspl_db;        /* Втрати у вільному просторі (FSPL) в дБ */
    double eirp_dbm;       /* Ефективна ізотропно випромінювана потужність в дБм */
    double prx_dbm;        /* Рівень сигналу на вході приймача в дБм */
    double margin_db;      /* Запас зв'язку (Fade Margin) в дБ */
    bool is_reliable;      /* Чи є лінк надійним (запас >= 10 дБ) */
} link_result_t;

bool link_budget_validate(const link_params_t *params, char *err_msg, size_t err_size);
void link_budget_calculate(const link_params_t *params, link_result_t *result);
void link_budget_print_report(const link_params_t *params, const link_result_t *result);

#endif /* LINK_BUDGET_H */
