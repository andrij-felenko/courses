#include <algorithm>
#include <vector>

// Перший зріз: за ROI спадно. O(n log n).
std::vector<Strategy> rank_by_roi(std::vector<Strategy> strategies) {
    std::sort(strategies.begin(), strategies.end(),
              [](const Strategy& a, const Strategy& b) { return a.roi() > b.roi(); });
    return strategies;
}

struct Pick {
    std::vector<Strategy> chosen;
    double spent;
    double total;
};

// Іди по ранжованому списку й бери все, що ще влазить у бюджет.
Pick greedy_pick(const std::vector<Strategy>& strategies, double budget) {
    Pick p{{}, 0.0, 0.0};
    for (const auto& s : rank_by_roi(strategies)) {
        if (p.spent + s.cost <= budget) {
            p.chosen.push_back(s);
            p.spent += s.cost;
        }
    }
    for (const auto& s : p.chosen) p.total += s.benefit();
    return p;
}
