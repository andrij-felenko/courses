#include <vector>
#include <stack>
#include <cstddef>

struct CSRGraph {
    std::vector<int> offset;
    std::vector<int> target;

    [[nodiscard]] std::size_t num_vertices() const noexcept {
        return offset.empty() ? 0 : offset.size() - 1;
    }
};

void dfs_csr_cpp(const CSRGraph& g, int start) {
    const std::size_t n = g.num_vertices();
    std::vector<int> color(n, 0); // 0: White, 1: Gray, 2: Black
    std::stack<int> st;

    color[start] = 1;
    st.push(start);

    while (!st.empty()) {
        int u = st.top();
        st.pop();
        color[u] = 2;

        int start_idx = g.offset[u];
        int end_idx = g.offset[u + 1];

        for (int i = start_idx; i < end_idx; ++i) {
            int v = g.target[i];
            if (color[v] == 0) {
                color[v] = 1;
                st.push(v);
            }
        }
    }
}
