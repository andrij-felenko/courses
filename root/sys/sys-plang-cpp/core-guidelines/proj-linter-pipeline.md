# ⚙️ Налаштування автоматичного аудиту коду через Clang-Tidy та CMake

Впровадження C++ Core Guidelines у щоденну практику інженерної команди неможливо реалізувати винятково усними домовленостями або ручними перевірками під час рецензування коду (code review). Людська увага швидко втомлюється, а суб'єктивне трактування стилістичних нюансів створює постійні конфлікти та призводить до накопичення прихованих дефектів. Єдиний спосіб забезпечити безкомпромісну безпеку пам'яті та гігієну типів — перевести вимоги Core Guidelines у статус формальних автоматизованих перевірок, що блокують збірку на етапі локальної компіляції та в конвеєрах неперервної інтеграції (CI/CD).

Основним інструментом для механічного аудиту за правилами Core Guidelines у відкритому кросплатформному середовищі виступає статичний аналізатор **`clang-tidy`** з інтегрованим набором чекерів модуля **`cppcoreguidelines-*`**.

---

## 1. Архітектура та налаштування конфігурації `.clang-tidy`

Інструмент `clang-tidy` працює на базі синтаксичного дерева AST (Abstract Syntax Tree) компілятора Clang. Його поведінка конфігурується через ієрархічний файл налаштувань `.clang-tidy` у форматі YAML, який розміщується в корені репозиторію проєкту.

Під час аналізу кожного файлу сирцевого коду утиліта рекурсивно підіймається вгору деревом каталогів у пошуках найближчого конфігураційного файлу. Це дозволяє задавати загальні глобальні правила для всього репозиторію та водночас перевизначати їх для окремих специфічних підкаталогів (наприклад, для папки низькорівневих системних драйверів або тестів).

Нижче наведено зразок суворої виробничої конфігурації `.clang-tidy`, що вмикає комплексний аудит Core Guidelines разом із супутніми модулями пошуку багів і проблем продуктивності:

```yaml
---
# Забороняємо підійматися вище кореневої директорії репозиторію
RootPriority: true

# Регулярний вираз для фільтрації заголовків:
# аналізуємо лише файли проєкту, ігноруючи системні бібліотеки та сторонній код
HeaderFilterRegex: '^(src|include|lib)/.*'

# Перелік активних перевірок
Checks: >
  -*,
  cppcoreguidelines-*,
  -cppcoreguidelines-avoid-magic-numbers,
  -cppcoreguidelines-macro-usage,
  bugprone-*,
  performance-*,
  readability-redundant-smartptr-get,
  modernize-use-override,
  modernize-use-using,
  modernize-make-unique,
  modernize-make-shared

# Перетворюємо всі попередження Core Guidelines на фатальні помилки
WarningsAsErrors: 'cppcoreguidelines-*,bugprone-*'

# Детальне налаштування поведінки окремих перевірок
CheckOptions:
  cppcoreguidelines-special-member-functions.AllowSoleDefaultDtor: true
  cppcoreguidelines-special-member-functions.AllowMissingMoveFunctions: false
  cppcoreguidelines-init-variables.IncludeStyle: llvm
  cppcoreguidelines-owning-memory.LegacyResourceProducers: '::fopen;::malloc;::CreateFileA;::CreateFileW'
  cppcoreguidelines-owning-memory.LegacyResourceConsumers: '::fclose;::free;::CloseHandle'
  cppcoreguidelines-narrowing-conversions.PedanticMode: true
  cppcoreguidelines-prefer-member-initializer.UseAssignment: false

# Інтеграція зі стилем форматування коду
FormatStyle: file
...
```

---

## 2. Анатомія ключових перевірок модуля `cppcoreguidelines-*`

Модуль `cppcoreguidelines-*` містить понад тридцять спеціалізованих правил. Їх можна згрупувати за чотирма основними напрямами надійності:

