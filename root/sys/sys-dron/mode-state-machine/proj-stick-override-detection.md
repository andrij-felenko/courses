# ⚙️ Детектування втручання пілота через стіки RC (Stick Override) та перехід у безпечний режим

Автономний політ безпілотного апарата за заздалегідь завантаженою місією (`AUTO`), процедура автоматичного повернення на точку старту (`RTL`) або політ за цільовими траєкторіями від зовнішнього супровідного комп'ютера (`OFFBOARD`/`GUIDED`) спираються на безперервну роботу навігаційних алгоритмів. Проте в реальних умовах польоту виникають критичні ситуації, які бортова автоматика не здатна вчасно розпізнати або безпечно оминути: раптова поява не позначеної на навігаційній карті високовольтної лінії передач, небезпечне зближення з іншим повітряним судном або птахом, раптове локальне погіршення погодних умов, потрапляння в турбулентний вихор або програмний збій бортових алгоритмів комп'ютерного зору.

У таких сценаріях безпека апарата цілком залежить від швидкості реакції пілота-оператора. Якщо єдиним способом повернути ручний контроль є фізичне перемикання тумблера польотного режиму на пульті радіокерування (RC), час реакції збільшується на критичні 0.5–1.5 секунди: пілоту необхідно зняти пальці з ручок керування, знайти потрібний перемикач на панелі передавача та перевести його у відповідне положення. В аварійній ситуації на високій польотній швидкості людина інстинктивно смикає стік керування у бік ухилення від перешкоди.

Алгоритм **перехоплення стіками** (*Stick Override*) призначений для миттєвого виявлення усвідомленого фізичного втручання пілота в контур польоту через ручки пульта, автоматичного призупинення виконання автономної програми та детермінованого безвузлового переведення апарата в керований ручний або напівавтономний режим.

---

## Проблематика детектування: чому сирого опитування стіків недостатньо

Спроба реалізувати перехоплення керування за допомогою наївного порівняння сирих значень радіоканалів із порогом (`if (rc_channel[ROLL] > 1600) trigger_override();`) у реальній польотній системі призводить до небезпечних аварійних ситуацій і постійних неправдивих спрацьовувань через фізичну природу радіотракту та механіки пультів:

```
[Сигнал RC з шумом і дрейфом] 
            │
            ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ 1. Шуми АЦП / датчиків Холла: ±2...8 мкс                    │
 │ 2. Механічний люфт і неточне центрування пружин: ±15...35 мкс│
 │ 3. Температурний дрейф резистивних доріжок: ±10...20 мкс    │
 │ 4. Пропуски та поодинокі спотворення фреймів SBUS/CRSF      │
 └─────────────────────────────────────────────────────────────┘
            │
            ▼  (Без фільтрації та мертвої зони)
 ┌─────────────────────────────────────────────────────────────┐
 │ Постійне хибне скидання автономної місії у польоті          │
 └─────────────────────────────────────────────────────────────┘
```

1. **Шум квантування та електромагнітні завади**: вихідний сигнал АЦП стіка пульта або послідовний пакет протоколів SBUS чи CRSF містить випадкові флуктуації тривалості імпульсу амплітудою ±2...8 мкс навіть за повної нерухомості рук оператора.
2. **Механічний гістерезис і неточність пружинного механізму**: при відпусканні ручки пружини повертають стік у нейтральне положення з похибкою до 1...3% від повного діапазону ходу. Замість ідеальних 1500 мкс реальний центр може зафіксуватися на позначці 1525 мкс або 1480 мкс залежно від того, з якого боку було відпущено ручку.
3. **Температурний і часовий дрейф тримерів**: зміна температури навколишнього середовища змінює опір контактних доріжок потенціометрів або чутливість сенсорів Холла, зміщуючи апаратну нейтраль пульта під час тривалого польоту.
4. **Випадкові короткочасні торкання**: оператор може випадково зачепити ручку пульта під час носіння апаратури на шийному ремені, коригування налаштувань відеошолома або внаслідок пориву вітру, що хитає руки пілота.

Надійний інженерний алгоритм Stick Override розв'язує ці проблеми через чотири послідовні каскади обробки:
- **Нормалізація та усунення асиметрії ходу**: зведення фізичних сигналів до стандартного безрозмірного діапазону [-1.0, +1.0].
- **Адаптивна мертва зона (Deadband)**: гарантоване придушення шуму нейтралі з нелінійним масштабуванням робочого залишку ходу без розриву функції керування.
- **Багатоосьовий аналіз відхилень**: розрахунок сумарного вектора деформації з можливістю селективного маскування каналів (наприклад, дозвіл огляду камерою за курсом Yaw без зриву місії).
- **Часовий дебаунсинг (Hold Delay)**: валідація наміру пілота через інтегрування сигналу в часі для відсікання одиночних імпульсних викидів.

---

## Нормалізація вхідних сигналів та безрозривна мертва зона

Більшість протоколів радіокерування (PWM, PPM, SBUS, CRSF, IBUS) оперують мікросекундами або числовими відліками каналів. Для подальших обчислень сире значення `PWM_in` у діапазоні `[PWM_min, PWM_max]` перетворюється на нормалізоване значення `u` у діапазоні `[-1.0, +1.0]` відносно центру тримування `PWM_center`:

```
u = (PWM_in - PWM_center) / (PWM_max - PWM_center),   якщо PWM_in >= PWM_center
u = (PWM_in - PWM_center) / (PWM_center - PWM_min),   якщо PWM_in <  PWM_center
```

Стандартний діапазон PWM становить 1000...2000 мкс із центром на 1500 мкс, проте внаслідок асиметрії кінцевих точок передавача верхнє і нижнє плече можуть мати різну фізичну довжину.

### Математична модель мертвої зони без стрибка

Просте обнулення сигналу всередині мертвої зони (Deadband) породжує небезпечний стрибок (розрив першого роду) на межі порогу:

