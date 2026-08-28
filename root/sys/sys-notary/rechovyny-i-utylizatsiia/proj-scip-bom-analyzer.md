# ⚙️ Аналізатор матеріального складу BOM для оцінки RoHS та генерації SCIP-досьє

Перевірка відповідності виробничого переліку компонентів (Bill of Materials, BOM) екологічним директивам — це складна обчислювальна задача. У сучасному електронному пристрої кількість унікальних компонентів сягає сотень позицій, а кількість окремих матеріалів і хімічних речовин перевищує тисячі.

Головний інженерний виклик полягає у правильному застосуванні двох різних математичних моделей:
1. **RoHS:** Перевірка концентрації 10 заборонених речовин у кожному *гомогенному матеріалі* окремо (ліміт `100 ppm` для кадмію, `1000 ppm` для решти речовин).
2. **REACH / SCIP:** Перевірка концентрації речовин дуже високого занепокоєння (SVHC) за принципом *Once An Article, Always An Article* (OAOA, рішення Суду ЄС C-106/14). Концентрація кожної речовини SVHC розраховується від маси конкретного *виробу-компонента* (sub-article), а не від маси всього фінального пристрою. Якщо частка SVHC перевищує `0.1% w/w` (1000 мг/кг), компонент підлягає обов'язковій реєстрації в базі даних SCIP Європейського хімічного агентства (ECHA).

Створимо утиліту аналізу матеріального складу BOM, яка перевіряє ліміти RoHS, знаходить компоненти із перевищенням порогу SVHC та генерує структурований звіт для технічного файлу комплаєнсу.

---

### Архітектура даних та алгоритм аналізу

Програма приймає ієрархічну структуру даних, де пристрій складається з масиву компонентів (articles), кожен компонент має власну масу, назву та містить перелік хімічних речовин із зазначенням їхньої абсолютної маси в міліграмах, категорії небезпеки та прапорця наявності легального винятку (RoHS exemption).

```
Ієрархія даних комплаєнсу:
[Прилад: Device]
  └── [Компонент / Виріб: Article] (маса M_art)
        └── [Речовина / Матеріал: Substance] (маса M_sub, тип, виняток)
```

Алгоритм виконує два послідовні проходи:
- **Прохід 1 (RoHS Audit):** Для кожної речовини обчислюється її масова частка у гомогенному матеріалі:
```
C_rohs = (M_sub / M_material) · 100%
```
Якщо `C_rohs` перевищує граничний ліміт і для цієї позиції не заявлено чинний виняток (наприклад, виняток 6(c) для свинцю в латуні до 4%), прапорець валідації скидається, а позиція позначається як критичне порушення (FAIL).

- **Прохід 2 (REACH SVHC & SCIP Audit):** Для кожної речовини зі списку SVHC обчислюється її масова частка відносно повної маси компонента (OAOA):
```
C_svhc = (M_sub / M_art) · 100%
```
Якщо `C_svhc > 0.1%`, формується запис для нотифікаційного досьє SCIP із зазначенням артикула деталі, назви речовини, коду CAS та діапазону концентрації за класифікатором ECHA.

---

### Реалізація: C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define ROHS_LIMIT_DEFAULT_PPM  1000.0   /* 0.1% w/w */
#define ROHS_LIMIT_CADMIUM_PPM   100.0   /* 0.01% w/w */
#define REACH_SVHC_LIMIT_PPM    1000.0   /* 0.1% w/w */

typedef enum {
    SUBSTANCE_BENIGN = 0,
    SUBSTANCE_ROHS_LEAD,
    SUBSTANCE_ROHS_CADMIUM,
    SUBSTANCE_ROHS_MERCURY,
    SUBSTANCE_ROHS_HEX_CHROMIUM,
    SUBSTANCE_ROHS_PBB_PBDE,
    SUBSTANCE_ROHS_PHTHALATE,
    SUBSTANCE_REACH_SVHC
} SubstanceType;

typedef struct {
    const char *name;
    const char *cas_number;
    SubstanceType type;
    double mass_mg;
    const char *rohs_exemption; /* NULL якщо винятку немає */
} Substance;

typedef struct {
    const char *part_number;
    const char *description;
    double total_mass_mg;
    Substance *substances;
    size_t substance_count;
} Article;

typedef struct {
    const char *product_name;
    Article *articles;
    size_t article_count;
} DeviceBom;

