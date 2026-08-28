// Обрізати пробіли/табуляції з обох країв.
static std::string trim(const std::string& s) {
    size_t a = s.find_first_not_of(" \t\r\n");
    if (a == std::string::npos) return "";
    size_t b = s.find_last_not_of(" \t\r\n");
    return s.substr(a, b - a + 1);
}

// Нормалізувати позначення: обрізати краї + ВЕЛИКА літерна частина.
// R7, r7, " R7 " → усі стають "R7", тож у множині вони — один елемент.
static std::string norm_ref(const std::string& raw) {
    std::string s = trim(raw);
    for (char& c : s)
        if (c >= 'a' && c <= 'z') c -= 32;     // до верхнього регістру (ASCII)
    return s;
}
