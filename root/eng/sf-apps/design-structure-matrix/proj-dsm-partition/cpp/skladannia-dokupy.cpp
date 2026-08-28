static std::string signature(const std::vector<int>& mem,
                             const std::vector<std::string>& name) {
    std::string s;
    for (size_t k = 0; k < mem.size(); ++k) { if (k) s += ','; s += name[mem[k]]; }
    return s;
}

static std::string brief(const std::vector<int>& mem,
                         const std::vector<std::string>& name) {
    std::string s;
    for (size_t k = 0; k < mem.size() && k < 3; ++k) { if (k) s += ", "; s += name[mem[k]]; }
    if (mem.size() > 3) s += ", … (" + std::to_string(mem.size()) + ")";
    return s;
}

static void print_cycles(const Csr& g, const Input& in, const Cond& c,
                         const std::vector<int>& comp, const std::vector<int>& order,
                         const Layout& L) {
    int cyc = 0;
    for (const int b : order) if (c.members[b].size() > 1) ++cyc;
    std::printf("циклів (блоків більш ніж з одного елемента): %d\n", cyc);
    for (const int b : order) {
        if (c.members[b].size() <= 1) continue;
        std::printf("  B%d  %s\n", L.pos[b] + 1, signature(c.members[b], in.name).c_str());
        for (const int v : c.members[b])
            for (int e = g.head[v]; e < g.head[v + 1]; ++e)
                if (comp[g.to[e]] == b)
                    std::printf("      %s -> %s\n", in.name[v].c_str(),
                                in.name[g.to[e]].c_str());
    }
    std::printf("\n");
}

static int check_baseline(const Input& in, const Cond& c, const std::vector<int>& order,
                          const Layout& L, const std::string& path) {
    std::ifstream f(path);
    if (!f) { std::fprintf(stderr, "еталон не читається: %s\n", path.c_str()); return 1; }
    std::unordered_set<std::string> known;
    std::string line;
    while (std::getline(f, line)) {
        const std::string s = trim(line);
        if (!s.empty()) known.insert(s);
    }
    int fresh = 0;
    for (const int b : order) {
        if (c.members[b].size() <= 1) continue;
        const std::string s = signature(c.members[b], in.name);
        if (!known.count(s)) {
            std::printf("НОВИЙ блок B%d: %s\n", L.pos[b] + 1, s.c_str());
            ++fresh;
        }
    }
    if (fresh) { std::printf("нових блоків: %d — збірка падає\n", fresh); return 2; }
    std::printf("нових блоків немає\n");
    return 0;
}

static int write_baseline(const Input& in, const Cond& c, const std::vector<int>& order,
                          const std::string& path) {
    std::ofstream f(path);
    if (!f) { std::fprintf(stderr, "еталон не пишеться: %s\n", path.c_str()); return 1; }
    for (const int b : order)
        if (c.members[b].size() > 1) f << signature(c.members[b], in.name) << '\n';
    return 0;
}

int main(int argc, char** argv) {
    std::string src, baseline, write;
    int limit = 60;
    for (int i = 1; i < argc; ++i) {
        const std::string a = argv[i];
        if (a == "--baseline" && i + 1 < argc) baseline = argv[++i];
        else if (a == "--write-baseline" && i + 1 < argc) write = argv[++i];
        else if (a == "--limit" && i + 1 < argc) limit = std::atoi(argv[++i]);
        else if (!a.empty() && a[0] != '-') src = a;
        else { std::fprintf(stderr, "не розумію аргумент: %s\n", a.c_str()); return 1; }
    }

    std::ifstream file;
    std::istream* stream = &std::cin;
    if (!src.empty()) {
        file.open(src);
        if (!file) { std::fprintf(stderr, "не читається: %s\n", src.c_str()); return 1; }
        stream = &file;
    }

    const Input in = read_edges(*stream);
    const int n = (int)in.name.size();
    if (n == 0) { std::printf("порожній вхід\n"); return 0; }

    const Csr g = build_csr(n, in.edge);
    std::vector<int> comp;
    const int ncomp = tarjan(g, comp);
    const Cond c = condense(g, comp, ncomp);
    const std::vector<int> order = canonical_order(c);
    if ((int)order.size() != ncomp) {             // конденсація ациклічна за побудовою
        std::fprintf(stderr, "внутрішня помилка: цикл у конденсації\n");
        return 1;
    }
    const Layout L = lay_out(c, order, n);

    std::printf("елементів: %d, дуг: %zu, блоків: %d", n, in.edge.size(), ncomp);
    if (in.dup)  std::printf(", дублікатів відкинуто: %lld", in.dup);
    if (in.self) std::printf(", петель сам-на-себе: %lld", in.self);
    std::printf("\n\n");

    print_matrix(g, in, c, comp, L, limit);
    print_cycles(g, in, c, comp, order, L);

    const Visibility vis = visibility(c, order, n);
    std::vector<int> show = order;
    if ((int)show.size() > limit) {               // на великих системах — лише найважчі
        const size_t k = std::min<size_t>(10, show.size());
        std::partial_sort(show.begin(), show.begin() + k, show.end(),
                          [&](int a, int b) {     // при рівних — за абеткою, а не «як вийде»
                              if (vis.seen[a] != vis.seen[b]) return vis.seen[a] > vis.seen[b];
                              return c.members[a][0] < c.members[b][0];
                          });
        show.resize(k);
    }
    std::printf("видимість (скільки елементів бачить кожен член блоку):\n");
    for (const int b : show)
        std::printf("  B%-3d %-40s %lld\n", L.pos[b] + 1,
                    brief(c.members[b], in.name).c_str(), vis.seen[b]);
    std::printf("\n  сума за елементами: %lld\n", vis.total);
    std::printf("  вартість поширення: %lld / %d² = %.1f %%\n\n", vis.total, n,
                100.0 * vis.cost);

    if (!write.empty()) return write_baseline(in, c, order, write);
    if (!baseline.empty()) return check_baseline(in, c, order, L, baseline);
    return 0;
}