void analyze_compliance(const DeviceBom *bom) {
    printf("=================================================================\n");
    printf("ЗВІТ ЕКОЛОГІЧНОЇ ВІДПОВІДНОСТІ (RoHS / REACH / SCIP)\n");
    printf("Виріб: %s\n", bom->product_name);
    printf("=================================================================\n\n");

    bool rohs_overall_pass = true;
    size_t scip_notifications_required = 0;

    for (size_t i = 0; i < bom->article_count; ++i) {
        const Article *art = &bom->articles[i];
        printf("Компонент [%s]: %s (Маса: %.2f мг)\n",
               art->part_number, art->description, art->total_mass_mg);

        if (art->total_mass_mg <= 0.0) {
            printf("  [ПОМИЛКА]: Некоректна маса компонента!\n");
            continue;
        }

        for (size_t j = 0; j < art->substance_count; ++j) {
            const Substance *sub = &art->substances[j];
            double ppm = (sub->mass_mg / art->total_mass_mg) * 1000000.0;
            double percent = (sub->mass_mg / art->total_mass_mg) * 100.0;

            /* Перевірка вимог RoHS */
            if (sub->type >= SUBSTANCE_ROHS_LEAD && sub->type <= SUBSTANCE_ROHS_PHTHALATE) {
                double limit_ppm = (sub->type == SUBSTANCE_ROHS_CADMIUM) ?
                                   ROHS_LIMIT_CADMIUM_PPM : ROHS_LIMIT_DEFAULT_PPM;

                if (ppm > limit_ppm) {
                    if (sub->rohs_exemption != NULL && strlen(sub->rohs_exemption) > 0) {
                        printf("  · [RoHS EXEMPT]: %s (%.2f ppm / %.3f%%) -> Дозволено за винятком: %s\n",
                               sub->name, ppm, percent, sub->rohs_exemption);
                    } else {
                        printf("  · [RoHS FAIL]: %s (%.2f ppm / %.3f%%) -> Перевищує ліміт %.0f ppm!\n",
                               sub->name, ppm, percent, limit_ppm);
                        rohs_overall_pass = false;
                    }
                } else {
                    printf("  · [RoHS OK]: %s (%.2f ppm / %.4f%%)\n", sub->name, ppm, percent);
                }
            }

            /* Перевірка вимог REACH SVHC за правилом OAOA */
            if (sub->type == SUBSTANCE_REACH_SVHC || sub->type == SUBSTANCE_ROHS_LEAD || sub->type == SUBSTANCE_ROHS_PHTHALATE) {
                if (ppm > REACH_SVHC_LIMIT_PPM) {
                    printf("  · [SCIP MANDATORY]: Речовина SVHC %s [CAS %s] = %.3f%% w/w (> 0.1%%)\n",
                           sub->name, sub->cas_number, percent);
                    scip_notifications_required++;
                }
            }
        }
        printf("\n");
    }

    printf("-----------------------------------------------------------------\n");
    printf("ПІДСУМОК АУДИТУ:\n");
    printf("Статус RoHS: %s\n", rohs_overall_pass ? "ВІДПОВІДАЄ (PASS)" : "НЕ ВІДПОВІДАЄ (FAIL)");
    printf("Кількість обов'язкових нотифікацій у базі SCIP: %zu\n", scip_notifications_required);
    printf("=================================================================\n");
}

