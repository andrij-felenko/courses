# ⚙️ Імпортер технологічних правил фабрики в правила DRC

Коли інженер розробляє друковану плату для серійного виробництва або переносить готовий проєкт від одного контрактного виробника до іншого (наприклад, перемикає замовлення з JLCPCB на PCBWay або Eurocircuits), ручне переналаштування десятків числових параметрів у діалогових вікнах САПР майже неминуче призводить до помилок. Достатньо забути змінити зазор від міді до краю плати з 0.25 мм на 0.50 мм при переході на скрайбування (V-cut) або помилитися в перерахунку одиниць вимірювання (mils у міліметри для мінімального пояска металізації), щоб завод повернув замовлення на стадії попередньої перевірки або виготовив браковану партію.

Цей інструмент автоматизує трансляцію технологічних специфікацій фабрик друкованих плат (PCB Capabilities) у файли правил системи автоматизованого проєктування (САПР), генеруючи готові правила користувацької перевірки правил проєктування (Custom Design Rule Check, DRC) для САПР KiCad 8/9 (у форматі `.kicad_dru`) та Altium Designer.

## Постановка задачі та інженерні вимоги

Сучасне виробництво друкованих плат спирається на жорстко стандартизовані параметри виробничих ліній. Кожен завод публікує технологічну таблицю обмежень (англ. *PCB Capabilities Matrix*), де зазначаються фізичні ліміти фотолітографії, свердління, нанесення маски та механічної обробки заготовок. Проте ці обмеження не є статичними: вони залежать від кількості шарів у структурі (Layer Stackup), товщини базової мідної фольги (0.5 oz, 1.0 oz, 2.0 oz), типу діелектрика (FR-4 Standard Tg, High Tg, Rogers), кольору паяльної маски та обраного способу панелізації (фрезерування чи скрайбування).

У процесі проєктування інженер стикається з трьома критичними проблемами узгодження САПР і фабрики:

1. **Людський фактор і розкид параметрів:** у типовій САПР правила трасування розкидані між кількома різними меню — глобальними налаштуваннями плати (Board Setup), властивостями класів кіл (Net Classes), генератором паяльної маски (Solder Mask Defaults) та конфігурацією заливки полігонів (Zone Defaults). Під час переходу між фабриками ручна зміна 20–30 окремих полів забирає час і створює ризик пропуску одиничного параметра (наприклад, мінімального зазору між перехідними отворами Hole-to-Hole).
2. **Конфлікт одиниць вимірювання (Imperial vs Metric):** закордонні фабрики часто публікують специфікації в тисячних долях дюйма (mils), тоді як європейські заводи та сучасні стандарти IPC працюють у міліметрах (мм). Неточне округлення при ручному введенні (наприклад, запис 6 mil як 0.150 мм замість точних 0.1524 мм) призводить до хибних спрацьовувань або пропуску мікропорушень.
3. **Автоматизація в конвеєрах неперервної інтеграції (CI/CD):** сучасні команди розробки апаратного забезпечення використовують автоматичні перевірки герберів та топології на серверах CI/CD (GitHub Actions, GitLab CI) за допомогою консольних утиліт (`kicad-cli pcb drc`). Для такої автоматизації файл правил DRC повинен генеруватися динамічно залежно від обраного цільового профілю виробництва без участі графічного інтерфейсу САПР.

Інструмент повинен вирішувати такі задачі:
- Зберігати стандартизовані технологічні профілі провідних світових фабрик (JLCPCB 2-Layer 1oz Standard, JLCPCB 4-Layer 0.5oz Advanced, PCBWay Standard, Eurocircuits Standard Pool).
- Підтримувати параметричне перевизначення товщини міді (1 oz, 2 oz, 3 oz) з автоматичним масштабуванням мінімальної ширини провідників та зазорів за законом фактора травлення.
- Генерувати синтаксично валідні файли `.kicad_dru`, що містять повний набір перевірок:
  - Мінімальна ширина провідників (Min Track Width);
  - Мінімальний зазор між провідниками (Min Clearance);
  - Мінімальний діаметр свердла (Min Drill Diameter);
  - Мінімальний радіальний поясок металізації (Min Annular Ring);
  - Мінімальний місток паяльної маски (Min Solder Mask Dam);
  - Відступ міді до краю плати для фрезерування (Edge Milling Clearance);
  - Відступ міді до осі скрайбування (V-cut Scoring Clearance);
  - Мінімальний зазор між отворами (Hole-to-Hole Clearance);
  - Відступ шовкографії від паяльних майданчиків (Silk-to-Mask Clearance);
  - Геометрія оптичних реперів (Fiducial Marks Clearance);
  - Зазори для диференційних пар із контрольованим імпедансом (Diff Pair Gap).
- Працювати у двох режимах: як вбудована бібліотека для автоматизованих конвеєрів CI/CD та як автономна консольна утиліта (CLI).

---

## Архітектура та модель даних

Архітектура утиліти побудована за модульним принципом із розділенням бази знань технологічних норм, розрахункового ядра масштабування фізичних параметрів та спеціалізованих серіалізаторів під конкретні САПР:

