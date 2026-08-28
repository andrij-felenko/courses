    using Cand = std::pair<float, int>;      // (квадрат відстані, номер точки)

    void knn(int n, const Point& q, int k, std::priority_queue<Cand>& heap) const {
        const Node& nd = nodes_[n];
        if (nd.axis < 0) {
            for (int i = nd.begin; i < nd.end; ++i) {
                const float d2 = dist2(pts_[idx_[i]], q);
                if (static_cast<int>(heap.size()) < k) heap.emplace(d2, idx_[i]);
                else if (d2 < heap.top().first) { heap.pop(); heap.emplace(d2, idx_[i]); }
            }
            return;
        }
        const float diff = q.c[nd.axis] - nd.split;
        const int near = (diff < 0.0f) ? n + 1 : nd.right;
        const int far  = (diff < 0.0f) ? nd.right : n + 1;
        knn(near, q, k, heap);
        const float r2 = (static_cast<int>(heap.size()) < k) ? INFINITY : heap.top().first;
        if (diff * diff < r2) knn(far, q, k, heap);
    }
