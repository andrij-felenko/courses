struct NodeMap {
    std::unordered_map<Point, int, PointHash> id;
    std::vector<Point> pt;                    // вузол → координата (для діагностики)
    int node_at(const Point& p) {
        auto it = id.find(p);
        if (it != id.end()) return it->second; // уже є вузол на цій точці
        int n = (int)pt.size();
        id.emplace(p, n);
        pt.push_back(p);
        return n;                              // новий вузол на новій точці
    }
};

// Будуємо геометричні ланцюги: спільна координата → спільний вузол;
// кінці кожного дроту зливаємо; Т-дотики ловимо окремим проходом.
static DSU build_geometry(const std::vector<Wire>& wires,
                          const std::vector<Pin>&  pins,
                          NodeMap& nm)
{
    // 1) Заводимо вузли на всіх кінцях дротів і всіх пінах (збіг точок = той самий вузол).
    for (const auto& w : wires) { nm.node_at(w.a); nm.node_at(w.b); }
    for (const auto& p : pins)  { nm.node_at(p.at); }

    DSU dsu((int)nm.pt.size());

    // 2) Кінці того самого дроту — очевидно один ланцюг.
    for (const auto& w : wires)
        dsu.unite(nm.node_at(w.a), nm.node_at(w.b));

    // 3) Т-ДОТИКИ: вузол (пін чи кінець дроту), що лежить УСЕРЕДИНІ іншого дроту.
    //    Без цього кроку трійник «кінець у середину» загубився б.
    for (int v = 0; v < (int)nm.pt.size(); ++v) {
        const Point& p = nm.pt[v];
        for (const auto& w : wires) {
            if (p == w.a || p == w.b) continue;        // кінці вже злиті в кроці 2
            if (point_on_wire(p, w)) {                 // p сидить на тілі дроту w
                dsu.unite(v, nm.node_at(w.a));         // приєднати до того дроту
            }
        }
    }
    return dsu;
}
