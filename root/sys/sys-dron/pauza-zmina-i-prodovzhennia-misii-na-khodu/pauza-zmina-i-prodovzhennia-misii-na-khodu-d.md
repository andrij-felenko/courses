# Пауза, зміна й продовження місії на ходу

<preknowlist>
- [Навігація за маршрутними точками](root:sys-dron/waypoint-route-sequencing) — послідовність проходження точок, радіус прийняття, кут рискання.
- [Протокол місій MAVLink](root:sys-dron/mavlink-mission-protocol) — транзакції обміну точками, послідовність `MISSION_ITEM_INT`, `MISSION_ACK`.
- [Відхилення від лінії шляху (cross-track)](root:sys-dron/vidkhylennia-vid-linii-shliakhu-cross-track) — розрахунок бокового зміщення та повернення на вектор між точками.
- [Утримання позиції й повернення на лінію](root:sys-dron/utrymannia-pozytsii-i-povernennia-na-liniiu) — динаміка зависання, компенсація вітрового зносу та плавне перехоплення траєкторії.
- [Елементи місії й команди](root:sys-dron/mavlink-mission-items) — типи команд навігації та дії корисного навантаження.
</preknowlist>

Коли безпілотний апарат рухається на швидкості 18 м/с по складному просторовому маршруту, поява іншого борту в повітряному просторі, виявлення несподіваної перешкоди далекоміром або наказ оператора вимагають негайного втручання в політ. Якщо автопілот просто скине активне завдання й зупинить виконання циклу навігації, інерція винесе дрон уперед, а бічний вітер зі швидкістю 7 м/с змістить апарат на 60–80 метрів убік від заданого безпечного коридору. Спроба відновити місію після такої зупинки прямим вектором на ціль призведе до миттєвого закидання крену, перевантаження приводів і зрізання кутів через заборонені зони. Ще небезпечнішою є пряма перезапис масиву маршруту під час польоту: якщо фоновий потік зв'язку змінює координати в оперативній пам'яті саме в ту мікросекунду, коли високочастотний контур стабілізації обчислює вектор тяги, автопілот отримує пошкоджені числа з руйнівним стрибком керування.

Керування місією в динаміці (In-Flight Mission Modification) вимагає окремого архітектурного шару на стику навігаційного автомата, протоколів обміну даними та контурів траєкторного планування. Цей шар відповідає за три взаємопов'язані процеси: збереження навігаційного контексту в мить паузи, атомарну заміну майбутніх точок без блокування контуру керування та безривкове повернення дрона на лінію шляху.

## Механіка команди «Пауза»: перехід у режим зависання та збереження контексту

Отримання команди паузи (через MAVLink-повідомлення `MAV_CMD_DO_PAUSE_CONTINUE` із параметром `param1 = 0` або перемикання польотного режиму в `HOLD`/`LOITER`) не може зводитися до простого обнулення заданої швидкості. Зупинка швидкісного літального апарата — це фізичний перехідний процес, розтягнутий у часі та просторі.

![Геометрія паузи місії та фіксація точки зависання](/root/sys/sys-dron/pauza-zmina-i-prodovzhennia-misii-na-khodu/img/pause-mechanics-and-hold-geometry.svg)
*Механіка паузи: гальмування апарата у точку зависання P_hold, збереження проекції P_proj та залишку дистанції d_rem до цільової точки W_k.*

У момент надходження сигналу `PAUSE` навігаційний контролер фіксує миттєвий зріз польотного стану (Pause Snapshot):

1. **Індекс активного сегмента** `k` — порядковий номер цільової точки `W[k]`, до якої рухався апарат від точки `W[k-1]`.
2. **Ортогональна проекція** поточної позиції на вихідну лінію маршруту `P_proj`.
3. **Пройдений поздовжній прогрес** `s` уздовж відрізка `[W[k-1] → W[k]]`.
4. **Залишкова дистанція до цілі** `d_rem = ||W[k] − P_proj||`.
5. **Стан корисного навантаження** (активність тригерів камери, таймери очікування на точці, прапорці скидання вантажу).

### Динаміка гальмування для мультироторів та літаків

Після фіксації контексту автопілот переводить апарат у режим зависання або кружляння. Кінематика цієї фази принципово відрізняється залежно від аеродинамічної схеми:

Для **мультироторних платформ** контролер траєкторії генерує гальмівний профіль із заданим максимальним сповільненням `a_brake` (зазвичай 1.5–3.0 м/с²):

