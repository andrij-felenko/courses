// Те саме серце мовою C++: розбір рядка й згортка avail(k).
// Збірка: c++ -O2 -std=c++20 -o budinfo budinfo.cpp
#include <charconv>
#include <string>
#include <string_view>
#include <vector>

struct ZoneRow {
    int node{};
    std::string name;
    std::vector<unsigned long> nr_free;   // довжину задає ядро, не ми
    std::vector<unsigned long> avail;
    unsigned long free_pages{};
    int top{-1};
};

static std::vector<unsigned long> numbers(std::string_view s)
{
    std::vector<unsigned long> v;
    while (!s.empty()) {
        while (!s.empty() && (s.front() == ' ' || s.front() == '\t'))
            s.remove_prefix(1);
        unsigned long x{};
        auto [p, ec] = std::from_chars(s.data(), s.data() + s.size(), x);
        if (ec != std::errc{}) break;     // чисел більше немає
        v.push_back(x);
        s.remove_prefix(static_cast<std::size_t>(p - s.data()));
    }
    return v;
}

static bool parse_row(std::string_view line, ZoneRow &r)
{
    auto n = line.find("Node ");
    if (n == std::string_view::npos) return false;
    line.remove_prefix(n + 5);

    unsigned long id{};
    auto [p, ec] = std::from_chars(line.data(), line.data() + line.size(), id);
    if (ec != std::errc{}) return false;
    r.node = static_cast<int>(id);
    line.remove_prefix(static_cast<std::size_t>(p - line.data()));

    auto z = line.find("zone");
    if (z == std::string_view::npos) return false;
    line.remove_prefix(z + 4);
    while (!line.empty() && line.front() == ' ') line.remove_prefix(1);
    auto end = line.find(' ');
    if (end == std::string_view::npos || end == 0) return false;
    r.name = line.substr(0, end);
    line.remove_prefix(end);

    r.nr_free = numbers(line);
    return !r.nr_free.empty();
}

// avail(k) = 2·avail(k+1) + nr_free[k] — одним проходом згори вниз.
static void analyze(ZoneRow &r)
{
    r.avail.assign(r.nr_free.size(), 0);
    unsigned long acc = 0;
    for (std::size_t i = r.nr_free.size(); i-- > 0; ) {
        acc = acc * 2 + r.nr_free[i];
        r.avail[i] = acc;
    }
    r.free_pages = r.avail.front();
    r.top = -1;
    for (std::size_t i = 0; i < r.nr_free.size(); ++i)
        if (r.nr_free[i]) r.top = static_cast<int>(i);
}