```
 ┌────────────────────────────────────────────────────────┐
 │           1. База технологічних профілів              │
 │   (JLCPCB Standard, JLCPCB Advanced, PCBWay, Euro)     │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │      2. Ядро валідації та масштабування норм           │
 │  (Корекція під товщину міді, перерахунок одиниць)      │
 └───────────────────────────┬────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
 ┌──────────────────────┐          ┌──────────────────────┐
 │  3a. Генератор       │          │  3b. Генератор       │
 │  KiCad 8/9 DRC       │          │  Altium DRC          │
 │  (.kicad_dru)        │          │  (Query Export)      │
 └──────────────────────┘          └──────────────────────┘
```

### Модель параметрів технологічного профілю

Кожен технологічний профіль фабрики містить структурований набір фізичних констант виробничого процесу:

```
Parameter               Unit     Description
──────────────────────────────────────────────────────────────────────────
name                    string   Назва фабрики та технологічного класу
tier_name               string   Рівень складності (Standard Pool, Advanced)
copper_oz               float    Базова товщина фольги (0.5, 1.0, 2.0, 3.0 oz)
min_track_width         mm       Мінімальна ширина сигнальної доріжки
min_track_space         mm       Мінімальний зазор між доріжками
min_drill_dia           mm       Мінімальний діаметр механічного свердла
min_annular_ring        mm       Мінімальна ширина пояска металізації (AR)
mask_expansion          mm       Технологічний зазор маски до міді
min_mask_dam            mm       Мінімальна ширина містка маски між майданчиками
min_edge_milling        mm       Зазор міді до фрезерованого краю контуру
min_edge_vcut           mm       Зазор міді до осі скрайбування (V-cut)
min_hole_to_hole        mm       Мінімальна відстань між краями отворів
min_silk_width          mm       Мінімальна товщина лінії шовкографії
min_silk_clearance      mm       Мінімальний відступ шовкографії від маски
fiducial_edge_clear     mm       Відступ оптичного репера від краю плати
max_aspect_ratio        float    Граничне співвідношення товщини плати до свердла
```

### Синтаксис користувацьких правил KiCad 8/9 (.kicad_dru)

Система користувацьких правил KiCad використовує деревоподібний синтаксис S-виразів. Кожне правило складається з унікального ідентифікатора, пріоритету, одного або кількох числових обмежень (`constraint`) та логічної умови (`condition`), що оцінюється для пари топологічних об'єктів `A` і `B`:

```lisp
(rule "Factory_Min_Clearance"
  (priority 100)
  (constraint clearance (min 0.150mm))
  (condition "A.NetClass != B.NetClass"))
```

У цьому виразі:
- `(priority 100)` визначає порядок оцінки правила: чим вище число, тим раніше правило перевіряється геометричним рушієм. Це дозволяє створювати загальні правила низького пріоритету (priority 10) і специфічні винятки високого пріоритету (priority 200) для BGA-чипів чи диференційних ліній.
- `constraint clearance (min 0.150mm)` вказує ядру геометричного аналізатора перевіряти відстань між контурами провідників і генерувати помилку DRC, якщо відстань менша за 0.150 мм.
- `condition "A.NetClass != B.NetClass"` обмежує дію правила лише об'єктами, що належать до різних електричних кіл, дозволяючи провідникам одного кола з'єднуватися без створення помилок.

Для перевірки відступів до контуру плати використовується обмеження `edge_clearance`:

```lisp
(rule "Factory_Edge_Milling_Clearance"
  (priority 150)
  (constraint edge_clearance (min 0.300mm))
  (condition "A.Type == 'Track' || A.Type == 'Zone' || A.Type == 'Pad'"))
```

Для контролю мікротріщин діелектрика між сусідніми отворами використовується обмеження `hole_clearance`:

```lisp
(rule "Factory_Hole_To_Hole_Clearance"
  (priority 120)
  (constraint hole_clearance (min 0.500mm))
  (condition "A.Type == 'Via' || A.Type == 'Pad'"))
```

---

## Порівняльний аналіз профілів фабрик-виробників

Утиліта містить чотири еталонні профілі, що покривають типові сценарії контрактного виробництва:

1. **JLCPCB Standard (1–2 Layer, 1 oz):**
   - Найдешевший пул для швидкого прототипування.
   - Мінімальні норми трасування: `0.15 мм / 0.15 мм` (6/6 mil).
   - Мінімальне свердло: `0.30 мм` (12 mil), поясок металізації `0.15 мм`.
   - Зазор маски: розширення `0.05 мм`, місток `0.10 мм` (для зеленої маски).
   - Відступ до краю: `0.30 мм` при фрезеруванні, `0.50 мм` при скрайбуванні.
   - Зазор між отворами: `0.50 мм` (20 mil) між краями просвердлених отворів.

2. **JLCPCB Advanced (4–6 Layer, 0.5 oz):**
   - Високощільний монтаж (BGA, QFN 0.4 мм, швидкісні шини DDR/PCIe).
   - Використовує лазерне пряме експонування (LDI) та фольгу 0.5 oz (H oz).
   - Мінімальні норми трасування: `0.09 мм / 0.09 мм` (3.5/3.5 mil).
   - Мінімальне свердло: `0.15 мм` (лазерне мікросвердло) або `0.20 мм` (механічне), поясок `0.10 мм` (4 mil).
   - Зазор маски: розширення `0.03 мм`, місток `0.08 мм`.
   - Зазор між отворами: `0.40 мм`.

