#include <cmath>
#include <cstdio>
#include <limits>
#include <memory>
#include <string>
#include <utility>
#include <vector>

// Коло, у якому працює ключ, і бюджет, у який він мусить улізти.
struct Circuit {
    double v_bus;    // напруга шини, В
    double i_load;   // струм навантаження, А
    double duty;     // шпаруватість — частка часу у відкритому стані
    double t_amb;    // температура довкілля всередині корпусу, °C
    double t_j_max;  // проєктна межа температури кристала, °C
    double v_drive;  // амплітуда керування затвором, В
    double i_drive;  // струм драйвера затвора, А
};

// Чотири рахунки нарізно — щоб бачити, хто саме гріє.
struct Losses {
    double cond = 0.0, sw = 0.0, drive = 0.0, leak = 0.0;
    double total() const { return cond + sw + drive + leak; }
};

// Спільний інтерфейс: калькулятор не мусить знати, ЧИМ саме клацають.
struct Switch {
    std::string name;
    double r_th;                       // тепловий опір кристал → довкілля, K/Вт

    virtual ~Switch() = default;
    virtual double edge_time(const Circuit& c) const = 0;
    virtual Losses losses(const Circuit& c, double f, double t_j) const = 0;

protected:
    Switch(std::string n, double rth) : name(std::move(n)), r_th(rth) {}
};

struct Mosfet : Switch {
    double r_on_25;    // опір відкритого каналу при 25 °C, Ω
    double r_on_k;     // R_ON(125 °C)/R_ON(25 °C) — з нормованого графіка даташита
    double q_g;        // повний заряд затвора, Кл
    double q_gd;       // заряд Міллера (затвор–стік), Кл
    double i_leak_25;  // витік закритого ключа при 25 °C, А
    double leak_k;     // I_вит(125 °C)/I_вит(25 °C) — теж із графіка даташита

    Mosfet(std::string n, double r25, double k, double qg, double qgd,
           double ileak, double lk, double rth)
        : Switch(std::move(n), rth), r_on_25(r25), r_on_k(k), q_g(qg),
          q_gd(qgd), i_leak_25(ileak), leak_k(lk) {}

    // Фронт триває рівно стільки, скільки драйвер вигрібає заряд Міллера.
    double edge_time(const Circuit& c) const override { return q_gd / c.i_drive; }

    Losses losses(const Circuit& c, double f, double t_j) const override {
        const double r_on   = r_on_25 * std::pow(r_on_k, (t_j - 25.0) / 100.0);
        const double e_edge = 0.5 * c.v_bus * c.i_load * edge_time(c);
        const double i_leak = i_leak_25 * std::pow(leak_k, (t_j - 25.0) / 100.0);
        Losses p;
        p.cond  = c.i_load * c.i_load * r_on * c.duty;
        p.sw    = 2.0 * f * e_edge;
        p.drive = q_g * c.v_drive * f;
        p.leak  = c.v_bus * i_leak * (1.0 - c.duty);
        return p;
    }
};

struct Bjt : Switch {
    double v_sat_25;   // напруга насичення при 25 °C і робочому струмі, В
    double v_sat_tc;   // температурний коефіцієнт напруги насичення, В/°C
    double i_base;     // струм бази за форсованого β, А
    double v_be;       // напруга база–емітер у насиченні, В
    double t_edge;     // фронт: у біполярного його задає розсмоктування, с
    double i_leak_25;
    double leak_k;

    Bjt(std::string n, double vsat, double tc, double ib, double vbe,
        double tedge, double ileak, double lk, double rth)
        : Switch(std::move(n), rth), v_sat_25(vsat), v_sat_tc(tc), i_base(ib),
          v_be(vbe), t_edge(tedge), i_leak_25(ileak), leak_k(lk) {}

    double edge_time(const Circuit&) const override { return t_edge; }

    Losses losses(const Circuit& c, double f, double t_j) const override {
        const double v_sat  = v_sat_25 + v_sat_tc * (t_j - 25.0);
        const double e_edge = 0.5 * c.v_bus * c.i_load * t_edge;
        const double i_leak = i_leak_25 * std::pow(leak_k, (t_j - 25.0) / 100.0);
        Losses p;
        p.cond  = v_sat * c.i_load * c.duty;
        p.sw    = 2.0 * f * e_edge;
        p.drive = i_base * v_be * c.duty;      // база просить струм увесь час
        p.leak  = c.v_bus * i_leak * (1.0 - c.duty);
        return p;
    }
};

enum class Verdict { Ok, TooHot, Runaway, NotASwitch };

const char* verdict_name(Verdict v) {
    switch (v) {
        case Verdict::Ok:         return "вкладається";
        case Verdict::TooHot:     return "перегрів";
        case Verdict::Runaway:    return "розгін";
        case Verdict::NotASwitch: return "вже не ключ";
    }
    return "?";
}

struct Result {
    Verdict verdict;
    double t_j;
    double gain;      // підсилення петлі, зчитане з самої ітерації
    Losses losses;
};

