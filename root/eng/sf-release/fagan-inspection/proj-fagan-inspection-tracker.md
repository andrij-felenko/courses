# ⚙️ Система ведення протоколів інспекції Фагана та метрик дефектів

Система ведення протоколів інспекції Фагана забезпечує структуровану реєстрацію знахідок під час верифікації апаратних схем і вбудованого коду, автоматичний розрахунок темпу вичитування, щільності дефектів та обчислення критеріїв повторної інспекції. Без централізованого обліку метрик формальний аудит перетворюється на хаотичний збір усних зауважень, де неможливо об'єктивно оцінити якість артефакту та готовність системи до запуску у виробництво.

## Архітектура та модель даних інспекційного протоколу

Формальний процес аудиту спирається на суворе розмежування типів дефектів, фаз виявлення та метрик навантаження на команду. Модель даних побудована навколо чотирьох ключових сутностей: сесії інспекції, зареєстрованого дефекту, параметрів вимірювання артефакту та фінального звіту про проходження критеріїв виходу.

Сесія інспекції фіксує повні метадані артефакту, що проходить перевірку: назву програмного модуля (наприклад, низькорівневий драйвер контролера прямого доступу до пам'яті DMA) чи ревізію апаратної принципової електричної схеми вузла живлення процесорного ядра. Додатково фіксуються ревізія у системі контролю версій або номер ревізії трасування друкованої плати, персональний склад учасників засідання з чітким розподілом ролей (модератор, автор артефакту, читець та інспектори-експерти), а також облік трудовитрат. Окремо фіксується час, витрачений кожним інспектором на етапі індивідуального вичитування (у людино-годинах), і тривалість очного пленарного засідання (у хвилинах).

Кожен зареєстрований дефект описується фіксованим набором атрибутів, що унеможливлює двозначне трактування зауваження:

1. **Рівень критичності (Severity):**
   - `CRITICAL` (Блокувальний / Критичний): дефект, який за умови потрапляння у фізичний пристрій призводить до незворотного апаратного пошкодження компонентів (наприклад, короткого замикання через одночасне відкриття верхнього та нижнього ключів напівмоста), зависання ядра процесора в нескінченному циклі обробника переривань (ISR), мертвого блокування (deadlock) між критичними секціями або неконтрольованого руйнування стек-фрейму з перетиранням таблиці векторів переривань. Наявність хоча б одного такого дефекту безумовно блокує випуск артефакту та вимагає обов'язкової повторної сесії інспекції після доопрацювання.
   - `MAJOR` (Значний): функціональна невідповідність затвердженим технічним вимогам або специфікації протоколу обміну, яка не викликає фізичного руйнування апаратури, але порушує цілісність даних чи логіку роботи. Прикладами є некоректне обчислення полінома контрольної суми CRC, порушення таймінгів шини даних без пошкодження драйверів лінії, втрата окремих пакетів у кільцевому буфері під навантаженням або відсутність тайм-ауту при очікуванні готовності апаратного периферійного модуля.
   - `MINOR` (Незначний): локальні відхилення від галузевих стандартів кодування та оформлення схемотехнічної документації, які не впливають безпосередньо на виконання функціональних завдань у штатному режимі. До цієї категорії належать порушення правил стандарту MISRA C / MISRA C++, відсутність маркування тестових контрольних точок на схемі, неоптимальний номінал блокувального конденсатора, що залишає пульсації живлення в допустимому коридорі, або невідповідність корпоративним правилам найменування змінних та сигнальних трас.

2. **Категорія виникнення дефекту (Category):**
   - `LOGIC` (Логіка та алгоритмічна коректність): помилки в математичних розрахунках, некоректні умови виходу з циклічних конструкцій, пропущені гілки умовних переходів `switch-case`, неперевірені значення змінних перед використанням.
   - `CONCURRENCY` (Конкурентність та обробка переривань): неатомарний доступ до спільних багатобайтових структур даних між фоновим циклом `main()` та асинхронними обробниками переривань, пропущені кваліфікатори `volatile` для сигнальних змінних стану, блокуючі затримки всередині контексту переривань, відсутність апаратних бар'єрів пам'яті (memory barriers).
   - `HW_INTERFACE` (Апаратний інтерфейс та схемотехніка): висячі цифрові входи без внутрішньої або зовнішньої підтяжки (floating inputs), відсутність підтягувальних резисторів на лініях з відкритим стоком шин I2C, перевищення гранично допустимого вихідного струму виводів GPIO, некоректна послідовність подачі напруг живлення ядра та периферії (power sequencing).
   - `RESOURCE_SAFETY` (Безпека ресурсів та меж): переповнення статичних або кільцевих буферів, неконтрольоване зростання глибини викликів функцій, що загрожує переповненням апаратного стека мікроконтролера, некоректне приведення типів вказівників із порушенням правил суворого псевдонімування (strict aliasing).
   - `STANDARDS_COMPLIANCE` (Відповідність стандартам безпеки): порушення обов'язкових та обов'язково-рекомендованих правил стандартів MISRA C:2012, MISRA C++:2023, ISO 26262 або IEC 61508.

3. **Фаза виявлення (Detection Phase):**
   - `PREPARATION` (Індивідуальна підготовка): дефект знайдено інспектором під час індивідуального глибокого аналізу артефакту до початку засідання.
   - `MEETING` (Очне засідання): дефект виявлено безпосередньо під час синхронного читання та пояснення логіки читцем у присутності всієї групи.

## Математичний апарат та обчислення інспекційних показників

Програмне ядро системи здійснює багатокритеріальний аналіз отриманих первинних даних, спираючись на формальні статистичні моделі Майкла Фагана та стандартизовані формули оцінки якості програмного забезпечення IEEE 1044.

Першим базовим показником є швидкість вичитування артефакту (Inspection Rate, `R`), яка відображає інтенсивність когнітивної обробки матеріалу інспекційною групою. Швидкість вимірюється в кількості рядків вихідного коду (LOC, Lines of Code) або кількості еквівалентних електронних компонентів для схем, опрацьованих за одну астрономічну годину чистого часу засідання:

```
R = (Size_Units × 60.0) / Duration_Minutes
```

Якщо обчислена швидкість перевищує емпіричний поріг 220 LOC/год (або 40 компонентів на годину для апаратних схем), система генерує попередження `rate_warning = true`. Перевищення темпу свідчить про те, що засідання пройшло у режимі поверхневого перегляду, а значна частка прихованих логічних помилок і гонок у перериваннях залишилася непоміченою.

Другим ключовим показником є щільність виявлених дефектів (Defect Density, `D`), нормована на тисячу рядків коду (KLOC) або на сто дискретних компонентів схеми:

```
D = (Total_Defects × 1000.0) / Size_Units
```

Нормування дозволяє безпосередньо зіставляти якість роботи різних команд, модулів різного розміру та оцінювати ефективність застосування автоматизованих лінтерів перед передачею артефакту на інспекцію.

Для інтегральної оцінки тяжкості знайдених проблем система використовує зважений індекс дефектності (Weighted Defect Score, `WDS`). Вагові коефіцієнти відображають порядок різниці у вартості виправлення дефектів на наступних фазах життєвого циклу:

```
WDS = (Count_Critical × 10.0) + (Count_Major × 3.0) + (Count_Minor × 1.0)
```

Критичний дефект має коефіцієнт ваги 10.0, оскільки його потрапляння в реліз загрожує відкликом партії пристроїв або апаратним перепроектуванням друкованої плати. Значний дефект отримує коефіцієнт 3.0, а незначне зауваження — 1.0.

На основі значень `WDS`, кількості критичних зауважень та перевірки порогів швидкості алгоритм ухвалює однозначне рішення щодо виконання критеріїв виходу (Exit Criteria):
- `PASSED` (Артефакт прийнято без зауважень): відсутні будь-які дефекти, темп інспекції відповідав регламенту.
- `REWORK_AND_VERIFY` (Доопрацювання з індивідуальною верифікацією): критичні дефекти відсутні, значні дефекти мають локалізований характер (`Count_Critical == 0`, `WDS < 25.0`). Автор усуває помилки самостійно, після чого модератор особисто перевіряє кожен внесений рядок за протоколом без повторного збору всієї групи.
- `RE_INSPECT` (Обов'язкова повна повторна інспекція): знайдено хоча б один критичний дефект або зважений бал перевищив порогове значення (`Count_Critical > 0` або `WDS >= 25.0`), або обсяг переписаного коду перевищує 5% від загального розміру артефакту. У цьому випадку після завершення доопрацювання призначається повноцінна повторна інспекція з проходженням усіх фаз процесу.

## Повнофункціональна реалізація трекера інспекції

Нижче представлено дві повністю функціональні, готові до компіляції та запуску реалізації інспекційного трекера:
- Версія на стандарті **C99**: суворий процедурний стиль, робота зі статичними рядковими буферами безпечного розміру, динамічне розширення пулу дефектів із повною обробкою помилок виділення пам'яті (`malloc`/`realloc`), детерміноване очищення ресурсів.
- Версія на стандарті **C++20**: використання строгих типізованих класів перерахувань (`enum class`), семантика нульового копіювання через `std::string_view`, інкапсуляція стану в класі з RAII-гарантіями, безпечні опціональні результати обчислення через `std::optional`, суворе форматування числових потоків.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define FAGAN_MAX_STR_LEN       128
#define FAGAN_MAX_DESC_LEN      256
#define FAGAN_MAX_INSPECTORS    8
#define FAGAN_INITIAL_CAPACITY  16

typedef enum {
    SEV_MINOR = 0,
    SEV_MAJOR,
    SEV_CRITICAL
} defect_severity_t;

typedef enum {
    CAT_LOGIC = 0,
    CAT_CONCURRENCY,
    CAT_HW_INTERFACE,
    CAT_RESOURCE_SAFETY,
    CAT_STANDARDS_MISRA
} defect_category_t;

typedef enum {
    PHASE_PREPARATION = 0,
    PHASE_MEETING
} detection_phase_t;

typedef enum {
    ARTIFACT_EMBEDDED_C_CPP = 0,
    ARTIFACT_SCHEMATIC,
    ARTIFACT_PCB_LAYOUT
} artifact_type_t;

typedef enum {
    DECISION_PASSED = 0,
    DECISION_REWORK_VERIFY,
    DECISION_RE_INSPECT
} exit_decision_t;

typedef struct {
    char location[FAGAN_MAX_STR_LEN];
    char description[FAGAN_MAX_DESC_LEN];
    defect_severity_t severity;
    defect_category_t category;
    detection_phase_t phase;
    int line_or_refdes_num;
} defect_entry_t;

typedef struct {
    char artifact_name[FAGAN_MAX_STR_LEN];
    char author[FAGAN_MAX_STR_LEN];
    char moderator[FAGAN_MAX_STR_LEN];
    char reader[FAGAN_MAX_STR_LEN];
    char inspectors[FAGAN_MAX_INSPECTORS][FAGAN_MAX_STR_LEN];
    int inspector_count;
    artifact_type_t artifact_type;
    size_t artifact_size_units; /* Кількість LOC або компонентів */
    double prep_time_person_hours;
    double meeting_duration_minutes;
    defect_entry_t *defects;
    size_t defect_count;
    size_t defect_capacity;
} fagan_session_t;

typedef struct {
    double inspection_rate_per_hour;
    double defect_density_per_kloc;
    double weighted_defect_score;
    size_t critical_count;
    size_t major_count;
    size_t minor_count;
    size_t prep_findings_count;
    size_t meeting_findings_count;
    exit_decision_t decision;
    bool rate_warning;
} inspection_metrics_t;

static const char* severity_to_str(defect_severity_t sev) {
    switch (sev) {
        case SEV_CRITICAL: return "CRITICAL";
        case SEV_MAJOR:    return "MAJOR";
        case SEV_MINOR:    return "MINOR";
        default:           return "UNKNOWN";
    }
}

static const char* category_to_str(defect_category_t cat) {
    switch (cat) {
        case CAT_LOGIC:           return "Logic/Algorithm";
        case CAT_CONCURRENCY:     return "Concurrency/ISR";
        case CAT_HW_INTERFACE:    return "Hardware Interface";
        case CAT_RESOURCE_SAFETY: return "Resource/Memory Safety";
        case CAT_STANDARDS_MISRA: return "Standards/MISRA";
        default:                  return "Unknown";
    }
}

static const char* decision_to_str(exit_decision_t dec) {
    switch (dec) {
        case DECISION_PASSED:        return "PASSED (Artifact Approved)";
        case DECISION_REWORK_VERIFY: return "REWORK (Verify fixes by Moderator)";
        case DECISION_RE_INSPECT:    return "RE-INSPECT (Mandatory Full Re-session)";
        default:                     return "UNKNOWN";
    }
}

bool fagan_session_init(fagan_session_t *session,
                        const char *artifact_name,
                        const char *author,
                        const char *moderator,
                        const char *reader,
                        artifact_type_t type,
                        size_t size_units,
                        double meeting_mins) {
    if (!session || !artifact_name || !author || !moderator || !reader || size_units == 0) {
        return false;
    }

    memset(session, 0, sizeof(fagan_session_t));
    strncpy(session->artifact_name, artifact_name, FAGAN_MAX_STR_LEN - 1);
    strncpy(session->author, author, FAGAN_MAX_STR_LEN - 1);
    strncpy(session->moderator, moderator, FAGAN_MAX_STR_LEN - 1);
    strncpy(session->reader, reader, FAGAN_MAX_STR_LEN - 1);
    session->artifact_type = type;
    session->artifact_size_units = size_units;
    session->meeting_duration_minutes = meeting_mins;

    session->defects = (defect_entry_t*)malloc(FAGAN_INITIAL_CAPACITY * sizeof(defect_entry_t));
    if (!session->defects) {
        return false;
    }
    session->defect_capacity = FAGAN_INITIAL_CAPACITY;
    session->defect_count = 0;
    return true;
}

bool fagan_session_add_inspector(fagan_session_t *session, const char *inspector_name) {
    if (!session || !inspector_name) return false;
    if (session->inspector_count >= FAGAN_MAX_INSPECTORS) return false;

    strncpy(session->inspectors[session->inspector_count], inspector_name, FAGAN_MAX_STR_LEN - 1);
    session->inspector_count++;
    return true;
}

void fagan_session_add_prep_time(fagan_session_t *session, double person_hours) {
    if (session && person_hours > 0.0) {
        session->prep_time_person_hours += person_hours;
    }
}

bool fagan_session_record_defect(fagan_session_t *session,
                                 const char *location,
                                 int line_or_refdes,
                                 defect_severity_t severity,
                                 defect_category_t category,
                                 detection_phase_t phase,
                                 const char *description) {
    if (!session || !location || !description) return false;

    if (session->defect_count >= session->defect_capacity) {
        size_t new_cap = session->defect_capacity * 2;
        defect_entry_t *new_arr = (defect_entry_t*)realloc(session->defects,
                                                          new_cap * sizeof(defect_entry_t));
        if (!new_arr) return false;
        session->defects = new_arr;
        session->defect_capacity = new_cap;
    }

    defect_entry_t *entry = &session->defects[session->defect_count];
    strncpy(entry->location, location, FAGAN_MAX_STR_LEN - 1);
    entry->line_or_refdes_num = line_or_refdes;
    entry->severity = severity;
    entry->category = category;
    entry->phase = phase;
    strncpy(entry->description, description, FAGAN_MAX_DESC_LEN - 1);

    session->defect_count++;
    return true;
}

bool fagan_session_calculate_metrics(const fagan_session_t *session,
                                    inspection_metrics_t *metrics) {
    if (!session || !metrics || session->artifact_size_units == 0) return false;

    memset(metrics, 0, sizeof(inspection_metrics_t));

    if (session->meeting_duration_minutes > 0.0) {
        metrics->inspection_rate_per_hour =
            ((double)session->artifact_size_units * 60.0) / session->meeting_duration_minutes;
    } else {
        metrics->inspection_rate_per_hour = 0.0;
    }

    /* Поріг швидкості для вбудованих систем: оптимально 100..150 LOC/год */
    if (metrics->inspection_rate_per_hour > 220.0 || metrics->inspection_rate_per_hour < 40.0) {
        metrics->rate_warning = true;
    }

    for (size_t i = 0; i < session->defect_count; ++i) {
        const defect_entry_t *d = &session->defects[i];
        switch (d->severity) {
            case SEV_CRITICAL:
                metrics->critical_count++;
                metrics->weighted_defect_score += 10.0;
                break;
            case SEV_MAJOR:
                metrics->major_count++;
                metrics->weighted_defect_score += 3.0;
                break;
            case SEV_MINOR:
                metrics->minor_count++;
                metrics->weighted_defect_score += 1.0;
                break;
        }

        if (d->phase == PHASE_PREPARATION) {
            metrics->prep_findings_count++;
        } else {
            metrics->meeting_findings_count++;
        }
    }

    metrics->defect_density_per_kloc =
        ((double)session->defect_count * 1000.0) / (double)session->artifact_size_units;

    /* Визначення фінального рішення модератора */
    if (metrics->critical_count > 0 || metrics->weighted_defect_score >= 25.0) {
        metrics->decision = DECISION_RE_INSPECT;
    } else if (metrics->major_count > 0 || metrics->minor_count > 0) {
        metrics->decision = DECISION_REWORK_VERIFY;
    } else {
        metrics->decision = DECISION_PASSED;
    }

    return true;
}

void fagan_session_print_report(const fagan_session_t *session,
                                const inspection_metrics_t *metrics) {
    if (!session || !metrics) return;

    printf("================================================================================\n");
    printf("                  ПРОТОКОЛ ФОРМАЛЬНОЇ ІНСПЕКЦІЇ ФАГАНА                          \n");
    printf("================================================================================\n");
    printf("Артефакт:        %s\n", session->artifact_name);
    printf("Автор:           %s\n", session->author);
    printf("Модератор:       %s\n", session->moderator);
    printf("Читець:          %s\n", session->reader);
    printf("Інспектори (%d):  ", session->inspector_count);
    for (int i = 0; i < session->inspector_count; ++i) {
        printf("%s%s", session->inspectors[i], (i == session->inspector_count - 1) ? "" : ", ");
    }
    printf("\n");
    printf("Розмір об'єкта:  %zu %s\n", session->artifact_size_units,
           (session->artifact_type == ARTIFACT_EMBEDDED_C_CPP) ? "LOC" : "Компонентів");
    printf("Час засідання:   %.1f хв | Трудовитрати підготовки: %.1f людино-годин\n",
           session->meeting_duration_minutes, session->prep_time_person_hours);
    printf("--------------------------------------------------------------------------------\n");
    printf("МЕТРИКИ ЯКОСТІ ТА ЕФЕКТИВНОСТІ:\n");
    printf("  Швидкість інспекції: %.1f од/год %s\n",
           metrics->inspection_rate_per_hour,
           metrics->rate_warning ? "[УВАГА: темп поза оптимальними межами 100-150!]" : "[НОРМА]");
    printf("  Знайдено дефектів:   %zu (Підготовка: %zu, Засідання: %zu)\n",
           session->defect_count, metrics->prep_findings_count, metrics->meeting_findings_count);
    printf("  Розподіл критичності: CRITICAL: %zu | MAJOR: %zu | MINOR: %zu\n",
           metrics->critical_count, metrics->major_count, metrics->minor_count);
    printf("  Щільність дефектів:  %.2f дефектів / KLOC\n", metrics->defect_density_per_kloc);
    printf("  Зважений бал (WDS):  %.1f\n", metrics->weighted_defect_score);
    printf("--------------------------------------------------------------------------------\n");
    printf("РЕЗУЛЬТАТ (Exit Criteria): %s\n", decision_to_str(metrics->decision));
    printf("================================================================================\n");
    printf("ЗАРЕЄСТРОВАНІ ДЕФЕКТИ:\n");
    for (size_t i = 0; i < session->defect_count; ++i) {
        const defect_entry_t *d = &session->defects[i];
        printf("[%02zu] %-8s | %-16s | %s:%d\n     Опис: %s\n",
               i + 1,
               severity_to_str(d->severity),
               category_to_str(d->category),
               d->location,
               d->line_or_refdes_num,
               d->description);
    }
    printf("================================================================================\n");
}

void fagan_session_free(fagan_session_t *session) {
    if (session) {
        if (session->defects) {
            free(session->defects);
            session->defects = NULL;
        }
        session->defect_count = 0;
        session->defect_capacity = 0;
    }
}

int main(void) {
    fagan_session_t session;
    if (!fagan_session_init(&session,
                            "drivers/spi_dma_stm32f4.c",
                            "О. Ковальчук (Firmware)",
                            "І. Бондар (Lead Moderator)",
                            "В. Ткаченко (Reader)",
                            ARTIFACT_EMBEDDED_C_CPP,
                            380,   /* 380 LOC драйвера */
                            150.0  /* 2.5 години = 150 хв */)) {
        fprintf(stderr, "Помилка ініціалізації сесії інспекції\n");
        return 1;
    }

    fagan_session_add_inspector(&session, "М. Шевченко (Safety Engineer)");
    fagan_session_add_inspector(&session, "Д. Мельник (Hardware Architect)");
    fagan_session_add_prep_time(&session, 3.5);

    /* Фіксація дефектів, знайдених під час підготовки та засідання */
    fagan_session_record_defect(&session, "spi_dma_stm32f4.c", 142,
                                SEV_CRITICAL, CAT_CONCURRENCY, PHASE_PREPARATION,
                                "Відсутній memory barrier перед запуском DMA; гонка кешу та пам'яті");

    fagan_session_record_defect(&session, "spi_dma_stm32f4.c", 89,
                                SEV_MAJOR, CAT_HW_INTERFACE, PHASE_MEETING,
                                "Не скидається прапорець TXE перед читанням RXNE на шині SPI; зависання");

    fagan_session_record_defect(&session, "spi_dma_stm32f4.c", 215,
                                SEV_MINOR, CAT_STANDARDS_MISRA, PHASE_PREPARATION,
                                "Порушення MISRA Rule 10.4: неявне приведення знакового int до uint32_t");

    inspection_metrics_t metrics;
    if (fagan_session_calculate_metrics(&session, &metrics)) {
        fagan_session_print_report(&session, &metrics);
    }

    fagan_session_free(&session);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <iomanip>
#include <span>
#include <format>
#include <memory>
#include <cstdint>

enum class DefectSeverity {
    Minor,
    Major,
    Critical
};

enum class DefectCategory {
    Logic,
    Concurrency,
    HardwareInterface,
    ResourceSafety,
    StandardsCompliance
};

enum class DetectionPhase {
    Preparation,
    Meeting
};

enum class ArtifactType {
    EmbeddedCode,
    Schematic,
    PcbLayout
};

enum class ExitDecision {
    Passed,
    ReworkAndVerify,
    ReInspect
};

struct DefectRecord {
    std::string location;
    int line_or_refdes{0};
    DefectSeverity severity{DefectSeverity::Minor};
    DefectCategory category{DefectCategory::Logic};
    DetectionPhase phase{DetectionPhase::Meeting};
    std::string description;
};

struct InspectionMetrics {
    double inspection_rate_per_hour{0.0};
    double defect_density_per_kloc{0.0};
    double weighted_defect_score{0.0};
    std::size_t critical_count{0};
    std::size_t major_count{0};
    std::size_t minor_count{0};
    std::size_t prep_findings{0};
    std::size_t meeting_findings{0};
    ExitDecision decision{ExitDecision::Passed};
    bool rate_warning{false};
};

class FaganInspectionSession {
public:
    FaganInspectionSession(std::string_view artifact_name,
                           std::string_view author,
                           std::string_view moderator,
                           std::string_view reader,
                           ArtifactType type,
                           std::size_t size_units,
                           double meeting_minutes)
        : artifact_name_(artifact_name),
          author_(author),
          moderator_(moderator),
          reader_(reader),
          artifact_type_(type),
          artifact_size_units_(size_units),
          meeting_duration_minutes_(meeting_minutes) {}

    void add_inspector(std::string_view inspector_name) {
        inspectors_.emplace_back(inspector_name);
    }

    void add_prep_time(double person_hours) noexcept {
        if (person_hours > 0.0) {
            prep_time_person_hours_ += person_hours;
        }
    }

    void record_defect(std::string_view location,
                       int line_or_refdes,
                       DefectSeverity severity,
                       DefectCategory category,
                       DetectionPhase phase,
                       std::string_view description) {
        defects_.push_back(DefectRecord{
            .location = std::string(location),
            .line_or_refdes = line_or_refdes,
            .severity = severity,
            .category = category,
            .phase = phase,
            .description = std::string(description)
        });
    }

    [[nodiscard]] std::optional<InspectionMetrics> compute_metrics() const noexcept {
        if (artifact_size_units_ == 0) {
            return std::nullopt;
        }

        InspectionMetrics m;

        if (meeting_duration_minutes_ > 0.0) {
            m.inspection_rate_per_hour =
                (static_cast<double>(artifact_size_units_) * 60.0) / meeting_duration_minutes_;
        }

        if (m.inspection_rate_per_hour > 220.0 || m.inspection_rate_per_hour < 40.0) {
            m.rate_warning = true;
        }

        for (const auto& d : defects_) {
            switch (d.severity) {
                case DefectSeverity::Critical:
                    m.critical_count++;
                    m.weighted_defect_score += 10.0;
                    break;
                case DefectSeverity::Major:
                    m.major_count++;
                    m.weighted_defect_score += 3.0;
                    break;
                case DefectSeverity::Minor:
                    m.minor_count++;
                    m.weighted_defect_score += 1.0;
                    break;
            }

            if (d.phase == DetectionPhase::Preparation) {
                m.prep_findings++;
            } else {
                m.meeting_findings++;
            }
        }

        m.defect_density_per_kloc =
            (static_cast<double>(defects_.size()) * 1000.0) / static_cast<double>(artifact_size_units_);

        if (m.critical_count > 0 || m.weighted_defect_score >= 25.0) {
            m.decision = ExitDecision::ReInspect;
        } else if (m.major_count > 0 || m.minor_count > 0) {
            m.decision = ExitDecision::ReworkAndVerify;
        } else {
            m.decision = ExitDecision::Passed;
        }

        return m;
    }

    void render_summary(std::ostream& os) const {
        auto metrics_opt = compute_metrics();
        if (!metrics_opt) {
            os << "Помилка обчислення метрик: нульовий розмір артефакту.\n";
            return;
        }
        const auto& m = *metrics_opt;

        os << "================================================================================\n";
        os << "                  ПРОТОКОЛ ФОРМАЛЬНОЇ ІНСПЕКЦІЇ ФАГАНА (C++20)                 \n";
        os << "================================================================================\n";
        os << "Артефакт:        " << artifact_name_ << "\n";
        os << "Автор:           " << author_ << "\n";
        os << "Модератор:       " << moderator_ << "\n";
        os << "Читець:          " << reader_ << "\n";
        os << "Інспектори:      ";
        for (std::size_t i = 0; i < inspectors_.size(); ++i) {
            os << inspectors_[i] << (i + 1 == inspectors_.size() ? "" : ", ");
        }
        os << "\n";
        os << "Розмір об'єкта:  " << artifact_size_units_ << " "
           << (artifact_type_ == ArtifactType::EmbeddedCode ? "LOC" : "Компонентів") << "\n";
        os << "Час засідання:   " << meeting_duration_minutes_ << " хв | Підготовка: "
           << prep_time_person_hours_ << " людино-годин\n";
        os << "--------------------------------------------------------------------------------\n";
        os << "МЕТРИКИ:\n";
        os << "  Швидкість:     " << std::fixed << std::setprecision(1)
           << m.inspection_rate_per_hour << " од/год "
           << (m.rate_warning ? "[УВАГА: темп поза оптимальними межами 100-150!]" : "[НОРМА]") << "\n";
        os << "  Дефекти:       " << defects_.size() << " (Підготовка: " << m.prep_findings
           << ", Засідання: " << m.meeting_findings << ")\n";
        os << "  Розподіл:      CRITICAL: " << m.critical_count
           << " | MAJOR: " << m.major_count
           << " | MINOR: " << m.minor_count << "\n";
        os << "  Щільність:     " << std::setprecision(2) << m.defect_density_per_kloc << " def / KLOC\n";
        os << "  Зважений бал:  " << std::setprecision(1) << m.weighted_defect_score << "\n";
        os << "--------------------------------------------------------------------------------\n";
        os << "РІШЕННЯ ВИХОДУ: " << decision_to_string(m.decision) << "\n";
        os << "================================================================================\n";
        os << "СПИСОК ДЕФЕКТІВ:\n";
        for (std::size_t i = 0; i < defects_.size(); ++i) {
            const auto& d = defects_[i];
            os << "[" << std::setw(2) << std::setfill('0') << (i + 1) << "] "
               << std::setw(8) << std::setfill(' ') << severity_to_string(d.severity) << " | "
               << std::setw(20) << category_to_string(d.category) << " | "
               << d.location << ":" << d.line_or_refdes << "\n"
               << "     Опис: " << d.description << "\n";
        }
        os << "================================================================================\n";
    }

private:
    static std::string_view severity_to_string(DefectSeverity sev) noexcept {
        switch (sev) {
            case DefectSeverity::Critical: return "CRITICAL";
            case DefectSeverity::Major:    return "MAJOR";
            case DefectSeverity::Minor:    return "MINOR";
        }
        return "UNKNOWN";
    }

    static std::string_view category_to_string(DefectCategory cat) noexcept {
        switch (cat) {
            case DefectCategory::Logic:               return "Logic/Algorithm";
            case DefectCategory::Concurrency:         return "Concurrency/ISR";
            case DefectCategory::HardwareInterface:    return "Hardware Interface";
            case DefectCategory::ResourceSafety:      return "Resource Safety";
            case DefectCategory::StandardsCompliance: return "Standards/MISRA";
        }
        return "Unknown";
    }

    static std::string_view decision_to_string(ExitDecision dec) noexcept {
        switch (dec) {
            case ExitDecision::Passed:          return "PASSED (Artifact Approved)";
            case ExitDecision::ReworkAndVerify: return "REWORK (Verify fixes by Moderator)";
            case ExitDecision::ReInspect:       return "RE-INSPECT (Mandatory Full Re-session)";
        }
        return "UNKNOWN";
    }

    std::string artifact_name_;
    std::string author_;
    std::string moderator_;
    std::string reader_;
    std::vector<std::string> inspectors_;
    ArtifactType artifact_type_{ArtifactType::EmbeddedCode};
    std::size_t artifact_size_units_{0};
    double prep_time_person_hours_{0.0};
    double meeting_duration_minutes_{0.0};
    std::vector<DefectRecord> defects_;
};

int main() {
    FaganInspectionSession session(
        "drivers/spi_dma_stm32f4.cpp",
        "О. Ковальчук (Firmware)",
        "І. Бондар (Lead Moderator)",
        "В. Ткаченко (Reader)",
        ArtifactType::EmbeddedCode,
        380,
        150.0
    );

    session.add_inspector("М. Шевченко (Safety Engineer)");
    session.add_inspector("Д. Мельник (Hardware Architect)");
    session.add_prep_time(3.5);

    session.record_defect(
        "spi_dma_stm32f4.cpp", 142,
        DefectSeverity::Critical,
        DefectCategory::Concurrency,
        DetectionPhase::Preparation,
        "Відсутній memory barrier перед запуском DMA; гонка кешу та пам'яті"
    );

    session.record_defect(
        "spi_dma_stm32f4.cpp", 89,
        DefectSeverity::Major,
        DefectCategory::HardwareInterface,
        DetectionPhase::Meeting,
        "Не скидається прапорець TXE перед читанням RXNE на шині SPI; зависання"
    );

    session.record_defect(
        "spi_dma_stm32f4.cpp", 215,
        DefectSeverity::Minor,
        DefectCategory::StandardsCompliance,
        DetectionPhase::Preparation,
        "Порушення MISRA Rule 10.4: неявне приведення знакового int до uint32_t"
    );

    session.render_summary(std::cout);
    return 0;
}
```
:::

## Інженерний аналіз дефектів із тестового сценарію

Для демонстрації практичної цінності трекера розглянемо реальні інженерні дефекти, зафіксовані в тестовому сценарії запуску низькорівневого драйвера `drivers/spi_dma_stm32f4`:

1. **Критичний дефект конкурентності у рядку 142 (Race condition між кешем та DMA):**
   У сучасних мікроконтролерах на ядрах ARM Cortex-M7 (наприклад, серії STM32F7 / STM32H7) або Cortex-A процесорне ядро працює через дворівневий кеш даних (L1 D-Cache). Коли драйвер готує буфер передачі в оперативній пам'яті, модифіковані байти залишаються в кеш-лініях процесора і помічаються як «брудні» (dirty). Якщо запустити контролер прямого доступу до пам'яті DMA без примусового скидання кешу (`SCB_CleanDCache_by_Addr()`) та бар'єра інструкцій `__DMB()` (Data Memory Barrier), DMA вичитає з фізичної SRAM застарілі дані, які були там до запису.
   Цей дефект класифікується як `CRITICAL`, оскільки під час звичайного модульного тестування на низьких тактових частотах або за вимкненого кешування помилка себе не проявляє. Проте під час масової експлуатації на граничних швидкостях шини виникає стохастичне спотворення даних, що призводить до аварійного відключення приладу.

2. **Значний дефект апаратного інтерфейсу у рядку 89 (Зависання автомата станів SPI):**
   Периферійний модуль SPI у багатьох архітектурах є повнодуплексним зсувним регістром. При кожному такті передачі біта на лінії MOSI одночасно здійснюється зсув біта з лінії MISO у внутрішній буфер прийому. Якщо розробник ініціює передачу нового байта записом у регістр даних `DR`, не дочекавшись встановлення прапорця готовності передавача `TXE == 1`, або не вичитує отриманий байт після появи прапорця `RXNE == 1`, в апаратному модулі виникає помилка переповнення приймача (`OVR = 1`, Overrun Error).
   Встановлення біта `OVR` у контролерах STM32 апаратно блокує генерацію наступних запитів переривань та DMA, викликаючи мертве зависання інтерфейсу обміну. Дефект класифіковано як `MAJOR`, оскільки він порушує стабільність каналу зв'язку, хоч і не призводить до фізичного виходу з ладу трансиверів.

3. **Незначний дефект стандарту MISRA у рядку 215 (Неявне приведення знакового типу):**
   У рядку 215 розробник використав вираз бітового зсуву виду `(1 << pin_number)`, де літерал `1` за замовчуванням має знаковий тип `int`. За стандартом C99/C++ зсув одиниці у 31-й знаковий біт для 32-бітного знакового цілого породжує невизначену поведінку (Undefined Behavior).
   Правило стандарту MISRA C:2012 Rule 10.4 вимагає явної типізації констант: `(1u << pin_number)` або `((uint32_t)1 << pin_number)`. Дефект зафіксовано як `MINOR`, оскільки на поточному компіляторі GCC зі знятими прапорцями суворої оптимізації код міг генерувати очікувану інструкцію, проте при зміні версії компілятора чи рівня оптимізації `-O3` міг призвести до непередбачуваної поведінки генератора коду.

## Детальний розбір реалізації та порівняльний аналіз парадигм

Обидві реалізації вирішують одне завдання обліку та математичної обробки протоколів, проте демонструють принципово різні архітектурні підходи до управління пам'яттю, безпеки типів та гарантій часу виконання.

У C99-реалізації особлива увага приділена запобіганню витоків пам'яті та захисту від пошкодження стека. Функція `fagan_session_init` виділяє початковий динамічний блок пам'яті під фіксовану кількість дефектів (`FAGAN_INITIAL_CAPACITY = 16`). При заповненні масиву функція `fagan_session_record_defect` виконує подвоєння місткості через виклик `realloc`. Критично важливим паттерном для мови C є збереження результату `realloc` у проміжну локальну змінну `new_arr`. Пряме присвоєння `session->defects = realloc(...)` є класичною помилкою: якщо системі забракне пам'яті, функція поверне `NULL`, старий вказівник буде безповоротно втрачено, а виділена раніше пам'ять перетвориться на витік. Використання проміжної змінної зберігає цілісність початкового стану структури.

Робота з текстовими рядками в C-версії базується на використанні масивів фіксованої довжини всередині структур та функції `strncpy` з примусовим записом нуль-термінатора `'\0'` в останній байт буфера (`FAGAN_MAX_STR_LEN - 1`). Це запобігає виходу за межі пам'яті у випадку, якщо переданий ззовні рядок перевищує виділений ліміт.

У C++20-реалізації процедурні структури замінено на інкапсульований клас `FaganInspectionSession`. Замість ручного керування динамічною пам'яттю застосовано контейнери стандартної бібліотеки `std::vector<DefectRecord>` та `std::vector<std::string>`. Контейнери реалізують парадигму RAII (Resource Acquisition Is Initialization), автоматично звільняючи виділену динамічну пам'ять у момент виходу об'єкта сесії з області видимості. Це усуває необхідність у ручних функціях деструктуризації на зразок `fagan_session_free` та гарантує повну відсутність витоків ресурсів навіть у разі виникнення виняткових ситуацій.

Передача текстових аргументів у методи C++20 здійснюється через тип `std::string_view`. На відміну від `const char*` у мові C, `std::string_view` передає вказівник на початок рядка та його довжину як єдиний об'єкт без потреби у виклику `strlen()`. Це виключає накладні витрати на підрахунок довжини та дозволяє передавати підрядки без виділення проміжних копій у купі.

Важливою перевагою C++20 є також використання строго типізованих перерахувань `enum class` (`DefectSeverity`, `DefectCategory`, `ExitDecision`). На відміну від звичайних перерахувань `enum` у мові C, значення яких неявно приводяться до цілочисельного типу `int`, `enum class` не дозволяє випадково передати значення категорії дефекту замість його критичності. Компілятор виявляє такі невідповідності на етапі статичного аналізу коду ще до запуску програми.

## Обробка крайових випадків та відмовостійкість

Під час практичної експлуатації системи на етапі підготовки релізу вбудованих пристроїв виникають специфічні прикордонні стани, які вимагають детермінованої та безпечної поведінки програмного ядра:

1. **Нульовий або некоректний розмір артефакту (`artifact_size_units == 0`):**
   Якщо користувач помилково передав нульовий розмір файлу або схеми, прямий розрахунок швидкості та щільності дефектів призведе до фатальної помилки ділення на нуль (`SIGFPE`). У C99 функція `fagan_session_calculate_metrics` негайно перевіряє цю умову та повертає статус `false`. У C++20 метод `compute_metrics()` повертає типізований порожній об'єкт `std::nullopt`, вимагаючи від клієнтського коду явної перевірки валідності отриманого результату через конструкцію `if (!metrics_opt)`.

2. **Нульова тривалість зустрічі (`meeting_duration_minutes == 0.0`):**
   Така ситуація виникає, якщо модератор зупинив засідання на самому початку фази відкриття через те, що інспектори не пройшли попередню перевірку готовності (не заповнили індивідуальні чеклісти підготовки). Алгоритм встановлює швидкість інспекції рівною нулю, але не перериває розрахунок інших показників, зберігаючи всі зафіксовані на фазі підготовки зауваження.

3. **Сплеск дефектів та переповнення буфера протоколу:**
   Якщо якість артефакту виявилася катастрофічно низькою і кількість зареєстрованих проблем перевищила початкову місткість буфера (`FAGAN_INITIAL_CAPACITY`), алгоритм автоматично розширює пам'ять із геометричним коефіцієнтом 2.0. Це забезпечує амортизовану складність додавання запису `O(1)` і виключає падіння програми при великій кількості зауважень.

4. **Граничні значення темпу інспекції:**
   Алгоритм містить двосторонню перевірку швидкості:
   - Якщо `R > 220 LOC/год`, встановлюється попередження про ризик поверхневого вичитування (false sense of quality).
   - Якщо `R < 40 LOC/год`, встановлюється попередження про надмірне затягування засідання. Такий стан зазвичай свідчить про те, що група скотилася у заборонену фазою інспекції діяльність — пошук та проектування архітектурних рішень безпосередньо під час зустрічі (design-on-the-fly) замість швидкої фіксації знахідок.

## Специфіка конфігурації метрик для апаратної верифікації схем

При застосуванні трекера до апаратних артефактів (принципові схеми та трасування друкованих плат) виникає питання коректного вибору одиниць вимірювання розміру. Рядки коду (LOC) тут замінюються еквівалентними апаратними одиницями:
- Для принципових електричних схем базовою одиницею виступає кількість активних інтегральних мікросхем (ICs) та складних дискретних транзисторних каскадів. Пасивні компоненти (резистори та конденсатори) враховуються з ваговим коефіцієнтом 0.1 або групуються за функціональними вузлами (наприклад, вузол фільтрації живлення як 1 еквівалентна одиниця).
- Емпіричний перерахунок свідчить, що інспекція однієї мікросхеми середньої складності (наприклад, драйвер крокового двигуна з обв'язкою) за часовими витратами еквівалентна вичитуванню приблизно 15–20 рядків низькорівневого C-коду.
- Оптимальний темп інспекції схем складає 20–30 мікросхем на годину. Якщо темп перевищує 40 ICs/год, різко зростає ризик пропуску помилок у розрахунках розсіюваної теплової потужності, допустимих струмів захисних TVS-діодів або помилок підключення диференційних ліній зв'язку.

## Промислова інтеграція в конвеєр випуску релізу

Розроблений трекер інспекції інтегрується в загальний процес забезпечення якості як обов'язковий етап перед формуванням релізного образу прошивки або передачею Gerber-файлів на фабрику виготовлення друкованих плат.

У конвеєрі автоматизації згенерований протокол експортується у форматі машиночитних даних (JSON або структурований лог). Спеціалізований скрипт воріт релізу перевіряє фінальне поле `decision`:
- При отриманні статусу `PASSED` артефакт маркується як верифікований, і система дозволяє злиття ревізії з релізною гілкою `main`/`release`.
- При отриманні статусу `REWORK_AND_VERIFY` злиття блокується доти, доки модератор не підпише повторний акт верифікації виправлень.
- При отриманні статусу `RE_INSPECT` автоматично створюється блокуюче завдання на проведення повторної сесії, а попередня версія прошивки помічається як така, що не пройшла критерії надійності.

Такий підхід повністю усуває людський фактор і гарантує, що жодна апаратна чи програмна помилка критичного рівня не потрапить у масове серійне виробництво.