3. **PCBWay Standard Production (1 oz):**
   - Промисловий стандарт для дрібносерійного та серійного виробництва.
   - Трасування: `0.15 мм / 0.15 мм` (6/6 mil).
   - Свердло: `0.30 мм`, поясок `0.15 мм`.
   - Відступ до краю: `0.25 мм` при контурному фрезеруванні.
   - Зазор між отворами: `0.50 мм`.

4. **Eurocircuits Standard Pool (1 oz):**
   - Європейський стандарт промислової надійності (класифікація за класами шаблонів Pattern Class 6 і Drill Class B).
   - Трасування: `0.15 мм / 0.15 мм`.
   - Свердло: `0.25 мм` (10 mil), поясок `0.125 мм` (5 mil).
   - Суворий контроль розширення маски: `0.04 мм`, мінімальний місток `0.10 мм`.
   - Відступ до фрезерованого контуру: `0.25 мм`, відступ до V-cut: `0.45 мм`.

---

## Генерація правил для Altium Designer

Окрім синтаксису KiCad, утиліта підтримує експорт правил у форматі запитів Altium Designer (Query Language).

В Altium Designer правила перевірки конфігуруються у вигляді текстових запитів над множинами топологічних об'єктів:
- **Мінімальний зазор (Clearance Constraint):**
```
Rule: Clearance_Factory_Min
Where First Object Matches: All
Where Second Object Matches: All
Constraints: Min Clearance = 0.150mm
```
- **Правило для полігонів живлення біля краю плати (Plane Pullback):**
```
Rule: Plane_Pullback_Edge
Where First Object Matches: InNetClass('Power') And IsZone
Where Second Object Matches: Touch(All, 'BoardOutline')
Constraints: Min Clearance = 0.500mm
```
- **Мінімальний поясок перехідних отворів (Via Annular Ring):**
```
Rule: Via_Min_Annular_Ring
Where First Object Matches: IsVia
Constraints: Min Annular Ring = 0.150mm
```

---

## Контроль імпедансу, оптичні репери та тестові точки

Окрім базових норм трасування, професійні виробничі правила охоплюють високочастотні та складальні вимоги:

### 1. Диференційні пари з контрольованим імпедансом (Controlled Impedance)

Для сигнальних інтерфейсів USB 2.0/3.0, Ethernet та HDMI фабрика надає стандартизовані структури шарів (Stackups) із фіксованою діелектричною проникністю препрегів (`ε_r ≈ 4.2–4.5` для FR-4) та товщиною діелектрика над опорним шаром `H`.

Генератор транслює ці параметри в обмеження зазору та ширини диференційних провідників:

```lisp
(rule "Diff_Pair_USB90_Constraint"
  (priority 180)
  (constraint diff_pair_gap (min 0.120mm) (opt 0.150mm) (max 0.180mm))
  (condition "A.NetClass == 'USB90'"))
```

### 2. Оптичні репери (Fiducial Marks)

Автоматичні постановники компонентів (Pick and Place) орієнтуються за оптичними мітками — круглими мідними дисками діаметром 1.0 мм, оточеними круглим відкритим вікном маски діаметром 2.0 мм.
- Правило DFM вимагає, щоб оптичні репери розташовувалися на відстані не менше `5.0 мм` від краю плати (зони захоплення конвеєра монтажної лінії).
- Забороняється нанесення шовкографії ближче ніж `1.0 мм` до відкритої зони репера, щоб не збивати оптичну систему розпізнавання камер.

### 3. Тестові точки для автоматичного контролю (In-Circuit Testing — ICT)

Для перевірки змонтованих плат за допомогою голчастих адаптерів (Bed of Nails) правила проєктування накладають обмеження:
- Діаметр тестового майданчика: `≥ 0.80–1.00 мм`.
- Крок між тестовими точками (Pitch): `≥ 1.27–2.54 мм` (50–100 mil).
- Зазор до високих компонентів (висотою понад 4 мм): `≥ 1.50 мм` для запобігання пошкодженню голками корпусу мікросхем.

---

## Повна програмна реалізація: C99 та C++20

Нижче наведено повну реалізацію конвертера мовами C (C99) та C++ (C++20). Програма формує файл правил `.kicad_dru` для САПР KiCad та демонструє параметричну генерацію для різних фабрик.

:::tabs
@tab C (C99)
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

/* Структура технологічних обмежень виробника друкованих плат */
typedef struct {
    const char *factory_name;
    const char *tier_name;
    double copper_oz;           /* 0.5, 1.0, 2.0 oz */
    double min_track_width;     /* мм */
    double min_track_space;     /* мм */
    double min_drill_dia;       /* мм */
    double min_annular_ring;    /* мм */
    double mask_expansion;      /* мм */
    double min_mask_dam;        /* мм */
    double min_edge_milling;    /* мм */
    double min_edge_vcut;       /* мм */
    double min_hole_to_hole;    /* мм */
    double min_silk_width;      /* мм */
    double min_silk_clearance;  /* мм */
    double fiducial_edge_clear; /* мм */
    double max_aspect_ratio;    /* наприклад, 8.0 або 10.0 */
} factory_profile_t;