```
[Ступінчаста мертва зона — НЕПРАВИЛЬНО]
u_out
  ^
  |        /
  |       /
  |      |  <-- Стрибок на величині d!
  +------+---------> u_in
 -d      d
```

Якщо пілот відхиляє ручку на величину `u_in = d + eps`, де `d` — радіус мертвої зони, вихідний сигнал миттєво стрибає від 0.0 до `d`, викликаючи ударне навантаження на контур кутових швидкостей і ривок сервоприводів або моторів.

Для забезпечення абсолютної плавності застосовується функція з масштабуванням робочого залишку ходу (Scaled Deadband):

```
u_out = 0.0,                                      якщо |u_in| <= d
u_out = sign(u_in) * (|u_in| - d) / (1.0 - d),    якщо |u_in| >  d
```

де `d` у діапазоні `[0.0, 0.5]` — нормований радіус мертвої зони (зазвичай 0.04...0.08, що відповідає ±20...40 мкс навколо нейтралі).

```
[Масштабована неперервна мертва зона — ПРАВИЛЬНО]
u_out
  ^
  |          /
  |         /
  |        /   (Плавний старт від 0.0 при виході з зони d)
  +-------+---------> u_in
 -d       d
```

Така неперервна передавальна характеристика гарантує, що при виході зі стану спокою керувальний вплив плавно зростає від нуля до максимального значення без ривків і стрибків прискорення.

### Вплив кривих експоненти (Expo Curves) на поріг детектування

У спортивних та інспекційних пультах пілоти часто налаштовують експоненційне пом'якшення відгуку ручок (*Expo*) навколо центру для точнішого позиціонування:

```
u_expo = (1.0 - expo) * u_linear + expo * (u_linear)^3
```

де `expo` — коефіцієнт нелінійності від 0.0 до 1.0. 

Якщо обчислення детектора оверрайду виконувати над експоненційно згладженим сигналом `u_expo`, чутливість детектора навколо центру суттєво падає: для подолання порогу 15% пілоту доведеться відхилити фізичний стік на 25–30% ходу.

**Архітектурне правило**: нормалізація для детектора Stick Override завжди виконується строго над лінійною шкалою ходу ручки, до застосування користувацьких кривих Expo чи Dual Rates. Експоненційні перетворення підключаються пізніше — виключно в контурі формування цільових кутових швидкостей ручного керування.

### Специфіка каналу газу (Throttle Channel)

Канал газу має принципову відмінність залежно від типу літального апарата та активного базового режиму:
1. **Мультикоптер у режимах зі стабілізацією висоти (`ALT_HOLD`, `POS_HOLD`)**: нейтраль газу розташована по центру (1500 мкс, 50% тяги). У межах мертвої зони навколо 50% автопілот утримує стабільну висоту. Відхилення вгору означає набір висоти, униз — контрольований спуск. Відповідно, детектор оверрайду відстежує відхилення від центрального значення 0.5.
2. **Літак з фіксованим крилом або прямий ручний газ (`MANUAL`, `STABILIZE`)**: нейтраль газу відсутня, робочий діапазон тяги становить від 0.0 до 1.0. Оверрайд за газом у таких умовах може активуватися лише при різкому збільшенні тяги понад крейсерський рівень або при скиданні нижче безпечної межі звалювання.

---

## Метрики виявлення відхилення стіків

Для прийняття рішення про втручання алгоритм формує узагальнену метрику деформації керування `D_stick`. Залежно від конфігурації автопілота застосовуються три взаємодоповнюючі стратегії:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Стратегії розрахунку відхилення                      │
├───────────────────────────────────┬────────────────────────────────────┤
│ 1. Поканальна нерівність (L_inf)  │ D = max(|u_r|, |u_p|, |u_y|, |u_t|)│
│ 2. Евклідова норма в площині (L_2)│ D_xy = sqrt(u_r^2 + u_p^2)         │
│ 3. Маскований селективний аналіз  │ D_masked = max(u_i * mask_i)       │
└───────────────────────────────────┴────────────────────────────────────┘
```

1. **Чебишовська норма (`L_inf`, максимальне абсолютне відхилення)**:

```
D_inf = max( |u_roll| / Th_roll, |u_pitch| / Th_pitch, |u_yaw| / Th_yaw, |u_thr - u_thr_center| / Th_thr )
```

де `Th_i` — індивідуальний поріг спрацьовування для відповідної осі (наприклад, 15% для Roll і Pitch, 25% для Yaw, 20% для Throttle). Якщо `D_inf >= 1.0`, умова перевищення порогу вважається виконаною.

2. **Евклідова норма в площині крену й тангажу (`L_2`)**:
   При русі стіка по діагоналі (наприклад, уперед-вправо) відхилення по окремих осях Roll і Pitch може складати 12% і 12%, що нижче за індивідуальний поріг 15%. Проте сумарне зміщення ручки від центру становить `sqrt(12^2 + 12^2) ≈ 16.97%`, що є очевидним маневром ухилення. Тому векторне відхилення площини горизонту розраховується як:

```
D_horiz = sqrt( u_roll^2 + u_pitch^2 )
```

3. **Бітова маска дозволених каналів (`channel_mask`)**:
   Параметр конфігурації дозволяє виключити певні осі з контуру детектування оверрайду:
   - `STICK_OVR_MASK_ROLL` (`0x01`)
   - `STICK_OVR_MASK_PITCH` (`0x02`)
   - `STICK_OVR_MASK_YAW` (`0x04`)
   - `STICK_OVR_MASK_THROTTLE` (`0x08`)

Це дає змогу оператору коригувати кут огляду носової камери апарата за курсом (Yaw), не зриваючи виконання автоматичної місії, у той час як будь-який рух по Roll або Pitch негайно повертає повний ручний контроль.

---

## Кінцевий автомат дебаунсингу та таймер утримання (Hold Delay FSM)

Миттєве перемикання режиму в той самий мілісекундний такт, коли стік перетнув поріг, є неприпустимим через ризик короткочасних імпульсних викидів. Алгоритм реалізує спеціалізований кінцевий автомат із часовим фільтром підтвердження (Debounce Timer) та фазою фіксації стану (Hold / Latch Delay).

```
   ┌────────────────────────────────────────────────────────┐
   │                       IDLE                             │
   │  Стіки в межах мертвої зони (D < Threshold)            │
   └──────────────────────────┬─────────────────────────────┘
                              │
                              │ [D >= Threshold]
                              │ Запуск таймера активації
                              ▼
   ┌────────────────────────────────────────────────────────┐
   │                    QUALIFYING                          │
   │  Очікування безперервного утримання: t >= T_activate   │
   └─────────────┬────────────────────────────▲─────────────┘
                 │                            │
                 │ [t >= T_activate]          │ [D < Threshold]
                 │ Генерувати перехід         │ (Хибний імпульс)
                 ▼                            │
   ┌──────────────────────────────────────────┴─────────────┐
   │                 OVERRIDE_ACTIVE                        │
   │  Ручний контроль активний, автономна місія зупинена    │
   └─────────────┬──────────────────────────────────────────┘
                 │
                 │ [D < Threshold]
                 │ Стіки відпущені в центр
                 ▼
   ┌────────────────────────────────────────────────────────┐
   │                   RELEASE_HOLD                         │
   │  Таймер блокування зворотного автопереходу (T_release) │
   └──────────────────────────┬─────────────────────────────┘
                              │
                              │ [t >= T_release]
                              ▼
                        (Повернення в IDLE)
