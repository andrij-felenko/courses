#include <vector>
#include <queue>

// adj[v] — список сусідів вершини v; вершини занумеровано 0..N-1
bool reachable(const std::vector<std::vector<int>>& adj, int src, int dst) {
    if (src == dst) return true;
    std::vector<char> seen(adj.size(), 0);   // хто вже відвіданий
    std::queue<int> frontier;                // фронт хвилі обходу
    seen[src] = 1;
    frontier.push(src);

    while (!frontier.empty()) {
        int v = frontier.front();
        frontier.pop();
        for (int nb : adj[v]) {              // усі сусіди поточної вершини
            if (nb == dst) return true;      // дійшли до цілі
            if (!seen[nb]) {                 // ще не бачили — у фронт
                seen[nb] = 1;
                frontier.push(nb);
            }
        }
    }
    return false;                            // фронт вичерпано — шляху нема
}
