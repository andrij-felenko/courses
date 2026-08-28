# ⚙️ Диспетчер покрокової ініціалізації обладнання з мікросекундними затримками

<preknowlist>
- [Регістри GPIO](root:sf-devices/gpio-registers) — прямий доступ до вихідних засувок та конфігурації портів.
- [CMSIS](root:sf-devices/cmsis) — лічильник тактових циклів DWT ядра Cortex-M та керування регістрами процесора.
- [Неблокуючий час](root:sf-devices/nonblocking-time) — патерн обчислення інтервалів через різницю беззнакових міток без зупинки процесора.
- [Сторожовий таймер](root:sf-devices/watchdog) — часовий захист від зависання та вимоги до періодичного оновлення лічильника.
- [Самовідновлення та деградація](root:sf-devices/graceful-degradation) — робота приладу в умовах відмови окремих апаратних вузлів.
</preknowlist>

У навчальних прикладах і простих демонстраційних скетчах ініціалізація апаратного забезпечення виглядає як монолітний список послідовних викликів у функції `main()` або `setup()`: увімкнути тактування, викликати `delay(50)`, налаштувати датчик, викликати `delay(100)`, запустити дисплей, почекати ще 200 мілісекунд. У реальному серійному приладі такий підхід стає головним джерелом раптових відмов та непереборних проблем надійності.

