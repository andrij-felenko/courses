# ⚙️ Автоматизована перевірка архітектурних і організаційних меж

Цей приклад показує створення автоматизованої перевірки архітектурної придатності (англ. *Architecture Fitness Function*) для CI/CD-конвеєра, яка виявляє порушення меж між зв'язаними контекстами та перевіряє відповідність між власниками коду (`CODEOWNERS`) та залежностями у вихідному коді.

## Проблема: ерозія меж у процесі активної розробки

Навіть після успішного проведення Зворотного маневру Конвея та вирівнювання команд за Bounded Contexts, розробники під тиском жорстких термінів випуску фіч можуть припускатися архітектурних компромісів. Найпоширенішим виявом таких компромісів є створення прямих несанкціонованих імпортів між ізольованими модулями або внесення змін у чужі контексти без належного узгодження з командою-власником.

Якщо розробник з команди «Автоматизації» починає напряму імпортувати внутрішні класи з модуля «Керування пристроями» через відносний шлях файлової системи замість використання публічного контракту подій, межа контексту непомітно руйнується. Якщо такий імпорт потрапляє у продакшн, дві системи стають жорстко зв'язаними на рівні бінарного коду.

Щоб запобігти такій ерозії, у конвеєр автоматичного збирання та тестування (CI/CD) вбудовують спеціальний аналізатор. Він перевіряє граф залежностей вихідного коду на відповідність дозволеній мапі контекстів.

## Принцип роботи та архітектура аналізатора

Автоматизована перевірка меж спирається на три фундаментальні правила:

1. **Ізоляція за каталогами:** Кожен Bounded Context проживає у власному ізольованому каталозі репозиторію. Усі внутрішні деталі реалізації знаходяться у приватних підкаталогах, а назовні виставляється лише чітко визначений пакет публічних контрактів (`contracts` або `public`).
2. **Білий список дозволених залежностей:** Для кожного контексту формується суворий список дозволених імпортів (наприклад, контекст «Автоматизації» має право імпортувати лише публічні пакети `twin_contracts`, `identity_sdk` та `event_bus`). Будь-який інший імпорт вважається архітектурним дефектом.
3. **За заборона зворотних залежностей:** Контексти нижчого рівня (наприклад, `identity` або `hub_acl`) ніколи не можуть імпортувати класи з контекстів вищого рівня (`automations` або `billing`).

Нижче наведено практичну реалізацію аналізатора меж контекстів двома мовами: Python (для інструментарію автоматизації CI/CD) та C++20 (для високоефективних статичних аналізаторів великих систем).