/* Вбудовані пресети виробничих ліній */
static const factory_profile_t PROFILES[] = {
    {
        .factory_name = "JLCPCB",
        .tier_name = "Standard 1-2 Layer (1 oz)",
        .copper_oz = 1.0,
        .min_track_width = 0.150,    /* 6.0 mil */
        .min_track_space = 0.150,    /* 6.0 mil */
        .min_drill_dia = 0.300,      /* 12.0 mil */
        .min_annular_ring = 0.150,   /* 6.0 mil */
        .mask_expansion = 0.050,     /* 2.0 mil */
        .min_mask_dam = 0.100,       /* 4.0 mil */
        .min_edge_milling = 0.300,   /* 12.0 mil */
        .min_edge_vcut = 0.500,      /* 20.0 mil */
        .min_hole_to_hole = 0.500,   /* 20.0 mil */
        .min_silk_width = 0.150,     /* 6.0 mil */
        .min_silk_clearance = 0.150, /* 6.0 mil */
        .fiducial_edge_clear = 5.000,/* 5.0 мм */
        .max_aspect_ratio = 8.0
    },
    {
        .factory_name = "JLCPCB",
        .tier_name = "Advanced 4-6 Layer (0.5 oz)",
        .copper_oz = 0.5,
        .min_track_width = 0.090,    /* 3.5 mil */
        .min_track_space = 0.090,    /* 3.5 mil */
        .min_drill_dia = 0.150,      /* 6.0 mil */
        .min_annular_ring = 0.100,   /* 4.0 mil */
        .mask_expansion = 0.030,     /* 1.2 mil */
        .min_mask_dam = 0.080,       /* 3.1 mil */
        .min_edge_milling = 0.200,   /* 8.0 mil */
        .min_edge_vcut = 0.400,      /* 16.0 mil */
        .min_hole_to_hole = 0.400,   /* 16.0 mil */
        .min_silk_width = 0.120,     /* 4.7 mil */
        .min_silk_clearance = 0.120, /* 4.7 mil */
        .fiducial_edge_clear = 4.000,
        .max_aspect_ratio = 10.0
    },
    {
        .factory_name = "PCBWay",
        .tier_name = "Standard Production (1 oz)",
        .copper_oz = 1.0,
        .min_track_width = 0.150,
        .min_track_space = 0.150,
        .min_drill_dia = 0.300,
        .min_annular_ring = 0.150,
        .mask_expansion = 0.050,
        .min_mask_dam = 0.100,
        .min_edge_milling = 0.250,
        .min_edge_vcut = 0.500,
        .min_hole_to_hole = 0.500,
        .min_silk_width = 0.150,
        .min_silk_clearance = 0.150,
        .fiducial_edge_clear = 5.000,
        .max_aspect_ratio = 8.0
    },
    {
        .factory_name = "Eurocircuits",
        .tier_name = "Standard Pool (1 oz)",
        .copper_oz = 1.0,
        .min_track_width = 0.150,
        .min_track_space = 0.150,
        .min_drill_dia = 0.250,      /* 10.0 mil */
        .min_annular_ring = 0.125,   /* 5.0 mil */
        .mask_expansion = 0.040,     /* 1.6 mil */
        .min_mask_dam = 0.100,
        .min_edge_milling = 0.250,
        .min_edge_vcut = 0.450,
        .min_hole_to_hole = 0.450,
        .min_silk_width = 0.150,
        .min_silk_clearance = 0.125,
        .fiducial_edge_clear = 5.000,
        .max_aspect_ratio = 8.5
    }
};

static const size_t NUM_PROFILES = sizeof(PROFILES) / sizeof(PROFILES[0]);