```

### Стани автомата детектора:

1. **`STATE_IDLE` (Спокій)**:
   - Всі стіки перебувають у межах мертвих зон або нижче порогів спрацьовування.
   - Таймери скинуті в нуль.
   - Прапорець перехоплення `override_active = false`.

2. **`STATE_QUALIFYING` (Валідація наміру)**:
   - Метрика `D_stick` перевищила поріг спрацьовування.
   - Ініціалізується таймер підтвердження `activation_timer`.
   - Якщо стік повертається в нейтраль до закінчення часу `T_activate` (зазвичай 80...150 мс), автомат повертається в `IDLE`, кваліфікуючи подію як випадковий зачіп або шум.

3. **`STATE_OVERRIDE_ACTIVE` (Активне перехоплення)**:
   - Стік утримувався у відхиленому стані довше за час `T_activate`.
   - Формується системна подія `EVENT_STICK_OVERRIDE`.
   - Менеджер режимів отримує директиву на примусову зміну стану польотного автомата.
   - Стан утримується весь час, поки стіки залишаються відхиленими.

4. **`STATE_RELEASE_HOLD` (Затримка після відпускання)**:
   - Пілот відпустив стіки в нейтраль після виконання маневру перехоплення.
   - Щоб запобігти миттєвому неконтрольованому відновленню автоматичного польоту наземною станцією або супровідним комп'ютером, запускається таймер фіксації `T_release` (зазвичай 500...1500 мс).
   - Тільки після закінчення цього часу дозволяються повторні команди на перехід у повністю автономні режими.

---

## Безпечний каскадний вибір режиму та безвузлове перехоплення

Коли детектор підтверджує факт перехоплення, постає критичне питання: у який саме польотний режим слід перевести апарат?

Цільовий режим не може бути жорстко зашитим константним значенням, оскільки в момент аварії окремі навігаційні сенсори можуть бути пошкодженими. Алгоритм виконує динамічний каскадний вибір стану на основі поточної бітової маски сенсорного здоров'я фільтра EKF:

```
[Подія: Stick Override підтверджено]
                 │
                 ▼
     ┌───────────────────────┐
     │ 3D-позиція EKF дійсна? │───── ТАК ─────► Перехід у POS_HOLD (LOITER)
     └───────────┬───────────┘
                 │ НІ
                 ▼
     ┌───────────────────────┐
     │ Висота EKF-Z / Баро?  │───── ТАК ─────► Перехід у ALT_HOLD
     └───────────┬───────────┘
                 │ НІ
                 ▼
     ┌───────────────────────┐
     │ Орієнтація AHRS/IMU?  │───── ТАК ─────► Перехід у STABILIZE
     └───────────┬───────────┘
                 │ НІ
                 ▼
     Примусова аварійна посадка (EMERGENCY_LAND / TERMINATION)