:::tabs
```py
from dataclasses import dataclass
from pathlib import Path
import re
import sys

@dataclass(frozen=True)
class ContextRule:
    source_context: str
    allowed_imports: tuple[str, ...]

class ConwayBoundaryChecker:
    """Аналізатор меж контекстів та володіння кодом."""
    
    def __init__(self, rules: list[ContextRule]):
        self.rules = {r.source_context: set(r.allowed_imports) for r in rules}
        self.import_pattern = re.compile(r"^\s*(?:from|import)\s+([\w\.]+)", re.MULTILINE)

    def check_file(self, file_path: Path, current_context: str) -> list[str]:
        violations: list[str] = []
        allowed = self.rules.get(current_context, set())
        
        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as err:
            return [f"Не вдалося прочитати файл {file_path}: {err}"]

        for match in self.import_pattern.finditer(content):
            imported_module = match.group(1)
            imported_context = imported_module.split(".")[0]
            
            # Не перевіряємо внутрішні імпорти того самого контексту та системні модулі
            if imported_context == current_context or imported_context in ("sys", "os", "typing"):
                continue
                
            if imported_context not in allowed:
                violations.append(
                    f"Порушення межі Конвея у {file_path}: контекст '{current_context}' "
                    f"напряму імпортує '{imported_module}' з контексту '{imported_context}'. "
                    f"Дозволені залежності: {sorted(allowed)}"
                )
        return violations

def main() -> None:
    # Правила залежностей Digital Homes
    rules = [
        ContextRule("automations", ("twin_contracts", "identity_sdk", "event_bus")),
        ContextRule("device_control", ("hub_acl_contracts", "identity_sdk")),
        ContextRule("telemetry", ("event_bus", "identity_sdk")),
    ]
    
    checker = ConwayBoundaryChecker(rules)
    violations = checker.check_file(Path("automations/engine.py"), "automations")
    
    if violations:
        print("❌ ВИЯВЛЕНО ПОРУШЕННЯ МЕЖ КОНТЕКСТІВ:")
        for v in violations:
            print(f"  · {v}")
        sys.exit(1)
    else:
        print("✅ Усі межі контекстів відповідають мапі команд!")

if __name__ == "__main__":
    main()
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <filesystem>
#include <regex>
#include <expected>

namespace fs = std::filesystem;

struct ContextRule {
    std::string source_context;
    std::unordered_set<std::string> allowed_imports;
};

class ConwayBoundaryChecker {
public:
    explicit ConwayBoundaryChecker(std::vector<ContextRule> rules) {
        for (auto& r : rules) {
            rules_map_[std::move(r.source_context)] = std::move(r.allowed_imports);
        }
    }

    [[nodiscard]] std::expected<std::vector<std::string>, std::string> 
    check_file(const fs::path& file_path, std::string_view current_context) const {
        std::ifstream file(file_path);
        if (!file.is_open()) {
            return std::unexpected("Не вдалося відкрити файл: " + file_path.string());
        }

        std::vector<std::string> violations;
        auto it = rules_map_.find(std::string(current_context));
        const static std::unordered_set<std::string> empty_set;
        const auto& allowed = (it != rules_map_.end()) ? it->second : empty_set;

        std::string line;
        const std::regex include_regex(R"(^\s*#include\s+["<]([^"/>]+)/.*[">])");
        std::smatch match;

        while (std::getline(file, line)) {
            if (std::regex_search(line, match, include_regex)) {
                std::string imported_context = match[1].str();
                
                if (imported_context == current_context || imported_context == "iostream" || imported_context == "vector") {
                    continue;
                }

                if (!allowed.contains(imported_context)) {
                    violations.push_back(
                        "Порушення межі Конвея у " + file_path.string() + 
                        ": контекст '" + std::string(current_context) + "' включає заголовок з '" + 
                        imported_context + "', що не є в списку дозволених."
                    );
                }
            }
        }
        return violations;
    }

private:
    std::unordered_map<std::string, std::unordered_set<std::string>> rules_map_;
};

int main() {
    std::vector<ContextRule> rules = {
        {"automations", {"twin_contracts", "identity_sdk", "event_bus"}},
        {"device_control", {"hub_acl_contracts", "identity_sdk"}},
    };

    ConwayBoundaryChecker checker(rules);
    auto result = checker.check_file("automations/engine.cpp", "automations");

    if (!result) {
        std::cerr << "Помилка аналізу: " << result.error() << '\n';
        return 1;
    }

    if (!result->empty()) {
        std::cout << "❌ ВИЯВЛЕНО ПОРУШЕННЯ МЕЖ КОНТЕКСТІВ:\n";
        for (const auto& v : *result) {
            std::cout << "  · " << v << '\n';
        }
        return 1;
    }

    std::cout << "✅ Межі контекстів C++ код бази чисті!\n";
    return 0;
}
```
:::

## Детальний розбір механізму перевірки

Аналіз вихідного коду виконується в декілька етапів перед запуском основних модульних чи інтеграційних тестів у CI/CD-конвеєрі:

