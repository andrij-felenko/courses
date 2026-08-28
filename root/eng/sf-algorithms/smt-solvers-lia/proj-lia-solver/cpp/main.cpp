#include <iostream>
#include <vector>
#include <optional>
#include <cmath>
#include <algorithm>
#include <limits>
#include <string_view>

enum class LiaResult {
    Sat,
    Unsat,
    Unknown
};

class LiaSolver {
public:
    static constexpr double Inf = std::numeric_limits<double>::infinity();
    static constexpr double Eps = 1e-9;

    struct VarState {
        double low = -Inf;
        double high = Inf;
        double val = 0.0;
        bool is_integer = true;
    };

    struct TrailEntry {
        size_t var_idx;
        double old_low;
        double old_high;
    };

    LiaSolver(size_t num_vars, size_t num_rows)
        : num_vars_(num_vars), num_rows_(num_rows),
          matrix_(num_rows, std::vector<double>(num_vars, 0.0)),
          basic_vars_(num_rows), non_basic_vars_(num_vars),
          vars_(num_vars + num_rows) {
        
        for (size_t i = 0; i < num_vars; ++i) {
            non_basic_vars_[i] = i;
            vars_[i].is_integer = true;
        }
        for (size_t r = 0; r < num_rows; ++r) {
            basic_vars_[r] = num_vars + r;
            vars_[num_vars + r].low = 0.0;
            vars_[num_vars + r].high = 0.0;
            vars_[num_vars + r].is_integer = false;
        }
    }

    void set_matrix_coeff(size_t row, size_t col, double val) {
        matrix_[row][col] = val;
    }

    void set_slack_bound(size_t row, double low, double high) {
        vars_[num_vars_ + row].low = low;
        vars_[num_vars_ + row].high = high;
    }

    void push() {
        scope_markers_.push_back(trail_.size());
    }

    void pop() {
        if (scope_markers_.empty()) return;
        size_t target_size = scope_markers_.back();
        scope_markers_.pop_back();
        
        while (trail_.size() > target_size) {
            const auto& e = trail_.back();
            vars_[e.var_idx].low = e.old_low;
            vars_[e.var_idx].high = e.old_high;
            trail_.pop_back();
        }
    }

    bool set_bound(size_t var_idx, double low, double high) {
        trail_.push_back({var_idx, vars_[var_idx].low, vars_[var_idx].high});
        vars_[var_idx].low = std::max(vars_[var_idx].low, low);
        vars_[var_idx].high = std::min(vars_[var_idx].high, high);
        return vars_[var_idx].low <= vars_[var_idx].high + Eps;
    }

    LiaResult check_real_relaxation() {
        int max_iter = 1000;
        while (max_iter-- > 0) {
            std::optional<size_t> viol_row;
            bool is_below = false;

            for (size_t r = 0; r < num_rows_; ++r) {
                size_t b_var = basic_vars_[r];
                if (vars_[b_var].val < vars_[b_var].low - Eps) {
                    viol_row = r;
                    is_below = true;
                    break;
                }
                if (vars_[b_var].val > vars_[b_var].high + Eps) {
                    viol_row = r;
                    is_below = false;
                    break;
                }
            }

            if (!viol_row.has_value()) {
                return LiaResult::Sat;
            }

            size_t r = *viol_row;
            std::optional<size_t> pivot_col;

            for (size_t c = 0; c < num_vars_; ++c) {
                double coeff = matrix_[r][c];
                size_t nb_var = non_basic_vars_[c];

                if (is_below) {
                    if (coeff > Eps && vars_[nb_var].val < vars_[nb_var].high - Eps) {
                        pivot_col = c;
                        break;
                    }
                    if (coeff < -Eps && vars_[nb_var].val > vars_[nb_var].low + Eps) {
                        pivot_col = c;
                        break;
                    }
                } else {
                    if (coeff > Eps && vars_[nb_var].val > vars_[nb_var].low + Eps) {
                        pivot_col = c;
                        break;
                    }
                    if (coeff < -Eps && vars_[nb_var].val < vars_[nb_var].high - Eps) {
                        pivot_col = c;
                        break;
                    }
                }
            }

            if (!pivot_col.has_value()) {
                return LiaResult::Unsat;
            }

            pivot(r, *pivot_col);
        }
        return LiaResult::Unknown;
    }