```

### Процедура безвузлового підхоплення (Bumpless Takeover)

У момент переходу автопілот не повинен скидати поточні уставки швидкостей у нуль. Якщо пілот нахилив стік Roll на 40% вправо, контур стабілізації зобов'язаний миттєво підхопити це відхилення:

1. **Ініціалізація цільових кутів або швидкостей**:
   - У режимі `POS_HOLD` відхилення стіків негайно транслюється в цільову горизонтальну швидкість `V_target_xy`, вектор якої розраховується з першого ж такту.
   - У режимі `ALT_HOLD` вертикальна швидкість `V_target_z` одразу встановлюється відповідно до положення ручки газу.
2. **Скидання навігаційних інтеграторів**:
   - Інтегратори позиційних контурів місії негайно обнуляються, щоб усунути накопичену раніше помилку слідування траєкторії.
3. **Предзавантаження базової тяги**:
   - Інтегратор висотного контуру پیشзавантажується поточною адаптивною оцінкою тяги висіння `T_hover_estimate`.

---

## Інженерна реалізація мовою C

Нижче наведено повну модульну реалізацію детектора Stick Override на чистому стандарті C99, розраховану на роботу у складі вбудованих операційних систем реального часу (FreeRTOS, NuttX) або bare-metal контролерів літальних апаратів.

Код не містить динамічного виділення пам'яті, спирається на фіксовані структури даних і строго розмежовує конфігураційні параметри, вхідні телеметричні вектори та внутрішній стан фільтрів.

:::tabs
@tab C
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define RC_CHANNEL_ROLL        0
#define RC_CHANNEL_PITCH       1
#define RC_CHANNEL_YAW         2
#define RC_CHANNEL_THROTTLE    3
#define RC_MAX_CHANNELS        4

#define STICK_OVR_MASK_ROLL     (1u << RC_CHANNEL_ROLL)
#define STICK_OVR_MASK_PITCH    (1u << RC_CHANNEL_PITCH)
#define STICK_OVR_MASK_YAW      (1u << RC_CHANNEL_YAW)
#define STICK_OVR_MASK_THROTTLE (1u << RC_CHANNEL_THROTTLE)
#define STICK_OVR_MASK_ALL_RP   (STICK_OVR_MASK_ROLL | STICK_OVR_MASK_PITCH)
#define STICK_OVR_MASK_ALL      (STICK_OVR_MASK_ALL_RP | STICK_OVR_MASK_YAW | STICK_OVR_MASK_THROTTLE)

typedef enum {
    OVR_STATE_IDLE = 0,
    OVR_STATE_QUALIFYING,
    OVR_STATE_ACTIVE,
    OVR_STATE_RELEASE_HOLD
} StickOverrideState;

typedef enum {
    TARGET_MODE_STABILIZE = 0,
    TARGET_MODE_ALT_HOLD  = 1,
    TARGET_MODE_POS_HOLD  = 2,
    TARGET_MODE_ACRO      = 3
} FallbackFlightMode;

// Калібрувальні параметри апаратного каналу RC
typedef struct {
    uint16_t pwm_min;
    uint16_t pwm_trim;
    uint16_t pwm_max;
    float deadband_norm;      // Мертва зона (0.0 ... 0.2)
    float threshold_norm;     // Поріг активації оверрайду (0.05 ... 0.5)
} RcChannelCalibration;

// Конфігурація модуля Stick Override
typedef struct {
    RcChannelCalibration channels[RC_MAX_CHANNELS];
    uint32_t channel_mask;          // Маска активних каналів детектування
    uint32_t activation_delay_ms;  // Час безперервного відхилення для спрацьовування
    uint32_t release_hold_ms;       // Час утримання блокування після скидання стіків
    float euclidean_threshold_rp;  // Поріг для комбінованої норми Roll+Pitch
    bool use_euclidean_norm;       // Прапорець використання комбінованої норми
} StickOverrideConfig;

// Нормалізовані сигнали керування (-1.0 ... +1.0)
typedef struct {
    float roll;
    float pitch;
    float yaw;
    float throttle;
    bool is_valid;
} NormalizedRcInput;

// Стан детектора перехоплення
typedef struct {
    StickOverrideState state;
    uint32_t state_entry_timestamp_ms;
    uint32_t last_update_timestamp_ms;
    float current_max_deflection;
    bool override_active;
    bool override_latched_event;
    FallbackFlightMode recommended_mode;
} StickOverrideDetector;

// Ініціалізація конфігурації детектора типовими безпечними значеннями
static inline void stick_override_init_config(StickOverrideConfig *cfg) {
    if (!cfg) return;

    for (int i = 0; i < RC_MAX_CHANNELS; ++i) {
        cfg->channels[i].pwm_min = 1000;
        cfg->channels[i].pwm_trim = 1500;
        cfg->channels[i].pwm_max = 2000;
        cfg->channels[i].deadband_norm = 0.05f;    // 5% мертва зона (+-25 мкс)
        cfg->channels[i].threshold_norm = 0.15f;  // 15% поріг оверрайду (+-75 мкс)
    }

    // Канал газу за замовчуванням має більший поріг для уникнення хибних зривів
    cfg->channels[RC_CHANNEL_THROTTLE].threshold_norm = 0.20f;
    cfg->channels[RC_CHANNEL_YAW].threshold_norm = 0.25f;

    cfg->channel_mask = STICK_OVR_MASK_ALL_RP | STICK_OVR_MASK_THROTTLE;
    cfg->activation_delay_ms = 100;    // 100 мс дебаунсинг
    cfg->release_hold_ms = 1000;       // 1000 мс утримання після відпускання
    cfg->euclidean_threshold_rp = 0.18f;
    cfg->use_euclidean_norm = true;
}

// Ініціалізація об'єкта детектора
static inline void stick_override_detector_init(StickOverrideDetector *det) {
    if (!det) return;
    det->state = OVR_STATE_IDLE;
    det->state_entry_timestamp_ms = 0;
    det->last_update_timestamp_ms = 0;
    det->current_max_deflection = 0.0f;
    det->override_active = false;
    det->override_latched_event = false;
    det->recommended_mode = TARGET_MODE_POS_HOLD;
}

// Функція обчислення симетричної нормалізації з неперервним зняттям мертвої зони
static float normalize_channel_with_deadband(uint16_t pwm_raw, const RcChannelCalibration *cal) {
    if (pwm_raw < cal->pwm_min) pwm_raw = cal->pwm_min;
    if (pwm_raw > cal->pwm_max) pwm_raw = cal->pwm_max;

    float raw_norm = 0.0f;
    if (pwm_raw >= cal->pwm_trim) {
        float span = (float)(cal->pwm_max - cal->pwm_trim);
        if (span > 1.0f) {
            raw_norm = (float)(pwm_raw - cal->pwm_trim) / span;
        }
    } else {
        float span = (float)(cal->pwm_trim - cal->pwm_min);
        if (span > 1.0f) {
            raw_norm = -(float)(cal->pwm_trim - pwm_raw) / span;
        }
    }

    // Безрозривне масштабування мертвої зони
    float abs_val = fabsf(raw_norm);
    float db = cal->deadband_norm;

    if (abs_val <= db) {
        return 0.0f;
    }

    float scaled = (abs_val - db) / (1.0f - db);
    if (scaled > 1.0f) scaled = 1.0f;

    return (raw_norm >= 0.0f) ? scaled : -scaled;
}

// Нормалізація всього пакета радіоканалів
static void process_rc_inputs(const uint16_t raw_pwm[RC_MAX_CHANNELS],
                              const StickOverrideConfig *cfg,
                              NormalizedRcInput *out_norm) {
    if (!raw_pwm || !cfg || !out_norm) return;

    out_norm->roll     = normalize_channel_with_deadband(raw_pwm[RC_CHANNEL_ROLL], &cfg->channels[RC_CHANNEL_ROLL]);
    out_norm->pitch    = normalize_channel_with_deadband(raw_pwm[RC_CHANNEL_PITCH], &cfg->channels[RC_CHANNEL_PITCH]);
    out_norm->yaw      = normalize_channel_with_deadband(raw_pwm[RC_CHANNEL_YAW], &cfg->channels[RC_CHANNEL_YAW]);
    out_norm->throttle = normalize_channel_with_deadband(raw_pwm[RC_CHANNEL_THROTTLE], &cfg->channels[RC_CHANNEL_THROTTLE]);
    out_norm->is_valid = true;
}

// Визначення цільового безпечного режиму на основі сенсорного здоров'я
static FallbackFlightMode resolve_fallback_mode(uint32_t sensor_flags) {
    #define SENSOR_EKF_HORIZ_POS (1u << 4)
    #define SENSOR_EKF_VERT_POS  (1u << 3)
    #define SENSOR_AHRS_ATTITUDE (1u << 1)

    if ((sensor_flags & SENSOR_EKF_HORIZ_POS) != 0) {
        return TARGET_MODE_POS_HOLD;
    }
    if ((sensor_flags & SENSOR_EKF_VERT_POS) != 0) {
        return TARGET_MODE_ALT_HOLD;
    }
    if ((sensor_flags & SENSOR_AHRS_ATTITUDE) != 0) {
        return TARGET_MODE_STABILIZE;
    }

    return TARGET_MODE_STABILIZE;
}

// Основний польотний цикл обробки детектора Stick Override
void stick_override_update(StickOverrideDetector *det,
                           const StickOverrideConfig *cfg,
                           const NormalizedRcInput *rc,
                           uint32_t sensor_flags,
                           uint32_t current_time_ms) {
    if (!det || !cfg || !rc || !rc->is_valid) {
        return;
    }

    det->last_update_timestamp_ms = current_time_ms;
    det->override_latched_event = false;

    // Розрахунок нормованих відхилень за каналами
    float defl_roll     = fabsf(rc->roll);
    float defl_pitch    = fabsf(rc->pitch);
    float defl_yaw      = fabsf(rc->yaw);
    float defl_throttle = fabsf(rc->throttle);

    bool threshold_exceeded = false;
    float max_deflection = 0.0f;

    // Поканальна перевірка з урахуванням маски
    if ((cfg->channel_mask & STICK_OVR_MASK_ROLL) && (defl_roll >= cfg->channels[RC_CHANNEL_ROLL].threshold_norm)) {
        threshold_exceeded = true;
        if (defl_roll > max_deflection) max_deflection = defl_roll;
    }
    if ((cfg->channel_mask & STICK_OVR_MASK_PITCH) && (defl_pitch >= cfg->channels[RC_CHANNEL_PITCH].threshold_norm)) {
        threshold_exceeded = true;
        if (defl_pitch > max_deflection) max_deflection = defl_pitch;
    }
    if ((cfg->channel_mask & STICK_OVR_MASK_YAW) && (defl_yaw >= cfg->channels[RC_CHANNEL_YAW].threshold_norm)) {
        threshold_exceeded = true;
        if (defl_yaw > max_deflection) max_deflection = defl_yaw;
    }
    if ((cfg->channel_mask & STICK_OVR_MASK_THROTTLE) && (defl_throttle >= cfg->channels[RC_CHANNEL_THROTTLE].threshold_norm)) {
        threshold_exceeded = true;
        if (defl_throttle > max_deflection) max_deflection = defl_throttle;
    }

    // Комбінована норма площини горизонту
    if (cfg->use_euclidean_norm && ((cfg->channel_mask & STICK_OVR_MASK_ALL_RP) == STICK_OVR_MASK_ALL_RP)) {
        float euclidean_rp = sqrtf(rc->roll * rc->roll + rc->pitch * rc->pitch);
        if (euclidean_rp >= cfg->euclidean_threshold_rp) {
            threshold_exceeded = true;
            if (euclidean_rp > max_deflection) max_deflection = euclidean_rp;
        }
    }

    det->current_max_deflection = max_deflection;

    // Кінцевий автомат дебаунсингу та утримання
    switch (det->state) {
        case OVR_STATE_IDLE:
            det->override_active = false;
            if (threshold_exceeded) {
                det->state = OVR_STATE_QUALIFYING;
                det->state_entry_timestamp_ms = current_time_ms;
            }
            break;

        case OVR_STATE_QUALIFYING:
            det->override_active = false;
            if (!threshold_exceeded) {
                // Відхилення було короткочасним шумом
                det->state = OVR_STATE_IDLE;
            } else {
                uint32_t elapsed = current_time_ms - det->state_entry_timestamp_ms;
                if (elapsed >= cfg->activation_delay_ms) {
                    det->state = OVR_STATE_ACTIVE;
                    det->state_entry_timestamp_ms = current_time_ms;
                    det->override_active = true;
                    det->override_latched_event = true;
                    det->recommended_mode = resolve_fallback_mode(sensor_flags);
                }
            }
            break;

        case OVR_STATE_ACTIVE:
            det->override_active = true;
            det->recommended_mode = resolve_fallback_mode(sensor_flags);
            if (!threshold_exceeded) {
                // Стіки повернулися в нейтраль, перехід у фазу фіксації
                det->state = OVR_STATE_RELEASE_HOLD;
                det->state_entry_timestamp_ms = current_time_ms;
            }
            break;

        case OVR_STATE_RELEASE_HOLD:
            // Під час утримання оверрайд вважається формально завершеним,
            // але повторний вхід у стан IDLE заблоковано на час затримки
            det->override_active = false;
            if (threshold_exceeded) {
                // Пілот знову смикнув стік під час відліку паузи
                det->state = OVR_STATE_ACTIVE;
                det->state_entry_timestamp_ms = current_time_ms;
                det->override_active = true;
            } else {
                uint32_t elapsed = current_time_ms - det->state_entry_timestamp_ms;
                if (elapsed >= cfg->release_hold_ms) {
                    det->state = OVR_STATE_IDLE;
                }
            }
            break;

        default:
            det->state = OVR_STATE_IDLE;
            det->override_active = false;
            break;
    }
}
```
@tab C++
```cpp
#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <algorithm>
#include <string_view>

namespace autopilot::rc_override {

enum class ChannelAxis : uint8_t {
    Roll = 0,
    Pitch = 1,
    Yaw = 2,
    Throttle = 3,
    Count = 4
};

enum class OverrideState : uint8_t {
    Idle = 0,
    Qualifying,
    Active,
    ReleaseHold
};

enum class FallbackFlightMode : uint8_t {
    Stabilize = 0,
    AltHold = 1,
    PosHold = 2,
    Acro = 3
};

struct ChannelMask {
    static constexpr uint32_t Roll     = 1u << 0;
    static constexpr uint32_t Pitch    = 1u << 1;
    static constexpr uint32_t Yaw      = 1u << 2;
    static constexpr uint32_t Throttle = 1u << 3;
    static constexpr uint32_t RollPitch = Roll | Pitch;
    static constexpr uint32_t All = Roll | Pitch | Yaw | Throttle;
};

struct SensorFlags {
    static constexpr uint32_t AhrsAttitude = 1u << 1;
    static constexpr uint32_t EkfVertPos   = 1u << 3;
    static constexpr uint32_t EkfHorizPos  = 1u << 4;
};

// Конфігурація окремого фізичного каналу радіокерування
struct ChannelCalibration {
    uint16_t pwm_min{1000};
    uint16_t pwm_trim{1500};
    uint16_t pwm_max{2000};
    float deadband_norm{0.05f};    // 5% радіус мертвої зони
    float threshold_norm{0.15f};   // 15% поріг детектування втручання

    [[nodiscard]] constexpr float normalize(uint16_t pwm_raw) const noexcept {
        const uint16_t clamped_pwm = std::clamp(pwm_raw, pwm_min, pwm_max);
        float raw_norm = 0.0f;

        if (clamped_pwm >= pwm_trim) {
            const float span = static_cast<float>(pwm_max - pwm_trim);
            if (span > 1.0f) {
                raw_norm = static_cast<float>(clamped_pwm - pwm_trim) / span;
            }
        } else {
            const float span = static_cast<float>(pwm_trim - pwm_min);
            if (span > 1.0f) {
                raw_norm = -static_cast<float>(pwm_trim - clamped_pwm) / span;
            }
        }

        const float abs_val = std::abs(raw_norm);
        if (abs_val <= deadband_norm) {
            return 0.0f;
        }

        const float scaled = (abs_val - deadband_norm) / (1.0f - deadband_norm);
        const float clamped_scaled = std::clamp(scaled, 0.0f, 1.0f);
        return (raw_norm >= 0.0f) ? clamped_scaled : -clamped_scaled;
    }
};

// Нормалізовані польотні вектори керування
struct NormalizedChannels {
    float roll{0.0f};
    float pitch{0.0f};
    float yaw{0.0f};
    float throttle{0.0f};
    bool is_valid{false};

    [[nodiscard]] constexpr float get(ChannelAxis axis) const noexcept {
        switch (axis) {
            case ChannelAxis::Roll: return roll;
            case ChannelAxis::Pitch: return pitch;
            case ChannelAxis::Yaw: return yaw;
            case ChannelAxis::Throttle: return throttle;
            default: return 0.0f;
        }
    }
};

// Повний конфігураційний профіль модуля
struct Config {
    std::array<ChannelCalibration, static_cast<size_t>(ChannelAxis::Count)> channels{};
    uint32_t channel_mask{ChannelMask::RollPitch | ChannelMask::Throttle};
    uint32_t activation_delay_ms{100};
    uint32_t release_hold_ms{1000};
    float euclidean_threshold_rp{0.18f};
    bool use_euclidean_norm{true};

    constexpr Config() noexcept {
        channels[static_cast<size_t>(ChannelAxis::Throttle)].threshold_norm = 0.20f;
        channels[static_cast<size_t>(ChannelAxis::Yaw)].threshold_norm = 0.25f;
    }
};

// Клас детектора втручання пілота
class StickOverrideDetector {
public:
    explicit constexpr StickOverrideDetector(const Config& config = Config{}) noexcept
        : config_(config) {}

    void reset() noexcept {
        state_ = OverrideState::Idle;
        state_entry_ms_ = 0;
        last_update_ms_ = 0;
        current_max_deflection_ = 0.0f;
        override_active_ = false;
        latched_transition_event_ = false;
        recommended_mode_ = FallbackFlightMode::PosHold;
    }

    [[nodiscard]] NormalizedChannels process_raw_channels(std::span<const uint16_t> raw_pwm) const noexcept {
        NormalizedChannels out{};
        if (raw_pwm.size() < static_cast<size_t>(ChannelAxis::Count)) {
            return out;
        }

        out.roll = config_.channels[static_cast<size_t>(ChannelAxis::Roll)].normalize(raw_pwm[0]);
        out.pitch = config_.channels[static_cast<size_t>(ChannelAxis::Pitch)].normalize(raw_pwm[1]);
        out.yaw = config_.channels[static_cast<size_t>(ChannelAxis::Yaw)].normalize(raw_pwm[2]);
        out.throttle = config_.channels[static_cast<size_t>(ChannelAxis::Throttle)].normalize(raw_pwm[3]);
        out.is_valid = true;
        return out;
    }

    void update(const NormalizedChannels& rc, uint32_t sensor_flags, uint32_t current_time_ms) noexcept {
        if (!rc.is_valid) {
            return;
        }

        last_update_ms_ = current_time_ms;
        latched_transition_event_ = false;

        const bool threshold_exceeded = evaluate_deflection(rc);

        switch (state_) {
            case OverrideState::Idle:
                override_active_ = false;
                if (threshold_exceeded) {
                    state_ = OverrideState::Qualifying;
                    state_entry_ms_ = current_time_ms;
                }
                break;

            case OverrideState::Qualifying:
                override_active_ = false;
                if (!threshold_exceeded) {
                    state_ = OverrideState::Idle;
                } else if ((current_time_ms - state_entry_ms_) >= config_.activation_delay_ms) {
                    state_ = OverrideState::Active;
                    state_entry_ms_ = current_time_ms;
                    override_active_ = true;
                    latched_transition_event_ = true;
                    recommended_mode_ = resolve_fallback(sensor_flags);
                }
                break;

            case OverrideState::Active:
                override_active_ = true;
                recommended_mode_ = resolve_fallback(sensor_flags);
                if (!threshold_exceeded) {
                    state_ = OverrideState::ReleaseHold;
                    state_entry_ms_ = current_time_ms;
                }
                break;

            case OverrideState::ReleaseHold:
                override_active_ = false;
                if (threshold_exceeded) {
                    state_ = OverrideState::Active;
                    state_entry_ms_ = current_time_ms;
                    override_active_ = true;
                } else if ((current_time_ms - state_entry_ms_) >= config_.release_hold_ms) {
                    state_ = OverrideState::Idle;
                }
                break;
        }
    }

    [[nodiscard]] constexpr bool is_override_active() const noexcept { return override_active_; }
    [[nodiscard]] constexpr bool has_triggered_transition() const noexcept { return latched_transition_event_; }
    [[nodiscard]] constexpr OverrideState state() const noexcept { return state_; }
    [[nodiscard]] constexpr FallbackFlightMode recommended_mode() const noexcept { return recommended_mode_; }
    [[nodiscard]] constexpr float current_deflection() const noexcept { return current_max_deflection_; }
    [[nodiscard]] const Config& config() const noexcept { return config_; }
    void set_config(const Config& cfg) noexcept { config_ = cfg; }

private:
    [[nodiscard]] bool evaluate_deflection(const NormalizedChannels& rc) noexcept {
        bool exceeded = false;
        float max_d = 0.0f;

        auto check_axis = [&](ChannelAxis axis, uint32_t mask_bit, float val) {
            if ((config_.channel_mask & mask_bit) != 0) {
                const float abs_v = std::abs(val);
                const float th = config_.channels[static_cast<size_t>(axis)].threshold_norm;
                if (abs_v >= th) {
                    exceeded = true;
                    max_d = std::max(max_d, abs_v);
                }
            }
        };

        check_axis(ChannelAxis::Roll, ChannelMask::Roll, rc.roll);
        check_axis(ChannelAxis::Pitch, ChannelMask::Pitch, rc.pitch);
        check_axis(ChannelAxis::Yaw, ChannelMask::Yaw, rc.yaw);
        check_axis(ChannelAxis::Throttle, ChannelMask::Throttle, rc.throttle);

        if (config_.use_euclidean_norm && ((config_.channel_mask & ChannelMask::RollPitch) == ChannelMask::RollPitch)) {
            const float euclidean_rp = std::sqrt(rc.roll * rc.roll + rc.pitch * rc.pitch);
            if (euclidean_rp >= config_.euclidean_threshold_rp) {
                exceeded = true;
                max_d = std::max(max_d, euclidean_rp);
            }
        }

        current_max_deflection_ = max_d;
        return exceeded;
    }

    [[nodiscard]] static constexpr FallbackFlightMode resolve_fallback(uint32_t sensor_flags) noexcept {
        if ((sensor_flags & SensorFlags::EkfHorizPos) != 0) {
            return FallbackFlightMode::PosHold;
        }
        if ((sensor_flags & SensorFlags::EkfVertPos) != 0) {
            return FallbackFlightMode::AltHold;
        }
        if ((sensor_flags & SensorFlags::AhrsAttitude) != 0) {
            return FallbackFlightMode::Stabilize;
        }
        return FallbackFlightMode::Stabilize;
    }

    Config config_{};
    OverrideState state_{OverrideState::Idle};
    uint32_t state_entry_ms_{0};
    uint32_t last_update_ms_{0};
    float current_max_deflection_{0.0f};
    bool override_active_{false};
    bool latched_transition_event_{false};
    FallbackFlightMode recommended_mode_{FallbackFlightMode::PosHold};
};

} // namespace autopilot::rc_override
```
:::