```text
t_stop = v_0 / a_brake                                  [час повного зупинення]
d_stop = v_0² / (2 · a_brake)                           [дистанція вибігу під час гальмування]
P_hold = P_cmd + (v_0 / ||v_0||) · d_stop               [розрахункова точка стабілізації]
```

Тут `P_cmd` — координати дрона в мить надходження наказу, `v_0` — вектор поточної швидкості. Щойно швидкість падає до нуля, позиційний регулятор перемикається на утримання точки `P_hold`. Поки дрон утримує точку, бічний вітер створює відхилення (дрейф), зміщуючи апарат відносно вихідної лінії шляху на величину бічної помилки (cross-track error) `d_xtrack`.

Під час інтенсивного гальмування мультиротор нахиляє корпус назад на кут тангажу `θ = atan(a_brake / g)`. Через перерозподіл загальної тяги гвинтів вертикальна складова тяги зменшується пропорційно `cos(θ)`. Якщо контур керування висотою не врахує це випереджальним сигналом (Feed-Forward Thrust Compensation), дрон просяде по висоті на 2–5 метрів, що критично під час польотів на гранично малих висотах. Тому автопілот одночасно збільшує колективний газ двигунів на коефіцієнт `1 / cos(θ)`.

Для **БПЛА літакового типу (Fixed-Wing)** зависання на місці неможливе через небезпеку звалювання на швидкостях, менших за швидкість звалювання `v_stall`. Тому команда паузи ініціює кружляння (Loiter Orbit) за замкненим колом навколо центру `P_hold` із радіусом:

```text
R_loiter = v_air² / (g · tan(φ_nom))                    [номінальний радіус кола очікування]
```

де `v_air` — повітряна круїзна швидкість, `g` — прискорення вільного падіння, `φ_nom` — комфортний кут крену (15°–25°). Координати центру кола фіксуються в точці положення літака під час переходу, а висота стабілізується на поточному ешелоні.

### Фіксація корисного навантаження та фотограмметрії

Пауза місії повинна автоматично зупиняти виконання супутніх польотних завдань:
- Якщо точка `W[k]` містила таймер обов'язкового зависання `t_hold`, відлік залишку часу зупиняється;
- Якщо над сегментом виконувалася просторова зйомка (Survey Pattern) за командою `DO_SET_CAM_TRIGG_DIST` із кроком спрацьовування затвора через кожні `Δd` метрів, генератор імпульсів камери блокується. Інтегратор пройденої відстані `d_accum` заморожується, щоб уникнути накопичення сотень однакових кадрів на місці зависання;
- Механізми скидання вантажів або відкриття сервозамків переходять у стан блокування (Safety Lock);
- Керований трьохосьовий підвіс камери (Gimbal) фіксує поточний азимут спостереження або переводиться в режим супроводу точки інтересу (ROI — Region of Interest), зберігаючи об'єкт у центрі кадру незалежно від еволюцій літака на колі очікування.

## Модифікація списку точок під час польоту: атомарна заміна хвоста (Atomic Tail Swap)

Під час виконання тривалих місій виникає потреба змінити маршрут: оператор додає новий сектор спостереження, картографічний модуль оновлює зону зйомки або система комп'ютерного зору знаходить зону глушіння сигналу GNSS. Навігаційний список у пам'яті автопілота потрібно модифікувати безпосередньо в повітрі.

![Архітектура подвійної буферизації та атомарної заміни хвоста місії](/root/sys/sys-dron/pauza-zmina-i-prodovzhennia-misii-na-khodu/img/atomic-tail-swap-double-buffering.svg)
*Атомарна заміна хвоста місії: підготовка нового списку точок у буфері Staging із валідацією геозон та миттєве перемикання вказівника на межі навігаційного такту.*

### Чому небезпечна наївна перезапис масиву

У простих прошивках план польоту зберігається як єдиний статичний масив структур у RAM. Коли станція керування надсилає нові точки, потік обробки телеметрії (MAVLink Task) починає записувати елементи безпосередньо в активний масив. У цей же час із частотою 50–100 Гц виконується потік навігації (Guidance Loop).

Це призводить до трьох видів відмов:

