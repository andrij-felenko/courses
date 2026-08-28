struct Unit { double scale; const char *name; };
static const Unit VOLT[] = {{1.0,"В"},{1e-3,"мВ"},{1e-6,"мкВ"},{1e-9,"нВ"},{1e-12,"пВ"}};
static const Unit OHM[]  = {{1e9,"ГОм"},{1e6,"МОм"},{1e3,"кОм"},{1.0,"Ом"}};

static std::string eng(double v, const Unit *u, size_t n) {
    char buf[32];
    double a = std::fabs(v);
    for (size_t i = 0; i < n; ++i)
        if (a >= u[i].scale) {
            std::snprintf(buf, sizeof buf, "%.1f %s", v / u[i].scale, u[i].name);
            return buf;
        }
    std::snprintf(buf, sizeof buf, "0 %s", u[n - 1].name);
    return buf;
}
static std::string volts(double v) { return eng(v, VOLT, sizeof VOLT / sizeof *VOLT); }
static std::string ohms(double v)  { return eng(v, OHM,  sizeof OHM  / sizeof *OHM);  }

// printf вирівнює по БАЙТАХ, а кирилиця в UTF-8 займає по два байти на літеру —
// без цього стовпці таблиці розповзуться. Рахуємо ширину в символах.
static std::string pad(const std::string &s, size_t w, bool left = false) {
    size_t n = 0;
    for (unsigned char ch : s)
        if ((ch & 0xC0) != 0x80) ++n;      // рахуємо лише перші байти символів
    if (n >= w) return s;
    std::string sp(w - n, ' ');
    return left ? s + sp : sp + s;
}

typedef std::pair<Error, const Amp *> Row;

static void report(const std::vector<Amp> &amps, const Circuit &c,
                   double tmin, double tmax, double budget, const char *title) {
    std::printf("%s: R⁺ = %s, R⁻ = %s, %g…%g °C, бюджет на вході %s\n",
                title, ohms(c.r_plus).c_str(), ohms(c.r_minus).c_str(),
                tmin, tmax, volts(budget).c_str());
    std::printf("    %s %s %s %s %s   вирок\n",
                pad("прилад", 11, true).c_str(), pad("V_os", 9).c_str(),
                pad("струм·R", 9).c_str(), pad("дрейф", 9).c_str(), pad("разом", 9).c_str());

    std::vector<Row> rows;
    for (size_t i = 0; i < amps.size(); ++i)
        rows.push_back(Row(worst_case(amps[i], c, tmin, tmax), &amps[i]));
    std::sort(rows.begin(), rows.end(),
              [](const Row &x, const Row &y) { return x.first.total() < y.first.total(); });

    for (size_t i = 0; i < rows.size(); ++i) {
        const Error &e = rows[i].first;
        const Amp &a = *rows[i].second;
        std::string verdict;
        if ((e.vos + e.cur) * c.noise_gain > c.swing)
            verdict = "вихід у насиченні — схема не працює";
        else if (e.total() <= budget)
            verdict = "проходить як є";
        else if (e.cur + e.drift <= budget)
            verdict = "треба калібрувати нуль приладу";
        else if (e.drift <= budget)
            verdict = "треба калібрувати в зборі з датчиком";
        else {
            char b[96];   // байтів, а не літер: кирилиця в UTF-8 займає по два
            std::snprintf(b, sizeof b, "не проходить: ×%.0f над бюджетом", e.total() / budget);
            verdict = b;
        }
        double rc = comp_resistor(a, c);
        if (rc > 0.0) verdict += "; спробуй Rc = " + ohms(rc);

        std::printf("    %s %s %s %s %s   %s\n",
                    pad(a.name, 11, true).c_str(), pad(volts(e.vos), 9).c_str(),
                    pad(volts(e.cur), 9).c_str(), pad(volts(e.drift), 9).c_str(),
                    pad(volts(e.total()), 9).c_str(), verdict.c_str());
    }
    std::putchar('\n');
}

int main() {
    const double INF = std::numeric_limits<double>::infinity();
    const std::vector<Amp> amps = {
        //  назва          V_os     TC V_os    I_B       I_os     T_flat
        { "µA741",         6e-3,    20e-6,    500e-9,   200e-9,   INF  },
        { "OP07E",        75e-6,     1.3e-6,    4e-9,     3.8e-9, INF  },
        { "LF356",        10e-3,     5e-6,    200e-12,   50e-12,  25.0 },
        { "OPA333",       10e-6,     0.05e-6, 200e-12,  400e-12,  85.0 },
        { "ADA4530-1",    50e-6,     0.13e-6,  20e-15,   40e-15,  85.0 },
    };

    // 1. pH-метр: скляний електрод 200 МОм на повторювачі, 0…50 °C,
    //    бюджет 0.01 pH = 0.01 · 59.16 мВ/pH.
    Circuit ph = { 200e6, 0.0, 1.0, 10.0 };
    report(amps, ph, 0.0, 50.0, 0.01 * 59.16e-3, "pH-метр");

    // 2. Термопара K: 50 Ом з обох боків, підсилення 100, 0…60 °C,
    //    бюджет 0.5 °C = 0.5 · 41 мкВ/°C.
    Circuit tc = { 50.0, 50.0, 100.0, 4.0 };
    report(amps, tc, 0.0, 60.0, 0.5 * 41e-6, "Термопара K");

    // 3. Буфер ×1 перед 16-бітним АЦП, джерело 10 кОм: бюджет задає чверть LSB.
    Circuit buf = { 10e3, 10e3, 1.0, 4.0 };
    report(amps, buf, 0.0, 60.0,
           budget_from_adc(4.096, 16, 0.25, buf.noise_gain), "Буфер 10 кОм перед 16-бітним АЦП");

    // 4. Датчик 1 МОм на неінвертувальному ×10 (R⁻ = 10к ‖ 90к = 9 кОм), 25…85 °C.
    Circuit raw = { 1e6, 9e3, 10.0, 10.0 };
    report(amps, raw, 25.0, 85.0, 1e-3, "Датчик 1 МОм, опори НЕ зрівняні");
    report(amps, balanced(raw), 25.0, 85.0, 1e-3, "Датчик 1 МОм, опори зрівняні");
    return 0;
}
