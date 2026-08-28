#include <cassert>
#include <map>
#include <string>
#include <type_traits>
#include <vector>

// Один узагальнений доступ, що віддає рівно те, що віддав контейнер.
constexpr auto lookup = [](auto&& c, auto&& k) -> decltype(auto) {
    return c.at(k);
};

// Лічильник копій і переміщень.
struct probe {
    static inline int copies = 0, moves = 0;
    probe() = default;
    probe(const probe&)     { ++copies; }
    probe(probe&&) noexcept { ++moves; }
};
probe  by_value()     { return probe{}; }
probe& by_reference() { static probe p; return p; }

int main() {
    std::chrono::nanoseconds t{};
    std::vector<int>  vi{1, 2, 3};
    std::vector<bool> vb{true, false};
    const std::map<std::string, int> mi{{"a", 1}};

    // 1. Категорія й константність доходять неушкодженими.
    static_assert(std::is_same_v<decltype(timed(t, lookup, vi, 0)),  int&>);
    static_assert(std::is_same_v<decltype(timed(t, lookup, mi, "a")), const int&>);
    static_assert(std::is_same_v<decltype(timed(t, lookup, vb, 0)),
                                 std::vector<bool>::reference>);

    // 2. Крізь обгортку так само пишуть — і в звичайний контейнер, і в посередник.
    timed(t, lookup, vi, 0) = 42;
    timed(t, lookup, vb, 1) = true;
    assert(vi[0] == 42 && vb[1]);

    // 3. Жодної зайвої копії й жодного зайвого переміщення.
    probe::copies = probe::moves = 0;

    probe made = timed(t, by_value);
    assert(probe::copies == 0 && probe::moves == 0);

    probe& same = timed(t, by_reference);
    assert(&same == &by_reference());
    assert(probe::copies == 0 && probe::moves == 0);

    // 4. Обіцянка про винятки — рівно та сама.
    auto quiet = []() noexcept { return 1; };
    auto loud  = []()          { return 1; };
    static_assert( noexcept(timed(t, quiet)));
    static_assert(!noexcept(timed(t, loud)));

    // 5. Для непридатних аргументів обгортка не ламається — вона зникає.
    static_assert(!requires { timed(t, quiet, 1, 2, 3); });

    // 6. Аргументи проходять наскрізь зі своєю категорією.
    auto sink = [](probe) { };   // бере за значенням
    probe src;

    probe::copies = probe::moves = 0;
    timed(t, sink, src);         // lvalue → одна копія, і та вже в самому sink
    assert(probe::copies == 1 && probe::moves == 0);

    probe::copies = probe::moves = 0;
    timed(t, sink, probe{});     // rvalue → жодної копії, одне переміщення
    assert(probe::copies == 0 && probe::moves == 1);
}