/* Генерація файлу правил .kicad_dru для САПР KiCad 8/9 */
bool export_kicad_dru(const factory_profile_t *p, const char *filepath) {
    if (!p || !filepath) return false;

    FILE *f = fopen(filepath, "w");
    if (!f) {
        perror("Не вдалося відкрити файл для запису");
        return false;
    }

    /* Заголовок та метадані */
    fprintf(f, ";; ===================================================================\n");
    fprintf(f, ";; KiCad 8/9 Custom DRC Rules\n");
    fprintf(f, ";; Factory Profile: %s - %s\n", p->factory_name, p->tier_name);
    fprintf(f, ";; Copper Weight: %.1f oz | Max Aspect Ratio: %.1f:1\n", p->copper_oz, p->max_aspect_ratio);
    fprintf(f, ";; Generated automatically by DFM Rules Importer\n");
    fprintf(f, ";; ===================================================================\n\n");
    fprintf(f, "(version 1)\n\n");

    /* 1. Мінімальна ширина провідників */
    fprintf(f, "(rule \"Factory_Min_Track_Width\"\n");
    fprintf(f, "  (priority 100)\n");
    fprintf(f, "  (constraint track_width (min %.3fmm))\n", p->min_track_width);
    fprintf(f, "  (condition \"A.Type == 'Track'\"))\n\n");

    /* 2. Мінімальний ізоляційний зазор */
    fprintf(f, "(rule \"Factory_Min_Clearance\"\n");
    fprintf(f, "  (priority 100)\n");
    fprintf(f, "  (constraint clearance (min %.3fmm))\n", p->min_track_space);
    fprintf(f, "  (condition \"A.NetClass != B.NetClass\"))\n\n");

    /* 3. Мінімальний діаметр свердла */
    fprintf(f, "(rule \"Factory_Min_Drill\"\n");
    fprintf(f, "  (priority 110)\n");
    fprintf(f, "  (constraint hole_size (min %.3fmm))\n", p->min_drill_dia);
    fprintf(f, "  (condition \"A.Type == 'Via' || A.Type == 'Pad'\"))\n\n");

    /* 4. Мінімальний поясок металізації (Annular Ring) */
    fprintf(f, "(rule \"Factory_Min_Annular_Ring\"\n");
    fprintf(f, "  (priority 110)\n");
    fprintf(f, "  (constraint annular_width (min %.3fmm))\n", p->min_annular_ring);
    fprintf(f, "  (condition \"A.Type == 'Via'\"))\n\n");

    /* 5. Відступ міді до контуру плати (фрезерування) */
    fprintf(f, "(rule \"Factory_Edge_Milling_Clearance\"\n");
    fprintf(f, "  (priority 120)\n");
    fprintf(f, "  (constraint edge_clearance (min %.3fmm))\n", p->min_edge_milling);
    fprintf(f, "  (condition \"A.Type == 'Track' || A.Type == 'Zone' || A.Type == 'Pad'\"))\n\n");

    /* 6. Спеціальне правило для зон скрайбування (V-Cut) */
    fprintf(f, "(rule \"Factory_VCut_Scoring_Clearance\"\n");
    fprintf(f, "  (priority 130)\n");
    fprintf(f, "  (constraint edge_clearance (min %.3fmm))\n", p->min_edge_vcut);
    fprintf(f, "  (condition \"A.Type == 'Zone' && A.NetClass == 'Power'\"))\n\n");

    /* 7. Зазор між отворами (Hole-to-Hole) */
    fprintf(f, "(rule \"Factory_Hole_To_Hole\"\n");
    fprintf(f, "  (priority 105)\n");
    fprintf(f, "  (constraint hole_clearance (min %.3fmm))\n", p->min_hole_to_hole);
    fprintf(f, "  (condition \"A.Type == 'Via' || A.Type == 'Pad'\"))\n\n");

    /* 8. Відступ шовкографії від паяльних майданчиків */
    fprintf(f, "(rule \"Factory_Silk_To_Mask_Clearance\"\n");
    fprintf(f, "  (priority 90)\n");
    fprintf(f, "  (constraint silk_clearance (min %.3fmm))\n", p->min_silk_clearance);
    fprintf(f, "  (condition \"A.Type == 'Graphic' && A.Layer == 'F.SilkS'\"))\n\n");

    /* 9. Відступ оптичних реперів від краю плати */
    fprintf(f, "(rule \"Factory_Fiducial_Edge_Clearance\"\n");
    fprintf(f, "  (priority 140)\n");
    fprintf(f, "  (constraint edge_clearance (min %.3fmm))\n", p->fiducial_edge_clear);
    fprintf(f, "  (condition \"A.Type == 'Footprint' && A.Reference == 'FID*'\"))\n\n");

    fclose(f);
    return true;
}

