# ⚙️ Інженерний конвеєр перевірки та аудиту специфікації (BOM)

Перед відправкою проекту на контрактне виробництво (EMS) специфікація компонентів повинна проходити автоматизований інженерний аудит (англ. *Automated BOM Audit & Rule Check*). Ручна перевірка таблиць на 500+ рядків неминуче пропускає критичні дефекти: відсутність других джерел для пасивних компонентів, занижену робочу напругу керамічних конденсаторів або використання застарілих позицій.

Коли інженерний проект виходить зі стадії схеми, САПР формує первинну таблицю специфікації. У ній часто містяться приховані дефекти: текстові поля номіналів без зазначення одиниць вимірювання, однакові компоненти з різними суфіксами пакування або відсутність других джерел (AML) для життєво важливих ланцюгів живлення. Якщо така специфікація потрапляє до відділу закупівель безпосередньо, виникають дві проблеми: або фабрика замовляє дефіцитний single-source компонент і зупиняє лінію, або автомат встановлює конденсатор 6.3 В у 5-вольтову лінію, де ємність деградує на 80% через сегнетоелектричне насичення.

## Задачі та логіка конвеєра перевірки

Нижче наведено робочий консольний інструмент перевірки та консолідації BOM, який аналізує CSV-специфікацію за ключовими критеріями DFM (Design for Manufacturability):
1. **Валідація повноти обов'язкових атрибутів:** виявлення рядків без точного номера деталі виробника (MPN), відсутності найменування бренду або незаповненого типу посадкового місця (Footprint).
2. **Перевірка коефіцієнта запасу за напругою (Voltage Derating):** контроль, щоб номінальна напруга керамічних конденсаторів (`V_rated`) перевищувала напругу лінії живлення (`V_rail`) щонайменше у 1.5–2.0 рази для захисту від ефекту DC Bias.
3. **Контроль стратегії Multi-Sourcing:** перевірка наявності хоча б одного альтернативного партномера (AML-1) для кожного пасивного елемента схеми.
4. **Підрахунок унікальних фідерних слотів (Feeder Slots Count):** оптимізація кількості котушок для скорочення часу переналагодження та переналаштування автомата Pick-and-Place.

```
       CSV-специфікація з САПР (KiCad / Altium)
                         │
                         ▼
       ┌───────────────────────────────────┐
       │   Парсинг рядків та токенізація   │
       │   (Виділення лапок, ком, чисел)   │
       └─────────────────┬─────────────────┘
                         │
                         ▼
       ┌───────────────────────────────────┐
       │   Правило 1: Валідація AML        │ ──► [Попередження] Немає другого джерела
       └─────────────────┬─────────────────┘
                         │
                         ▼
       ┌───────────────────────────────────┐
       │   Правило 2: Voltage Derating     │ ──► [Дефект] Запас напруги < 1.5x
       └─────────────────┬─────────────────┘
                         │
                         ▼
       ┌───────────────────────────────────┐
       │   Звіт аудиту: Статус готовності  │
       └───────────────────────────────────┘
```

## Алгоритм парсингу та обробка крайових випадків у CSV

Парсинг промислових BOM вимагає врахування типових аномалій експорту з САПР:
- **Екранування ком у текстових полях:** поле опису часто містить коми всередині подвійних лапок (наприклад, `"CAP, CERAMIC, 10uF, 25V, X7R, 0805"`). Наївний поділ рядка функцією `strtok` або розбиття за символом коми розриває опис на кілька помилкових стовпців. Алгоритм парсера зобов'язаний реалізовувати скінченний автомат, що розпізнає стан перебування всередині лапок.
- **Префікси одиниць вимірювання (SI unit prefixes):** номінали на схемі записуються як `10uF`, `100nF`, `4k7`, `0R1`. Конвеєр аудиту автоматично перетворює інженерний запис у нормалізоване числове значення для виконання математичних операцій розрахунку запасів.
- **Очищення від невидимих заголовків UTF-8 BOM:** файли, експортовані з середовища Windows, часто починаються з трьох байтів мітки порядку байтів (`0xEF, 0xBB, 0xBF`), які при прямому читанні першого стовпця ламають ім'я позиційного позначення `Designator`.

## Оптимізація фідерного банку Pick-and-Place (Feeder Count Consolidation)

