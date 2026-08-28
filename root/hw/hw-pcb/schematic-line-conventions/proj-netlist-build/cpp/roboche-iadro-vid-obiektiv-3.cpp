struct DSU {
    std::vector<int> parent, rank_;
    explicit DSU(int n) : parent(n), rank_(n, 0) {
        for (int i = 0; i < n; ++i) parent[i] = i;   // кожен — сам собі корінь
    }
    int find(int x) {
        while (parent[x] != x) x = parent[x] = parent[parent[x]];  // стиснення шляху
        return x;
    }
    void unite(int a, int b) {                       // злити два ланцюги
        a = find(a); b = find(b);
        if (a == b) return;
        if (rank_[a] < rank_[b]) std::swap(a, b);
        parent[b] = a;
        if (rank_[a] == rank_[b]) ++rank_[a];
    }
};