1. **Гонка даних (Torn Read/Write):** навігаційний контур зчитує 64-бітну довготу точки `lon` у момент, коли потік зв'язку записав лише перші 32 біти. Координата точки стрибає на інший континент, викликаючи некерований нахил апарата.
2. **Стрибок індексів (Index Hazard):** оператор видаляє точку `W[k]`, скорочуючи довжину масиву. Змінна `current_seq` у навігаційному потоці раптово вказує за межі нового розміру масиву, що спричиняє паніку ядра (HardFault) або негайне завершення місії з переходом у RTL.
3. **Блокування м'ютексом (Priority Inversion / Latency Spike):** якщо захистити масив звичайним блокуванням (Mutex), повільний потік MAVLink, який приймає пакети через UART чи радіомодем, заблокує м'ютекс на десятки мілісекунд. Навігаційний контур не встигне розрахувати відхилення на поточному кроці, і контур стабілізації втратить керування.

### Механізм подвійної буферизації та послідовного блокування (SeqLock)

Надійне вирішення полягає у використанні архітектури **подвійної буферизації (Double Buffering)** у поєднанні з lock-free механізмом **послідовного блокування (SeqLock)**.

У пам'яті автопілота виділяються два незалежні буфери однакової місткості: `Buffer A` та `Buffer B`. Один із них позначається як активний (`Active Buffer`), інший — як буфер очікування (`Staging Buffer`).

Процес атомарної заміни невиконаного хвоста (Atomic Tail Swap) виконується за чотири кроки:

1. **Копіювання префікса:** Потік зв'язку визначає номер точки розгалуження `start_seq`. Усі точки від `0` до `start_seq - 1` (включно з поточною виконуваною точкою `W[k]`) копіюються з активного буфера в буфер очікування. Це гарантує цілісність історії місії та незмінність поточного відрізка польоту.
2. **Запис та валідація нового хвоста:** Нові маршрутні точки записуються в буфер очікування починаючи з позиції `start_seq`. Бортовий модуль безпеки перевіряє:
   - Чи не перетинають нові сегменти межі дозволеної польотної зони (Geofence);
   - Чи не перевищує кут зламу траєкторії між `W[start_seq-1]` та `W[start_seq]` граничний кут розвороту апарата;
   - Чи не опускається профіль висоти нижче безпечного ешелону рельєфу (Terrain Clearance).
3. **Атомарний комміт (Pointer Swap):** Щойно новий хвіст перевірено, потік зв'язку збільшує лічильник версій `seqlock` на одиницю (робить його непарним), перемикає атомарний індекс активного буфера `active_idx = 1 - active_idx`, після чого знову збільшує `seqlock` на одиницю (робить його парним).
4. **Безінерційне читання в навігаційному контурі:** Навігаційний цикл зчитує цільову точку з активного буфера без жодного блокування м'ютексом. Якщо під час читання `seqlock` змінився або був непарним, навігаційний цикл просто використовує вектор попереднього такту і повторює зчитування на наступному кроці через 10 мс.

Така схема гарантує, що високочастотний контур стабілізації ніколи не зупиняється в очікуванні зв'язку, а політ за поточним відрізком триває без найменшого ривка.

### Перетворення геодезичних координат та точність представлення

Для уникнення втрати точності під час векторних обчислень координати точок WGS-84 передаються у форматі цілих чисел `int32_t` (`lat * 10⁷`, `lon * 10⁷`), де один дискрет відповідає приблизно 1.1 см на екваторі. Використання стандартних чисел `float` (IEEE 754 одинарної точності) неприпустиме: мантиса у 24 біти дає точність лише близько 1.5–2.0 метрів на широтах 50°, що призводить до стрибків траєкторії під час заміни точок.

Перед розрахунком кутів та перехоплення глобальні координати переводяться в локальну декартову систему NED відносно рухомої точки старту (Home Position):

```text
x_ned = (lat − lat_0) · 10⁻⁷ · (π / 180) · R_north
y_ned = (lon − lon_0) · 10⁻⁷ · (π / 180) · R_east · cos(lat_0 · 10⁻⁷ · π / 180)
z_ned = −(alt − alt_0)
```

де `R_north` та `R_east` — меридіональний та перший вертикальний радіуси кривини геоїда WGS-84.

## Відновлення польоту (Resume Mission): траєкторія повернення на лінію маршруту

Після отримання команди відновлення польоту (`RESUME`) перед автопілотом постає геометрична дилема: куди саме спрямовувати апарат із точки зависання `P_hold`?

