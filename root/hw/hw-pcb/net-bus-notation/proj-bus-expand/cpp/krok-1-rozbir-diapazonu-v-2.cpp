// Розібрати "D[7..0]" → BusName{"D", 7, 0, true}.
// Запис без дужок ("CLK") — це скаляр: BusName{"CLK", 0, 0, false}.
// Кривий запис ("D[7..]", "D[a..b]") — повертаємо false, хай редактор лається.
static bool parse_bus(const std::string& s, BusName& out) {
    size_t lb = s.find('[');
    if (lb == std::string::npos) {           // дужок нема — звичайний скаляр
        out = { s, 0, 0, false };
        return true;
    }
    size_t dd = s.find("..", lb + 1);        // роздільник діапазону
    size_t rb = s.find(']', lb + 1);         // закрита дужка
    if (dd == std::string::npos || rb == std::string::npos || !(lb < dd && dd < rb))
        return false;                        // нема "..", нема "]", або переплутаний порядок

    out.prefix = s.substr(0, lb);
    std::string a = s.substr(lb + 1, dd - lb - 1);   // між '[' і '..'
    std::string b = s.substr(dd + 2, rb - dd - 2);   // між '..' і ']'
    try {
        out.left  = std::stoi(a);            // кине виняток, якщо не число
        out.right = std::stoi(b);
    } catch (...) {
        return false;                        // "[a..b]" — не діапазон
    }
    out.is_vector = true;
    return true;
}
