/* Структура елемента черги пріоритетів */
struct VWElement {
    double area{0.0};
    size_t id{0};

    bool operator>(const VWElement& other) const noexcept {
        return area > other.area;
    }
};

/* Спрощення Вісвалінгам–Вайатта на купі min-heap */
[[nodiscard]] std::vector<Point> simplifyVisvalingamWhyatt(std::span<const Point> points, size_t targetK) {
    const size_t n = points.size();
    if (n <= targetK || n <= 2) {
        return std::vector<Point>(points.begin(), points.end());
    }

    struct Node {
        Point pt;
        double area{0.0};
        size_t prev{0};
        size_t next{0};
        bool removed{false};
    };

    std::vector<Node> nodes(n);
    std::priority_queue<VWElement, std::vector<VWElement>, std::greater<VWElement>> pq;

    for (size_t i = 0; i < n; ++i) {
        nodes[i].pt = points[i];
        nodes[i].prev = (i > 0) ? (i - 1) : 0;
        nodes[i].next = (i + 1 < n) ? (i + 1) : n - 1;
        nodes[i].removed = false;

        if (i > 0 && i + 1 < n) {
            const double cross = (points[i].x - points[i - 1].x) * (points[i + 1].y - points[i - 1].y)
                               - (points[i].y - points[i - 1].y) * (points[i + 1].x - points[i - 1].x);
            nodes[i].area = 0.5 * std::abs(cross);
            pq.push({nodes[i].area, i});
        } else {
            nodes[i].area = 1e30;
        }
    }

    size_t currentCount = n;
    while (currentCount > targetK && !pq.empty()) {
        const auto [area, idx] = pq.top();
        pq.pop();

        if (nodes[idx].removed || std::abs(nodes[idx].area - area) > 1e-9) {
            continue;
        }

        nodes[idx].removed = true;
        const size_t p = nodes[idx].prev;
        const size_t nx = nodes[idx].next;
        nodes[p].next = nx;
        nodes[nx].prev = p;

        if (p > 0) {
            const double crossP = (nodes[p].pt.x - nodes[nodes[p].prev].pt.x) * (nodes[nx].pt.y - nodes[nodes[p].prev].pt.y)
                                - (nodes[p].pt.y - nodes[nodes[p].prev].pt.y) * (nodes[nx].pt.x - nodes[nodes[p].prev].pt.x);
            nodes[p].area = 0.5 * std::abs(crossP);
            pq.push({nodes[p].area, p});
        }

        if (nx + 1 < n) {
            const double crossNx = (nodes[nx].pt.x - nodes[p].pt.x) * (nodes[nodes[nx].next].pt.y - nodes[p].pt.y)
                                 - (nodes[nx].pt.y - nodes[p].pt.y) * (nodes[nodes[nx].next].pt.x - nodes[p].pt.x);
            nodes[nx].area = 0.5 * std::abs(crossNx);
            pq.push({nodes[nx].area, nx});
        }

        --currentCount;
    }

    std::vector<Point> result;
    result.reserve(targetK);
    for (size_t i = 0; i < n; ++i) {
        if (!nodes[i].removed) {
            result.push_back(nodes[i].pt);
        }
    }
    return result;
}