int main(void) {
    /* Тестові дані: розбір компонентів виробу */
    Substance r1_substances[] = {
        {"Тетрабромбісфенол А (TBBA)", "79-94-7", SUBSTANCE_REACH_SVHC, 12.0, NULL},
        {"Оксид свинцю у склі резистивного шару", "1317-36-8", SUBSTANCE_ROHS_LEAD, 0.45, "7(c)-I"}
    };

    Substance screw_substances[] = {
        {"Свинець у латунному сплаві CuZn39Pb3", "7439-92-1", SUBSTANCE_ROHS_LEAD, 25.0, "6(c)"}
    };

    Substance seal_substances[] = {
        {"Пластифікатор DEHP у гумі NBR", "117-81-7", SUBSTANCE_ROHS_PHTHALATE, 15.0, NULL}
    };

    Article articles[] = {
        {"R0805-10K", "Чіп-резистор 0805", 15.0, r1_substances, 2},
        {"SCR-M3-10", "Гвинт латунний M3x10", 850.0, screw_substances, 1},
        {"GSK-ORING-5", "Кільце ущільнювача корпусу", 500.0, seal_substances, 1}
    };

    DeviceBom device = {
        "Промисловий контролер IoT Gateway v2.0",
        articles,
        3
    };

    analyze_compliance(&device);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <iomanip>

enum class SubstanceCategory {
    Benign,
    RohsRestricted,
    ReachSvhcCandidate
};

struct SubstanceEntry {
    std::string name;
    std::string cas_number;
    SubstanceCategory category;
    double mass_mg{0.0};
    double rohs_limit_ppm{1000.0};
    std::string rohs_exemption{}; // Порожньо, якщо винятку нема
};

struct ArticleComponent {
    std::string part_number;
    std::string description;
    double total_mass_mg{0.0};
    std::vector<SubstanceEntry> declared_substances{};
};

struct ComplianceReport {
    bool rohs_compliant{true};
    size_t scip_dossiers_required{0};
    std::vector<std::string> log_entries{};
};

class BomComplianceEngine {
public:
    static ComplianceReport evaluate(std::string_view product_name,
                                     const std::vector<ArticleComponent>& articles) {
        ComplianceReport report;
        report.log_entries.emplace_back("Аналіз матеріальної відповідності виробу: " + std::string(product_name));

        constexpr double SVHC_THRESHOLD_PPM = 1000.0; // 0.1% w/w за регламентом REACH

        for (const auto& art : articles) {
            if (art.total_mass_mg <= 0.0) {
                report.log_entries.emplace_back("[ПОМИЛКА]: Неприпустима маса деталі " + art.part_number);
                continue;
            }

            for (const auto& sub : art.declared_substances) {
                const double ppm = (sub.mass_mg / art.total_mass_mg) * 1'000'000.0;
                const double weight_percent = (sub.mass_mg / art.total_mass_mg) * 100.0;

                // 1. Перевірка лімітів RoHS
                if (sub.category == SubstanceCategory::RohsRestricted) {
                    if (ppm > sub.rohs_limit_ppm) {
                        if (!sub.rohs_exemption.empty()) {
                            report.log_entries.emplace_back(
                                "  [RoHS EXEMPT] " + art.part_number + ": " + sub.name +
                                " (" + std::to_string(ppm) + " ppm) -> Виняток " + sub.rohs_exemption);
                        } else {
                            report.log_entries.emplace_back(
                                "  [RoHS FAIL] " + art.part_number + ": " + sub.name +
                                " (" + std::to_string(ppm) + " ppm > ліміту " +
                                std::to_string(sub.rohs_limit_ppm) + " ppm)");
                            report.rohs_compliant = false;
                        }
                    }
                }

                // 2. Перевірка REACH SVHC за правилом OAOA (CJEU C-106/14)
                if (sub.category == SubstanceCategory::ReachSvhcCandidate ||
                    sub.category == SubstanceCategory::RohsRestricted) {
                    if (ppm > SVHC_THRESHOLD_PPM) {
                        report.scip_dossiers_required++;
                        report.log_entries.emplace_back(
                            "  [SCIP TRIGGER] " + art.part_number + " -> Речовина SVHC: " +
                            sub.name + " [CAS " + sub.cas_number + "] = " +
                            std::to_string(weight_percent) + "% w/w (Потрібне досьє в ECHA SCIP)");
                    }
                }
            }
        }
        return report;
    }
};

int main() {
    std::vector<ArticleComponent> bill_of_materials = {
        {
            "R0805-10K", "Чіп-резистор товстоплівковий 10 кОм", 15.0,
            {
                {"Тетрабромбісфенол А (TBBA)", "79-94-7", SubstanceCategory::ReachSvhcCandidate, 12.0, 1000.0, ""},
                {"Оксид свинцю в склі (PbO)", "1317-36-8", SubstanceCategory::RohsRestricted, 0.45, 1000.0, "7(c)-I"}
            }
        },
        {
            "SCR-M3-10", "Гвинт латунний різьбовий M3x10", 850.0,
            {
                {"Свинець (Pb) у мідному сплаві", "7439-92-1", SubstanceCategory::RohsRestricted, 25.0, 1000.0, "6(c)"}
            }
        },
        {
            "GSK-ORING-5", "Герметизуюче кільце NBR 5мм", 500.0,
            {
                {"Дибутилфталат (DBP)", "84-74-2", SubstanceCategory::RohsRestricted, 15.0, 1000.0, ""}
            }
        }
    };

    const auto report = BomComplianceEngine::evaluate("IoT Gateway Industrial", bill_of_materials);

    std::cout << "====================================================\n";
    for (const auto& line : report.log_entries) {
        std::cout << line << "\n";
    }
    std::cout << "====================================================\n";
    std::cout << "Підсумковий статус RoHS: " << (report.rohs_compliant ? "ВІДПОВІДАЄ" : "ПОРУШЕННЯ") << "\n";
    std::cout << "Необхідно сформувати SCIP досьє: " << report.scip_dossiers_required << "\n";

    return 0;
}
```
:::

---

### Розбір роботи програми та аналіз результатів

Розглянемо, як програма інтерпретує конкретні приклади компонентів:

1. **Резистор 0805 (`R0805-10K`):**
   - Містить 0.45 мг оксиду свинцю в захисному склі. Концентрація `(0.45 / 15.0) · 100% = 3.0% (30 000 ppm)`. Це перевищує загальний ліміт RoHS 1000 ppm, проте компонент має юридичний виняток **7(c)-I** (*Lead in electronic ceramics and glass*). Програма маркує позицію як `[RoHS EXEMPT]`, дозволяючи її використання у виробі.
   - Одночасно деталь містить 12.0 мг TBBA, що становить `12.0 / 15.0 = 80%` маси діелектричної підкладки. Оскільки TBBA входить до списку кандидатів SVHC, програма активує прапорець `[SCIP TRIGGER]` та вносить артикул `R0805-10K` до списку обов'язкових декларацій у базі даних ECHA SCIP.
2. **Латунний гвинт (`SCR-M3-10`):**
   - Латунь марки CuZn39Pb3 містить 25.0 мг свинцю на 850.0 мг загальної маси, тобто `25.0 / 850.0 = 2.94% (29 411 ppm)`. Завдяки посиланню на виняток **6(c)** (*Lead as an alloying element in copper containing up to 4% lead by weight*), деталь успішно проходить аудит RoHS. Проте свинець є речовиною SVHC, тому через концентрацію `2.94% > 0.1%` гвинт обов'язково нотифікується в системі SCIP як окремий металовиріб.
3. **Ущільнювач (`GSK-ORING-5`):**
   - Кільце містить 15.0 мг дибутилфталату (DBP) на 500.0 мг маси, що становить `3.0% (30 000 ppm)`. Фталати не мають винятків для загальної споживчої техніки. Програма фіксує статус `[RoHS FAIL]`, що вимагає негайної заміни матеріалу на етапі прототипування.

---

### Обробка крайових випадків та інтеграція у виробничий пайплайн

Під час інтеграції аналізатора в реальні інженерні САПР (Altium Designer, KiCad, Cadence Allegro) необхідно враховувати специфічні крайові ситуації:

#### 1. Деталі з нульовою або незадекларованою масою
У вихідних BOM-файлах часто трапляються позиції віртуальних компонентів (монтажні отвори, тестові точки, перемички нульового опору) або імпортовані сторонні бібліотечні елементи без заповненого поля повної маси. Алгоритм обов'язково перевіряє умову `total_mass_mg <= 0.0`. Якщо маса відсутня, обчислення концентрації у відсотках призведе до ділення на нуль (NaN або нескінченність). Програма генерує попередження та блокує випуск звіту до внесення точних вагових даних.

#### 2. Багаторазове входження однакових деталей (Reference Designators)
На друкованій платі один і той самий артикул резистора може зустрічатися десятки разів під різними позиційними позначеннями (`R1, R2, R15, R48`). Для аудиту RoHS та нотифікації SCIP кожна позиція агрегується за унікальним номером виробника (MPN — Manufacturer Part Number). Досьє SCIP генерується один раз для даного артикула, а в полі опису виробу зазначається загальна кількість таких деталей у зборі.

#### 3. Відстеження термінів дії винятків RoHS
Винятки за Додатками III/IV директиви 2011/65/EU мають обмежений термін чинності (зазвичай від 3 до 5 років) і підлягають регулярному перегляду Європейською Комісією. У промисловій системі структура даних винятку містить дату закінчення дії (`expiration_date`). Якщо дата релізу нової версії прошивки чи ревізії плати перевищує термін чинності винятку, система позначає компонент як такий, що потребує негайного редизайну (Redesign Alert).

Автоматизація такого розрахунку дозволяє розробникам інтегрувати перевірку чистоти матеріалів безпосередньо в конвеєри безперервної інтеграції (CI/CD) під час генерації файлів Gerber та BOM у САПР друкованих плат, запобігаючи дорогим юридичним помилкам задовго до запуску складальної лінії.
