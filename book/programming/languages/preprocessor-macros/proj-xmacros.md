# ⚙️ Генерація таблиць і серіалізація через X-Macros

У розробці мережевих протоколів, низькорівневих драйверів і вбудованих систем виникає постійна інженерна рутина: підтримка взаємної синхронізації кількох пов'язаних структур даних.

Розгляньмо типову інженерну задачу. Протокол зв'язку бортового комп'ютера керує набором команд телеметрії. Для кожної команди в кодовій базі необхідно забезпечити:
1. Ідентифікатор у переліченні (`enum`) для зручної та швидкої диспетчеризації у коді;
2. Числовий код для серіалізації в бінарний мережевий пакет;
3. Текстову назву для виводу в лог-файли та налагоджувальні консолі;
4. Функцію зворотного перетворення (парсингу) з текстового рядка в числову команду;
5. Метадані безпеки (наприклад, прапорець обов'язкової автентифікації користувача).

При наївному підході розробник оголошує `enum`, потім в іншому файлі пише функцію `command_to_string` із довгим блоком `switch`, у третьому модулі створює таблицю парсингу рядків, а в четвертому — масив прав доступу.

Щойно в протокол додається нова команда або змінюється числовий код наявної команди, розробник зобов'язаний вручну внести узгоджені правки в усі чотири місця. Якщо одне з місць випадково забули оновити, компілятор не видасть жодної помилки: програма успішно скомпілюється, але під час експлуатації парсер текстових команд не розпізнає новий запит або в лог запишеться спотворене значення.

Ця проблема порушує фундаментальний принцип розробки ПЗ — *Single Source of Truth* (єдине джерело правди). Інженерне вирішення полягає в тому, щоб описати структуру всіх команд рівно один раз у вигляді центральної таблиці, а потім автоматично згенерувати всі похідні мовні структури.

У мові C головним інструментом для цього є техніка **X-Macros**.

---

### Архітектура патерна X-Macros у мові C

Патерн X-Macros спирається на двоетапну текстову макропідстановку. Ми оголошуємо макрос списку (майстер-таблицю), який приймає як формальний аргумент ім'я іншого макросу (традиційно позначеного літерою `X`). Тіло списку викликає цей макрос `X(...)` для кожного запису таблиці:

:::tabs
```c
#define TELEMETRY_COMMAND_TABLE(X) \
    X(CMD_PING,       0x01, "ping",       false) \
    X(CMD_GET_STATUS, 0x02, "get_status", false) \
    X(CMD_SET_CONFIG, 0x03, "set_config", true)  \
    X(CMD_REBOOT,     0xFF, "reboot",     true)
```
```cpp
// У C++ майстер-таблиця X-Macro має ідентичний синтаксис для сумісності з C
#define TELEMETRY_COMMAND_TABLE(X) \
    X(CMD_PING,       0x01, "ping",       false) \
    X(CMD_GET_STATUS, 0x02, "get_status", false) \
    X(CMD_SET_CONFIG, 0x03, "set_config", true)  \
    X(CMD_REBOOT,     0xFF, "reboot",     true)
```
:::

Кожен рядок таблиці фіксує чотири параметри: ідентифікатор мови, числовий код протоколу, текстовий рядок для логів та логічний прапорець вимоги прав адміністратора.

Маючи таку таблицю, ми можемо багаторазово розгортати її для генерації коду: щоразу перед викликом таблиці ми визначаємо макрос `X` під конкретну форму виводу, а одразу після розгортання видаляємо його директивою `#undef X`.

---

### Повна реалізація на C та C++

Нижче наведено закінчену реалізацію протоколу: генерацію перелічення, друку, перевірки прав та парсингу команд.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>

/* ── 1. Єдине джерело правди (Майстер-таблиця) ── */
#define TELEMETRY_COMMAND_TABLE(X) \
    X(CMD_PING,       0x01, "ping",       false) \
    X(CMD_GET_STATUS, 0x02, "get_status", false) \
    X(CMD_SET_CONFIG, 0x03, "set_config", true)  \
    X(CMD_REBOOT,     0xFF, "reboot",     true)

/* ── 2. Генерація перелічення (Enum) ── */
typedef enum {
#define X(name, code, str, auth) name = code,
    TELEMETRY_COMMAND_TABLE(X)
#undef X
    CMD_INVALID = 0x00
} TelemetryCmd;

/* ── 3. Генерація функції Enum -> String ── */
static const char* telemetry_cmd_to_str(TelemetryCmd cmd) {
    switch (cmd) {
#define X(name, code, str, auth) case name: return str;
        TELEMETRY_COMMAND_TABLE(X)
#undef X
        default: return "UNKNOWN";
    }
}

/* ── 4. Генерація перевірки вимоги автентифікації ── */
static bool telemetry_cmd_requires_auth(TelemetryCmd cmd) {
    switch (cmd) {
#define X(name, code, str, auth) case name: return auth;
        TELEMETRY_COMMAND_TABLE(X)
#undef X
        default: return true; /* Безпечний дефолт */
    }
}

/* ── 5. Генерація функції String -> Enum (Парсер) ── */
static TelemetryCmd telemetry_str_to_cmd(const char* str) {
    if (!str) return CMD_INVALID;

#define X(name, code, str_val, auth) \
    if (strcmp(str, str_val) == 0) return name;
    TELEMETRY_COMMAND_TABLE(X)
#undef X

    return CMD_INVALID;
}

int main(void) {
    const char* input_command = "set_config";
    TelemetryCmd cmd = telemetry_str_to_cmd(input_command);

    if (cmd != CMD_INVALID) {
        printf("Знайдено команду: %s (код: 0x%02X)\n",
               telemetry_cmd_to_str(cmd), (unsigned int)cmd);
        printf("Потрібна автентифікація: %s\n",
               telemetry_cmd_requires_auth(cmd) ? "ТАК" : "НІ");
    } else {
        printf("Команду «%s» не розпізнано!\n", input_command);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <array>
#include <optional>
#include <cstdint>

// У C++20 задачу єдиного джерела правди розв'язують через типізовані constexpr-таблиці
// без використання макропідстановок у точках генерації логіки.

enum class TelemetryCmd : uint8_t {
    Ping       = 0x01,
    GetStatus  = 0x02,
    SetConfig  = 0x03,
    Reboot     = 0xFF,
    Invalid    = 0x00
};

struct CommandMeta {
    TelemetryCmd cmd;
    std::string_view name;
    bool requires_auth;
};

// Єдине джерело правди як constexpr-масив структур
inline constexpr std::array<CommandMeta, 4> CommandRegistry{{
    { TelemetryCmd::Ping,      "ping",       false },
    { TelemetryCmd::GetStatus, "get_status", false },
    { TelemetryCmd::SetConfig, "set_config", true  },
    { TelemetryCmd::Reboot,    "reboot",     true  }
}};

// Пошук текстової назви команди (працює і під час компіляції, і під час виконання)
[[nodiscard]] constexpr std::string_view to_string(TelemetryCmd cmd) noexcept {
    for (const auto& entry : CommandRegistry) {
        if (entry.cmd == cmd) return entry.name;
    }
    return "UNKNOWN";
}

// Перевірка вимоги автентифікації
[[nodiscard]] constexpr bool requires_auth(TelemetryCmd cmd) noexcept {
    for (const auto& entry : CommandRegistry) {
        if (entry.cmd == cmd) return entry.requires_auth;
    }
    return true; // Безпечний дефолт
}

// Парсер рядка в значення перелічення
[[nodiscard]] constexpr std::optional<TelemetryCmd> from_string(std::string_view str) noexcept {
    for (const auto& entry : CommandRegistry) {
        if (entry.name == str) return entry.cmd;
    }
    return std::nullopt;
}

int main() {
    constexpr std::string_view input_command = "set_config";
    const auto cmd_opt = from_string(input_command);

    if (cmd_opt.has_value()) {
        const auto cmd = *cmd_opt;
        std::cout << "Знайдено команду: " << to_string(cmd)
                  << " (код: 0x" << std::hex << static_cast<unsigned>(cmd) << std::dec << ")\n";
        std::cout << "Потрібна автентифікація: "
                  << (requires_auth(cmd) ? "ТАК" : "НІ") << "\n";
    } else {
        std::cout << "Команду «" << input_command << "» не розпізнано!\n";
    }
    return 0;
}
```
:::

---

### Варіант X-Macros через зовнішній файл `.def`

Коли таблиця містить сотні записів (наприклад, таблиця всіх системних викликів ядра ОС або опкодів віртуальної машини), тримати її всередині багаторядкового макросу зі зворотними слешами `\` стає незручно.

У таких проєктах саму таблицю виносять в окремий файл без header guards (наприклад, `commands.def`):

:::tabs
```c
/* Файл: commands.def (навмисно без #ifndef / #pragma once) */
X(CMD_PING,       0x01, "ping",       false)
X(CMD_GET_STATUS, 0x02, "get_status", false)
X(CMD_SET_CONFIG, 0x03, "set_config", true)
X(CMD_REBOOT,     0xFF, "reboot",     true)
```
```cpp
// Файл: commands.def для C++ (структура записів ідентична)
X(CMD_PING,       0x01, "ping",       false)
X(CMD_GET_STATUS, 0x02, "get_status", false)
X(CMD_SET_CONFIG, 0x03, "set_config", true)
X(CMD_REBOOT,     0xFF, "reboot",     true)
```
:::

У файлі реалізації C або C++ таблиця викликається повторним включенням файлу через `#include`:

:::tabs
```c
typedef enum {
#define X(name, code, str, auth) name = code,
#include "commands.def"
#undef X
} TelemetryCmd;
```
```cpp
enum class TelemetryCmd : uint8_t {
#define X(name, code, str, auth) name = code,
#include "commands.def"
#undef X
};
```
:::

Препроцесор щоразу заново відкриває `commands.def`, підставляючи актуальне визначення макросу `X`.

---

### Механізм розгортання та аналіз машинного коду

Розгляньмо, що саме відбувається під капотом компілятора під час трансляції функції `telemetry_cmd_to_str`.

Препроцесор на фазі 4 розгортає макрос у чистий блок коду:

:::tabs
```c
static const char* telemetry_cmd_to_str(TelemetryCmd cmd) {
    switch (cmd) {
        case CMD_PING: return "ping";
        case CMD_GET_STATUS: return "get_status";
        case CMD_SET_CONFIG: return "set_config";
        case CMD_REBOOT: return "reboot";
        default: return "UNKNOWN";
    }
}
```
```cpp
// Розгорнута форма в C++ містить типізовані мітки перелічення enum class
constexpr const char* telemetry_cmd_to_str_cpp(TelemetryCmd cmd) noexcept {
    switch (cmd) {
        case TelemetryCmd::Ping: return "ping";
        case TelemetryCmd::GetStatus: return "get_status";
        case TelemetryCmd::SetConfig: return "set_config";
        case TelemetryCmd::Reboot: return "reboot";
        default: return "UNKNOWN";
    }
}
```
:::

Компілятор бачить звичайну конструкцію `switch`. Оскільки значення констант відомі на етапі компіляції, оптимізатор будує компактну таблицю переходів (*jump table*) або бінарне дерево порівнянь. У машинному коді не залишається жодних слідів макросів: виклик функції `telemetry_cmd_to_str` виконується за кілька тактів процесора без додаткового виділення динамічної пам'яті на купі.

---

### Ієрархічні та багаторівневі X-Macros

У великих архітектурних системах таблиці часто формують ієрархію: кілька підсистем реєструють власні списки команд, які згодом агрегуються в загальний реєстр пристрою.

Патерн X-Macros масштабується на таку вкладеність:

:::tabs
```c
#include <stdio.h>

#define POWER_COMMANDS(X) \
    X(PWR_SLEEP, 0x10, "sleep") \
    X(PWR_WAKE,  0x11, "wake")

#define SENSOR_COMMANDS(X) \
    X(SNS_READ_TEMP, 0x20, "read_temp") \
    X(SNS_READ_HUM,  0x21, "read_hum")

#define ALL_SYSTEM_COMMANDS(X) \
    POWER_COMMANDS(X) \
    SENSOR_COMMANDS(X)

typedef enum {
#define X(name, code, str) name = code,
    ALL_SYSTEM_COMMANDS(X)
#undef X
} SystemCmd;

int main(void) {
    printf("Код команди PWR_SLEEP: 0x%02X\n", PWR_SLEEP);
    printf("Код команди SNS_READ_TEMP: 0x%02X\n", SNS_READ_TEMP);
    return 0;
}
```
```cpp
#include <iostream>
#include <cstdint>

#define POWER_COMMANDS(X) \
    X(PWR_SLEEP, 0x10, "sleep") \
    X(PWR_WAKE,  0x11, "wake")

#define SENSOR_COMMANDS(X) \
    X(SNS_READ_TEMP, 0x20, "read_temp") \
    X(SNS_READ_HUM,  0x21, "read_hum")

#define ALL_SYSTEM_COMMANDS(X) \
    POWER_COMMANDS(X) \
    SENSOR_COMMANDS(X)

enum class SystemCmd : uint8_t {
#define X(name, code, str) name = code,
    ALL_SYSTEM_COMMANDS(X)
#undef X
};

int main() {
    std::cout << "Код PWR_SLEEP: 0x" << std::hex
              << static_cast<unsigned>(SystemCmd::PWR_SLEEP) << "\n";
    return 0;
}
```
:::

Завдяки вкладеності викликів додавання нової групи команд в одну з підсистем автоматично оновлює загальний диспетчер всієї системи.

---

### Порівняльний аналіз: X-Macros у C проти `constexpr` у C++

Обидва підходи реалізують принцип Single Source of Truth, проте оперують на різних фазах трансляції:

| Критерій | C: X-Macros | C++: `constexpr std::array` / Шаблони |
| :--- | :--- | :--- |
| **Етап генерації** | Фаза 4 препроцесора (текстова підстановка токенів) | Фаза 7 компілятора (синтаксичний аналіз, типи, AST) |
| **Перевірка типів** | Відсутня під час розгортання; помилки ловляться пізніше | Повна строга перевірка типів компілятором у точці опису |
| **Підтримка IDE** | Обмежена: перехід до визначення веде до рядка макросу | Бездоганна: навігація по символах, автодоповнення полів |
| **Формування `switch`** | Автоматично створює оптимізований блок `switch-case` | `constexpr` цикл розгортається компілятором у таблицю або бінарний пошук |
| **Швидкість компіляції** | Практично миттєва підстановка тексту | Вимагає часу на інстанціювання шаблонів та constexpr-вирахування |

### Правила гігієни при роботі з X-Macros

1. **Обов'язковий `#undef X` після кожного використання.** Якщо пропустити директиву `#undef X`, подальше перевизначення `#define X(...)` викличе попередження компілятора, а випадкове використання літери `X` у наступному коді буде катастрофічно спотворене.
2. **Захист коми у складних аргументах.** Якщо поле таблиці містить кому (наприклад, тип `pair<int, int>` або вираз `(a, b)`), препроцесор сприйме її як роздільник макроаргументів. Щоб уникнути синтаксичної помилки, такі вирази беруть у круглі дужки.
3. **Обмеження модифікації.** X-Macros генерує однотипний код для кожного елемента. Якщо одна з команд потребує індивідуального прототипу чи спеціального прапорця, таблицю доводиться розширювати додатковими стовпцями для всіх записів.

X-Macros залишається найпотужнішим інструментом метапрограмування в мові C, який гарантує нульові накладні витрати в рантаймі та повну узгодженість структур даних.