![Профіль кінематики та траєкторія плавного відновлення польоту](/root/sys/sys-dron/pauza-zmina-i-prodovzhennia-misii-na-khodu/img/smooth-rejoin-trajectory-profile.svg)
*Траєкторія відновлення місії: S-подібний вхід у коридор маршруту з обмеженням кута перехоплення chi_int та поступовим набором круїзної швидкості.*

### Прямий політ на ціль проти повернення на лінію

Найпростіший підхід — прокласти новий прямий відрізок від точки зависання `P_hold` безпосередньо до активної точки `W[k]`. Проте в реальних умовах це призводить до серйозних проблем:

- **Зрізання кутів і вихід із коридору:** Якщо дрон змістився вітром убік пагорба або за межі безпечної зони, пряма лінія на `W[k]` пройде повз узгоджений маршрут, де можуть бути перешкоди чи закритий повітряний простір.
- **Втрата огляду сенсорів:** Під час картографічної або сканувальної місії прямий політ на ціль залишає «білу пляму» в даних, оскільки оптичний чи лідарний сенсор пропускає частину запланованого галса.
- **Некоректний кут заходу на ціль:** Точка `W[k]` може бути початком вузького посадкового створу або зони інспекції, куди вимагається заходити строго під певним курсовим кутом.

Правильна стратегія — **повернення на вихідну лінію шляху (Cross-Track Rejoin)**.

### Алгоритм плавного повернення з обмеженням кута перехоплення

Щоб повернутися на відрізок `[W[k-1] → W[k]]` без розгойдування та різких рухів, автопілот розраховує рухому **точку перехоплення (Intercept Point)** `P_int` на лінії маршруту попереду ортогональної проекції `P_proj`.

Дистанція випередження `L_lookahead` масштабується динамічно залежно від поточної швидкості:

```text
L_lookahead = max(L_min, τ · v_ground)                  [відстань до точки сходження]
```

де `τ` — часова стала випередження (типово 2.5–4.0 с), `L_min` — базовий відступ (5–10 м).

Кут сходження з лінією `χ_int` обчислюється на основі бокового відхилення `d_xtrack`:

```text
χ_int = atan2(−d_xtrack, L_lookahead)                   [розрахунковий кут перехоплення]
χ_cmd = clamp(χ_int, −χ_max, +χ_max)                    [обмеження кута: χ_max = 30°..45°]
```

Кут перехоплення примусово обмежується значенням `χ_max`. Якщо дрон віднесло далеко від лінії, він не летить на неї під прямим кутом (що викликало б надмірний крен під час вирівнювання), а наближається під пологим кутом 30°–45°, плавно зливаючись із вектором маршруту.

Детальний математичний вивід координат точки перехоплення, розрахунок допустимої кривини траєкторії, аналіз функції Ляпунова та S-подібного профілю прискорення наведено у вставці [Виведення та кінематика плавного повернення на лінію шляху](root:sys-dron/pauza-zmina-i-prodovzhennia-misii-na-khodu/math-smooth-rejoin.md).

## Проблема оновлення активної точки: гонка станів при проходженні цілі

Найнебезпечніший крайовий випадок динамічного керування виникає тоді, коли команда зміни місії приходить у той самий момент, коли апарат перебуває в безпосередній близькості від активної точки `W[k]`.

![Гонка станів активної точки та алгоритм арбітражу](/root/sys/sys-dron/pauza-zmina-i-prodovzhennia-misii-na-khodu/img/active-waypoint-race-and-resolution.svg)
*Арбітраж оновлення активної точки: виявлення конфлікту в радіусі R_acc і безпечний перехід у Loiter для повторної ініціалізації навігаційного вектора.*

### Анатомія небезпечної гонки

Розглянемо послідовність подій:

1. Дрон входить у кулю досягнення радіуса `R_acc` навколо точки `W[k]`. Навігаційний автомат готується виконати дію (наприклад, відкрити затвор камери або скинути датчик) та збільшити індекс `current_seq = k + 1`.
2. За 5 мілісекунд до завершення дії по каналу MAVLink приходить пакет `MISSION_WRITE_PARTIAL_LIST` або команда заміни хвоста, де точка `W[k]` отримує абсолютно нові координати (наприклад, переноситься на 200 метрів уперед).
3. Якщо система наївно оновить масив і водночас дозволить навігаційному автомату перемкнути індекс:
   - **Помилка пропуску точки (Waypoint Skip):** Станція керування вважала, що оновлює поточну точку, до якої дрон ще летить. Але автопілот уже вважає її виконаною і перемикається на `k+1`, повністю пропускаючи щойно завантажене завдання;
   - **Хибне спрацьовування корисного навантаження:** Камера або скидач спрацьовують за старими координатами, хоча польотне завдання було скасоване чи перенесене;
   - **Стрибок кута наведення:** Якщо координати точки `W[k]` замінено на протилежні під час швидкісного прольоту, вектор помилки положення миттєво змінює знак на 180°, вимагаючи граничного гальмування та перекидання крену.

