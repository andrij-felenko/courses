class MinHeap {
public:
    struct Node { long long key; int id; };

    explicit MinHeap(int cap) : pos(cap, NONE) {}

    bool empty() const { return h.empty(); }
    int  size()  const { return (int)h.size(); }
    bool contains(int id) const { return pos[id] != NONE; }

    const Node& peek() const { return h[0]; }   // мінімум — у корені: O(1)

private:
    static constexpr int NONE = -1;
    std::vector<Node> h;     // сама купа: щільний масив записів
    std::vector<int>  pos;   // id -> індекс у h (де саме лежить елемент)
};
