// Розділити позначення на літерний префікс і числовий хвіст: "R12" → ("R",12).
// Якщо хвіст не число — number = -1 (не діапазонне позначення).
static void split_ref(const std::string& r, std::string& prefix, int& number) {
    size_t i = 0;
    while (i < r.size() && !(r[i] >= '0' && r[i] <= '9')) ++i;   // префікс — до першої цифри
    prefix = r.substr(0, i);
    if (i == r.size()) { number = -1; return; }                 // цифр немає
    number = 0;
    for (; i < r.size(); ++i) {
        if (!(r[i] >= '0' && r[i] <= '9')) { number = -1; return; } // хвіст не чисто числовий
        number = number * 10 + (r[i] - '0');
    }
}

// Розгорнути "R1-R4" → {"R1","R2","R3","R4"}. Якщо це не діапазон — повернути сам токен.
// Працює лише коли префікси збігаються (R..R), а хвости — числа.
static std::vector<std::string> expand_range(const std::string& token) {
    size_t dash = token.find('-');
    if (dash == std::string::npos)
        return { token };                                       // не діапазон

    std::string lo_s = norm_ref(token.substr(0, dash));
    std::string hi_s = norm_ref(token.substr(dash + 1));
    std::string lp, hp; int ln, hn;
    split_ref(lo_s, lp, ln);
    split_ref(hi_s, hp, hn);

    // Діапазон правомірний лише якщо обидва боки — позначення з ОДНАКОВИМ префіксом.
    if (ln < 0 || hn < 0 || lp.empty() || lp != hp)
        return { norm_ref(token) };                             // не схоже на діапазон — як є

    std::vector<std::string> out;
    int step = (ln <= hn) ? 1 : -1;                             // діапазон може й спадати
    for (int n = ln; ; n += step) {
        out.push_back(lp + std::to_string(n));                  // R1, R2, ...
        if (n == hn) break;
    }
    return out;
}
