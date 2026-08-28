#include <iostream>
#include <string>
#include <vector>
#include <string_view>
#include <optional>
#include <variant>
#include <expected>
#include <algorithm>
#include <span>

namespace arch {

// Результат кваліфікації макро-патерну організації системи
enum class MacroPattern {
    ModularMonolith,       // Модульний моноліт (Дефолтний збалансований стан)
    Microservices,         // Розподілені автономні сервіси (Database-per-Service)
    Serverless,            // Подійно-орієнтовані хмарні функції (FaaS)
    DistributedMonolithRisk // АНТИПАТЕРН: Розподілений моноліт (Критичний ризик)
};

// Вхідні виміряні метрики інженерної системи та організації
struct SystemMetrics {
    std::size_t teamCount{1};                 // Кількість автономних команд
    double domainBoundaryMaturity{0.2};        // Зрілість меж домену [0.0 ... 1.0]
    double p99LatencyBudgetMs{100.0};          // Бюджет затримки відповіді (ms)
    bool independentScaleDriver{false};        // Наявність асиметричного масштабу
    bool sharedDatabaseCoupling{false};        // Зчеплення через спільну БД
    bool highEventDrivenLoad{false};           // Подійна природа трафіку
};

// Деталізований результат оцінки з балами та аргументацією
struct EvaluationResult {
    MacroPattern recommendedPattern;
    double modularMonolithScore{0.0};
    double microservicesScore{0.0};
    double serverlessScore{0.0};
    std::vector<std::string> warningFlags;
    std::string primaryRationale;

    [[nodiscard]] bool hasCriticalWarnings() const noexcept {
        return !warningFlags.empty();
    }
};

class MacroPatternEvaluator {
public:
    [[nodiscard]] static EvaluationResult evaluate(const SystemMetrics& metrics) noexcept {
        EvaluationResult res{};

        // -------------------------------------------------------------------
        // Крок 1: Детекція пастки Розподіленого Моноліта
        // Якщо системи порізані по мережі, але ділять спільну СУБД — це антипатерн.
        // -------------------------------------------------------------------
        if (metrics.sharedDatabaseCoupling && metrics.teamCount > 1) {
            res.warningFlags.push_back(
                "КРИТИЧНА ПОМИЛКА: Виявлено спільну базу даних поверх мережевих сервісів! "
                "Це утворює Розподілений Моноліт з максимальним операційним ризиком."
            );
        }

        // -------------------------------------------------------------------
        // Крок 2: Обчислення інтегрального бала для Модульного Моноліта (Дефолт)
        // Моноліт отримує високий стартовий бал через відсутність мережевого податку.
        // -------------------------------------------------------------------
        res.modularMonolithScore = 80.0; // Базовий поріг дефолту

        if (metrics.teamCount <= 3) {
            res.modularMonolithScore += 15.0; // Мала команда виграє від єдиного процесу
        }
        if (metrics.domainBoundaryMaturity < 0.6) {
            res.modularMonolithScore += 25.0; // Плаваючі межі вимагають двобічних дверей
        }
        if (metrics.p99LatencyBudgetMs < 20.0) {
            res.modularMonolithScore += 20.0; // Жорстка затримка вимагає викликів у пам'яті
        }
        if (!metrics.independentScaleDriver) {
            res.modularMonolithScore += 10.0; // Відсутність окремого профілю навантаження
        }

        // -------------------------------------------------------------------
        // Крок 3: Обчислення бала для Мікросервісів
        // Сервіси повинні заробляти бали через виміряні драйвери.
        // -------------------------------------------------------------------
        res.microservicesScore = 20.0; // Низький стартовий бал через Microservice Premium

        if (metrics.teamCount >= 4) {
            res.microservicesScore += 30.0; // Закон Конвея: ізоляція команд
        }
        if (metrics.domainBoundaryMaturity >= 0.7) {
            res.microservicesScore += 25.0; // Межі домену дозріли для опублікування
        }
        if (metrics.independentScaleDriver) {
            res.microservicesScore += 35.0; // Асиметричний масштаб купує мережу
        }
        if (metrics.p99LatencyBudgetMs < 10.0) {
            res.microservicesScore -= 40.0; // Податок мережі не вкладається у бюджет
        }

        // -------------------------------------------------------------------
        // Крок 4: Обчислення бала для Серверлесу (FaaS)
        // -------------------------------------------------------------------
        res.serverlessScore = 15.0;

        if (metrics.highEventDrivenLoad) {
            res.serverlessScore += 45.0; // Подійний трафік ідеально лягає на FaaS
        }
        if (metrics.teamCount <= 2 && metrics.domainBoundaryMaturity >= 0.5) {
            res.serverlessScore += 20.0; // Мала команда без бажання адмініструвати K8s
        }
        if (metrics.p99LatencyBudgetMs < 50.0) {
            res.serverlessScore -= 30.0; // Cold starts шкодять суворому p99
        }

        // -------------------------------------------------------------------
        // Крок 5: Формування остаточного висновку та аргументації
        // -------------------------------------------------------------------
        if (metrics.sharedDatabaseCoupling && !metrics.independentScaleDriver && metrics.domainBoundaryMaturity < 0.5) {
            res.recommendedPattern = MacroPattern::DistributedMonolithRisk;
            res.primaryRationale = 
                "ПРИСУД: Зійдіть з мережевих меж та консолідуйте код назад у Модульний Моноліт. "
                "Поточна конфігурація є розподіленим монолітом без жодних переваг автономії.";
        } else if (res.microservicesScore > res.modularMonolithScore && res.microservicesScore > res.serverlessScore) {
            res.recommendedPattern = MacroPattern::Microservices;
            res.primaryRationale = 
                "ПРИСУД: Виділення мікросервісів обґрунтовано високою зрілістю меж, "
                "великою кількістю команд та асиметричним профілем масштабування.";
        } else if (res.serverlessScore > res.modularMonolithScore && res.serverlessScore > res.microservicesScore) {
            res.recommendedPattern = MacroPattern::Serverless;
            res.primaryRationale = 
                "ПРИСУД: Серверлесс-архітектура рекомендована через виражену подійну природу "
                "навантаження та можливість повністю усунути інфраструктурний оверхед.";
        } else {
            res.recommendedPattern = MacroPattern::ModularMonolith;
            res.primaryRationale = 
                "ПРИСУД: Модульний моноліт є оптимальним архітектурним дефолтом. "
                "Він забезпечує мінімальний мережевий податок, зберігає двобічні двері "
                "для рефакторингу та усуває Microservice Premium.";
        }

        return res;
    }
};

} // namespace arch

