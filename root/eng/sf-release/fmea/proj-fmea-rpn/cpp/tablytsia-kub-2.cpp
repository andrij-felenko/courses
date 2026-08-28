constexpr int idx(int s, int o, int d) { return (s - 1) * 100 + (o - 1) * 10 + (d - 1); }

AP letter(char c) {
    switch (c) {
        case 'H': return AP::High;
        case 'M': return AP::Medium;
        case 'L': return AP::Low;
    }
    throw std::invalid_argument(std::string("невідома літера політики: ") + c);
}

// Розгорнути смуги в 1000 клітин — і заразом довести, що таблиця ПОВНА
// (кожне (S,O,D) вкрито) і НЕСУПЕРЕЧЛИВА (жодне не вкрито двічі).
std::array<AP, 1000> compile_policy(const std::vector<SRow>& policy) {
    std::array<std::optional<AP>, 1000> cube{};   // усі клітини порожні
    for (const auto& sr : policy) {
        for (const auto& oc : sr.row) {
            if (oc.letters.size() != D_BANDS.size())
                throw std::invalid_argument(
                    "S=" + std::to_string(sr.s.lo) + "-" + std::to_string(sr.s.hi) +
                    " O=" + std::to_string(oc.o.lo) + "-" + std::to_string(oc.o.hi) +
                    ": " + std::to_string(oc.letters.size()) + " клітин замість " +
                    std::to_string(D_BANDS.size()));
            for (std::size_t k = 0; k < D_BANDS.size(); ++k) {
                const Band db = D_BANDS[k];
                const AP ap = letter(oc.letters[k]);
                for (int s = sr.s.lo; s <= sr.s.hi; ++s)
                  for (int o = oc.o.lo; o <= oc.o.hi; ++o)
                    for (int d = db.lo; d <= db.hi; ++d) {
                        auto& slot = cube[idx(s, o, d)];
                        if (slot)
                            throw std::invalid_argument(
                                "смуги перекриваються на S=" + std::to_string(s) +
                                " O=" + std::to_string(o) + " D=" + std::to_string(d));
                        slot = ap;
                    }
            }
        }
    }
    std::vector<std::array<int, 3>> holes;
    for (int s = 1; s <= 10; ++s)
      for (int o = 1; o <= 10; ++o)
        for (int d = 1; d <= 10; ++d)
            if (!cube[idx(s, o, d)]) holes.push_back({s, o, d});
    if (!holes.empty()) {
        const auto& h = holes.front();
        throw std::invalid_argument(
            "таблиця неповна: " + std::to_string(holes.size()) +
            " клітин без пріоритету, перша з них (" + std::to_string(h[0]) + ", " +
            std::to_string(h[1]) + ", " + std::to_string(h[2]) + ")");
    }
    std::array<AP, 1000> out{};
    for (std::size_t i = 0; i < out.size(); ++i) out[i] = *cube[i];
    return out;
}

const std::array<AP, 1000> AP_CUBE = compile_policy(AP_POLICY);

AP action_priority(int s, int o, int d) {   // Пошук, а не формула: одне індексування, O(1).
    return AP_CUBE[idx(s, o, d)];            // Нічого не множимо.
}