constexpr int    MAX_STEPS  = 10000;
constexpr double TOL        = 1e-4;   // K — дрібніше дробити температуру немає сенсу
constexpr double T_CEILING  = 300.0;  // °C — вище кремнію не буває, там модель уже казка
constexpr double EDGE_LIMIT = 0.2;    // найбільша частка періоду, віддана фронтам

// Яку частку періоду з'їдають обидва фронти.
double transition_share(const Switch& sw, const Circuit& c, double f) {
    return 2.0 * sw.edge_time(c) * f;
}

// Стала температура кристала з рівняння T = T_amb + Rθ·P(f, T).
//
// Ітеруємо ВІД ДОВКІЛЛЯ ВГОРУ — це не «обраний за зручністю метод», а модель
// самого нагріву: холодний кристал вмикають, він гріється, нагрів піднімає
// втрати, більші втрати піднімають нагрів. Кожен крок — оберт справжньої петлі.
Result settle(const Switch& sw, const Circuit& c, double f) {
    const double nan = std::numeric_limits<double>::quiet_NaN();
    const double inf = std::numeric_limits<double>::infinity();

    if (transition_share(sw, c, f) > EDGE_LIMIT)
        return {Verdict::NotASwitch, nan, nan, Losses{nan, nan, nan, nan}};

    double t = c.t_amb, prev_step = -1.0, gain = 0.0;
    Losses p{};
    for (int i = 0; i < MAX_STEPS; ++i) {
        p = sw.losses(c, f, t);
        const double t_next = c.t_amb + sw.r_th * p.total();
        if (t_next > T_CEILING)
            return {Verdict::Runaway, inf, std::fmax(gain, 1.0), p};
        const double step = t_next - t;
        if (prev_step > TOL) {
            gain = step / prev_step;       // підсилення петлі — задарма, з самих кроків
            if (gain >= 1.0) return {Verdict::Runaway, inf, gain, p};
        }
        if (step < TOL) {
            const Verdict v = (t_next <= c.t_j_max) ? Verdict::Ok : Verdict::TooHot;
            return {v, t_next, gain, sw.losses(c, f, t_next)};
        }
        prev_step = step;
        t = t_next;
    }
    return {Verdict::Runaway, inf, gain, p};
}

// Найбільша частота, за якої ключ ще вкладається в бюджет.
//
// Утрати ростуть із частотою, температура — з утрат, тож «вкладається»
// вимикається раз і назавжди: предикат монотонний, його можна ділити навпіл.
double f_ceiling(const Switch& sw, const Circuit& c,
                 double f_hi = 20e6, double tol_hz = 100.0) {
    if (settle(sw, c, 0.0).verdict != Verdict::Ok) return 0.0;  // не тягне й на «постійці»
    if (settle(sw, c, f_hi).verdict == Verdict::Ok) return f_hi; // стеля вища за діапазон
    double lo = 0.0, hi = f_hi;
    while (hi - lo > tol_hz) {
        const double mid = 0.5 * (lo + hi);
        if (settle(sw, c, mid).verdict == Verdict::Ok) lo = mid;
        else                                           hi = mid;
    }
    return lo;
}

int main() {
    const Circuit box{12.0, 3.0, 0.5, 40.0, 125.0, 10.0, 0.5};

    std::vector<std::unique_ptr<Switch>> shelf;
    shelf.push_back(std::make_unique<Mosfet>("SOT-23, дрібний",
        68e-3, 1.7, 8e-9, 2.5e-9, 1e-6, 50.0, 250.0));
    shelf.push_back(std::make_unique<Mosfet>("SO-8, середній",
        25e-3, 1.7, 20e-9, 6e-9, 1e-6, 50.0, 62.0));
    shelf.push_back(std::make_unique<Mosfet>("SO-8, міліомний",
        6e-3, 1.9, 65e-9, 20e-9, 5e-6, 50.0, 62.0));
    shelf.push_back(std::make_unique<Bjt>("DPAK, біполярний",
        0.25, 0.6e-3, 0.15, 1.0, 400e-9, 1e-6, 50.0, 70.0));

    for (const auto& sw : shelf) {
        const double pencil = box.t_amb + sw->r_th * sw->losses(box, 20e3, 25.0).total();
        const Result r = settle(*sw, box, 20e3);
        const double f = f_ceiling(*sw, box);

        std::printf("%s\n", sw->name.c_str());
        std::printf("  олівцем при 25 °C : T_j = %.0f °C\n", pencil);
        std::printf("  чесно на 20 кГц   : %s, M = %.3f", verdict_name(r.verdict), r.gain);
        if (std::isfinite(r.t_j)) std::printf("   T_j = %.0f °C", r.t_j);
        std::printf("\n");
        if (f == 0.0) std::printf("  стеля частоти     : немає жодної придатної\n");
        else          std::printf("  стеля частоти     : %.0f кГц\n", f / 1e3);
        if (r.verdict == Verdict::Ok)
            std::printf("  розклад, Вт       : провідність %.3f · перехід %.3f"
                        " · керування %.3f · витік %.4f  →  разом %.3f\n",
                        r.losses.cond, r.losses.sw, r.losses.drive,
                        r.losses.leak, r.losses.total());
    }
    return 0;
}