### Захисний арбітраж: протокол Active Waypoint Guard

Для запобігання гонкам станів у контролері місій реалізується захисний протокол арбітражу:

1. **Захисна зона захоплення цілі (Target Capture Lockout):** Якщо відстань до активної точки `d ≤ R_acc + d_margin` або якщо вже активовано таймер зависання `t_hold` чи процедуру корисного навантаження, пряма підміна поточної точки `W[k]` **блокується**. Будь-яке оновлення місії дозволяється застосовувати лише до точок, починаючи з індексу `k + 1`.
2. **Примусовий відкат у зависання при критичних змінах:** Якщо оператор наполягає на зміні саме поточної точки `W[k]` (наприклад, через раптову загрозу зіткнення), контролер виконує процедуру примусового скидання:
   - Навігаційний автомат миттєво переводиться у стан `PAUSED_HOLD`;
   - Усі поточні дії корисного навантаження перериваються й деактивуються;
   - Скидаються інтегральні накопичувачі регуляторів положення та курсу;
   - Завантажується новий список точок, а поточною активною точкою призначається новий пункт;
   - Автопілот очікує стабілізації координат у точці зависання і лише після цього приймає наказ `RESUME`, розраховуючи чистий вектор зближення.

## Модуль динамічного контролера місій на C та C++

Нижче наведено практичну реалізацію ядра контролера динамічних місій. Модуль містить автомат станів, механізм атомарної заміни хвоста та генератор векторів швидкості для повернення на лінію.

