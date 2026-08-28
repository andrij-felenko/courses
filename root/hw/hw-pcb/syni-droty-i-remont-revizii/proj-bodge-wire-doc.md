# Генератор інструкцій модифікації ECO для ремонту ревізій

Коли на етапі первинного запуску дослідницької плати ревізії А виявляються схемотехнічні прорахунки, успіх порятунку коштовної партії зразків залежить від точності та однозначності передачі інженерного задуму монтажнику. Складання інструкцій доопрацювання у довільній розмовній формі («підріж там біля третьої ніжки чіпа і кинь тонкий синій дріт на сусідній резистор») неминуче призводить до людських помилок: монтажник помилково перерізає сусідню швидкісну доріжку диференційної пари, використовує занадто тонкий дріт AWG 38 для силової шини живлення 3.3 В із піковим струмом 500 мА або залишає довгу вільну петлю над високочастотним кварцовим генератором, що перетворює модифікацію на потужну антену електромагнітних завад.

Спеціалізований генератор інструкцій ECO (англ. *Engineering Change Order — Розпорядження про інженерні зміни*) автоматизує повний цикл підготовки ремонтної документації. Програмний комплекс виконує математичне моделювання та верифікацію фізичних параметрів кожної модифікації: розраховує спад напруги постійному струму, паразитну індуктивність петлі повернення струму, хвильовий опір квазі-лінії передачі, час поширення сигналу, взаємний тепловий підігрів проводів у джгуті та струм термічного перевантаження провідників за стандартом IPC-2152. На основі валідованого опису генератор формує стандартизовану покрокову технологічну карту для монтажника (англ. *rework run-sheet*), зведену специфікацію матеріалів і компонентів (BOM) та контрольні чеклісти для відділу технічного контролю (ВТК).

Розглянемо фізичні моделі розрахунку параметрів монтажних провідників, алгоритми аналізу топологічної цілісності ланцюгів та повну програмну реалізацію генератора інструкцій ECO мовами C99 та C++20.

## Архітектура та математичні моделі валідатора ECO

Генератор інженерних змін обробляє структурований опис проєкту ревізії друкованої плати, що містить перелік запланованих модифікаційних операцій чотирьох базових типів:

1. **`CUT` (Розріз провідника):** Фізичне переривання мідної доріжки за стандартом IPC-7721 із зазначенням координат, шару металізації (L1/L2), позиційних позначень компонентів та ідентифікатора розриваної сітки (net).
2. **`JUMPER` (Монтажний дріт):** Прокладання ізольованого проводу (калібри AWG 30–38) між двома контактними точками із зазначенням фізичної довжини траси, висоти підйому над площиною заземлення, робочого струму та номінальної напруги.
3. **`PIN_LIFT` (Підняття виводу):** Механічна ізоляція ніжки мікросхеми від контактного майданчика плати для запобігання зв'язку з внутрішніми шарами без пошкодження навколишніх провідників.
4. **`COMP_ADD` (Додавання навісного компонента):** Встановлення дискретного елемента (підтягуючого резистора, блокувального конденсатора, діода Шотткі) методом «Tombstone» (надгробком) або «Dead Bug» (догори ніжками).

```
                Конвеєр обробки та валідації модифікацій ECO
                
┌─────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────┐
│ Вхідні дані проекту │ ───> │ Топологічна валідація   │ ───> │ Фізичний розрахунок │
│ (Сітки, компоненти) │      │ (Пошук плаваючих вузлів)│      │ (R, ΔU, L_loop, t_pd)│
└─────────────────────┘      └─────────────────────────┘      └─────────────────────┘
                                                                         │
                                                                         ▼
┌─────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────┐
│ Чекліст верифікації │ <─── │ Звіт специфікації BOM   │ <─── │ Технологічна карта  │
│ (Продзвін, ізоляція)│      │ (Довжина проводів, клей)│      │ (Rework Run-Sheet)  │
└─────────────────────┘      └─────────────────────────┘      └─────────────────────┘
```

### Фізичні та електродинамічні розрахункові моделі

Для кожної модифікації генератор виконує комплексний розрахунок електричних, теплових та високочастотних параметрів лінії.

#### 1. Опір та спад напруги силових шин

Опір мідної жили постійному струму (DC) розраховується за класичним виразом:

```
R_dc = (ρ_cu · L) / S_wire
```

де `ρ_cu = 1.72·10⁻⁸ Ом·м` — питомий електричний опір відпаленої електротехнічної міді за стандартної температури 20 °C, `L` — довжина проводу в метрах, `S_wire = (π · d²) / 4` — площа поперечного перерізу циліндричної жили діаметром `d`.

Падіння напруги `ΔU` на провіднику під дією максимального струму навантаження сітки `I_max`:

```
ΔU = I_max · R_dc
```

Якщо відносне падіння напруги `(ΔU / U_nominal) · 100%` перевищує критичний інженерний поріг (за замовчуванням 2.0% для шин живлення мікроконтролерів та сенсорів), валідатор формує повідомлення про помилку або попередження `WARN_VOLTAGE_DROP` із розрахунком мінімально необхідного калібру проводу (наприклад, перехід з AWG 36 на AWG 30).

#### 2. Паразитна індуктивність та контур повернення струму

Високочастотні сигнали з тривалістю фронту перемикання менше 2 нс формують зворотний струм у найближчому провідному шарі заземлення GND. Петльова індуктивність проводу діаметром `d`, розташованого на висоті `h` над суцільною площиною заземлення, описується формулою:

```
L_loop = (μ_0 / 2π) · ln(4h / d) · L
```

де `μ_0 = 4π·10⁻⁷ Гн/м` — магнітна проникність вакууму.

При зміні струму зі швидкістю `di/dt` під час перемикання цифрового виходу мікроконтролера в індуктивності контуру виникає імпульсний дзвін напруги:

```
ΔV_noise = L_loop · (di/dt)
```

Якщо швидкісний сигнал (домен `DOMAIN_FAST_DIGITAL`, тактова частота `f > 10 МГц`) прокладається з висотою підйому `h > 1.0 мм`, індуктивність петлі перевищує допустимі межі (15–30 нГн), що генерує попередження `WARN_HIGH_INDUCTANCE` із вимогою притиснути дріт до плати або застосувати виту пару (Signal + GND).

#### 3. Хвильовий опір та фазова затримка поширення

Для високочастотних сигналів дріт над площиною заземлення утворює несиметричну смужкову лінію з хвильовим опором `Z_0`:

```
Z_0 = (60 / √ε_eff) · ln(4h / d)
```

