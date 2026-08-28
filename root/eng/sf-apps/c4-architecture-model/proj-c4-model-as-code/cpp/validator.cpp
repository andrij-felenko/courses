// validator.cpp — Архітектурний валідатор на C++20
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

struct Relationship {
    std::string source;
    std::string destination;
    std::string description;
    std::string technology;
};

class ArchitectureLinter {
public:
    static bool validate(const std::string& json_path) {
        std::ifstream file(json_path);
        if (!file.is_open()) {
            std::cerr << "Помилка відкриття файлу моделі: " << json_path << "\n";
            return false;
        }

        json data;
        file >> data;

        std::vector<std::string> violations;

        for (const auto& item : data.value("relationships", json::array())) {
            Relationship rel{
                item.value("source", ""),
                item.value("destination", ""),
                item.value("description", ""),
                item.value("technology", "")
            };

            // Інваріант 1: Обов'язковість зазначення протоколу
            if (rel.technology.empty()) {
                violations.push_back("[RULE-1] Відсутній протокол у зв'язку: " + rel.source + " -> " + rel.destination);
            }

            // Інваріант 2: Заборона прямого доступу UI до бази даних
            if (rel.source.find("webSpa") != std::string::npos && rel.destination.find("Db") != std::string::npos) {
                violations.push_back("[RULE-2 CRITICAL] Прямий доступ із клієнта до БД: " + rel.source + " -> " + rel.destination);
            }

            // Інваріант 3: Single Writer для платіжної БД
            if (rel.destination.find("paymentDb") != std::string::npos && rel.source.find("paymentService") == std::string::npos) {
                violations.push_back("[RULE-3] Порушення Single Writer: сторонній сервіс " + rel.source + " викликає " + rel.destination);
            }
        }

        if (!violations.empty()) {
            std::cerr << "❌ Архітектурний лінтинг провалено (" << violations.size() << " дефектів):\n";
            for (const auto& v : violations) {
                std::cerr << "  - " << v << "\n";
            }
            return false;
        }

        std::cout << "✅ C++ валідатор: модель повністю відповідає архітектурним інваріантам.\n";
        return true;
    }
};

int main(int argc, char* argv[]) {
    std::string path = (argc > 1) ? argv[1] : "./architecture/output/workspace.json";
    return ArchitectureLinter::validate(path) ? 0 : 1;
}