---

## Інженерні пастки, крайові випадки та правила інтеграції

Практична інтеграція алгоритму перехоплення стіками у польотний стек вимагає врахування низки критичних аспектів авіоніки:

### 1. Конфлікт пріоритетів: RC Failsafe проти Stick Override

Найнебезпечніша помилка проектування — відсутність перевірки валідності пакетів радіозв'язку перед аналізом відхилення стіків.

```
+─────────────────────────────────────────────────────────────────────────+
|               Ієрархія пріоритетів безпеки в польоті                   |
+─────────────────────────────────────────────────────────────────────────+
|  Рівень 0: Аварійні протоколи (RC Failsafe, Geofence, Critical Battery)  | [Вищий]
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+─────────────────────────────────────────────────────────────────────────+
|  Рівень 1: Втручання пілота через Stick Override                        |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+─────────────────────────────────────────────────────────────────────────+
|  Рівень 2: Автономне виконання місії (Auto / Mission / RTL)             | [Нижчий]
+─────────────────────────────────────────────────────────────────────────+
```

Якщо під час виконання автономної місії дрон вилітає за радіогоризонт і втрачає радіозв'язок, приймач RC у режимі `Hold Last State` може зафіксувати останнє ненульове положення ручок. Якщо детектор оверрайду проігнорує статус втрати лінку (`rc_lost == true`), система сприйме застигле значення як неперервне втручання пілота, заблокує спрацьовування аварійного повернення додому `FAILSAFE_RTL` і зависне над лісом або водою до повного розряду батареї.

