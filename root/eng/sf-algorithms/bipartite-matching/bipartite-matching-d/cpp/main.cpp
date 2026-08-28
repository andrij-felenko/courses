// Ідіоматична реалізація рекурсивного DFS мовою C++20
// adj[u] містить список сусідніх вершин v ∈ V
bool kuhn_dfs(std::size_t u, const std::vector<std::vector<std::size_t>>& adj,
              std::vector<bool>& used, std::vector<int>& match) {
    if (used[u]) return false;
    used[u] = true;

    for (std::size_t v : adj[u]) {
        if (match[v] == -1 || kuhn_dfs(static_cast<std::size_t>(match[v]), adj, used, match)) {
            match[v] = static_cast<int>(u); // фіксуємо нове паросполучення
            return true;
        }
    }
    return false;
}
