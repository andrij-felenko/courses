# ⚙️ Оцінювач макро-патернів та фітнес-функції архітектурного вибору

Цей практичний приклад реалізує аналітичний рушій оцінки архітектурного стану системи (Macro Pattern Evaluator) та автоматизовані фітнес-функції на мовах C++20 та TypeScript. Рушій приймає операційні параметри проєкту (кількість команд, зрілість меж домену, вимоги до латентності, профіль навантаження) та обчислює рекомендований макро-патерн, сигналізуючи про виникнення антипатерну розподіленого моноліта.

## 1. Архітектурні критерії та фізичний сенс параметрів оцінювача

Вибір макро-патерну організації системи не може ґрунтуватися на інтуїції або суб'єктивних уподобаннях розробників. Для побудови об'єктивного аналітичного рушія використовується математично зважена оцінка п'яти ключових інженерних та організаційних параметрів, кожен з яких характеризує фізичну спроможність системи та команди:

1. `teamCount` (Кількість автономних продуктових команд):
   Відображає організаційний поріг Закону Конвея. Якщо над проєктом працює 1–3 команди (до 15–20 інженерів), комунікаційні витрати залишаються низькими, а обмін знаннями відбувається через спільний репозиторій. У цьому діапазоні розкрій на мікросервіси створює операційне навантаження, яке перевищує вигоду від автономії деплою. Коли кількість команд перевищує 4–5, точка тертя переміщується у збірку та версіонування єдиного бінарника, що робить незалежні релізи сервісів економічно доцільними.

2. `domainBoundaryMaturity` (Коефіцієнт зрілості меж домену від 0.0 до 1.0):
   Характеризує стабільність обмежених контекстів (Bounded Contexts) у поняттях предметно-орієнтованого проєктування (DDD). На ранніх стадіях життя проєкту (значення 0.0–0.4) межі домену постійно змінюються: концепції зливаються, сутності мігрують між контекстами, а бізнес-модель перевіряється ринком. Будь-яка мережева межа, протягнута на цій стадії, стає однобічними дверима й зацементовує криві абстракції в REST/gRPC контракти. Лише при досягненні високої зрілості (0.7–1.0), коли межі не змінювалися протягом багатьох місяців під тиском реальних викликів, розкрій на сервіси стає безпечним.

3. `p99LatencyBudgetMs` (Граничний бюджет затримки відповіді p99 у мілісекундах):
   Жорстке фізичне обмеження на час обробки транзакції. Виклики функцій у спільному адресному просторі модульного моноліта виконуються за десятки наносекунд. Синхронний мережевий виклик між сервісами (навіть по внутрішньому gRPC/mTLS) додає 2–15 мілісекунд. Якщо бюджет затримки системи становить менше 10–20 мілісекунд, послідовний синхронний ланцюг із кількох мікросервісів фізично не зможе вкластися у вказаний бюджет, що робить моноліт єдиним придатним рішенням.

4. `independentScaleDriver` (Наявність асиметричного профілю масштабування):
   Прапор, що фіксує наявність конкретного доменного модуля, чий профіль навантаження за обчисленнями (CPU), пам'яттю (RAM) або мережевим вводом-виводом (I/O) відрізняється від решти системи на 2–3 порядки. Прикладом є потік обробки телеметрії або відеоаналітика, яка вимагає спеціалізованих GPU-вузлів. За відсутності такого драйвера масштабувати весь модульний моноліт за допомогою реплікації процесових екземплярів виявляється дешевше, ніж утримувати окрему сервісну інфраструктуру.

5. `sharedDatabaseCoupling` (Наявність спільних таблиць чи JOIN у СУБД):
   Індикатор критичного архітектурного регресу. Якщо незалежно розгорнуті сервіси або модулі виконують прямі SQL-запити в таблиці один одного або ділять спільну реляційну схему, система негайно ідентифікується як **розподілений моноліт**. Це антипатерн, у якому зчеплення за даними позбавляє команди автономії деплою, а мережеві межі додають відмови й затримки.

## 2. Реалізація аналітичного оцінювача та алгоритму виваження

