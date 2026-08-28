# ⚙️ Трекер експозиції Floor Life та калькулятор сушіння компонентів

У сучасному промисловому виробництві друкованих плат на автоматизованій лінії поверхневого монтажу (SMT) одночасно встановлюються десятки котушок із компонентами різного рівня вологочутливості — від невибагливих пасивних чіп-резисторів рівня MSL 1 до критичних мікроконтролерів у корпусах QFN (MSL 3 або MSL 4) та багатовивідних процесорів BGA (MSL 5 або MSL 5a). Якщо облік часу перебування відкритих компонентів у цеху вести вручну за допомогою паперових журналів, маркерних записів на боковинах котушок або таблиць у загальному доступі, людський фактор неминуче призводить до технологічних помилок. Оператор забуває зафіксувати точний час відкриття пакета, не враховує нічні стрибки вологості в цеху або повертає залишок стрічки у звичайну картонну коробку замість сухої шафи. У результаті компоненти з вичерпаним строком Floor Life потрапляють у піч оплавлення припою, де перегріта пара розриває корпуси мікросхем зсередини («ефект попкорну»).

Цей проект пропонує повністю автономний вбудований та серверний програмний комплекс для автоматизованого відстеження життєвого циклу вологочутливих компонентів (**MSL Floor Life Tracker & Baking Recovery Calculator**). Програма підтримує скінченний автомат станів котушки (FSM), неперервну числову інтеграцію витрати Floor Life з урахуванням динамічного дерайтингу за поточною температурою та вологістю цеху (стандарт IPC/JEDEC J-STD-033), алгоритм накопичення кредиту десорбції за правилом 5x у сухих шафах з вологістю RH < 5%, контроль сумарного високотемпературного сушіння (залізничний ліміт 96 годин при 125 °C), перерахунок еквівалентної термодози при зміні температур сушіння та автоматичний вибір технологічного режиму сушіння залежно від конструктиву носія (стрічка, лоток, тубус).

---

### Фізико-математична модель та числова інтеграція експозиції

Номінальний строк цехового життя компонентів T_nominal за стандартом IPC/JEDEC J-STD-020 визначено строго для стандартних умов: температура повітря T₀ = 30 °C та відносна вологість RH₀ = 60%. У цих умовах парціальний тиск водяної пари в атмосфері становить:

```text
P_sat(30 °C) = 0.61078 * exp((17.27 * 30.0) / (30.0 + 237.3)) = 4.246 кПа
P_nominal = 0.60 * P_sat(30 °C) = 2.547 кПа
```

У реальному виробничому приміщенні температура T(t) та вологість RH(t) неперервно змінюються протягом доби. Згідно з першим законом Фіка та законом Генрі для полімерів, швидкість дифузійного потоку вологи крізь поверхню корпусу пропорційна миттєвому парціальному тиску пари:
```text
P_actual(t) = (RH(t) / 100.0) * P_sat(T(t))
```

Миттєвий безрозмірний коефіцієнт дерайтингу K(t) показує, у скільки разів швидше (або повільніше) компонент поглинає вологу порівняно зі стандартними умовами:

```text
K(t) = P_actual( T(t), RH(t) ) / P_nominal( 30 °C, 60% RH )
```

Ефективний витрачений час перебування компонента в цеху Δt_eff за проміжок часу від t₀ до t₁ обчислюється числовою інтеграцією миттєвого коефіцієнта дерайтингу:

```text
Δt_eff = ∫[t0..t1] K(t) dt ≈ ∑[i=1..N] ( (K(t_{i-1}) + K(t_i)) / 2 ) * Δt_i
```

Рушій трекера виконує дискретне інтегрування за методом трапецій при кожному надходженні нового вимірювання від цехових термогігрометрів. Залишок строку Floor Life L(t) на поточний момент часу зменшується на величину Δt_eff. Якщо L(t) досягає нуля, автомат негайно переводить деталь у заблокований стан.

```text
Динаміка коефіцієнта дерайтингу K для типових виробничих зон:
- Кондиційована чиста кімната (22 °C, 40% RH):   P_act = 1.057 кПа → K = 0.415 (життя довше у 2.4 раза)
- Стандартні номінальні умови (30 °C, 60% RH):   P_act = 2.547 кПа → K = 1.000 (номінальна швидкість)
- Спекотний літній цех без осушення (28 °C, 75% RH): P_act = 2.836 кПа → K = 1.113 (життя скорочується)
- Критично вологий цех (32 °C, 85% RH):           P_act = 4.043 кПа → K = 1.587 (життя тане у 1.6 раза швидше)
```

---

### Архітектура скінченного автомата станів (FSM)

Життєвий цикл кожної одиниці тари (котушки *Tape & Reel*, тубуса або матричного лотка *JEDEC Tray*) формалізується у вигляді семи строго визначених станів із детермінованими переходами:

