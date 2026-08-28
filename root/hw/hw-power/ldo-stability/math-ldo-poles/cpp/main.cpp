#include <cmath>
#include <cstdio>

// ── Мала-сигнальна петля LDO: два полюси + нуль ESR ─────────────────
constexpr double PI    = 3.14159265358979323846;
constexpr double VT    = 0.02585;      // тепловий потенціал при 27 °C, В
constexpr double N_SUB = 1.3;          // коефіцієнт нахилу підпорогової ділянки
constexpr double V_OUT = 3.3;          // напруга виходу, В
constexpr double V_REF = 1.2;          // опорна напруга, В
constexpr double BETA  = V_REF / V_OUT;   // частка виходу, що вертається в петлю
constexpr double A_EA  = 200.0;        // підсилення підсилювача похибки
constexpr double R_EA  = 200e3;        // його вихідний опір, Ом
constexpr double C_G   = 20e-12;       // ємність затвора прохідного транзистора, Ф
constexpr double C_OUT = 1e-6;         // вихідний конденсатор, Ф

const double F_P2 = 1.0 / (2 * PI * R_EA * C_G);   // полюс вузла A — від струму не залежить

// Крутість прохідного PMOS: сильна інверсія ∝ √I, слабка — стеля I/(n·VT).
double gm_pass(double i_load)
{
    constexpr double V_OV_FULL = 0.4, I_FULL = 0.5;
    constexpr double k = 2 * I_FULL / (V_OV_FULL * V_OV_FULL);   // параметр приладу, А/В²
    return std::fmin(std::sqrt(2 * k * i_load), i_load / (N_SUB * VT));
}

struct Loop { double mag; double deg; };

Loop loop(double f, double i_load, double esr)
{
    const double r_out = V_OUT / i_load;                  // опір вузла виходу
    const double f_p1  = 1.0 / (2 * PI * r_out * C_OUT);  // полюс виходу
    const double f_z   = 1.0 / (2 * PI * esr * C_OUT);    // нуль ESR
    const double t0    = A_EA * gm_pass(i_load) * r_out * BETA;
    const double mag   = t0 * std::hypot(1.0, f / f_z)
                       / (std::hypot(1.0, f / f_p1) * std::hypot(1.0, f / F_P2));
    const double rad   = std::atan(f / f_z) - std::atan(f / f_p1) - std::atan(f / F_P2);
    return { mag, rad * 180.0 / PI };
}

// Частота зрізу — де модуль петлі падає до одиниці (ділення навпіл по логарифму).
double crossover(double i_load, double esr)
{
    double lo = 1.0, hi = 1e9;
    for (int i = 0; i < 200; ++i) {
        const double mid = std::sqrt(lo * hi);
        if (loop(mid, i_load, esr).mag > 1.0) lo = mid; else hi = mid;
    }
    return std::sqrt(lo * hi);
}

int main()
{
    constexpr double I = 1e-3;                    // найтяжчий кут: легке навантаження
    const struct { const char *name; double esr; } caps[] = {
        { "тантал",   1.0   },
        { "кераміка", 0.005 },
    };
    for (const auto &c : caps) {
        const double f_c = crossover(I, c.esr);
        std::printf("%s: ESR=%5.3f Ом, нуль=%8.1f кГц, зріз=%6.1f кГц, запас фази=%4.1f°\n",
                    c.name, c.esr, 1.0 / (2 * PI * c.esr * C_OUT) / 1e3,
                    f_c / 1e3, 180.0 + loop(f_c, I, c.esr).deg);
    }
}
