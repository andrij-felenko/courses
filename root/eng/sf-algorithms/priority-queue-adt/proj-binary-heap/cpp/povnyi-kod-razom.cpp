#include <vector>
#include <utility>   // std::swap

// Черга з пріоритетом: min-купа над щільним масивом записів (key, id).
// id — стабільний цілий дескриптор 0..cap-1 (вершина графа, номер задачі).
class MinHeap {
public:
    struct Node { long long key; int id; };

    explicit MinHeap(int cap) : pos(cap, NONE) {}

    // Побудова з готового набору за O(n) — Флойдове heapify.
    MinHeap(const std::vector<Node>& items, int cap) : h(items), pos(cap, NONE) {
        for (int i = 0; i < (int)h.size(); ++i) pos[h[i].id] = i;
        for (int i = (int)h.size() / 2 - 1; i >= 0; --i) sift_down(i);
    }

    bool empty() const { return h.empty(); }
    int  size()  const { return (int)h.size(); }
    bool contains(int id) const { return pos[id] != NONE; }
    const Node& peek() const { return h[0]; }            // O(1)

    void push(long long key, int id) {                   // O(log n)
        h.push_back({key, id});
        pos[id] = (int)h.size() - 1;
        sift_up((int)h.size() - 1);
    }

    Node pop_min() {                                     // O(log n)
        swap_nodes(0, (int)h.size() - 1);
        Node top = h.back();
        h.pop_back();
        pos[top.id] = NONE;
        if (!h.empty()) sift_down(0);
        return top;
    }

    void decrease_key(int id, long long new_key) {       // O(log n)
        int i = pos[id];
        h[i].key = new_key;
        sift_up(i);
    }

private:
    static constexpr int NONE = -1;
    std::vector<Node> h;      // купа
    std::vector<int>  pos;    // id -> індекс (єдине джерело правди про місце)

    void swap_nodes(int i, int j) {          // єдиний рух записів
        std::swap(h[i], h[j]);
        pos[h[i].id] = i;
        pos[h[j].id] = j;
    }
    void sift_up(int i) {
        while (i > 0) {
            int parent = (i - 1) / 2;
            if (h[parent].key <= h[i].key) break;
            swap_nodes(i, parent);
            i = parent;
        }
    }
    void sift_down(int i) {
        int n = (int)h.size();
        for (;;) {
            int smallest = i, l = 2*i + 1, r = 2*i + 2;
            if (l < n && h[l].key < h[smallest].key) smallest = l;
            if (r < n && h[r].key < h[smallest].key) smallest = r;
            if (smallest == i) break;
            swap_nodes(i, smallest);
            i = smallest;
        }
    }
};
