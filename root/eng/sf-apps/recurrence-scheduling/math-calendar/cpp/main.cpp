// C++: '/' обтинає в бік нуля, тож від'ємні роки треба зміщувати вручну
constexpr int days_from_civil(int y, int m, int d) noexcept {
    const int k = (m > 2) ? m - 3 : m + 9;          // Бер→0 … Гру→9, Січ→10, Лют→11
    y -= (m <= 2);                                  // січень і лютий — кінець попереднього року
    const int era = (y >= 0 ? y : y - 399) / 400;   // зсув −399 імітує підлогу
    const int yoe = y - era * 400;                  // [0, 399]
    const int doy = (153 * k + 2) / 5 + d - 1;      // [0, 365]
    const int doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;   // [0, 146096]
    return era * 146097 + doe - 719468;
}