**Правило безпеки**: обробка детектора Stick Override повинна негайно блокуватися при активному прапорці `rc_link_lost` або `rc_failsafe_active`.

### 2. Апаратне тримування на пульті під час польоту

Якщо пілот під час польоту в ручному режимі змінює положення механічних тримерів на корпусі пульта, апаратне значення нейтралі змінюється (наприклад, з 1500 мкс на 1580 мкс). Коли оператор згодом запускає автономну місію, дрейф тримування перевищує мертву зону 5%, і автопілот у перший же такт скидає автономний режим назад у ручний.

Для усунення цієї проблеми в сучасних польотних прошивках реалізується механізм автоматичного калібрування центра нейтралі (`Auto-Trim Capture`): у момент зведення моторів на землі (`Arming Event`) автопілот фіксує поточні позиції каналів як опорні точки `PWM_trim` для всього наступного польоту.

### 3. Специфіка планера: мультикоптери проти літаків

Реакція системи на рух стіка газу суттєво залежить від аеродинаміки планера:
- **Мультикоптер**: оверрайд за газом безпечний у будь-якому напрямку. Навіть при повному скиданні газу в нуль у режимі `ALT_HOLD` або `POS_HOLD` автопілот обмежує максимальну швидкість зниження безпечним значенням (зазвичай не більше 2.5 м/с).
- **Літак з фіксованим крилом**: скидання газу нижче мінімального польотного порогу спричиняє падіння повітряної швидкості нижче швидкості звалювання `V_stall`. Тому для літаків канал газу виключається з маски оверрайду (`channel_mask &= ~STICK_OVR_MASK_THROTTLE`), а перехоплення дозволяється лише за креном і тангажем.

