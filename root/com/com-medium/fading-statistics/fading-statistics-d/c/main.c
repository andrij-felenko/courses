#include <stdio.h>
#include <math.h>

/* Обчислення ймовірності виходу з ладу (Outage Probability) у каналі Релея */
double rayleigh_outage_probability(double snr_avg_db, double snr_th_db) {
    double gamma_avg = pow(10.0, snr_avg_db / 10.0);
    double gamma_th  = pow(10.0, snr_th_db / 10.0);
    return 1.0 - exp(-gamma_th / gamma_avg);
}

/* Обчислення необхідного запасу на завмирання (дБ) для заданої надійності */
double required_fading_margin_db(double reliability) {
    double outage_target = 1.0 - reliability;
    double margin_linear = -1.0 / log(1.0 - outage_target);
    return 10.0 * log10(margin_linear);
}

int main(void) {
    double snr_avg_db = 25.0;
    double snr_th_db  = 10.0;

    double p_out = rayleigh_outage_probability(snr_avg_db, snr_th_db);
    double margin_999 = required_fading_margin_db(0.999);

    printf("Середнє SNR: %.1f дБ, Поріг SNR: %.1f дБ\n", snr_avg_db, snr_th_db);
    printf("Поточна імовірність виходу з ладу: %.4f %%\n", p_out * 100.0);
    printf("Необхідний запас на завмирання для надійності 99.9%%: %.2f дБ\n", margin_999);

    return 0;
}