    LiaResult solve_integer() {
        LiaResult res = check_real_relaxation();
        if (res != LiaResult::Sat) return res;

        std::optional<size_t> frac_var;
        double frac_val = 0.0;

        for (size_t i = 0; i < num_vars_; ++i) {
            if (vars_[i].is_integer && !is_integer_value(vars_[i].val)) {
                frac_var = i;
                frac_val = vars_[i].val;
                break;
            }
        }

        if (!frac_var.has_value()) {
            return LiaResult::Sat;
        }

        size_t v = *frac_var;

        // Гілка x_i <= floor(val)
        push();
        if (set_bound(v, vars_[v].low, std::floor(frac_val))) {
            if (solve_integer() == LiaResult::Sat) return LiaResult::Sat;
        }
        pop();

        // Гілка x_i >= ceil(val)
        push();
        if (set_bound(v, std::ceil(frac_val), vars_[v].high)) {
            if (solve_integer() == LiaResult::Sat) return LiaResult::Sat;
        }
        pop();

        return LiaResult::Unsat;
    }

    double get_value(size_t var_idx) const {
        return vars_.at(var_idx).val;
    }

private:
    size_t num_vars_;
    size_t num_rows_;
    std::vector<std::vector<double>> matrix_;
    std::vector<size_t> basic_vars_;
    std::vector<size_t> non_basic_vars_;
    std::vector<VarState> vars_;
    std::vector<TrailEntry> trail_;
    std::vector<size_t> scope_markers_;

    static bool is_integer_value(double v) {
        return std::abs(v - std::round(v)) < Eps;
    }

    void update_row_values(size_t row) {
        double sum = 0.0;
        for (size_t c = 0; c < num_vars_; ++c) {
            sum += matrix_[row][c] * vars_[non_basic_vars_[c]].val;
        }
        vars_[basic_vars_[row]].val = sum;
    }

    void pivot(size_t row, size_t col) {
        double a_ij = matrix_[row][col];
        size_t b_var = basic_vars_[row];
        size_t nb_var = non_basic_vars_[col];

        basic_vars_[row] = nb_var;
        non_basic_vars_[col] = b_var;

        matrix_[row][col] = 1.0 / a_ij;
        for (size_t c = 0; c < num_vars_; ++c) {
            if (c != col) {
                matrix_[row][c] /= -a_ij;
            }
        }

        for (size_t r = 0; r < num_rows_; ++r) {
            if (r != row) {
                double gamma = matrix_[r][col];
                matrix_[r][col] = 0.0;
                for (size_t c = 0; c < num_vars_; ++c) {
                    matrix_[r][c] += gamma * matrix_[row][c];
                }
            }
        }

        for (size_t r = 0; r < num_rows_; ++r) {
            update_row_values(r);
        }
    }
};

int main() {
    // 2*x1 + x2 = 5, 0 <= x1 <= 2, 0 <= x2 <= 2, x1, x2 in Z
    LiaSolver solver(2, 1);
    solver.set_matrix_coeff(0, 0, 2.0);
    solver.set_matrix_coeff(0, 1, 1.0);
    solver.set_slack_bound(0, 5.0, 5.0); // s0 = 5

    solver.set_bound(0, 0.0, 2.0);
    solver.set_bound(1, 0.0, 2.0);

    if (solver.solve_integer() == LiaResult::Sat) {
        std::cout << "LIA SAT: x1 = " << solver.get_value(0) 
                  << ", x2 = " << solver.get_value(1) << "\n";
    } else {
        std::cout << "LIA UNSAT\n";
    }
    return 0;
}
