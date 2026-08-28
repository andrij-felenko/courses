// fitness_checker.cpp — Статичний перевірник архітектурних меж C++20
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <filesystem>
#include <regex>
#include <set>
#include <map>
#include <stdexcept>

namespace fs = std::filesystem;

struct Violation {
    std::string source_file;
    std::size_t line_number;
    std::string included_header;
    std::string rule_name;
};

class ArchitectureFitnessGuard {
public:
    explicit ArchitectureFitnessGuard(fs::path root_dir) : root_dir_(std::move(root_dir)) {}

    // Заборона включення легасі-заголовків із зазначених каталогів
    void add_forbidden_rule(std::string source_pattern, std::string forbidden_header_substring) {
        forbidden_rules_.push_back({std::move(source_pattern), std::move(forbidden_header_substring)});
    }

    std::vector<Violation> inspect_codebase() {
        std::vector<Violation> violations;
        std::regex include_regex(R"#(^\s*#include\s*["<]([^">]+)[">])#");

        for (const auto& entry : fs::recursive_directory_iterator(root_dir_)) {
            if (!entry.is_regular_file()) continue;
            auto ext = entry.path().extension().string();
            if (ext != ".cpp" && ext != ".hpp" && ext != ".h" && ext != ".cc") continue;

            std::string rel_path = fs::relative(entry.path(), root_dir_).string();
            std::replace(rel_path.begin(), rel_path.end(), '\\', '/');

            std::ifstream file(entry.path());
            std::string line;
            std::size_t line_num = 0;

            while (std::getline(file, line)) {
                ++line_num;
                std::smatch match;
                if (std::regex_search(line, match, include_regex)) {
                    std::string header = match[1].str();

                    for (const auto& rule : forbidden_rules_) {
                        if (rel_path.find(rule.source_pattern) != std::string::npos &&
                            header.find(rule.forbidden_substring) != std::string::npos) {
                            violations.push_back({
                                rel_path,
                                line_num,
                                header,
                                "LAYER_VIOLATION: v2 code cannot include legacy v1 db headers"
                            });
                        }
                    }
                }
            }
        }
        return violations;
    }

private:
    struct Rule {
        std::string source_pattern;
        std::string forbidden_substring;
    };

    fs::path root_dir_;
    std::vector<Rule> forbidden_rules_;
};

int main(int argc, char* argv[]) {
    try {
        fs::path repo_root = (argc > 1) ? argv[1] : fs::current_path();
        ArchitectureFitnessGuard guard(repo_root);

        // Налаштування суворих архітектурних правил міграції
        guard.add_forbidden_rule("src/v2/", "v1/legacy_db/");
        guard.add_forbidden_rule("src/v2/", "postgres_raw_client.hpp");
        guard.add_forbidden_rule("src/services/twin/", "monolith_shared_state.h");

        std::cout << "[FITNESS GUARD] Запуск аналізу меж коду в: " << repo_root << std::endl;
        auto violations = guard.inspect_codebase();

        if (!violations.empty()) {
            std::cerr << "\n❌ ВИЯВЛЕНО ЕРОЗІЮ АРХІТЕКТУРИ (" << violations.size() << " порушень):\n";
            for (const auto& v : violations) {
                std::cerr << "  • " << v.source_file << ":" << v.line_number 
                          << " -> включено '" << v.included_header << "' [" << v.rule_name << "]\n";
            }
            return 1;
        }

        std::cout << "✅ [FITNESS GUARD] Ерозії коду не виявлено. Усі шви архітектури дотримано.\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання перевірника: " << ex.what() << std::endl;
        return 2;
    }
}