### 4. Асистоване підрулювання (Nudge) проти повного скидання (Full Override)

Залежно від тактичного призначення апарата застосовують два принципово різні підходи до обробки стіків в автономних режимах:

| Параметр | Повне перехоплення (Full Mode Override) | Асистоване підрулювання (Assisted Nudge) |
| :--- | :--- | :--- |
| **Зміна польотного режиму** | Відбувається примусовий перехід у `POS_HOLD` або `ALT_HOLD`. | Режим `AUTO` зберігається, автомат станів не перемикається. |
| **Поведінка після відпускання стіків** | Дрон зависає в точці відпускання й чекає нових дій оператора. | Дрон плавно повертається на лінію поточної місії та продовжує політ. |
| **Сфера застосування** | Екстрене ухилення від аварій, інспекційні польоти, посадка. | Невеликий обхід раптових перешкод на маршруті без зриву плану польоту. |
| **Навантаження на пілота** | Вимагає повторної команди з пульта або GCS для продовження місії. | Мінімальне: відпустив стік — місія продовжилась автоматично. |

### 5. Багатопотоковість та синхронізація в ОСРЧ (RTOS Concurrency)

У реальному автопілоті на базі FreeRTOS або NuttX обробка радіопакетів і робота автомата режимів розділені на різні асинхронні задачі:
- **`rc_input_task`** (частота 50–200 Гц): працює за перериваннями UART/DMA від приймача SBUS/CRSF, виконує парсинг фреймів і нормалізацію.
- **`flight_fsm_task`** (частота 400–1000 Гц): виконує контур швидкого оцінювання орієнтації та оновлення кінцевого автомата режимів.

