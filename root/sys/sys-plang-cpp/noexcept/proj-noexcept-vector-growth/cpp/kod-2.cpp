// Яку послідовність місткостей дає ваша стандартна бібліотека.
std::vector<std::size_t> capacity_trace(std::size_t n) {
    std::vector<std::size_t> caps;
    std::vector<char> v;          // стратегія зростання рахується в елементах,
    for (std::size_t i = 0; i < n; ++i) {   // тому тип елемента тут не важить
        v.push_back(0);
        if (caps.empty() || v.capacity() != caps.back())
            caps.push_back(v.capacity());
    }
    return caps;
}

void report(const char* label, const Run& r) {
    std::cout << std::left << std::setw(24) << label << std::right
              << " побудов "     << std::setw(6) << r.c.ctor
              << "   копій "     << std::setw(6) << r.c.copy
              << "   переміщень "<< std::setw(6) << r.c.move
              << "   знищень "   << std::setw(6) << r.c.dtor
              << "   час "       << std::setw(8) << std::fixed
              << std::setprecision(2) << r.seconds * 1e3 << " мс\n";
}

int main() {
    const std::size_t N = 8000;   // скільки елементів додаємо
    const std::size_t P = 64;     // скільки double у кожному елементі
    const int         R = 7;      // повторів на варіант

    std::cout << "місткості: ";
    for (std::size_t c : capacity_trace(N)) std::cout << c << ' ';
    std::cout << "\n\n";

    const Run slow   = best_of<false>(R, N, P, false);
    const Run fast   = best_of<true >(R, N, P, false);
    const Run slow_r = best_of<false>(R, N, P, true);
    const Run fast_r = best_of<true >(R, N, P, true);

    report("без noexcept",           slow);
    report("з noexcept",             fast);
    report("без noexcept + reserve", slow_r);
    report("з noexcept + reserve",   fast_r);

    std::cout << "\nповільніше в " << slow.seconds / fast.seconds << " раза\n"
              << "checksum " << slow.checksum + fast.checksum
                              + slow_r.checksum + fast_r.checksum << '\n';
}