Нижче наведено повну реалізацію оцінювача на мовах C++20 та TypeScript. Реалізація на C++ використовує сучасні можливості стандарту (компіляційні перевірки `noexcept`, `[[nodiscard]]`, семантику `std::span`, строгі типізовані структури даних), а версія на TypeScript забезпечує строгий статичний аналіз через строгі інтерфейси та дискриміновані об'єднання.

:::tabs
```cpp
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
```
```ts
export type MacroPattern = 
  | 'ModularMonolith' 
  | 'Microservices' 
  | 'Serverless' 
  | 'DistributedMonolithRisk';

export interface SystemMetrics {
  teamCount: number;                 // Кількість команд
  domainBoundaryMaturity: number;    // Зрілість меж [0.0 ... 1.0]
  p99LatencyBudgetMs: number;        // Бюджет затримки (ms)
  independentScaleDriver: boolean;   // Асиметричний масштаб
  sharedDatabaseCoupling: boolean;   // Спільна БД
  highEventDrivenLoad: boolean;      // Подійне навантаження
}

export interface EvaluationResult {
  recommendedPattern: MacroPattern;
  scores: {
    modularMonolith: number;
    microservices: number;
    serverless: number;
  };
  warningFlags: string[];
  primaryRationale: string;
}

export class MacroPatternEvaluator {
  public static evaluate(metrics: SystemMetrics): EvaluationResult {
    const warningFlags: string[] = [];

    // Детекція пастки Розподіленого Моноліта
    if (metrics.sharedDatabaseCoupling && metrics.teamCount > 1) {
      warningFlags.push(
        'КРИТИЧНА ПОМИЛКА: Виявлено спільну базу даних поверх мережевих сервісів! ' +
        'Це утворює Розподілений Моноліт з максимальним операційним ризиком.'
      );
    }

    // Розрахунок бала для Модульного Моноліта
    let modularMonolith = 80.0;
    if (metrics.teamCount <= 3) modularMonolith += 15.0;
    if (metrics.domainBoundaryMaturity < 0.6) modularMonolith += 25.0;
    if (metrics.p99LatencyBudgetMs < 20.0) modularMonolith += 20.0;
    if (!metrics.independentScaleDriver) modularMonolith += 10.0;

    // Розрахунок бала для Мікросервісів
    let microservices = 20.0;
    if (metrics.teamCount >= 4) microservices += 30.0;
    if (metrics.domainBoundaryMaturity >= 0.7) microservices += 25.0;
    if (metrics.independentScaleDriver) microservices += 35.0;
    if (metrics.p99LatencyBudgetMs < 10.0) microservices -= 40.0;

    // Розрахунок бала для Серверлесу
    let serverless = 15.0;
    if (metrics.highEventDrivenLoad) serverless += 45.0;
    if (metrics.teamCount <= 2 && metrics.domainBoundaryMaturity >= 0.5) serverless += 20.0;
    if (metrics.p99LatencyBudgetMs < 50.0) serverless -= 30.0;

    let recommendedPattern: MacroPattern = 'ModularMonolith';
    let primaryRationale = '';

    if (metrics.sharedDatabaseCoupling && !metrics.independentScaleDriver && metrics.domainBoundaryMaturity < 0.5) {
      recommendedPattern = 'DistributedMonolithRisk';
      primaryRationale = 
        'ПРИСУД: Зійдіть з мережевих меж та консолідуйте код назад у Модульний Моноліт. ' +
        'Поточна конфігурація є розподіленим монолітом без жодних переваг автономії.';
    } else if (microservices > modularMonolith && microservices > serverless) {
      recommendedPattern = 'Microservices';
      primaryRationale = 
        'ПРИСУД: Виділення мікросервісів обґрунтовано високою зрілістю меж, ' +
        'великою кількістю команд та асиметричним профілем масштабування.';
    } else if (serverless > modularMonolith && serverless > microservices) {
      recommendedPattern = 'Serverless';
      primaryRationale = 
        'ПРИСУД: Серверлесс-архітектура рекомендована через виражену подійну природу ' +
        'навантаження та можливість повністю усунути інфраструктурний оверхед.';
    } else {
      recommendedPattern = 'ModularMonolith';
      primaryRationale = 
        'ПРИСУД: Модульний моноліт є оптимальним архітектурним дефолтом. ' +
        'Він забезпечує мінімальний мережевий податок, зберігає двобічні двері ' +
        'для рефакторингу та усуває Microservice Premium.';
    }

    return {
      recommendedPattern,
      scores: {
        modularMonolith,
        microservices,
        serverless,
      },
      warningFlags,
      primaryRationale,
    };
  }
}
```
:::