Прямий спільний доступ до структури `NormalizedRcInput` без синхронізації створює стан гонитви даних (*race condition*): коли завдання FSM зчитує оновлений крен, але ще застарілий тангаж з попереднього пакету.

Для гарантування цілісності передачі даних без блокування високочастотного польотного контуру застосовується техніка подвійної буферизації без блокувань (*lock-free double buffering*) або атомарного обміну покажчиками за допомогою інструкції `atomic_exchange`.

### 6. Практичне калібрування параметрів для різних класів безпілотників

| Клас літального апарата | Мертва зона `deadband` | Поріг активації `threshold` | Затримка `activation_delay_ms` | Пауза скидання `release_hold_ms` |
| :--- | :--- | :--- | :--- | :--- |
| **FPV / Гоночний квадрокоптер** | 3% (±15 мкс) | 10% (±50 мкс) | 50 мс | 500 мс |
| **Важкий інспекційний коптер** | 5% (±25 мкс) | 15% (±75 мкс) | 100 мс | 1000 мс |
| **Літак дальньої розвідки** | 6% (±30 мкс) | 18% (±90 мкс) | 150 мс | 1500 мс |
| **Вантажний конвертоплан (VTOL)**| 5% (±25 мкс) | 15% (±75 мкс) | 120 мс | 1200 мс |

Збільшення часу дебаунсингу `activation_delay_ms` для важких літаків зумовлене тим, що велика аеродинамічна інерція планера не вимагає мікросекундної реакції, але надзвичайно чутлива до випадкових смикань стіків пілотом у поривчастому вітрі.

---

## Діагностика, польотні журнали та MAVLink-телеметрія

Будь-яке спрацьовування алгоритму Stick Override обов'язково супроводжується фіксацією в бортових журналах та інформуванням наземної станції керування (QGroundControl, Mission Planner):

1. **Текстове сповіщення `STATUSTEXT` (MAVLink ID #253)**:
   При переході автомата в стан `OVR_STATE_ACTIVE` формується високопріоритетне повідомлення:
   `"Pilot override detected: Mode changed to POSHOLD (Roll/Pitch deflection 24%)"`.
2. **Бінарне логування у потоках DataFlash / ULog**:
   - Повідомлення `RCIN`: сирі значення мікросекунд за всіма каналами.
   - Повідомлення `OVRD`: стан детектора (`State`), обчислене значення деформації (`DeflMax`), маска активних каналів (`Mask`).
   - Повідомлення `MODE`: точна часова мітка зміни режиму зі статусом джерела `MODE_REASON_RC_OVERRIDE`.

Синхронізація цих графіків під час аналізу польотного інциденту дозволяє однозначно підтвердити, що вихід апарата з лінії автономного маршруту відбувся внаслідок усвідомленої фізичної дії пілота, а не через програмний збій навігаційного стека.