```text
       [ Запечатано в MBB ] (SEALED_IN_MBB)
                 |
                 | (Розпакування, зчитування HIC = OK)
                 v
   +-----> [ Експозиція в цеху ] (EXPOSED_ON_LINE) <-----+
   |             |                     |                 |
   | (Винос)     | (RH < 10%)          | (RH < 5%)       | (Відновлено 5x)
   |             v                     v                 |
   |      [ Пауза в шафі ]      [ Відновлення 5x ] ------+
   |     (PAUSED_DRY_10RH)      (RECOVERING_5RH)
   |             |                     |
   |             | (Час вичерпано)     | (Час вичерпано)
   |             +----------+----------+
   |                        |
   |                        v
   |             [ Прострочено: потрібен Bake ] (EXPIRED_NEEDS_BAKE)
   |                        |
   |                        | (Завантаження в піч 125 °C / 90 °C / 40 °C)
   |                        v
   |             [ Сушіння в термопечі ] (BAKING_IN_OVEN)
   |                        |
   +------------------------+ (Завершення циклу сушіння: Floor Life = 100%)
                 |
                 | (Успішний монтаж на плату та проходження печі)
                 v
       [ Оплавлено в печі SMT ] (CONSUMED_IN_REFLOW)
```

#### Детальний аналіз станів та правил переходів

1. **Стан `SEALED_IN_MBB` (Герметично запечатано в пакеті MBB):**
   Початковий стан нової котушки на складі. Вміст вологи всередині пакету контролюється пакетиком осушувача. Лічильник залишкового цехового життя становить строго 100% від номіналу (L = T_nominal). Перехід у робочий стан `EXPOSED_ON_LINE` здійснюється оператором через сканування штрихкоду під час відкриття пакету в антистатичній зоні (EPA). Якщо при відкритті виявлено, що індикаторна картка HIC змінила колір (10% пляма стала рожевою для MSL 2a–5a або 5% рожева для MSL 2), оператор фіксує порушення умов транспортування, і котушка автоматично скеровується у стан `EXPIRED_NEEDS_BAKE`.

2. **Стан `EXPOSED_ON_LINE` (Відкрито в цеху на лінії монтажу):**
   Котушка встановлена у фідер автомата Pick-and-Place або лежить на робочому столі комплектації. При кожному кванті часу Δt залишкова квота Floor Life зменшується на величину Δt_eff = K(t) * Δt. Одночасно накопичується лічильник неперервної поточної сесії експозиції t_session. Якщо L(t) зменшується до нуля, генератор подій переводить котушку у стан `EXPIRED_NEEDS_BAKE`, а програмний інтерфейс виставляє апаратне блокування живильника на складальній лінії.

3. **Стан `PAUSED_DRY_10RH` (Пауза в стандартній сухій шафі з 5% < RH ≤ 10%):**
   Котушку зняли з лінії монтажу після завершення виробничої зміни та помістили в суху шафу з контролем вологості на рівні 5–10%. За стандартом J-STD-033 таке середовище повністю зупиняє подальше поглинання вологи полімером, але не забезпечує достатнього градієнта концентрації для швидкої зворотної десорбції. Витрата Floor Life заморожується. При повторному винесенні котушки на лінію монтажу відлік Floor Life продовжується з точки зупинки.

4. **Стан `RECOVERING_5RH` (Сухе відновлення в шафі ультранизької вологості RH ≤ 5%):**
   Якщо котушка провела на відкритому повітрі відносно короткий час t_session, що не перевищує граничного порогу короткої експозиції T_short_limit (12 годин для MSL 2, 2a, 3 або 8 годин для MSL 4, 5, 5a), волога встигла проникнути лише в найтонший приповерхневий шар компаунда, не досягнувши межі розділу кристала. Поміщення такої котушки в шафу з RH ≤ 5% запускає процес відновлення за правилом 5x: кожна година перебування в шафі накопичує кредит десорбції. Щойно час у шафі досягає значення:
   ```text
   t_dry = 5 * t_session
   ```
   лічильник Floor Life повністю відновлюється до 100% (L = T_nominal), поточна сесія скидається в нуль, і компонент повертає повний заводський запас цехового життя без термічного навантаження на виводи.

