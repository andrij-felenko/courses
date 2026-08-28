class DSATURSolver {
public:
    explicit DSATURSolver(const Graph& g) 
        : graph_(g), n_(g.size()), colors_(n_, 0),
          neighbor_colors_(n_, 0ULL), sat_deg_(n_, 0),
          uncolored_deg_(n_, 0), best_colors_(n_, 0) {
        for (size_t i = 0; i < n_; ++i) {
            uncolored_deg_[i] = static_cast<int>(graph_.degree(i));
        }
    }

    ColoringResult run_heuristic() {
        ColoringResult res;
        int max_color = 0;

        for (size_t step = 0; step < n_; ++step) {
            res.iterations++;
            int v = choose_next();
            if (v == -1) break;

            int c = 1;
            while ((neighbor_colors_[v] & (1ULL << c)) != 0ULL) {
                c++;
            }

            colors_[v] = c;
            max_color = std::max(max_color, c);

            for (size_t u = 0; u < n_; ++u) {
                if ((graph_.neighbors(v) & (1ULL << u)) != 0ULL && colors_[u] == 0) {
                    if ((neighbor_colors_[u] & (1ULL << c)) == 0ULL) {
                        neighbor_colors_[u] |= (1ULL << c);
                        sat_deg_[u]++;
                    }
                    uncolored_deg_[u]--;
                }
            }
        }

        res.colors = colors_;
        res.chromatic_number = max_color;
        res.is_valid = true;
        return res;
    }

    ColoringResult solve_exact() {
        ColoringResult heur = run_heuristic();
        best_k_ = heur.chromatic_number;
        best_colors_ = heur.colors;
        search_steps_ = 0;

        std::fill(colors_.begin(), colors_.end(), 0);
        std::fill(neighbor_colors_.begin(), neighbor_colors_.end(), 0ULL);
        std::fill(sat_deg_.begin(), sat_deg_.end(), 0);
        for (size_t i = 0; i < n_; ++i) {
            uncolored_deg_[i] = static_cast<int>(graph_.degree(i));
        }

        backtrack(0, 0);

        ColoringResult exact_res;
        exact_res.chromatic_number = best_k_;
        exact_res.colors = best_colors_;
        exact_res.iterations = search_steps_;
        exact_res.is_valid = true;
        return exact_res;
    }

private:
    [[nodiscard]] int choose_next() const noexcept {
        int best_v = -1;
        int max_sat = -1;
        int max_deg = -1;

        for (size_t v = 0; v < n_; ++v) {
            if (colors_[v] == 0) {
                if (sat_deg_[v] > max_sat || (sat_deg_[v] == max_sat && uncolored_deg_[v] > max_deg)) {
                    max_sat = sat_deg_[v];
                    max_deg = uncolored_deg_[v];
                    best_v = static_cast<int>(v);
                }
            }
        }
        return best_v;
    }

    void backtrack(size_t colored_count, int current_max_k) {
        search_steps_++;
        if (colored_count == n_) {
            if (current_max_k < best_k_) {
                best_k_ = current_max_k;
                best_colors_ = colors_;
            }
            return;
        }

        if (current_max_k >= best_k_) return;

        int v = choose_next();
        if (v == -1) return;

        for (int c = 1; c <= current_max_k + 1 && c < best_k_; ++c) {
            if ((neighbor_colors_[v] & (1ULL << c)) == 0ULL) {
                colors_[v] = c;

                std::vector<size_t> changed;
                for (size_t u = 0; u < n_; ++u) {
                    if ((graph_.neighbors(v) & (1ULL << u)) != 0ULL && colors_[u] == 0) {
                        uncolored_deg_[u]--;
                        if ((neighbor_colors_[u] & (1ULL << c)) == 0ULL) {
                            neighbor_colors_[u] |= (1ULL << c);
                            sat_deg_[u]++;
                            changed.push_back(u);
                        }
                    }
                }

                backtrack(colored_count + 1, std::max(current_max_k, c));

                colors_[v] = 0;
                for (size_t u : changed) {
                    neighbor_colors_[u] &= ~(1ULL << c);
                    sat_deg_[u]--;
                }
                for (size_t u = 0; u < n_; ++u) {
                    if ((graph_.neighbors(v) & (1ULL << u)) != 0ULL && colors_[u] == 0) {
                        uncolored_deg_[u]++;
                    }
                }
            }
        }
    }

    const Graph& graph_;
    size_t n_;
    std::vector<int> colors_;
    std::vector<uint64_t> neighbor_colors_;
    std::vector<int> sat_deg_;
    std::vector<int> uncolored_deg_;
    std::vector<int> best_colors_;
    int best_k_{1000};
    uint64_t search_steps_{0};
};

ColoringResult color_exact_solver(const Graph& g) {
    DSATURSolver solver(g);
    return solver.solve_exact();
}
