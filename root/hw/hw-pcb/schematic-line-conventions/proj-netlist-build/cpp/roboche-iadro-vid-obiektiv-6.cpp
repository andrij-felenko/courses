// Розгорнути векторну шину "DATA[0..7]" → ["DATA0","DATA1",...,"DATA7"].
// Якщо запис не схожий на шину — повертаємо саме ім'я як єдиний член.
static std::vector<std::string> expand_bus(const std::string& name) {
    size_t lb = name.find('[');
    size_t dd = name.find("..", lb == std::string::npos ? 0 : lb);
    size_t rb = name.find(']', dd == std::string::npos ? 0 : dd);
    if (lb == std::string::npos || dd == std::string::npos || rb == std::string::npos
        || !(lb < dd && dd < rb)) {
        return { name };                               // не шина — звичайна мітка
    }
    std::string prefix = name.substr(0, lb);
    int lo = std::stoi(name.substr(lb + 1, dd - lb - 1));
    int hi = std::stoi(name.substr(dd + 2, rb - dd - 2));
    int step = (lo <= hi) ? 1 : -1;                    // діапазон може й спадати
    std::vector<std::string> members;
    for (int i = lo; ; i += step) {
        members.push_back(prefix + std::to_string(i)); // DATA0, DATA1, ...
        if (i == hi) break;
    }
    return members;
}
