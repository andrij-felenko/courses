struct Net {
    std::string name;                 // ім'я з мітки або службове
    std::vector<int> pins;            // індекси пінів у цьому ланцюзі
};

static std::vector<Net> build_netlist(const std::vector<Wire>&  wires,
                                      const std::vector<Pin>&   pins,
                                      const std::vector<Label>& labels)
{
    NodeMap nm;
    DSU dsu = build_geometry(wires, pins, nm);   // 1) склеїти за дотиком
    merge_by_labels(labels, nm, dsu);            // 2) долити за іменами (й членами шин)

    // 3) Згрупувати ПІНИ за коренем ланцюга.
    std::unordered_map<int, Net> by_root;
    for (size_t i = 0; i < pins.size(); ++i) {
        int root = dsu.find(nm.node_at(pins[i].at));
        by_root[root].pins.push_back((int)i);
    }
    // 4) Дати ланцюгам імена з міток, що на них висять.
    for (const auto& L : labels) {
        int root = dsu.find(nm.node_at(L.at));
        auto it = by_root.find(root);
        if (it != by_root.end() && it->second.name.empty())
            it->second.name = L.name;            // перша мітка дає ім'я ланцюгу
    }
    std::vector<Net> nets;
    for (auto& kv : by_root) {
        if (kv.second.name.empty())
            kv.second.name = "Net-" + std::to_string(kv.first); // службове ім'я
        nets.push_back(std::move(kv.second));
    }
    return nets;
}
