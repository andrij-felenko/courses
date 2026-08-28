#include <vector>
#include <numeric>
#include <algorithm>
#include <cstdint>
#include <span>
#include <stdexcept>

template <typename ValueType = int64_t>
class HeavyLightDecomposition {
private:
    struct SegmentTree {
        int size{0};
        std::vector<ValueType> tree;
        std::vector<ValueType> lazy;

        void init(int n) {
            size = n;
            tree.assign(4 * n, ValueType{0});
            lazy.assign(4 * n, ValueType{0});
        }

        void push(int node, int l, int r) {
            if (lazy[node] == ValueType{0}) return;
            int mid = l + (r - l) / 2;
            ValueType val = lazy[node];

            tree[node * 2 + 1] += val * (mid - l + 1);
            lazy[node * 2 + 1] += val;

            tree[node * 2 + 2] += val * (r - mid);
            lazy[node * 2 + 2] += val;

            lazy[node] = ValueType{0};
        }

        void build(int node, int l, int r, std::span<const ValueType> initial_values) {
            lazy[node] = ValueType{0};
            if (l == r) {
                tree[node] = initial_values[l];
                return;
            }
            int mid = l + (r - l) / 2;
            build(node * 2 + 1, l, mid, initial_values);
            build(node * 2 + 2, mid + 1, r, initial_values);
            tree[node] = tree[node * 2 + 1] + tree[node * 2 + 2];
        }

        void update(int node, int l, int r, int ql, int qr, ValueType val) {
            if (ql <= l && r <= qr) {
                tree[node] += val * (r - l + 1);
                lazy[node] += val;
                return;
            }
            push(node, l, r);
            int mid = l + (r - l) / 2;
            if (ql <= mid) update(node * 2 + 1, l, mid, ql, qr, val);
            if (qr > mid)  update(node * 2 + 2, mid + 1, r, ql, qr, val);
            tree[node] = tree[node * 2 + 1] + tree[node * 2 + 2];
        }

        ValueType query(int node, int l, int r, int ql, int qr) {
            if (ql <= l && r <= qr) return tree[node];
            push(node, l, r);
            int mid = l + (r - l) / 2;
            ValueType res{0};
            if (ql <= mid) res += query(node * 2 + 1, l, mid, ql, qr);
            if (qr > mid)  res += query(node * 2 + 2, mid + 1, r, ql, qr);
            return res;
        }
    };

    int node_count{0};
    int current_dfs_pos{0};
    std::vector<std::vector<int>> adj;
    std::vector<int> parent;
    std::vector<int> depth;
    std::vector<int> subtree_size;
    std::vector<int> heavy_child;
    std::vector<int> chain_head;
    std::vector<int> position;
    std::vector<ValueType> node_values;
    std::vector<ValueType> flat_values;
    SegmentTree seg_tree;

    void dfs_size(int u, int p, int d) {
        parent[u] = p;
        depth[u] = d;
        subtree_size[u] = 1;
        heavy_child[u] = -1;
        int max_sub_size = 0;

        for (int v : adj[u]) {
            if (v == p) continue;
            dfs_size(v, u, d + 1);
            subtree_size[u] += subtree_size[v];
            if (subtree_size[v] > max_sub_size) {
                max_sub_size = subtree_size[v];
                heavy_child[u] = v;
            }
        }
    }

    void dfs_hld(int u, int h) {
        chain_head[u] = h;
        position[u] = current_dfs_pos;
        flat_values[current_dfs_pos] = node_values[u];
        current_dfs_pos++;

        if (heavy_child[u] != -1) {
            dfs_hld(heavy_child[u], h);
        }

        for (int v : adj[u]) {
            if (v == parent[u] || v == heavy_child[u]) continue;
            dfs_hld(v, v);
        }
    }

public:
    explicit HeavyLightDecomposition(int n)
        : node_count(n),
          adj(n),
          parent(n, -1),
          depth(n, 0),
          subtree_size(n, 0),
          heavy_child(n, -1),
          chain_head(n, 0),
          position(n, 0),
          node_values(n, ValueType{0}),
          flat_values(n, ValueType{0}) {
        if (n <= 0) {
            throw std::invalid_argument("Кількість вершин дерева повинна бути додатною.");
        }
    }

    void add_edge(int u, int v) {
        if (u < 0 || u >= node_count || v < 0 || v >= node_count) {
            throw std::out_of_range("Індекс вершини виходить за межі діапазону графа.");
        }
        adj[u].push_back(v);
        adj[v].push_back(u);
    }

    void set_value(int u, ValueType val) {
        if (u < 0 || u >= node_count) {
            throw std::out_of_range("Індекс вершини виходить за межі діапазону графа.");
        }
        node_values[u] = val;
    }

    void build(int root = 0) {
        current_dfs_pos = 0;
        dfs_size(root, -1, 0);
        dfs_hld(root, root);
        seg_tree.init(node_count);
        seg_tree.build(0, 0, node_count - 1, flat_values);
    }

    [[nodiscard]] int find_lca(int u, int v) const {
        while (chain_head[u] != chain_head[v]) {
            if (depth[chain_head[u]] > depth[chain_head[v]]) {
                u = parent[chain_head[u]];
            } else {
                v = parent[chain_head[v]];
            }
        }
        return depth[u] < depth[v] ? u : v;
    }

    void update_path(int u, int v, ValueType val) {
        while (chain_head[u] != chain_head[v]) {
            if (depth[chain_head[u]] < depth[chain_head[v]]) {
                std::swap(u, v);
            }
            seg_tree.update(0, 0, node_count - 1, position[chain_head[u]], position[u], val);
            u = parent[chain_head[u]];
        }
        if (depth[u] > depth[v]) {
            std::swap(u, v);
        }
        seg_tree.update(0, 0, node_count - 1, position[u], position[v], val);
    }

    [[nodiscard]] ValueType query_path(int u, int v) {
        ValueType sum{0};
        while (chain_head[u] != chain_head[v]) {
            if (depth[chain_head[u]] < depth[chain_head[v]]) {
                std::swap(u, v);
            }
            sum += seg_tree.query(0, 0, node_count - 1, position[chain_head[u]], position[u]);
            u = parent[chain_head[u]];
        }
        if (depth[u] > depth[v]) {
            std::swap(u, v);
        }
        sum += seg_tree.query(0, 0, node_count - 1, position[u], position[v]);
        return sum;
    }

    void update_subtree(int v, ValueType val) {
        seg_tree.update(0, 0, node_count - 1, position[v], position[v] + subtree_size[v] - 1, val);
    }

    [[nodiscard]] ValueType query_subtree(int v) {
        return seg_tree.query(0, 0, node_count - 1, position[v], position[v] + subtree_size[v] - 1);
    }
};
