#include "link_budget.h"
#include <stdio.h>
#include <math.h>

bool link_budget_validate(const link_params_t *params, char *err_msg, size_t err_size) {
    if (!params) {
        if (err_msg && err_size > 0) snprintf(err_msg, err_size, "Параметри не вказані (NULL).");
        return false;
    }
    if (params->freq_mhz <= 0.0) {
        if (err_msg && err_size > 0) snprintf(err_msg, err_size, "Частота має бути більше 0 МГц.");
        return false;
    }
    if (params->distance_km <= 0.0) {
        if (err_msg && err_size > 0) snprintf(err_msg, err_size, "Дистанція має бути більше 0 км.");
        return false;
    }
    if (params->tx_power_dbm < -30.0 || params->tx_power_dbm > 60.0) {
        if (err_msg && err_size > 0) snprintf(err_msg, err_size, "Потужність Tx поза реальними межами [-30..+60 дБм].");
        return false;
    }
    if (params->rx_sens_dbm > 0.0 || params->rx_sens_dbm < -160.0) {
        if (err_msg && err_size > 0) snprintf(err_msg, err_size, "Чутливість Rx має бути в межах [-160..0 дБм].");
        return false;
    }
    return true;
}

void link_budget_calculate(const link_params_t *params, link_result_t *result) {
    /* Рівняння Фріїса у логарифмічній шкалі децибел:
       FSPL (дБ) = 20*log10(d_km) + 20*log10(f_mhz) + 32.44 */
    result->fspl_db = 20.0 * log10(params->distance_km) + 20.0 * log10(params->freq_mhz) + 32.44;

    /* EIRP = Ptx + Gtx - Ltx */
    result->eirp_dbm = params->tx_power_dbm + params->tx_gain_dbi - params->tx_loss_db;

    /* Prx = EIRP + Grx - Lrx - FSPL */
    result->prx_dbm = result->eirp_dbm + params->rx_gain_dbi - params->rx_loss_db - result->fspl_db;

    /* Margin = Prx - Rx_sensitivity */
    result->margin_db = result->prx_dbm - params->rx_sens_dbm;

    /* Інженерний поріг надійного зв'язку */
    result->is_reliable = (result->margin_db >= 10.0);
}

void link_budget_print_report(const link_params_t *params, const link_result_t *result) {
    printf("\n==================================================\n");
    printf("        ЕНЕРГЕТИЧНИЙ БЮДЖЕТ РАДІОЛІНІЇ (FSPL)     \n");
    printf("==================================================\n");
    printf("Частота каналу:          %10.2f МГц\n", params->freq_mhz);
    printf("Дистанція траси:         %10.3f км\n", params->distance_km);
    printf("--------------------------------------------------\n");
    printf("Потужність Tx:           %+10.2f дБм\n", params->tx_power_dbm);
    printf("Підсилення антени Tx:    %+10.2f дБі\n", params->tx_gain_dbi);
    printf("Втрати кабелю Tx:        %10.2f дБ\n", params->tx_loss_db);
    printf("Еквівалентна EIRP:       %+10.2f дБм\n", result->eirp_dbm);
    printf("--------------------------------------------------\n");
    printf("Втрати простору (FSPL):  %10.2f дБ\n", result->fspl_db);
    printf("--------------------------------------------------\n");
    printf("Підсилення антени Rx:    %+10.2f дБі\n", params->rx_gain_dbi);
    printf("Втрати кабелю Rx:        %10.2f дБ\n", params->rx_loss_db);
    printf("Рівень сигналу Prx:      %+10.2f дБм\n", result->prx_dbm);
    printf("Чутливість приймача:     %+10.2f дБм\n", params->rx_sens_dbm);
    printf("==================================================\n");
    printf("ЗАПАС ЗВ'ЯЗКУ (MARGIN):  %+10.2f дБ\n", result->margin_db);
    if (result->is_reliable) {
        printf("СТАТУС: [ НАДІЙНИЙ ЛІНК ] (запас >= 10 дБ)\n");
    } else if (result->margin_db > 0.0) {
        printf("СТАТУС: [ НЕСТАБІЛЬНИЙ ] (запас < 10 дБ, можливі втрати пакетів)\n");
    } else {
        printf("СТАТУС: [ ВТРАТА ЗВ'ЯЗКУ ] (сигнал нижчий за чутливість)\n");
    }
    printf("==================================================\n\n");
}
