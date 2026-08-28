// dh_coupling_analyzer.cpp — Ідіоматичний C++20 аналізатор зчеплення та Extraction Score
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <optional>
#include <string_view>
#include <algorithm>
#include <iomanip>

struct ContextMetrics {
    double resource_asymmetry{0.0};
    double deploy_autonomy{0.0};
    double fault_isolation{0.0};
    double compliance_wall{0.0};
};

class BoundedContext {
public:
    BoundedContext(std::string name, ContextMetrics metrics, std::vector<std::string> tables)
        : name_(std::move(name)), metrics_(metrics), tables_(std::move(tables)) {}

    [[nodiscard]] const std::string& name() const noexcept { return name_; }
    [[nodiscard]] const ContextMetrics& metrics() const noexcept { return metrics_; }
    [[nodiscard]] const std::vector<std::string>& tables() const noexcept { return tables_; }

    [[nodiscard]] bool owns_table(std::string_view table_name) const noexcept {
        return std::find(tables_.begin(), tables_.end(), table_name) != tables_.end();
    }

private:
    std::string name_;
    ContextMetrics metrics_;
    std::vector<std::string> tables_;
};

class CouplingAnalyzer {
public:
    void register_context(BoundedContext ctx) {
        for (const auto& table : ctx.tables()) {
            table_to_context_map_[table] = ctx.name();
        }
        contexts_.emplace(ctx.name(), std::move(ctx));
    }

    void process_sql_query(std::string_view sql) {
        if (sql.find("JOIN") == std::string_view::npos && sql.find("join") == std::string_view::npos) {
            return;
        }

        // Автоматичний аналіз таблиць у запиті
        auto [table_a, table_b] = parse_join_tables(sql);
        if (table_a.empty() || table_b.empty()) return;

        auto ctx_a = find_context(table_a);
        auto ctx_b = find_context(table_b);

        if (ctx_a && ctx_b && *ctx_a != *ctx_b) {
            std::string key = make_edge_key(*ctx_a, *ctx_b);
            cross_joins_[key]++;
        }
    }

    [[nodiscard]] double calculate_score(const std::string& context_name) const {
        auto it = contexts_.find(context_name);
        if (it == contexts_.cend()) return 0.0;

        const auto& ctx = it->second;
        const auto& m = ctx.metrics();

        int total_joins = 0;
        for (const auto& [edge_key, count] : cross_joins_) {
            if (edge_key.find(context_name) != std::string::npos) {
                total_joins += count;
            }
        }

        double penalty = total_joins * 1.5;
        return (2.5 * m.resource_asymmetry) +
               (2.0 * m.deploy_autonomy) +
               (3.0 * m.fault_isolation) +
               (3.5 * m.compliance_wall) -
               penalty;
    }

    void print_audit_report() const {
        std::cout << "=== Результати сервіс-аудиту Digital Homes (C++20) ===\n";
        for (const auto& [name, ctx] : contexts_) {
            double score = calculate_score(name);
            std::cout << "Домен: " << std::left << std::setw(20) << name
                      << " | Score: " << std::right << std::setw(6) << std::fixed << std::setprecision(1) << score
                      << " | Вердикт: " << (score >= 15.0 ? "🟢 ВИДІЛЯТИ СЕРВІС" : "🔴 ЗАЛИШИТИ В МОНОЛІТІ")
                      << "\n";
        }
    }

private:
    [[nodiscard]] std::optional<std::string> find_context(std::string_view table) const {
        auto it = table_to_context_map_.find(std::string(table));
        if (it != table_to_context_map_.end()) return it->second;
        return std::nullopt;
    }

    static std::string make_edge_key(std::string_view a, std::string_view b) {
        return (a < b) ? std::string(a) + ":" + std::string(b) : std::string(b) + ":" + std::string(a);
    }

    static std::pair<std::string, std::string> parse_join_tables(std::string_view sql) {
        // Спрощений витяг таблиць із SQL
        size_t from_pos = sql.find("FROM ");
        if (from_pos == std::string_view::npos) from_pos = sql.find("from ");
        size_t join_pos = sql.find("JOIN ");
        if (join_pos == std::string_view::npos) join_pos = sql.find("join ");

        if (from_pos == std::string_view::npos || join_pos == std::string_view::npos) return {"", ""};

        std::string t1(sql.substr(from_pos + 5, join_pos - (from_pos + 5)));
        t1.erase(std::remove(t1.begin(), t1.end(), ' '), t1.end());

        std::string t2(sql.substr(join_pos + 5, 20));
        size_t space_pos = t2.find(' ');
        if (space_pos != std::string::npos) t2 = t2.substr(0, space_pos);

        return {t1, t2};
    }

    std::unordered_map<std::string, BoundedContext> contexts_;
    std::unordered_map<std::string, std::string> table_to_context_map_;
    std::unordered_map<std::string, int> cross_joins_;
};

int main() {
    CouplingAnalyzer analyzer;

    analyzer.register_context(BoundedContext("dh-telemetry", {9.5, 8.0, 4.0, 0.0}, {"telemetry_events"}));
    analyzer.register_context(BoundedContext("dh-video", {9.0, 6.0, 9.5, 0.0}, {"video_feeds"}));
    analyzer.register_context(BoundedContext("dh-device-mgmt", {3.0, 3.0, 2.0, 0.0}, {"devices"}));
    analyzer.register_context(BoundedContext("dh-digital-twin", {4.0, 4.0, 2.0, 0.0}, {"device_states"}));

    analyzer.process_sql_query("SELECT * FROM device_states JOIN devices ON device_states.id = devices.id");
    analyzer.process_sql_query("SELECT * FROM device_states JOIN devices ON device_states.id = devices.id");

    analyzer.print_audit_report();
    return 0;
}
