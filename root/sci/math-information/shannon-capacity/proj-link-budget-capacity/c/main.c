#include <stdio.h>
#include <math.h>

typedef struct {
    const char* name;
    double freq_hz;        // несуча частота, Гц
    double bandwidth_hz;   // ширина смуги B, Гц
    double tx_power_dbm;   // потужність передавача P_tx, дБм
    double tx_gain_dbi;    // коефіцієнт підсилення антени передавача G_tx, дБі
    double rx_gain_dbi;    // коефіцієнт підсилення антени приймача G_rx, дБі
    double path_loss_db;   // сумарні втрати сигналу на трасі, дБ
    double noise_fig_db;   // коефіцієнт шуму приймача NF, дБ
    double shannon_gap_db; // розрив Шеннона для вибраного типу FEC, дБ
} LinkParams;

typedef struct {
    double noise_floor_dbm; // поріг шуму у смузі, дБм
    double rx_power_dbm;    // потужність сигналу на вході приймача, дБм
    double snr_db;          // відношення сигнал/шум, дБ
    double snr_linear;      // відношення сигнал/шум у лінійній шкалі (рази)
    double capacity_bps;    // теоретична ємність за Шенноном, біт/с
    double practical_bps;   // практично досяжна швидкість, біт/с
    double spectral_eff;    // спектральна ефективність, біт/с/Гц
} LinkResult;

LinkResult calculate_link_capacity(const LinkParams* link) {
    LinkResult res;
    // Спектральна густина теплового шуму при 290 К: -174.0 дБм/Гц
    const double thermal_density_dbm = -174.0;
    
    // 1. Повний рівень шуму у смузі: N_total = -174 + 10*log10(B) + NF
    res.noise_floor_dbm = thermal_density_dbm + 10.0 * log10(link->bandwidth_hz) + link->noise_fig_db;
    
    // 2. Потужність сигналу на приймачі: P_rx = P_tx + G_tx + G_rx - PathLoss
    res.rx_power_dbm = link->tx_power_dbm + link->tx_gain_dbi + link->rx_gain_dbi - link->path_loss_db;
    
    // 3. Відношення сигнал/шум
    res.snr_db = res.rx_power_dbm - res.noise_floor_dbm;
    res.snr_linear = pow(10.0, res.snr_db / 10.0);
    
    // 4. Теоретична ємність Шеннона: C = B * log2(1 + SNR)
    res.capacity_bps = link->bandwidth_hz * (log(1.0 + res.snr_linear) / log(2.0));
    res.spectral_eff = res.capacity_bps / link->bandwidth_hz;
    
    // 5. Практична швидкість із розривом Гапа Gamma
    double gap_linear = pow(10.0, link->shannon_gap_db / 10.0);
    res.practical_bps = link->bandwidth_hz * (log(1.0 + res.snr_linear / gap_linear) / log(2.0));
    
    return res;
}

void print_link_report(const LinkParams* p, const LinkResult* r) {
    printf("====================================================\n");
    printf("Сценарій: %s\n", p->name);
    printf("----------------------------------------------------\n");
    printf("  Частота / смуга:       %.2f ГГц / %.2f МГц\n", p->freq_hz / 1e9, p->bandwidth_hz / 1e6);
    printf("  Рівень шуму N_total:   %.2f дБм\n", r->noise_floor_dbm);
    printf("  Прийнятий сигнал P_rx: %.2f дБм\n", r->rx_power_dbm);
    printf("  Відношення SNR:        %.2f дБ (x%.3f)\n", r->snr_db, r->snr_linear);
    printf("  Спектральна ефективн.: %.2f біт/с/Гц\n", r->spectral_eff);
    printf("  Ємність Шеннона C:     %.2f Мбіт/с\n", r->capacity_bps / 1e6);
    printf("  Практична швидкість:   %.2f Мбіт/с (розрив %.1f дБ)\n\n", 
           r->practical_bps / 1e6, p->shannon_gap_db);
}

int main(void) {
    LinkParams scenarios[] = {
        {
            .name = "Wi-Fi 6 (802.11ax, 5 ГГц, кімната 5 м)",
            .freq_hz = 5.18e9,
            .bandwidth_hz = 80.0e6,
            .tx_power_dbm = 20.0,
            .tx_gain_dbi = 3.0,
            .rx_gain_dbi = 3.0,
            .path_loss_db = 68.0,
            .noise_fig_db = 6.0,
            .shannon_gap_db = 2.0 // сучасний LDPC код
        },
        {
            .name = "5G NR (Sub-6 GHz, міська забудова 800 м)",
            .freq_hz = 3.5e9,
            .bandwidth_hz = 100.0e6,
            .tx_power_dbm = 43.0,
            .tx_gain_dbi = 15.0,
            .rx_gain_dbi = 0.0,
            .path_loss_db = 112.0,
            .noise_fig_db = 7.0,
            .shannon_gap_db = 2.0 // LDPC + Polar
        },
        {
            .name = "LoRa (868 МГц, дальній лінк IoT 10 км)",
            .freq_hz = 868.0e6,
            .bandwidth_hz = 125.0e3,
            .tx_power_dbm = 14.0,
            .tx_gain_dbi = 2.0,
            .rx_gain_dbi = 2.0,
            .path_loss_db = 140.0,
            .noise_fig_db = 5.0,
            .shannon_gap_db = 1.5 // розширення спектра CSS
        }
    };

    size_t count = sizeof(scenarios) / sizeof(scenarios[0]);
    for (size_t i = 0; i < count; ++i) {
        LinkResult r = calculate_link_capacity(&scenarios[i]);
        print_link_report(&scenarios[i], &r);
    }
    return 0;
}