### А. Володіння ресурсами та пам'яттю
- **`cppcoreguidelines-owning-memory`**: Реалізує фундаментальні правила R.3 та I.11. Перевірка забороняє присвоєння адреси, повернутої оператором `new` або функцією `malloc()`, звичайному сирому вказівнику `T*`. Пам'ять зобов'язана негайно захоплюватися об'єктом із семантикою володіння — `std::unique_ptr<T>`, `std::shared_ptr<T>` або `gsl::owner<T*>`. Крім того, чекер перехоплює будь-які спроби виклику операторів `delete` чи `delete[]` над сирими неволодіючими вказівниками.
- **`cppcoreguidelines-no-malloc`**: Відповідає правилу R.10. Повністю забороняє використання архаїчних функцій розподілу пам'яті мови C (`malloc`, `calloc`, `realloc`, `free`), вимагаючи використання стандартних типів, що керують пам'яттю автоматично за принципом RAII.
- **`cppcoreguidelines-rvalue-reference-param-not-moved`**: Відповідає правилу F.18. Ловить параметри функцій, передані за rvalue-посиланням (`T&&`), над якими не було викликано `std::move()` або `std::forward()`. Якщо ресурс не переміщується, передача за rvalue-посиланням є оманливою і має бути замінена на константне посилання.

### Б. Безпека меж (Bounds Safety)
- **`cppcoreguidelines-avoid-c-arrays`**: Реалізує правило Bounds.1. Забороняє створення C-масивів фіксованого розміру `T arr[N]` у ролі локальних змінних, членів класів або аргументів функцій. Натомість вимагається використання `std::array<T, N>` для стек-буферів або `std::vector<T>` для динамічних структур.
- **`cppcoreguidelines-pro-bounds-pointer-arithmetic`**: Забороняє зміщення сирих вказівників за допомогою арифметичних операторів `ptr++`, `ptr + offset` або індексації `ptr[i]`. Операції з послідовностями повинні виконуватися через ітератори або безпечний перегляд `std::span<T>`.
- **`cppcoreguidelines-pro-bounds-array-to-pointer-decay`**: Ловить неявне перетворення (decay) масиву у вказівник при передачі аргументів, що призводить до втрати інформації про довжину буфера.
- **`cppcoreguidelines-pro-bounds-constant-array-index`**: Перевіряє операції статичного індексування масивів, сигналізуючи про вихід за межі діапазону ще на етапі компіляції.

### В. Типобезпека (Type Safety)
- **`cppcoreguidelines-pro-type-vararg`**: Відповідає правилу Type.1. Забороняє виклики C-варіативних функцій (`printf`, `sprintf`, `scanf`, використання макросів `<cstdarg>`). Такі функції не здійснюють перевірку типів аргументів під час компіляції, що є частим джерелом експлойтів псування пам'яті (format string vulnerabilities).
- **`cppcoreguidelines-pro-type-cstyle-cast` та `cppcoreguidelines-pro-type-reinterpret-cast`**: Забороняють використання небезпечного C-приведення `(Type)val` та грубого перетворення бінарного представлення `reinterpret_cast`, дозволяючи лише безпечні перетворення `static_cast` або поліморфні `dynamic_cast`.
- **`cppcoreguidelines-pro-type-union-access`**: Забороняє читання неактивних полів C-об'єднань `union`, які використовуються для небезпечного реінтерпретування пам'яті (type punning). Вимагає переходу на безпечний шаблон `std::variant`.
- **`cppcoreguidelines-pro-type-static-cast-downcast`**: Вимагає використання `dynamic_cast` замість `static_cast` при низхідному приведенні вказівників у поліморфних ієрархіях класів.

