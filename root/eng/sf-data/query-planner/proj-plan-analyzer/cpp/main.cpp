#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <string_view>
#include <iomanip>

struct DiagnosticSummary {
    int total_nodes = 0;
    int cardinality_warnings = 0;
    int disk_spills = 0;
    int filter_warnings = 0;
    int64_t total_shared_hit = 0;
    int64_t total_shared_read = 0;
};

class PlanNode {
public:
    std::string node_type;
    std::string relation_name;
    double startup_cost = 0.0;
    double total_cost = 0.0;
    double plan_rows = 0.0;
    double actual_time_ms = 0.0;
    double actual_rows = 0.0;
    int actual_loops = 1;
    int64_t shared_hit_blocks = 0;
    int64_t shared_read_blocks = 0;
    int64_t rows_removed_filter = 0;
    bool spilled_to_disk = false;

    std::vector<std::unique_ptr<PlanNode>> children;

    PlanNode(std::string_view type, std::string_view rel, double cost,
             double plan_r, double act_time, double act_r, int loops = 1)
        : node_type(type), relation_name(rel), total_cost(cost),
          plan_rows(plan_r), actual_time_ms(act_time), actual_rows(act_r),
          actual_loops(loops) {}

    void add_child(std::unique_ptr<PlanNode> child) {
        if (child) children.push_back(std::move(child));
    }
};

class PlanAnalyzer {
public:
    static void generate_report(const PlanNode& root) {
        std::cout << "================ ЗВІТ АНАЛІЗУ ПЛАНУ EXPLAIN ================\n";
        DiagnosticSummary summary;
        traverse(root, 0, summary);

        std::cout << "\n----------------------- ПІДСУМОК -----------------------\n";
        std::cout << "Всього вузлів у дереві: " << summary.total_nodes << "\n";
        std::cout << "Помилок кардинальності: " << summary.cardinality_warnings << "\n";
        std::cout << "Скидань на диск:       " << summary.disk_spills << "\n";
        std::cout << "Вузлів із високою фільтрацією: " << summary.filter_warnings << "\n";

        const int64_t total_blocks = summary.total_shared_hit + summary.total_shared_read;
        if (total_blocks > 0) {
            const double hit_ratio = static_cast<double>(summary.total_shared_hit) /
                                     static_cast<double>(total_blocks) * 100.0;
            std::cout << std::fixed << std::setprecision(2);
            std::cout << "Ефективність кешу (Hit Ratio): " << hit_ratio << "% ("
                      << summary.total_shared_hit << " hit, " << summary.total_shared_read << " read)\n";
            if (hit_ratio < 95.0 && summary.total_shared_read > 500) {
                std::cout << "⚠️  [УВАГА: Кеш] Hit ratio нижчий за 95%. Можливий дефіцит пам'яті.\n";
            }
        }
        std::cout << "============================================================\n";
    }

private:
    static void traverse(const PlanNode& node, int depth, DiagnosticSummary& summary) {
        summary.total_nodes++;
        summary.total_shared_hit += node.shared_hit_blocks;
        summary.total_shared_read += node.shared_read_blocks;

        const double total_actual_rows = node.actual_rows * node.actual_loops;
        const double ratio = node.plan_rows > 0.0 ? total_actual_rows / node.plan_rows : 1.0;

        std::string indent(depth * 2, ' ');
        std::cout << indent << "-> " << node.node_type;
        if (!node.relation_name.empty()) {
            std::cout << " on " << node.relation_name;
        }
        std::cout << std::fixed << std::setprecision(2);
        std::cout << " (cost=" << node.total_cost << ", act_time="
                  << (node.actual_time_ms * node.actual_loops) << " ms, act_rows="
                  << total_actual_rows << ", plan_rows=" << node.plan_rows << ")\n";

        // 1. Кардинальність
        if ((ratio > 10.0 || ratio < 0.1) && total_actual_rows > 100.0) {
            summary.cardinality_warnings++;
            std::cout << indent << "  ⚠️  [УВАГА: Кардинальність] Прогноз " << node.plan_rows
                      << " рядків, факт: " << total_actual_rows << " (коефіцієнт " << ratio << "x)\n";
        }

        // 2. Скидання на диск
        if (node.spilled_to_disk) {
            summary.disk_spills++;
            std::cout << indent << "  ⚠️  [КРИТИЧНО: Диск] Вузол скинув дані на диск через нестачу work_mem!\n";
        }

        // 3. Фільтрація
        if (node.rows_removed_filter > 10000) {
            summary.filter_warnings++;
            std::cout << indent << "  ⚠️  [УВАГА: Фільтр] Відкинуто " << node.rows_removed_filter
                      << " рядків предиката. Потрібен індекс!\n";
        }

        for (const auto& child : node.children) {
            if (child) traverse(*child, depth + 1, summary);
        }
    }
};

int main() {
    auto root = std::make_unique<PlanNode>("Hash Join", "", 942.50, 4300, 14.30, 4120, 1);
    root->shared_hit_blocks = 1200;
    root->shared_read_blocks = 450;

    auto scan_orders = std::make_unique<PlanNode>("Seq Scan", "orders", 540.00, 15000, 6.80, 15000, 1);
    scan_orders->rows_removed_filter = 35000;
    scan_orders->shared_hit_blocks = 800;
    scan_orders->shared_read_blocks = 400;

    auto hash_node = std::make_unique<PlanNode>("Hash", "", 160.00, 1200, 0.74, 1180, 1);
    auto scan_users = std::make_unique<PlanNode>("Index Scan", "users", 160.00, 120, 0.52, 1180, 1);
    scan_users->shared_hit_blocks = 400;
    scan_users->shared_read_blocks = 50;

    hash_node->add_child(std::move(scan_users));
    root->add_child(std::move(scan_orders));
    root->add_child(std::move(hash_node));

    PlanAnalyzer::generate_report(*root);
    return 0;
}
