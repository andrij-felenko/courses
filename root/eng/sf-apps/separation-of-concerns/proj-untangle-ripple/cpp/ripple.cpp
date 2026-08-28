// ripple.cpp — радіус вибуху зміни за графом одиниць коду.
// Збірка: g++ -std=c++17 -O2 -o ripple ripple.cpp
// Запуск: ./ripple model.units

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <map>
#include <queue>
#include <sstream>
#include <string>
#include <vector>

struct Unit {
    std::string name;
    int  lines  = 0;
    bool hidden = false;   // споживачі спираються на обіцянку, а не на нутрощі
    bool test   = false;   // тест звіряє поведінку, тому бачить крізь межу
    bool slow   = false;   // потребує бази чи мережі
};

struct Change {
    std::string name;
    std::vector<int> seeds;            // одиниці, які відкриваєш і правиш
};

struct Model {
    std::vector<Unit> unit;
    std::vector<std::vector<int>> users;   // users[v] — хто спирається на v
    std::map<std::string, int> byName;
    std::vector<Change> change;

    int id(const std::string& name) {
        auto [it, fresh] = byName.emplace(name, static_cast<int>(unit.size()));
        if (fresh) {
            unit.push_back(Unit{name});
            users.emplace_back();
        }
        return it->second;
    }
};

static Model load(const char* path) {
    std::ifstream in(path);
    if (!in) { std::fprintf(stderr, "не відкрити %s\n", path); std::exit(1); }

    Model m;
    for (std::string raw; std::getline(in, raw); ) {
        if (auto hash = raw.find('#'); hash != std::string::npos) raw.erase(hash);
        std::istringstream ls(raw);
        std::string kind;
        if (!(ls >> kind)) continue;

        if (kind == "unit") {
            std::string name;
            int lines = 0;
            ls >> name >> lines;
            Unit& u = m.unit[m.id(name)];
            u.lines = lines;
            for (std::string flag; ls >> flag; ) {
                if      (flag == "hidden") u.hidden = true;
                else if (flag == "test")   u.test   = true;
                else if (flag == "slow")   u.test = u.slow = true;
            }
        } else if (kind == "dep") {
            std::string from, to;
            ls >> from >> to;
            const int t = m.id(to), f = m.id(from);   // id() може посунути вектор,
            m.users[t].push_back(f);                  // тож спершу індекси, потім доступ
        } else if (kind == "change") {
            Change c;
            ls >> c.name;
            for (std::string s; ls >> s; ) c.seeds.push_back(m.id(s));
            m.change.push_back(std::move(c));
        }
    }
    return m;
}

struct Blast {
    std::vector<int> edit, reread, fast, slow;
};

static Blast blastOf(const Model& m, const Change& c) {
    std::vector<char> seen(m.unit.size(), 0);
    std::queue<int> q;
    Blast b;

    for (int s : c.seeds)
        if (!seen[s]) { seen[s] = 1; b.edit.push_back(s); q.push(s); }

    while (!q.empty()) {
        const int v = q.front();
        q.pop();
        const bool holds = m.unit[v].hidden;            // межа тримає обіцянку
        for (int w : m.users[v]) {
            if (seen[w]) continue;
            if (holds && !m.unit[w].test) continue;     // споживач бачить лише обіцянку
            seen[w] = 1;
            if (m.unit[w].test) (m.unit[w].slow ? b.slow : b.fast).push_back(w);
            else                b.reread.push_back(w);
            q.push(w);
        }
    }
    return b;
}

static int linesOf(const Model& m, const std::vector<int>& v) {
    int s = 0;
    for (int i : v) s += m.unit[i].lines;
    return s;
}

// Вартість поширення: частка пар (А, Б), де А хоч якимось шляхом дістає до Б.
// Рахуємо лише на коді — тести до розкладу системи не належать.
static void propagationCost(const Model& m) {
    const int n = static_cast<int>(m.unit.size());
    std::vector<std::vector<int>> deps(n);
    int code = 0;
    for (int v = 0; v < n; ++v) {
        if (m.unit[v].test) continue;
        ++code;
        for (int u : m.users[v])
            if (!m.unit[u].test) deps[u].push_back(v);
    }

    long long reach = 0;
    for (int s = 0; s < n; ++s) {
        if (m.unit[s].test) continue;
        std::vector<char> seen(n, 0);
        std::queue<int> q;
        seen[s] = 1;
        q.push(s);
        while (!q.empty()) {
            const int v = q.front();
            q.pop();
            ++reach;
            for (int w : deps[v]) if (!seen[w]) { seen[w] = 1; q.push(w); }
        }
    }

    const double sq = 1.0 * code * code;
    std::printf("вартість поширення: %.1f %% (без діагоналі %.1f %%)\n",
                100.0 * reach / sq,
                code > 1 ? 100.0 * (reach - code) / (sq - code) : 0.0);
}

int main(int argc, char** argv) {
    if (argc < 2) { std::fprintf(stderr, "вжиток: ripple <модель.units>\n"); return 1; }
    const Model m = load(argv[1]);

    int codeUnits = 0, codeLines = 0, testUnits = 0, testLines = 0;
    for (const Unit& u : m.unit) {
        if (u.test) { ++testUnits; testLines += u.lines; }
        else        { ++codeUnits; codeLines += u.lines; }
    }
    std::printf("модель: код %d од. / %d ряд.; тести %d од. / %d ряд.\n",
                codeUnits, codeLines, testUnits, testLines);
    propagationCost(m);

    for (const Change& c : m.change) {
        const Blast b = blastOf(m, c);
        const int edit = linesOf(m, b.edit), reread = linesOf(m, b.reread);
        std::printf("\n%s: правити %zu од. / %d ряд.; перечитати %zu од. / %d ряд.\n",
                    c.name.c_str(), b.edit.size(), edit, b.reread.size(), reread);
        std::printf("  у голові разом: %d ряд.; тести: швидких %zu, повільних %zu\n",
                    edit + reread, b.fast.size(), b.slow.size());
    }

    for (size_t i = 0; i < m.change.size(); ++i)
        for (size_t j = i + 1; j < m.change.size(); ++j) {
            std::vector<int> a = m.change[i].seeds, b = m.change[j].seeds, both;
            std::sort(a.begin(), a.end());
            std::sort(b.begin(), b.end());
            std::set_intersection(a.begin(), a.end(), b.begin(), b.end(),
                                  std::back_inserter(both));
            if (!both.empty())
                std::printf("\nспільні одиниці «%s» і «%s»: %zu — паралельно не зробити\n",
                            m.change[i].name.c_str(), m.change[j].name.c_str(), both.size());
        }
    return 0;
}