int main(int argc, char *argv[]) {
    printf("=== DFM Rules Importer CLI (C99) ===\n\n");

    if (argc < 2) {
        printf("Використання: %s <індекс_профілю> [вихідний_файл.kicad_dru]\n", argv[0]);
        printf("Доступні профілі фабрик:\n");
        for (size_t i = 0; i < NUM_PROFILES; ++i) {
            printf("  [%zu] %s — %s (Мідь: %.1f oz, Min W/S: %.2f/%.2f мм)\n",
                   i, PROFILES[i].factory_name, PROFILES[i].tier_name,
                   PROFILES[i].copper_oz, PROFILES[i].min_track_width, PROFILES[i].min_track_space);
        }
        return 1;
    }

    size_t idx = (size_t)atoi(argv[1]);
    if (idx >= NUM_PROFILES) {
        fprintf(stderr, "Помилка: некоректний індекс профілю %zu (діапазон 0..%zu)\n", idx, NUM_PROFILES - 1);
        return 1;
    }

    const char *outfile = (argc >= 3) ? argv[2] : "factory_rules.kicad_dru";
    const factory_profile_t *p = &PROFILES[idx];

    printf("Експорт профілю '%s (%s)' у файл '%s'...\n", p->factory_name, p->tier_name, outfile);
    if (export_kicad_dru(p, outfile)) {
        printf("Файл правил успішно згенеровано!\n");
        return 0;
    } else {
        fprintf(stderr, "Помилка під час генерації файлу!\n");
        return 1;
    }
}
```
@tab C++ (C++20)
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <format>
#include <span>

namespace dfm_importer {

/* Опис технологічного профілю виробника друкованих плат */
struct FactoryProfile {
    std::string_view factory_name;
    std::string_view tier_name;
    double copper_oz{1.0};           // 0.5, 1.0, 2.0 oz
    double min_track_width{0.150};    // мм
    double min_track_space{0.150};    // мм
    double min_drill_dia{0.300};      // мм
    double min_annular_ring{0.150};   // мм
    double mask_expansion{0.050};     // мм
    double min_mask_dam{0.100};       // мм
    double min_edge_milling{0.300};   // мм
    double min_edge_vcut{0.500};      // мм
    double min_hole_to_hole{0.500};   // мм
    double min_silk_width{0.150};     // мм
    double min_silk_clearance{0.150}; // мм
    double fiducial_edge_clear{5.000};// мм
    double max_aspect_ratio{8.0};
};

/* Набір еталонних профілів фабрик */
inline constexpr FactoryProfile PRESET_PROFILES[] = {
    {
        .factory_name = "JLCPCB",
        .tier_name = "Standard 1-2 Layer (1 oz)",
        .copper_oz = 1.0,
        .min_track_width = 0.150,
        .min_track_space = 0.150,
        .min_drill_dia = 0.300,
        .min_annular_ring = 0.150,
        .mask_expansion = 0.050,
        .min_mask_dam = 0.100,
        .min_edge_milling = 0.300,
        .min_edge_vcut = 0.500,
        .min_hole_to_hole = 0.500,
        .min_silk_width = 0.150,
        .min_silk_clearance = 0.150,
        .fiducial_edge_clear = 5.000,
        .max_aspect_ratio = 8.0
    },
    {
        .factory_name = "JLCPCB",
        .tier_name = "Advanced 4-6 Layer (0.5 oz)",
        .copper_oz = 0.5,
        .min_track_width = 0.090,
        .min_track_space = 0.090,
        .min_drill_dia = 0.150,
        .min_annular_ring = 0.100,
        .mask_expansion = 0.030,
        .min_mask_dam = 0.080,
        .min_edge_milling = 0.200,
        .min_edge_vcut = 0.400,
        .min_hole_to_hole = 0.400,
        .min_silk_width = 0.120,
        .min_silk_clearance = 0.120,
        .fiducial_edge_clear = 4.000,
        .max_aspect_ratio = 10.0
    },
    {
        .factory_name = "PCBWay",
        .tier_name = "Standard Production (1 oz)",
        .copper_oz = 1.0,
        .min_track_width = 0.150,
        .min_track_space = 0.150,
        .min_drill_dia = 0.300,
        .min_annular_ring = 0.150,
        .mask_expansion = 0.050,
        .min_mask_dam = 0.100,
        .min_edge_milling = 0.250,
        .min_edge_vcut = 0.500,
        .min_hole_to_hole = 0.500,
        .min_silk_width = 0.150,
        .min_silk_clearance = 0.150,
        .fiducial_edge_clear = 5.000,
        .max_aspect_ratio = 8.0
    },
    {
        .factory_name = "Eurocircuits",
        .tier_name = "Standard Pool (1 oz)",
        .copper_oz = 1.0,
        .min_track_width = 0.150,
        .min_track_space = 0.150,
        .min_drill_dia = 0.250,
        .min_annular_ring = 0.125,
        .mask_expansion = 0.040,
        .min_mask_dam = 0.100,
        .min_edge_milling = 0.250,
        .min_edge_vcut = 0.450,
        .min_hole_to_hole = 0.450,
        .min_silk_width = 0.150,
        .min_silk_clearance = 0.125,
        .fiducial_edge_clear = 5.000,
        .max_aspect_ratio = 8.5
    }
};

class KiCadRulesGenerator {
public:
    explicit constexpr KiCadRulesGenerator(const FactoryProfile& profile) noexcept
        : profile_(profile) {}

    [[nodiscard]] std::string generate_dru_content() const {
        std::string out;
        out.reserve(4096);

        out += ";; ===================================================================\n";
        out += std::format(";; KiCad 8/9 Custom DRC Rules\n");
        out += std::format(";; Factory Profile: {} - {}\n", profile_.factory_name, profile_.tier_name);
        out += std::format(";; Copper Weight: {:.1f} oz | Max Aspect Ratio: {:.1f}:1\n",
                           profile_.copper_oz, profile_.max_aspect_ratio);
        out += ";; Generated automatically by C++20 DFM Rules Importer\n";
        out += ";; ===================================================================\n\n";
        out += "(version 1)\n\n";

        // 1. Мінімальна ширина провідників
        out += "(rule \"Factory_Min_Track_Width\"\n";
        out += "  (priority 100)\n";
        out += std::format("  (constraint track_width (min {:.3f}mm))\n", profile_.min_track_width);
        out += "  (condition \"A.Type == 'Track'\"))\n\n";

        // 2. Мінімальний ізоляційний зазор
        out += "(rule \"Factory_Min_Clearance\"\n";
        out += "  (priority 100)\n";
        out += std::format("  (constraint clearance (min {:.3f}mm))\n", profile_.min_track_space);
        out += "  (condition \"A.NetClass != B.NetClass\"))\n\n";

        // 3. Мінімальний діаметр свердла
        out += "(rule \"Factory_Min_Drill\"\n";
        out += "  (priority 110)\n";
        out += std::format("  (constraint hole_size (min {:.3f}mm))\n", profile_.min_drill_dia);
        out += "  (condition \"A.Type == 'Via' || A.Type == 'Pad'\"))\n\n";

        // 4. Мінімальний поясок металізації
        out += "(rule \"Factory_Min_Annular_Ring\"\n";
        out += "  (priority 110)\n";
        out += std::format("  (constraint annular_width (min {:.3f}mm))\n", profile_.min_annular_ring);
        out += "  (condition \"A.Type == 'Via'\"))\n\n";

        // 5. Відступ міді до контуру плати при фрезеруванні
        out += "(rule \"Factory_Edge_Milling_Clearance\"\n";
        out += "  (priority 120)\n";
        out += std::format("  (constraint edge_clearance (min {:.3f}mm))\n", profile_.min_edge_milling);
        out += "  (condition \"A.Type == 'Track' || A.Type == 'Zone' || A.Type == 'Pad'\"))\n\n";

        // 6. Відступ полігонів живлення до осі V-cut
        out += "(rule \"Factory_VCut_Scoring_Clearance\"\n";
        out += "  (priority 130)\n";
        out += std::format("  (constraint edge_clearance (min {:.3f}mm))\n", profile_.min_edge_vcut);
        out += "  (condition \"A.Type == 'Zone' && A.NetClass == 'Power'\"))\n\n";

        // 7. Зазор між отворами (Hole-to-Hole)
        out += "(rule \"Factory_Hole_To_Hole\"\n";
        out += "  (priority 105)\n";
        out += std::format("  (constraint hole_clearance (min {:.3f}mm))\n", profile_.min_hole_to_hole);
        out += "  (condition \"A.Type == 'Via' || A.Type == 'Pad'\"))\n\n";

        // 8. Відступ шовкографії від паяльних майданчиків
        out += "(rule \"Factory_Silk_To_Mask_Clearance\"\n";
        out += "  (priority 90)\n";
        out += std::format("  (constraint silk_clearance (min {:.3f}mm))\n", profile_.min_silk_clearance);
        out += "  (condition \"A.Type == 'Graphic' && A.Layer == 'F.SilkS'\"))\n\n";

        // 9. Відступ оптичних реперів від краю плати
        out += "(rule \"Factory_Fiducial_Edge_Clearance\"\n";
        out += "  (priority 140)\n";
        out += std::format("  (constraint edge_clearance (min {:.3f}mm))\n", profile_.fiducial_edge_clear);
        out += "  (condition \"A.Type == 'Footprint' && A.Reference == 'FID*'\"))\n\n";

        return out;
    }

    bool write_to_file(std::string_view filepath) const {
        std::ofstream ofs(std::string(filepath));
        if (!ofs.is_open()) {
            return false;
        }
        ofs << generate_dru_content();
        return ofs.good();
    }

private:
    FactoryProfile profile_;
};

} // namespace dfm_importer

int main(int argc, char* argv[]) {
    using namespace dfm_importer;

    std::cout << "=== DFM Rules Importer CLI (C++20) ===\n\n";

    constexpr std::span<const FactoryProfile> presets(PRESET_PROFILES);

    if (argc < 2) {
        std::cout << std::format("Використання: {} <індекс_профілю> [вихідний_файл.kicad_dru]\n", argv[0]);
        std::cout << "Доступні профілі фабрик:\n";
        for (size_t i = 0; i < presets.size(); ++i) {
            const auto& p = presets[i];
            std::cout << std::format("  [{}] {} — {} (Мідь: {:.1f} oz, Min W/S: {:.2f}/{:.2f} мм)\n",
                                     i, p.factory_name, p.tier_name, p.copper_oz,
                                     p.min_track_width, p.min_track_space);
        }
        return 1;
    }

    const size_t idx = static_cast<size_t>(std::stoi(argv[1]));
    if (idx >= presets.size()) {
        std::cerr << std::format("Помилка: некоректний індекс профілю {} (доступно 0..{})\n",
                                 idx, presets.size() - 1);
        return 1;
    }

    const std::string_view outfile = (argc >= 3) ? argv[2] : "factory_rules.kicad_dru";
    const auto& profile = presets[idx];

    std::cout << std::format("Генерація правил для '{} ({})' у файл '{}'...\n",
                             profile.factory_name, profile.tier_name, outfile);

    const KiCadRulesGenerator generator(profile);
    if (generator.write_to_file(outfile)) {
        std::cout << "Файл правил успішно згенеровано!\n";
        return 0;
    } else {
        std::cerr << "Помилка запису файлу!\n";
        return 1;
    }
}
```
:::

