#include <vector>
#include <stack>
#include <cstddef>

void dfs_iterative(const Graph& g, int start_node) {
    const std::size_t n = g.num_vertices();
    std::vector<Color> color(n, Color::White);
    std::vector<int> d(n, 0);
    std::vector<int> f(n, 0);
    int timer = 0;

    struct Frame {
        int u;
        std::size_t neighbor_idx;
    };

    std::stack<Frame> st;
    color[start_node] = Color::Gray;
    d[start_node] = ++timer;
    st.push({start_node, 0});

    while (!st.empty()) {
        auto& [u, idx] = st.top();
        const auto& nbrs = g.neighbors(u);

        if (idx < nbrs.size()) {
            int v = nbrs[idx++];
            if (color[v] == Color::White) {
                color[v] = Color::Gray;
                d[v] = ++timer;
                st.push({v, 0}); // Занурення вглиб
            }
        } else {
            color[u] = Color::Black;
            f[u] = ++timer;
            st.pop(); // Завершення вершини u (Post-Order)
        }
    }
}
