#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Структури конфігурації радіолінії */
typedef struct {
    double pwr_tx_dbm;      /* Потужність передавача (dBm) */
    double loss_tx_db;      /* Втрати у кабелі TX (dB) */
    double gain_tx_dbi;     /* Підсилення антени TX (dBi) */
} tx_config_t;

typedef struct {
    double freq_mhz;        /* Несуча частота (МГц) */
    double distance_km;     /* Відстань між антенами (км) */
    double loss_atm_db;     /* Атмосферні втрати (dB) */
    double loss_fade_db;    /* Запас на завмирання (dB) */
    double loss_misc_db;    /* Додаткові втрати (dB) */
} channel_config_t;

typedef struct {
    double gain_rx_dbi;     /* Підсилення антени RX (dBi) */
    double loss_rx_db;      /* Втрати у кабелі RX (dB) */
    double bandwidth_hz;    /* Смуга частот приймача (Гц) */
    double noise_figure_db; /* Коефіцієнт шуму N_F (dB) */
    double snr_min_db;      /* Поріг демодуляції SNR (dB) */
} rx_config_t;

typedef struct {
    double eirp_dbm;        /* EIRP = P_TX - L_tx + G_TX */
    double fspl_db;        /* Втрати у вільному просторі */
    double loss_path_total;/* Загальні втрати траси */
    double pwr_rx_dbm;     /* Потужність на вході RX */
    double sensitivity_dbm;/* Поріг чутливості RX */
    double margin_db;      /* Запас радіолінії (Margin) */
    double max_distance_km;/* Максимальна відстань при Margin=0 */
    bool is_link_viable;   /* Ознака успішності зв'язку (Margin >= 0) */
} link_budget_result_t;

/* Обчислення бюджету лінії */
link_budget_result_t calculate_link_budget(const tx_config_t *tx,
                                           const channel_config_t *channel,
                                           const rx_config_t *rx) {
    link_budget_result_t res;

    /* 1. Розрахунок EIRP */
    res.eirp_dbm = tx->pwr_tx_dbm - tx->loss_tx_db + tx->gain_tx_dbi;

    /* 2. Розрахунок FSPL у dB: 20*log10(d_km) + 20*log10(f_MHz) + 32.44 */
    res.fspl_db = 20.0 * log10(channel->distance_km) + 
                  20.0 * log10(channel->freq_mhz) + 32.44;

    /* 3. Загальні втрати траси */
    res.loss_path_total = res.fspl_db + channel->loss_atm_db + 
                          channel->loss_fade_db + channel->loss_misc_db;

    /* 4. Потужність сигналу на вхідному роз'ємі приймача */
    res.pwr_rx_dbm = res.eirp_dbm - res.loss_path_total + rx->gain_rx_dbi - rx->loss_rx_db;

    /* 5. Обчислення порогу чутливості: P_sens = -174 + 10*log10(B) + N_F + SNR_min */
    double thermal_noise_dbm = -173.98 + 10.0 * log10(rx->bandwidth_hz);
    res.sensitivity_dbm = thermal_noise_dbm + rx->noise_figure_db + rx->snr_min_db;

    /* 6. Запас радіолінії (Link Margin) */
    res.margin_db = res.pwr_rx_dbm - res.sensitivity_dbm;
    res.is_link_viable = (res.margin_db >= 0.0);

    /* 7. Максимально припустимі втрати FSPL_max при Margin = 0 */
    double fspl_max_db = res.eirp_dbm - channel->loss_atm_db - channel->loss_fade_db 
                         - channel->loss_misc_db + rx->gain_rx_dbi - rx->loss_rx_db 
                         - res.sensitivity_dbm;

    /* d_max = 10 ^ ( (FSPL_max - 20*log10(f_MHz) - 32.44) / 20 ) */
    double exp_val = (fspl_max_db - 20.0 * log10(channel->freq_mhz) - 32.44) / 20.0;
    res.max_distance_km = pow(10.0, exp_val);

    return res;
}

int main(void) {
    /* Налаштування сценарію: 868 МГц LoRa лінк на 10 км */
    tx_config_t tx = { .pwr_tx_dbm = 14.0, .loss_tx_db = 1.0, .gain_tx_dbi = 2.15 };
    channel_config_t ch = { 
        .freq_mhz = 868.0, 
        .distance_km = 10.0, 
        .loss_atm_db = 0.5, 
        .loss_fade_db = 10.0, 
        .loss_misc_db = 1.5 
    };
    rx_config_t rx = { 
        .gain_rx_dbi = 2.15, 
        .loss_rx_db = 1.0, 
        .bandwidth_hz = 125000.0, /* 125 кГц */
        .noise_figure_db = 6.0, 
        .snr_min_db = -10.0       /* CSS розширення спектра */
    };

    link_budget_result_t res = calculate_link_budget(&tx, &ch, &rx);

    printf("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ БЮДЖЕТУ ЛІНІЇ ===\n");
    printf("EIRP передавача:       %+.2f dBm\n", res.eirp_dbm);
    printf("Втрати простору FSPL:   %.2f dB\n", res.fspl_db);
    printf("Загальні втрати траси:  %.2f dB\n", res.loss_path_total);
    printf("Прийнята потужність:   %+.2f dBm\n", res.pwr_rx_dbm);
    printf("Поріг чутливості RX:   %+.2f dBm\n", res.sensitivity_dbm);
    printf("Запас лінії (Margin):   %+.2f dB [%s]\n", 
           res.margin_db, res.is_link_viable ? "ПРАЦЮЄ" : "ПОМИЛКА СИГНАЛУ");
    printf("Максимальна дальність:  %.2f км\n", res.max_distance_km);

    return 0;
}
