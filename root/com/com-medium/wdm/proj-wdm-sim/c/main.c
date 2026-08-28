#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define SPEED_OF_LIGHT 299792458.0   /* м/с */
#define ITU_REF_FREQ_THZ 193.10       /* ТГц */
#define PLANCK_CONST 6.62607015e-34  /* Дж·с */
#define OSNR_BW_HZ 12.5e9            /* 0.1 нм на 1550 нм */

typedef struct {
    int channel_index;
    double frequency_thz;
    double wavelength_nm;
} dwdm_channel_t;

typedef struct {
    double total_distance_km;
    double final_osnr_db;
    double total_dispersion_ps_nm;
    double rx_power_dbm;
    int link_viable;
} link_result_t;

/* Обчислення сітки каналів DWDM за ITU-T G.694.1 */
int generate_itu_grid(int num_channels, double start_m, double step_thz, dwdm_channel_t *out_channels) {
    if (!out_channels || num_channels <= 0) return -1;

    for (int i = 0; i < num_channels; i++) {
        double m = start_m + (double)i;
        double f_thz = ITU_REF_FREQ_THZ + m * step_thz;
        double f_hz = f_thz * 1.0e12;
        double lambda_m = SPEED_OF_LIGHT / f_hz;

        out_channels[i].channel_index = i + 1;
        out_channels[i].frequency_thz = f_thz;
        out_channels[i].wavelength_nm = lambda_m * 1.0e9;
    }
    return 0;
}

/* Моделювання проходження магістралі DWDM */
link_result_t simulate_dwdm_link(int num_spans, double span_len_km, double alpha_db_km,
                                double disp_coeff, double tx_dbm, double edfa_nf_db,
                                double mux_loss_db, double demux_loss_db) {
    link_result_t res;
    res.total_distance_km = num_spans * span_len_km;
    res.total_dispersion_ps_nm = res.total_distance_km * disp_coeff;

    /* Втрати одного прольоту та необхідне підсилення EDFA */
    double span_loss_db = span_len_km * alpha_db_km;
    double edfa_gain_linear = pow(10.0, span_loss_db / 10.0);
    double nf_linear = pow(10.0, edfa_nf_db / 10.0);

    /* Потужність сигналу на вході кожного EDFA (після прольоту) */
    double p_in_channel_dbm = tx_dbm - mux_loss_db - span_loss_db;
    double p_in_watts = 1.0e-3 * pow(10.0, p_in_channel_dbm / 10.0);

    /* Потужність шуму ASE від одного EDFA */
    double f_hz = ITU_REF_FREQ_THZ * 1.0e12;
    double p_ase_span_watts = nf_linear * (edfa_gain_linear - 1.0) * PLANCK_CONST * f_hz * OSNR_BW_HZ;

    /* Послідовне додавання шуму N підсилювачів */
    double p_ase_total_watts = p_ase_span_watts * (double)num_spans;

    /* Підсумкове OSNR на виході */
    double osnr_linear = p_in_watts * edfa_gain_linear / p_ase_total_watts;
    res.final_osnr_db = 10.0 * log10(osnr_linear);

    /* Вихідна потужність на приймачі */
    res.rx_power_dbm = tx_dbm - mux_loss_db - (num_spans * span_loss_db) + 
                       (num_spans * span_loss_db) - demux_loss_db;

    /* Критерії працездатності: OSNR >= 18 дБ, дисперсія <= 8000 пс/нм */
    res.link_viable = (res.final_osnr_db >= 18.0) && (fabs(res.total_dispersion_ps_nm) <= 8000.0);

    return res;
}

int main(void) {
    int num_channels = 40;
    dwdm_channel_t *channels = malloc(sizeof(dwdm_channel_t) * num_channels);
    if (!channels) return 1;

    generate_itu_grid(num_channels, -20.0, 0.1, channels);

    printf("=== ITU-T DWDM Grid (Перші 5 каналів із %d) ===\n", num_channels);
    for (int i = 0; i < 5; i++) {
        printf("Канал %02d: %7.2f ТГц | %7.2f нм\n",
               channels[i].channel_index, channels[i].frequency_thz, channels[i].wavelength_nm);
    }

    link_result_t res = simulate_dwdm_link(5, 80.0, 0.22, 17.0, 0.0, 5.5, 4.0, 4.0);

    printf("\n=== Результати моделювання оптичного тракту ===\n");
    printf("Загальна відстань: %.1f км (%d прольотів по 80 км)\n", res.total_distance_km, 5);
    printf("Підсумковий OSNR:   %.2f дБ (поріг: >= 18.0 дБ)\n", res.final_osnr_db);
    printf("Сумарна дисперсія:  %.1f пс/нм\n", res.total_dispersion_ps_nm);
    printf("Потужність на Rx:   %.2f дБм\n", res.rx_power_dbm);
    printf("Статус магістралі:  %s\n", res.link_viable ? "ПРОЙДЕНО (ОК)" : "ПОМИЛКА (Потрібен DSP/EDFA)");

    free(channels);
    return 0;
}
