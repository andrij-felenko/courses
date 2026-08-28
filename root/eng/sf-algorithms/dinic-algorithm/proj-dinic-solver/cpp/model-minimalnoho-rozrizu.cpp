#include <iostream>
#include <vector>
#include <numeric>

struct ProjectSelector {
    int num_projects;
    std::vector<int64_t> weights;
    std::vector<std::pair<int, int>> dependencies;

    ProjectSelector(int n) : num_projects(n), weights(n) {}

    void set_weight(int project_id, int64_t weight) {
        weights[project_id] = weight;
    }

    void add_dependency(int from_project, int to_project) {
        dependencies.emplace_back(from_project, to_project);
    }

    std::pair<int64_t, std::vector<int>> solve() {
        int s = num_projects;
        int t = num_projects + 1;
        DinicSolver<int64_t> solver(num_projects + 2);
        const int64_t inf = 1e15;

        int64_t positive_sum = 0;

        for (int i = 0; i < num_projects; ++i) {
            if (weights[i] > 0) {
                solver.add_edge(s, i, weights[i]);
                positive_sum += weights[i];
            } else if (weights[i] < 0) {
                solver.add_edge(i, t, -weights[i]);
            }
        }

        for (const auto& dep : dependencies) {
            solver.add_edge(dep.first, dep.second, inf);
        }

        int64_t min_cut_val = solver.max_flow(s, t);
        int64_t max_profit = positive_sum - min_cut_val;

        std::vector<bool> in_s = solver.min_cut(s);
        std::vector<int> selected_projects;

        for (int i = 0; i < num_projects; ++i) {
            if (in_s[i]) {
                selected_projects.push_back(i);
            }
        }

        return {max_profit, selected_projects};
    }
};
