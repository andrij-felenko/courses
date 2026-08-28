// Побудова мінімального вершинного покриття за теоремою Кеніга
std::pair<std::vector<bool>, std::vector<bool>> 
build_min_vertex_cover(std::size_t u_size, std::size_t v_size,
                       const std::vector<std::vector<std::size_t>>& adj,
                       const std::vector<int>& match_v) {
    std::vector<int> match_u(u_size, -1);
    for (std::size_t v = 0; v < v_size; ++v) {
        if (match_v[v] != -1) {
            match_u[static_cast<std::size_t>(match_v[v])] = static_cast<int>(v);
        }
    }

    std::vector<bool> visited_u(u_size, false);
    std::vector<bool> visited_v(v_size, false);
    std::queue<std::size_t> q;

    // 1. Починаємо BFS з усіх вільних вершин U
    for (std::size_t u = 0; u < u_size; ++u) {
        if (match_u[u] == -1) {
            visited_u[u] = true;
            q.push(u);
        }
    }

    // 2. Змінний обхід по ребрах поза M (від U до V) та по ребрах з M (від V до U)
    while (!q.empty()) {
        std::size_t u = q.front();
        q.pop();

        for (std::size_t v : adj[u]) {
            if (!visited_v[v] && match_u[u] != static_cast<int>(v)) {
                visited_v[v] = true;
                if (match_v[v] != -1 && !visited_u[static_cast<std::size_t>(match_v[v])]) {
                    visited_u[static_cast<std::size_t>(match_v[v])] = true;
                    q.push(static_cast<std::size_t>(match_v[v]));
                }
            }
        }
    }

    // 3. Формуємо покриття: C = (U \ Z) union (V intersect Z)
    std::vector<bool> cover_u(u_size, false);
    std::vector<bool> cover_v(v_size, false);

    for (std::size_t u = 0; u < u_size; ++u) {
        if (!visited_u[u]) cover_u[u] = true;
    }
    for (std::size_t v = 0; v < v_size; ++v) {
        if (visited_v[v]) cover_v[v] = true;
    }

    return {cover_u, cover_v};
}
