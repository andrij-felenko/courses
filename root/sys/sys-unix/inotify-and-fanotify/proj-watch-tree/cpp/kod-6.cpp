struct PendingMove {
    bool used{false};
    uint32_t cookie{0};
    int from_parent{-1};
    int moved_wd{-1};
    std::string name;
    std::chrono::steady_clock::time_point deadline;
};
static std::vector<PendingMove> moves(MOVE_SLOTS);

static void move_out(Context& c, Node* dir, const std::string& name, bool isdir, uint32_t cookie) {
    Node* sub = isdir ? child_of(dir->wd, name) : nullptr;
    for (auto& m : moves) {
        if (m.used) continue;
        m.used = true;
        m.cookie = cookie;
        m.from_parent = dir->wd;
        m.moved_wd = sub ? sub->wd : -1;
        m.name = name;
        m.deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(MOVE_TIMEOUT_MS);
        return;
    }
    c.rebuild = true;
}

static void reparent(Node* n, int new_parent, const std::string& new_name) {
    unlink_sib(n);
    n->name = new_name;
    n->parent = new_parent;
    Node* p = map_get(new_parent);
    n->sib = p ? p->child : nullptr;
    if (p) p->child = n;
}

static void move_in(Context& c, Node* dir, const std::string& name, bool isdir, uint32_t cookie) {
    for (auto& m : moves) {
        if (!m.used || m.cookie != cookie) continue;

        std::string from = path_of(m.from_parent);
        std::string to = path_of(dir->wd);
        if (!from.empty() && !to.empty())
            std::cout << "> " << from << "/" << m.name << " " << to << "/" << name << "\n";

        Node* sub = map_get(m.moved_wd);
        if (sub)        reparent(sub, dir->wd, name);
        else if (isdir) defer_scan(c, dir->wd, name);
        m.used = false;
        return;
    }
    emit("+", dir->wd, name);
    if (isdir) defer_scan(c, dir->wd, name);
}

static void expire_moves(Context& c) {
    auto now = std::chrono::steady_clock::now();
    for (auto& m : moves) {
        if (!m.used || m.deadline > now) continue;
        emit("-", m.from_parent, m.name);
        Node* sub = map_get(m.moved_wd);
        if (sub) unwatch_subtree(c, sub);
        m.used = false;
    }
}

static int next_timeout() {
    auto now = std::chrono::steady_clock::now();
    int best = -1;
    for (const auto& m : moves) {
        if (!m.used) continue;
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(m.deadline - now).count();
        if (ms < 0) ms = 0;
        if (best < 0 || ms < best) best = static_cast<int>(ms);
    }
    return best;
}
