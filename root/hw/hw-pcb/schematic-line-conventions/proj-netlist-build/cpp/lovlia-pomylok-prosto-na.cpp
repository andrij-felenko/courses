// Відстань Левенштайна: скільки правок (вставити/вилучити/замінити літеру)
// перетворюють a на b. Імена з відстанню 1 — кандидати на одрук.
static int lev(const std::string& a, const std::string& b) {
    std::vector<int> d(b.size() + 1);
    for (size_t j = 0; j <= b.size(); ++j) d[j] = (int)j;
    for (size_t i = 1; i <= a.size(); ++i) {
        int prev = d[0]; d[0] = (int)i;
        for (size_t j = 1; j <= b.size(); ++j) {
            int cur = d[j];
            d[j] = std::min({ d[j] + 1,                       // вилучити
                              d[j - 1] + 1,                   // вставити
                              prev + (a[i-1] != b[j-1]) });   // замінити
            prev = cur;
        }
    }
    return d[b.size()];
}

// Попередити про пари іменованих ланцюгів, чиї імена відрізняються на 1 правку.
static void warn_typos(const std::vector<Net>& nets) {
    for (size_t i = 0; i < nets.size(); ++i)
        for (size_t j = i + 1; j < nets.size(); ++j) {
            const std::string& a = nets[i].name, & b = nets[j].name;
            if (a.rfind("Net-",0)==0 || b.rfind("Net-",0)==0) continue; // лише іменовані
            if (a.size() == b.size() && lev(a, b) == 1)
                printf("ПОПЕРЕДЖЕННЯ: '%s' і '%s' схожі — одрук в імені?\n",
                       a.c_str(), b.c_str());
        }
}