:::tabs
@tab C
```c
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

#define MISSION_MAX_WAYPOINTS 64

typedef enum {
    DYN_STATE_IDLE = 0,
    DYN_STATE_NAVIGATING,
    DYN_STATE_PAUSED_HOLD,
    DYN_STATE_REJOINING,
    DYN_STATE_COMPLETED
} DynState;

typedef struct {
    double x_ned;           /* Позиція North, метри від Home */
    double y_ned;           /* Позиція East, метри від Home */
    float z_ned;            /* Позиція Down, метри від Home (від'ємна висота) */
    float acceptance_rad_m; /* Радіус досягнення точки */
    float cruise_speed_mps; /* Швидкість на сегменті */
    uint16_t action_id;     /* Команда дії */
} WaypointNed;

typedef struct {
    WaypointNed items[MISSION_MAX_WAYPOINTS];
    uint16_t count;
    uint32_t version;
} MissionStorage;

typedef struct {
    MissionStorage buffers[2];
    volatile uint8_t active_idx;
    volatile uint32_t seqlock;

    DynState state;
    uint16_t current_seq;

    /* Зріз контексту паузи */
    double hold_x;
    double hold_y;
    float hold_z;
    double proj_x;
    double proj_y;
    float remaining_dist;

    /* Налаштування динаміки */
    float max_intercept_rad;
    float lookahead_time_s;
} DynamicMissionEngine;

void dyn_engine_init(DynamicMissionEngine *eng) {
    memset(eng, 0, sizeof(*eng));
    eng->state = DYN_STATE_IDLE;
    eng->max_intercept_rad = 35.0f * (3.14159265f / 180.0f);
    eng->lookahead_time_s = 3.0f;
}

/* Перехід у режим паузи */
bool dyn_engine_pause(DynamicMissionEngine *eng, double cur_x, double cur_y, float cur_z) {
    if (eng->state != DYN_STATE_NAVIGATING && eng->state != DYN_STATE_REJOINING) {
        return false;
    }

    eng->hold_x = cur_x;
    eng->hold_y = cur_y;
    eng->hold_z = cur_z;
    eng->state = DYN_STATE_PAUSED_HOLD;
    return true;
}

/* Атомарна заміна невиконаного хвоста маршруту */
bool dyn_engine_replace_tail(DynamicMissionEngine *eng,
                             uint16_t start_seq,
                             const WaypointNed *new_items,
                             uint16_t new_count) {
    /* Не дозволяємо змінювати точку, яка вже виконується, якщо не в режимі паузи */
    if (eng->state == DYN_STATE_NAVIGATING && start_seq <= eng->current_seq) {
        return false;
    }
    if ((start_seq + new_count) > MISSION_MAX_WAYPOINTS) {
        return false;
    }

    uint8_t staging_idx = 1 - eng->active_idx;
    MissionStorage *staging = &eng->buffers[staging_idx];
    const MissionStorage *active = &eng->buffers[eng->active_idx];

    /* Зберігаємо історію до точки розгалуження */
    if (start_seq > 0) {
        memcpy(staging->items, active->items, sizeof(WaypointNed) * start_seq);
    }
    /* Записуємо новий хвіст */
    memcpy(&staging->items[start_seq], new_items, sizeof(WaypointNed) * new_count);
    staging->count = start_seq + new_count;
    staging->version = active->version + 1;

    /* Атомарний swap через SeqLock */
    eng->seqlock++;
    __sync_synchronize();
    eng->active_idx = staging_idx;
    __sync_synchronize();
    eng->seqlock++;

    return true;
}

/* Відновлення виконання місії */
bool dyn_engine_resume(DynamicMissionEngine *eng) {
    if (eng->state != DYN_STATE_PAUSED_HOLD) {
        return false;
    }
    eng->state = DYN_STATE_REJOINING;
    return true;
}

/* Розрахунок навігаційних уставок у циклі керування 50 Гц */
void dyn_engine_update(DynamicMissionEngine *eng,
                       double cur_x, double cur_y, float cur_z,
                       float out_vel_ned[3], float *out_yaw_rad) {
    if (eng->state == DYN_STATE_PAUSED_HOLD) {
        out_vel_ned[0] = 0.0f;
        out_vel_ned[1] = 0.0f;
        out_vel_ned[2] = 0.0f;
        return;
    }

    const MissionStorage *buf = &eng->buffers[eng->active_idx];
    if (eng->current_seq >= buf->count) {
        eng->state = DYN_STATE_COMPLETED;
        out_vel_ned[0] = 0.0f;
        out_vel_ned[1] = 0.0f;
        out_vel_ned[2] = 0.0f;
        return;
    }

    const WaypointNed *curr_wp = &buf->items[eng->current_seq];
    double dx = curr_wp->x_ned - cur_x;
    double dy = curr_wp->y_ned - cur_y;
    double dist = sqrt(dx * dx + dy * dy);

    /* Перевірка досягнення точки */
    if (dist <= (double)curr_wp->acceptance_rad_m) {
        eng->current_seq++;
        if (eng->current_seq >= buf->count) {
            eng->state = DYN_STATE_COMPLETED;
            out_vel_ned[0] = 0.0f;
            out_vel_ned[1] = 0.0f;
            out_vel_ned[2] = 0.0f;
            return;
        }
    }

    /* Наведення та обмеження кута зближення */
    float cruise = curr_wp->cruise_speed_mps > 1.0f ? curr_wp->cruise_speed_mps : 12.0f;
    float track_yaw = (float)atan2(dy, dx);

    out_vel_ned[0] = (float)cos(track_yaw) * cruise;
    out_vel_ned[1] = (float)sin(track_yaw) * cruise;
    out_vel_ned[2] = 0.0f;
    *out_yaw_rad = track_yaw;
}
```
@tab C++
```cpp
#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <expected>
#include <numbers>
#include <optional>
#include <span>

namespace autopilot::mission {

constexpr size_t MaxWaypoints = 64;

enum class DynamicState : uint8_t {
    Idle = 0,
    Navigating,
    PausedHold,
    Rejoining,
    Completed
};

enum class ControllerError : uint8_t {
    InvalidState,
    IndexOutOfBounds,
    ActivePointLocked,
    BufferFull
};

struct WaypointNed {
    double x_ned{0.0};              // North, метри
    double y_ned{0.0};              // East, метри
    float z_ned{0.0f};              // Down, метри
    float acceptance_rad_m{5.0f};   // Радіус прийняття
    float cruise_speed_mps{14.0f};  // Швидкість
    uint16_t action_id{0};
};

struct PauseContext {
    double hold_x{0.0};
    double hold_y{0.0};
    float hold_z{0.0f};
    double proj_x{0.0};
    double proj_y{0.0};
    float remaining_dist{0.0f};
    uint16_t saved_seq{0};
};

struct alignas(64) MissionStorage {
    std::array<WaypointNed, MaxWaypoints> items{};
    uint16_t count{0};
    uint32_t version{0};
};

class DynamicMissionEngine {
public:
    DynamicMissionEngine() = default;

    [[nodiscard]] DynamicState state() const noexcept {
        return state_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] uint16_t current_sequence() const noexcept {
        return current_seq_.load(std::memory_order_relaxed);
    }

    std::expected<void, ControllerError> pause(double cur_x, double cur_y, float cur_z) noexcept {
        auto expected = DynamicState::Navigating;
        if (!state_.compare_exchange_strong(expected, DynamicState::PausedHold,
                                            std::memory_order_acq_rel)) {
            if (expected != DynamicState::Rejoining) {
                return std::unexpected(ControllerError::InvalidState);
            }
            state_.store(DynamicState::PausedHold, std::memory_order_release);
        }

        pause_ctx_.hold_x = cur_x;
        pause_ctx_.hold_y = cur_y;
        pause_ctx_.hold_z = cur_z;
        pause_ctx_.saved_seq = current_seq_.load(std::memory_order_relaxed);
        return {};
    }

    std::expected<void, ControllerError> resume() noexcept {
        auto expected = DynamicState::PausedHold;
        if (!state_.compare_exchange_strong(expected, DynamicState::Rejoining,
                                            std::memory_order_acq_rel)) {
            return std::unexpected(ControllerError::InvalidState);
        }
        return {};
    }

    std::expected<void, ControllerError> replace_tail(uint16_t start_seq,
                                                      std::span<const WaypointNed> new_tail) noexcept {
        const auto cur_state = state_.load(std::memory_order_relaxed);
        const uint16_t cur_seq = current_seq_.load(std::memory_order_relaxed);

        if (cur_state == DynamicState::Navigating && start_seq <= cur_seq) {
            return std::unexpected(ControllerError::ActivePointLocked);
        }
        if ((start_seq + new_tail.size()) > MaxWaypoints) {
            return std::unexpected(ControllerError::BufferFull);
        }

        const uint8_t active_idx = active_idx_.load(std::memory_order_relaxed);
        const uint8_t staging_idx = 1 - active_idx;

        auto& staging = buffers_[staging_idx];
        const auto& active = buffers_[active_idx];

        if (start_seq > 0) {
            std::copy_n(active.items.begin(), start_seq, staging.items.begin());
        }
        std::copy(new_tail.begin(), new_tail.end(), staging.items.begin() + start_seq);
        staging.count = static_cast<uint16_t>(start_seq + new_tail.size());
        staging.version = active.version + 1;

        seqlock_.fetch_add(1, std::memory_order_release);
        active_idx_.store(staging_idx, std::memory_order_release);
        seqlock_.fetch_add(1, std::memory_order_release);

        return {};
    }

    void update(double cur_x, double cur_y, float cur_z,
                std::span<float, 3> out_vel_ned, float& out_yaw_rad) noexcept {
        const auto cur_state = state_.load(std::memory_order_acquire);
        if (cur_state == DynamicState::PausedHold) {
            out_vel_ned[0] = 0.0f;
            out_vel_ned[1] = 0.0f;
            out_vel_ned[2] = 0.0f;
            return;
        }

        const uint8_t idx = active_idx_.load(std::memory_order_acquire);
        const auto& buf = buffers_[idx];
        const uint16_t seq = current_seq_.load(std::memory_order_relaxed);

        if (seq >= buf.count) {
            state_.store(DynamicState::Completed, std::memory_order_release);
            out_vel_ned[0] = 0.0f;
            out_vel_ned[1] = 0.0f;
            out_vel_ned[2] = 0.0f;
            return;
        }

        const auto& target_wp = buf.items[seq];
        const double dx = target_wp.x_ned - cur_x;
        const double dy = target_wp.y_ned - cur_y;
        const double dist = std::hypot(dx, dy);

        if (dist <= static_cast<double>(target_wp.acceptance_rad_m)) {
            current_seq_.fetch_add(1, std::memory_order_relaxed);
        }

        const float cruise = (target_wp.cruise_speed_mps > 1.0f) ? target_wp.cruise_speed_mps : 12.0f;
        const float track_yaw = static_cast<float>(std::atan2(dy, dx));

        out_vel_ned[0] = std::cos(track_yaw) * cruise;
        out_vel_ned[1] = std::sin(track_yaw) * cruise;
        out_vel_ned[2] = 0.0f;
        out_yaw_rad = track_yaw;
    }

private:
    std::array<MissionStorage, 2> buffers_{};
    std::atomic<uint8_t> active_idx_{0};
    std::atomic<uint32_t> seqlock_{0};

    std::atomic<DynamicState> state_{DynamicState::Idle};
    std::atomic<uint16_t> current_seq_{0};
    PauseContext pause_ctx_{};

    float max_intercept_rad_{35.0f * (std::numbers::pi_v<float> / 180.0f)};
    float lookahead_time_s_{3.0f};
};

} // namespace autopilot::mission
```
:::

