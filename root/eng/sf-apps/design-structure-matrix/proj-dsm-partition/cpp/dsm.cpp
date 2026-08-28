// dsm.cpp — розбиття матриці залежностей.
// g++ -std=c++20 -O2 -o dsm dsm.cpp
//   ./dsm deps.txt
//   ./dsm deps.txt --baseline cycles.txt        (новий блок → код повернення 2)
//   ./dsm deps.txt --write-baseline cycles.txt

#include <algorithm>
#include <bit>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <queue>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using Word = std::uint64_t;
static constexpr int WBITS = 64;

struct Input {
    std::vector<std::string> name;              // id → ім'я, за абеткою
    std::vector<std::pair<int, int>> edge;      // (хто потребує, кого потребує)
    std::vector<char> loop;                     // петля сам-на-себе
    long long dup = 0, self = 0;                // скільки відкинуто
};

static std::string trim(const std::string& s) {
    const size_t a = s.find_first_not_of(" \t\r\n");
    if (a == std::string::npos) return {};
    return s.substr(a, s.find_last_not_of(" \t\r\n") - a + 1);
}

static Input read_edges(std::istream& in) {
    std::unordered_map<std::string, int> seen;
    std::vector<std::string> raw;
    std::vector<std::pair<int, int>> arc;

    auto id_of = [&](const std::string& s) {
        const auto [it, fresh] = seen.emplace(s, (int)raw.size());
        if (fresh) raw.push_back(s);
        return it->second;
    };

    std::string line;
    while (std::getline(in, line)) {
        if (const size_t h = line.find('#'); h != std::string::npos) line.resize(h);
        const size_t arrow = line.find("->");
        if (arrow == std::string::npos) {
            const std::string lone = trim(line);       // елемент без залежностей
            if (!lone.empty()) id_of(lone);
            continue;
        }
        const std::string a = trim(line.substr(0, arrow));
        const std::string b = trim(line.substr(arrow + 2));
        if (!a.empty() && !b.empty()) arc.emplace_back(id_of(a), id_of(b));
    }

    // Перенумерація за абеткою: номер елемента більше не залежить від того,
    // у якому порядку видобувач виплюнув рядки, — отже, не залежить і вивід.
    const int n = (int)raw.size();
    std::vector<int> byname(n);
    for (int i = 0; i < n; ++i) byname[i] = i;
    std::sort(byname.begin(), byname.end(),
              [&](int x, int y) { return raw[x] < raw[y]; });

    Input g;
    g.name.resize(n);
    std::vector<int> newid(n);
    for (int k = 0; k < n; ++k) { newid[byname[k]] = k; g.name[k] = raw[byname[k]]; }

    g.edge.reserve(arc.size());
    for (const auto& e : arc) g.edge.emplace_back(newid[e.first], newid[e.second]);

    std::sort(g.edge.begin(), g.edge.end());
    g.edge.erase(std::unique(g.edge.begin(), g.edge.end()), g.edge.end());
    g.dup = (long long)arc.size() - (long long)g.edge.size();

    g.loop.assign(n, 0);                          // петлі геть з матриці, але в облік
    std::vector<std::pair<int, int>> keep;
    keep.reserve(g.edge.size());
    for (const auto& e : g.edge) {
        if (e.first == e.second) { g.loop[e.first] = 1; ++g.self; }
        else keep.push_back(e);
    }
    g.edge.swap(keep);
    return g;
}
