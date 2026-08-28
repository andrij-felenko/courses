#include <algorithm>
#include <cmath>
#include <cstdio>
#include <limits>
#include <string>
#include <utility>
#include <vector>

struct Amp {
    const char *name;
    double vos25;    // В: зсув напруги, паспортний МАКСИМУМ за 25 °C
    double tcvos;    // В/°C: максимальний дрейф зсуву напруги
    double ib25;     // А: середній вхідний струм, максимум за 25 °C
    double ios25;    // А: струм неузгодженості, максимум за 25 °C
    double t_flat;   // °C: доки струм сталий; вище — подвоєння на кожні 10 °C
};

struct Circuit {
    double r_plus;      // Ом: опір постійному струмові з «плюс»-входу
    double r_minus;     // Ом: те саме з «мінус»-входу
    double noise_gain;  // у стільки разів похибка входу росте на виході
    double swing;       // В: скільки вихід може відійти від робочої точки
};

struct Error {
    double vos;    // знімається калібруванням самого приладу
    double cur;    // знімається лише разом із датчиком
    double drift;  // не знімається нічим — межа точності
    double total() const { return vos + cur + drift; }
};

// Струми входу за температури t: витік подвоюється кожні 10 °C вище t_flat.
static void bias_at(const Amp &a, double t, double *ib, double *ios) {
    double over = t - a.t_flat;
    double k = (over <= 0.0) ? 1.0 : std::pow(2.0, over / 10.0);
    *ib  = a.ib25  * k;
    *ios = a.ios25 * k;
}

// Похибка, зведена до входу. Знаки доданків наперед невідомі,
// тож найгірший випадок — сума модулів.
static Error dc_error(const Amp &a, const Circuit &c, double t) {
    double ib, ios;
    bias_at(a, t, &ib, &ios);
    double dr = std::fabs(c.r_plus - c.r_minus);  // різниця опорів — на неї діє I_B
    double sr = c.r_plus + c.r_minus;             // сума опорів    — на неї діє I_os

    Error e;
    e.vos   = a.vos25;
    e.cur   = a.ib25 * dr + 0.5 * a.ios25 * sr;
    e.drift = a.tcvos * std::fabs(t - 25.0)
            + (ib - a.ib25) * dr
            + 0.5 * (ios - a.ios25) * sr;
    return e;
}

// Найгірше по діапазону. Кожен доданок опуклий за t (модуль і показникова),
// а максимум опуклої функції на відрізку — на його кінці. Тож двох точок досить.
static Error worst_case(const Amp &a, const Circuit &c, double tmin, double tmax) {
    Error lo = dc_error(a, c, tmin), hi = dc_error(a, c, tmax);
    return (hi.total() > lo.total()) ? hi : lo;
}
