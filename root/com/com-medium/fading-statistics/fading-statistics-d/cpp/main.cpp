#include <iostream>
#include <cmath>
#include <iomanip>

// Обчислення ймовірності виходу з ладу (Outage Probability) у каналі Релея
double rayleigh_outage_probability(double snr_avg_db, double snr_th_db) {
    double gamma_avg = std::pow(10.0, snr_avg_db / 10.0);
    double gamma_th  = std::pow(10.0, snr_th_db / 10.0);
    // P(SNR <= SNR_th) = 1 - exp(-gamma_th / gamma_avg)
    return 1.0 - std::exp(-gamma_th / gamma_avg);
}

// Обчислення необхідного запасу на завмирання (дБ) для заданої надійності (наприклад, 0.999)
double required_fading_margin_db(double reliability) {
    double outage_target = 1.0 - reliability;
    // P_out = 1 - exp(-1 / Margin_linear) => Margin_linear = -1 / ln(1 - P_out)
    double margin_linear = -1.0 / std::log(1.0 - outage_target);
    return 10.0 * std::log10(margin_linear);
}

int main() {
    double snr_avg_db = 25.0; // Середнє SNR = 25 дБ
    double snr_th_db  = 10.0; // Поріг SNR = 10 дБ

    double p_out = rayleigh_outage_probability(snr_avg_db, snr_th_db);
    double margin_999 = required_fading_margin_db(0.999);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Середнє SNR: " << snr_avg_db << " дБ, Поріг SNR: " << snr_th_db << " дБ\n";
    std::cout << "Поточна імовірність виходу з ладу (Outage Probability): " 
              << p_out * 100.0 << " %\n";
    std::cout << "Необхідний запас на завмирання для надійності 99.9%: " 
              << margin_999 << " дБ\n";

    return 0;
}
