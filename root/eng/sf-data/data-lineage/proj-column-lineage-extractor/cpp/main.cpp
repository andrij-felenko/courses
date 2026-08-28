#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <regex>
#include <memory>

struct ColumnDependency {
    std::string target_table;
    std::string target_column;
    std::string source_table;
    std::string source_column;
    std::string expression_type;
};

class SQLLineageGraph {
public:
    std::vector<ColumnDependency> extract_lineage(
        std::string_view sql_query,
        std::string_view target_table
    ) {
        std::vector<ColumnDependency> results;
        std::unordered_map<std::string, std::string> aliases;

        std::string sql(sql_query);

        // 1. Пошук таблиць у секціях FROM та JOIN
        std::regex from_regex(R"(FROM\s+([a-zA-Z0-9_\.]+)(?:\s+(?:AS\s+)?([a-zA-Z0-9_]+))?)", std::regex::icase);
        std::smatch match;
        if (std::regex_search(sql, match, from_regex)) {
            std::string real_tbl = match[1].str();
            std::string alias = match[2].matched ? match[2].str() : real_tbl;
            aliases[alias] = real_tbl;
        }

        std::regex join_regex(R"(JOIN\s+([a-zA-Z0-9_\.]+)(?:\s+(?:AS\s+)?([a-zA-Z0-9_]+))?)", std::regex::icase);
        auto join_begin = std::sregex_iterator(sql.begin(), sql.end(), join_regex);
        auto join_end = std::sregex_iterator();
        for (auto it = join_begin; it != join_end; ++it) {
            std::string real_tbl = (*it)[1].str();
            std::string alias = (*it)[2].matched ? (*it)[2].str() : real_tbl;
            aliases[alias] = real_tbl;
        }

        // 2. Пошук виразів у SELECT ... FROM
        std::regex select_regex(R"(SELECT\s+([\s\S]*?)\s+FROM)", std::regex::icase);
        if (std::regex_search(sql, match, select_regex)) {
            std::string select_clause = match[1].str();
            auto projections = split_projections(select_clause);

            for (const auto& proj : projections) {
                analyze_projection(proj, target_table, aliases, results);
            }
        }

        return results;
    }

private:
    std::vector<std::string> split_projections(std::string_view clause) {
        std::vector<std::string> out;
        std::string cur;
        int depth = 0;
        for (char c : clause) {
            if (c == '(') ++depth;
            else if (c == ')') --depth;
            else if (c == ',' && depth == 0) {
                if (!cur.empty()) out.push_back(trim(cur));
                cur.clear();
                continue;
            }
            cur += c;
        }
        if (!cur.empty()) out.push_back(trim(cur));
        return out;
    }

    void analyze_projection(
        const std::string& proj,
        std::string_view target_table,
        const std::unordered_map<std::string, std::string>& aliases,
        std::vector<ColumnDependency>& out
    ) {
        std::regex as_regex(R"(\s+AS\s+([a-zA-Z0-9_]+)$)", std::regex::icase);
        std::smatch match;
        std::string target_col;
        std::string expr_body = proj;

        if (std::regex_search(proj, match, as_regex)) {
            target_col = match[1].str();
            expr_body = proj.substr(0, match.position());
        } else {
            auto dot_pos = proj.rfind('.');
            target_col = (dot_pos != std::string::npos) ? proj.substr(dot_pos + 1) : proj;
        }

        std::string expr_type = "TRANSFORM";
        if (std::regex_search(expr_body, std::regex(R"(\b(SUM|AVG|COUNT|MIN|MAX)\b)", std::regex::icase))) {
            expr_type = "AGGREGATION";
        } else if (std::regex_match(expr_body, std::regex(R"(^[a-zA-Z0-9_\.]+$)"))) {
            expr_type = "IDENTITY";
        }

        std::regex col_ref_regex(R"(([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+))");
        auto it_begin = std::sregex_iterator(expr_body.begin(), expr_body.end(), col_ref_regex);
        auto it_end = std::sregex_iterator();

        for (auto it = it_begin; it != it_end; ++it) {
            std::string alias = (*it)[1].str();
            std::string src_col = (*it)[2].str();
            std::string src_tbl = aliases.contains(alias) ? aliases.at(alias) : alias;

            out.push_back(ColumnDependency{
                .target_table = std::string(target_table),
                .target_column = target_col,
                .source_table = src_tbl,
                .source_column = src_col,
                .expression_type = expr_type
            });
        }
    }

    static std::string trim(std::string_view s) {
        size_t start = s.find_first_not_of(" \t\n\r");
        if (start == std::string::npos) return "";
        size_t end = s.find_last_not_of(" \t\n\r");
        return std::string(s.substr(start, end - start + 1));
    }
};

int main() {
    SQLLineageGraph graph;
    std::string query = 
        "SELECT o.order_id AS id, SUM(o.amount / fx.rate) AS revenue_usd "
        "FROM raw.orders AS o "
        "JOIN ref.fx_rates AS fx ON o.currency = fx.code";

    auto deps = graph.extract_lineage(query, "mart.fct_revenue");
    for (const auto& d : deps) {
        std::cout << "[" << d.expression_type << "] " 
                  << d.source_table << "." << d.source_column << " -> "
                  << d.target_table << "." << d.target_column << "\n";
    }
    return 0;
}