int main() {
    // Демонстрація оцінки проєкту Digital Homes на ранній стадії
    arch::SystemMetrics dhEarlyMetrics{
        .teamCount = 2,
        .domainBoundaryMaturity = 0.35,
        .p99LatencyBudgetMs = 15.0,
        .independentScaleDriver = false,
        .sharedDatabaseCoupling = false,
        .highEventDrivenLoad = false
    };

    auto result = arch::MacroPatternEvaluator::evaluate(dhEarlyMetrics);

    std::cout << "==================================================\n";
    std::cout << "    Аналітичний Оцінювач Макро-Патернів Системи    \n";
    std::cout << "==================================================\n";
    std::cout << "Рекомендований макро-патерн: ";
    switch (result.recommendedPattern) {
        case arch::MacroPattern::ModularMonolith:
            std::cout << "МОДУЛЬНИЙ МОНОЛІТ (Дефолт)\n"; break;
        case arch::MacroPattern::Microservices:
            std::cout << "МІКРОСЕРВІСИ\n"; break;
        case arch::MacroPattern::Serverless:
            std::cout << "СЕРВЕРЛЕСС (FaaS)\n"; break;
        case arch::MacroPattern::DistributedMonolithRisk:
            std::cout << "УВАГА: РОЗПОДІЛЕНИЙ МОНОЛІТ!\n"; break;
    }
    std::cout << "\nАргументація:\n  " << result.primaryRationale << "\n\n";
    std::cout << "Оціночні бали кандидатів:\n";
    std::cout << "  • Модульний моноліт: " << result.modularMonolithScore << " балів\n";
    std::cout << "  • Мікросервіси:     " << result.microservicesScore << " балів\n";
    std::cout << "  • Серверлесс (FaaS): " << result.serverlessScore << " балів\n";

    if (result.hasCriticalWarnings()) {
        std::cout << "\nЗастереження перевірки:\n";
        for (const auto& warn : result.warningFlags) {
            std::cout << "  [!] " << warn << "\n";
        }
    }
    std::cout << "==================================================\n";

    return 0;
}
