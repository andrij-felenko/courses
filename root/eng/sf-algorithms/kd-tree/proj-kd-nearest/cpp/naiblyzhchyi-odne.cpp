    static float dist2(const Point& a, const Point& b) {
        float s = 0.0f;
        for (int i = 0; i < D; ++i) { const float t = a.c[i] - b.c[i]; s += t * t; }
        return s;
    }

    void nn(int n, const Point& q, int& best, float& bestD2) const {
        const Node& nd = nodes_[n];
        if (nd.axis < 0) {                                // листок — перебір підряд
            for (int i = nd.begin; i < nd.end; ++i) {
                const float d2 = dist2(pts_[idx_[i]], q);
                if (d2 < bestD2) { bestD2 = d2; best = idx_[i]; }
            }
            return;
        }
        const float diff = q.c[nd.axis] - nd.split;
        const int near = (diff < 0.0f) ? n + 1 : nd.right;
        const int far  = (diff < 0.0f) ? nd.right : n + 1;
        nn(near, q, best, bestD2);                        // спершу СВОЯ половина
        if (diff * diff < bestD2) nn(far, q, best, bestD2);
    }

public:
    int nearest(const Point& q) const {
        int best = -1;
        float bestD2 = INFINITY;
        if (!nodes_.empty()) nn(0, q, best, bestD2);
        return best;
    }
