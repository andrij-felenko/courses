// adr_checker.cpp - Ідіоматичний статичний аналізатор фітнес-функцій (C++20 version)
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <filesystem>
#include <expected>

namespace fs = std::filesystem;

struct ArchRule {
    std::string source_context;
    std::string forbidden_target;
    std::string adr_id;
};

class FitnessAuditEngine {
private:
    std::vector<ArchRule> rules_;

public:
    FitnessAuditEngine() {
        // Конфігурація правил на основі журналу ADR Digital Homes
        rules_.push_back({"telemetry", "billing_db", "ADR-004"});
        rules_.push_back({"edge_engine", "user_auth", "ADR-012"});
    }

    [[nodiscard]] std::expected<size_t, std::string> audit_file(const fs::path& filepath, std::string_view current_context) const {
        if (!fs::exists(filepath)) {
            return std::unexpected("Файл не існує: " + filepath.string());
        }

        std::ifstream file(filepath);
        if (!file.is_open()) {
            return std::unexpected("Не вдалося відкрити файл: " + filepath.string());
        }

        std::string line;
        size_t line_num = 0;
        size_t violations = 0;

        while (std::getline(file, line)) {
            line_num++;
            for (const auto& rule : rules_) {
                if (rule.source_context == current_context && line.find(rule.forbidden_target) != std::string::npos) {
                    std::cout << "[FAIL] Фітнес-функція " << rule.adr_id 
                              << " порушена у " << filepath.string() << ":" << line_num << "\n"
                              << "       Вміст: " << line << "\n";
                    violations++;
                }
            }
        }

        return violations;
    }
};

int main() {
    std::cout << "=== Digital Homes C++20 Architectural Fitness Auditor ===\n";
    FitnessAuditEngine engine;

    const fs::path test_path = "src/telemetry/ingest.cpp";
    
    // Створення тестового файлу
    {
        std::ofstream out(test_path);
        out << "#include <iostream>\n";
        out << "void handle_ingest() {\n";
        out << "    // Порушення: прямий доступ до БД білінгу\n";
        out << "    auto db = connect_to_billing_db();\n";
        out << "}\n";
    }

    auto result = engine.audit_file(test_path, "telemetry");
    if (!result) {
        std::cerr << "[ERROR] " << result.error() << "\n";
        return 2;
    }

    if (*result > 0) {
        std::cout << "\n[BUILD BLOCKED] Виявлено " << *result << " зафіксованих порушень ADR!\n";
        return 1;
    }

    std::cout << "\n[SUCCESS] Усі фітнес-функції пройдено успішно.\n";
    return 0;
}