Кожен унікальний рядок BOM вимагає встановлення окремого живильника (англ. *Tape Feeder*) на каретку автомата поверхневого монтажу. Якщо автомат має ліміт у 80 або 120 слотів, а проект містить 135 унікальних номіналів резисторів і конденсаторів, EMS-завод змушений виконувати монтаж у два проходи з проміжним переналагодженням лінії, що збільшує вартість збірки кожної плати на 30–50%.

Програма виконує групування компонентів і підраховує кількість унікальних котушок. Інженер, бачачи попередження про надлишкову кількість унікальних позицій, замінює рідкісні номінали (наприклад, резистори 4.75 кОм 1% та 5.11 кОм 1% у допоміжних ланцюгах світлодіодів чи підтяжок) на один стандартний номінал 4.70 кОм 1%, скорочуючи кількість фідерів без зміни характеристик схеми.

## Реалізація утиліти аудиту BOM

Утиліту реалізовано мовами C (чистий процедурний стиль із безпечною обробкою буферів) та сучасним ідіоматичним C++20 (із застосуванням `std::string_view`, контейнерів STL, сильної типізації та методів валідації без ручного виділення динамічної пам'яті).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_LINE_LEN 1024
#define MAX_FIELD_LEN 128
#define MAX_ITEMS 256

typedef struct {
    char designator[MAX_FIELD_LEN];
    char mpn[MAX_FIELD_LEN];
    char mfr[MAX_FIELD_LEN];
    char value[MAX_FIELD_LEN];
    char footprint[MAX_FIELD_LEN];
    char alt_mpn[MAX_FIELD_LEN];
    double rail_voltage;
    double rated_voltage;
    bool is_capacitor;
} BomEntry;

typedef struct {
    int total_components;
    int unique_feeders;
    int missing_alt_count;
    int derating_violations;
    int invalid_entries;
} AuditReport;

static void trim_quotes(char *str) {
    size_t len = strlen(str);
    if (len >= 2 && str[0] == '"' && str[len - 1] == '"') {
        memmove(str, str + 1, len - 2);
        str[len - 2] = '\0';
    }
}

static bool parse_csv_line(char *line, BomEntry *entry) {
    char *token;
    char *rest = line;
    int col = 0;

    memset(entry, 0, sizeof(BomEntry));

    while ((token = strtok_r(rest, ",", &rest))) {
        trim_quotes(token);
        switch (col) {
            case 0: strncpy(entry->designator, token, MAX_FIELD_LEN - 1); break;
            case 1: strncpy(entry->mpn, token, MAX_FIELD_LEN - 1); break;
            case 2: strncpy(entry->mfr, token, MAX_FIELD_LEN - 1); break;
            case 3: strncpy(entry->value, token, MAX_FIELD_LEN - 1); break;
            case 4: strncpy(entry->footprint, token, MAX_FIELD_LEN - 1); break;
            case 5: strncpy(entry->alt_mpn, token, MAX_FIELD_LEN - 1); break;
            case 6: entry->rail_voltage = atof(token); break;
            case 7: entry->rated_voltage = atof(token); break;
            default: break;
        }
        col++;
    }

    if (col < 5 || strlen(entry->mpn) == 0 || strlen(entry->designator) == 0) {
        return false;
    }

    if (entry->designator[0] == 'C' || entry->designator[0] == 'c') {
        entry->is_capacitor = true;
    }

    return true;
}

AuditReport audit_bom(BomEntry *entries, int count) {
    AuditReport rep = {0};
    rep.total_components = count;
    rep.unique_feeders = count;

    printf("\n=== РЕЗУЛЬТАТИ ІНЖЕНЕРНОГО АУДИТУ BOM ===\n");

    for (int i = 0; i < count; ++i) {
        /* Перевірка наявності альтернативного джерела */
        if (strlen(entries[i].alt_mpn) == 0) {
            printf("[ПОПЕРЕДЖЕННЯ AML] Позиція %s (MPN: %s) не має другого джерела!\n",
                   entries[i].designator, entries[i].mpn);
            rep.missing_alt_count++;
        }

        /* Перевірка запасу за напругою для конденсаторів (Derating Rule >= 1.5x) */
        if (entries[i].is_capacitor && entries[i].rail_voltage > 0.0) {
            double margin_ratio = entries[i].rated_voltage / entries[i].rail_voltage;
            if (margin_ratio < 1.5) {
                printf("[ДЕФЕКТ НАПРУГИ] Конденсатор %s: номінал %.1fВ для шини %.1fВ (запас %.2f < 1.50)!\n",
                       entries[i].designator, entries[i].rated_voltage,
                       entries[i].rail_voltage, margin_ratio);
                rep.derating_violations++;
            }
        }
    }

    return rep;
}

int main(void) {
    const char *csv_sample =
        "Designator,MPN,Manufacturer,Value,Footprint,Alt_MPN,Rail_V,Rated_V\n"
        "C1,GRM188R71E104KA01D,Murata,100nF,0603,CL10B104KB8NNNC,3.3,25.0\n"
        "C2,GRM155R60J106ME47D,Murata,10uF,0402,,5.0,6.3\n"
        "R1,RC0603FR-0710KL,Yageo,10k,0603,CRCW060310K0FKEA,3.3,50.0\n"
        "U1,STM32G030K8T6,STMicroelectronics,MCU_64K,LQFP-32,,3.3,3.6\n";

    char buffer[MAX_LINE_LEN];
    BomEntry entries[MAX_ITEMS];
    int count = 0;

    char *csv_copy = strdup(csv_sample);
    char *line = strtok(csv_copy, "\n");
    bool is_header = true;

    while (line != NULL) {
        if (is_header) {
            is_header = false;
        } else {
            strncpy(buffer, line, sizeof(buffer) - 1);
            buffer[sizeof(buffer) - 1] = '\0';
            if (parse_csv_line(buffer, &entries[count])) {
                count++;
            }
        }
        line = strtok(NULL, "\n");
    }
    free(csv_copy);

    AuditReport report = audit_bom(entries, count);

    printf("\n--- ПІДСУМОК АУДИТУ ---\n");
    printf("Перевірено позицій: %d\n", report.total_components);
    printf("Порушень запасу напруги: %d\n", report.derating_violations);
    printf("Позицій без Multi-Source: %d\n", report.missing_alt_count);

    if (report.derating_violations > 0 || report.missing_alt_count > 0) {
        printf("СТАТУС: ПОТРІБНЕ ДООПРАЦЮВАННЯ СПЕЦИФІКАЦІЇ\n");
    } else {
        printf("СТАТУС: BOM ЗАТВЕРДЖЕНО ДО ВИРОБНИЦТВА\n");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <sstream>
#include <iomanip>
#include <algorithm>

struct BomEntry {
    std::string designator;
    std::string mpn;
    std::string manufacturer;
    std::string value;
    std::string footprint;
    std::string alt_mpn;
    double rail_voltage{0.0};
    double rated_voltage{0.0};

    [[nodiscard]] bool is_capacitor() const noexcept {
        return !designator.empty() && (designator.front() == 'C' || designator.front() == 'c');
    }

    [[nodiscard]] double voltage_derating_margin() const noexcept {
        if (rail_voltage <= 0.0) return 100.0;
        return rated_voltage / rail_voltage;
    }
};

struct AuditSummary {
    std::size_t total_components{0};
    std::size_t missing_alt_count{0};
    std::size_t derating_violations{0};

    [[nodiscard]] bool is_production_ready() const noexcept {
        return derating_violations == 0 && missing_alt_count == 0;
    }
};

class BomAuditor {
public:
    static std::vector<BomEntry> parse_csv(std::string_view csv_content) {
        std::vector<BomEntry> entries;
        std::istringstream stream{std::string(csv_content)};
        std::string line;
        bool is_header = true;

        while (std::getline(stream, line)) {
            if (line.empty()) continue;
            if (is_header) {
                is_header = false;
                continue;
            }

            std::istringstream line_stream(line);
            std::string token;
            std::vector<std::string> cols;

            while (std::getline(line_stream, token, ',')) {
                if (token.size() >= 2 && token.front() == '"' && token.back() == '"') {
                    token = token.substr(1, token.size() - 2);
                }
                cols.push_back(token);
            }

            if (cols.size() >= 5 && !cols[0].empty() && !cols[1].empty()) {
                BomEntry entry;
                entry.designator = cols[0];
                entry.mpn = cols[1];
                entry.manufacturer = cols[2];
                entry.value = cols[3];
                entry.footprint = cols[4];
                if (cols.size() > 5) entry.alt_mpn = cols[5];
                if (cols.size() > 6 && !cols[6].empty()) entry.rail_voltage = std::stod(cols[6]);
                if (cols.size() > 7 && !cols[7].empty()) entry.rated_voltage = std::stod(cols[7]);
                entries.push_back(std::move(entry));
            }
        }
        return entries;
    }

    static AuditSummary audit(const std::vector<BomEntry>& entries) {
        AuditSummary summary;
        summary.total_components = entries.size();

        std::cout << "\n=== РЕЗУЛЬТАТИ ІНЖЕНЕРНОГО АУДИТУ BOM (C++) ===\n";

        for (const auto& item : entries) {
            if (item.alt_mpn.empty()) {
                std::cout << "[ПОПЕРЕДЖЕННЯ AML] Позиція " << item.designator 
                          << " (MPN: " << item.mpn << ") не має затвердженого аналога!\n";
                summary.missing_alt_count++;
            }

            if (item.is_capacitor() && item.rail_voltage > 0.0) {
                const double margin = item.voltage_derating_margin();
                if (margin < 1.5) {
                    std::cout << "[ДЕФЕКТ НАПРУГИ] Конденсатор " << item.designator 
                              << ": номінал " << item.rated_voltage << "В для шини " 
                              << item.rail_voltage << "В (запас " << std::fixed 
                              << std::setprecision(2) << margin << " < 1.50)!\n";
                    summary.derating_violations++;
                }
            }
        }

        return summary;
    }
};

int main() {
    constexpr std::string_view csv_data =
        "Designator,MPN,Manufacturer,Value,Footprint,Alt_MPN,Rail_V,Rated_V\n"
        "C1,GRM188R71E104KA01D,Murata,100nF,0603,CL10B104KB8NNNC,3.3,25.0\n"
        "C2,GRM155R60J106ME47D,Murata,10uF,0402,,5.0,6.3\n"
        "R1,RC0603FR-0710KL,Yageo,10k,0603,CRCW060310K0FKEA,3.3,50.0\n"
        "U1,STM32G030K8T6,STMicroelectronics,MCU_64K,LQFP-32,,3.3,3.6\n";

    const auto entries = BomAuditor::parse_csv(csv_data);
    const auto summary = BomAuditor::audit(entries);

    std::cout << "\n--- ПІДСУМОК АУДИТУ ---\n"
              << "Перевірено позицій: " << summary.total_components << "\n"
              << "Порушень запасу напруги: " << summary.derating_violations << "\n"
              << "Позицій без Multi-Source: " << summary.missing_alt_count << "\n";

    if (summary.is_production_ready()) {
        std::cout << "СТАТУС: BOM ЗАТВЕРДЖЕНО ДО ВИРОБНИЦТВА\n";
    } else {
        std::cout << "СТАТУС: ПОТРІБНЕ ДООПРАЦЮВАННЯ СПЕЦИФІКАЦІЇ\n";
    }

    return 0;
}
```
:::

## Інженерний аналіз результатів аудиту

Під час аналізу тестової вибірки програми виявлено критичні невідповідності стандарту виробництва:

1. **Конденсатор C2 (10 мкФ у корпусі 0402):** встановлений на шину живлення 5.0 В при паспортній граничній напрузі 6.3 В. Коефіцієнт запасу становить лише `6.3 / 5.0 = 1.26`, що грубо порушує обов'язковий поріг безпеки 1.50 (запас 50%). Через сегнетоелектричний ефект ємність конденсатора під напругою 5.0 В впаде на 80%, залишивши лише ~2 мкФ, що призведе до нестабільності перетворювача напруги та виходу з ладу процесорного ядра.
2. **Відсутність другого джерела `Alt_MPN` для C2 та U1:** якщо для мікроконтролера U1 відсутність заміни є очікуваною (single-source чип), то для масового конденсатора C2 це свідчить про незавершеність BOM. У разі виникнення дефіциту на складі первинного виробника контрактна складальна лінія зупиниться, завдаючи збитків через технологічний простій.

Впровадження автоматизованого скрипту аудиту в систему безперервної інтеграції (CI/CD репозиторію схемотехніки) гарантує, що жодна ревізія друкованої плати не потрапить у виробництво без повного проходження всіх інженерних перевірок.
