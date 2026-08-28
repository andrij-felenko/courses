#include <vector>
#include <cstddef>

// Пошук з ітеративним уполовиненням шляху (Path Halving) на C++
std::size_t find_path_halving(std::vector<std::size_t>& parent, std::size_t x) noexcept {
    while (parent[x] != x) {
        parent[x] = parent[parent[x]];
        x = parent[x];
    }
    return x;
}

// Пошук з розщепленням шляху (Path Splitting) на C++
std::size_t find_path_splitting(std::vector<std::size_t>& parent, std::size_t x) noexcept {
    while (parent[x] != x) {
        const std::size_t next = parent[x];
        parent[x] = parent[next];
        x = next;
    }
    return x;
}