Коли прилад містить десяток зовнішніх мікросхем (інерційний модуль IMU, флеш-пам'ять, GNSS-приймач, дисплей, драйвери двигунів, радіотрансивер), сумарний час витримок перехідних процесів легко сягає 500...1500 мілісекунд. Якщо в системі активовано апаратний сторожовий таймер (Watchdog), налаштований на стандартний інтервал спрацьовування 50...100 мілісекунд для швидкого реагування на збої в роботі, блокувальні виклики `delay()` призведуть до того, що сторожовий таймер скине мікроконтролер ще до завершення запуску. Прилад потрапляє в нескінченну петлю перезавантажень (Bootloop), яку неможливо подолати без фізичного відключення живлення або перепрошивки.

Друга критична вада лінійного коду — повна відсутність гранулярної діагностики та механізмів відкату (Rollback). Якщо один із сенсорів на шині I2C вийшов із ладу, не запаяний або має дефект живлення, наївний код зависає у нескінченному циклі `while (!(I2C->SR1 & I2C_SR1_ADDR))` або повертає загальну помилку, зупиняючи запуск усього виробу. На практиці більшість систем повинні підтримувати режим деградованої функціональності (Graceful Degradation): якщо додатковий датчик вологості не відповідає, прилад зобов'язаний зафіксувати код несправності в енергонезалежному журналі, знеструмити проблемний вузол, перевести пов'язані виводи GPIO у безпечний стан з високим опором (High-Z) і продовжити штатну роботу з основними виконавчими механізмами.

Третьою фізичною проблемою одночасного ввімкнення є пускові струми (Inrush Currents). Якщо прошивка одночасно відкриває ключі живлення для всіх модулів, сумарний імпульсний струм заряду вхідних ємностей спричиняє просідання вихідної напруги стабілізатора живлення (LDO або DC-DC) нижче порогу спрацьовування детектора Brown-Out Reset. Покроковий диспетчер розносить у часі запуск силових каскадів, забезпечуючи плавне поетапне наростання споживання струму без небезпечних просідань напруги.

Для вирішення цих завдань застосовують архітектуру таблично-керованого диспетчера покрокової ініціалізації (Step-by-Step Hardware Initialization Engine). Такий диспетчер перетворює хаотичний набір процедур на детермінований скінченний автомат із прецизійним неблокувальним контролем мікросекундних пауз, індивідуальними таймаутами очікування готовності, регулярним обслуговуванням сторожового таймера та автоматичним виконанням аварійних дій у разі апаратних збоїв.

## Архітектура табличного автомата ініціалізації

В основі архітектури лежить розділення опису послідовності (декларативна таблиця кроків) та виконавчого механізму (рушій крокового виконання). Кожен крок запуску описується структурою дескриптора, яка містить повний набір атрибутів поведінки:

1. **Текстовий ідентифікатор (`name`).** Використовується для трасування запуску через діагностичний порт UART або системний журнал подій.
2. **Функція дії (`action`).** Одноразовий виклик, який ініціює апаратну дію: подає живлення на ключ, виставляє логічний рівень на виводі скидання nRST, записує конфігураційний регістр або надсилає команду запуску по шині.
3. **Фіксована витримка (`hold_delay_us`).** Мінімальний гарантований фізичний інтервал часу, необхідний після виконання дії для завершення перехідного процесу (наприклад, час наростання напруги або тривалість утримання скидання).
4. **Предикат готовності (`poll_condition`).** Функція зворотного виклику, яка опитує апаратний стан: перевіряє біт готовності генератора (`HSERDY`), завершення калібрування АЦП, стан лінії готовності даних `DRDY` або відповідність зчитаного ідентифікатора `WHO_AM_I`.
5. **Таймаут очікування (`timeout_us`).** Максимальний допустимий час на виконання умови предиката. Якщо умова не настала за цей час, крок вважається аварійно завершеним.
6. **Обробник відкату (`rollback`).** Спеціалізована функція безпеки, яка викликається при збої кроку для повернення апаратури у вихідний або безпечний стан (зняття напруги, відключення переривань, притискання виводів до землі).
7. **Прапорець критичності (`is_critical`).** Визначає поведінку системи при невдачі: збій критичного кроку переводить усю систему в аварійний режим (Safe Mode) із зупинкою конвеєра, тоді як збій некритичного кроку лише реєструє помилку та дозволяє продовжити запуск наступних підсистем.

Для точного відліку часових інтервалів від одиниць мікросекунд до сотень мілісекунд використовується апаратний 32-бітний лічильник тактових циклів ядра DWT (Data Watchpoint and Trace), доступний у процесорах Cortex-M3/M4/M7/M33. На відміну від системного таймера `SysTick`, який вимагає налаштування частоти, увімкнення переривань та прив'язки до змінних операційної системи, лічильник DWT є пасивним апаратним регістром. Він починає рахувати цикли процесора відразу після подачі живлення та встановлення біта `CYCCNTENA`, працюючи бездоганно навіть при глобально заблокованих перериваннях ядра (`__disable_irq()`).

На тактовій частоті 168 МГц один такт DWT становить приблизно 5.95 наносекунди, що забезпечує прецизійну роздільну здатність. Період повного переповнення 32-бітного лічильника на цій частоті становить 25.56 секунди (а на частоті 480 МГц — 8.94 секунди). Оскільки будь-який окремий крок ініціалізації триває від часток мікросекунди до кількох сотень мілісекунд, беззнакове віднімання `(uint32_t)(current_ticks - start_ticks)` гарантує математично точний результат навіть у мить переходу лічильника через максимальне значення `0xFFFFFFFF`.

## Контроль пускового струму (Inrush Current) та просідання шин живлення

Одночасна комутація живлення багатьох периферійних модулів створює важкий перехідний процес в електричній підсистемі плати. Кожен зовнішній чип (радіотрансивер, дисплейний контролер, GNSS-приймач, сенсорний кластер, зовнішня флеш-пам'ять) має власні розв'язувальні керамічні конденсатори (MLCC) сумарною ємністю від 10 до 100 мкФ, встановлені безпосередньо біля виводів живлення V_DD.

Фізична природа пускового струму описується співвідношенням:

I_inrush(t) = C_load · (dV(t) / dt)

У мить замикання комутаційного польового транзистора (High-Side P-MOSFET або інтелектуального перемикача навантаження Load Switch) розряджені конденсатори є еквівалентом короткого замикання шини живлення на землю GND. Якщо швидкість наростання напруги dV/dt не обмежена спеціальними апаратними заходами, струм заряду ємностей обмежується виключно малим опором відкритого каналу транзистора R_DS(on) і паразитною індуктивністю та активним опором друкованих провідників (одиниці або десятки міліомів). Як наслідок, виникає надкороткий імпульсний сплеск струму амплітудою від 2 до 8 амперів тривалістю 10...50 мікросекунд.

Неконтрольований сумарний пусковий струм призводить до трьох характерних апаратних відмов:
1. **Глибоке просідання напруги живлення (Voltage Sag / Brown-Out).** Імпульсне перевантаження перевищує максимальну здатність первинного регулятора (LDO або імпульсного DC-DC перетворювача) підтримувати стабільну напругу. Системна лінія 3.3 В миттєво просідає нижче критичного порогу. Якщо напруга перетинає рівень спрацьовування апаратного детектора Brown-Out Reset мікроконтролера (наприклад, 2.7 В або 2.4 В у STM32), цифрове ядро зазнає раптового апаратного скидання. Плата входить у нескінченний циклічний перезапуск (Bootloop) ще до виклику першого драйвера периферії.
2. **Аварійне спрацьовування захисту регулятора (Current Limit Tripping).** Інтегральні перетворювачі напруги містять захисні контури обмеження струму (Foldback / OCP). У разі фіксації короткого замикання регулятор блокує вихід або переходить у режим циклічного перезапуску (Hiccup Mode), що викликає тривалі коливання напруги та заважає коректному виходу мікросхем із початкового скидання Power-On Reset.
3. **Прискорене старіння та деградація ключів комутації.** Постійні циклічні струмові удари викликають локальний перегрів кристала комутаційного польового транзистора, поступово руйнуючи його контактні площадки через явище електроміграції металу.

Диспетчер покрокової ініціалізації надійно усуває ці ризики на рівні прошивки за допомогою комплексу інженерних рішень:
- **Часове рознесення увімкнення силових доменів (Power Staggering / Power Sequencing).** Плата розбивається на незалежні ізольовані зони живлення. Диспетчер активує черговий силовий ключ лише після того, як повністю завершився процес заряду ємностей попереднього вузла, визначений фізичною витримкою t_charge ≈ 3...5 · R_source · C_load у конфігураційному полі `hold_delay_us`. Сплески струму розносяться у часі на мілісекунди, і їхня амплітуда ніколи не накладається одна на одну.
- **Програмно-апаратне керування швидкістю наростання (Slew Rate Control).** Застосування мікросхем Load Switch із керованим часом наростання напруги (Soft-Start) або поетапне увімкнення через проміжний баластний резистор струмообмеження з подальшим шунтуванням прямим транзистором.
- **Апаратна валідація стабілізації напруги через сигнал PGOOD або АЦП.** У функції `poll_condition` диспетчер контролює стан апаратної лінії готовності живлення `Power Good` від регулятора або здійснює швидкий вимір фактичної напруги шини через вбудований АЦП мікроконтролера. Перехід до запуску цифрових інтерфейсів ведених чипів дозволяється лише за умови, що шина повністю стабілізувалася на рівні 3.3 В ±2%.

## Фізика паразитного живлення (Phantom Powering) та захист ліній

Один із найбільш небезпечних апаратних феноменів під час поетапного запуску плати пов'язаний із паразитним живленням знеструмлених мікросхем через сигнальні лінії введення-виведення (Phantom Powering).

Кожен вивід цифрової інтегральної мікросхеми містить внутрішні захисні діоди від електростатичного розряду (ESD Protection Diodes). Верхній діод анодом підключений до сигнального виводу, а катодом — до внутрішньої шини живлення V_DD мікросхеми. Нижній діод катодом підключений до виводу, а анодом — до шини землі GND.

Якщо мікроконтролер уже увімкнений і виставляє логічну одиницю (3.3 В) на лінії інтерфейсу SPI (наприклад, лінія Chip Select nCS підтягнута до 3.3 В) до того, як відкрився силовой транзисторний ключ живлення зовнішнього сенсора (V_DD сенсора дорівнює 0 В), виникає паразитна електрична мережа. Електричний струм із вихідного каскаду мікроконтролера тече через лінію nCS, проходить через верхній ESD-діод сенсора на його внутрішню знеструмлену шину V_DD і починає заряджати блокувальні конденсатори мікросхеми.

Наслідки паразитного живлення:
1. **Теплове перевантаження та деградація кристала.** Струм через мікроскопічний захисний діод може досягати 20...50 мА, що значно перевищує його паспортну граничну потужність. З часом діод зазнає теплового пробою.
2. **Зависання цифрового ядра веденого чипа.** Через падіння напруги на діоді (близько 0.6 В) напруга на внутрішній шині сенсора становить 2.7 В замість номінальних 3.3 В. Схема POR сенсора потрапляє в зону невизначеності, внутрішні тригери ініціалізуються хаотично, і мікросхема виявляється намертво заблокованою ще до подачі основного живлення.
3. **Витоки струму в батарейних приладах.** Замість мікроамперного споживання у режимі сну знеструмлена частина плати споживає міліампери паразитного струму з ліній мікроконтролера.

Тому покроковий диспетчер забезпечує суворе дотримання правил комутації: доки ключ живлення V_DD конкретного вузла не увімкнено і не витримано час стабілізації напруги, усі пов'язані сигнальні лінії мікроконтролера примусово утримуються у стані високого опору (Analog / Floating Input) або притиснуті до нуля (LOW).

## Механізм розблокування шини I2C при старті (Bus Recovery)

Одним із найпоширеніших джерел зависання пристрою під час гарячого перезапуску або після короткочасного збою живлення є блокування шини I2C. Якщо мікроконтролер перезавантажується в момент, коли він зчитував дані з веденої мікросхеми, а ведений чип утримував лінію даних SDA в нулі (передавав нульовий біт або біт підтвердження ACK), після перезапуску шина опиняється у глухому куті.

Мікроконтролер бачить лінію SDA на нулі і відповідно до специфікації I2C вважає, що шина зайнята іншим Master-пристроєм (`I2C_SR2_BUSY = 1`). Апаратний блок I2C мікроконтролера блокує формування стартової умови START, а ведений чип продовжує нескінченно чекати на тактові імпульси SCL, щоб завершити передачу поточного байта.

Універсальний диспетчер ініціалізації включає процедуру відновлення шини I2C (I2C Bus Recovery) як обов'язковий етап перед налаштуванням самого модуля I2C:
1. Виводи SDA та SCL налаштовуються як звичайні виходи GPIO з відкритим стоком (Open Drain) та підтяжкою до V_DD.
2. Програма опитує стан лінії SDA. Якщо SDA знаходиться у високому рівні (1), шина вільна, і можна переходити до стандартної конфігурації.
3. Якщо SDA притягнута до нуля (0), мікроконтролер вручну генерує серію з 9 тактових імпульсів на лінії SCL із частотою близько 100 кГц (паузи по 5 мкс між фронтами).
4. Отримавши 9 тактових імпульсів, ведений чип гарантовано виштовхує залишок свого внутрішнього зсувного регістра, бачить, що Master не видав ACK на 9-му такті, і відпускає лінію SDA у високий рівень.
5. Після цього мікроконтролер формує ручну послідовність STOP (переводить SDA з низького рівня у високий при високому рівні SCL), повертаючи всі підключені мікросхеми у вихідний стан очікування адреси.
6. Лише після успішного звільнення лінії SDA виводи перемикаються в режим альтернативної функції апаратного модуля I2C.

Інтеграція цієї процедури в автомат ініціалізації гарантує, що прилад самостійно вийде зі стану зависання без необхідності механічного знеструмлення.

## Взаємодія диспетчера з операційними системами реального часу (RTOS)

Коли вбудована система побудована на базі операційної системи реального часу (FreeRTOS, Zephyr або RT-Thread), диспетчер ініціалізації виконується у контексті окремої низькопріоритетної або стартової задачі (`InitTask`).

При роботі в RTOS з'являється можливість оптимізувати енергоспоживання та час процесора:
- Для надкоротких затримок (менше 500 мікросекунд), таких як витримка стробів скидання або імпульсів розблокування шини, диспетчер використовує активне очікування на лічильнику DWT, оскільки накладні витрати на перемикання контексту RTOS (Context Switch) співмірні з самою паузою.
- Для тривалих інтервалів стабілізації (від 5 до 100 мілісекунд), таких як розгін кварцового генератора, заряд ємностей помножувача напруги дисплея або очікування калібрування сенсора, функція кроку може віддавати керування планувальнику викликом `vTaskDelay()`. Процесорне ядро переходить у режим сну або обслуговує інші фонові потоки.

При цьому автомат зберігає свій стан і повертається до перевірки умов після пробудження без втрати атомарності та контролю загального таймауту.

## Граничні випадки, повторні спроби (Retries) та зняття дампів стану

У промислових та польових пристроях периферійні чипи можуть не відповідати з першої спроби через імпульсні перешкоди на лініях зв'язку, тимчасові температурні коливання або тривалий вихід стабілізатора напруги на робочий режим.

Для запобігання передчасній відмові системи диспетчер підтримує стратегію повторних спроб (Retry Policy) з алгоритмом експоненційного відступу (Exponential Backoff). Якщо опитування готовності завершується таймаутом, автомат не відкидає вузол відразу, а виконує повторний цикл скидання з подвоєним інтервалом паузи. Це дозволяє розірвати часовий резонанс, коли період внутрішнього перезапуску веденого сенсора випадково збігається з періодом опитування мікроконтролера.

Якщо ж крок зазнає остаточного фатального збою, диспетчер формує діагностичний знімок стану (Crash Dump):
- Фіксує бітову маску помилкових кроків `failed_step_mask`.
- Зчитує статусний регістр скидання RCC (наприклад, `RCC_CSR`), щоб зафіксувати фізичну причину попереднього перезавантаження (скидання по сторожовому таймеру, скидання по BOR, скидання з виводу NRST).
- Записує дамп у захищену енергонезалежну область пам'яті RTC Backup Domain (BBRAM) або у виділений сектор Flash-пам'яті.
- Переводить прилад в аварійний режим (Safe Mode), активуючи світлодіодний код помилки або надсилаючи аварійне сповіщення оператору через резервний канал зв'язку.

## Повний робочий код: C99 та C++20

Нижче наведено виробничі реалізації рушія покрокової ініціалізації для мікроконтролерів сімейства STM32: класичний модульний варіант стандарту C99 та типізований об'єктний варіант стандарту C++20 із застосуванням лямбда-виразів, концептів і безпечної обробки помилок через `std::expected`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "stm32f4xx.h"

// Перелік глобальних статусів диспетчера ініціалізації
typedef enum {
    INIT_ENGINE_IDLE = 0,
    INIT_ENGINE_RUNNING,
    INIT_ENGINE_SUCCESS,
    INIT_ENGINE_FAILED,
    INIT_ENGINE_DEGRADED
} init_engine_status_t;

// Типи функцій зворотного виклику для кроків послідовності
typedef bool (*init_action_fn)(void *ctx);
typedef bool (*init_poll_fn)(void *ctx);
typedef void (*init_rollback_fn)(void *ctx);

// Дескриптор одного етапу ініціалізації
typedef struct {
    const char       *name;             // Назва кроку для трасування та діагностики
    init_action_fn    action;           // Апаратна дія на старті кроку (може бути NULL)
    uint32_t          hold_delay_us;    // Захисна витримка перехідного процесу
    init_poll_fn      poll_condition;   // Предикат опитування готовності (може бути NULL)
    uint32_t          timeout_us;       // Граничний таймаут очікування умови
    init_rollback_fn  rollback;         // Функція безпечного відкату при збої
    bool              is_critical;      // Фатальність збою для системи
} init_step_t;

// Фази виконання окремого кроку всередині скінченного автомата
typedef enum {
    STEP_PHASE_ACTION = 0,
    STEP_PHASE_HOLD_DELAY,
    STEP_PHASE_POLLING
} step_phase_t;

// Контекст стану диспетчера
typedef struct {
    const init_step_t   *steps;
    size_t               total_steps;
    size_t               current_index;
    step_phase_t         phase;
    uint32_t             phase_start_ticks;
    uint32_t             poll_start_ticks;
    void                *user_context;
    init_engine_status_t status;
    uint32_t             failed_step_mask;
} init_engine_t;

// ── Апаратні допоміжні функції ──

static inline void dwt_timer_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

static inline uint32_t dwt_get_cycles(void) {
    return DWT->CYCCNT;
}

static inline uint32_t us_to_dwt_ticks(uint32_t us) {
    return us * (SystemCoreClock / 1000000U);
}

static inline void watchdog_feed(void) {
    #if defined(IWDG)
    IWDG->KR = 0xAAAAU; // Оновлення незалежного сторожового таймера
    #endif
}

// ── Публічне API рушія ініціалізації ──

void init_engine_start(init_engine_t *eng, const init_step_t *steps, size_t count, void *ctx) {
    dwt_timer_init();
    eng->steps = steps;
    eng->total_steps = count;
    eng->current_index = 0;
    eng->phase = STEP_PHASE_ACTION;
    eng->phase_start_ticks = dwt_get_cycles();
    eng->poll_start_ticks = 0;
    eng->user_context = ctx;
    eng->status = (count > 0) ? INIT_ENGINE_RUNNING : INIT_ENGINE_SUCCESS;
    eng->failed_step_mask = 0;
}

init_engine_status_t init_engine_poll(init_engine_t *eng) {
    if (eng->status != INIT_ENGINE_RUNNING) {
        return eng->status;
    }

    watchdog_feed(); // Регулярне скидання вартівника без блокування

    if (eng->current_index >= eng->total_steps) {
        eng->status = (eng->failed_step_mask == 0) ? INIT_ENGINE_SUCCESS : INIT_ENGINE_DEGRADED;
        return eng->status;
    }

    const init_step_t *step = &eng->steps[eng->current_index];
    uint32_t now = dwt_get_cycles();

    switch (eng->phase) {
        case STEP_PHASE_ACTION: {
            if (step->action != NULL) {
                if (!step->action(eng->user_context)) {
                    // Апаратна дія повернула помилку: виклик відкату
                    if (step->rollback != NULL) {
                        step->rollback(eng->user_context);
                    }
                    eng->failed_step_mask |= (1U << eng->current_index);
                    if (step->is_critical) {
                        eng->status = INIT_ENGINE_FAILED;
                        return eng->status;
                    }
                    // Некритичний крок — перехід до наступного етапу
                    eng->current_index++;
                    eng->phase = STEP_PHASE_ACTION;
                    return eng->status;
                }
            }
            eng->phase_start_ticks = now;
            eng->phase = STEP_PHASE_HOLD_DELAY;
            break;
        }

        case STEP_PHASE_HOLD_DELAY: {
            uint32_t delay_ticks = us_to_dwt_ticks(step->hold_delay_us);
            if ((now - eng->phase_start_ticks) >= delay_ticks) {
                if (step->poll_condition != NULL) {
                    eng->poll_start_ticks = now;
                    eng->phase = STEP_PHASE_POLLING;
                } else {
                    // Фіксована витримка завершена, перевірка не потрібна
                    eng->current_index++;
                    eng->phase = STEP_PHASE_ACTION;
                }
            }
            break;
        }

        case STEP_PHASE_POLLING: {
            if (step->poll_condition(eng->user_context)) {
                // Умова готовності підтверджена
                eng->current_index++;
                eng->phase = STEP_PHASE_ACTION;
            } else {
                uint32_t timeout_ticks = us_to_dwt_ticks(step->timeout_us);
                if ((now - eng->poll_start_ticks) >= timeout_ticks) {
                    // Вичерпано таймаут очікування
                    if (step->rollback != NULL) {
                        step->rollback(eng->user_context);
                    }
                    eng->failed_step_mask |= (1U << eng->current_index);
                    if (step->is_critical) {
                        eng->status = INIT_ENGINE_FAILED;
                        return eng->status;
                    }
                    // Некритичний збій — продовження роботи у деградованому режимі
                    eng->current_index++;
                    eng->phase = STEP_PHASE_ACTION;
                }
            }
            break;
        }
    }

    return eng->status;
}

// ── Реалізація практичного сценарію ініціалізації плати ──

typedef struct {
    bool psu_good;
    bool i2c_bus_recovered;
    bool imu_online;
    bool flash_online;
} board_system_ctx_t;

// Крок 1: Увімкнення стабілізатора живлення 3.3V
static bool act_power_rail_on(void *ctx) {
    (void)ctx;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOCEN;
    GPIOC->BSRR = GPIO_BSRR_BS13; // Високий рівень на ключ Enable
    GPIOC->MODER = (GPIOC->MODER & ~GPIO_MODER_MODER13_Msk) | (1U << GPIO_MODER_MODER13_Pos);
    return true;
}

static bool poll_power_rail_ready(void *ctx) {
    board_system_ctx_t *board = (board_system_ctx_t *)ctx;
    board->psu_good = true;
    return true;
}

static void rb_power_rail_fault(void *ctx) {
    (void)ctx;
    GPIOC->BSRR = GPIO_BSRR_BR13; // Аварійне зняття живлення
}

// Крок 2: Розблокування шини I2C (Bus Recovery)
static bool act_i2c_bus_recovery(void *ctx) {
    (void)ctx;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;
    // Налаштування PB8 (SCL) та PB9 (SDA) як виходи Open Drain
    GPIOB->MODER = (GPIOB->MODER & ~(GPIO_MODER_MODER8_Msk | GPIO_MODER_MODER9_Msk)) |
                   (1U << GPIO_MODER_MODER8_Pos) | (1U << GPIO_MODER_MODER9_Pos);
    GPIOB->OTYPER |= GPIO_OTYPER_OT_8 | GPIO_OTYPER_OT_9;
    GPIOB->BSRR = GPIO_BSRR_BS8 | GPIO_BSRR_BS9;

    // Генерація 9 імпульсів для звільнення лінії SDA
    for (int i = 0; i < 9; i++) {
        GPIOB->BSRR = GPIO_BSRR_BR8; // SCL = 0
        for (volatile int d = 0; d < 50; d++) __NOP();
        GPIOB->BSRR = GPIO_BSRR_BS8; // SCL = 1
        for (volatile int d = 0; d < 50; d++) __NOP();
    }
    return true;
}

static bool poll_i2c_bus_free(void *ctx) {
    board_system_ctx_t *board = (board_system_ctx_t *)ctx;
    bool sda_high = (GPIOB->IDR & GPIO_IDR_IDR_9) != 0;
    board->i2c_bus_recovered = sda_high;
    return sda_high;
}

static void rb_i2c_fault(void *ctx) {
    board_system_ctx_t *board = (board_system_ctx_t *)ctx;
    board->i2c_bus_recovered = false;
}

// Крок 3: Апаратне скидання акселерометра IMU
static bool act_imu_reset_pulse(void *ctx) {
    (void)ctx;
    GPIOC->BSRR = GPIO_BSRR_BR4; // nRST = LOW
    GPIOC->MODER = (GPIOC->MODER & ~GPIO_MODER_MODER4_Msk) | (1U << GPIO_MODER_MODER4_Pos);
    return true;
}

static bool act_imu_release_reset(void *ctx) {
    (void)ctx;
    GPIOC->BSRR = GPIO_BSRR_BS4; // nRST = HIGH (Release)
    return true;
}

static bool poll_imu_whoami(void *ctx) {
    board_system_ctx_t *board = (board_system_ctx_t *)ctx;
    // Імітація обміну по SPI: перевірка відповіді 0x75
    board->imu_online = true;
    return true;
}

static void rb_imu_isolate(void *ctx) {
    board_system_ctx_t *board = (board_system_ctx_t *)ctx;
    board->imu_online = false;
    // Переведення виводів датчика у високий опір
    GPIOC->MODER &= ~GPIO_MODER_MODER4_Msk;
}

// Таблиця конфігурації етапів ініціалізації обладнання
static const init_step_t g_system_init_sequence[] = {
    {
        .name = "POWER_RAIL_3V3_ENABLE",
        .action = act_power_rail_on,
        .hold_delay_us = 10000U, // 10 мс на наростання напруги V_DD
        .poll_condition = poll_power_rail_ready,
        .timeout_us = 5000U,
        .rollback = rb_power_rail_fault,
        .is_critical = true
    },
    {
        .name = "I2C_BUS_RECOVERY",
        .action = act_i2c_bus_recovery,
        .hold_delay_us = 2000U,  // 2 мс стабілізації ліній
        .poll_condition = poll_i2c_bus_free,
        .timeout_us = 3000U,
        .rollback = rb_i2c_fault,
        .is_critical = false
    },
    {
        .name = "IMU_ASSERT_RESET",
        .action = act_imu_reset_pulse,
        .hold_delay_us = 15000U, // 15 мс утримання апаратного скидання
        .poll_condition = NULL,
        .timeout_us = 0,
        .rollback = NULL,
        .is_critical = false
    },
    {
        .name = "IMU_BOOT_AND_PROBE",
        .action = act_imu_release_reset,
        .hold_delay_us = 25000U, // 25 мс очікування завантаження ROM чипа
        .poll_condition = poll_imu_whoami,
        .timeout_us = 10000U,
        .rollback = rb_imu_isolate,
        .is_critical = false
    }
};

void run_c99_bringup_task(void) {
    board_system_ctx_t board_state = {0};
    init_engine_t engine;

    init_engine_start(&engine, g_system_init_sequence,
                      sizeof(g_system_init_sequence) / sizeof(g_system_init_sequence[0]),
                      &board_state);

    while (init_engine_poll(&engine) == INIT_ENGINE_RUNNING) {
        // Фонова робота: миготіння світлодіодом, очікування подій
        __NOP();
    }

    if (engine.status == INIT_ENGINE_SUCCESS) {
        // Усі вузли готові до штатної роботи
    } else if (engine.status == INIT_ENGINE_DEGRADED) {
        // Запуск приладу з відключеними другорядними сенсорами
    } else {
        // Аварійна зупинка: критичний збій живлення
    }
}
```
```cpp
#include <cstdint>
#include <concepts>
#include <chrono>
#include <expected>
#include <span>
#include <string_view>
#include <functional>
#include <array>
#include "stm32f4xx.h"

namespace hal::init {

using namespace std::chrono_literals;

enum class EngineStatus : uint8_t {
    Running,
    Success,
    Failed,
    Degraded
};

enum class StepError : uint8_t {
    ActionFailed,
    TimeoutExpired,
    HardwareFault
};

template <typename Context>
struct StepDescriptor {
    std::string_view name;
    std::function<std::expected<void, StepError>(Context&)> action{nullptr};
    std::chrono::microseconds hold_delay{0us};
    std::function<bool(Context&)> poll_condition{nullptr};
    std::chrono::microseconds timeout{0us};
    std::function<void(Context&)> rollback{nullptr};
    bool is_critical{true};
};

class DwtClock {
public:
    static void init() noexcept {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    }

    [[nodiscard]] static uint32_t cycles() noexcept {
        return DWT->CYCCNT;
    }

    template <typename Rep, typename Period>
    [[nodiscard]] static uint32_t to_cycles(std::chrono::duration<Rep, Period> duration) noexcept {
        const auto us = std::chrono::duration_cast<std::chrono::microseconds>(duration).count();
        return static_cast<uint32_t>(us) * (SystemCoreClock / 1'000'000U);
    }
};

template <typename Context>
class SequenceEngine {
public:
    explicit SequenceEngine(Context& context, std::span<const StepDescriptor<Context>> steps) noexcept
        : context_(context), steps_(steps), current_index_(0), status_(EngineStatus::Running) {
        DwtClock::init();
        phase_start_cycles_ = DwtClock::cycles();
    }

    [[nodiscard]] EngineStatus poll() noexcept {
        if (status_ != EngineStatus::Running) {
            return status_;
        }

        feed_watchdog();

        if (current_index_ >= steps_.size()) {
            status_ = (failed_mask_ == 0) ? EngineStatus::Success : EngineStatus::Degraded;
            return status_;
        }

        const auto& step = steps_[current_index_];
        const uint32_t now = DwtClock::cycles();

        switch (phase_) {
            case Phase::ExecuteAction: {
                if (step.action) {
                    auto result = step.action(context_);
                    if (!result.has_value()) {
                        handle_step_failure(step);
                        return status_;
                    }
                }
                phase_start_cycles_ = now;
                phase_ = Phase::WaitHoldDelay;
                break;
            }

            case Phase::WaitHoldDelay: {
                const uint32_t delay_ticks = DwtClock::to_cycles(step.hold_delay);
                if ((now - phase_start_cycles_) >= delay_ticks) {
                    if (step.poll_condition) {
                        poll_start_cycles_ = now;
                        phase_ = Phase::PollCondition;
                    } else {
                        advance_next_step();
                    }
                }
                break;
            }

            case Phase::PollCondition: {
                if (step.poll_condition(context_)) {
                    advance_next_step();
                } else {
                    const uint32_t timeout_ticks = DwtClock::to_cycles(step.timeout);
                    if ((now - poll_start_cycles_) >= timeout_ticks) {
                        handle_step_failure(step);
                    }
                }
                break;
            }
        }

        return status_;
    }

    [[nodiscard]] uint32_t failed_mask() const noexcept { return failed_mask_; }

private:
    enum class Phase : uint8_t {
        ExecuteAction,
        WaitHoldDelay,
        PollCondition
    };

    Context& context_;
    std::span<const StepDescriptor<Context>> steps_;
    size_t current_index_{0};
    Phase phase_{Phase::ExecuteAction};
    uint32_t phase_start_cycles_{0};
    uint32_t poll_start_cycles_{0};
    uint32_t failed_mask_{0};
    EngineStatus status_{EngineStatus::Running};

    static void feed_watchdog() noexcept {
        #if defined(IWDG)
        IWDG->KR = 0xAAAAU;
        #endif
    }

    void advance_next_step() noexcept {
        current_index_++;
        phase_ = Phase::ExecuteAction;
    }

    void handle_step_failure(const StepDescriptor<Context>& step) noexcept {
        if (step.rollback) {
            step.rollback(context_);
        }
        failed_mask_ |= (1U << current_index_);
        if (step.is_critical) {
            status_ = EngineStatus::Failed;
        } else {
            advance_next_step();
        }
    }
};

// ── Приклад декларативного конфігурування на C++20 ──

struct FlightControllerContext {
    bool power_good{false};
    bool i2c_recovered{false};
    bool imu_ready{false};
    bool barometer_ready{false};
};

inline const std::array<StepDescriptor<FlightControllerContext>, 4> g_flight_steps{{
    {
        .name = "POWER_RAIL_STABILIZE",
        .action = [](FlightControllerContext& ctx) -> std::expected<void, StepError> {
            RCC->AHB1ENR |= RCC_AHB1ENR_GPIOCEN;
            GPIOC->BSRR = GPIO_BSRR_BS13; // Power ON
            GPIOC->MODER = (GPIOC->MODER & ~GPIO_MODER_MODER13_Msk) | (1U << GPIO_MODER_MODER13_Pos);
            ctx.power_good = true;
            return {};
        },
        .hold_delay = 12'000us,
        .poll_condition = [](FlightControllerContext& ctx) noexcept { return ctx.power_good; },
        .timeout = 5'000us,
        .rollback = [](FlightControllerContext& ctx) noexcept {
            GPIOC->BSRR = GPIO_BSRR_BR13;
            ctx.power_good = false;
        },
        .is_critical = true
    },
    {
        .name = "I2C_BUS_CLOCK_CLEANUP",
        .action = [](FlightControllerContext&) -> std::expected<void, StepError> {
            RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;
            GPIOB->MODER |= (1U << GPIO_MODER_MODER8_Pos);
            for (int i = 0; i < 9; ++i) {
                GPIOB->BSRR = GPIO_BSRR_BR8;
                for (volatile int d = 0; d < 40; ++d) __NOP();
                GPIOB->BSRR = GPIO_BSRR_BS8;
                for (volatile int d = 0; d < 40; ++d) __NOP();
            }
            return {};
        },
        .hold_delay = 2'000us,
        .poll_condition = [](FlightControllerContext& ctx) noexcept {
            ctx.i2c_recovered = true;
            return true;
        },
        .timeout = 3'000us,
        .rollback = [](FlightControllerContext& ctx) noexcept { ctx.i2c_recovered = false; },
        .is_critical = false
    },
    {
        .name = "IMU_HARDWARE_RESET_CYCLE",
        .action = [](FlightControllerContext&) -> std::expected<void, StepError> {
            GPIOC->BSRR = GPIO_BSRR_BR4; // Assert nRST
            return {};
        },
        .hold_delay = 15'000us,
        .poll_condition = nullptr,
        .timeout = 0us,
        .rollback = nullptr,
        .is_critical = false
    },
    {
        .name = "IMU_BOOT_AND_VALIDATE",
        .action = [](FlightControllerContext&) -> std::expected<void, StepError> {
            GPIOC->BSRR = GPIO_BSRR_BS4; // Release nRST
            return {};
        },
        .hold_delay = 25'000us,
        .poll_condition = [](FlightControllerContext& ctx) noexcept {
            ctx.imu_ready = true;
            return true;
        },
        .timeout = 10'000us,
        .rollback = [](FlightControllerContext& ctx) noexcept { ctx.imu_ready = false; },
        .is_critical = true // Для польотного контролера IMU є критичним
    }
}};

void run_cpp_bringup_example() {
    FlightControllerContext context;
    SequenceEngine<FlightControllerContext> engine(context, g_flight_steps);

    while (engine.poll() == EngineStatus::Running) {
        // Неблокувальний цикл диспетчера
    }

    if (engine.poll() == EngineStatus::Success) {
        // Усі датчики готові до навігаційного циклу
    }
}

} // namespace hal::init
```
:::

## Інженерні рекомендації щодо застосування диспетчера

Застосування покрокового диспетчера ініціалізації кардинально змінює процес налагодження та супроводу вбудованих приладів на всіх стадіях життєвого циклу:

1. **Єдина точка зміни фізичних констант.** Усі часові параметри перехідних процесів зафіксовані у єдиній конфігураційній таблиці. При заміні ревізії кремнію або переході на інший тип стабілізатора напруги інженер коригує лише відповідне поле `hold_delay` без необхідності пошуку прихованих викликів `delay` у глибинах вихідного коду драйверів.
2. **Точна телеметрія та раннє виявлення деградації.** Зберігаючи фактичний час очікування апаратних прапорців у пам'яті RTC Backup RAM, прошивка фіксує динаміку старіння компонентів. Якщо час запуску кварцового резонатора або стабілізатора напруги поступово зростає від 2 мс до 15 мс, система може завчасно попередити оператора про необхідність профілактичного обслуговування (Predictive Maintenance) до настання раптової повної відмови.
3. **Безпечна поведінка в аварійних режимах.** Завдяки явному визначенню функцій `rollback` для кожного кроку, невдача ініціалізації сенсора не залишає його виводи під напругою, запобігаючи паразитному живленню через захисні діоди (Phantom Powering) та витокам струму в режимах глибокого сну.
4. **Повна сумісність з автоматизованим тестуванням (HIL Testing).** Таблична структура дозволяє легко підміняти апаратні покажчики дій на програмні макети (Mocks) або інжектувати штучні таймаути в окремі етапи для перевірки реакції системи на аварії без необхідності фізичного пошкодження компонентів на стенді.
5. **Масштабованість на багатоплатформні проекти.** Однаковий інтерфейс таблиць кроків дозволяє переносити логіку послідовності запуску між різними сімействами мікроконтролерів (STM32, ESP32, NXP LPC, RP2040), замінюючи лише низькорівневі маніпуляції з регістрами в окремих функціях дій `action`.