### Г. Ініціалізація, класи та життєвий цикл
- **`cppcoreguidelines-init-variables`**: Відповідає правилу ES.20. Забороняє оголошення локальних змінних без негайної ініціалізації значенням. Унеможливлює помилки читання сміття зі стека.
- **`cppcoreguidelines-prefer-member-initializer`**: Відповідає правилу C.49. Вимагає ініціалізувати поля класу у списку ініціалізації конструктора або безпосередньо за місцем оголошення (Default Member Initialization), а не присвоювати значення у тілі конструктора.
- **`cppcoreguidelines-special-member-functions`**: Відповідає правилам C.21 та C.67 (Правило п'яти / Правило нуля). Якщо клас явно оголошує або видаляє хоча б одну спеціальну функцію-член (деструктор, конструктор копіювання, оператор присвоєння копіюванням, конструктор переміщення або оператор присвоєння переміщенням), розробник зобов'язаний явно визначити або видалити всі решту чотири функції.
- **`cppcoreguidelines-narrowing-conversions`**: Ловить неявні приведення чисел, які можуть змінити значення (наприклад, перетворення `double` в `int` або від'ємного `int` у беззнаковий `unsigned long`).
- **`cppcoreguidelines-interfaces-global-init`**: Відповідає правилу I.22. Ловить оголошення глобальних об'єктів з нетривіальними конструкторами, які залежать від інших одиниць трансляції, запобігаючи аваріям фіаско порядку ініціалізації (static initialization order fiasco).

---

## 3. Практичний сценарій: Виявлення дефектів та рефакторинг

Розглянемо практичний приклад модуля обробки телеметрії. Продемонструємо відмінність між старим процедурним підходом мови C та його проблемною напівмодернізацією на C++:

:::tabs
```c
/* Процедурний C: ручна алокація, сирі вказівники, сигналізація через коди */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    double timestamp;
    float value;
    int status_flags;
} TelemetryPacket;

int filter_active_packets(const TelemetryPacket* input, int count, 
                          TelemetryPacket** output, int* out_count) {
    if (!input || count <= 0 || !output || !out_count) {
        return -1;
    }

    TelemetryPacket* buffer = (TelemetryPacket*)malloc(sizeof(TelemetryPacket) * count);
    if (!buffer) {
        return -2;
    }

    int active = 0;
    for (int i = 0; i < count; ++i) {
        if ((input[i].status_flags & 0x01) != 0) {
            buffer[active++] = input[i];
        }
    }

    *output = buffer;
    *out_count = active;
    printf("Extracted %d active packets\n", active);
    return 0;
}
```
```cpp
// Легасі-код на C++ із накопиченими порушеннями Core Guidelines
#include <cstdio>
#include <cstdlib>

struct TelemetryPacket {
    double timestamp;
    float value;
    int status_flags;
};

int filter_active_packets(const TelemetryPacket* input, int count, 
                          TelemetryPacket*& output, int& out_count) {
    // Дефект 1: ES.20 (неініціалізовані змінні)
    int active;
    int error_code;

    // Дефект 2: I.11 та Bounds.1 (сирий вказівник + int замість std::span)
    if (input == nullptr || count <= 0) {
        return -1;
    }

    // Дефект 3: R.10 та R.3 (сире виділення пам'яті в купі з неявним володінням)
    output = new TelemetryPacket[count];

    active = 0;
    for (int i = 0; i < count; ++i) {
        // Дефект 4: ES.46 (звужувальне перетворення при бітовій масці)
        short flag_masked = input[i].status_flags & 0x01;
        if (flag_masked != 0) {
            output[active] = input[i];
            active++;
        }
    }

    out_count = active;
    
    // Дефект 5: Type.1 (C-варіативна функція printf)
    std::printf("Extracted %d active packets\n", active);

    return 0;
}
```
:::

### Діагностичний звіт Clang-Tidy

При запуску аналізу файлу:
```bash
clang-tidy -p build/ telemetry_filter.cpp
```

Аналізатор формує чіткий структурований список помилок:

```text
telemetry_filter.cpp:13:5: error: variable 'active' is not initialized [cppcoreguidelines-init-variables]
    int active;
    ^
               = 0
telemetry_filter.cpp:14:5: error: variable 'error_code' is not initialized [cppcoreguidelines-init-variables]
    int error_code;
    ^
                  = 0

telemetry_filter.cpp:11:27: error: do not use pointer arithmetic or pass array as pointer/size pair [cppcoreguidelines-avoid-c-arrays,cppcoreguidelines-pro-bounds-pointer-arithmetic]
int filter_active_packets(const TelemetryPacket* input, int count, 
                          ^

telemetry_filter.cpp:21:14: error: assigning newly created 'gsl::owner<>' to non-owner 'TelemetryPacket *&' [cppcoreguidelines-owning-memory]
    output = new TelemetryPacket[count];
             ^

telemetry_filter.cpp:26:29: error: narrowing conversion from 'int' to 'short' [cppcoreguidelines-narrowing-conversions]
        short flag_masked = input[i].status_flags & 0x01;
                            ^

telemetry_filter.cpp:35:5: error: do not call c-style vararg functions like 'printf' [cppcoreguidelines-pro-type-vararg]
    std::printf("Extracted %d active packets\n", active);
    ^
```

---

## 4. Глибокий рефакторинг: Ідіоматичний та безпечний сучасний C++

Виправимо кожну проблему за допомогою відповідних стандартних конструкцій:

1. **Інтерфейс вхідних даних**: Замість `const TelemetryPacket* input, int count` використовуємо **`std::span<const TelemetryPacket>`** (правила I.13, Bounds.2). Це гарантує нерозривність даних та розміру без жодного копіювання.
2. **Семантика вихідних даних**: Замість вихідних посилань `TelemetryPacket*& output` повертаємо **`std::vector<TelemetryPacket>`** як результат функції за значенням (правила F.20, R.1). Завдяки оптимізації повернення значень (RVO) та семантиці переміщення (move semantics) повернення вектора не створює додаткових накладних витрат.
3. **Обробка помилок**: Замість повернення числових кодів помилок `int` використовуємо **`std::expected<std::vector<TelemetryPacket>, FilterError>`** (C++23) або кидаємо типізований виняток (правила E.2, E.3).
4. **Форматування рядків**: Замість `std::printf` використовуємо типобезпечний **`std::println`** (C++23) або `std::format` (C++20).

Оновлена безпечна реалізація:

```cpp
#include <span>
#include <vector>
#include <expected>
#include <print>
#include <cstdint>

struct TelemetryPacket {
    double timestamp{0.0};
    float value{0.0f};
    std::uint32_t status_flags{0};
};

enum class FilterError : std::uint8_t {
    EmptyInput,
    BufferCorrupted
};

[[nodiscard]] std::expected<std::vector<TelemetryPacket>, FilterError> 
filter_active_packets(std::span<const TelemetryPacket> input) noexcept 
{
    if (input.empty()) {
        return std::unexpected(FilterError::EmptyInput);
    }

    std::vector<TelemetryPacket> active_packets;
    active_packets.reserve(input.size());

    for (const auto& packet : input) {
        if ((packet.status_flags & 0x01U) != 0U) {
            active_packets.push_back(packet);
        }
    }

    std::println("Extracted {} active packets safely", active_packets.size());
    return active_packets;
}
```

Код пройшов повну статичну перевірку: нуль попереджень лінтера, повна відсутність витоків пам'яті, гарантована типобезпека та чистий самодокументований інтерфейс.

---

## 5. Порівняння інструментів: Clang-Tidy проти MSVC C++ Core Check

В індустрії C++ склалися дві основні реалізації автоматизованого аудиту Core Guidelines:

| Критерій | LLVM Clang-Tidy (`cppcoreguidelines-*`) | Microsoft Visual C++ Core Check (`/analyze`) |
| :--- | :--- | :--- |
| **Архітектурний рушій** | AST Matchers + Clang Static Analyzer (символьне виконання) | Вбудований у бекенд компілятора плагін `EspXEngine.dll` |
| **Профіль Lifetime Safety** | Частковий експериментальний аналіз (`-Wlifetime`) | Повний розвинений міжфункціональний аналіз життєвого циклу |
| **Конфігурація** | Текстовий файл `.clang-tidy` (YAML) | XML-файли наборів правил (`.ruleset`) у MSBuild / CMake |
| **Автоматичне виправлення** | Підтримується через `clang-apply-replacements` / `-fix` | Підтримується інтерактивно через Quick Actions у Visual Studio |
| **Кросплатформність** | Повна підтримка: Linux, macOS, Windows, FreeBSD, Android | Windows (MSVC) та крос-збірка під Linux через Clang/MSVC |

У середовищі Visual Studio C++ Core Check активується прапорцем компілятора `/analyze` та вибором відповідного набору правил (Rule Set):
- `CppCoreCheckOwnerRules.ruleset` — суворий контроль володіння ресурсами.
- `CppCoreCheckBoundsRules.ruleset` — перевірка безпеки меж масивів.
- `CppCoreCheckLifetimeRules.ruleset` — відстеження висячих вказівників та посилань.

Міжфункціональний аналіз у MSVC будує граф залежностей життєвого циклу об'єктів. Якщо функція приймає посилання на тимчасовий об'єкт і зберігає його в полі довгоживучого класу, компілятор MSVC генерує попередження `C26444` або `C26486` безпосередньо під час регулярної компіляції файлу.

---

## 6. Аудит багатопотоковості та конкурентності (Concurrency Rules)

Окремий потужний напрям у Core Guidelines становлять правила розділу CP (Concurrency and Parallelism), спрямовані на запобігання гонитвам за даними (data races) та взаємним блокуванням (deadlocks):

1. **`cppcoreguidelines-concurrency-mt-unsafe`**:
   Відповідає правилу CP.2. Забороняє виклики системних функцій стандартної бібліотеки C, які використовують небезпечний внутрішній статичний стан без синхронізації (`strtok`, `asctime`, `ctime`, `localtime`, `rand`). Вимагає заміни на реентрабельні C++ еквіваленти або генератори `<random>`.

2. **Захист ресурсів через RAII-блокування**:
   Відповідає правилу CP.20. Забороняє прямі виклики методів `.lock()` та `.unlock()` над об'єктами `std::mutex`. Захоплення м'ютекса зобов'язане відбуватися винятково через безпечні охоронці життєвого циклу: `std::scoped_lock` (C++17, з автоматичним алгоритмом запобігання дедлокам при захопленні кількох м'ютексів) або `std::unique_lock`.

3. **Заборона сирих потоків у бізнес-логіці**:
   Правило CP.1 рекомендує уникати прямого створення об'єктів `std::thread` без явної необхідності, надаючи перевагу високорівневим паралельним алгоритмам STL (`std::for_each(std::execution::par, ...)`), задачам `std::async` або пулам потоків.

---

## 7. Розробка власних правил на базі Clang AST Matchers

У великих корпоративних проєктах часто виникає потреба створити власні специфічні розширення правил Core Guidelines. Завдяки модульній архітектурі Clang це реалізується за допомогою бібліотеки `clang::ast_matchers`.

Приклад написання власного чекера, який перевіряє, що всі фабричні методи повертають об'єкти винятково через `std::unique_ptr`, а не через сирий вказівник:

```cpp
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/StaticAnalyzer/Checkers/BuiltinCheckerRegistration.h"
#include "clang/Tidy/ClangTidyCheck.h"

using namespace clang::ast_matchers;

namespace custom_guidelines {

class FactoryReturnCheck : public clang::tidy::ClangTidyCheck {
public:
    FactoryReturnCheck(llvm::StringRef Name, clang::tidy::ClangTidyContext *Context)
        : ClangTidyCheck(Name, Context) {}

    void registerMatchers(MatchFinder *Finder) override {
        // Шукаємо оголошення функцій, назва яких починається з "create" або "make",
        // які повертають сирий вказівник замість розумного
        Finder->addMatcher(
            functionDecl(
                hasName("create"),
                returns(pointerType(pointee(hasDeclaration(recordDecl()))))
            ).bind("faulty_factory"),
            this
        );
    }

    void check(const MatchFinder::MatchResult &Result) override {
        const auto *MatchedDecl = Result.Nodes.getNodeAs<clang::FunctionDecl>("faulty_factory");
        if (!MatchedDecl) return;

        diag(MatchedDecl->getLocation(),
             "Фабрична функція %0 повертає сирий вказівник; за правилом R.3 слід повертати std::unique_ptr")
            << MatchedDecl;
    }
};

} // namespace custom_guidelines
```

Такий підхід дозволяє перетворювати будь-яку архітектурну угоду команди на непідкупний компіляторний контроль.

---

## 8. Легітимні низькорівневі винятки та їх ізоляція

У системному програмуванні існують об'єктивні ситуації, коли пряме порушення правил є неминучим:
- Розробка високоефективних алокаторів пам'яті (Memory Arenas, Slab Allocators).
- Взаємодія з системним API ядра ОС або C-бібліотеками драйверів (POSIX, Win32 API).
- Пряма робота з апаратними регістрами введення-виведення (Memory-Mapped I/O).
- Реалізація користувацьких структур даних низького рівня (Custom Lock-free Queues).

Статичний аналізатор не може автоматично довести коректність низькорівневої адресної арифметики в таких специфічних вузлах. Для таких випадків Core Guidelines формулюють принцип: **«Порушуй правило лише за абсолютної технічної необхідності; локалізуй порушення в окремій функції та надай формальне доведення інваріанту безпеки»**.

### Спосіб 1: Атрибут `[[gsl::suppress(...)]]`
Офіційний механізм, розроблений для підтримки інструментами аналізу:

```cpp
#include <cstddef>
#include <new>

class HardwareDMAController {
public:
    [[nodiscard]] void* allocate_coherent_buffer(std::size_t size) {
        // Локально документуємо виняток для виділення сирої DMA пам'яті
        [[gsl::suppress("cppcoreguidelines-owning-memory", 
          justification = "DMA-буфер вирівнюється за сторінкою пам'яті; звільняється в ~HardwareDMAController")]]
        void* dma_buffer = ::operator new(size, std::align_val_t{4096});
        return dma_buffer;
    }
};
```

### Спосіб 2: Директива лінтера `// NOLINTNEXTLINE(...)`
Універсальний інструментальний синтаксис для `clang-tidy`. Обов'язково вимагає вказувати конкретне ім'я чекера та технічне обґрунтування:

```cpp
// NOLINTNEXTLINE(cppcoreguidelines-pro-type-reinterpret-cast): Пряме відображення апаратного регістру таймера APB1
auto* timer_reg = reinterpret_cast<volatile uint32_t*>(0x40000000UL);
```

> ⚠️ **Антипатерн масового глушіння:** Використання неспецифікованої директиви `// NOLINT` або глобальне відключення чекерів у `.clang-tidy` є грубим порушенням інженерної культури. Будь-яке придушення попередження без технічного обґрунтування інваріанту відхиляється на етапі code review.

---

## 9. Стратегія поетапного впровадження у великі легасі-проєкти

Якщо спробувати увімкнути повний набір перевірок `cppcoreguidelines-*` у кодовій базі на кілька мільйонів рядків старого коду, аналізатор згенерує десятки тисяч повідомлень про помилки, паралізувавши роботу команди.

Для безпечної та поступової модернізації кодових баз застосовують триетапну стратегію:

1. **Диференційний аудит модифікованого коду (Diff-based Tidy)**:
   Лінтер запускається винятково на змінених рядках коду в межах поточного Pull Request. Для цього використовується офіційний скрипт `clang-tidy-diff.py`:
   ```bash
   git diff -U0 HEAD~1 | clang-tidy-diff.py -p1 -path build/
   ```
   Це гарантує залізне правило: новий код пишеться за новими стандартами, а старий код не чіпається до планового рефакторингу.

2. **Покрокове вмикання груп чекерів (Phased Rollout)**:
   - *Фаза 1 (Ініціалізація та явність)*: `cppcoreguidelines-init-variables`, `cppcoreguidelines-explicit-virtual-functions`.
   - *Фаза 2 (Володіння та витоки)*: `cppcoreguidelines-owning-memory`, `cppcoreguidelines-no-malloc`.
   - *Фаза 3 (Безпека меж та приведення)*: `cppcoreguidelines-avoid-c-arrays`, `cppcoreguidelines-pro-type-*`.

3. **Автоматизоване виправлення через `clang-apply-replacements`**:
   Багато чекерів Clang-Tidy здатні самостійно трансформувати синтаксичне дерево коду, замінюючи старі конструкції новими:
   ```bash
   run-clang-tidy -fix -format -p build/
   ```
   Утиліта автоматично розставляє ключові слова `override`, замінює C-масиви на `std::array` та ініціалізує змінні нульовими значеннями.

---

## 10. Інтеграція в сучасні середовища розробки (IDE) та мовні сервери

Для забезпечення найшвидшого зворотного зв'язку (feedback loop) порушення Core Guidelines мають підсвічуватися безпосередньо під час набору коду в редакторі інженера:

1. **Мовний сервер `clangd` (VS Code, Neovim, Emacs)**:
   Сервер `clangd` містить вбудовану підтримку `clang-tidy`. Для її активації достатньо створити файл `.clangd` у корені проєкту:
   ```yaml
   CompileFlags:
     CompilationDatabase: "build"
   Diagnostics:
     ClangTidy:
       Add: [cppcoreguidelines-*]
       Remove: [cppcoreguidelines-avoid-magic-numbers]
     UnusedIncludes: Strict
   ```
   Усі порушення правил підкреслюються як помилки компіляції в реальному часі.

2. **JetBrains CLion**:
   CLion постачається з вбудованим рушієм Clangd. У розділі налаштувань `Settings -> Editor -> Inspections -> C/C++ -> Clang-Tidy` обирається пункт `Prefer .clang-tidy file`, що автоматично синхронізує правила середовища з конфігурацією репозиторію.

3. **Visual Studio 2022**:
   У налаштуваннях властивостей проєкту (`Project Properties -> Code Analysis -> Clang-Tidy`) вмикається прапорець `Enable Clang-Tidy`, що запускає аналіз у фоновому потоці під час збереження файлу.

---

## 11. Продуктивність лінтера, модулі C++20 та кешування

На великих проєктах розробники часто скаржаться на швидкість роботи `clang-tidy`, оскільки він змушений парсити повне дерево заголовків для кожної одиниці трансляції. Для прискорення перевірок у 5–10 разів застосовуються такі інженерні практики:

1. **Паралелізація запуску**: Використання утиліти `run-clang-tidy` із параметром `-j $(nproc)`, яка розподіляє аналіз файлів по всіх доступних ядрах процесора.
2. **Кешування синтаксичного дерева**: Інструменти на зразок `clang-tidy-cache` хешують сирцевий файл разом із усіма залежними заголовками. Якщо вміст файлу не змінився з моменту останнього прогону, результат попереднього аналізу витягується з кешу за мілісекунди.
3. **Використання C++20 модулів (`import std;`)**: Модульна система C++20 кардинально змінює роботу лінтера. Замість повторного текстового розгортання мільйонів рядків заголовків стандартної бібліотеки компілятор Clang зчитує попередньо скомпільований бінарний інтерфейс модуля (BMI). Це скорочує час побудови AST для статичного аналізу на 60–70%.
4. **Інкрементальні збірки з ccache**: Інтеграція `ccache` із Clang-Tidy дозволяє оминати повторний семантичний аналіз тих одиниць трансляції, що не зазнали жодних змін у вихідному коді або заголовках.

---

## 12. Практичний чеклист для міграції проєкту на Core Guidelines

Для систематичного переведення кодової бази на стандарти C++ Core Guidelines рекомендується дотримуватися такого алгоритму:

1. **Встановлення стандарту мови**: Увімкніть щонайменше стандарт C++20 у системі збірки (`CMAKE_CXX_STANDARD 20`), щоб відкрити доступ до `std::span`, концептів, `std::format` та модулів.
2. **Генерація бази компіляції**: Переконайтеся, що файл `compile_commands.json` генерується автоматично під час конфігурації CMake (`set(CMAKE_EXPORT_COMPILE_COMMANDS ON)`).
3. **Формування початкового профілю**: Створіть файл `.clang-tidy` з активацією базових чекерів безпеки меж та ініціалізації.
4. **Автоматизоване виправлення тривіальних помилок**: Запустіть `run-clang-tidy -fix` для автоматичного проставлення `override`, `nullptr` та ініціалізації числових змінних.
5. **Рефакторинг інтерфейсів**: Замініть небезпечні пари `(T* ptr, int size)` на `std::span<T>`, а C-рядки `const char*` — на `std::string_view`.
6. **Захист CI/CD конвеєра**: Налаштуйте перевірку змінених рядків через `clang-tidy-diff.py` як обов'язковий блокуючий статус (blocking status check) у системі керування репозиторієм (GitHub Actions / GitLab CI).
7. **Постійний моніторинг кодової бази**: Щотижневий автоматичний запуск повного аудиту всього репозиторію для виявлення застарілих винятків та відстеження метрик покриття правилами.

---

## 13. Інтеграція в CMake та конвеєр CI/CD GitHub Actions

### Налаштування системи збірки CMake

Для запуску перевірок безпосередньо під час кожної локальної компіляції додайте в `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.22)
project(CoreGuidelinesProject CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Експорт бази компіляції (compile_commands.json) для лінтерів
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_program(CLANG_TIDY_EXE NAMES clang-tidy)

if(CLANG_TIDY_EXE)
    message(STATUS "Clang-Tidy активовано: ${CLANG_TIDY_EXE}")
    set(CMAKE_CXX_CLANG_TIDY 
        "${CLANG_TIDY_EXE};--config-file=${CMAKE_CURRENT_SOURCE_DIR}/.clang-tidy;--warnings-as-errors=*")
else()
    message(WARNING "Clang-Tidy не знайдено на машині розробника!")
endif()

add_library(telemetry_lib src/telemetry_filter.cpp)
add_executable(telemetry_app src/main.cpp)
target_link_libraries(telemetry_app PRIVATE telemetry_lib)
```

### Конфігурація неперервної інтеграції GitHub Actions

Щоб жоден pull request із дефектами безпеки пам'яті не потрапив у головну гілку репозиторію, створимо файл робочого процесу `.github/workflows/core-guidelines-ci.yml`:

```yaml
name: C++ Core Guidelines CI Audit

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  clang-tidy-audit:
    runs-on: ubuntu-24.04

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install Clang-Tidy and LLVM Tools
        run: |
          sudo apt-get update
          sudo apt-get install -y clang-tidy-18 ninja-build

      - name: Configure CMake and Generate Compilation Database
        run: |
          cmake -B build -G Ninja \
            -DCMAKE_CXX_COMPILER=clang++-18 \
            -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

      - name: Run Clang-Tidy Parallel Analysis
        run: |
          run-clang-tidy-18 -p build -j $(nproc) \
            -config-file=.clang-tidy \
            -header-filter="^(src|include)/.*" \
            -warnings-as-errors='cppcoreguidelines-*'
```

Такий конвеєр повністю автоматизує захист кодової бази: кожна зміна перевіряється математично суворими алгоритмами аналізу синтаксичного дерева, гарантуючи відповідність стандарту сучасного надійного C++.
