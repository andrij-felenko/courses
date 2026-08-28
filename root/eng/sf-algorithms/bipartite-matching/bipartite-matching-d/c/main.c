// Реалізація рекурсивного пошуку доповнюючого шляху мовою C
// g_head[], g_to[], g_next[] — список суміжності графа
// match[v] містить індекс вершини з U, спарованої з v ∈ V, або -1
bool kuhn_dfs(int u, const int* head, const int* to, const int* next, bool* used, int* match) {
    if (used[u]) return false;
    used[u] = true;

    for (int e = head[u]; e != -1; e = next[e]) {
        int v = to[e];
        if (match[v] == -1 || kuhn_dfs(match[v], head, to, next, used, match)) {
            match[v] = u; // фіксуємо нове паросполучення
            return true;
        }
    }
    return false;
}
