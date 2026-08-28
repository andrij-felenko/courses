uint64_t varsMask(const CNF& F) {                  // маска змінних, що з'являються у F
    uint64_t m = 0;
    for (const Clause& c : F) for (Lit L : c) m |= 1ULL << (var(L) - 1);
    return m;
}

struct DSU {                                       // об'єднання-пошук: змінні однієї компоненти
    vector<int> p;
    DSU(int n) : p(n) { for (int i = 0; i < n; ++i) p[i] = i; }
    int find(int x) { return p[x] == x ? x : p[x] = find(p[x]); }
    void unite(int a, int b) { p[find(a)] = find(b); }
};

// Розкласти формулу на незалежні компоненти (клаузи без спільних змінних).
vector<CNF> decompose(const CNF& F, int n) {
    DSU dsu(n);
    for (const Clause& c : F)
        for (size_t i = 1; i < c.size(); ++i)
            dsu.unite(var(c[0]) - 1, var(c[i]) - 1);   // усі змінні клаузи — в один клас
    std::unordered_map<int, CNF> groups;
    for (const Clause& c : F)
        groups[dsu.find(var(c[0]) - 1)].push_back(c);  // клауза йде до кореня свого класу
    vector<CNF> out;
    for (auto& kv : groups) out.push_back(std::move(kv.second));
    return out;
}

// Канонічний ключ компоненти: відсортовані літерали в клаузах, відсортовані клаузи.
std::string key(CNF F) {
    for (Clause& c : F) std::sort(c.begin(), c.end());
    std::sort(F.begin(), F.end());
    std::string s;
    for (const Clause& c : F) { for (Lit L : c) { s += std::to_string(L); s += ','; } s += ';'; }
    return s;
}

// core(F): число моделей НАД РІВНО тими змінними, що з'являються у F.
// Залежить лише від F → безпечно кешується за key(F).
Count core(const CNF& F, int n, std::unordered_map<std::string, Count>& cache) {
    if (F.empty()) return 1;                        // жодної змінної → одна порожня модель
    std::string k = key(F);
    auto it = cache.find(k);
    if (it != cache.end()) return it->second;       // готове число — без нового піддерева

    uint64_t Vin = varsMask(F);
    vector<CNF> comps = decompose(F, n);
    Count result;
    if (comps.size() > 1) {                         // незалежні компоненти → числа МНОЖАТЬСЯ
        result = 1;
        for (const CNF& Fi : comps) result *= core(Fi, n, cache);
    } else {                                        // одна компонента → розгалуження + додавання
        int v = var(F[0][0]);
        bool cf1 = false, cf0 = false;
        CNF F1 = assign(F,  v, cf1);
        CNF F0 = assign(F, -v, cf0);
        uint64_t drop1 = Vin & ~varsMask(F1) & ~(1ULL << (v - 1));  // змінні, що випали в гілці
        uint64_t drop0 = Vin & ~varsMask(F0) & ~(1ULL << (v - 1));
        Count s1 = cf1 ? 0 : core(F1, n, cache) << bits(drop1);     // × 2^(вільні в гілці)
        Count s0 = cf0 ? 0 : core(F0, n, cache) << bits(drop0);
        result = s1 + s0;
    }
    cache[k] = result;
    return result;
}

// Повний лічильник: core над змінними-учасницями × 2^(змінні поза всіма клаузами).
Count countModels(const CNF& F, int n) {
    std::unordered_map<std::string, Count> cache;
    int freeTop = n - bits(varsMask(F));            // змінні, яких нема в жодній клаузі
    return core(F, n, cache) << freeTop;            // × 2^(вільні верхнього рівня)
}