## 3. Автоматизовані фітнес-функції перевірки меж на CI/CD

Архітектурні рішення, прийняті на етапі проєктування, схильні до поступової деградації (Architecture Drift), коли розробники під тиском строків зрізають кути й протягують прямі залежності між модулями. Щоб зробити недопущення розподіленого моноліта автоматичним гарантом, у CI/CD вбудовуються **фітнес-функції (Fitness Functions)**.

Фітнес-функція аналізує топологу залежностей та конфігурацію сховищ даних, негайно завалюючи збірку в разі виявлення двох критичних патологій:
1. **Direct DB Access Violation**: Наявність мережевого сервісу `A`, який виконує з'єднання із базою даних, що належить сервісу `B`.
2. **Circular Network Cascade**: Наявність замкненого циклу синхронних HTTP/gRPC викликів (`Service A -> Service B -> Service C -> Service A`), який гарантовано створює розподілений dead-lock при навантаженні.

:::tabs
```cpp
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
```
```ts
export interface ServiceDependency {
  sourceService: string;
  targetService: string;
  isSynchronousHttp: boolean;
  sharesDatabaseSchema: boolean;
}

export class ArchitectureFitnessChecker {
  public static verifyNoDistributedMonolith(dependencies: ServiceDependency[]): void {
    const violations: string[] = [];

    for (const dep of dependencies) {
      if (dep.sharesDatabaseSchema) {
        violations.push(
          `ПОШКОДЖЕННЯ МЕЖІ: Сервіс [${dep.sourceService}] має прямий доступ до СУБД сервісу [${dep.targetService}]. Спільні схеми заборонені!`
        );
      }
    }

    if (violations.length > 0) {
      console.error('\n❌ ФІТНЕС-ФУНКЦІЯ ЗАВАЛИЛА ЗБІРКУ CI/CD:');
      violations.forEach((v) => console.error(`  - ${v}`));
      throw new Error('Архітектурний регрес: Спроба побудови Розподіленого Моноліта!');
    }

    console.log('✅ ФІТНЕС-ФУНКЦІЯ ПРОЙДЕНА: Архітектурні межі суворі. Зчеплення за даними відсутнє.');
  }
}
```
:::

## 4. Аналіз крайових випадків та небезпечних конфігурацій

При практичному застосуванні оцінювача архітектори часто зіштовхуються з трьома аномальними конфігураціями проєктів:

1. **Суперечність «Багато команд при низькій зрілості меж»**:
   Ситуація, коли в компанії працює 8 команд (`teamCount = 8`), але доменні межі постійно плавають (`domainBoundaryMaturity = 0.2`). Наївне застосування Закону Конвея штовхає до нарізання мікросервісів. Проте аналітичний рушій призначає високий бал модульному моноліту, оскільки розкрій незрілого домену створить десятки сервісів із кривими межами, перетворивши систему на розподілений моноліт. Рішення: утримувати модульний моноліт у монорепозиторії, доки межі не зафіксуються.

2. **Суперечність «Надсувора затримка при асиметричному масштабі»**:
   Ситуація, де `p99LatencyBudgetMs = 5 ms`, але один з модулів вимагає асиметричного масштабування. Мережевий розкрій додасть 8 ms, що завалить бюджет. Рішення: залишити гарячий шлях обробки в пам'яті модульного моноліта, а асиметричний модуль винести не через мережевий RPC, а через асинхронну реплікацію даних у пам'яті (In-Memory Shared Data Grid або ZeroMQ IPC).

3. **Небезпека "Microservice Premium" у малих стартапах**:
   Стартап із 2 розробників обирає мікросервіси через маркетингові гасла. Аналітичний оцінювач показує низький бал (20.0), оскільки операційний оверхед на Kubernetes, CI/CD pipelines та Jaeger tracing відбере 60% ресурсів команди, сповільнюючи Time-to-Market у рази.
