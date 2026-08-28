typedef struct VWNode {
    Point pt;
    double area;
    size_t prev;
    size_t next;
    bool removed;
} VWNode;

static inline double triangle_area(Point a, Point b, Point c) {
    double cross = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
    return 0.5 * fabs(cross);
}

/* Спрощення за методом ефективної площі до цільової кількості точок target_k */
size_t simplify_visvalingam_whyatt(const Point* pts, size_t n, size_t target_k, Point* out) {
    if (n <= target_k || n <= 2) {
        for (size_t i = 0; i < n; ++i) out[i] = pts[i];
        return n;
    }

    VWNode* nodes = (VWNode*)malloc(n * sizeof(VWNode));
    if (!nodes) return 0;

    for (size_t i = 0; i < n; ++i) {
        nodes[i].pt = pts[i];
        nodes[i].prev = (i > 0) ? (i - 1) : 0;
        nodes[i].next = (i + 1 < n) ? (i + 1) : n - 1;
        nodes[i].removed = false;
        if (i > 0 && i < n - 1) {
            nodes[i].area = triangle_area(pts[i - 1], pts[i], pts[i + 1]);
        } else {
            nodes[i].area = 1e30; /* Кінцеві вершини не видаляються */
        }
    }

    size_t current_count = n;
    while (current_count > target_k) {
        double min_area = 1e30;
        size_t min_idx = 0;

        for (size_t i = 1; i < n - 1; ++i) {
            if (!nodes[i].removed && nodes[i].area < min_area) {
                min_area = nodes[i].area;
                min_idx = i;
            }
        }

        if (min_idx == 0) break;

        /* Видалення вершини з ланцюжка */
        nodes[min_idx].removed = true;
        size_t p = nodes[min_idx].prev;
        size_t nx = nodes[min_idx].next;
        nodes[p].next = nx;
        nodes[nx].prev = p;

        /* Перерахунок площ сусідів */
        if (p > 0) {
            nodes[p].area = triangle_area(nodes[nodes[p].prev].pt, nodes[p].pt, nodes[nx].pt);
        }
        if (nx < n - 1) {
            nodes[nx].area = triangle_area(nodes[p].pt, nodes[nx].pt, nodes[nodes[nx].next].pt);
        }

        current_count--;
    }

    size_t out_count = 0;
    for (size_t i = 0; i < n; ++i) {
        if (!nodes[i].removed) {
            out[out_count++] = nodes[i].pt;
        }
    }

    free(nodes);
    return out_count;
}