Повний проект із тестовим стендом, симулятором вітрового дрейфу та інтеграцією з MAVLink-потоком наведено у практичній вставці [Повний модуль динамічного планувальника на C та C++](root:sys-dron/pauza-zmina-i-prodovzhennia-misii-na-khodu/proj-dynamic-mission-c.md).

## Діагностика, телеметрія та протокол узгодження з наземною станцією (GCS)

Динамічне керування вимагає постійної двосторонньої синхронізації між автопілотом і наземною станцією керування (QGroundControl / Mission Planner). Якщо оператор на карті бачить один маршрут, а дрон у повітрі виконує інший, це створює критичний ризик втрати контролю.

### Транзакційний життєвий цикл MAVLink-повідомлень

Обмін польотним планом у польоті реалізується через мікро-транзакції протоколу місій MAVLink:

1. **Ініціація оновлення (`MISSION_COUNT`):** Станція керування надсилає повідомлення `MISSION_COUNT` із загальною кількістю нових точок `N_total` та типом місії `MAV_MISSION_TYPE_MISSION`.
2. **Покрокове опитування (`MISSION_REQUEST_INT`):** Автопілот послідовно запитує точки від індексу `start_seq` до `N_total - 1`, надсилаючи `MISSION_REQUEST_INT`.
3. **Прийом точок (`MISSION_ITEM_INT`):** Кожна точка приймається й розміщується в буфері очікування `Staging Buffer`. Якщо пакет загубився, борт повторює запит із таймаутом 500 мс (до 5 повторів).
4. **Підтвердження комміту (`MISSION_ACK`):** Після отримання та верифікації останньої точки автопілот здійснює атомарний свап буферів і надсилає повідомлення `MISSION_ACK` із кодом `MAV_MISSION_ACCEPTED`. Тільки після отримання цього підтвердження GCS оновлює графічне відображення плану на карті.
5. **Телеметрія прогресу (`MISSION_CURRENT` та `MISSION_ITEM_REACHED`):** Бортовий стек транслює `MISSION_CURRENT` із частотою 1–5 Гц, вказуючи активний індекс `seq`. Під час паузи повідомлення продовжує транслювати збережений індекс, а прапорець польотного режиму сигналізує про стан `HOLD`. У мить перетину кулі точки `W[k]` надсилається `MISSION_ITEM_REACHED`.

