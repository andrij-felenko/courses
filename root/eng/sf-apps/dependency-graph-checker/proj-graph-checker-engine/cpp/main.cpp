#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <stack>
#include <algorithm>
#include <string_view>
#include <span>

enum class Layer {
    Infrastructure = 0,
    Domain = 1,
    Application = 2,
    Presentation = 3
};

struct Node {
    std::string name;
    Layer layer;
    int context_id;
};

class DependencyGraphChecker {
public:
    int add_node(std::string name, Layer layer, int context_id) {
        if (auto it = name_to_id_.find(name); it != name_to_id_.end()) {
            return it->second;
        }
        int id = static_cast<int>(nodes_.size());
        name_to_id_[name] = id;
        nodes_.push_back(Node{std::move(name), layer, context_id});
        adj_.emplace_back();
        return id;
    }

    void add_dependency(int from, int to) {
        adj_[from].push_back(to);
    }

    struct AnalysisReport {
        std::vector<std::vector<std::string>> cycles;
        std::vector<std::string> layer_violations;
        bool has_violations() const { return !cycles.empty() || !layer_violations.empty(); }
    };

    AnalysisReport analyze() const {
        AnalysisReport report;
        find_cycles(report);
        check_layers(report);
        return report;
    }

private:
    std::vector<Node> nodes_;
    std::unordered_map<std::string, int> name_to_id_;
    std::vector<std::vector<int>> adj_;

    void find_cycles(AnalysisReport& report) const {
        int n = static_cast<int>(nodes_.size());
        std::vector<int> dfn(n, 0);
        std::vector<int> low(n, 0);
        std::vector<bool> in_stack(n, false);
        std::stack<int> st;
        int timer = 0;

        auto tarjan_dfs = [&](auto& self, int u) -> void {
            dfn[u] = low[u] = ++timer;
            st.push(u);
            in_stack[u] = true;

            for (int v : adj_[u]) {
                if (dfn[v] == 0) {
                    /* Пряме дерево обходу DFS */
                    self(self, v);
                    low[u] = std::min(low[u], low[v]);
                } else if (in_stack[v]) {
                    /* Зворотне ребро у вершину, активну в стеку */
                    low[u] = std::min(low[u], dfn[v]);
                }
            }

            /* Вершина u є коренем сильно зв'язаної компоненти */
            if (low[u] == dfn[u]) {
                std::vector<std::string> scc_group;
                while (!st.empty()) {
                    int node = st.top();
                    st.pop();
                    in_stack[node] = false;
                    scc_group.push_back(nodes_[node].name);
                    if (node == u) break;
                }
                if (scc_group.size() > 1) {
                    report.cycles.push_back(std::move(scc_group));
                }
            }
        };

        for (int i = 0; i < n; ++i) {
            if (dfn[i] == 0) {
                tarjan_dfs(tarjan_dfs, i);
            }
        }
    }

    void check_layers(AnalysisReport& report) const {
        for (size_t u = 0; u < adj_.size(); ++u) {
            for (int v : adj_[u]) {
                if (nodes_[u].layer < nodes_[v].layer) {
                    report.layer_violations.push_back(
                        "Зворотна залежність: " + nodes_[u].name + " (рівень " +
                        std::to_string(static_cast<int>(nodes_[u].layer)) + ") -> " +
                        nodes_[v].name + " (рівень " +
                        std::to_string(static_cast<int>(nodes_[v].layer)) + ")"
                    );
                }
            }
        }
    }
};

int main() {
    DependencyGraphChecker checker;

    int api   = checker.add_node("Presentation.HttpApi", Layer::Presentation, 1);
    int order = checker.add_node("Application.OrderService", Layer::Application, 1);
    int core  = checker.add_node("Domain.OrderCore", Layer::Domain, 1);
    int repo  = checker.add_node("Infrastructure.PostgresRepo", Layer::Infrastructure, 1);
    int bill  = checker.add_node("Application.BillingService", Layer::Application, 2);

    /* Дозволені залежності */
    checker.add_dependency(api, order);
    checker.add_dependency(order, core);
    checker.add_dependency(order, repo);

    /* Порушення 1: Зворотна залежність Domain -> Infrastructure (DIP) */
    checker.add_dependency(core, repo);

    /* Порушення 2: Циклічна залежність між сервісами */
    checker.add_dependency(order, bill);
    checker.add_dependency(bill, order);

    auto report = checker.analyze();

    std::cout << "=== СТАТИЧНИЙ АНАЛІЗ АРХІТЕКТУРНИХ ЗАЛЕЖНОСТЕЙ (C++) ===\n";
    for (size_t i = 0; i < report.cycles.size(); ++i) {
        std::cout << "[ПОМИЛКА: ЦИКЛ #" << (i + 1) << "]: ";
        for (size_t j = 0; j < report.cycles[i].size(); ++j) {
            std::cout << report.cycles[i][j] << (j + 1 < report.cycles[i].size() ? " <-> " : "\n");
        }
    }

    for (const auto& violation : report.layer_violations) {
        std::cout << "[ПОМИЛКА: ШАР] " << violation << "\n";
    }

    return report.has_violations() ? 1 : 0;
}
