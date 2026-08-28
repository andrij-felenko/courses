// ── 2а. Перетворювачі: у віджеті завжди рядок ──
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <string>

std::string numToText(const double& v) {
    if (v != v) return "";                       // NaN — порожнє поле
    char buf[32];
    std::snprintf(buf, sizeof buf, "%g", v);
    return buf;
}

double textToNum(const std::string& s) {
    const char* first = s.c_str();
    char* last = nullptr;
    const double v = std::strtod(first, &last);
    if (last == first || *last != '\0')          // порожнє чи сміття — НЕ нуль
        return std::numeric_limits<double>::quiet_NaN();
    return v;
}
