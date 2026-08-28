#include <cstdio>

// Усі величини — у базових одиницях СІ: кулони, ампери, фаради, секунди, вольти.
struct BootParams {
    double Qg;          // заряд затвора верхнього ключа, Кл (з даташита MOSFET)
    double Qls;         // заряд зсуву рівня за такт, Кл (з даташита драйвера)
    double Qrr;         // зворотний заряд відновлення діода, Кл (0 для Шотткі)
    double Iqbs;        // струм спокою верхнього боку, А (макс із даташита)
    double Icbs_leak;   // витік плаваючої шини драйвера + конденсатора, А
    double Ig_leak;     // витік затвора + зсуву рівня в статиці, А
    double f;           // частота ШІМ, Гц
    double duty_max;    // максимальна робоча шпаруватість, 0..1
    double dV_allow;    // дозволене просідання VB-VS, В
    double R_charge;    // сумарний послідовний опір доливу, Ом
    double dcbias_derate; // частка ємності, що лишається під напругою (напр. 0.5)
    double margin;      // додатковий запас (пуск, розкид), напр. 3.0
};

// Нижня межа: скільки ємності треба, щоб не просісти за найдовший відкритий такт.
double cbs_min(const BootParams &p, double *q_total_out = nullptr) {
    double t_on   = p.duty_max / p.f;                   // найдовший відкритий час
    double q_once = p.Qg + p.Qls + p.Qrr;              // разові порції
    double i_flow = p.Iqbs + p.Icbs_leak + p.Ig_leak;
    double q_flow = i_flow * t_on;                      // цівки × час
    double q_total = q_once + q_flow;
    if (q_total_out) *q_total_out = q_total;
    return q_total / p.dV_allow;                        // Cbs >= Qвитрат / ΔV
}

// Верхня межа: більше цієї ємності не встигне долитися за паузу t_off (5·τ).
double cbs_max(const BootParams &p) {
    double t_off = (1.0 - p.duty_max) / p.f;            // закрита частина періоду
    double tau_allow = t_off / 5.0;                     // 5 сталих часу на долив
    return tau_allow / p.R_charge;                      // Cbs_max = t_off / (5·R)
}

// Номінал, який реально ставимо: підлогу ділимо на DC-bias і множимо на запас.
double cbs_pick(const BootParams &p) {
    double lo = cbs_min(p);
    return lo / p.dcbias_derate * p.margin;             // компенсуємо DC-bias і запас
}

int main() {
    BootParams p{
        .Qg = 50e-9, .Qls = 5e-9, .Qrr = 2e-9,
        .Iqbs = 230e-6, .Icbs_leak = 50e-6, .Ig_leak = 0.3e-6,
        .f = 20e3, .duty_max = 0.90, .dV_allow = 0.5,
        .R_charge = 10.0, .dcbias_derate = 0.5, .margin = 3.0,
    };

    double q_total;
    double lo = cbs_min(p, &q_total);
    double hi = cbs_max(p);
    double pick = cbs_pick(p);

    printf("Qвитрат   = %.1f нКл\n", q_total * 1e9);
    printf("Cbs(min)  = %.0f нФ   (нижня межа з балансу заряду)\n", lo * 1e9);
    printf("Cbs(max)  = %.0f нФ   (верхня межа з перезаряду)\n", hi * 1e9);
    printf("ставимо   ~ %.2f мкФ  (з DC-bias і запасом)\n", pick * 1e6);

    if (pick > hi) {
        printf("УВАГА: потрібна ємність не долиється за паузу!\n");
        printf("  → знизь R доливу, зменш стелю шпаруватості або візьми зарядову помпу.\n");
    }
    return 0;
}
