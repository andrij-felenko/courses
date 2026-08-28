struct KdCounted {
    KdCounted(const double* pts, int n, int d, int leaf)
        : p_(pts), n_(n), d_(d), leaf_(leaf), idx_(n), lo_(d), hi_(d) {
        for (int i = 0; i < n; ++i) idx_[i] = i;
        nodes_.reserve(4 * (n / leaf + 1));
        build(0, n);
    }

    int leaves() const {
        int k = 0;
        for (const Node& nd : nodes_) if (nd.axis < 0) ++k;
        return k;
    }

    int nearest(const double* q) {          // номер найближчої точки
        visitedLeaves = distCalls = 0;
        best_ = -1;  bestD2_ = HUGE_VAL;
        nn(0, q);
        return best_;
    }

    long visitedLeaves = 0, distCalls = 0;  // ← весь вимір живе тут

private:
    struct Node { double split; int axis, right, begin, end; };

    const double* p_;
    int n_, d_, leaf_;
    std::vector<int>    idx_;
    std::vector<double> lo_, hi_;           // буфери меж комірки, по одному на дерево
    std::vector<Node>   nodes_;
    int    best_   = -1;
    double bestD2_ = HUGE_VAL;

    const double* pt(int i) const { return p_ + static_cast<size_t>(i) * d_; }

    int build(int b, int e) {
        const int me = static_cast<int>(nodes_.size());
        nodes_.push_back(Node{0.0, -1, -1, b, e});          // поки що листок
        if (e - b <= leaf_) return me;

        for (int a = 0; a < d_; ++a) { lo_[a] = HUGE_VAL; hi_[a] = -HUGE_VAL; }
        for (int i = b; i < e; ++i) {
            const double* v = pt(idx_[i]);
            for (int a = 0; a < d_; ++a) {
                if (v[a] < lo_[a]) lo_[a] = v[a];
                if (v[a] > hi_[a]) hi_[a] = v[a];
            }
        }
        int axis = 0;
        for (int a = 1; a < d_; ++a)
            if (hi_[a] - lo_[a] > hi_[axis] - lo_[axis]) axis = a;
        if (hi_[axis] <= lo_[axis]) return me;              // ділити нічим

        const int mid = b + (e - b) / 2;
        std::nth_element(idx_.begin() + b, idx_.begin() + mid, idx_.begin() + e,
                         [&](int i, int j) { return pt(i)[axis] < pt(j)[axis]; });
        nodes_[me].axis  = axis;
        nodes_[me].split = pt(idx_[mid])[axis];
        build(b, mid);                                      // лівий нащадок = me + 1
        const int r = build(mid, e);
        nodes_[me].right = r;
        return me;
    }

    void nn(int node, const double* q) {
        const Node nd = nodes_[node];
        if (nd.axis < 0) {
            ++visitedLeaves;
            for (int i = nd.begin; i < nd.end; ++i) {
                ++distCalls;
                const double D2 = dist2(q, pt(idx_[i]), d_);
                if (D2 < bestD2_) { bestD2_ = D2; best_ = idx_[i]; }
            }
            return;
        }
        const double diff = q[nd.axis] - nd.split;
        const int near = (diff < 0.0) ? node + 1 : nd.right;
        const int far  = (diff < 0.0) ? nd.right : node + 1;
        nn(near, q);
        if (diff * diff < bestD2_) nn(far, q);              // єдине правило відсікання
    }
};

int main() {
    const int n = 20000, leaf = 16, queries = 20;
    std::printf("   d   leaves   visited    frac      dists\n");
    for (int d : {2, 3, 5, 8, 10, 12, 15, 20, 100}) {
        const std::vector<double> pts = gen(n, d, 20260808ULL + d);
        const std::vector<double> qs  = gen(queries, d, 20260808ULL + d + 0x51ED);
        KdCounted t(pts.data(), n, d, leaf);

        long vl = 0, dc = 0;
        for (int q = 0; q < queries; ++q) {
            const double* Q = qs.data() + static_cast<size_t>(q) * d;
            const int got = t.nearest(Q);
            vl += t.visitedLeaves;  dc += t.distCalls;

            int ref = 0;                                    // звіряння з перебором
            double bd = HUGE_VAL;
            for (int i = 0; i < n; ++i) {
                const double D2 = dist2(Q, pts.data() + static_cast<size_t>(i) * d, d);
                if (D2 < bd) { bd = D2; ref = i; }
            }
            if (got != ref) std::printf("  !!! d=%d q=%d: дерево збрехало\n", d, q);
        }
        const double avg = static_cast<double>(vl) / queries;
        std::printf("%4d   %6d   %7.1f   %5.1f%%   %8.0f\n",
                    d, t.leaves(), avg, 100.0 * avg / t.leaves(),
                    static_cast<double>(dc) / queries);
    }
}
