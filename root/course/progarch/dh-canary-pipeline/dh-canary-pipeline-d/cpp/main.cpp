#include <algorithm>

double compute_canary_score(double err_rate_diff, double latency_ratio) {
    double score_val = 100.0;
    if (err_rate_diff > 0.005) {
        score_val -= 50.0;
    }
    if (latency_ratio > 1.20) {
        score_val -= 30.0;
    }
    return std::max(0.0, score_val);
}