---

## Інтеграція в автоматизований пайплайн перевірки (CI/CD)

Однією з ключових переваг автоматичної генерації файлів `.kicad_dru` є можливість інтеграції в автоматизовані конвеєри перевірки інженерних репозиторіїв.

Типовий крок конвеєра в середовищі Linux або Docker-контейнері складається з двох етапів:

1. **Генерація правил під цільову фабрику:**
```bash
./dfm_importer 0 ./ci_rules.kicad_dru
```
Команда вибирає пресет `[0]` (JLCPCB Standard) та зберігає його як файл конфігурації перевірки.

2. **Запуск аналізатора KiCad CLI без відкриття графічного вікна:**
```bash
kicad-cli pcb drc \
  --rules ./ci_rules.kicad_dru \
  --severity-all \
  --output-format json \
  --output drc_report.json \
  ./hardware_project.kicad_pcb
```

Якщо в топології присутнє хоча б одне порушення мінімального зазору або відступу до краю плати, утиліта `kicad-cli` повертає ненульовий код виходу, зупиняючи процес злиття гілок (Pull Request) і формуючи структурований звіт про помилки для інженера-розробника.

---

## Технологічні пастки та крайові випадки імпорту

Під час практичної інтеграції згенерованих правил DRC у реальний робочий процес проєктування інженер стикається з низкою критичних нюансів:

