struct Rating {
    int s, o, d;
    Rating(int s_, int o_, int d_) : s(s_), o(o_), d(d_) {
        auto guard = [](const char* nm, int v) {
            if (v < 1 || v > 10)
                throw std::invalid_argument(
                    std::string(nm) + "=" + std::to_string(v) + ": ранг поза 1…10");
        };
        guard("S", s); guard("O", o); guard("D", d);
    }
    int rpn() const { return s * o * d; }   // для звітів і легасі; у ключ черги НЕ пускаємо
    AP  ap()  const { return action_priority(s, o, d); }
};

struct Entry {
    std::string id;
    std::string item;      // вузол
    std::string function;  // що вузол має робити
    std::string mode;      // вид відмови: як саме не виконав
    std::string cause;     // причина: чому
    std::string effect;    // наслідок: що відчула система
    std::string control;   // чим ловимо це зараз
    Rating before;
    std::string action;
    std::optional<Rating> after;

    Rating current() const { return after ? *after : before; }

    // Захід знижує частоту або виявність. Тяжкість — лише зміною конструкції:
    // наслідок не м'якшає від того, що ми додали перевірку.
    Entry& plan(std::string act, Rating aft, bool design_change = false) {
        if (aft.s < before.s && !design_change)
            throw std::invalid_argument(
                id + ": тяжкість " + std::to_string(before.s) + " → " +
                std::to_string(aft.s) + " без зміни конструкції. Наслідок «" +
                effect + "» лишився той самий — тяжкість не падає від того, "
                "що ми додали перевірку.");
        action = std::move(act);
        after = aft;
        return *this;
    }
};

using Key = std::tuple<int, int, int, int, std::string>;

// Лексикографічно: пріоритет → тяжкість → частота → виявність → id.
// Жодного добутку. id наприкінці — щоб порядок був відтворюваний.
Key priority_key(const Entry& e, bool before = false) {
    const Rating r = before ? e.before : e.current();
    return { -static_cast<int>(r.ap()), -r.s, -r.o, -r.d, e.id };
}

std::vector<Entry> by_priority(std::vector<Entry> rows, bool before = false) {
    std::sort(rows.begin(), rows.end(), [&](const Entry& a, const Entry& b) {
        return priority_key(a, before) < priority_key(b, before);   // O(n log n)
    });
    return rows;
}

std::vector<Entry> by_rpn(std::vector<Entry> rows, bool before = false) {
    // Як роблять зазвичай. Тут — лише щоб було з чим порівняти.
    std::sort(rows.begin(), rows.end(), [&](const Entry& a, const Entry& b) {
        return (before ? a.before : a.current()).rpn()
             > (before ? b.before : b.current()).rpn();
    });
    return rows;
}
