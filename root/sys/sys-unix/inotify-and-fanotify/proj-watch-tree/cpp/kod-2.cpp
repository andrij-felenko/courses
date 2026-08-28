static std::unordered_map<int, std::unique_ptr<Node>> node_map;
static size_t nwatch = 0;

static Node* map_get(int wd) {
    auto it = node_map.find(wd);
    return (it != node_map.end()) ? it->second.get() : nullptr;
}

static Node* map_add(int wd, int parent, const std::string& name) {
    auto n = std::make_unique<Node>();
    n->wd = wd;
    n->parent = parent;
    n->name = name;

    Node* raw = n.get();
    node_map[wd] = std::move(n);

    Node* p = map_get(parent);
    raw->sib = p ? p->child : nullptr;
    if (p) p->child = raw;

    nwatch++;
    return raw;
}

static void unlink_sib(Node* n) {
    Node* p = map_get(n->parent);
    if (!p) return;
    for (Node** pp = &p->child; *pp; pp = &(*pp)->sib) {
        if (*pp == n) { *pp = n->sib; return; }
    }
}

static Node* child_of(int parent_wd, const std::string& name) {
    Node* p = map_get(parent_wd);
    if (!p) return nullptr;
    for (Node* n = p->child; n; n = n->sib) {
        if (n->name == name) return n;
    }
    return nullptr;
}

static std::string path_of(int wd) {
    std::vector<std::string> parts;
    for (int cur = wd; cur >= 0; ) {
        Node* n = map_get(cur);
        if (!n || parts.size() == MAXDEPTH) return "";
        parts.push_back(n->name);
        cur = n->parent;
    }
    std::string out;
    for (auto it = parts.rbegin(); it != parts.rend(); ++it) {
        if (!out.empty() && out.back() != '/') out += '/';
        out += *it;
    }
    return out;
}

static void emit(const char* what, int dir_wd, const std::string& name) {
    std::string p = path_of(dir_wd);
    if (p.empty()) return;
    std::cout << what << " " << p << (p.back() == '/' ? "" : "/") << name << "\n";
}
