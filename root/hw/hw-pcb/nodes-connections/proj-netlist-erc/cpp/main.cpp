// Система неперетинних множин зі стисненням шляхів і об'єднанням за рангом.
struct DSU {
    std::vector<int> parent, rank_;
    explicit DSU(int n) : parent(n), rank_(n, 0) {
        for (int i = 0; i < n; ++i) parent[i] = i;   // makeset: кожен пін — сам собі корінь
    }
    int find(int x) {                                // корінь множини піна x
        while (parent[x] != x) x = parent[x] = parent[parent[x]];  // зі стисненням
        return x;
    }
    void unite(int a, int b) {                       // злити два ланцюги в один
        a = find(a); b = find(b);
        if (a == b) return;
        if (rank_[a] < rank_[b]) std::swap(a, b);
        parent[b] = a;
        if (rank_[a] == rank_[b]) ++rank_[a];
    }
};

// Кожен дріт, крапка-з'єднання й однакова мітка дають по виклику unite():
DSU dsu(pin_count);
for (auto [a, b] : wires)          dsu.unite(a, b);          // дроти й крапки
for (auto& g : named_nets)         for (int p : g) dsu.unite(g[0], p);  // мітки-імена

// find(корінь) для кожного піна — і піни з однаковим коренем складають один ланцюг.
std::map<int, std::vector<int>> nets;
for (int p = 0; p < pin_count; ++p) nets[dsu.find(p)].push_back(p);