1. **Сканування файлової системи та виявлення контексту:** Аналізатор рекурсивно обходить усі каталоги вихідного коду проекту. Назва контексту визначається за першим підкаталогом від кореня вихідного коду (наприклад, `/src/automations/...` належить до контексту `automations`).
2. **Парсинг операторів імпорту та включення:** У кожному файлі аналізатор шукає директиви `import` / `from ... import` (для Python/TypeScript) або `#include` (для C++). У випадку виявлення псевдонімів імпортів (аліасів) або відносних шляхів на зразок `../../device_control/models` аналізатор нормалізує шлях до канонічного вигляду.
3. **Порівняння з білим списком дозволів:** Знайдений модуль порівнюється з конфігурацією дозволених контекстів-залежностей. Внутрішні імпорти того самого контексту та системні бібліотеки мови програмування (стандартна бібліотека C++ або модулі `sys`/`os` у Python) автоматично ігноруються.
4. **Формування деталізованого звіту про дефекти:** При виявленні несанкціонованого імпорту аналізатор повертає ненульовий код виходу (`exit code 1`), друкує точний рядок коду, шлях до файлу та перелік дозволених залежностей. Це автоматично блокує збірку в CI/CD.

## Крайові випадки та виклики статичного аналізу

При впровадженні перевірок меж Конвея в реальних проектних кодових базах виникають складні крайові випадки, які вимагають додаткових архітектурних рішень:

- **Динамічні імпорти та відображення (Reflection):** У мовах на зразок Python або JavaScript розробники можуть використовувати `importlib.import_module("device_control.models")` або динамічний `require()`. Простий аналіз на основі регулярних виразів не бачить таких викликів. Для їх перехоплення статичний аналіз доповнюють аналізом абстрактного синтаксичного дерева (AST) та інструментами динамічного трасування у тесах.
- **Приховані залежності через бази даних:** Двоє контекстів можуть не мати жодного спільного імпорту у коді, але напряму читати й писати в одну й ту саму таблицю `devices` у PostgreSQL. Статичний аналізатор коду це пропустить. Для блокування цієї пастки застосовують розділення прав доступу на рівні СУБД (окремі схеми та окремі користувачі баз даних для кожного контексту).
- **Інверсія залежностей (DIP) та спільні інтерфейси:** Для уникнення прямих залежностей контекст `automations` може визначати інтерфейс `IDeviceStateProvider`. Реалізацію цього інтерфейсу надає модуль `device_control` під час старт-апу через Dependency Injection. Статичний аналізатор має дозволяти імпорт пакетів з абстрактними інтерфейсами, але забороняти імпорт конкретних реалізацій.

## Інтеграція з CODEOWNERS та процес розробки

Перевірка меж у коді дає максимальний ефект при поєднанні з межами володіння у Git-репозиторії через файл `.github/CODEOWNERS`:

```text
# Файл CODEOWNERS проекту Digital Homes
/src/contexts/hub_acl/          @digital-homes/edge-team
/src/contexts/device_control/   @digital-homes/core-smart-home-team
/src/contexts/twin/             @digital-homes/core-smart-home-team
/src/contexts/automations/      @digital-homes/automation-engine-team
/src/contexts/telemetry/        @digital-homes/media-telemetry-team
/src/contexts/video/            @digital-homes/media-telemetry-team
/src/contexts/identity/         @digital-homes/platform-team
```

Інтеграція в конвеєр автоматичного збирання GitHub Actions налаштовується через YAML-конфігурацію:

```yaml
name: Arch Boundary Check
on: [push, pull_request]

jobs:
  conway-governance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Run Conway Boundary Checker
        run: python scripts/ci/check_conway_boundaries.py
```

Коли розробник із команди «Автоматизації» створює Pull Request, який зачіпає файли в каталозі `/src/contexts/device_control/`, платформа розробки (GitHub чи GitLab) автоматично додає інженерів з `@digital-homes/core-smart-home-team` як обов'язкових рев'юерів. Без їхнього схвалення мердж коду стає неможливим.

Завдяки комбінації статичного аналізатора залежностей у CI/CD та файлу `CODEOWNERS` організація отримує подвійний контур захисту:
- **Технічний контур:** Аналізатор не дає створити заборонені імпорти між модулями на рівні вихідного коду.
- **Соціальний контур:** `CODEOWNERS` блокує несанкціоновані зміни в чужому контексті на рівні процесів розробки.

Це гарантує збереження автономії потокових команд та запобігає зворотній деградації системи у моноліт.
