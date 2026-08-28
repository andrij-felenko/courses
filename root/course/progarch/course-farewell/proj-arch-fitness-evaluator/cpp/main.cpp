#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <iomanip>
#include <numeric>
#include <algorithm>

enum class Layer {
    Domain = 0,
    UseCase = 1,
    Infrastructure = 2,
    Presentation = 2
};

struct ModuleNode {
    std::string name;
    Layer layer;
};

class FitnessArchitectureEvaluator {
public:
    struct AnalysisResult {
        std::string module_name;
        Layer layer;
        size_t afferent_ca{0};
        size_t efferent_ce{0};
        double instability{0.0};
    };

    struct Violation {
        std::string source_module;
        Layer source_layer;
        std::string target_module;
        Layer target_layer;
    };

    size_t add_module(std::string name, Layer layer) {
        size_t id = modules_.size();
        modules_.push_back({std::move(name), layer});
        adj_matrix_.resize(modules_.size(), std::vector<bool>(modules_.size(), false));
        for (auto& row : adj_matrix_) {
            row.resize(modules_.size(), false);
        }
        return id;
    }

    void add_dependency(size_t from_id, size_t to_id) {
        if (from_id < modules_.size() && to_id < modules_.size()) {
            adj_matrix_[from_id][to_id] = true;
        }
    }

    [[nodiscard]] std::vector<AnalysisResult> compute_metrics() const {
        std::vector<AnalysisResult> results;
        results.reserve(modules_.size());

        for (size_t i = 0; i < modules_.size(); ++i) {
            size_t ca = 0;
            size_t ce = 0;

            for (size_t j = 0; j < modules_.size(); ++j) {
                if (i == j) continue;
                if (adj_matrix_[i][j]) ++ce;
                if (adj_matrix_[j][i]) ++ca;
            }

            double inst = (ca + ce > 0) ? static_cast<double>(ce) / static_cast<double>(ca + ce) : 0.0;
            results.push_back({modules_[i].name, modules_[i].layer, ca, ce, inst});
        }
        return results;
    }

    [[nodiscard]] std::vector<Violation> find_layer_violations() const {
        std::vector<Violation> violations;

        for (size_t i = 0; i < modules_.size(); ++i) {
            for (size_t j = 0; j < modules_.size(); ++j) {
                if (i == j) continue;

                if (adj_matrix_[i][j]) {
                    if (static_cast<int>(modules_[i].layer) < static_cast<int>(modules_[j].layer)) {
                        violations.push_back({
                            modules_[i].name, modules_[i].layer,
                            modules_[j].name, modules_[j].layer
                        });
                    }
                }
            }
        }
        return violations;
    }

private:
    std::vector<ModuleNode> modules_;
    std::vector<std::vector<bool>> adj_matrix_;
};

int main() {
    FitnessArchitectureEvaluator evaluator;

    auto m_domain = evaluator.add_module("DomainCore", Layer::Domain);
    auto m_usecase = evaluator.add_module("OrderUseCase", Layer::UseCase);
    auto m_db = evaluator.add_module("PostgresAdapter", Layer::Infrastructure);
    auto m_web = evaluator.add_module("HttpController", Layer::Presentation);

    evaluator.add_dependency(m_web, m_usecase);
    evaluator.add_dependency(m_db, m_domain);
    evaluator.add_dependency(m_usecase, m_domain);

    auto metrics = evaluator.compute_metrics();
    std::cout << "=== СТАТИСТИКА НЕСТАБІЛЬНОСТІ МОДУЛІВ ===\n";
    for (const auto& res : metrics) {
        std::cout << "Модуль: " << std::left << std::setw(16) << res.module_name
                  << " | Ca=" << std::setw(2) << res.afferent_ca
                  << " | Ce=" << std::setw(2) << res.efferent_ce
                  << " | Instability I=" << std::fixed << std::setprecision(2) << res.instability << "\n";
    }

    auto violations = evaluator.find_layer_violations();
    std::cout << "\n=== РЕЗУЛЬТАТ ПЕРЕВІРКИ ФІТНЕС-ФУНКЦІЇ ===\n";
    if (violations.empty()) {
        std::cout << "✅ Усі фітнес-функції успішно виконано. Архітектурну ерозію не виявлено.\n";
        return 0;
    }

    for (const auto& v : violations) {
        std::cerr << "❌ ПОШКОДЖЕННЯ МЕЖІ: Модуль [" << v.source_module
                  << "] імпортує вищий шар [" << v.target_module << "]\n";
    }
    return 1;
}