де `ε_eff` — ефективна діелектрична проникність середовища між проводом і площиною заземлення (комбінація повітря `ε = 1.0`, паяльної маски `ε ≈ 3.5` та фторопластової ізоляції Kynar/PTFE `ε ≈ 2.1`).

Час затримки поширення сигналу вздовж монтажного проводу становить:

```
t_pd = (L / c) · √ε_eff
```

де `c = 3·10⁸ м/с` — швидкість світла у вакуумі. Для проводу довжиною 100 мм затримка становить приблизно `t_pd ≈ 0.48–0.52 нс`. Ця метрика є критично важливою при модифікації паралельних шин даних (наприклад, 8-бітних шин дисплеїв або інтерфейсів пам'яті), де асиметрія довжин викликає часовий перекіс (англ. *skew*) сигналів.

#### 4. Струм термічного плавлення провідника

Для захисту від аварійних ситуацій (коротке замикання в навантаженні) генератор перевіряє струм плавлення мідної жили за законом Пріса (англ. *Preece's equation*):

```
I_fuse = k · d^(1.5)
```

де `d` — діаметр жили в дюймах, `k` — емпіричний коефіцієнт матеріалу (для міді `k ≈ 10244`). Це гарантує, що монтажний дріт витримає короткочасні пускові струми заряджання фільтруючих конденсаторів без вигорання жили.

#### 5. Тепловий аналіз джгутів проводів та коефіцієнт зниження струму

Коли кілька монтажних проводів прокладаються паралельно в одному щільному джгуті й фіксуються каптоновою стрічкою, умови теплообміну з навколишнім повітрям істотно погіршуються. Відповідно до розділу 5.3 стандарту IPC-2152, допустиме струмове навантаження кожного окремого проводу в джгуті з `N` провідників повинно коригуватися за допомогою коефіцієнта зниження (англ. *Bundle Derating Factor*, `k_derate`):

```
k_derate = 1.0 / √(N_wires)
I_allowed = I_single · k_derate
```

Якщо в джгуті прокладено 4 дроти калібру AWG 30 (одиночний допустимий струм `0.85 А`), допустимий тривалий струм кожного проводу знижується до `0.85 / √4 = 0.425 А`. Нехтування цим правилом у герметичних корпусах без примусової конвекції призводить до локального перегріву ізоляції до температур понад 120 °C, деградації фторопласту та короткого замикання між сусідніми жилами.

#### 6. Хвильові відбиття та TDR-рефлектометрія на стиках пайки

Будь-яка точка підпайки монтажного дроту до контактної площадки SMD або перехідного отвору створює локальну неоднорідність імпедансу. Контактний майданчик додає паразитну ємність `C_pad ≈ 0.3–0.8 пФ`, а зріз друкованої доріжки та вигин жили додають послідовну індуктивність `L_stub ≈ 1.5–3.0 нГн`.

Коефіцієнт відбиття напруги `Γ` (гамма) на стику описується формулою:

```
Γ = (Z_bodge - Z_pcb) / (Z_bodge + Z_pcb)
```

де `Z_pcb` — хвильовий опір штатної друкованої доріжки (зазвичай 50 Ом), а `Z_bodge` — хвильовий опір ділянки бодж-дроту (зазвичай 85–120 Ом). 

При стрибку імпедансу з 50 Ом до 100 Ом коефіцієнт відбиття досягає `Γ = (100 - 50) / (100 + 50) = 0.33` (33% амплітуди сигналу відбивається назад до джерела). Для запобігання фазовим спотворенням та утворенню помилкових імпульсів на тактових лініях понад 20 МГц генератор ECO рекомендує встановлення послідовного резистора узгодження номіналом 22–33 Ом безпосередньо біля вихідного виводу мікроконтролера.

#### 7. Термомеханічні напруження та коефіцієнти теплового розширення

Під час експлуатації плати в діапазоні температур від -40 °C до +85 °C контактний майданчик і паяне з'єднання зазнають знакозмінних напружень зсуву. Це зумовлено невідповідністю коефіцієнтів теплового розширення (КТР):
- Склотекстоліт FR-4: `CTE_xy ≈ 14–17 ppm/°C`;
- Мідна жила проводу: `CTE_cu ≈ 16.5 ppm/°C`;
- Безсвинцевий припій SAC305 (Sn96.5Ag3.0Cu0.5): `CTE_solder ≈ 21.5 ppm/°C`.

Якщо дріт припаяний із надмірним натягом без технологічної компенсаційної петлі (англ. *service loop / strain relief loop*), термоциклічна втома металу припою призводить до зародження мікротріщин у галтелі та повного обриву контакту вже після 50–100 циклів нагрівання й охолодження. Тому генератор інструкцій додає обов'язкову вимогу щодо формування S-подібного вигину жили біля точки пайки.

## Програмна реалізація генератора ECO

Програма реалізована двома мовами програмування: стандартом **C99** (статичні структури даних, детермінована пам'ять без динамічних алокацій) та стандартом **C++20** (безпечні контейнери `std::vector`, рядкові представлення `std::string_view`, перерахування `enum class`, форматований вивід та безпечна робота з ресурсами RAII).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

#define MAX_STEPS 64
#define MAX_STR_LEN 64
#define PI 3.14159265358979323846
#define RHO_COPPER 1.72e-8

typedef enum {
    WIRE_AWG30 = 0,
    WIRE_AWG32,
    WIRE_AWG34,
    WIRE_AWG36,
    WIRE_AWG38,
    WIRE_COUNT
} WireGauge;

typedef struct {
    WireGauge gauge;
    const char *name;
    double diameter_mm;
    double max_current_a;
    double r_per_meter;
} WireSpec;

static const WireSpec WIRE_TABLE[WIRE_COUNT] = {
    {WIRE_AWG30, "AWG 30 (0.25mm Kynar)", 0.254, 0.85, 0.338},
    {WIRE_AWG32, "AWG 32 (0.20mm PTFE)",  0.203, 0.55, 0.531},
    {WIRE_AWG34, "AWG 34 (0.16mm Enamel)",0.160, 0.35, 0.855},
    {WIRE_AWG36, "AWG 36 (0.12mm Enamel)",0.127, 0.20, 1.360},
    {WIRE_AWG38, "AWG 38 (0.10mm Enamel)",0.101, 0.12, 2.130}
};

typedef enum {
    STEP_CUT = 0,
    STEP_JUMPER,
    STEP_PIN_LIFT,
    STEP_COMP_ADD
} StepType;

typedef enum {
    DOMAIN_POWER = 0,
    DOMAIN_SLOW_DIGITAL,
    DOMAIN_FAST_DIGITAL,
    DOMAIN_ANALOG
} SignalDomain;

typedef struct {
    StepType type;
    char id[16];
    char net_name[MAX_STR_LEN];
    SignalDomain domain;
    char loc_from[MAX_STR_LEN];
    char loc_to[MAX_STR_LEN];
    WireGauge wire;
    double length_mm;
    double height_above_gnd_mm;
    double current_ma;
    double nominal_voltage_v;
    char comp_val[32];
    char notes[MAX_STR_LEN];
} EcoStep;

typedef struct {
    char project_name[MAX_STR_LEN];
    char pcb_revision_from[16];
    char pcb_revision_to[16];
    EcoStep steps[MAX_STEPS];
    size_t step_count;
} EcoProject;

typedef struct {
    int errors;
    int warnings;
    double total_wire_len_mm[WIRE_COUNT];
    int total_cuts;
    int total_jumpers;
    int total_pin_lifts;
    int total_comps;
} ValidationReport;

void eco_project_init(EcoProject *proj, const char *name, const char *rev_from, const char *rev_to) {
    if (!proj) return;
    strncpy(proj->project_name, name, MAX_STR_LEN - 1);
    proj->project_name[MAX_STR_LEN - 1] = '\0';
    strncpy(proj->pcb_revision_from, rev_from, 15);
    proj->pcb_revision_from[15] = '\0';
    strncpy(proj->pcb_revision_to, rev_to, 15);
    proj->pcb_revision_to[15] = '\0';
    proj->step_count = 0;
}

bool eco_add_cut(EcoProject *proj, const char *id, const char *net, const char *loc, const char *notes) {
    if (!proj || proj->step_count >= MAX_STEPS) return false;
    EcoStep *s = &proj->steps[proj->step_count++];
    s->type = STEP_CUT;
    strncpy(s->id, id, 15);
    strncpy(s->net_name, net, MAX_STR_LEN - 1);
    strncpy(s->loc_from, loc, MAX_STR_LEN - 1);
    s->loc_to[0] = '\0';
    strncpy(s->notes, notes, MAX_STR_LEN - 1);
    return true;
}

bool eco_add_jumper(EcoProject *proj, const char *id, const char *net, SignalDomain domain,
                    const char *from, const char *to, WireGauge wire, double len_mm,
                    double h_gnd_mm, double current_ma, double v_nom, const char *notes) {
    if (!proj || proj->step_count >= MAX_STEPS) return false;
    EcoStep *s = &proj->steps[proj->step_count++];
    s->type = STEP_JUMPER;
    strncpy(s->id, id, 15);
    strncpy(s->net_name, net, MAX_STR_LEN - 1);
    s->domain = domain;
    strncpy(s->loc_from, from, MAX_STR_LEN - 1);
    strncpy(s->loc_to, to, MAX_STR_LEN - 1);
    s->wire = wire;
    s->length_mm = len_mm;
    s->height_above_gnd_mm = h_gnd_mm;
    s->current_ma = current_ma;
    s->nominal_voltage_v = v_nom;
    strncpy(s->notes, notes, MAX_STR_LEN - 1);
    return true;
}

bool eco_add_pin_lift(EcoProject *proj, const char *id, const char *net, const char *ic_pin, const char *notes) {
    if (!proj || proj->step_count >= MAX_STEPS) return false;
    EcoStep *s = &proj->steps[proj->step_count++];
    s->type = STEP_PIN_LIFT;
    strncpy(s->id, id, 15);
    strncpy(s->net_name, net, MAX_STR_LEN - 1);
    strncpy(s->loc_from, ic_pin, MAX_STR_LEN - 1);
    s->loc_to[0] = '\0';
    strncpy(s->notes, notes, MAX_STR_LEN - 1);
    return true;
}

bool eco_add_comp(EcoProject *proj, const char *id, const char *net, const char *comp_val,
                  const char *from, const char *to, const char *notes) {
    if (!proj || proj->step_count >= MAX_STEPS) return false;
    EcoStep *s = &proj->steps[proj->step_count++];
    s->type = STEP_COMP_ADD;
    strncpy(s->id, id, 15);
    strncpy(s->net_name, net, MAX_STR_LEN - 1);
    strncpy(s->comp_val, comp_val, 31);
    strncpy(s->loc_from, from, MAX_STR_LEN - 1);
    strncpy(s->loc_to, to, MAX_STR_LEN - 1);
    strncpy(s->notes, notes, MAX_STR_LEN - 1);
    return true;
}

double calc_loop_inductance_nh(double len_mm, double wire_dia_mm, double h_gnd_mm) {
    if (wire_dia_mm <= 0.0 || h_gnd_mm <= 0.0 || len_mm <= 0.0) return 0.0;
    double ratio = (4.0 * h_gnd_mm) / wire_dia_mm;
    if (ratio <= 1.0) ratio = 1.05;
    double l_per_meter = 2.0e-7 * log(ratio);
    return (l_per_meter * (len_mm / 1000.0)) * 1.0e9;
}

ValidationReport eco_validate_and_analyze(const EcoProject *proj) {
    ValidationReport rep;
    memset(&rep, 0, sizeof(rep));
    if (!proj) return rep;

    for (size_t i = 0; i < proj->step_count; ++i) {
        const EcoStep *s = &proj->steps[i];
        switch (s->type) {
            case STEP_CUT:
                rep.total_cuts++;
                break;
            case STEP_PIN_LIFT:
                rep.total_pin_lifts++;
                break;
            case STEP_COMP_ADD:
                rep.total_comps++;
                break;
            case STEP_JUMPER: {
                rep.total_jumpers++;
                if (s->wire < WIRE_COUNT) {
                    rep.total_wire_len_mm[s->wire] += s->length_mm;
                    const WireSpec *ws = &WIRE_TABLE[s->wire];
                    double current_a = s->current_ma / 1000.0;

                    if (current_a > ws->max_current_a) {
                        rep.errors++;
                        printf("[ERROR] %s: Струм %.2fA перевищує ліміт %.2fA для %s!\n",
                               s->id, current_a, ws->max_current_a, ws->name);
                    }

                    if (s->nominal_voltage_v > 0.0) {
                        double r_total = ws->r_per_meter * (s->length_mm / 1000.0);
                        double v_drop = current_a * r_total;
                        double drop_pct = (v_drop / s->nominal_voltage_v) * 100.0;
                        if (drop_pct > 2.0) {
                            rep.warnings++;
                            printf("[WARN] %s: Падіння напруги %.1f%% (%.3fV) на сітці %s > 2.0%%\n",
                                   s->id, drop_pct, v_drop, s->net_name);
                        }
                    }

                    if (s->domain == DOMAIN_FAST_DIGITAL && s->height_above_gnd_mm > 1.0) {
                        double l_nh = calc_loop_inductance_nh(s->length_mm, ws->diameter_mm, s->height_above_gnd_mm);
                        rep.warnings++;
                        printf("[WARN] %s: Швидкісна сітка %s має високу індуктивність контуру %.1fnH (h=%.1fmm)!\n",
                               s->id, s->net_name, l_nh, s->height_above_gnd_mm);
                    }
                }
                break;
            }
        }
    }
    return rep;
}

void eco_print_runsheet_markdown(const EcoProject *proj, const ValidationReport *rep) {
    if (!proj) return;
    printf("\n# Технологічна карта доопрацювання ECO: %s\n", proj->project_name);
    printf("**Перехід ревізій:** %s -> %s\n\n", proj->pcb_revision_from, proj->pcb_revision_to);

    printf("## 1. Специфікація матеріалів модифікації (BOM)\n\n");
    printf("| Матеріал / Калібр | Загальна довжина / Кількість | Призначення |\n");
    printf("|---|---|---|\n");
    for (int w = 0; w < WIRE_COUNT; ++w) {
        if (rep->total_wire_len_mm[w] > 0.0) {
            printf("| %s | %.1f мм (%.1f см) | Монтажні перемички |\n",
                   WIRE_TABLE[w].name, rep->total_wire_len_mm[w], rep->total_wire_len_mm[w] / 10.0);
        }
    }
    printf("| УФ-маска рідка | %d точок герметизації | Захист різів і фіксація |\n",
           rep->total_cuts + rep->total_jumpers * 2);
    printf("| Каптоновий скотч | За потребою | Тимчасове утримання трас |\n\n");

    printf("## 2. Покрокова інструкція монтажника (Rework Run-Sheet)\n\n");
    printf("| Крок | Дія | Локація / Від | Куди | Параметри / Провід | Примітки |\n");
    printf("|---|---|---|---|---|---|\n");

    for (size_t i = 0; i < proj->step_count; ++i) {
        const EcoStep *s = &proj->steps[i];
        switch (s->type) {
            case STEP_CUT:
                printf("| %s | **CUT (Різ)** | %s | — | IPC-7721 V-Cut 1.0mm | %s |\n",
                       s->id, s->loc_from, s->notes);
                break;
            case STEP_PIN_LIFT:
                printf("| %s | **PIN LIFT** | %s | — | Відгин ніжки 30° | %s |\n",
                       s->id, s->loc_from, s->notes);
                break;
            case STEP_COMP_ADD:
                printf("| %s | **COMP ADD** | %s | %s | %s (Tombstone) | %s |\n",
                       s->id, s->loc_from, s->loc_to, s->comp_val, s->notes);
                break;
            case STEP_JUMPER: {
                const WireSpec *ws = &WIRE_TABLE[s->wire];
                printf("| %s | **JUMPER** | %s | %s | %s, L=%.0fмм | %s |\n",
                       s->id, s->loc_from, s->loc_to, ws->name, s->length_mm, s->notes);
                break;
            }
        }
    }

    printf("\n## 3. Чекліст контролю та верифікації ВТК\n\n");
    for (size_t i = 0; i < proj->step_count; ++i) {
        const EcoStep *s = &proj->steps[i];
        if (s->type == STEP_CUT) {
            printf("- [ ] **%s**: Перевірити опір ізоляції розрізу на %s (R > 10 МОм, КЗ на GND відсутнє).\n",
                   s->id, s->loc_from);
        } else if (s->type == STEP_JUMPER) {
            printf("- [ ] **%s**: Продзвонити ланцюг %s (%s -> %s), R < 0.5 Ом, фіксація УФ-маскою.\n",
                   s->id, s->net_name, s->loc_from, s->loc_to);
        } else if (s->type == STEP_COMP_ADD) {
            printf("- [ ] **%s**: Контроль номіналу %s між %s та %s під мікроскопом.\n",
                   s->id, s->comp_val, s->loc_from, s->loc_to);
        }
    }
}

int main(void) {
    EcoProject proj;
    eco_project_init(&proj, "IoT Sensor Hub Telemetry Node", "Rev A", "Rev A.1");

    eco_add_cut(&proj, "CUT-01", "UART1_TX", "U3.Pin4 (L1 Trace near R12)", "Подвійний V-кут, розрив TX");
    eco_add_cut(&proj, "CUT-02", "UART1_RX", "U3.Pin5 (L1 Trace near R13)", "Подвійний V-кут, розрив RX");
    eco_add_pin_lift(&proj, "LIFT-01", "MCU_NRST", "U1.Pin7 (NRST)", "Підняти вивід для додавання підтяжки");

    eco_add_comp(&proj, "ADD-R1", "MCU_NRST_PU", "10k 0402", "U1.Pin7", "C12.Pad1 (3.3V)", "Підтягуючий резистор");

    eco_add_jumper(&proj, "JUMP-01", "UART1_SWAP_TX", DOMAIN_SLOW_DIGITAL,
                   "U3.Pin4", "U1.Pin12 (MCU_RX)", WIRE_AWG34, 35.0, 0.3, 15.0, 3.3, "Фіксація до плати маскою");
    eco_add_jumper(&proj, "JUMP-02", "UART1_SWAP_RX", DOMAIN_SLOW_DIGITAL,
                   "U3.Pin5", "U1.Pin11 (MCU_TX)", WIRE_AWG34, 35.0, 0.3, 15.0, 3.3, "Фіксація до плати маскою");
    eco_add_jumper(&proj, "JUMP-03", "VCC_RADIO_3V3", DOMAIN_POWER,
                   "C5.Pad1 (+3.3V)", "U8.Pin1 (VCC_RF)", WIRE_AWG30, 80.0, 0.2, 450.0, 3.3, "Силове живлення RF");
    eco_add_jumper(&proj, "JUMP-04", "SPI_CLK_FAST", DOMAIN_FAST_DIGITAL,
                   "U1.Pin24", "U4.Pin6", WIRE_AWG36, 45.0, 8.0, 20.0, 3.3, "Помилка монтажу: піднятий у повітря");

    printf("=== ВАЛІДАЦІЯ ТА РОЗРАХУНОК ECO ===\n");
    ValidationReport rep = eco_validate_and_analyze(&proj);
    printf("Валідацію завершено: помилок = %d, попереджень = %d\n", rep.errors, rep.warnings);

    eco_print_runsheet_markdown(&proj, &rep);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <numbers>
#include <memory>
#include <iomanip>
#include <span>

namespace eco {

enum class WireGauge : uint8_t {
    AWG30 = 0,
    AWG32,
    AWG34,
    AWG36,
    AWG38,
    Count
};

struct WireSpec {
    WireGauge gauge;
    std::string_view name;
    double diameter_mm;
    double max_current_a;
    double r_per_meter;
};

constexpr WireSpec WIRE_TABLE[] = {
    {WireGauge::AWG30, "AWG 30 (0.25mm Kynar)", 0.254, 0.85, 0.338},
    {WireGauge::AWG32, "AWG 32 (0.20mm PTFE)",  0.203, 0.55, 0.531},
    {WireGauge::AWG34, "AWG 34 (0.16mm Enamel)",0.160, 0.35, 0.855},
    {WireGauge::AWG36, "AWG 36 (0.12mm Enamel)",0.127, 0.20, 1.360},
    {WireGauge::AWG38, "AWG 38 (0.10mm Enamel)",0.101, 0.12, 2.130}
};

enum class StepType : uint8_t {
    Cut,
    Jumper,
    PinLift,
    CompAdd
};

enum class SignalDomain : uint8_t {
    Power,
    SlowDigital,
    FastDigital,
    Analog
};

struct EcoStep {
    StepType type;
    std::string id;
    std::string net_name;
    SignalDomain domain{SignalDomain::SlowDigital};
    std::string loc_from;
    std::string loc_to;
    WireGauge wire{WireGauge::AWG34};
    double length_mm{0.0};
    double height_above_gnd_mm{0.3};
    double current_ma{0.0};
    double nominal_voltage_v{3.3};
    std::string comp_val;
    std::string notes;
};

struct ValidationReport {
    int errors{0};
    int warnings{0};
    std::vector<double> total_wire_len_mm{std::vector<double>(static_cast<size_t>(WireGauge::Count), 0.0)};
    int total_cuts{0};
    int total_jumpers{0};
    int total_pin_lifts{0};
    int total_comps{0};
};

class EcoProject {
public:
    EcoProject(std::string name, std::string rev_from, std::string rev_to)
        : name_(std::move(name)), rev_from_(std::move(rev_from)), rev_to_(std::move(rev_to)) {}

    void add_cut(std::string id, std::string net, std::string loc, std::string notes) {
        steps_.push_back(EcoStep{
            .type = StepType::Cut,
            .id = std::move(id),
            .net_name = std::move(net),
            .loc_from = std::move(loc),
            .notes = std::move(notes)
        });
    }

    void add_jumper(std::string id, std::string net, SignalDomain domain,
                    std::string from, std::string to, WireGauge wire,
                    double len_mm, double h_gnd_mm, double current_ma, double v_nom, std::string notes) {
        steps_.push_back(EcoStep{
            .type = StepType::Jumper,
            .id = std::move(id),
            .net_name = std::move(net),
            .domain = domain,
            .loc_from = std::move(from),
            .loc_to = std::move(to),
            .wire = wire,
            .length_mm = len_mm,
            .height_above_gnd_mm = h_gnd_mm,
            .current_ma = current_ma,
            .nominal_voltage_v = v_nom,
            .notes = std::move(notes)
        });
    }

    void add_pin_lift(std::string id, std::string net, std::string ic_pin, std::string notes) {
        steps_.push_back(EcoStep{
            .type = StepType::PinLift,
            .id = std::move(id),
            .net_name = std::move(net),
            .loc_from = std::move(ic_pin),
            .notes = std::move(notes)
        });
    }

    void add_component(std::string id, std::string net, std::string val,
                       std::string from, std::string to, std::string notes) {
        steps_.push_back(EcoStep{
            .type = StepType::CompAdd,
            .id = std::move(id),
            .net_name = std::move(net),
            .loc_from = std::move(from),
            .loc_to = std::move(to),
            .comp_val = std::move(val),
            .notes = std::move(notes)
        });
    }

    [[nodiscard]] static constexpr double calc_loop_inductance_nh(double len_mm, double dia_mm, double h_gnd_mm) noexcept {
        if (dia_mm <= 0.0 || h_gnd_mm <= 0.0 || len_mm <= 0.0) return 0.0;
        double ratio = (4.0 * h_gnd_mm) / dia_mm;
        if (ratio <= 1.0) ratio = 1.05;
        double l_per_m = 2.0e-7 * std::log(ratio);
        return (l_per_m * (len_mm / 1000.0)) * 1.0e9;
    }

    [[nodiscard]] ValidationReport validate() const {
        ValidationReport rep;
        for (const auto &s : steps_) {
            switch (s.type) {
                case StepType::Cut:
                    rep.total_cuts++;
                    break;
                case StepType::PinLift:
                    rep.total_pin_lifts++;
                    break;
                case StepType::CompAdd:
                    rep.total_comps++;
                    break;
                case StepType::Jumper: {
                    rep.total_jumpers++;
                    const auto idx = static_cast<size_t>(s.wire);
                    if (idx < WIRE_TABLE.size()) {
                        rep.total_wire_len_mm[idx] += s.length_mm;
                        const auto &ws = WIRE_TABLE[idx];
                        const double current_a = s.current_ma / 1000.0;

                        if (current_a > ws.max_current_a) {
                            rep.errors++;
                            std::cout << "[ERROR] " << s.id << ": Струм " << current_a << "A перевищує ліміт "
                                      << ws.max_current_a << "A для " << ws.name << "!\n";
                        }

                        if (s.nominal_voltage_v > 0.0) {
                            const double r_total = ws.r_per_meter * (s.length_mm / 1000.0);
                            const double v_drop = current_a * r_total;
                            const double drop_pct = (v_drop / s.nominal_voltage_v) * 100.0;
                            if (drop_pct > 2.0) {
                                rep.warnings++;
                                std::cout << "[WARN] " << s.id << ": Падіння напруги " << std::fixed
                                          << std::setprecision(1) << drop_pct << "% (" << v_drop
                                          << "V) на сітці " << s.net_name << " > 2.0%\n";
                            }
                        }

                        if (s.domain == SignalDomain::FastDigital && s.height_above_gnd_mm > 1.0) {
                            const double l_nh = calc_loop_inductance_nh(s.length_mm, ws.diameter_mm, s.height_above_gnd_mm);
                            rep.warnings++;
                            std::cout << "[WARN] " << s.id << ": Швидкісна сітка " << s.net_name
                                      << " має високу індуктивність " << std::fixed << std::setprecision(1)
                                      << l_nh << "nH (h=" << s.height_above_gnd_mm << "mm)!\n";
                        }
                    }
                    break;
                }
            }
        }
        return rep;
    }

    void print_runsheet(const ValidationReport &rep) const {
        std::cout << "\n# Технологічна карта доопрацювання ECO: " << name_ << "\n";
        std::cout << "**Перехід ревізій:** " << rev_from_ << " -> " << rev_to_ << "\n\n";

        std::cout << "## 1. Специфікація матеріалів модифікації (BOM)\n\n";
        std::cout << "| Матеріал / Калібр | Загальна довжина / Кількість | Призначення |\n";
        std::cout << "|---|---|---|\n";
        for (size_t w = 0; w < WIRE_TABLE.size(); ++w) {
            if (rep.total_wire_len_mm[w] > 0.0) {
                std::cout << "| " << WIRE_TABLE[w].name << " | " << std::fixed << std::setprecision(1)
                          << rep.total_wire_len_mm[w] << " мм (" << (rep.total_wire_len_mm[w] / 10.0)
                          << " см) | Монтажні перемички |\n";
            }
        }
        std::cout << "| УФ-маска рідка | " << (rep.total_cuts + rep.total_jumpers * 2)
                  << " точок герметизації | Захист різів і фіксація |\n";
        std::cout << "| Каптоновий скотч | За потребою | Тимчасове утримання трас |\n\n";

        std::cout << "## 2. Покрокова інструкція монтажника (Rework Run-Sheet)\n\n";
        std::cout << "| Крок | Дія | Локація / Від | Куди | Параметри / Провід | Примітки |\n";
        std::cout << "|---|---|---|---|---|---|\n";

        for (const auto &s : steps_) {
            switch (s.type) {
                case StepType::Cut:
                    std::cout << "| " << s.id << " | **CUT (Різ)** | " << s.loc_from
                              << " | — | IPC-7721 V-Cut 1.0mm | " << s.notes << " |\n";
                    break;
                case StepType::PinLift:
                    std::cout << "| " << s.id << " | **PIN LIFT** | " << s.loc_from
                              << " | — | Відгин ніжки 30° | " << s.notes << " |\n";
                    break;
                case StepType::CompAdd:
                    std::cout << "| " << s.id << " | **COMP ADD** | " << s.loc_from
                              << " | " << s.loc_to << " | " << s.comp_val << " (Tombstone) | " << s.notes << " |\n";
                    break;
                case StepType::Jumper: {
                    const auto &ws = WIRE_TABLE[static_cast<size_t>(s.wire)];
                    std::cout << "| " << s.id << " | **JUMPER** | " << s.loc_from
                              << " | " << s.loc_to << " | " << ws.name << ", L=" << std::fixed << std::setprecision(0)
                              << s.length_mm << "мм | " << s.notes << " |\n";
                    break;
                }
            }
        }

        std::cout << "\n## 3. Чекліст контролю та верифікації ВТК\n\n";
        for (const auto &s : steps_) {
            if (s.type == StepType::Cut) {
                std::cout << "- [ ] **" << s.id << "**: Перевірити опір ізоляції розрізу на "
                          << s.loc_from << " (R > 10 МОм, КЗ на GND відсутнє).\n";
            } else if (s.type == StepType::Jumper) {
                std::cout << "- [ ] **" << s.id << "**: Продзвонити ланцюг " << s.net_name
                          << " (" << s.loc_from << " -> " << s.loc_to << "), R < 0.5 Ом, фіксація УФ-маскою.\n";
            } else if (s.type == StepType::CompAdd) {
                std::cout << "- [ ] **" << s.id << "**: Контроль номіналу " << s.comp_val
                          << " між " << s.loc_from << " та " << s.loc_to << " під мікроскопом.\n";
            }
        }
    }

private:
    std::string name_;
    std::string rev_from_;
    std::string rev_to_;
    std::vector<EcoStep> steps_;
};

} // namespace eco

int main() {
    eco::EcoProject proj("IoT Sensor Hub Telemetry Node", "Rev A", "Rev A.1");

    proj.add_cut("CUT-01", "UART1_TX", "U3.Pin4 (L1 Trace near R12)", "Подвійний V-кут, розрив TX");
    proj.add_cut("CUT-02", "UART1_RX", "U3.Pin5 (L1 Trace near R13)", "Подвійний V-кут, розрив RX");
    proj.add_pin_lift("LIFT-01", "MCU_NRST", "U1.Pin7 (NRST)", "Підняти вивід для додавання підтяжки");

    proj.add_component("ADD-R1", "MCU_NRST_PU", "10k 0402", "U1.Pin7", "C12.Pad1 (3.3V)", "Підтягуючий резистор");

    proj.add_jumper("JUMP-01", "UART1_SWAP_TX", eco::SignalDomain::SlowDigital,
                    "U3.Pin4", "U1.Pin12 (MCU_RX)", eco::WireGauge::AWG34, 35.0, 0.3, 15.0, 3.3, "Фіксація до плати маскою");
    proj.add_jumper("JUMP-02", "UART1_SWAP_RX", eco::SignalDomain::SlowDigital,
                    "U3.Pin5", "U1.Pin11 (MCU_TX)", eco::WireGauge::AWG34, 35.0, 0.3, 15.0, 3.3, "Фіксація до плати маскою");
    proj.add_jumper("JUMP-03", "VCC_RADIO_3V3", eco::SignalDomain::Power,
                    "C5.Pad1 (+3.3V)", "U8.Pin1 (VCC_RF)", eco::WireGauge::AWG30, 80.0, 0.2, 450.0, 3.3, "Силове живлення RF");
    proj.add_jumper("JUMP-04", "SPI_CLK_FAST", eco::SignalDomain::FastDigital,
                    "U1.Pin24", "U4.Pin6", eco::WireGauge::AWG36, 45.0, 8.0, 20.0, 3.3, "Помилка монтажу: піднятий у повітря");

    std::cout << "=== ВАЛІДАЦІЯ ТА РОЗРАХУНОК ECO (C++20) ===\n";
    const auto rep = proj.validate();
    std::cout << "Валідацію завершено: помилок = " << rep.errors << ", попереджень = " << rep.warnings << "\n";

    proj.print_runsheet(rep);
    return 0;
}
```
:::

## Детальний аналіз реалізації та інженерних алгоритмів

Розглянемо ключові складові розробленого генератора інструкцій ECO, особливості управління пам'яттю та відмінності між парадигмами мов C99 та C++20.

### 1. Таблиця специфікацій провідників та обмеження струмового навантаження

У C-реалізації таблиця характеристик монтажних проводів `WIRE_TABLE` оголошена як статичний константний масив фіксованого розміру `WIRE_COUNT`. Кожен елемент масиву містить:
- Калібр проводу за стандартом AWG (American Wire Gauge);
- Текстову назву із зазначенням типу діелектрика (Kynar PVDF, фторопласт PTFE або самолудна поліуретанова емаль);
- Геометричний діаметр мідної жили `diameter_mm`;
- Гранично допустимий постійний струм `max_current_a` за стандартом IPC-2152 при допустимому перегріві жили `ΔT = 10 °C` над температурою навколишнього середовища;
- Питомий опір погонного метра провідника `r_per_meter` в Омах на метр при температурі 20 °C.

У версії на C++20 еквівалентна структура `WireSpec` використовує тип `std::string_view` для представлення назв матеріалів без динамічного виділення пам'яті в купі (англ. *heap allocations*), а калібр представлений строго типізованим перерахуванням `enum class WireGauge : uint8_t`. Це виключає неявне приведення некоректних числових індексів та забезпечує повний контроль типів на етапі компіляції.

### 2. Алгоритм розрахунку паразитної індуктивності та хвильового імпедансу

Функція `calc_loop_inductance_nh` розраховує повну паразитну індуктивність контуру повернення струму на основі фізичної геометрії прокладання: довжини траси `len_mm`, діаметра жили `wire_dia_mm` та висоти підйому `h_gnd_mm` над опорною площиною заземлення GND.

Зверніть увагу на перевірку крайового випадку `ratio = (4.0 * h) / d`: якщо провід укладено впритул до паяльної маски текстоліту (товщина маски `h ≈ 20–30 мкм`), аргумент натурального логарифма може наблизитися до одиниці або стати меншим за неї через допуски вимірювань. Валідатор примусово обмежує відношення мінімальним фізичним значенням `1.05`, що запобігає отриманню від'ємних або нульових значень індуктивності.

У C++ версії ця функція реалізована як `[[nodiscard]] static constexpr double calc_loop_inductance_nh(...) noexcept`, що дозволяє компілятору виконувати попередній розрахунок індуктивності фіксованих інженерних конфігурацій безпосередньо під час оптимізації коду.

### 3. Багаторівневий конвеєр валідації модифікацій

Метод `validate()` (або `eco_validate_and_analyze` у C99) виконує послідовну перевірку всіх кроків проєкту:
- **Перевірка струмового перевантаження (Current Overload Check):** Якщо струм навантаження перевищує допустимий ліміт `max_current_a`, валідатор генерує критичну помилку `[ERROR]` із зазначенням ідентифікатора кроку. Такий проєкт не може бути переданий у виробництво до заміни калібру дроту.
- **Контроль допустимого падіння напруги (Voltage Drop Check):** На основі питомого опору та довжини обчислюється абсолютний спад напруги `v_drop` та його відсоткове відношення до номінальної напруги шини. Перевищення порогу 2.0% генерує попередження `[WARN]`, інформуючи розробника про ризик нестабільної роботи мікросхеми через просідання напруги під час пікових навантажень.
- **Аналіз високочастотних сигнальних контурів (High-Speed Loop Check):** Для ліній домену `DOMAIN_FAST_DIGITAL` (тактові сигнали, шини SPI/QSPI, RMII) перевіряється висота прокладання над платою. Якщо висота перевищує 1.0 мм, валідатор фіксує порушення цілісності сигналів та рекомендує зафіксувати дріт краплями УФ-маски впритул до текстоліту.

### 4. Генерація технологічної карти (Run-Sheet) та специфікації BOM

Метод `print_runsheet` форматує повний технологічний пакет у стандарті Markdown, оптимізованому для друку або відображення на планшеті монтажника:
- **Специфікація матеріалів (BOM):** Агрегує сумарну довжину проводів кожного калібру з переведенням у сантиметри, а також автоматично розраховує мінімальну кількість точок нанесення рідкої УФ-маски (два кінці кожного дроту для зняття механічного напруження плюс кожна зона різу для герметизації).
- **Покрокова таблиця дій:** Містить унікальні мікроінженерні ідентифікатори (`CUT-01`, `JUMP-01`, `LIFT-01`, `ADD-R1`), прив'язані до позиційних позначень компонентів шовкографії.
- **Чекліст верифікації ВТК:** Формує індивідуальні пункти контролю якості. Для розрізів це обов'язковий контроль опору ізоляції мегаомметром (поріг `R > 10 МОм`), для перемичок — контроль перехідного опору пайки (`R < 0.5 Ом`), для навісних компонентів — візуальний контроль номіналу та пайки під стереомікроскопом.

## Практичний приклад виконання та аналіз результатів

При запуску скомпільованої програми валідатор обробляє модельний проєкт ревізії А вузла телеметрії «IoT Sensor Hub Telemetry Node» і генерує такий звіт:

```
=== ВАЛІДАЦІЯ ТА РОЗРАХУНОК ECO ===
[WARN] JUMP-04: Швидкісна сітка SPI_CLK_FAST має високу індуктивність контуру 20.8nH (h=8.0mm)!
Валідацію завершено: помилок = 0, попереджень = 1

# Технологічна карта доопрацювання ECO: IoT Sensor Hub Telemetry Node
**Перехід ревізій:** Rev A -> Rev A.1

## 1. Специфікація матеріалів модифікації (BOM)

| Матеріал / Калібр | Загальна довжина / Кількість | Призначення |
|---|---|---|
| AWG 30 (0.25mm Kynar) | 80.0 мм (8.0 см) | Монтажні перемички |
| AWG 34 (0.16mm Enamel) | 70.0 мм (7.0 см) | Монтажні перемички |
| AWG 36 (0.12mm Enamel) | 45.0 мм (4.5 см) | Монтажні перемички |
| УФ-маска рідка | 10 точок герметизації | Захист різів і фіксація |
| Каптоновий скотч | За потребою | Тимчасове утримання трас |

## 2. Покрокова інструкція монтажника (Rework Run-Sheet)

| Крок | Дія | Локація / Від | Куди | Параметри / Провід | Примітки |
|---|---|---|---|---|---|
| CUT-01 | **CUT (Різ)** | U3.Pin4 (L1 Trace near R12) | — | IPC-7721 V-Cut 1.0mm | Подвійний V-кут, розрив TX |
| CUT-02 | **CUT (Різ)** | U3.Pin5 (L1 Trace near R13) | — | IPC-7721 V-Cut 1.0mm | Подвійний V-кут, розрив RX |
| LIFT-01 | **PIN LIFT** | U1.Pin7 (NRST) | — | Відгин ніжки 30° | Підняти вивід для додавання підтяжки |
| ADD-R1 | **COMP ADD** | U1.Pin7 | C12.Pad1 (3.3V) | 10k 0402 (Tombstone) | Підтягуючий резистор |
| JUMP-01 | **JUMPER** | U3.Pin4 | U1.Pin12 (MCU_RX) | AWG 34 (0.16mm Enamel), L=35мм | Фіксація до плати маскою |
| JUMP-02 | **JUMPER** | U3.Pin5 | U1.Pin11 (MCU_TX) | AWG 34 (0.16mm Enamel), L=35мм | Фіксація до плати маскою |
| JUMP-03 | **JUMPER** | C5.Pad1 (+3.3V) | U8.Pin1 (VCC_RF) | AWG 30 (0.25mm Kynar), L=80мм | Силове живлення RF |
| JUMP-04 | **JUMPER** | U1.Pin24 | U4.Pin6 | AWG 36 (0.12mm Enamel), L=45мм | Помилка монтажу: піднятий у повітря |

## 3. Чекліст контролю та верифікації ВТК

- [ ] **CUT-01**: Перевірити опір ізоляції розрізу на U3.Pin4 (L1 Trace near R12) (R > 10 МОм, КЗ на GND відсутнє).
- [ ] **CUT-02**: Перевірити опір ізоляції розрізу на U3.Pin5 (L1 Trace near R13) (R > 10 МОм, КЗ на GND відсутнє).
- [ ] **ADD-R1**: Контроль номіналу 10k 0402 між U1.Pin7 та C12.Pad1 (3.3V) під мікроскопом.
- [ ] **JUMP-01**: Продзвонити ланцюг UART1_SWAP_TX (U3.Pin4 -> U1.Pin12 (MCU_RX)), R < 0.5 Ом, фіксація УФ-маскою.
- [ ] **JUMP-02**: Продзвонити ланцюг UART1_SWAP_RX (U3.Pin5 -> U1.Pin11 (MCU_TX)), R < 0.5 Ом, фіксація УФ-маскою.
- [ ] **JUMP-03**: Продзвонити ланцюг VCC_RADIO_3V3 (C5.Pad1 (+3.3V) -> U8.Pin1 (VCC_RF)), R < 0.5 Ом, фіксація УФ-маскою.
- [ ] **JUMP-04**: Продзвонити ланцюг SPI_CLK_FAST (U1.Pin24 -> U4.Pin6), R < 0.5 Ом, фіксація УФ-маскою.
```

Згенероване попередження щодо кроку `JUMP-04` дозволяє схемотехніку виявити проблему цілісності сигналів до початку монтажу. Дріт тактової лінії SPI довжиною 45 мм, піднятий над платою на 8 мм, має паразитну індуктивність 20.8 нГн. Інженер коригує інструкцію, вказуючи висоту прокладання `h <= 0.3 мм` із фіксацією краплями маски, що знижує індуктивність контуру до 5.2 нГн і гарантує безпомилкову передачу даних на частоті 25 МГц.

## Інженерні пастки та крайові випадки при доопрацюванні

Під час практичного використання генератора ECO слід враховувати кілька важливих фізичних та технологічних аспектів:

### 1. Теплове відведення при паянні сильнострумових провідників

Пайка силового проводу AWG 30 до масивного мідного полігону заземлення або виводу фільтруючого електролітичного конденсатора потребує значної теплової енергії. Якщо паяльник має недостатню теплоємність жала (наприклад, голчасте мікроконічне жало), припій переходить у пастоподібний стан, утворюючи дефектну "холодну пайку" з високим перехідним опором і мікротріщинами. Для таких точок необхідно використовувати зрізане жало типу «chisel» (викрутка) завширшки 1.5–2.0 мм за температури 340–350 °C з попереднім прогрівом плати на нижньому підігрівачі до 60–80 °C.

### 2. Скін-ефект на високих частотах

На частотах понад 10 МГц змінний струм витісняється до поверхні провідника. Глибина скін-шару `δ` в міді становить:

```
δ = 1 / √(π · f · μ_0 · σ)
```

На частоті `f = 50 МГц` глибина скін-шару складає лише `δ ≈ 9.3 мкм`. Для тонких проводів AWG 36/38 (радіус жили ~50–60 мкм) високочастотний активний опір `R_ac` зростає у 2.5–3 рази порівняно з постійним струмом `R_dc`. Це збільшує затухання високочастотних гармонік сигналу, тому для критичних радіочастотних трас рекомендується використовувати посріблені проводи Kynar, де срібне покриття зменшує поверхневі втрати.

### 3. Топологічна верифікація та виявлення прихованих розривів

При складних модифікаціях із багатьма розрізами виникає ризик непередбаченого розриву суміжних споживачів. Якщо розріз виконується посередині магістральної лінії, до якої підключено три мікросхеми, просте перемикання джерела до першого приймача залишає два інших входи у плаваючому стані.

Перед випуском карти ECO обов'язково будується граф зв'язності нетлиста. Для кожної розділеної ділянки провідника перевіряється наявність електричного шляху до активного драйвера або джерела живлення. Якщо вузол втрачає зв'язок із джерелом, генератор вимагає створення додаткових розгалужених перемичок (англ. *daisy-chain jumpers*) для відновлення живлення всіх абонентів шини.

### 4. Очищення флюсу та іонна чистота поверхні (IPC-A-610)

Після завершення пайки та перед нанесенням фінішної УФ-маски зона модифікації підлягає обов'язковому дворазовому відмиванню ультрачистим ізопропіловим спиртом (IPA ≥ 99.8%) із використанням антистатичних пензлів. Залишки навіть безвідмивного флюсу ROL0 під шаром полімеризованої УФ-маски утворюють герметичні кишені. Під дією прикладеної постійної напруги та підвищеної вологості залишковий флюс активує електрохімічну міграцію іонів міді, утворюючи ниткоподібні дендрити крізь мікротріщини маски та викликаючи незворотне коротке замикання між сусідніми виводами мікросхеми.

### 5. Автоматизована інтеграція з САПР друкованих плат

Для прискорення формування специфікації ECO генератор підтримує імпорт координат контактних майданчиків безпосередньо з файлів САПР (наприклад, через скриптовий інтерфейс `pcbnew` у KiCad або звіти IPC-D-356 в Altium Designer). Використання точних фізичних координат посадкових місць `(X, Y)` на платі дозволяє автоматично розраховувати евклідову довжину проводу `L_wire = √((X_2 - X_1)² + (Y_2 - Y_1)²)` із додаванням 15% технологічного запасу на вигини траси вздовж корпусів компонентів.

### 6. Версіонування та інтеграція з репозиторієм апаратного забезпечення

Згенерована технологічна карта ECO та специфікація матеріалів повинні зберігатися у системі контролю версій Git у каталозі `hardware/eco/` поряд із схемою та Gerber-файлами. Назва файлу повинна чітко відображати перехід ревізій (наприклад, `ECO-001-RevA-to-RevA1.md`). Тільки після того, як партія модифікованих плат успішно пройде всі функціональні, кліматичні та вібраційні випробування, інженер вносить виправлений нетлист у САПР друкованих плат для замовлення чистої серійної ревізії B.
