class KdTree {
public:
    explicit KdTree(std::vector<Point> pts, int leaf = 16)
        : pts_(std::move(pts)), idx_(pts_.size()), leaf_(leaf) {
        std::iota(idx_.begin(), idx_.end(), 0);
        nodes_.reserve(4 * idx_.size() / leaf_ + 8);      // стеля кількості вузлів
        if (!idx_.empty()) build(0, static_cast<int>(idx_.size()));
    }

private:
    std::vector<Point> pts_;
    std::vector<int>   idx_;
    std::vector<Node>  nodes_;
    int                leaf_;

    int build(int b, int e) {
        const int me = static_cast<int>(nodes_.size());
        nodes_.push_back(Node{0.0f, -1, -1, b, e});       // поки що листок
        if (e - b <= leaf_) return me;

        float lo[D], hi[D];
        for (int a = 0; a < D; ++a) { lo[a] = +INFINITY; hi[a] = -INFINITY; }
        for (int i = b; i < e; ++i)
            for (int a = 0; a < D; ++a) {
                const float v = pts_[idx_[i]].c[a];
                lo[a] = std::min(lo[a], v);
                hi[a] = std::max(hi[a], v);
            }
        int axis = 0;
        for (int a = 1; a < D; ++a)
            if (hi[a] - lo[a] > hi[axis] - lo[axis]) axis = a;
        if (hi[axis] <= lo[axis]) return me;   // вся комірка — одна точка, ділити нічим

        const int mid = b + (e - b) / 2;
        std::nth_element(idx_.begin() + b, idx_.begin() + mid, idx_.begin() + e,
                         [&](int i, int j) { return pts_[i].c[axis] < pts_[j].c[axis]; });

        nodes_[me].axis  = axis;
        nodes_[me].split = pts_[idx_[mid]].c[axis];
        build(b, mid);                       // лівий нащадок = me + 1
        const int r = build(mid, e);         // ⚠ не писати одразу в nodes_[me].right
        nodes_[me].right = r;
        return me;
    }
