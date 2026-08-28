#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>
#include <unordered_set>

namespace arch::fitness {

struct ServiceDependency {
    std::string sourceService;
    std::string targetService;
    bool isSynchronousHttp{false};
    bool sharesDatabaseSchema{false};
};

class ArchitectureFitnessChecker {
public:
    static void verifyNoDistributedMonolith(const std::vector<ServiceDependency>& dependencies) {
        std::vector<std::string> violations;

        for (const auto& dep : dependencies) {
            // Перевірка Патології 1: Спільна база даних
            if (dep.sharesDatabaseSchema) {
                violations.push_back(
                    "ПОШКОДЖЕННЯ МЕЖІ: Сервіс [" + dep.sourceService + 
                    "] має прямого доступу до СУБД сервісу [" + dep.targetService + 
                    "]. Спільні реляційні схеми заборонені!"
                );
            }
        }

        if (!violations.empty()) {
            std::cout << "\n❌ ФІТНЕС-ФУНКЦІЯ ЗАВАЛИЛА ЗБІРКУ CI/CD:\n";
            for (const auto& v : violations) {
                std::cout << "  - " << v << "\n";
            }
            throw std::runtime_error("Архітектурний регрес: Спроба побудови Розподіленого Моноліта!");
        }

        std::cout << "✅ ФІТНЕС-ФУНКЦІЯ ПРОЙДЕНА: Архітектурні межі суворі. Зчеплення за даними відсутнє.\n";
    }
};

} // namespace arch::fitness

int main() {
    // Приклад конфігурації залежностей для CI-перевірки
    std::vector<arch::fitness::ServiceDependency> pipelineDeps = {
        {"OrdersService", "PaymentService", true, false},
        {"NotificationService", "UsersService", false, false},
        {"BillingService", "UsersService", true, true} // Критичне порушення!
    };

    try {
        arch::fitness::ArchitectureFitnessChecker::verifyNoDistributedMonolith(pipelineDeps);
    } catch (const std::exception& e) {
        std::cout << "\nРеакція CI-сервера: " << e.what() << "\n";
        return 1; // Код помилки для зупинки CI пайплайну
    }

    return 0;
}
