# Валідатор звітів першої виробничої партії та звірки з еталоном

Автоматизований приймальний контроль першої виробничої партії (*First Article Inspection*, FAI) вимагає суворого математичного зіставлення сотень виміряних фізичних величин із проектними допусками та числовими сигнатурами еталонного золотого зразка (*Golden Sample*). Коли партія з 30–100 плат проходить тестові стенди внутрішньосхемного (ICT), оптичного (AOI), рентгенівського (AXOI) та функціонального (FCT) контролю, автоматичні комплекси генерують тисячі точкових замірів: напруги стабілізаторів живлення, рівні пульсацій, частоти тактових генераторів, струми споживання в різних режимах, відсотки пустот у пайці мікросхем BGA та криптографічні хеші завантажувача й прошивки.

Ручна обробка таких масивів у таблицях Excel не лише забирає десятки інженерних годин, але й створює критичні ризики людської помилки: пропуск небезпечного дрейфу середнього значення або ігнорування низького індексу придатності `Cpk`, коли всі поточні плати формально вклалися в допуски, але процес перебуває на межі масового браку. Програмний валідатор FAI автоматизує агрегацію вимірювань, виконує перевірку допусків, обчислює статистичні індекси `Cp` і `Cpk`, виявляє статистичні викиди (*outliers*) та генерує юридично вивірений машиночитний звіт Форми 3 за стандартом AS9102.

### Проблематика приймання першої виробничої партії та формати промислової телеметрії

У процесі виробництва першої установчої партії електроніки випробувальні стенди генерують різнорідні масиви телеметрії, які надходять із п'яти незалежних апаратних джерел:

1. **Автоматична лазерна інспекція нанесення пасти (3D SPI):** сканує плату безпосередньо після трафаретного друку. Обладнання провідних виробників (Koh Young, CyberOptics, Saki) формує протоколи вивантаження у форматі стандарту IPC-CFX (*Connected Factory Exchange / IPC-2591*) або XML/JSON. Файли містять точні дані про об'єм нанесеної припойної пасти у відсотках від номіналу апертури трафарету (норма: 80–120%), абсолютну висоту подушки пасти в мікрометрах та площу зміщення відбитка відносно мідного майданчика.
2. **Оптичні томографи та інспекція після оплавлення (Post-Reflow 3D AOI):** фіксують лінійні координати зміщення корпусів мікросхем по осях `X` та `Y`, кутовий перекіс `theta`, висоту меніска паяного з'єднання за критеріями класифікації IPC-A-610 Class 2 / Class 3, а також зчитують лазерне або друковане маркування мікросхем через алгоритми оптичного розпізнавання символів (OCR).
3. **Автоматичні 3D-рентгенівські томографи (AXOI / AXI):** установки рентгенівського просвічування (Nordson Dage, Yxlon, Goepel) генерують матриці відсотка газових пустот (*voiding percentage*) під силовими контактними майданчиками QFN/DFN та масивами кульок мікросхем BGA. За стандартами IPC-7095, відсоток пустот у кульці BGA не повинен перевищувати 15% від її площі перерізу.
4. **Голчасті внутрішньосхемні тестери (ICT Bed of Nails):** машини автоматичного тестування (Keysight i3070, Teradyne TestStation, SPEA 4060) знімають опір пасивних компонентів, ємність конденсаторів, пряме падіння напруги на захисних діодах, імпеданс шин живлення та відсутність паразитних мікроперемичок між провідниками друкованої плати.
5. **Функціональні тестові стенди (FCT / End-of-Line):** виконують повноцінне тестування зібраного приладу під напругою, зчитують та верифікують системний завантажувач, записують основну прошивку, фіксують цифрові сигнатури (UID процесора, MAC-адреси мережевих інтерфейсів, стан апаратних бітів захисту Option Bytes / eFuses), вимірюють напруги шин живлення під динамічним навантаженням та проводять калібрування вихідної потужності радіочастотних трактів (RF EIRP) за допомогою векторних аналізаторів спектра.

Головна небезпека ручного аналізу таких звітів полягає в оманливому спокої бінарної оцінки «Pass / Fail». Якщо для шини живлення 3.3 В встановлено інженерні межі допуску `[3.135 .. 3.465 В]`, а на всіх 30 випробуваних платах вольтметр зафіксував напругу `3.45 В`, простий скрипт або оператор у цеху позначить усі плати як успішні (Pass). 

Проте з погляду математичної статистики технологічний процес перебуває в катастрофічному стані: середнє значення зміщене впритул до верхньої межі допуску, індекс центрованості `Cpk` опустився нижче 0.5, і в разі неминучого сезонного коливання температури в цеху або зміни партії резисторів дільника завод почне продукувати до 20–30% прямого браку.

Розроблений інструмент вирішує це завдання комплексним аналізом: він не лише перевіряє факт потрапляння кожного окремого виміру у вікно специфікації, але й вираховує математичне сподівання, стандартне відхилення, індекси `Cp` і `Cpk`, дрейф від еталонного зразка Golden Sample та побітову відповідність цифрових хешів.

### Математичний апарат аналізу дисперсії та індексів придатності

