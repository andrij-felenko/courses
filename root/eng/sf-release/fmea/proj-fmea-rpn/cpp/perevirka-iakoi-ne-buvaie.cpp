// Здоровий глузд: погіршення БУДЬ-ЯКОЇ осі не сміє знизити пріоритет.
std::vector<std::string> check_monotone(const std::array<AP, 1000>& cube) {
    std::vector<std::string> bad;
    for (int s = 1; s <= 10; ++s)
      for (int o = 1; o <= 10; ++o)
        for (int d = 1; d <= 10; ++d) {
            const AP here = cube[idx(s, o, d)];
            struct Step { const char* axis; int s, o, d; };
            const Step steps[3] = {{"S", s + 1, o, d}, {"O", s, o + 1, d}, {"D", s, o, d + 1}};
            for (const Step& st : steps) {
                if (st.s > 10 || st.o > 10 || st.d > 10) continue;
                const AP there = cube[idx(st.s, st.o, st.d)];
                if (there < here)                        // enum class порівнюється, не додається
                    bad.push_back(
                        std::string(st.axis) + "↑: (" + std::to_string(s) + "," +
                        std::to_string(o) + "," + std::to_string(d) + ")=" + name(here) +
                        " → (" + std::to_string(st.s) + "," + std::to_string(st.o) + "," +
                        std::to_string(st.d) + ")=" + name(there));
            }
        }
    return bad;
}
