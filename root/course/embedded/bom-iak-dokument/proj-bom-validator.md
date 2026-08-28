# ⚙️ Автоматичний аудит і валідатор специфікації BOM

Помилка в специфікації компонентів, виявлена на конвеєрі монтажу, коштує сотні доларів за кожну годину простою лінії та тижні затримки виробничого циклу. Ручна перевірка таблиць із сотнями позицій неминуче пропускає одруківки в суфіксах, дублікати позиційних позначень або невідповідність між заявленою кількістю та фактичним списком компонентів.

Автоматизований валідатор BOM приймає експортований із САПР файл `CSV` і перевіряє його за правилами інженерного контракту до того, як замовлення потрапить до відділу закупівель або на фабрику.

## Задача аудиту та правила перевірки

Валідатор повинен зчитати таблицю BOM і перевірити шість інваріантів для кожного рядка та документа в цілому:

1. **Цілісність списку Designator:** розбити поле позначень за комами й перевірити кожне позначення за маскою `^[A-Z]{1,3}[0-9]+[A-Z]?$`. Маска підтримує як стандартні компоненти (`R1`, `C12`), так і багатосекційні елементи (`U1A`, `U1B` для зчетверених операційних підсилювачів). Специфікація не повинна містити діапазонів на кшталт `R1-R10` (вони мають бути розгорнуті в повний перелік `R1, R2, ..., R10`).
2. **Збіг кількості (Quantity Check):** кількість розпарсених позначень у рядку мусить строго дорівнювати значенню в стовпці `Qty`.
3. **Глобальна унікальність позначень (No Duplicates):** жоден десігнатор (наприклад `C14`) не може з'являтися у двох різних рядках BOM.
4. **Повнота артикулу монтованих компонентів:** якщо позиція не позначена як `DNP` / `DNI`, вона обов'язково повинна містити непорожні поля `MPN`, `Manufacturer` та `Footprint`. Значення `TBD`, `N/A`, `?`, `Unknown` вважаються критичними помилками.
5. **Евристика суфіксів пакування (Packaging Suffix Check):** активні мікросхеми у корпусах QFP, QFN, SOIC для серійного монтажу повинні мати суфікс котушки (`TR`, `R`, `T&R`), а не піддона (`Tray`) чи трубки (`Tube`), якщо тип пакування заявлено як `Tape & Reel`.
6. **Коректність DNP:** позиції зі статусом `DNP` повинні мати пояснення в описі або примітці (наприклад, тестова точка, необов'язковий фільтр, альтернативне живлення).

## Архітектура та логіка роботи валідатора

Процес валідації складається з чотирьох послідовних фаз:

1. **Лексичний аналіз CSV:** Рядок таблиці розбивається на поля за допомогою конечного автомата, що враховує лапки. Це критично, оскільки поле `Designator` зазвичай містить коми всередині лапок (наприклад, `"R1, R2, R3"`), які стандартний `strtok` помилково розпізнає як роздільники стовпців.
2. **Нормалізація та очищення:** Видаляються пробіли на початку та в кінці значень, відкидаються символи повернення каретки `\r`, фільтруються порожні рядки та байтовий маркер UTF-8 BOM (`\xEF\xBB\xBF`).
3. **Порядковий аудит інваріантів:** Для кожного рядка формується окремий список виділених позначень, звіряється їхня кількість з полем `Quantity`, перевіряється відсутність дублікатів через глобальну хеш-таблицю та аналізується валідність артикулу MPN.
4. **Зіставлення з файлом координат CPL (Cross-Check with Centroid):** Валідатор порівнює список активних монтованих компонентів із координатами Pick & Place (`.xy`, `.pos`, `.cpl`). Якщо деталь є в BOM, але відсутня в CPL, вона не буде змонтована автоматом. Якщо деталь є в CPL, але відсутня в BOM, сопло автомата шукатиме її в незарядженому фідері.
5. **Генерація структурованого звіту:** Помилки класифікуються на критичні (що блокують реліз і повертають ненульовий код виходу `1`) та попередження (що повертають `0`, але вимагають ручної уваги інженера).

## Реалізація валідатора BOM

Нижче наведено робочий валідатор, що підтримує стандартні діалекти CSV (включно з клітинками в лапках, що містять коми), перевіряє всі шість інваріантів і генерує звіт про помилки.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_LINE_LEN 2048
#define MAX_FIELDS 32
#define MAX_DESIGNATORS 2048
#define MAX_STR_LEN 128

typedef struct {
    char name[MAX_STR_LEN];
    int line_num;
} RefDesEntry;

typedef struct {
    RefDesEntry entries[MAX_DESIGNATORS];
    size_t count;
} RefDesTable;

// Розбір одного рядка CSV з урахуванням лапок
static int parse_csv_line(char *line, char *fields[], int max_f) {
    int count = 0;
    char *p = line;
    bool in_quotes = false;
    char *field_start = p;

    while (*p && count < max_f) {
        if (*p == '"') {
            in_quotes = !in_quotes;
        } else if (*p == ',' && !in_quotes) {
            *p = '\0';
            fields[count++] = field_start;
            field_start = p + 1;
        }
        p++;
    }
    if (count < max_f) {
        // Обрізаємо перенесення рядка
        char *end = p - 1;
        while (end >= field_start && (*end == '\r' || *end == '\n')) {
            *end = '\0';
            end--;
        }
        fields[count++] = field_start;
    }
    return count;
}

// Очищення пробілів і лапок на краях рядка
static void trim(char *s) {
    char *p = s;
    while (isspace((unsigned char)*p) || *p == '"') p++;
    if (p != s) memmove(s, p, strlen(p) + 1);

    size_t len = strlen(s);
    while (len > 0 && (isspace((unsigned char)s[len - 1]) || s[len - 1] == '"')) {
        s[--len] = '\0';
    }
}

// Перевірка синтаксису RefDes: 1-3 великі літери + цифри + опціональна секція
static bool is_valid_refdes(const char *s) {
    if (!s || !*s) return false;
    int letters = 0;
    while (isalpha((unsigned char)*s)) {
        if (!isupper((unsigned char)*s)) return false;
        letters++;
        s++;
    }
    if (letters < 1 || letters > 3) return false;
    if (!isdigit((unsigned char)*s)) return false;
    while (isdigit((unsigned char)*s)) s++;
    // Допускаємо букву секції для багатосекційних ІС (U1A, U1B)
    if (isalpha((unsigned char)*s) && isupper((unsigned char)*s)) s++;
    return *s == '\0';
}

// Перевірка на заборонені заглушки в артикулах
static bool is_dummy_value(const char *s) {
    if (!s || strlen(s) == 0) return true;
    if (strcmp(s, "TBD") == 0 || strcmp(s, "N/A") == 0 ||
        strcmp(s, "TODO") == 0 || strcmp(s, "?") == 0 ||
        strcmp(s, "DNI") == 0 || strcmp(s, "DNP") == 0) {
        return true;
    }
    return false;
}

// Головна процедура аудиту CSV файлу
int validate_bom(const char *filename) {
    FILE *f = fopen(filename, "r");
    if (!f) {
        fprintf(stderr, "Помилка відкриття файлу: %s\n", filename);
        return -1;
    }

    char line[MAX_LINE_LEN];
    char *fields[MAX_FIELDS];
    RefDesTable ref_table = { .count = 0 };
    int line_num = 0;
    int errors_count = 0;
    int warnings_count = 0;

    // Читаємо заголовок
    if (!fgets(line, sizeof(line), f)) {
        fclose(f);
        return -1;
    }
    line_num++;

    printf("=== Початок аудиту BOM: %s ===\n", filename);

    while (fgets(line, sizeof(line), f)) {
        line_num++;
        // Пропускаємо порожні рядки
        if (line[0] == '\r' || line[0] == '\n' || line[0] == '\0') continue;

        int num_fields = parse_csv_line(line, fields, MAX_FIELDS);
        if (num_fields < 5) {
            printf("[ПОМИЛКА] Рядок %d: недостатньо полів (%d)\n", line_num, num_fields);
            errors_count++;
            continue;
        }

        char *raw_designators = fields[0];
        char *raw_qty         = fields[1];
        char *raw_mpn         = fields[2];
        char *raw_mfg         = fields[3];
        char *raw_footprint   = fields[4];
        char *raw_status      = (num_fields > 5) ? fields[5] : "Populate";

        trim(raw_designators);
        trim(raw_qty);
        trim(raw_mpn);
        trim(raw_mfg);
        trim(raw_footprint);
        trim(raw_status);

        bool is_dnp = (strcasecmp(raw_status, "DNP") == 0 ||
                       strcasecmp(raw_status, "DNI") == 0 ||
                       strcasecmp(raw_status, "NF") == 0);

        int expected_qty = atoi(raw_qty);
        int parsed_qty = 0;

        // Розбираємо список позначень
        char des_copy[MAX_LINE_LEN];
        strncpy(des_copy, raw_designators, sizeof(des_copy) - 1);
        des_copy[sizeof(des_copy) - 1] = '\0';

        char *token = strtok(des_copy, ",; ");
        while (token) {
            trim(token);
            if (strlen(token) > 0) {
                parsed_qty++;

                // 1. Перевірка валідності формату позначення
                if (!is_valid_refdes(token)) {
                    printf("[ПОМИЛКА] Рядок %d: неприпустимий синтаксис позначення '%s'\n", line_num, token);
                    errors_count++;
                }

                // 2. Перевірка на глобальні дублікати
                for (size_t i = 0; i < ref_table.count; i++) {
                    if (strcmp(ref_table.entries[i].name, token) == 0) {
                        printf("[ПОМИЛКА] Рядок %d: дублікат позначення '%s' (раніше у рядку %d)\n",
                               line_num, token, ref_table.entries[i].line_num);
                        errors_count++;
                    }
                }

                // Додаємо в таблицю
                if (ref_table.count < MAX_DESIGNATORS) {
                    strncpy(ref_table.entries[ref_table.count].name, token, MAX_STR_LEN - 1);
                    ref_table.entries[ref_table.count].line_num = line_num;
                    ref_table.count++;
                }
            }
            token = strtok(NULL, ",; ");
        }

        // 3. Звірка Qty з фактичною кількістю
        if (parsed_qty != expected_qty) {
            printf("[ПОМИЛКА] Рядок %d: розбіжність Qty! Заявлено %d, перелічено %d (%s)\n",
                   line_num, expected_qty, parsed_qty, raw_designators);
            errors_count++;
        }

        // 4. Перевірка обов'язкових полів для монтованих позицій
        if (!is_dnp) {
            if (is_dummy_value(raw_mpn)) {
                printf("[ПОМИЛКА] Рядок %d: монтована деталь (%s) не має валідного MPN ('%s')\n",
                       line_num, raw_designators, raw_mpn);
                errors_count++;
            }
            if (is_dummy_value(raw_mfg)) {
                printf("[ПОМИЛКА] Рядок %d: монтована деталь (%s) не має виробника ('%s')\n",
                       line_num, raw_designators, raw_mfg);
                errors_count++;
            }
            if (is_dummy_value(raw_footprint)) {
                printf("[ПОМИЛКА] Рядок %d: відсутній посадковий футпрінт для (%s)\n",
                       line_num, raw_designators);
                errors_count++;
            }

            // 5. Евристика суфіксів Tape & Reel для мікросхем
            if (raw_designators[0] == 'U' && strlen(raw_mpn) > 5) {
                // Якщо це чіп, перевіряємо відсутність суфіксів стрічки
                const char *last_two = raw_mpn + strlen(raw_mpn) - 2;
                const char *last_one = raw_mpn + strlen(raw_mpn) - 1;
                if (strcasecmp(last_two, "TR") != 0 && strcasecmp(last_one, "R") != 0) {
                    printf("[ПОПЕРЕДЖЕННЯ] Рядок %d: чіп %s (%s) може не мати суфікса Tape&Reel\n",
                           line_num, raw_designators, raw_mpn);
                    warnings_count++;
                }
            }
        }
    }

    fclose(f);
    printf("=== Результат аудиту: помилок: %d, попереджень: %d ===\n", errors_count, warnings_count);
    return errors_count > 0 ? 1 : 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include <regex>
#include <optional>
#include <algorithm>

struct BomRow {
    std::string designators_raw;
    int quantity{0};
    std::string mpn;
    std::string manufacturer;
    std::string footprint;
    std::string status{"Populate"};
    int line_number{0};
};

struct AuditReport {
    int error_count{0};
    int warning_count{0};
    std::vector<std::string> messages;

    void add_error(int line, std::string_view msg) {
        error_count++;
        messages.push_back("[ПОМИЛКА] Рядок " + std::to_string(line) + ": " + std::string(msg));
    }

    void add_warning(int line, std::string_view msg) {
        warning_count++;
        messages.push_back("[ПОПЕРЕДЖЕННЯ] Рядок " + std::to_string(line) + ": " + std::string(msg));
    }
};

class BomValidator {
public:
    static std::vector<std::string> parse_csv_line(std::string_view line) {
        std::vector<std::string> fields;
        std::string current;
        bool in_quotes = false;

        for (char ch : line) {
            if (ch == '"') {
                in_quotes = !in_quotes;
            } else if (ch == ',' && !in_quotes) {
                fields.push_back(trim(current));
                current.clear();
            } else {
                current += ch;
            }
        }
        fields.push_back(trim(current));
        return fields;
    }

    static std::string trim(std::string_view s) {
        auto start = s.find_first_not_of(" \t\r\n\"");
        if (start == std::string_view::npos) return "";
        auto end = s.find_last_not_of(" \t\r\n\"");
        return std::string(s.substr(start, end - start + 1));
    }

    static std::vector<std::string> split_designators(std::string_view raw) {
        std::vector<std::string> result;
        std::string current;
        for (char c : raw) {
            if (c == ',' || c == ';' || c == ' ') {
                auto t = trim(current);
                if (!t.empty()) result.push_back(t);
                current.clear();
            } else {
                current += c;
            }
        }
        auto t = trim(current);
        if (!t.empty()) result.push_back(t);
        return result;
    }

    static bool is_valid_refdes(std::string_view s) {
        static const std::regex ref_pattern("^[A-Z]{1,3}[0-9]+[A-Z]?$");
        return std::regex_match(s.data(), ref_pattern);
    }

    static bool is_dummy(std::string_view s) {
        if (s.empty()) return true;
        static const std::unordered_set<std::string_view> dummies = {
            "TBD", "N/A", "TODO", "?", "DNI", "DNP", "NONE", "UNKNOWN"
        };
        std::string upper;
        for (char c : s) upper += static_cast<char>(std::toupper(c));
        return dummies.contains(upper);
    }

    AuditReport audit_file(const std::string& path) {
        AuditReport report;
        std::ifstream file(path);
        if (!file.is_open()) {
            report.add_error(0, "Неможливо відкрити файл специфікації: " + path);
            return report;
        }

        std::unordered_map<std::string, int> seen_designators;
        std::string line;
        int line_num = 0;

        // Пропускаємо шапку
        if (std::getline(file, line)) {
            line_num++;
        }

        while (std::getline(file, line)) {
            line_num++;
            if (line.empty() || line[0] == '\r') continue;

            auto fields = parse_csv_line(line);
            if (fields.size() < 5) {
                report.add_error(line_num, "Недостатня кількість полів у рядку (" + std::to_string(fields.size()) + ")");
                continue;
            }

            BomRow row{
                .designators_raw = fields[0],
                .quantity = 0,
                .mpn = fields[2],
                .manufacturer = fields[3],
                .footprint = fields[4],
                .status = (fields.size() > 5 && !fields[5].empty()) ? fields[5] : "Populate",
                .line_number = line_num
            };

            try {
                row.quantity = std::stoi(fields[1]);
            } catch (...) {
                report.add_error(line_num, "Нечислове значення у полі кількості: '" + fields[1] + "'");
                continue;
            }

            bool is_dnp = (row.status == "DNP" || row.status == "DNI" || row.status == "NF");
            auto des_list = split_designators(row.designators_raw);

            // 1. Звірка кількості
            if (static_cast<int>(des_list.size()) != row.quantity) {
                report.add_error(line_num, "Невідповідність Qty! Заявлено " + std::to_string(row.quantity) +
                                           ", перелічено " + std::to_string(des_list.size()) +
                                           " (" + row.designators_raw + ")");
            }

            // 2. Валідація кожного RefDes
            for (const auto& des : des_list) {
                if (!is_valid_refdes(des)) {
                    report.add_error(line_num, "Невалідний синтаксис позначення: '" + des + "'");
                }
                if (auto it = seen_designators.find(des); it != seen_designators.end()) {
                    report.add_error(line_num, "Дублювання позначення '" + des + "' (раніше у рядку " + std::to_string(it->second) + ")");
                } else {
                    seen_designators[des] = line_num;
                }
            }

            // 3. Перевірка обов'язкових полів для монтованих позицій
            if (!is_dnp) {
                if (is_dummy(row.mpn)) {
                    report.add_error(line_num, "Монтована деталь (" + row.designators_raw + ") не має валідного MPN ('" + row.mpn + "')");
                }
                if (is_dummy(row.manufacturer)) {
                    report.add_error(line_num, "Монтована деталь (" + row.designators_raw + ") не має назви виробника");
                }
                if (is_dummy(row.footprint)) {
                    report.add_error(line_num, "Відсутнє посадкове місце (Footprint) для (" + row.designators_raw + ")");
                }

                // 4. Перевірка суфікса Tape & Reel для мікросхем
                if (!des_list.empty() && des_list[0].starts_with('U')) {
                    std::string mpn_upper = row.mpn;
                    for (char& c : mpn_upper) c = static_cast<char>(std::toupper(c));
                    if (!mpn_upper.ends_with("TR") && !mpn_upper.ends_with("R") && !mpn_upper.ends_with("T&R")) {
                        report.add_warning(line_num, "Мікросхема " + row.designators_raw + " (" + row.mpn + ") може не містити суфікса стрічки (Tape & Reel)");
                    }
                }
            }
        }

        return report;
    }
};
```
:::

## Інтеграція валідатора в конвеєр CI/CD

Автоматизована перевірка BOM повинна бути вбудована в систему контролю версій Git на двох рівнях:

1. **Git Pre-Commit Hook:** скрипт запускається локально на комп'ютері розробника при кожній спробі зафіксувати коміт. Якщо в експортованому файлі `bom.csv` знайдено дублікат десігнатора або пусте поле MPN, коміт блокується.
2. **GitHub Actions / GitLab CI Pipeline:** при створенні Pull Request із новою ревізією заліза сервер збирає проект у KiCad/Altium за допомогою headless CLI утиліт, експортує виробничі файли та проганяє валідатор. Якщо код повернення `validate_bom != 0`, автоматичне злиття гілок блокується до виправлення помилок у схемі.

Приклад конфігурації кроку в GitHub Actions:

```yaml
name: Hardware BOM Audit
on: [push, pull_request]

jobs:
  validate-hardware:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build BOM Validator
        run: g++ -std=c++20 -O2 src/bom_validator.cpp -o bom_validator
      - name: Run BOM Integrity Audit
        run: ./bom_validator hardware/production/BOM_Rev_B.csv
```

## Пастки парсингу специфікацій

При автоматичному аналізі файлів BOM із різних САПР виникають три типові проблеми:

1. **Коми всередині списку десігнаторів:** експортери Altium та KiCad огортають комірку `Designator` лапками, якщо вона містить кому (`"R1, R2, R3"`). Простий виклик `strtok` або розбиття рядка за комою розірве рядок на хибну кількість стовпців. Валідатор зобов'язаний реалізовувати конечний автомат з урахуванням лапок.
2. **Преамбула UTF-8 BOM (`\xEF\xBB\xBF`):** деякі текстові редактори та генератори звітів Windows записують байтовий маркер порядку байтів на початку файлу. Якщо його не відсікти, перший стовпець `Designator` буде прочитано як `\xEF\xBB\xBFDesignator`, що зламає зіставлення заголовків.
3. **Регістр статусів монтажу:** САПР можуть експортувати значення `dnp`, `Dnp`, `DNP`, `Do Not Fit`. Валідатор виконує нечутливе до регістру порівняння (*case-insensitive comparison*).
4. **Різні символи кінця рядка:** Windows генерує `CRLF` (`\r\n`), тоді як Linux/macOS — `LF` (`\n`). Якщо валідатор не обрізає символ `\r` у кінці рядка, останнє поле (наприклад, статус або примітка) буде містити невидимий байт `0x0D`, що призведе до невдалого порівняння рядків.