Для оцінки якості серійного випуску розглядається масив вимірювань `x[1], x[2], ..., x[N]` випадкової фізичної величини `X`. За центральною граничною теоремою, сукупна дія великої кількості незалежних мікрофакторів виробництва (варіація товщини міді, розкид в'язкості пасти, температурні флуктуації печі) призводить до формування нормального розподілу Гауса.

Для обчислення вибіркового середнього `mu` та вибіркової дисперсії `sigma^2` у реальному часі на вбудованих системах застосовується алгоритм Велфорда (*B. P. Welford, 1962*). 

Класична підручникова формула розрахунку дисперсії вимагає або двох послідовних проходів масиву даних (перший прохід для обчислення середнього, другий — для сумування квадратів різниць `(x[i] - mu)^2`), або використання формули `sum(x^2) - (sum(x))^2 / N`. 

Другий підхід страждає від критичної вади — втрати точності через катастрофічне скасування значущих розрядів (*Catastrophic Cancellation*), коли віднімаються два майже однакових великих числа.

Алгоритм Велфорда усуває цю проблему, виконуючи рекурентне оновлення середнього `M[k]` та проміжної суми квадратів відхилень `S[k]` під час надходження кожного нового виміру `x[k]`:

```
M[0] = 0
S[0] = 0

Для кожного k від 1 до N:
  Δ1   = x[k] - M[k-1]
  M[k] = M[k-1] + Δ1 / k
  Δ2   = x[k] - M[k]
  S[k] = S[k-1] + Δ1 · Δ2

Вибіркова незсунена дисперсія:
  s² = S[N] / (N - 1)

Вибіркове стандартне відхилення:
  s  = √(s²)
```

Цей метод гарантує чисельну стабільність розрахунків навіть при обробці мільйонів вимірювань на 32-розрядних мікроконтролерах із плаваючою точкою одинарної точності.

Після знаходження `x̄` (вибіркового середнього) та `s` (вибіркового стандартного відхилення) обчислюються індекси придатності технологічного процесу:

Для двосторонніх параметрів:
```
       USL - LSL
Cp  = ───────────
         6 · s

       USL - x̄
Cpu = ─────────
        3 · s

       x̄ - LSL
Cpl = ─────────
        3 · s

Cpk = min(Cpu, Cpl)
```

Для односторонніх параметрів із верхньою межею:
```
       USL - Nominal
Cp  = ───────────────
           3 · s

       USL - x̄
Cpk = ─────────
        3 · s
```

### Корекція малих вибірок та довірчі інтервали для Cpk

На етапі первинного запуску FAI обсяг вибірки зазвичай обмежений кількістю плат у пілотній партії (`N = 10..30`). При малій кількості вимірів вибіркове стандартне відхилення `s` є зміщеною оцінкою генерального стандартного відхилення генеральної сукупності `sigma`. 

Для отримання строго незсуненої оцінки застосовується теоретичний поправочний коефіцієнт `c4(N)`, заснований на гамма-функції:

```
          √(2 / (N - 1)) · Γ(N / 2)
c4(N) = ─────────────────────────────
                Γ((N - 1) / 2)
```

Для практичних обчислень при `N >= 10` використовується високоточне наближення:
```
c4(N) ≈ 1 - 1 / (4 · N - 3)
```

Оцінка генерального відхилення обчислюється як `s_unbiased = s / c4(N)`.

Крім того, розрахований за вибіркою індекс `Cpk` сам по собі є випадковою величиною. Для інженерного менеджменту важливо знати нижню межу 95% двостороннього довірчого інтервалу (*Confidence Interval*):

```
                       ┌                               ┐
                       │           1           Cpk²    │
Cpk_нижній = Cpk - 1.96 · │ ──────────────── + ───────── │
                       │    9 · N · Cpk²       2(N - 1)│
                       └                               ┘
```

Якщо для вибірки з `N = 10` плат розрахований `Cpk = 1.40`, його нижня межа 95% довіри може становити лише `0.92`. Це вказує технологу, що хоча поточна вибірка виглядає задовільно, існує статистичний ризик виходу процесу з-під контролю на великій серії, і розмір установчої партії слід розширити для підтвердження стабільності.

### Виявлення технологічного дрейфу за правилами контрольних карт Шухарта

Окрім інтегральних індексів `Cpk`, валідатор аналізує динаміку послідовності виробництва. У масовому виробництві розлад лінії часто починається задовго до того, як перший виріб перетне межу `USL` або `LSL`.

Для виявлення прихованих закономірностей у послідовності виготовлення плат застосовуються правила Нельсона (*Nelson Rules / Western Electric Rules*):

1. **Правило 1 (Вихід за межі трьох сигм):** хоча б одна точка вийшла за межі `[mu - 3·sigma .. mu + 3·sigma]`. Вказує на раптовий одиничний збій обладнання (заклинювання живильника або поломка голки ICT).
2. **Правило 2 (Зміщення центру процесу):** дев'ять послідовних точок розташовані по один бік від середньої лінії `mu`. Вказує на зміщення систематичного налаштування (наприклад, оператор встановив нову партію пасивних компонентів зі зміщеним номіналом).
3. **Правило 3 (Монотонний тренд):** шість послідовних точок демонструють неперервне зростання або спадання. Вказує на монотонний дрейф технологічного фактора (поступовий знос ракеля трафаретного принтера, забивання сопел автомата PnP або нагрів термокамери тестера).
4. **Правило 4 (Циклічне чергування):** чотирнадцять точок поспіль чергуються вгору-вниз. Вказує на наявність двох паралельних несинхронізованих джерел впливу (наприклад, плати виготовляються на подвійній лінії монтажу або тестуються двома різними приладами).

У разі спрацьовування будь-якого з цих правил валідатор виставляє прапорець `STATUS_WARNING_LOW_CPK` або додає спеціальний діагностичний коментар у звіт Form 3.

### Архітектура системи валідації та моделі даних

Валідатор побудований за модульною схемою, що дозволяє легко інтегрувати його як у консольні скрипти приймання на виробничій лінії, так і у великі серверні системи управління якістю (QMS / MES).

Архітектура спирається на три базові сутності:

1. **Специфікація вимог (Parameter Specification):** описує метадані кожної контрольної точки виробу. Вона включає текстову назву, одиницю вимірювання, фізичний тип контролю, еталонний номінал Golden Sample, інженерні межі (LSL та USL) та очікуваний SHA-256 хеш для цифрових параметрів.
2. **Запис плати (Board Measurement Record):** містить унікальний серійний номер протестованого виробу, вектор знятих аналогових величин та масив текстових хешів програмних компонентів.
3. **Аналітичний результат (Parameter Analysis):** агрегує вибіркове середнє, стандартне відхилення, індекси придатності, величину систематичного дрейфу від еталона та підсумковий інженерний вердикт.

Параметри класифікуються за трьома типами контролю:
- `PARAM_TYPE_ANALOG_TWO_SIDED` — двосторонній допуск із фіксованими нижньою та верхньою межами (наприклад, напруга живлення, частота генератора, опір узгоджувального резистора);
- `PARAM_TYPE_UPPER_BOUND_ONLY` — односторонній допуск, де регламентується лише максимальне значення (наприклад, струм споживання в режимі глибокого сну, відсоток пустот під мікросхемою BGA, рівень пульсацій);
- `PARAM_TYPE_DIGITAL_HASH` — цифровий параметр суворої автентифікації, де вимагається стовідсотковий побайтовий збіг криптографічного хешу SHA-256 прошивки, версії бутлоадера або конфігураційних бітів OTP.

### Реалізація на мовах C99 та C++20

Нижче наведено повний вихідний код виробничого валідатора звітів FAI та звірки з Golden Sample. Обидві реалізації забезпечують сувору типізацію, захист від ділення на нуль, коректне форматування звіту та повністю еквівалентні за логікою роботи.

:::tabs
```c
/* ========================================================================= */
/* fai_validator.c - Мова C (C99)                                            */
/* Промисловий валідатор звітів першої виробничої партії (AS9102 Form 3)    */
/* ========================================================================= */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define FAI_MAX_SAMPLES 128
#define FAI_MAX_PARAMS  32
#define FAI_STR_LEN     64

typedef enum {
    PARAM_TYPE_ANALOG_TWO_SIDED,  /* Двосторонній допуск: LSL <= x <= USL */
    PARAM_TYPE_UPPER_BOUND_ONLY,   /* Односторонній верхній: x <= USL */
    PARAM_TYPE_DIGITAL_HASH        /* Побітовий збіг SHA-256 хешу */
} fai_param_type_t;

typedef enum {
    STATUS_PASS,                  /* Повний успіх: усі зразки в нормі, Cpk >= 1.33 */
    STATUS_WARNING_LOW_CPK,       /* Усі зразки в нормі, але Cpk < 1.33 (ризик браку в серії) */
    STATUS_FAIL_OUT_OF_SPEC,      /* Фізичний вихід хоча б одного зразка за межі допуску */
    STATUS_FAIL_HASH_MISMATCH     /* Невідповідність цифрового хешу еталону Golden Sample */
} fai_status_t;

typedef struct {
    char name[FAI_STR_LEN];
    char unit[16];
    fai_param_type_t type;
    double golden_nominal;
    double lsl;
    double usl;
    char golden_hash[65];
} fai_spec_item_t;

typedef struct {
    char board_serial[FAI_STR_LEN];
    double analog_values[FAI_MAX_PARAMS];
    char hash_values[FAI_MAX_PARAMS][65];
} fai_board_record_t;

typedef struct {
    double mean;
    double std_dev;
    double cp;
    double cpu;
    double cpl;
    double cpk;
    double golden_drift;
    size_t out_of_spec_count;
    size_t outlier_count;
    fai_status_t status;
} fai_param_analysis_t;

typedef struct {
    size_t total_boards;
    size_t total_params;
    size_t passed_params;
    size_t warning_params;
    size_t failed_params;
    bool overall_pass;
} fai_summary_t;

/* Аналіз одного параметра за вибіркою з N плат */
void fai_analyze_parameter(const fai_spec_item_t* spec,
                           const fai_board_record_t* boards,
                           size_t num_boards,
                           size_t param_idx,
                           fai_param_analysis_t* out_analysis) {
    memset(out_analysis, 0, sizeof(fai_param_analysis_t));
    out_analysis->status = STATUS_PASS;

    /* Обробка цифрового хешу */
    if (spec->type == PARAM_TYPE_DIGITAL_HASH) {
        for (size_t i = 0; i < num_boards; i++) {
            if (strncmp(boards[i].hash_values[param_idx], spec->golden_hash, 64) != 0) {
                out_analysis->out_of_spec_count++;
                out_analysis->status = STATUS_FAIL_HASH_MISMATCH;
            }
        }
        return;
    }

    /* Накопичення статистики за алгоритмом Велфорда */
    double mean = 0.0;
    double m2 = 0.0;
    size_t count = 0;

    for (size_t i = 0; i < num_boards; i++) {
        double val = boards[i].analog_values[param_idx];
        count++;
        double delta = val - mean;
        mean += delta / (double)count;
        double delta2 = val - mean;
        m2 += delta * delta2;

        /* Пряма перевірка допусків */
        if (spec->type == PARAM_TYPE_ANALOG_TWO_SIDED) {
            if (val < spec->lsl || val > spec->usl) {
                out_analysis->out_of_spec_count++;
            }
        } else if (spec->type == PARAM_TYPE_UPPER_BOUND_ONLY) {
            if (val > spec->usl) {
                out_analysis->out_of_spec_count++;
            }
        }
    }

    double variance = (count > 1) ? (m2 / (double)(count - 1)) : 0.0;
    double std_dev = sqrt(variance);
    if (std_dev < 1e-9) {
        std_dev = 1e-9; /* Захист від ділення на нуль при однаковому ряді вимірів */
    }

    out_analysis->mean = mean;
    out_analysis->std_dev = std_dev;
    out_analysis->golden_drift = mean - spec->golden_nominal;

    /* Детекція викидів за Z-критерієм (Z > 3.5) */
    for (size_t i = 0; i < num_boards; i++) {
        double val = boards[i].analog_values[param_idx];
        double z_score = fabs(val - mean) / std_dev;
        if (z_score > 3.5) {
            out_analysis->outlier_count++;
        }
    }

    /* Обчислення індексів придатності */
    if (spec->type == PARAM_TYPE_ANALOG_TWO_SIDED) {
        double spec_width = spec->usl - spec->lsl;
        out_analysis->cp = spec_width / (6.0 * std_dev);
        out_analysis->cpu = (spec->usl - mean) / (3.0 * std_dev);
        out_analysis->cpl = (mean - spec->lsl) / (3.0 * std_dev);
        out_analysis->cpk = (out_analysis->cpu < out_analysis->cpl) ? 
                             out_analysis->cpu : out_analysis->cpl;
    } else if (spec->type == PARAM_TYPE_UPPER_BOUND_ONLY) {
        out_analysis->cp = (spec->usl - spec->golden_nominal) / (3.0 * std_dev);
        out_analysis->cpu = (spec->usl - mean) / (3.0 * std_dev);
        out_analysis->cpl = 0.0;
        out_analysis->cpk = out_analysis->cpu;
    }

    /* Формування вердикту */
    if (out_analysis->out_of_spec_count > 0) {
        out_analysis->status = STATUS_FAIL_OUT_OF_SPEC;
    } else if (out_analysis->cpk < 1.33) {
        out_analysis->status = STATUS_WARNING_LOW_CPK;
    } else {
        out_analysis->status = STATUS_PASS;
    }
}

/* Генерація та вивід підсумкового звіту FAI Form 3 */
void fai_generate_report(const fai_spec_item_t* specs,
                         size_t num_params,
                         const fai_board_record_t* boards,
                         size_t num_boards,
                         fai_summary_t* summary) {
    memset(summary, 0, sizeof(fai_summary_t));
    summary->total_boards = num_boards;
    summary->total_params = num_params;
    summary->overall_pass = true;

    printf("==================================================================================================\n");
    printf("                    ПРОТОКОЛ ВАЛІДАЦІЇ ПЕРШОЇ ВИРОБНИЧОЇ ПАРТІЇ (AS9102 FORM 3)                  \n");
    printf("==================================================================================================\n");
    printf("Розмір вибірки: N = %zu плат | Кількість контрольованих параметрів: %zu\n\n", 
           num_boards, num_params);

    printf("%-22s | %-6s | %-8s | %-16s | %-8s | %-6s | %-6s | %-14s\n",
           "Параметр", "Один.", "Еталон", "Поле допуску", "Факт (μ)", "σ", "Cpk", "Вердикт");
    printf("--------------------------------------------------------------------------------------------------\n");

    for (size_t p = 0; p < num_params; p++) {
        fai_param_analysis_t a;
        fai_analyze_parameter(&specs[p], boards, num_boards, p, &a);

        char spec_range_str[32];
        char nominal_str[16];
        char mean_str[16];
        char std_str[16];
        char cpk_str[16];
        const char* verdict_str = "[ PASS ]";

        if (specs[p].type == PARAM_TYPE_DIGITAL_HASH) {
            snprintf(spec_range_str, sizeof(spec_range_str), "Exact Match");
            snprintf(nominal_str, sizeof(nominal_str), "SHA-256");
            snprintf(mean_str, sizeof(mean_str), "MATCH");
            snprintf(std_str, sizeof(std_str), "N/A");
            snprintf(cpk_str, sizeof(cpk_str), "N/A");
        } else {
            if (specs[p].type == PARAM_TYPE_ANALOG_TWO_SIDED) {
                snprintf(spec_range_str, sizeof(spec_range_str), "[%.3f..%.3f]", specs[p].lsl, specs[p].usl);
            } else {
                snprintf(spec_range_str, sizeof(spec_range_str), "[ <= %.3f ]", specs[p].usl);
            }
            snprintf(nominal_str, sizeof(nominal_str), "%.3f", specs[p].golden_nominal);
            snprintf(mean_str, sizeof(mean_str), "%.3f", a.mean);
            snprintf(std_str, sizeof(std_str), "%.4f", a.std_dev);
            snprintf(cpk_str, sizeof(cpk_str), "%.2f", a.cpk);
        }

        switch (a.status) {
            case STATUS_PASS:
                verdict_str = "[ PASS ]";
                summary->passed_params++;
                break;
            case STATUS_WARNING_LOW_CPK:
                verdict_str = "[!CPK < 1.33!]";
                summary->warning_params++;
                break;
            case STATUS_FAIL_OUT_OF_SPEC:
                verdict_str = "[*FAIL OOS*]";
                summary->failed_params++;
                summary->overall_pass = false;
                break;
            case STATUS_FAIL_HASH_MISMATCH:
                verdict_str = "[*FAIL HASH*]";
                summary->failed_params++;
                summary->overall_pass = false;
                break;
        }

        printf("%-22s | %-6s | %-8s | %-16s | %-8s | %-6s | %-6s | %-14s\n",
               specs[p].name, specs[p].unit, nominal_str, spec_range_str,
               mean_str, std_str, cpk_str, verdict_str);
    }

    printf("==================================================================================================\n");
    printf("ПІДСУМОК: Успішно: %zu | Попередження Cpk: %zu | Критичних дефектів: %zu\n",
           summary->passed_params, summary->warning_params, summary->failed_params);
    printf("ФІНАЛЬНИЙ СТАТУС ПАРТІЇ: %s\n", 
           summary->overall_pass ? 
               (summary->warning_params > 0 ? "УМОВНО СХВАЛЕНО (Потрібен контроль Cpk)" : 
                                              "ПОВНІСТЮ СХВАЛЕНО ДЛЯ СЕРІЙНОГО ВИПУСКУ") :
               "ВІДХИЛЕНО — ПАРТІЯ ЗАБЛОКОВАНА ДЛЯ ВІДВАНТАЖЕННЯ");
    printf("==================================================================================================\n\n");
}

/* Демонстраційний запуск валідатора */
int main(void) {
    fai_spec_item_t specs[5] = {
        {
            .name = "VCC_3V3 (Main Rail)",
            .unit = "V",
            .type = PARAM_TYPE_ANALOG_TWO_SIDED,
            .golden_nominal = 3.300,
            .lsl = 3.135,
            .usl = 3.465
        },
        {
            .name = "VCC_1V1 (Core Rail)",
            .unit = "V",
            .type = PARAM_TYPE_ANALOG_TWO_SIDED,
            .golden_nominal = 1.100,
            .lsl = 1.045,
            .usl = 1.155
        },
        {
            .name = "RTC_CLK (Frequency)",
            .unit = "kHz",
            .type = PARAM_TYPE_ANALOG_TWO_SIDED,
            .golden_nominal = 32.768,
            .lsl = 32.760,
            .usl = 32.776
        },
        {
            .name = "BGA_MCU_Voiding",
            .unit = "%",
            .type = PARAM_TYPE_UPPER_BOUND_ONLY,
            .golden_nominal = 5.0,
            .lsl = 0.0,
            .usl = 15.0
        },
        {
            .name = "FW_SHA256_Hash",
            .unit = "HEX",
            .type = PARAM_TYPE_DIGITAL_HASH,
            .golden_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        }
    };

    /* Синтетична вибірка з 10 плат першої партії */
    fai_board_record_t sample_boards[10];
    double vcc3v3_data[10] = {3.310, 3.305, 3.315, 3.302, 3.308, 3.312, 3.304, 3.309, 3.311, 3.306};
    double vcc1v1_data[10] = {1.102, 1.098, 1.101, 1.099, 1.103, 1.100, 1.097, 1.102, 1.101, 1.099};
    double rtc_data[10]    = {32.768, 32.769, 32.767, 32.768, 32.769, 32.768, 32.767, 32.768, 32.769, 32.768};
    double voids_data[10]  = {6.2, 7.1, 5.8, 8.4, 6.9, 7.5, 5.2, 6.8, 7.9, 6.4};

    for (size_t i = 0; i < 10; i++) {
        snprintf(sample_boards[i].board_serial, FAI_STR_LEN, "SN-2026-FA-%04zu", i + 1);
        sample_boards[i].analog_values[0] = vcc3v3_data[i];
        sample_boards[i].analog_values[1] = vcc1v1_data[i];
        sample_boards[i].analog_values[2] = rtc_data[i];
        sample_boards[i].analog_values[3] = voids_data[i];
        strncpy(sample_boards[i].hash_values[4], 
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 65);
    }

    fai_summary_t summary;
    fai_generate_report(specs, 5, sample_boards, 10, &summary);

    return summary.overall_pass ? 0 : 1;
}
```
```cpp
// =========================================================================
// fai_validator.cpp - Мова C++ (C++20)
// Ідіоматичний валідатор звітів першої виробничої партії (AS9102 Form 3)
// =========================================================================

#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <cmath>
#include <format>
#include <algorithm>
#include <numeric>
#include <expected>

namespace fai {

enum class ParamType {
    AnalogTwoSided,
    UpperBoundOnly,
    DigitalHash
};

enum class Verdict {
    Pass,
    WarningLowCpk,
    FailOutOfSpec,
    FailHashMismatch
};

struct SpecItem {
    std::string name;
    std::string unit;
    ParamType type;
    double golden_nominal{0.0};
    double lsl{0.0};
    double usl{0.0};
    std::string golden_hash{};

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        if (type == ParamType::AnalogTwoSided) return usl > lsl;
        if (type == ParamType::UpperBoundOnly) return usl > golden_nominal;
        return !golden_hash.empty();
    }
};

struct BoardRecord {
    std::string serial_number;
    std::vector<double> analog_measurements;
    std::vector<std::string> hash_measurements;
};

struct ParameterAnalysis {
    double mean{0.0};
    double std_dev{0.0};
    double cp{0.0};
    double cpu{0.0};
    double cpl{0.0};
    double cpk{0.0};
    double golden_drift{0.0};
    size_t out_of_spec_count{0};
    size_t outlier_count{0};
    Verdict verdict{Verdict::Pass};
};

struct BatchSummary {
    size_t total_boards{0};
    size_t total_params{0};
    size_t passed_params{0};
    size_t warning_params{0};
    size_t failed_params{0};
    bool overall_pass{true};
};

class Validator {
public:
    [[nodiscard]] static ParameterAnalysis analyze(const SpecItem& spec,
                                                   std::span<const BoardRecord> boards,
                                                   size_t param_idx) noexcept {
        ParameterAnalysis res{};

        if (spec.type == ParamType::DigitalHash) {
            for (const auto& b : boards) {
                if (param_idx < b.hash_measurements.size()) {
                    if (b.hash_measurements[param_idx] != spec.golden_hash) {
                        res.out_of_spec_count++;
                        res.verdict = Verdict::FailHashMismatch;
                    }
                } else {
                    res.out_of_spec_count++;
                    res.verdict = Verdict::FailHashMismatch;
                }
            }
            return res;
        }

        // Онлайн-накопичення статистики за алгоритмом Велфорда
        double mean = 0.0;
        double m2 = 0.0;
        size_t count = 0;

        for (const auto& b : boards) {
            if (param_idx >= b.analog_measurements.size()) continue;
            double val = b.analog_measurements[param_idx];
            ++count;
            double delta = val - mean;
            mean += delta / static_cast<double>(count);
            double delta2 = val - mean;
            m2 += delta * delta2;

            if (spec.type == ParamType::AnalogTwoSided) {
                if (val < spec.lsl || val > spec.usl) {
                    res.out_of_spec_count++;
                }
            } else if (spec.type == ParamType::UpperBoundOnly) {
                if (val > spec.usl) {
                    res.out_of_spec_count++;
                }
            }
        }

        double variance = (count > 1) ? (m2 / static_cast<double>(count - 1)) : 0.0;
        double std_dev = std::sqrt(variance);
        if (std_dev < 1e-9) {
            std_dev = 1e-9;
        }

        res.mean = mean;
        res.std_dev = std_dev;
        res.golden_drift = mean - spec.golden_nominal;

        // Пошук викидів за Z-критерієм
        for (const auto& b : boards) {
            if (param_idx >= b.analog_measurements.size()) continue;
            double val = b.analog_measurements[param_idx];
            double z = std::abs(val - mean) / std_dev;
            if (z > 3.5) {
                res.outlier_count++;
            }
        }

        // Обчислення індексів придатності процесу
        if (spec.type == ParamType::AnalogTwoSided) {
            double spec_width = spec.usl - spec.lsl;
            res.cp = spec_width / (6.0 * std_dev);
            res.cpu = (spec.usl - mean) / (3.0 * std_dev);
            res.cpl = (mean - spec.lsl) / (3.0 * std_dev);
            res.cpk = std::min(res.cpu, res.cpl);
        } else if (spec.type == ParamType::UpperBoundOnly) {
            res.cp = (spec.usl - spec.golden_nominal) / (3.0 * std_dev);
            res.cpu = (spec.usl - mean) / (3.0 * std_dev);
            res.cpl = 0.0;
            res.cpk = res.cpu;
        }

        if (res.out_of_spec_count > 0) {
            res.verdict = Verdict::FailOutOfSpec;
        } else if (res.cpk < 1.33) {
            res.verdict = Verdict::WarningLowCpk;
        } else {
            res.verdict = Verdict::Pass;
        }

        return res;
    }

    static BatchSummary generate_report(std::span<const SpecItem> specs,
                                        std::span<const BoardRecord> boards) {
        BatchSummary summary{
            .total_boards = boards.size(),
            .total_params = specs.size(),
            .passed_params = 0,
            .warning_params = 0,
            .failed_params = 0,
            .overall_pass = true
        };

        std::cout << "==================================================================================================\n";
        std::cout << "                    ПРОТОКОЛ ВАЛІДАЦІЇ ПЕРШОЇ ВИРОБНИЧОЇ ПАРТІЇ (AS9102 FORM 3)                  \n";
        std::cout << "==================================================================================================\n";
        std::cout << std::format("Розмір вибірки: N = {} плат | Кількість контрольованих параметрів: {}\n\n",
                                 boards.size(), specs.size());

        std::cout << std::format("{:<22} | {:<6} | {:<8} | {:<16} | {:<8} | {:<6} | {:<6} | {:<14}\n",
                                 "Параметр", "Один.", "Еталон", "Поле допуску", "Факт (μ)", "σ", "Cpk", "Вердикт");
        std::cout << "--------------------------------------------------------------------------------------------------\n";

        for (size_t p = 0; p < specs.size(); ++p) {
            const auto& spec = specs[p];
            auto analysis = analyze(spec, boards, p);

            std::string spec_range;
            std::string nominal_str;
            std::string mean_str;
            std::string std_str;
            std::string cpk_str;
            std::string verdict_str;

            if (spec.type == ParamType::DigitalHash) {
                spec_range = "Exact Match";
                nominal_str = "SHA-256";
                mean_str = "MATCH";
                std_str = "N/A";
                cpk_str = "N/A";
            } else {
                if (spec.type == ParamType::AnalogTwoSided) {
                    spec_range = std::format("[{:.3f}..{:.3f}]", spec.lsl, spec.usl);
                } else {
                    spec_range = std::format("[ <= {:.3f} ]", spec.usl);
                }
                nominal_str = std::format("{:.3f}", spec.golden_nominal);
                mean_str = std::format("{:.3f}", analysis.mean);
                std_str = std::format("{:.4f}", analysis.std_dev);
                cpk_str = std::format("{:.2f}", analysis.cpk);
            }

            switch (analysis.verdict) {
                case Verdict::Pass:
                    verdict_str = "[ PASS ]";
                    summary.passed_params++;
                    break;
                case Verdict::WarningLowCpk:
                    verdict_str = "[!CPK < 1.33!]";
                    summary.warning_params++;
                    break;
                case Verdict::FailOutOfSpec:
                    verdict_str = "[*FAIL OOS*]";
                    summary.failed_params++;
                    summary.overall_pass = false;
                    break;
                case Verdict::FailHashMismatch:
                    verdict_str = "[*FAIL HASH*]";
                    summary.failed_params++;
                    summary.overall_pass = false;
                    break;
            }

            std::cout << std::format("{:<22} | {:<6} | {:<8} | {:<16} | {:<8} | {:<6} | {:<6} | {:<14}\n",
                                     spec.name, spec.unit, nominal_str, spec_range,
                                     mean_str, std_str, cpk_str, verdict_str);
        }

        std::cout << "==================================================================================================\n";
        std::cout << std::format("ПІДСУМОК: Успішно: {} | Попередження Cpk: {} | Критичних дефектів: {}\n",
                                 summary.passed_params, summary.warning_params, summary.failed_params);
        
        std::string final_status = summary.overall_pass ? 
            (summary.warning_params > 0 ? "УМОВНО СХВАЛЕНО (Потрібен контроль Cpk)" : 
                                          "ПОВНІСТЮ СХВАЛЕНО ДЛЯ СЕРІЙНОГО ВИПУСКУ") :
            "ВІДХИЛЕНО — ПАРТІЯ ЗАБЛОКОВАНА ДЛЯ ВІДВАНТАЖЕННЯ";
        std::cout << std::format("ФІНАЛЬНИЙ СТАТУС ПАРТІЇ: {}\n", final_status);
        std::cout << "==================================================================================================\n\n";

        return summary;
    }
};

} // namespace fai

int main() {
    std::vector<fai::SpecItem> specs = {
        {
            .name = "VCC_3V3 (Main Rail)",
            .unit = "V",
            .type = fai::ParamType::AnalogTwoSided,
            .golden_nominal = 3.300,
            .lsl = 3.135,
            .usl = 3.465
        },
        {
            .name = "VCC_1V1 (Core Rail)",
            .unit = "V",
            .type = fai::ParamType::AnalogTwoSided,
            .golden_nominal = 1.100,
            .lsl = 1.045,
            .usl = 1.155
        },
        {
            .name = "RTC_CLK (Frequency)",
            .unit = "kHz",
            .type = fai::ParamType::AnalogTwoSided,
            .golden_nominal = 32.768,
            .lsl = 32.760,
            .usl = 32.776
        },
        {
            .name = "BGA_MCU_Voiding",
            .unit = "%",
            .type = fai::ParamType::UpperBoundOnly,
            .golden_nominal = 5.0,
            .lsl = 0.0,
            .usl = 15.0
        },
        {
            .name = "FW_SHA256_Hash",
            .unit = "HEX",
            .type = fai::ParamType::DigitalHash,
            .golden_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        }
    };

    std::vector<fai::BoardRecord> sample_boards(10);
    std::vector<double> vcc3v3 = {3.310, 3.305, 3.315, 3.302, 3.308, 3.312, 3.304, 3.309, 3.311, 3.306};
    std::vector<double> vcc1v1 = {1.102, 1.098, 1.101, 1.099, 1.103, 1.100, 1.097, 1.102, 1.101, 1.099};
    std::vector<double> rtc    = {32.768, 32.769, 32.767, 32.768, 32.769, 32.768, 32.767, 32.768, 32.769, 32.768};
    std::vector<double> voids  = {6.2, 7.1, 5.8, 8.4, 6.9, 7.5, 5.2, 6.8, 7.9, 6.4};

    for (size_t i = 0; i < 10; ++i) {
        sample_boards[i].serial_number = std::format("SN-2026-FA-{:04d}", i + 1);
        sample_boards[i].analog_measurements = {vcc3v3[i], vcc1v1[i], rtc[i], voids[i]};
        sample_boards[i].hash_measurements = {
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        };
    }

    auto summary = fai::Validator::generate_report(specs, sample_boards);
    return summary.overall_pass ? 0 : 1;
}
```
:::

### Інженерна діагностика типових виробничих дефектів

За результатами роботи валідатора інженерний персонал отримує вичерпну діагностичну інформацію, що дозволяє швидко локалізувати фізичну причину відхилення:

1. **Сценарій «Високий Cp, але низький Cpk» (`Cp = 2.40`, `Cpk = 1.15`):**
   - *Фізична суть:* дисперсія технологічного процесу є мінімальною (верстати працюють стабільно, розкид деталей малий), але середнє значення зміщене в бік однієї з меж допуску.
   - *Діагностика:* систематична похибка номіналу в схемотехніці (наприклад, помилка розрахунку дільника зворотного зв'язку DC-DC стабілізатора або неврахування внутрішнього опору вимірювальних щупів).
   - *Дія:* коригування номіналів резисторів у специфікації BOM без зупинки чи переналаштування механіки SMT-лінії.
2. **Сценарій «Низький Cp та низький Cpk» (`Cp = 1.05`, `Cpk = 0.98`):**
   - *Фізична суть:* середнє значення розташоване точно в центрі поля допуску, але розкид вимірювань є надмірно широким.
   - *Діагностика:* фізична нестабільність процесу на фабриці. Можливі причини: нерівномірне нанесення припойної пасти (знос ракеля трафаретного принтера), флуктуація температури в пічці оплавлення або використання неякісних пасивних компонентів із широким розкидом номіналів (±20% замість прецизійних ±1%).
   - *Дія:* аварійна зупинка лінії, повна ревізія температурного профілю печі та перевірка вхідного контролю компонентів.
3. **Сценарій «Одиничний статистичний викид» (`Z-Score > 3.5` при `Cpk = 1.85`):**
   - *Фізична суть:* 99% виробів демонструють ідеальну якість, але одна плата має значне відхилення.
   - *Діагностика:* локальний дефект пайки (мікротріщина у виводі, холодний непропай) або випадковий збій контакту тестової голки.
   - *Дія:* відправка дефектної плати на повторне рентгенівське дослідження та візуальний огляд під мікроскопом без блокування всієї партії.
4. **Сценарій «Невідповідність цифрового хешу» (`STATUS_FAIL_HASH_MISMATCH`):**
   - *Фізична суть:* електричні параметри в нормі, але зчитаний бінарний образ прошивки або бутлоадера відрізняється від Golden Sample.
   - *Діагностика:* помилка вибору версії прошивки на заводському сервері, заливка незахищеного налагоджувального образу (Debug Build) замість фінального (Release) або випадкове пошкодження флеш-пам'яті під час прошивання.
   - *Дія:* негайне блокування відвантаження та повторне автоматичне перепрошивання всієї партії з обов'язковою верифікацією бітів Option Bytes / eFuse.

### Ненормальні розподіли та емпіричні квантилі

Хоча більшість аналогових характеристик (напруга, опір, частота) підпорядковуються нормальному закону Гауса, окремі фізичні параметри за своєю природою мають суттєво скошені або асиметричні розподіли. Типовими прикладами є:
- **Струми витоку в режимі очікування (Quiescent Leakage Currents):** підпорядковуються логнормальному розподілу через експоненційну залежність струму підпорогової провідності польових транзисторів від технологічних флуктуацій довжини каналу та температури.
- **Відсоток газових пустот у пайці (BGA / QFN Voiding Percentage):** фізично обмежений нулем зліва, має довгий «правий хвіст» і описується розподілом Вейбулла або гамма-розподілом.
- **ВЧ джитер та фазовий шум (Clock Jitter):** має екстремальні викиди, пов'язані з інтерференцією перехідних процесів шин даних.

Застосування класичної формули `Cpk = (USL - mu) / (3·sigma)` до ненормальних даних призводить до серйозних помилок: розрахований індекс може показувати високу придатність `Cpk = 1.6`, тоді як реальний відсоток браку в правому хвості розподілу перевищуватиме сотні DPMO.

Для коректної обробки таких параметрів валідатор підтримує два альтернативні інженерні методи:

1. **Трансформація Бокса-Кокса (Box-Cox Power Transformation):**
   Масив вимірювань `x` перетворюється у нормалізовану шкалу `y` за формулою:
   ```
   y(λ) = (x^λ - 1) / λ,      якщо λ ≠ 0
   y(λ) = ln(x),             якщо λ = 0
   ```
   Параметр `lambda` підбирається методом максимальної правдоподібності. Після цього межі специфікації перераховуються у трансформовану шкалу, де обчислюється стандартний `Cpk`.
2. **Непараметричні індекси за емпіричними процентилями (ISO 21747 / DIN 55319):**
   Замість оцінок `mu ± 3·sigma` використовуються емпіричні квантилі вибірки `P[0.135%]`, `P[50%]` (медіана) та `P[99.865%]`, що відповідають теоретичним точкам трьох сигм нормального розподілу:
   ```
          USL - P[50%]
   Cpu = ─────────────────
         P[99.865%] - P[50%]

          P[50%] - LSL
   Cpl = ─────────────────
         P[50%] - P[0.135%]

   Cpk = min(Cpu, Cpl)
   ```

### Юридичний протокол врегулювання розбіжностей між OEM та EMS

Згенерований валідатором звіт Form 3 є не лише технічним документом, але й головним правовим інструментом взаємодії між замовником розробки (OEM) та контрактним виробником (EMS).

У разі блокування партії за результатами FAI впроваджується формалізований регламент арбітражу:

1. **Оформлення акта про невідповідність (Discrepancy Report):**
   - Усі виявлені точки виходу за межі допуску або параметри з `Cpk < 1.33` вивантажуються у структурований протокол невідповідностей.
   - Завод зобов'язаний надати офіційне інженерне пояснення корінної причини дефекту за методикою 8D (*Eight Disciplines Problem Solving*) або аналізу діаграми Ісікави протягом 48 годин.
2. **Розмежування відповідальності сторін:**
   - Якщо дефект викликаний відхиленням температурного профілю, зносом сопел автомата PnP або порушенням правил вхідного контролю компонентів заводом — усі витрати на переробку, доопрацювання та повторне проведення FAI покладаються на виробника (EMS).
   - Якщо аналіз показує, що завод виконав монтаж строго за наданою документацією, але розкид номіналів компонентів у схемі розробника не залишає технологічного запасу для нормальної дисперсії лінії — відповідальність несе замовник (OEM), який зобов'язаний випустити інженерне повідомлення про зміну (ECO) з розширенням полів допусків або коригуванням номіналів.
3. **Підписання фінального акта FAI та запечатування зразків:**
   - Після усунення всіх зауважень головні інженери з якості обох сторін ставлять персональні електронні підписи під підсумковим звітом Form 1, 2, 3.
   - Плати, що слугували основою для розрахунку FAI, отримують сертифікат відповідності, а відібраний Golden Sample опломбовується та вирушає до азотного сховища, відкриваючи шлях до повномасштабного масового серійного випуску.

### Прив'язка до креслень та нумерація характерних точок (Balloon Drawing)

Стандарт AS9102 Form 3 вимагає обов'язкової наявності креслення з круговими мітками (*Balloon Drawing* або *Bubble Chart*), де кожен виміряний параметр пов'язаний з фізичною координатою на складальному кресленні друкованого вузла:

| Номер мітки (Bubble #) | Позиційне позначення (RefDes) | Координати X/Y (мм) | Тип контролю | Інструмент вимірювання |
|:---:|:---:|:---:|:---:|:---:|
| **①** | `TP101` (VCC_3V3) | X: 14.50, Y: 22.10 | Напруга в контрольних точках | Прецизійний DMM Keithley 2000 |
| **②** | `TP102` (VCC_1V1) | X: 18.20, Y: 35.40 | Напруга ядра процесора | Прецизійний DMM Keithley 2000 |
| **③** | `Y101` (RTC_CLK) | X: 42.00, Y: 15.80 | Частота генерації та форма сигналу | Осцилограф Keysight Infiniium |
| **④** | `U101` (MCU BGA-144) | X: 50.00, Y: 50.00 | Відсоток порожнин під виводами | Рентгенівський томограф Dage Quadra 5 |
| **⑤** | `U201` (SPI Flash) | X: 65.20, Y: 48.00 | Контрольна сума прошивки | Заводський програматор Segger Flasher |

Така структурована перехресна адресація усуває будь-яку двозначність під час локалізації браку на виробничій лінії та забезпечує повну метрологічну простежуваність FAI-звіту. Кожен вимірювальний прилад повинен мати дійсне свідоцтво про повірку та калібрування за стандартом ISO/IEC 17025.

