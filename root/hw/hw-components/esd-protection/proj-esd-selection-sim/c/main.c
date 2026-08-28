#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define PI 3.14159265358979323846

typedef struct {
    const char *name;
    const char *tech_type;
    double c_esd_pf;      // Паразитна ємність (пФ)
    double r_dyn_ohm;     // Динамічний опір (Ом)
    double v_cl_tlp_v;    // Напруга фіксації при TLP 16 А (В)
    double max_surge_a;   // Піковий струм 8/20 мкс (А)
} esd_candidate_t;

typedef struct {
    double f_cutoff_ghz;      // Частота зрізу -3 дБ (ГГц)
    double delta_tr_ps;       // Завал фронту (пс)
    double s21_loss_db;       // Внесені втрати S21 на f_Nyquist (дБ)
    bool is_signal_clean;     // Чи вкладається у критерій S21 > -0.5 дБ
    bool is_protection_safe;  // Чи безпечна V_cl для приймача (< V_max)
} esd_evaluation_t;

static esd_evaluation_t evaluate_esd(const esd_candidate_t *cand,
                                    double data_rate_gbps,
                                    double z0_ohm,
                                    double v_receiver_max_v)
{
    esd_evaluation_t res;
    double c_farad = cand->c_esd_pf * 1e-12;
    double r_eff = z0_ohm / 2.0;
    double f_nyquist_hz = (data_rate_gbps * 1e9) / 2.0;

    // 1. Гранична частота зрізу -3 дБ
    double f_c_hz = 1.0 / (2.0 * PI * r_eff * c_farad);
    res.f_cutoff_ghz = f_c_hz / 1e9;

    // 2. Деградація часу наростання фронту
    double tr_sec = 2.2 * r_eff * c_farad;
    res.delta_tr_ps = tr_sec * 1e12;

    // 3. Внесені втрати S21 на частоті Найквіста
    double omega = 2.0 * PI * f_nyquist_hz;
    double denom = sqrt(4.0 + pow(omega * z0_ohm * c_farad, 2.0));
    double s21_mag = 2.0 / denom;
    res.s21_loss_db = 20.0 * log10(s21_mag);

    // 4. Критерії придатності
    res.is_signal_clean = (res.s21_loss_db >= -0.5);
    res.is_protection_safe = (cand->v_cl_tlp_v <= v_receiver_max_v);

    return res;
}

int main(void)
{
    const double data_rate = 20.0;    // USB4 Gen 3 / PCIe 5.0 (20 Гбіт/с на лінію)
    const double z0 = 50.0;           // 50 Ом одиночна лінія
    const double v_max_phy = 6.0;     // Гранична напруга входу приймача (В)

    const esd_candidate_t candidates[] = {
        {"Силовий TVS (SMAJ5.0A)", "Кремній (Single PN)", 450.0, 0.08, 9.2, 40.0},
        {"Стандартний ESD-TVS",    "Кремній (ESD-Array)",   3.5, 0.45, 8.5, 12.0},
        {"Низькоємнісний TVS",     "Діодний міст + Zener", 0.35, 0.30, 5.8,  5.0},
        {"Ультра-ESD TVS",         "Snapback SCR Deep-Sub", 0.12, 0.18, 4.8,  3.5},
        {"Полімерний PVVM",        "Polymer Matrix",       0.08, 1.80, 32.0, 0.5}
    };
    const size_t num_candidates = sizeof(candidates) / sizeof(candidates[0]);

    printf("=== Аналіз ESD-захисту для лінії %.1f Гбіт/с (f_Nyquist = %.1f ГГц, Z0 = %.0f Ом) ===\n",
           data_rate, data_rate / 2.0, z0);
    printf("Гранична напруга приймача V_max = %.1f В, критерій втрат S21 >= -0.5 дБ\n\n", v_max_phy);

    for (size_t i = 0; i < num_candidates; ++i) {
        const esd_candidate_t *c = &candidates[i];
        esd_evaluation_t eval = evaluate_esd(c, data_rate, z0, v_max_phy);

        printf("Компонент: %s [%s]\n", c->name, c->tech_type);
        printf("  Параметри: C = %.2f пФ, R_dyn = %.2f Ом, V_CL(@16A) = %.1f В\n",
               c->c_esd_pf, c->r_dyn_ohm, c->v_cl_tlp_v);
        printf("  Вплив на лінію: f_cutoff = %.2f ГГц, Δtr = %.2f пс, S21(10ГГц) = %.2f дБ\n",
               eval.f_cutoff_ghz, eval.delta_tr_ps, eval.s21_loss_db);
        printf("  Вердикт: %s | %s\n\n",
               eval.is_signal_clean ? "✓ СИГНАЛ ЧИСТИЙ" : "✗ СИГНАЛ ЗІПСОВАНО (велика ємність)",
               eval.is_protection_safe ? "✓ ЗАХИСТ НАДІЙНИЙ" : "✗ ЗАХИСТ НЕБЕЗПЕЧНИЙ (висока V_CL)");
    }
    return 0;
}