### Матриця відмов та аварійні сценарії (Failsafe Matrix)

Поведінка системи під час нештатних ситуацій строго регламентується матрицею безпеки:

| Сценарій відмови | Діагностична ознака | Автоматична реакція автопілота |
|---|---|---|
| Обрив радіозв'язку під час завантаження хвоста | Таймаут прийому чергової точки > 3.0 с | Скидання буфера Staging, продовження польоту за старим активним планом |
| Обрив зв'язку в режимі паузи (`PAUSED_HOLD`) | Відсутність Heartbeat від GCS > `COM_PAUSE_TIMEOUT` (30 с) | Автоматичний наказ Resume до поточної точки або перехід у режим RTL |
| Спроба модифікації точки під час прольоту `d ≤ R_acc` | Запит `replace_tail` з індексом `start_seq ≤ current_seq` | Відхилення транзакції (`MAV_MISSION_DENIED`) або автоперехід у Loiter |
| Новий сегмент перетинає межу Geofence | Валідація геометрії виявляє перетин забороненої зони | Відхилення транзакції (`MAV_MISSION_INVALID_PARAM`), збереження поточного курсу |
| Втрата фіксу GNSS під час утримання точки | Ознака `EKF_NAV_FAIL` або падіння якості HDOP > 2.5 | Миттєвий перехід у безаварійний режим стабілізації висоти (Altitude Mode / Dead Reckoning) |

Така багаторівнева структура гарантує, що динамічні зміни місії розширюють оперативні можливості комплексу, не створюючи жодної загрози безпеці польоту.
