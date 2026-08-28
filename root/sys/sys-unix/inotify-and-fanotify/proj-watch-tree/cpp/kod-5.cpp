struct Todo {
    int parent;
    std::string name;
};
static std::vector<Todo> todo_queue;

static void defer_scan(Context& c, int parent, const std::string& name) {
    if (todo_queue.size() >= TODO_MAX) { c.rebuild = true; return; }
    todo_queue.push_back({parent, name});
}

static void run_todo(Context& c) {
    auto items = std::move(todo_queue);
    todo_queue.clear();
    for (const auto& item : items) {
        std::string p = path_of(item.parent);
        if (p.empty()) continue;
        size_t len = p.size();
        if (len + 1 + item.name.size() >= PATH_MAX) continue;
        std::snprintf(c.buf.data(), PATH_MAX, "%s/%s", p.c_str(), item.name.c_str());
        scan(c, len + 1 + item.name.size(), item.parent, item.name);
    }
}