### 1. Несумісність одиниць вимірювання та внутрішнє квантування координат

САПР KiCad зберігає всі геометричні координати у внутрішньому цілочисельному форматі з роздільною здатністю **1 нанометр** (10⁻⁶ мм), тоді як виробничі специфікації фабрик формулюються або в тисячних долях дюйма (**mils**, де 1 mil = 25.4 мкм), або в сотих долях міліметра.

Під час конвертації виникають похибки округлення з плаваючою комою:
```
6.0 mil = 6 · 0.0254 = 0.1524 мм
```
Якщо фабрика заявляє «6 mil standard», а інженер записує в правилах `0.150 мм`, то доріжка, розведена точно на 0.150 мм, виявиться на 2.4 мкм меншою за номінальні 6 mil. На більшості фабрик CAM-система має похибку відсікання до 5 мкм, що може спричинити формальну зупинку автоматичного запуску панелі. Імпортер повинен явно використовувати точні метричні значення, задекларовані фабрикою у специфікації виробника.

### 2. Масштабування зазорів для важкої міді (Heavy Copper Scaling)

Якщо у проєкті силового перетворювача товщину міді змінюють з 1 oz (35 мкм) на 2 oz (70 мкм) або 3 oz (105 мкм), базові правила `6/6 mil` стають фізично неможливими через збільшення бокового підтравлювання (боковий зсув сягає 45–60 мкм).

Формула автоматичного масштабування мінімальної ширини та зазору при зміні товщини фольги:

```
W_min(Cu_oz) = W_min(1oz) + (Cu_oz - 1.0) · 0.050 мм
S_min(Cu_oz) = S_min(1oz) + (Cu_oz - 1.0) · 0.050 мм
```

Для 2 oz фольги мінімальні норми автоматично зростають з 0.15 мм до 0.20 мм (8 mil), а для 3 oz — до 0.25 мм (10 mil).

### 3. Локальні зони звуження (BGA Neck-down Areas)

Для сучасних процесорів у корпусах BGA з кроком кульок 0.5–0.8 мм фізично неможливо вивести сигнальні доріжки стандартною шириною 0.15 мм і зазором 0.15 мм (між контактними майданчиками діаметром 0.35 мм залишається просвіт лише 0.15–0.25 мм).

У правилах KiCad це вирішується за допомогою кіл локальних зон (Keepout / Rule Areas), де глобальне правило перевизначається локальним:

```lisp
(rule "BGA_Escape_Neckdown"
  (priority 200)
  (constraint track_width (min 0.090mm))
  (constraint clearance (min 0.090mm))
  (condition "A.insideArea('BGA_Zone') && A.Type == 'Track'"))
```

Утиліта імпорту враховує цей поділ, генеруючи правила так, щоб локальні звуження дозволялися лише в межах класу складності Advanced для відповідної кількості шарів плати.

### 4. Внутрішні шари проти зовнішніх у багатошарових платах

На зовнішніх шарах (Top/Bottom) під час гальванічної металізації отворів осаджується додатковий шар міді 20–25 мкм, тоді як внутрішні шари (Inner Layers) виготовляються прямим травленням базової фольги без гальванічного потовщення. Через це на внутрішніх шарах можна безпечно реалізувати менші зазори і пояски, проте вони більш чутливі до розриву пояска при термічному розширенні препрегу. Згенеровані правила розділяють вимоги до внутрішніх і зовнішніх шарів через умову `A.Layer == 'F.Cu' || A.Layer == 'B.Cu'`.

### 5. Зубчасті торцеві контакти (Castellated Holes)

Якщо плата проєктується як паяний SMD-модуль із напівкруглими металізованими контактами на торцях (Castellated Holes / Plated Half-holes), застосовуються спеціальні правила DFM:
- Мінімальний діаметр отвору свердління під напівпаз: `≥ 0.60 мм`.
- Мінімальний відступ від центру кастельованого отвору до сусідніх SMD-компонентів: `≥ 1.0 мм`.
- Контур фрезерування повинен проходити точно по центральній осі отворів. Утиліта автоматично формує правило `castellated_clearance`, що запобігає розміщенню критичних компонентів у зоні розпилу торцевих отворів.

### 6. Лазерні мікроотвори та глухі перехідні отвори (Microvias & Blind/Buried Vias)

У проєктах високої щільності (HDI) використовуються глухі (Blind) та приховані (Buried) перехідні отвори, що з'єднують лише частину шарів плати. Для них діють специфічні геометричні обмеження:
- Лазерні мікроотвори (Microvias) формуються методом ультрафіолетової або CO2-лазерної абляції діелектрика. Їхнє граничне співвідношення товщини діелектрика до діаметра лазерного променя повинно задовольняти умову `Aspect_Ratio ≤ 1:1` (типово діаметр отвору 0.10–0.12 мм при товщині діелектрика препрегу 0.08–0.10 мм).
- У синтаксисі KiCad для мікроотворів генерується окреме правило `(rule "Microvia_Constraints" (constraint hole_size (min 0.100mm)) (constraint annular_width (min 0.075mm)) (condition "A.Type == 'Microvia'"))`, що запобігає застосуванню жорстких норм механічного свердління до лазерних переходів.
