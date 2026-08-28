// Ключ збігу мітки: ім'я + область видимості (+ аркуш для локальних).
static std::string label_key(const Label& L) {
    if (L.scope == Scope::Global) return "G:" + L.name;          // на весь проєкт
    return "L:" + std::to_string(L.sheet) + ":" + L.name;         // лише цей аркуш
}

// Зливаємо за іменами: усі точки з однаковим ключем мітки → один ланцюг.
static void merge_by_labels(const std::vector<Label>& labels,
                            NodeMap& nm, DSU& dsu)
{
    std::unordered_map<std::string, int> first_node;   // ключ → перший побачений вузол
    for (const auto& L : labels) {
        int v = nm.node_at(L.at);                      // вузол точки, де висить мітка
        std::string k = label_key(L);
        auto it = first_node.find(k);
        if (it == first_node.end()) first_node.emplace(k, v); // перша з цим іменем
        else dsu.unite(it->second, v);                 // решта — зливаємо з першою
    }
}
