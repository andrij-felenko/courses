    struct Box { float lo[D], hi[D]; };

    static bool covers(const Box& w, const Box& c) {      // вікно накриває комірку цілком
        for (int a = 0; a < D; ++a)
            if (c.lo[a] < w.lo[a] || c.hi[a] > w.hi[a]) return false;
        return true;
    }
    static bool disjoint(const Box& w, const Box& c) {
        for (int a = 0; a < D; ++a)
            if (c.hi[a] < w.lo[a] || c.lo[a] > w.hi[a]) return true;
        return false;
    }
    static bool inside(const Box& w, const Point& p) {
        for (int a = 0; a < D; ++a)
            if (p.c[a] < w.lo[a] || p.c[a] > w.hi[a]) return false;
        return true;
    }

    void range(int n, const Box& w, const Box& cell, std::vector<int>& out) const {
        if (disjoint(w, cell)) return;                    // геть разом з усім піддеревом
        const Node& nd = nodes_[n];
        if (covers(w, cell)) {                            // ГУРТОМ, без перевірки точок
            out.insert(out.end(), idx_.begin() + nd.begin, idx_.begin() + nd.end);
            return;
        }
        if (nd.axis < 0) {
            for (int i = nd.begin; i < nd.end; ++i)
                if (inside(w, pts_[idx_[i]])) out.push_back(idx_[i]);
            return;
        }
        Box l = cell, r = cell;
        l.hi[nd.axis] = nd.split;
        r.lo[nd.axis] = nd.split;
        range(n + 1, w, l, out);
        range(nd.right, w, r, out);
    }