5. **Стан `EXPIRED_NEEDS_BAKE` (Прострочено, потрібне обов'язкове сушіння):**
   Компонент увібрав надлишкову критичну кількість вологи (залишок Floor Life вичерпано або час перебування в цеху перевищив T_short_limit без вчасного відновлення). Паяти такий чіп категорично заборонено. Єдиний дозволений шлях подальшого використання — переміщення котушки або лотка в термошафу для проходження циклу термічного зневоднення (*Baking*).

6. **Стан `BAKING_IN_OVEN` (Термічне сушіння в печі):**
   Компоненти витримуються в термокамері при контрольованій температурі. Рушій відстежує зворотний відлік необхідного часу витримки відповідно до товщини корпусу та рівня MSL. Для високотемпературного режиму (125 °C) ведеться суворий облік сумарного часу термічного стресу: якщо сумарний час за всі попередні цикли сушіння перевищує 96 годин, котушка вибраковується через незворотне потовщення крихкого інтерметалідного шару Cu₆Sn₅ на виводах, що призводить до незмочування припоєм.

7. **Стан `CONSUMED_IN_REFLOW` (Успішно встановлено та запаяно):**
   Компоненти змонтовані на плату й успішно пройшли піч оплавлення припою в межах валідного Floor Life. Запис у базі даних архівується для забезпечення повної простежуваності виробу (*Traceability*).

---

### Розрахунок дробового сушіння та еквівалентної термодози

На практиці трапляються ситуації, коли компоненти почали сушити при одній температурі, але через виробничу необхідність (наприклад, звільнення печі 125 °C) деталі переводять в інший температурний режим (наприклад, 90 °C або суху шафу 40 °C).

Для коректного врахування частково завершеного сушіння рушій обчислює частку виведеної вологи η(t) за лінійним нормуванням:

```text
η = t_витримки_1 / T_потрібне_1

Залишковий час при новій температурі:
t_залишок_2 = (1.0 - η) * T_потрібне_2
```

Наприклад, мікросхема MSL 3 товщиною 1.4 мм потребує 9 годин при 125 °C або 27 годин при 90 °C. Якщо вона пробула при 125 °C рівно 6 годин (η = 6/9 = 0.667), а потім була переміщена в середньотемпературну шафу 90 °C, залишковий час складе:
```text
t_залишок = (1.0 - 0.667) * 27.0 = 9.0 годин при 90 °C.
```

Цей підхід дозволяє комбінувати різні технологічні печі без ризику недосушування компонентів.

---

### Вибір температурних режимів сушіння та розрахунок часу

Тривалість термічного зневоднення експоненційно залежить від температури процесу та квадрата товщини корпусу мікросхеми. Стандарт IPC/JEDEC J-STD-033 регламентує нормативні часи витримки при трьох фіксованих температурах:

```text
Матриця необхідного часу сушіння (години) для компонентів різної товщини:

Товщина <= 1.4 мм (QFP, TQFP, TSSOP, QFN):
- MSL 2:   125 °C = 5 год   | 90 °C = 17 год  | 40 °C (RH<=5%) = 72 год (3 доби)
- MSL 2a:  125 °C = 7 год   | 90 °C = 23 год  | 40 °C (RH<=5%) = 120 год (5 діб)
- MSL 3:   125 °C = 9 год   | 90 °C = 27 год  | 40 °C (RH<=5%) = 192 год (8 діб)
- MSL 4:   125 °C = 11 год  | 90 °C = 34 год  | 40 °C (RH<=5%) = 240 год (10 діб)
- MSL 5:   125 °C = 15 год  | 90 °C = 41 год  | 40 °C (RH<=5%) = 312 год (13 діб)
- MSL 5a:  125 °C = 20 год  | 90 °C = 48 год  | 40 °C (RH<=5%) = 360 год (15 діб)

Товщина <= 2.0 мм (товсті QFP, стандартні BGA):
- MSL 3:   125 °C = 18 год  | 90 °C = 54 год  | 40 °C (RH<=5%) = 360 год (15 діб)
- MSL 4:   125 °C = 21 год  | 90 °C = 63 год  | 40 °C (RH<=5%) = 432 год (18 діб)

Товщина <= 4.5 мм (масивні силові модулі, товсті BGA):
- MSL 3:   125 °C = 48 год  | 90 °C = 144 год | 40 °C (RH<=5%) = 1080 год (45 діб)
```

Технологічний вибір температури сушіння жорстко обмежений матеріалом тари, у якій знаходяться мікросхеми:
- **Сушіння при 125 °C (найшвидше):** Дозволено лише для матричних піддонів **JEDEC Trays**, виготовлених із високотемпературних рідкокристалічних полімерів (LCP) з маркуванням `MAX 150°C`. Звичайні котушки розплавляться при цій температурі протягом 10 хвилин.
- **Сушіння при 90 °C (RH ≤ 5%):** Застосовується для термостійких тубусів та спеціальних піддонів із маркуванням `MAX 100°C`.
- **Сушіння при 40 °C (RH ≤ 5%):** Єдиний дозволений режим для сушіння компонентів безпосередньо у пластикових стрічках на котушках (*Tape & Reel*). Полістирольна або полікарбонатна стрічка розм'якшується вже при 55–60 °C, а захисна плівка (*Cover Tape*) відшаровується. Низькотемпературне сушіння при 40 °C триває від 8 до 15 діб, але повністю виключає трудомістку операцію пересипання мікросхем у термостійкі лотки.

---

### Апаратна реалізація бездротових трекерів та сухих шаф

Для побудови розподіленої системи контролю вологозахисту на заводі застосовують спеціалізовані апаратні вузли двох рівнів:

1. **Розумний ярлик котушки (Smart Feeder IoT Tag):**
   Компактний модуль на базі ультраекономічного мікроконтролера (STM32L0 або nRF52) з графічним дисплеєм на електронному папері (E-Paper 2.13"). Модуль кріпиться безпосередньо на пластикову боковину котушки. На екрані постійно відображаються рівень MSL, поточний стан FSM та велика кругова діаграма залишку Floor Life у годинах та відсотках. Модуль виходить в ефір по протоколу BLE Mesh або Sub-GHz (868 МГц) щохвилини, передаючи свій стан центральному серверу. Завдяки технології E-Paper екран споживає енергію лише під час зміни зображення, забезпечуючи 3–5 років автономної роботи від однієї літієвої батарейки CR2450.

2. **Автоматизований контролер сухої шафи (Dry Cabinet Controller):**
   Шафи сухого зберігання обладнують електронними модулями осушення на основі твердотільних електролітичних мембран або автоматичних подвійних колон із силікагелем, що почергово регенеруються вбудованими нагрівачами. Контролер шафи зчитує показання прецизійного датчика вологості (наприклад, Sensirion SHT41 з похибкою ± 1.5% RH), фіксує кожне відкриття дверей за допомогою магнітного геркона та передає серверу точні інтервали знаходження кожної котушки всередині камери.

---

### Журнал аудиту та відповідність стандартам IATF 16949 та ISO 9001

Для виробництв автомобільної (Automotive), аерокосмічної та медичної електроніки відповідність стандартам IATF 16949 вимагає 100% цифрового аудиту історії кожної партії деталей (*Audit Trail*).

Програмний рушій формує незмінний цифровий журнал подій (*Event Log*) у форматі JSON-Lines, де кожен запис містить:
- унікальний ідентифікатор котушки (*UID / DataMatrix*);
- тип події (`UNPACK`, `MOVE_TO_DRY_CABINET`, `MOVE_TO_LINE`, `START_BAKE`, `ALARM_EXPIRED`);
- значення температури та вологості навколишнього середовища;
- розрахований коефіцієнт дерайтингу та залишок Floor Life;
- електронний підпис оператора (ID картки доступу).

У разі виникнення польового відмови блоку керування автовиробник може за номером серії плати розгорнути точну хронологію: коли відкрили котушку процесора, у якій зоні цеху вона перебувала та скільки годин Floor Life залишалося на момент проходження печі оплавлення.

---

### Обробка крайових випадків та збоїв датчиків (FMEA)

У реальній промисловій системі програмний рушій повинен стійко обробляти нештатні та аварійні ситуації:

1. **Втрата зв'язку з датчиком температури/вологості:**
   Якщо цифровий термогігрометр на SMT-лінії не відповідає по шині Modbus/RS-485 протягом 5 хвилин, трекер автоматично перемикається в безпечний аварійний режим (*Fail-Safe Fallback*), приймаючи розрахункові умови цеху рівними найгіршому консервативному сценарію: 35 °C та 90% RH (K_derating ≈ 1.95). Одночасно генерується тривожне сповіщення оператору.

2. **Дробова циклічна експозиція:**
   Якщо котушку виносили на лінію кілька разів підряд на короткі проміжки (наприклад, 3 сесії по 2 години), лічильник поточної сесії t_session підсумовує загальну експозицію. Якщо сума перевищує 12 годин без завершення повного 5x циклу відновлення, режим швидкого відновлення блокується, і деталі перенаправляються на термічний Bake.

3. **Апаратний збій живлення контролера:**
   Усі стани та накопичені часові мітки зберігаються в енергонезалежній пам'яті (EEPROM або NVRAM) з контрольною сумою CRC-32. При перезавантаженні система зчитує час із годинника реального часу (RTC) з батарейним живленням, обчислює час відсутності живлення та автоматично списує відповідну квоту Floor Life.

---

### Повна реалізація рушія на мові C99

Нижче наведено повний вихідний код модуля трекера на чистому C99. Програма містить повноцінну модель FSM, розрахунок дерайтингу за формулою Тетенса, обробку подій, журнал переходів та демонстраційний сценарій життєвого циклу.

:::tabs
@tab C99
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#define MAX_NAME_LEN 64

typedef enum {
    MSL_1 = 0,
    MSL_2,
    MSL_2A,
    MSL_3,
    MSL_4,
    MSL_5,
    MSL_5A,
    MSL_6
} msl_class_t;

typedef enum {
    STATE_SEALED = 0,
    STATE_EXPOSED,
    STATE_PAUSED_DRY_10RH,
    STATE_RECOVERING_5RH,
    STATE_EXPIRED_NEEDS_BAKE,
    STATE_BAKING,
    STATE_CONSUMED
} tracker_state_t;

typedef enum {
    PKG_THICKNESS_LE_1_4MM = 0,
    PKG_THICKNESS_LE_2_0MM,
    PKG_THICKNESS_LE_4_5MM
} pkg_thickness_t;

typedef struct {
    msl_class_t msl;
    const char* label;
    double nominal_floor_life_hours;
    double max_short_exposure_hours;
} msl_metadata_t;

static const msl_metadata_t MSL_TABLE[] = {
    { MSL_1,  "MSL 1",  1e9,    1e9  },
    { MSL_2,  "MSL 2",  8760.0, 12.0 },
    { MSL_2A, "MSL 2a", 672.0,  12.0 },
    { MSL_3,  "MSL 3",  168.0,  12.0 },
    { MSL_4,  "MSL 4",  72.0,   8.0  },
    { MSL_5,  "MSL 5",  48.0,   8.0  },
    { MSL_5A, "MSL 5a", 24.0,   8.0  },
    { MSL_6,  "MSL 6",  6.0,    0.0  }
};

static const double BAKE_HOURS_125C[8][3] = {
    { 0,  0,   0  },
    { 5,  7,   9  },
    { 7,  8,   10 },
    { 9,  18,  48 },
    { 11, 21,  48 },
    { 15, 24,  48 },
    { 20, 28,  48 },
    { 24, 32,  48 }
};

typedef struct {
    char part_number[MAX_NAME_LEN];
    char lot_id[MAX_NAME_LEN];
    msl_class_t msl;
    pkg_thickness_t thickness;
    tracker_state_t state;
    
    double floor_life_remaining_hours;
    double current_exposure_run_hours;
    double recovery_credit_hours;
    
    double cumulative_bake_125c_hours;
    double current_bake_remaining_hours;
    
    bool hic_ok_on_open;
    bool is_active;
} component_reel_t;

static double calc_saturation_vapor_pressure(double temp_c) {
    return 0.61078 * exp((17.27 * temp_c) / (temp_c + 237.3));
}

static double calc_environmental_derating(double temp_c, double rh_percent) {
    double p_sat_curr = calc_saturation_vapor_pressure(temp_c);
    double p_actual = (rh_percent / 100.0) * p_sat_curr;
    
    double p_sat_nom = calc_saturation_vapor_pressure(30.0);
    double p_nom = 0.60 * p_sat_nom;
    
    double k = p_actual / p_nom;
    return (k < 0.1) ? 0.1 : k;
}

void reel_init(component_reel_t* reel, const char* part_num, const char* lot,
               msl_class_t msl, pkg_thickness_t th) {
    memset(reel, 0, sizeof(component_reel_t));
    strncpy(reel->part_number, part_num, MAX_NAME_LEN - 1);
    strncpy(reel->lot_id, lot, MAX_NAME_LEN - 1);
    reel->msl = msl;
    reel->thickness = th;
    reel->state = STATE_SEALED;
    reel->floor_life_remaining_hours = MSL_TABLE[msl].nominal_floor_life_hours;
    reel->is_active = true;
}

bool reel_event_unpack(component_reel_t* reel, bool hic_10_percent_blue) {
    if (reel->state != STATE_SEALED) {
        printf("[ПОМИЛКА] Котушка %s вже розпакована!\n", reel->part_number);
        return false;
    }
    reel->hic_ok_on_open = hic_10_percent_blue;
    if (!hic_10_percent_blue) {
        reel->state = STATE_EXPIRED_NEEDS_BAKE;
        reel->floor_life_remaining_hours = 0.0;
        printf("[УВАГА] HIC індикатор вологий! Котушка %s переведена на обов'язковий Bake.\n", reel->part_number);
        return false;
    }
    reel->state = STATE_EXPOSED;
    reel->current_exposure_run_hours = 0.0;
    printf("[OK] Котушка %s розпакована. MSL: %s, Запас Floor Life: %.1f год.\n",
           reel->part_number, MSL_TABLE[reel->msl].label, reel->floor_life_remaining_hours);
    return true;
}

bool reel_event_store_in_dry_cabinet(component_reel_t* reel, double cabinet_rh) {
    if (reel->state != STATE_EXPOSED) {
        printf("[ПОМИЛКА] Перемістити в суху шафу можна лише відкриту котушку.\n");
        return false;
    }
    if (cabinet_rh <= 5.0) {
        reel->state = STATE_RECOVERING_5RH;
        reel->recovery_credit_hours = 0.0;
        printf("[FSM] Котушка %s -> Суха шафа RH < 5%% (Режим відновлення 5x).\n", reel->part_number);
    } else if (cabinet_rh <= 10.0) {
        reel->state = STATE_PAUSED_DRY_10RH;
        printf("[FSM] Котушка %s -> Суха шафа RH < 10%% (Режим паузи).\n", reel->part_number);
    } else {
        printf("[ПОМИЛКА] Вологість шафи %.1f%% занадто висока (>10%%)!\n", cabinet_rh);
        return false;
    }
    return true;
}

bool reel_event_start_baking(component_reel_t* reel, double bake_temp_c) {
    if (reel->state != STATE_EXPIRED_NEEDS_BAKE && reel->state != STATE_EXPOSED) {
        printf("[ПОМИЛКА] Некоректний стан для старту сушіння.\n");
        return false;
    }
    double required_hours = 0.0;
    if (fabs(bake_temp_c - 125.0) < 5.0) {
        required_hours = BAKE_HOURS_125C[reel->msl][reel->thickness];
        if (reel->cumulative_bake_125c_hours + required_hours > 96.0) {
            printf("[КРИТИЧНО] Ліміт сумарного сушіння 96 год при 125 °C буде перевищено!\n");
            return false;
        }
    } else if (fabs(bake_temp_c - 40.0) < 5.0) {
        required_hours = BAKE_HOURS_125C[reel->msl][reel->thickness] * 18.0;
    } else {
        printf("[ПОМИЛКА] Непідтримувана температура сушіння: %.1f °C\n", bake_temp_c);
        return false;
    }
    reel->state = STATE_BAKING;
    reel->current_bake_remaining_hours = required_hours;
    printf("[BAKE] Котушка %s -> Піч %.0f °C. Потрібно: %.1f годин.\n",
           reel->part_number, bake_temp_c, required_hours);
    return true;
}

void reel_tick_time(component_reel_t* reel, double delta_hours, double ambient_t, double ambient_rh) {
    if (!reel->is_active) return;
    switch (reel->state) {
        case STATE_EXPOSED: {
            double derating = calc_environmental_derating(ambient_t, ambient_rh);
            double effective_spent = delta_hours * derating;
            reel->current_exposure_run_hours += delta_hours;
            reel->floor_life_remaining_hours -= effective_spent;
            if (reel->floor_life_remaining_hours <= 0.0) {
                reel->floor_life_remaining_hours = 0.0;
                reel->state = STATE_EXPIRED_NEEDS_BAKE;
                printf("[АВАРІЯ] Котушка %s: Floor Life ВИЧЕРПАНО! Пайку заблоковано.\n", reel->part_number);
            }
            break;
        }
        case STATE_RECOVERING_5RH: {
            reel->recovery_credit_hours += delta_hours;
            double max_short = MSL_TABLE[reel->msl].max_short_exposure_hours;
            double required_recovery = 5.0 * reel->current_exposure_run_hours;
            if (reel->current_exposure_run_hours <= max_short &&
                reel->recovery_credit_hours >= required_recovery) {
                reel->floor_life_remaining_hours = MSL_TABLE[reel->msl].nominal_floor_life_hours;
                reel->current_exposure_run_hours = 0.0;
                reel->recovery_credit_hours = 0.0;
                printf("[ВІДНОВЛЕНО] Котушка %s: Floor Life повністю відновлено до 100%% за правилом 5x!\n",
                       reel->part_number);
            }
            break;
        }
        case STATE_BAKING: {
            reel->current_bake_remaining_hours -= delta_hours;
            reel->cumulative_bake_125c_hours += delta_hours;
            if (reel->current_bake_remaining_hours <= 0.0) {
                reel->current_bake_remaining_hours = 0.0;
                reel->floor_life_remaining_hours = MSL_TABLE[reel->msl].nominal_floor_life_hours;
                reel->current_exposure_run_hours = 0.0;
                reel->state = STATE_PAUSED_DRY_10RH;
                printf("[СУШІННЯ ЗАВЕРШЕНО] Котушка %s повністю зневоднена та готова до монтажу.\n",
                       reel->part_number);
            }
            break;
        }
        default:
            break;
    }
}

void reel_print_status(const component_reel_t* reel) {
    const char* state_names[] = {
        "SEALED_IN_MBB", "EXPOSED_ON_LINE", "PAUSED_DRY_10RH",
        "RECOVERING_5RH", "EXPIRED_NEEDS_BAKE", "BAKING_IN_OVEN", "CONSUMED_REFLOW"
    };
    printf("┌─────────────────────────────────────────────────────────────┐\n");
    printf("│ ДЕТАЛЬ: %-20s ЛОТ: %-15s MSL: %-6s │\n",
           reel->part_number, reel->lot_id, MSL_TABLE[reel->msl].label);
    printf("│ СТАН:   %-20s ЗАЛИШОК LIFE: %6.1f год       │\n",
           state_names[reel->state], reel->floor_life_remaining_hours);
    printf("│ ЕКСПОЗИЦІЯ СЕСІЇ: %5.1f год    СУМАРНИЙ BAKE 125°C: %4.1f год │\n",
           reel->current_exposure_run_hours, reel->cumulative_bake_125c_hours);
    printf("└─────────────────────────────────────────────────────────────┘\n");
}

int main(void) {
    printf("=== ДЕМОНСТРАЦІЯ РОБОТИ MSL FLOOR LIFE TRACKER (C99) ===\n\n");
    component_reel_t qfn_chip;
    reel_init(&qfn_chip, "STM32H743IIT6", "LOT-2026-A89", MSL_3, PKG_THICKNESS_LE_1_4MM);
    reel_event_unpack(&qfn_chip, true);
    reel_print_status(&qfn_chip);
    
    printf("\n>>> Робота на SMT лінії протягом 8 годин при 30 °C / 75%% RH...\n");
    for (int i = 0; i < 8; ++i) {
        reel_tick_time(&qfn_chip, 1.0, 30.0, 75.0);
    }
    reel_print_status(&qfn_chip);
    
    printf("\n>>> Зняття залишку котушки в суху шафу RH < 5%% на відновлення...\n");
    reel_event_store_in_dry_cabinet(&qfn_chip, 3.0);
    
    for (int i = 0; i < 40; ++i) {
        reel_tick_time(&qfn_chip, 1.0, 22.0, 3.0);
    }
    reel_print_status(&qfn_chip);
    return 0;
}
```
@tab C++20
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <array>
#include <vector>
#include <optional>
#include <expected>
#include <cmath>
#include <format>

namespace tracker {

using namespace std::chrono_literals;

enum class MslLevel : uint8_t {
    Msl1 = 0, Msl2, Msl2a, Msl3, Msl4, Msl5, Msl5a, Msl6
};

enum class State : uint8_t {
    SealedInMbb,
    ExposedOnLine,
    PausedDry10Rh,
    Recovering5Rh,
    ExpiredNeedsBake,
    BakingInOven,
    ConsumedInReflow
};

enum class PkgThickness : uint8_t {
    Le1_4mm = 0,
    Le2_0mm,
    Le4_5mm
};

struct MslTraits {
    MslLevel level;
    std::string_view label;
    std::chrono::hours nominal_floor_life;
    std::chrono::hours max_short_exposure;
};

constexpr std::array<MslTraits, 8> MslTable = {{
    { MslLevel::Msl1,  "MSL 1",  std::chrono::hours::max(), std::chrono::hours::max() },
    { MslLevel::Msl2,  "MSL 2",  8760h,                     12h },
    { MslLevel::Msl2a, "MSL 2a", 672h,                      12h },
    { MslLevel::Msl3,  "MSL 3",  168h,                      12h },
    { MslLevel::Msl4,  "MSL 4",  72h,                       8h  },
    { MslLevel::Msl5,  "MSL 5",  48h,                       8h  },
    { MslLevel::Msl5a, "MSL 5a", 24h,                       8h  },
    { MslLevel::Msl6,  "MSL 6",  6h,                        0h  }
}};

constexpr std::array<std::array<std::chrono::hours, 3>, 8> BakeTable125C = {{
    { 0h,  0h,  0h  },
    { 5h,  7h,  9h  },
    { 7h,  8h,  10h },
    { 9h,  18h, 48h },
    { 11h, 21h, 48h },
    { 15h, 24h, 48h },
    { 20h, 28h, 48h },
    { 24h, 32h, 48h }
}};

[[nodiscard]] double calculate_derating(double temp_c, double rh_percent) noexcept {
    const auto p_sat = [](double t) {
        return 0.61078 * std::exp((17.27 * t) / (t + 237.3));
    };
    const double p_actual = (rh_percent / 100.0) * p_sat(temp_c);
    const double p_nominal = 0.60 * p_sat(30.0);
    return std::max(0.1, p_actual / p_nominal);
}

class ComponentReel {
public:
    ComponentReel(std::string part_number, std::string lot_id,
                  MslLevel msl, PkgThickness thickness)
        : part_number_(std::move(part_number)),
          lot_id_(std::move(lot_id)),
          msl_(msl),
          thickness_(thickness),
          state_(State::SealedInMbb),
          floor_life_remaining_(MslTable[static_cast<size_t>(msl)].nominal_floor_life) {}

    [[nodiscard]] std::expected<void, std::string_view> unpack(bool hic_10_percent_blue) noexcept {
        if (state_ != State::SealedInMbb) {
            return std::unexpected("Котушка вже була відкрита раніше.");
        }
        if (!hic_10_percent_blue) {
            state_ = State::ExpiredNeedsBake;
            floor_life_remaining_ = 0h;
            return std::unexpected("HIC індикатор сигналізує про зволоження! Потрібен Bake.");
        }
        state_ = State::ExposedOnLine;
        current_session_exposure_ = 0h;
        return {};
    }

    [[nodiscard]] std::expected<void, std::string_view> store_in_dry_cabinet(double cabinet_rh) noexcept {
        if (state_ != State::ExposedOnLine) {
            return std::unexpected("У суху шафу можна помістити лише відкриту котушку.");
        }
        if (cabinet_rh <= 5.0) {
            state_ = State::Recovering5Rh;
            recovery_credit_ = 0h;
        } else if (cabinet_rh <= 10.0) {
            state_ = State::PausedDry10Rh;
        } else {
            return std::unexpected("Вологість шафи перевищує ліміт 10% RH.");
        }
        return {};
    }

    [[nodiscard]] std::expected<void, std::string_view> start_baking(double temp_c) noexcept {
        if (state_ != State::ExpiredNeedsBake && state_ != State::ExposedOnLine) {
            return std::unexpected("Сушіння не дозволено в поточному стані.");
        }
        if (std::abs(temp_c - 125.0) < 5.0) {
            const auto needed = BakeTable125C[static_cast<size_t>(msl_)][static_cast<size_t>(thickness_)];
            if (cumulative_bake_125c_ + needed > 96h) {
                return std::unexpected("Критично: перевищення сумарного ліміту 96 год при 125 °C!");
            }
            current_bake_remaining_ = needed;
        } else if (std::abs(temp_c - 40.0) < 5.0) {
            const auto needed = BakeTable125C[static_cast<size_t>(msl_)][static_cast<size_t>(thickness_)] * 18;
            current_bake_remaining_ = needed;
        } else {
            return std::unexpected("Непідтримуваний температурний режим печі.");
        }
        state_ = State::BakingInOven;
        return {};
    }

    void tick(std::chrono::hours dt, double ambient_t, double ambient_rh) noexcept {
        switch (state_) {
            case State::ExposedOnLine: {
                const double derating = calculate_derating(ambient_t, ambient_rh);
                const auto effective_spent = std::chrono::hours(static_cast<int64_t>(std::ceil(dt.count() * derating)));
                current_session_exposure_ += dt;
                if (effective_spent >= floor_life_remaining_) {
                    floor_life_remaining_ = 0h;
                    state_ = State::ExpiredNeedsBake;
                } else {
                    floor_life_remaining_ -= effective_spent;
                }
                break;
            }
            case State::Recovering5Rh: {
                recovery_credit_ += dt;
                const auto max_short = MslTable[static_cast<size_t>(msl_)].max_short_exposure;
                const auto needed = current_session_exposure_ * 5;
                if (current_session_exposure_ <= max_short && recovery_credit_ >= needed) {
                    floor_life_remaining_ = MslTable[static_cast<size_t>(msl_)].nominal_floor_life;
                    current_session_exposure_ = 0h;
                    recovery_credit_ = 0h;
                }
                break;
            }
            case State::BakingInOven: {
                cumulative_bake_125c_ += dt;
                if (dt >= current_bake_remaining_) {
                    current_bake_remaining_ = 0h;
                    floor_life_remaining_ = MslTable[static_cast<size_t>(msl_)].nominal_floor_life;
                    current_session_exposure_ = 0h;
                    state_ = State::PausedDry10Rh;
                } else {
                    current_bake_remaining_ -= dt;
                }
                break;
            }
            default:
                break;
        }
    }

    void print_status() const {
        std::cout << std::format("Деталь: {:<16} Лот: {:<12} MSL: {:<6} Залишок Life: {:>5}h\n",
                                 part_number_, lot_id_,
                                 MslTable[static_cast<size_t>(msl_)].label,
                                 floor_life_remaining_.count());
    }

private:
    std::string part_number_;
    std::string lot_id_;
    MslLevel msl_;
    PkgThickness thickness_;
    State state_;
    
    std::chrono::hours floor_life_remaining_{0h};
    std::chrono::hours current_session_exposure_{0h};
    std::chrono::hours recovery_credit_{0h};
    std::chrono::hours cumulative_bake_125c_{0h};
    std::chrono::hours current_bake_remaining_{0h};
};

} // namespace tracker

int main() {
    using namespace std::chrono_literals;
    std::cout << "=== ДЕМОНСТРАЦІЯ РОБОТИ MSL FLOOR LIFE TRACKER (C++20) ===\n\n";
    tracker::ComponentReel reel("STM32H743IIT6", "LOT-2026-A89",
                                tracker::MslLevel::Msl3,
                                tracker::PkgThickness::Le1_4mm);
    auto unpack_res = reel.unpack(true);
    if (!unpack_res) {
        std::cerr << "Помилка розпакування: " << unpack_res.error() << '\n';
        return 1;
    }
    reel.print_status();
    
    std::cout << "\n>>> 8 годин роботи в цеху при 30 °C / 75% RH...\n";
    for (int i = 0; i < 8; ++i) {
        reel.tick(1h, 30.0, 75.0);
    }
    reel.print_status();
    
    std::cout << "\n>>> Переміщення в суху шафу RH < 5% на відновлення...\n";
    auto store_res = reel.store_in_dry_cabinet(3.0);
    if (!store_res) {
        std::cerr << "Помилка сховища: " << store_res.error() << '\n';
        return 1;
    }
    for (int i = 0; i < 40; ++i) {
        reel.tick(1h, 22.0, 3.0);
    }
    reel.print_status();
    return 0;
}
```
:::

---

### Інтеграція зі складськими системами MES, WMS та лінійними контролерами

Для практичного розгортання в умовах реального радіоелектронного виробництва трекер інтегрується з інфраструктурою підприємства на трьох функціональних рівнях:

1. **Ідентифікація та сканування маркування (DataMatrix 2D Barcode):**
   При надходженні котушок на склад сканер зчитує 2D-код формату DataMatrix відповідно до стандартів ANSI/EIA-556 та ISO/IEC 16022. Код містить префікси ідентифікаторів даних (*Data Identifiers*): `1P` (Part Number), `1T` (Lot ID), `Q` (кількість), `9D` (дата запаювання) та `14D` (рівень MSL). Серверна база даних автоматично створює запис котушки з відповідними параметрами товщини корпусу та допустимого часу експозиції.

2. **Шинна передача даних кліматичного моніторингу (Modbus RTU / MQTT):**
   Датчики вологості та температури в цеху опитуються мікроконтролерним шлюзом кожні 30–60 секунд. Пакет даних передається на сервер трекера у форматі JSON:
   ```json
   {
     "sensor_id": "SMT_LINE_2_ZONE_A",
     "timestamp": 1724875200,
     "temperature_c": 28.4,
     "relative_humidity_percent": 68.5,
     "calculated_derating_factor": 1.082
   }
   ```

3. **Апаратне блокування живильників Pick-and-Place (Interlocking):**
   Сервер трекера через відкритий API протоколу IPC-HERMES-9852 або OMRON/Panasonic/ASM Interface безперервно транслює стан активних котушок у керівний комп'ютер SMT-автомата. Якщо залишок Floor Life для будь-якої встановленої котушки стає меншим ніж 30 хвилин, на моніторі оператора спалахує жовте попередження. При вичерпанні ліміту (L = 0) автомат миттєво ставиться на паузу, каретка блокує захоплення компонентів із відповідного слота, а світлова колона перемикається в червоний миготливий режим зі звуковим сповіщенням інженера-технолога.

## Специфіка двостороннього монтажу та повторного оплавлення

Під час двостороннього монтажу друкованих плат компоненти першої сторони (Top Side) проходять крізь конвекційну піч двічі: спершу під час власного монтажу, а згодом — під час оплавлення протилежної сторони (Bottom Side). Стандарт IPC/JEDEC J-STD-033 встановлює суворі інженерні правила для обліку терміну перебування таких плат у цеху:

1. **Сумарна експозиція до другого проходу:** Час від моменту відкриття захисного пакета MBB з компонентами для верхньої сторони до завершення пайки **другої** сторони плати не повинен перевищувати паспортний ліміт Floor Life для найчутливішого елемента (найчастіше це BGA-процесори або пам'ять LPDDR рівня MSL 3 або MSL 4).
2. **Проміжне зберігання в сухому боксі:** Якщо технологічна пауза між монтажем першої та другої сторін перевищує кілька годин, змонтовані напівфабрикати плат обов'язково переміщуються у сухожарову шафу або сухий бокс із відносною вологістю `RH ≤ 5%`. Перебування в сухому боксі зупиняє лічильник Floor Life, запобігаючи насиченню вологою корпусів, які зазнають повторного теплового шоку при температурі піку пайки 245–260 °C.
3. **Обмеження кількості теплових циклів:** Стандарт J-STD-020 гарантує збереження надійності мікросхем не більше ніж для трьох послідовних циклів оплавлення (Reflow Passes). Кожен додатковий прохід через піч (наприклад, для селективної пайки THT-компонентів або ремонту) фіксується у паспорті виробу.

Така багаторівнева автоматизація виключає ризик монтажу зволожених компонентів, гарантує дотримання вимог стандарту IPC/JEDEC J-STD-033 та забезпечує 100% захист готових виробів від прихованого браку пайки.
