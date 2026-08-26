# Автомат станів і черга подій у системі пристроїв

<preknowlist>
- [Шарова архітектура](root:sf-apps/layered-architecture) — поділ системи на ізольовані горизонтальні рівні з односпрямованим потоком керування.
- [Кільцевий буфер](root:sf-algorithms/ring-buffer) — статична безблокуюча структура даних FIFO без динамічного виділення пам'яті.
- [Виклик проти повідомлення](root:embedded/vyklyk-proty-povidomlennia) — принципова різниця між синхронним блокуючим RPC-викликом та асинхронним обміном повідомленнями.
- [Критична секція](root:embedded/krytychna-sektsiia) — захист спільних структур даних від перегонів між перериваннями та основним циклом виконання.
</preknowlist>

Коли автономний польовий контролер керує лише одним світлодіодом і кнопкою, його логіка вміщується у десяток рядків лінійного коду. Але щойно пристрій виходить у реальний світ, кількість одночасних процесів зростає: треба періодично опитувати сенсори по шині I²C, тримати TCP-з'єднання через стільниковий модем, реагувати на команди користувача, слідкувати за напругою літієвого акумулятора, записувати телеметрію у флешпам'ять та безпечно знеструмлювати силові кола при аварії.

Перша інтуїтивна спроба зв'язати ці асинхронні процеси в єдину прошивку виглядає як набір булевих прапорців у глобальній пам'яті: `is_connected`, `is_measuring`, `has_data`, `is_low_battery`, `in_fault`. Через кілька місяців розробки такий код неминуче перетворюється на заплутані хащі вкладених умовних операторів, де кожен обробник переривання змінює окремий прапорець, а головний цикл намагається вгадати, що саме зараз відбувається з апаратом. Пристрій починає зависати в непередбачуваних проміжних станах, які виникають раз на тиждень у польових умовах і ніколи не відтворюються на столі налагодження під JTAG-адаптером.

## Проблема хаосу станів та обмеження простих FSM

Головна вада керування логікою через незалежні змінні-прапорці полягає у математичній природі комбінаторики. Кожен новий булевий прапорець, доданий у структуру стану пристрою, подвоює розмір теоретичного простору станів системи. Для пристрою, що має `N` незалежних булевих прапорців, загальна кількість можливих конфігурацій пам'яті описується співвідношенням:

```
S = 2ⁿ      [комбінаторний простір станів для n незалежних булевих прапорців]
```

Якщо система використовує 4 прапорці, процесор може опинитися у 16 станах. Якщо ж прапорців стає 10 (що є типовим для будь-якого промислового трекера чи контролера доступу), кількість можливих комбінацій сягає 1024:

```
S = 2¹⁰
  = 1024    [розмір простору станів при 10 прапорцях]
```

У реальній фізичній роботі пристрою зі всієї цієї тисячі комбінацій змістовними є лише 15–20 режимів. Решта 98% — це заборонені, суперечливі або фізично руйнівні поєднання. Наприклад, стан, де одночасно `is_connected == true` та `is_sleeping == true`, або де `in_fault == true` під час активного калібрування сенсорів `is_calibrating == true`.

Коли стан системи «розмазаний» по окремих прапорцях, компілятор та процесор нічого не знають про ці заборонені комбінації. Відповідальність за фільтрацію покладається на плечі програміста, через що кожна функція прошивки обростає громіздкими багатоповерховими перевірками:

:::tabs
```c
// Типовий приклад логіки на прапорцях: хаос умовних переходів
void process_telemetry(void) {
    if (is_connected && !is_low_power && !has_fault) {
        if (has_sensor_data) {
            send_packet();
            has_sensor_data = false;
        } else if (!is_measuring) {
            start_measurement();
            is_measuring = true;
        }
    } else if (has_fault && is_connected) {
        send_error_beacon();
        // Що робити, якщо під час відправки аварії зникне зв'язок?
    } else if (!is_connected && is_measuring) {
        // Небезпечний проміжний стан: зв'язок втрачено під час вимірювання
        abort_measurement();
        is_measuring = false;
    }
}
```
```cpp
// Еквівалент на C++: та сама комбінаторна крихкість умовних конструкцій
void process_telemetry() {
    if (is_connected && !is_low_power && !has_fault) {
        if (has_sensor_data) {
            send_packet();
            has_sensor_data = false;
        } else if (!is_measuring) {
            start_measurement();
            is_measuring = true;
        }
    } else if (has_fault && is_connected) {
        send_error_beacon();
    } else if (!is_connected && is_measuring) {
        abort_measurement();
        is_measuring = false;
    }
}
```
:::

Цей ефект у теорії надійності вбудованих систем називають **комбінаторним вибухом станів** (англ. *state explosion*). Його головна руйнівна сила — утворення **прихованих станів** (англ. *implicit states*).

Уявімо типову польову ситуацію: пристрій виконує збір даних по шині I²C з активним прапорцем `is_measuring = true`. Раптово напруга живлення короткочасно просідає через увімкнення зовнішнього реле, і стільниковий модем перезавантажується. Переривання від UART скидає прапорець `is_connected = false`. Якщо розробник забув додати окрему перевірку комбінації `!is_connected && is_measuring` у кожному місці прошивки, функція `process_telemetry()` більше ніколи не зайде в гілку відправки телеметрії й водночас не зможе перезапустити цикл опитування сенсорів, бо вважає, що вимір усе ще триває. Контролер перетворюється на «зомбі»: процесор працює, переривання клацають, але логіка назавжди зависла в мертвій точці.

Окрім логічної плутанини, прапорці створюють апаратні гонки пам'яті (англ. *race conditions*). На 32-бітних процесорах ARM Cortex-M операція читання-модифікації-запису над окремим байтом або бітовим полем не є атомарною. Якщо основний цикл зчитує `is_connected` у регістр `R0`, а в цей момент переривання UART змінює сусідній прапорець `is_transmitting`, зворотний запис `R0` в пам'ять затирає щойно встановлене значення переривання.

![Комбінаторний вибух прапорців проти явного детермінованого автомата](/root/course/embedded/avtomat-staniv-i-cherha-podii-u-systemi/img/state-explosion.svg)
*Зліва: незалежні прапорці плодять неявні стани та заплутані умовні оператори, де важко передбачити суперечності. Справа: скінченний автомат у кожен момент часу перебуває строго в одному явному стані з фіксованого переліку.*

Фундаментальним інженерним рішенням цієї проблеми є перехід до концепції **скінченного автомата** (англ. *Finite State Machine*, FSM; від латин. *finitus* — визначений, обмежений та грец. *automatos* — саморухомий).

У скінченному автоматі весь поточний стан системи згортається в єдину дискретну величину з фіксованого переліку `enum`. Система позбавляється неявних проміжних комбінацій: вона перебуває строго в одному стані в кожен момент часу. Усі зміни відбуваються виключно як реакція на дискретні події:

:::tabs
```c
typedef enum {
    STATE_OFFLINE,
    STATE_CONNECTING,
    STATE_ONLINE,
    STATE_MEASURING,
    STATE_FAULT
} device_state_t;

typedef enum {
    EVT_TIMER_WAKE,
    EVT_NET_CONNECTED,
    EVT_NET_ERROR,
    EVT_START_POLL,
    EVT_DATA_READY,
    EVT_RESET
} device_event_t;

static device_state_t current_state = STATE_OFFLINE;

void fsm_dispatch(device_event_t evt) {
    switch (current_state) {
        case STATE_OFFLINE:
            if (evt == EVT_TIMER_WAKE) {
                modem_power_on();
                current_state = STATE_CONNECTING;
            }
            break;

        case STATE_CONNECTING:
            if (evt == EVT_NET_CONNECTED) {
                current_state = STATE_ONLINE;
            } else if (evt == EVT_NET_ERROR) {
                current_state = STATE_FAULT;
            }
            break;

        case STATE_ONLINE:
            if (evt == EVT_START_POLL) {
                sensor_trigger();
                current_state = STATE_MEASURING;
            }
            break;

        case STATE_MEASURING:
            if (evt == EVT_DATA_READY) {
                telemetry_send();
                current_state = STATE_ONLINE;
            }
            break;

        case STATE_FAULT:
            if (evt == EVT_RESET) {
                system_reboot();
            }
            break;
    }
}
```
```cpp
enum class DeviceState : uint8_t {
    Offline,
    Connecting,
    Online,
    Measuring,
    Fault
};

enum class DeviceEvent : uint8_t {
    TimerWake,
    NetConnected,
    NetError,
    StartPoll,
    DataReady,
    Reset
};

class FlatFsm {
public:
    void dispatch(DeviceEvent evt) {
        switch (state_) {
            case DeviceState::Offline:
                if (evt == DeviceEvent::TimerWake) {
                    modem_power_on();
                    state_ = DeviceState::Connecting;
                }
                break;

            case DeviceState::Connecting:
                if (evt == DeviceEvent::NetConnected) {
                    state_ = DeviceState::Online;
                } else if (evt == DeviceEvent::NetError) {
                    state_ = DeviceState::Fault;
                }
                break;

            case DeviceState::Online:
                if (evt == DeviceEvent::StartPoll) {
                    sensor_trigger();
                    state_ = DeviceState::Measuring;
                }
                break;

            case DeviceState::Measuring:
                if (evt == DeviceEvent::DataReady) {
                    telemetry_send();
                    state_ = DeviceState::Online;
                }
                break;

            case DeviceState::Fault:
                if (evt == DeviceEvent::Reset) {
                    system_reboot();
                }
                break;
        }
    }

private:
    DeviceState state_{DeviceState::Offline};
};
```
:::

Плаский скінченний автомат гарантує, що пристрій не може одночасно перебувати в стані `STATE_OFFLINE` та `STATE_ONLINE`. Змінна стану однозначно визначає поведінку всієї системи.

В теорії автоматів розрізняють два класи таких машин:
- **Автомат Мура** (англ. *Moore machine*): вихідні сигнали та дії залежать виключно від поточного стану системи.
- **Автомат Мілі** (англ. *Mealy machine*): вихідні дії залежать як від поточного стану, так і від вхідної події, що викликала перехід.

У вбудованих системах чисті автомати Мура та Мілі мають суттєві обмеження. У міру зростання функціональності прошивки класичні пласкі автомати розбиваються об іншу стіну складності — **вибух переходів** (англ. *transition explosion*).

Уявімо, що в систему з 15 станами додаються три глобальні події аварійного характеру:
1. `EVT_LOW_BATTERY` — напруга акумулятора впала нижче 3.1 В (необхідно терміново вимкнути всі споживачі струму та заснути).
2. `EVT_EMERGENCY_STOP` — натиснуто апаратну кнопку аварійної зупинки.
3. `EVT_WATCHDOG_ALERT` — підсистема моніторингу зафіксувала збій зв'язку.

Оскільки подія `EVT_LOW_BATTERY` може статися в будь-який момент часу (під час вимірювання, передачі даних, очікування відповіді сервера, калібрування), розробник змушений вручну додати обробку `case EVT_LOW_BATTERY:` у кожен із 15 станів:

```
T = N_states · M_events     [розмір повної матриці переходів плаского автомата]
```

Для 15 станів і 10 подій матриця переходів містить 150 потенційних стрілок. Якщо під час рефакторингу з'являється 16-й стан, і програміст забуде прописати в ньому обробку аварійного живлення, пристрій при розряді батареї зависне саме в цьому стані й висадить літієвий елемент нижче допустимої межі глибокого розряду.

Плаский автомат принципово не має механізму **успадкування поведінки**: кожен стан ізольований і змушений заново описувати реакцію на загальні системні події.

> 🔧 **Навіщо це.** Спроба обійти дублювання коду в плаських автоматах через «зовнішній фільтр» на кшталт `if (evt == EVT_LOW_BATTERY) { state = STATE_OFFLINE; } else { fsm_dispatch(evt); }` створює ще небезпечніший дефект — порушення інваріантів очищення. Якщо система перебувала в стані `STATE_MEASURING` і ми примусово перезаписали `state = STATE_OFFLINE`, ніхто не вимкнув опорну напругу АЦП і не знеструмив аналогові підсилювачі. Як наслідок, у «сплячому» режимі плата продовжує споживати 15 мА замість 15 мкА, і батарея сідає за дві доби.

## Математика та семантика ієрархічних автоматів (Statecharts / HSM)

Для подолання проблеми повторення переходів у складних системах ізраїльський математик Девід Гарель (David Harel) у 1987 році запропонував математичний формалізм **Statecharts**. Його фундаментальне нововведення полягало у введенні **ієрархії станів** (вкладеності), семантики дій входу/виходу, псевдостанів історії та ортогональних компонентів. Програмну реалізацію цих ідей у вбудованому коді називають **ієрархічним автоматом станів** (англ. *Hierarchical State Machine*, HSM).

В ієрархічному автоматі стани організуються у вигляді орієнтованого дерева. Стан вищого рівня називають **суперстаном** (або композитним станом), а стан, вкладений у нього, — **підстаном** (або листовим станом):

```
RootState (корінь ієрархії)
 ├── FaultState (аварійний режим)
 └── Operational (робочий суперстан)
      ├── Idle (підстан очікування)
      ├── Sampling (підстан збору даних)
      └── Communicating (композитний суперстан зв'язку)
           ├── ModemConnecting (підстан авторизації в мережі)
           └── DataPublishing (підстан передачі пакетів)
```

Головний закон диспетчеризації HSM формулюється так: **вхідна подія спочатку доставляється поточному активному листовому стану. Якщо листовий стан не знає, як обробити цю подію, вона автоматично передається (спливає) до його суперстану, і так далі вгору по дереву ієрархії аж до досягнення кореня.**

Завдяки цьому правилу обробка сигналу `EVT_LOW_BATTERY` записується рівно один раз — у суперстані `Operational`. Усі дочірні стани (`Idle`, `Sampling`, `ModemConnecting`, `DataPublishing`) автоматично успадковують цей перехід без жодного рядка дубльованого коду. Математично кількість необхідних переходів у системі зменшується від квадратичної залежності `O(N · M)` до лінійної `O(N + M)`.

### Вхідні та вихідні дії (Entry / Exit Actions)

Стан у Statecharts є не просто абстрактною міткою на графі переходів, а **контекстом володіння апаратними ресурсами**. Аби гарантувати детермінованість захоплення та вивільнення ресурсів, кожен стан наділяється двома обов'язковими діями життєвого циклу:

1. **Дія входу** (англ. *Entry Action*) — процедура, що викликається автоматично при вході в стан. Її призначення — налаштувати апаратуру, запустити таймери, виділити буфери, увімкнути живлення периферії.
2. **Дія виходу** (англ. *Exit Action*) — процедура, що викликається автоматично перед тим, як стан перестане бути активним. Її призначення — зупинити перетворення, вимкнути передавачі, деініціалізувати DMA, скинути черги.

Ієрархічна природа автоматів накладає суворий топологічний порядок на виконання цих дій під час зміни стану:
- Дії виходу (`Exit`) виконуються **знизу вгору** (від найглибшого поточного підстану вгору до спільного суперстану).
- Дії входу (`Entry`) виконуються **згори вниз** (від спільного суперстану вниз до цільового підстану).

### Внутрішні переходи проти переходів на себе

У семантиці Statecharts розрізняють два типи переходів у межах одного стану:
- **Внутрішній перехід** (англ. *Internal Transition*): стан реагує на подію (наприклад, оновлює лічильник або фільтрує шум), але не змінює поточний стан. При цьому **жодні Exit чи Entry дії не викликаються**. Це зберігає ресурси процесора та не скидає апаратні таймери стану.
- **Перехід на самого себе** (англ. *Self-Transition*, `S → S`): стан явно перезапускається. При цьому рушій примусово викликає `Exit(S)`, виконує дію переходу, і знову викликає `Entry(S)`. Це необхідно для скидання локальних лічильників спроб та повного перезапуску апаратної периферії стану.

### Алгоритм транзакційного переходу через LCA

Коли ієрархічний автомат виконує перехід між двома станами `Source` та `Target`, рушій повинен знайти точку розвороту в дереві ієрархії. Ця точка називається **найменшим спільним предком** (англ. *Lowest Common Ancestor*, LCA; від латин. *antecessor* — попередник).

LCA — це найглибший суперстан у дереві ієрархії, який одночасно є предком як для стану `Source`, так і для стану `Target`.

![Послідовність виконання дій при переході через найменшого спільного предка](/root/course/embedded/avtomat-staniv-i-cherha-podii-u-systemi/img/hsm-lca-transition.svg)
*Транзакційний перехід у HSM: вихідні дії виконуються вгору від листового стану S11 до LCA, після чого виконується дія переходу, а вхідні дії розгортаються вниз від LCA до цільового листового стану S21.*

Повний транзакційний цикл переходу `Source → Target` виконується за строгим шестикроковим протоколом:

```
Крок 1. Обчислення шляху виходу: побудова ланцюга від Source вгору до LCA (не включаючи LCA).
Крок 2. Почерговий виклик Exit-дій для кожного стану на шляху виходу (знизу вгору).
Крок 3. Виконання атомарної дії самого переходу (Transition Action, якщо вона задана).
Крок 4. Обчислення шляху входу: побудова ланцюга від LCA вниз до Target (не включаючи LCA).
Крок 5. Почерговий виклик Entry-дій для кожного стану на шляху входу (згори вниз).
Крок 6. Якщо стан Target є композитним, виконання його початкового переходу за замовчуванням
        (Initial Transition) рекурсивно вниз до досягнення базового листового стану.
```

Цей протокол виключає виникнення неініціалізованих або напіввідкритих апаратних станів. Якщо перехід відбувається з глибини `ModemConnecting` (всередині `Communicating`, всередині `Operational`) у стан `FaultState` (на рівні `RootState`), LCA є сам `RootState`. Автомат послідовно виконає:
1. `Exit(ModemConnecting)` — зупинить очікування відповіді модема.
2. `Exit(Communicating)` — надішле команду апаратного знеструмлення модема.
3. `Exit(Operational)` — вимкне стабілізатор 3.3 В сенсорної шини.
4. `Entry(FaultState)` — увімкне аварійний світлодіод і переведе ядро в безпечний сон.

Жоден крок не може бути пропущений або виконаний у неправильному порядку, навіть якщо аварійний сигнал надійшов асинхронно посеред складного обміну даними.

> 🔧 **Навіщо це.** Без формалізму LCA та Entry/Exit дій у прошивках виникають підступні апаратні конфлікти: наприклад, коли перехід у стан сну викликається безпосередньо з обробника переривання, таймер генерації ШІМ двигуна залишається активним на рівні регістрів мікроконтролера. Силові транзистори інвертора продовжують перебувати у відкритому стані, через що обмотки двигуна перегріваються й горять під час «сну» пристрою. Entry/Exit дії перетворюють коректне вимикання периферії на непорушний інваріант структури програми.

## Принцип Run-to-Completion (RTC) та детермінізм черг подій

Математична коректність ієрархічного автомата базується на моделі виконання **Run-to-Completion** (RTC; від англ. *run to completion* — виконання до повного завершення).

Семантика RTC декларує: **після того як подія вилучена з черги та передана автомату, вона повинна бути оброблена повністю (включаючи всі дії виходу, переходу, входу та початкової ініціалізації), перш ніж рушій почне обробляти будь-яку іншу подію з черги.**

```
Подія e₁ з черги ──► [ Exit(S₁) ──► Action ──► Entry(S₂) ] ──► Фіксація нового стану (S₂)
                                                                       │
Наступна подія e₂ ─────────────────────────────────────────────────────┘
```

Семантику RTC часто хибно сприймають як синхронне блокування процесора, проте між ними є кардинальна різниця:

| Параметр | Блокуючий код (Superloop / Delay) | Подієвий автомат на базі RTC |
|---|---|---|
| **Очікування події** | `while (!flag)` або `delay_ms(100)` | Відсутнє. Обробник миттєво повертає керування |
| **Зміна стану** | У довільній точці всередині вкладеного циклу | Строго в кінці кванту обробки поточної події |
| **Глибина стека** | Росте пропорційно глибині викликів функцій | Повертається до нуля після кожного кроку RTC |
| **Витрати RAM** | Окремий стек на кожен потік (RTOS) | Один єдиний системний стек для всіх автоматів |
| **Гонки пам'яті** | Високий ризик через асинхронний доступ | Повністю відсутні всередині кроку обробки події |

В архітектурі RTC функція стану ніколи не зупиняє ядро процесора в очікуванні відповіді від заліза. Якщо датчику температури потрібно 50 мс для завершення аналого-цифрового перетворення, стан `SamplingState` не викликає функцію затримки. Замість цього він запускає таймер на 50 мс і миттєво повертає керування диспетчеру:

```
[Подія: SIG_TRIGGER] ──► Sampling::Entry ──► timer_start(50ms) ──► Повернення в диспетчер
                                                                           │
                                              (процесор спить або          │
                                               обробляє інші події)        │
                                                                           ▼
[Подія: SIG_TIMEOUT] ◄───────────────────────────────────────────── Таймер спрацював
        │
        └──► Sampling::Handle(SIG_TIMEOUT) ──► Читання регістрів ──► Перехід у Ready
```

### RTC проти витісняльної багатопотоковості RTOS

У класичних операційних системах реального часу (RTOS, наприклад FreeRTOS або Zephyr) для кожного асинхронного завдання створюється окремий потік (`Task`). Кожен потік вимагає виділення власного блоку стека пам'яті (зазвичай від 1 до 4 КБ RAM).

Якщо на мікроконтролері з 32 КБ RAM функціонує 8 потоків, лише на підтримку стеків витрачається половина всієї оперативної пам'яті. Крім того, взаємодія між потоками вимагає використання блокуючих примітивів синхронізації (м'ютексів, бінарних семафорів, моніторів), що відкриває двері для класичних багатопотокових патологій: дедлоків (англ. *deadlocks*), інверсії пріоритетів (англ. *priority inversion*) та гонок даних.

HSM у поєднанні з чергами подій реалізує архітектурний шаблон **активних об'єктів** (англ. *Active Objects* або модель акторів). Кожен активний об'єкт інкапсулює всередині себе ієрархічний автомат і власну подієву чергу. Об'єкти не мають спільного змінного стану й спілкуються виключно асинхронними повідомленнями. Вся система функціонує в єдиному циклі диспетчеризації на одному системному стеку, що дає змогу будувати наднадійні прошивки на мікроконтролерах із мінімальним обсягом оперативної пам'яті.

## Безпечна статична черга подій для мікроконтролера

Фундаментом архітектури Run-to-Completion є **статична черга подій** (англ. *Event Queue*). Черга забезпечує безпечну розв'язку між швидкими апаратними перериваннями (виробниками подій) та автоматом станів (споживачем подій).

В інженерії вбудованих систем діє залізне правило надійності: **повна відмова від динамічного виділення пам'яті (zero `malloc`/`free`) після завершення фази стартової ініціалізації**. Використання динамічної купи на мікроконтролерах неминуче призводить до фрагментації оперативної пам'яті, непередбачуваного часу виконання операцій та фатальних помилок вичерпання пам'яті після місяців безперервної експлуатації.

Подія у подієвій системі представляється як компактна типізована структура фіксованого розміру:

:::tabs
```c
typedef uint16_t signal_t;

typedef struct {
    signal_t sig;       // Числовий ідентифікатор сигналу
    uint16_t len;       // Довжина корисного навантаження в байтах
    union {
        uint32_t u32;   // Скалярний параметр
        int32_t  i32;   // Знакове числове значення
        void    *ptr;   // Вказівник на статичний блок пам'яті
        uint8_t  raw[8];// Масив сирих байтів
    } param;
} event_t;
```
```cpp
enum class Signal : uint16_t;

struct Event {
    Signal   sig{};
    uint16_t len{0};
    union Param {
        uint32_t u32;
        int32_t  i32;
        void*    ptr;
        uint8_t  raw[8];
    } param{};
};
```
:::

Черга подій організовується як кільцевий буфер фіксованої довжини, розташований у статичній секції пам'яті `.bss` або `.data`.

![Диспетчеризація подій через кільцеву чергу в семантиці Run-to-Completion](/root/course/embedded/avtomat-staniv-i-cherha-podii-u-systemi/img/rtc-dispatch-loop.svg)
*Архітектура подій: асинхронні переривання (ISR) та фонові завдання кладуть події у статичний кільцевий буфер, звідки RTC-диспетчер послідовно вилучає їх і транслює в активний стан автомата.*

### Захист на межі переривань: модель MPSC

У реальній прошивці події в чергу надсилають одночасно кілька різних джерел: переривання таймера, переривання UART DMA, зовнішні переривання від кнопок, фонові задачі перевірки живлення (багато виробників — Multiple Producers). Споживачем же є єдиний цикл диспетчеризації автомата (один споживач — Single Consumer). Така топологія називається моделлю **MPSC** (англ. *Multiple-Producer Single-Consumer*).

Оскільки переривання може виникнути в довільний момент часу (зокрема всередині іншого менш пріоритетного переривання під час модифікації покажчиків черги), операція додавання події (`push`) повинна бути атомарною. Для цього на мікроконтролерах із ядром ARM Cortex-M застосовують ультракороткі критичні секції, що блокують глобальні переривання лише на час оновлення індексів (2–3 машинних цикли):

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define EVENT_QUEUE_CAPACITY 32

typedef struct {
    event_t ring[EVENT_QUEUE_CAPACITY];
    uint8_t head;
    uint8_t tail;
    uint8_t count;
    uint8_t max_usage;  // Пікове заповнення черги для діагностики
} event_queue_t;

void event_queue_init(event_queue_t *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->max_usage = 0;
}

// Захист критичної секції для ядер ARM Cortex-M
static inline uint32_t enter_critical(void) {
    uint32_t primask;
    __asm__ volatile (
        "mrs %0, primask\n"
        "cpsid i\n"
        : "=r" (primask) :: "memory"
    );
    return primask;
}

static inline void exit_critical(uint32_t primask) {
    __asm__ volatile (
        "msr primask, %0\n"
        ::: "memory"
    );
}

bool event_queue_push(event_queue_t *q, const event_t *e) {
    uint32_t state = enter_critical();

    if (q->count >= EVENT_QUEUE_CAPACITY) {
        exit_critical(state);
        // Переповнення черги — фатальний дефект таймінгу
        return false;
    }

    q->ring[q->head] = *e;
    q->head = (uint8_t)((q->head + 1) % EVENT_QUEUE_CAPACITY);
    q->count++;

    if (q->count > q->max_usage) {
        q->max_usage = q->count;
    }

    exit_critical(state);
    return true;
}

bool event_queue_pop(event_queue_t *q, event_t *out_e) {
    uint32_t state = enter_critical();

    if (q->count == 0) {
        exit_critical(state);
        return false;
    }

    *out_e = q->ring[q->tail];
    q->tail = (uint8_t)((q->tail + 1) % EVENT_QUEUE_CAPACITY);
    q->count--;

    exit_critical(state);
    return true;
}
```
```cpp
#include <cstdint>
#include <array>
#include <optional>

template <typename EventType, size_t Capacity>
class StaticEventQueue {
public:
    StaticEventQueue() : head_{0}, tail_{0}, count_{0}, max_usage_{0} {}

    bool push(const EventType& e) {
        CriticalSectionGuard guard;
        if (count_ >= Capacity) {
            return false;
        }

        ring_[head_] = e;
        head_ = (head_ + 1) % Capacity;
        ++count_;

        if (count_ > max_usage_) {
            max_usage_ = count_;
        }
        return true;
    }

    std::optional<EventType> pop() {
        CriticalSectionGuard guard;
        if (count_ == 0) {
            return std::nullopt;
        }

        EventType e = ring_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        --count_;
        return e;
    }

    [[nodiscard]] size_t max_usage() const {
        CriticalSectionGuard guard;
        return max_usage_;
    }

private:
    struct CriticalSectionGuard {
        uint32_t primask_;
        CriticalSectionGuard() {
            __asm__ volatile (
                "mrs %0, primask\n"
                "cpsid i\n"
                : "=r" (primask_) :: "memory"
            );
        }
        ~CriticalSectionGuard() {
            __asm__ volatile (
                "msr primask, %0\n"
                ::: "memory"
            );
        }
    };

    std::array<EventType, Capacity> ring_{};
    size_t head_{0};
    size_t tail_{0};
    size_t count_{0};
    size_t max_usage_{0};
};
```
:::

Для передачі великих масивів даних (наприклад, 512-байтових блоків спектрального аналізу вібрації чи буферів Ethernet) передача за значенням через кільцеву чергу є неефективною. У таких сценаріях застосовують **статичні пули пам'яті фіксованого розміру** (англ. *Zero-Copy Static Block Pools*). Виробник виділяє блок із пулу за константний час `O(1)`, записує дані через DMA і передає в чергу подій лише типізований вказівник. Після завершення обробки споживач повертає блок назад у пул.

## Повний компактний рушій HSM на C та C++

Щоб реалізувати ієрархічний автомат на мові C без використання динамічної пам'яті, віртуальних методів компілятора чи зовнішніх важких бібліотек, використовують патерн **вказівників на функції-обробники станів** (англ. *State Handler Function Pointer*).

Кожен стан у системі моделюється як функція зі строго стандартизованою сигнатурою:

:::tabs
```c
typedef enum {
    Q_RET_HANDLED,    // Сигнал успішно оброблено цим станом
    Q_RET_IGNORED,    // Сигнал проігноровано (подальший підйом зупинено)
    Q_RET_TRAN,       // Замовлено транзакційний перехід у новий стан
    Q_RET_SUPER       // Сигнал не оброблено; передати його суперстану
} q_result_t;

typedef struct hsm_tag hsm_t;
typedef q_result_t (*state_handler_t)(hsm_t *me, const event_t *e);
```
```cpp
enum class Result : uint8_t {
    Handled,
    Ignored,
    Transition,
    Super
};

template <typename Derived>
class HierarchicalStateMachine;
```
:::

### Службові сигнали життєвого циклу

Для керування внутрішньою семантикою Statecharts рушій надсилає функціям станів чотири зарезервовані **системні сигнали**:
- `Q_SIG_ENTRY` — надсилається стану в момент його активації для виконання дій входу.
- `Q_SIG_EXIT` — надсилається стану перед виходом для деініціалізації та звільнення ресурсів.
- `Q_SIG_INIT` — надсилається композитному суперстану для запуску його початкового підстану за замовчуванням.
- `Q_SIG_EMPTY` — службовий порожній сигнал, що використовується внутрішнім алгоритмом рушія для опитування батьківського суперстану під час динамічного обчислення LCA.

### Структура та архітектура рушія

Структура `hsm_t` зберігає поточний активний стан системи (`state`) та тимчасовий вказівник (`temp`), який використовується для передачі цільового стану під час переходу:

:::tabs
```c
// hsm_engine.h — Заголовний файл компактного рушія HSM на C
#ifndef HSM_ENGINE_H
#define HSM_ENGINE_H

#include <stdint.h>
#include <stdbool.h>

#define MAX_STATE_DEPTH 8

enum {
    Q_SIG_EMPTY = 0,
    Q_SIG_ENTRY,
    Q_SIG_EXIT,
    Q_SIG_INIT,
    Q_SIG_USER_START = 10
};

typedef uint16_t signal_t;

typedef struct {
    signal_t sig;
    uint32_t param;
} event_t;

typedef enum {
    Q_RET_HANDLED,
    Q_RET_IGNORED,
    Q_RET_TRAN,
    Q_RET_SUPER
} q_result_t;

typedef struct hsm_tag hsm_t;
typedef q_result_t (*state_handler_t)(hsm_t *me, const event_t *e);

struct hsm_tag {
    state_handler_t state;  // Активний листовий стан
    state_handler_t temp;   // Тимчасовий стан під час транзакції
};

#define Q_TRAN(target_)  (((hsm_t *)me)->temp = (state_handler_t)(target_), Q_RET_TRAN)
#define Q_SUPER(super_)  (((hsm_t *)me)->temp = (state_handler_t)(super_), Q_RET_SUPER)
#define Q_HANDLED()      (Q_RET_HANDLED)
#define Q_IGNORED()      (Q_RET_IGNORED)

void hsm_init(hsm_t *me, state_handler_t initial);
void hsm_dispatch(hsm_t *me, const event_t *e);
q_result_t hsm_top_state(hsm_t *me, const event_t *e);

#endif // HSM_ENGINE_H
```
```cpp
// hsm_engine.hpp — Типобезпечний рушій HSM на C++20
#pragma once

#include <cstdint>
#include <array>
#include <utility>

enum class Signal : uint16_t {
    Empty = 0,
    Entry,
    Exit,
    Init,
    UserStart = 10
};

struct Event {
    Signal   sig{Signal::Empty};
    uint32_t param{0};
};

enum class Result : uint8_t {
    Handled,
    Ignored,
    Transition,
    Super
};

template <typename Derived>
class HierarchicalStateMachine {
public:
    using StateHandler = Result (Derived::*)(const Event&);

    void init(StateHandler initial) {
        temp_ = initial;
        Event init_evt{Signal::Init, 0};
        (static_cast<Derived*>(this)->*temp_)(init_evt);
        state_ = temp_;

        Event entry_evt{Signal::Entry, 0};
        (static_cast<Derived*>(this)->*state_)(entry_evt);
    }

    void dispatch(const Event& e) {
        StateHandler s = state_;
        Result res = Result::Super;

        // Спливання події від листового стану вгору по дереву
        while (s != nullptr && res == Result::Super) {
            temp_ = nullptr;
            res = (static_cast<Derived*>(this)->*s)(e);
            if (res == Result::Super) {
                s = temp_; // Отримано батьківський суперстан
            }
        }

        if (res == Result::Transition) {
            execute_transition(temp_);
        }
    }

    Result top_state(const Event&) {
        return Result::Ignored;
    }

protected:
    Result transition(StateHandler target) {
        temp_ = target;
        return Result::Transition;
    }

    Result super_state(StateHandler super_handler) {
        temp_ = super_handler;
        return Result::Super;
    }

    Result handled() { return Result::Handled; }
    Result ignored() { return Result::Ignored; }

private:
    void execute_transition(StateHandler target) {
        static constexpr size_t kMaxDepth = 8;
        std::array<StateHandler, kMaxDepth> exit_path{};
        std::array<StateHandler, kMaxDepth> entry_path{};

        size_t exit_count = 0;
        size_t entry_count = 0;

        StateHandler s = state_;
        StateHandler t = target;

        // 1. Трасування гілки джерела вгору
        StateHandler curr = s;
        while (curr != nullptr && exit_count < kMaxDepth) {
            exit_path[exit_count++] = curr;
            temp_ = nullptr;
            Event empty_evt{Signal::Empty, 0};
            (static_cast<Derived*>(this)->*curr)(empty_evt);
            curr = temp_;
        }

        // 2. Трасування гілки цілі вгору
        curr = t;
        while (curr != nullptr && entry_count < kMaxDepth) {
            entry_path[entry_count++] = curr;
            temp_ = nullptr;
            Event empty_evt{Signal::Empty, 0};
            (static_cast<Derived*>(this)->*curr)(empty_evt);
            curr = temp_;
        }

        // 3. Пошук найменшого спільного предка (LCA)
        size_t lca_src_idx = exit_count;
        size_t lca_dst_idx = entry_count;
        bool found_lca = false;

        for (size_t i = 0; i < exit_count && !found_lca; ++i) {
            for (size_t j = 0; j < entry_count; ++j) {
                if (exit_path[i] == entry_path[j]) {
                    lca_src_idx = i;
                    lca_dst_idx = j;
                    found_lca = true;
                    break;
                }
            }
        }

        // 4. Виконання Exit-дій знизу вгору до LCA
        Event exit_evt{Signal::Exit, 0};
        for (size_t i = 0; i < lca_src_idx; ++i) {
            (static_cast<Derived*>(this)->*exit_path[i])(exit_evt);
        }

        // 5. Виконання Entry-дій згори вниз від LCA до цілі
        Event entry_evt{Signal::Entry, 0};
        if (lca_dst_idx > 0) {
            for (size_t j = lca_dst_idx; j > 0; --j) {
                (static_cast<Derived*>(this)->*entry_path[j - 1])(entry_evt);
            }
        }

        state_ = target;

        // 6. Початковий перехід цільового стану
        Event init_evt{Signal::Init, 0};
        (static_cast<Derived*>(this)->*state_)(init_evt);
    }

    StateHandler state_{nullptr};
    StateHandler temp_{nullptr};
};
```
:::

### Реалізація динамічного обчислення LCA на C

На мові C алгоритм знаходження LCA використовує виклик обробника з подією `Q_SIG_EMPTY`. За цим викликом функція стану повертає макрос `Q_SUPER(parent_handler)`, що дозволяє рушію динамічно пройти вгору по ланцюгу батьків без необхідності виділяти пам'ять під статичні таблиці ієрархії у флешпам'яті:

:::tabs
```c
// hsm_engine.c — Ядро диспетчеризації та обчислення LCA на C
#include "hsm_engine.h"

static const event_t pkg_entry = { Q_SIG_ENTRY, 0 };
static const event_t pkg_exit  = { Q_SIG_EXIT, 0 };
static const event_t pkg_init  = { Q_SIG_INIT, 0 };
static const event_t pkg_empty = { Q_SIG_EMPTY, 0 };

q_result_t hsm_top_state(hsm_t *me, const event_t *e) {
    (void)me;
    (void)e;
    return Q_RET_IGNORED;
}

void hsm_init(hsm_t *me, state_handler_t initial) {
    me->temp = initial;
    (*me->temp)(me, &pkg_init);
    me->state = me->temp;
    (*me->state)(me, &pkg_entry);
}

void hsm_dispatch(hsm_t *me, const event_t *e) {
    state_handler_t s = me->state;
    q_result_t res = Q_RET_SUPER;

    // 1. Спливання події від активного листка до вершини
    while (s != NULL && res == Q_RET_SUPER) {
        me->temp = NULL;
        res = (*s)(me, e);
        if (res == Q_RET_SUPER) {
            s = me->temp; // Перехід до батьківського суперстану
        }
    }

    // 2. Якщо стан повернув запит на перехід — виконуємо транзакцію LCA
    if (res == Q_RET_TRAN) {
        state_handler_t target = me->temp;
        state_handler_t src_path[MAX_STATE_DEPTH];
        state_handler_t dst_path[MAX_STATE_DEPTH];
        uint8_t src_depth = 0;
        uint8_t dst_depth = 0;

        // Побудова ланцюга предків джерела
        state_handler_t curr = me->state;
        while (curr != hsm_top_state && curr != NULL && src_depth < MAX_STATE_DEPTH) {
            src_path[src_depth++] = curr;
            me->temp = NULL;
            (*curr)(me, &pkg_empty);
            curr = me->temp;
        }

        // Побудова ланцюга предків цілі
        curr = target;
        while (curr != hsm_top_state && curr != NULL && dst_depth < MAX_STATE_DEPTH) {
            dst_path[dst_depth++] = curr;
            me->temp = NULL;
            (*curr)(me, &pkg_empty);
            curr = me->temp;
        }

        // Пошук найменшого спільного предка (LCA)
        int8_t lca_src = -1;
        int8_t lca_dst = -1;
        for (int8_t i = 0; i < src_depth; i++) {
            for (int8_t j = 0; j < dst_depth; j++) {
                if (src_path[i] == dst_path[j]) {
                    lca_src = i;
                    lca_dst = j;
                    break;
                }
            }
            if (lca_src >= 0) break;
        }

        // Виклик Exit-дій знизу вгору до знайденого LCA
        int8_t exit_limit = (lca_src >= 0) ? lca_src : src_depth;
        for (int8_t i = 0; i < exit_limit; i++) {
            (*src_path[i])(me, &pkg_exit);
        }

        // Виклик Entry-дій згори вниз від LCA до цільового стану
        int8_t entry_start = (lca_dst >= 0) ? (lca_dst - 1) : (dst_depth - 1);
        for (int8_t j = entry_start; j >= 0; j--) {
            (*dst_path[j])(me, &pkg_entry);
        }

        me->state = target;

        // Виконання початкового переходу цільового стану
        me->temp = NULL;
        if ((*me->state)(me, &pkg_init) == Q_RET_TRAN) {
            state_handler_t leaf = me->temp;
            (*leaf)(me, &pkg_entry);
            me->state = leaf;
        }
    }
}
```
```cpp
// hsm_engine.cpp — Реалізація ядра для C++ версії
#include "hsm_engine.hpp"

// У C++ версії вся логіка реалізована за допомогою шаблону CRTP (Curiously Recurring
// Template Pattern) у файлі hsm_engine.hpp. Це забезпечує прямий виклик методів класу
// без накладних витрат віртуальних таблиць (vtable) і з нульовим динамічним оверхедом.
```
:::

## Практичний приклад: Контролер автономного польового вузла

Аби продемонструвати надійність HSM на практиці, реалізуємо прошивку автономного вимірювального вузла IoT із батарейним живленням.

Архітектура станів пристрою:
1. `RootState` (кореневий суперстан): ловить системні події `SIG_LOW_BATTERY` та аварійні скидання, переводячи всю систему в `FaultState`.
2. `Operational` (робочий суперстан): при вході вмикає стабілізатор живлення сенсорів 3.3 В, при виході — гарантовано вимикає його.
3. `IdleState` (підстан `Operational`): вузол спить і очікує системного таймера або натискання кнопки.
4. `SamplingState` (підстан `Operational`): запускає перетворення АЦП по DMA і збирає пакет вимірів.
5. `Communicating` (композитний суперстан): керує стільниковим зв'язком. При вході вмикає модем, при виході — вимикає його. Містить підстани `ModemConnecting` (реєстрація в мережі) та `DataPublishing` (відправка MQTT-пакета). Якщо на будь-якому етапі зв'язку спливає таймаут `SIG_NET_TIMEOUT`, суперстан `Communicating` автоматично повертає систему в `IdleState`.

![Діаграма станів польового контролера з суперстанами та аварійними переходами](/root/course/embedded/avtomat-staniv-i-cherha-podii-u-systemi/img/system-statechart.svg)
*Діаграма ієрархічного автомата: суперстан Operational об'єднує підстани Idle, Sampling та Communicating. Подія SIG_LOW_BATTERY переводить систему у FaultState з будь-якого стану Operational з гарантованим вимкненням датчиків та радіомодуля.*

:::tabs
```c
// node_fsm.c — Реалізація автомата польового вузла на C
#include "hsm_engine.h"
#include <stdio.h>

enum {
    SIG_TIMER_TICK = Q_SIG_USER_START,
    SIG_DATA_READY,
    SIG_NET_OK,
    SIG_NET_TIMEOUT,
    SIG_LOW_BATTERY,
    SIG_BUTTON_PRESS
};

typedef struct {
    hsm_t super;
    uint32_t battery_mv;
    uint16_t samples[16];
} iot_node_t;

static q_result_t state_root(hsm_t *me, const event_t *e);
static q_result_t state_operational(hsm_t *me, const event_t *e);
static q_result_t state_idle(hsm_t *me, const event_t *e);
static q_result_t state_sampling(hsm_t *me, const event_t *e);
static q_result_t state_communicating(hsm_t *me, const event_t *e);
static q_result_t state_modem_connecting(hsm_t *me, const event_t *e);
static q_result_t state_data_publishing(hsm_t *me, const event_t *e);
static q_result_t state_fault(hsm_t *me, const event_t *e);

// 1. Кореневий стан
static q_result_t state_root(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_INIT:
            return Q_TRAN(state_operational);

        case SIG_LOW_BATTERY:
            printf("[Root] Low battery (%u mV)! Emergency shutdown.\n", (unsigned)e->param);
            return Q_TRAN(state_fault);

        default:
            return Q_SUPER(hsm_top_state);
    }
}

// 2. Суперстан нормальної роботи
static q_result_t state_operational(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[Operational] Entry: Enable 3V3 sensor power rail\n");
            return Q_HANDLED();

        case Q_SIG_EXIT:
            printf("[Operational] Exit: Disable 3V3 rail, ensure radio OFF\n");
            return Q_HANDLED();

        case Q_SIG_INIT:
            return Q_TRAN(state_idle);

        default:
            return Q_SUPER(state_root);
    }
}

// 3. Підстан очікування (Idle)
static q_result_t state_idle(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[Idle] Entry: Arm periodic wakeup timer\n");
            return Q_HANDLED();

        case Q_SIG_EXIT:
            printf("[Idle] Exit: Disarm wakeup timer\n");
            return Q_HANDLED();

        case SIG_TIMER_TICK:
        case SIG_BUTTON_PRESS:
            return Q_TRAN(state_sampling);

        default:
            return Q_SUPER(state_operational);
    }
}

// 4. Підстан збору даних (Sampling)
static q_result_t state_sampling(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[Sampling] Entry: Start ADC conversion over DMA\n");
            return Q_HANDLED();

        case Q_SIG_EXIT:
            printf("[Sampling] Exit: Stop ADC DMA\n");
            return Q_HANDLED();

        case SIG_DATA_READY:
            printf("[Sampling] Acquired %u samples! Transition to Connect\n", (unsigned)e->param);
            return Q_TRAN(state_modem_connecting);

        default:
            return Q_SUPER(state_operational);
    }
}

// 5. Суперстан зв'язку (Communicating)
static q_result_t state_communicating(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[Communicating] Entry: Power on cellular modem\n");
            return Q_HANDLED();

        case Q_SIG_EXIT:
            printf("[Communicating] Exit: Send AT+CPOWD power down to modem\n");
            return Q_HANDLED();

        case SIG_NET_TIMEOUT:
            printf("[Communicating] Network timeout! Return to idle.\n");
            return Q_TRAN(state_idle);

        default:
            return Q_SUPER(state_operational);
    }
}

// 6. Підстан реєстрації в мережі
static q_result_t state_modem_connecting(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[ModemConnecting] Entry: Send AT+CREG? check registration\n");
            return Q_HANDLED();

        case SIG_NET_OK:
            printf("[ModemConnecting] Network registered! Publish telemetry.\n");
            return Q_TRAN(state_data_publishing);

        default:
            return Q_SUPER(state_communicating);
    }
}

// 7. Підстан передачі даних
static q_result_t state_data_publishing(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[DataPublishing] Entry: Publish MQTT telemetry packet\n");
            return Q_HANDLED();

        case SIG_NET_OK:
            printf("[DataPublishing] Telemetry ACK received!\n");
            return Q_TRAN(state_idle);

        default:
            return Q_SUPER(state_communicating);
    }
}

// 8. Аварійний стан
static q_result_t state_fault(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[Fault] Entry: Disconnect relays, write crashlog, sleep.\n");
            return Q_HANDLED();

        default:
            return Q_SUPER(state_root);
    }
}
```
```cpp
// node_fsm.cpp — Реалізація автомата польового вузла на C++
#include "hsm_engine.hpp"
#include <iostream>

enum class NodeSignal : uint16_t {
    TimerTick = static_cast<uint16_t>(Signal::UserStart),
    DataReady,
    NetOk,
    NetTimeout,
    LowBattery,
    ButtonPress
};

class IotNodeController : public HierarchicalStateMachine<IotNodeController> {
public:
    IotNodeController() = default;

    void start() {
        init(&IotNodeController::state_root);
    }

    Result state_root(const Event& e) {
        switch (e.sig) {
            case Signal::Init:
                return transition(&IotNodeController::state_operational);

            default:
                if (static_cast<NodeSignal>(e.sig) == NodeSignal::LowBattery) {
                    std::cout << "[Root] Low battery (" << e.param << " mV)! Emergency.\n";
                    return transition(&IotNodeController::state_fault);
                }
                return super_state(&IotNodeController::top_state);
        }
    }

    Result state_operational(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[Operational] Entry: Enable 3V3 sensor power rail\n";
                return handled();

            case Signal::Exit:
                std::cout << "[Operational] Exit: Disable 3V3 rail, ensure radio OFF\n";
                return handled();

            case Signal::Init:
                return transition(&IotNodeController::state_idle);

            default:
                return super_state(&IotNodeController::state_root);
        }
    }

    Result state_idle(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[Idle] Entry: Arm periodic wakeup timer\n";
                return handled();

            case Signal::Exit:
                std::cout << "[Idle] Exit: Disarm wakeup timer\n";
                return handled();

            default:
                auto sig = static_cast<NodeSignal>(e.sig);
                if (sig == NodeSignal::TimerTick || sig == NodeSignal::ButtonPress) {
                    return transition(&IotNodeController::state_sampling);
                }
                return super_state(&IotNodeController::state_operational);
        }
    }

    Result state_sampling(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[Sampling] Entry: Start ADC conversion over DMA\n";
                return handled();

            case Signal::Exit:
                std::cout << "[Sampling] Exit: Stop ADC DMA\n";
                return handled();

            default:
                if (static_cast<NodeSignal>(e.sig) == NodeSignal::DataReady) {
                    std::cout << "[Sampling] Acquired " << e.param << " samples! Connect.\n";
                    return transition(&IotNodeController::state_modem_connecting);
                }
                return super_state(&IotNodeController::state_operational);
        }
    }

    Result state_communicating(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[Communicating] Entry: Power on cellular modem\n";
                return handled();

            case Signal::Exit:
                std::cout << "[Communicating] Exit: Power down modem\n";
                return handled();

            default:
                if (static_cast<NodeSignal>(e.sig) == NodeSignal::NetTimeout) {
                    std::cout << "[Communicating] Network timeout! Return to idle.\n";
                    return transition(&IotNodeController::state_idle);
                }
                return super_state(&IotNodeController::state_operational);
        }
    }

    Result state_modem_connecting(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[ModemConnecting] Entry: Check network registration\n";
                return handled();

            default:
                if (static_cast<NodeSignal>(e.sig) == NodeSignal::NetOk) {
                    return transition(&IotNodeController::state_data_publishing);
                }
                return super_state(&IotNodeController::state_communicating);
        }
    }

    Result state_data_publishing(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[DataPublishing] Entry: Publish telemetry packet\n";
                return handled();

            default:
                if (static_cast<NodeSignal>(e.sig) == NodeSignal::NetOk) {
                    std::cout << "[DataPublishing] Telemetry ACK received!\n";
                    return transition(&IotNodeController::state_idle);
                }
                return super_state(&IotNodeController::state_communicating);
        }
    }

    Result state_fault(const Event& e) {
        switch (e.sig) {
            case Signal::Entry:
                std::cout << "[Fault] Entry: Disconnect relays, write crashlog.\n";
                return handled();

            default:
                return super_state(&IotNodeController::state_root);
        }
    }
};
```
:::

### Покроковий аналіз виконання та очищення ресурсів

Простежимо роботу тестової програми, яка емулює штатний робочий цикл та раптове аварійне падіння напруги під час підключення модема:

:::tabs
```c
int main(void) {
    iot_node_t node;
    hsm_init((hsm_t *)&node, state_root);

    printf("\n--- Подія 1: Спрацював таймер пробудження ---\n");
    event_t e_wake = { SIG_TIMER_TICK, 0 };
    hsm_dispatch((hsm_t *)&node, &e_wake);

    printf("\n--- Подія 2: АЦП завершив вимірювання ---\n");
    event_t e_adc = { SIG_DATA_READY, 16 };
    hsm_dispatch((hsm_t *)&node, &e_adc);

    printf("\n--- Подія 3: Аварійне падіння напруги під час зв'язку ---\n");
    event_t e_batt = { SIG_LOW_BATTERY, 2800 };
    hsm_dispatch((hsm_t *)&node, &e_batt);

    return 0;
}
```
```cpp
int main() {
    IotNodeController node;
    node.start();

    std::cout << "\n--- Подія 1: Спрацював таймер пробудження ---\n";
    Event e_wake{static_cast<Signal>(NodeSignal::TimerTick), 0};
    node.dispatch(e_wake);

    std::cout << "\n--- Подія 2: АЦП завершив вимірювання ---\n";
    Event e_adc{static_cast<Signal>(NodeSignal::DataReady), 16};
    node.dispatch(e_adc);

    std::cout << "\n--- Подія 3: Аварійне падіння напруги під час зв'язку ---\n";
    Event e_batt{static_cast<Signal>(NodeSignal::LowBattery), 2800};
    node.dispatch(e_batt);

    return 0;
}
```
:::

Лог виконання програми демонструє повну відповідність семантиці Statecharts:

```text
[Operational] Entry: Enable 3V3 sensor power rail
[Idle] Entry: Arm periodic wakeup timer

--- Подія 1: Спрацював таймер пробудження ---
[Idle] Exit: Disarm wakeup timer
[Sampling] Entry: Start ADC conversion over DMA

--- Подія 2: АЦП завершив вимірювання ---
[Sampling] Acquired 16 samples! Transition to Connect
[Sampling] Exit: Stop ADC DMA
[Communicating] Entry: Power on cellular modem
[ModemConnecting] Entry: Send AT+CREG? check network

--- Подія 3: Аварійне падіння напруги під час зв'язку ---
[Root] Low battery (2800 mV)! Emergency shutdown.
[Communicating] Exit: Send AT+CPOWD power down to modem
[Operational] Exit: Disable 3V3 rail, ensure radio OFF
[Fault] Entry: Disconnect relays, write crashlog, sleep.
```

На кроці 3 відбувається вирішальний момент: сигнал аварійного розряду батареї надійшов, коли автомат перебував у листовому стані `ModemConnecting`. Оскільки ані `ModemConnecting`, ані `Communicating`, ані `Operational` не перехопили цей сигнал, він сплив до кореневого суперстану `RootState`.

Рушій визначив, що LCA між `ModemConnecting` та `FaultState` — це сам `RootState`. Відповідно, рушій автоматично виконав вихідні дії:
1. `Exit(Communicating)` — вимкнув радіомодуль.
2. `Exit(Operational)` — знеструмив сенсорну шину.
3. `Entry(FaultState)` — увійшов у режим аварії.

Жоден периферійний блок не залишився ввімкненим, а логіка вимкнення модема та сенсорів не була продубльована в обробнику `ModemConnecting`.

## Типові пастки проєктування подієвих систем

Незважаючи на високу надійність архітектури HSM, при її практичній реалізації у вбудованих системах розробники часто припускаються кількох критичних помилок:

1. **Блокуючі виклики всередині обробника стану**. Найнебезпечніша помилка — використання `delay_ms()` або тривалого очікування прапорця апаратного регістра всередині функції стану. Оскільки автомат підпорядковується семантиці Run-to-Completion, будь-яка затримка блокує всю чергу подій системи. Інші критичні сигнали (наприклад, аварійні кінцевики або скидання сторожового таймера) не зможуть бути оброблені вчасно.
2. **Виконання дій під час замовлення переходу**. Модифікація апаратних регістрів безпосередньо в гілці `case`, яка повертає `Q_TRAN()`, порушує порядок транзакції. Усі дії очищення зобов'язані знаходитися виключно у виклику `Q_SIG_EXIT`, а дії ініціалізації — у `Q_SIG_ENTRY`.
3. **Надмірна глибина дерева станів**. Побудова ієрархій глибиною понад 4–5 рівнів робить поведінку пристрою важкою для аналізу людиною та збільшує витрати стека на трасування шляхів LCA. Якщо складності не уникнути, розбивайте систему на кілька паралельних ортогональних автоматів, що взаємодіють через статичну чергу повідомлень.
4. **Нехтування контролем переповнення черги**. Якщо розмір черги подій вибрано замалим, а частота генерації подій перериваннями перевищує швидкість їх обробки диспетчером, виникає переповнення (англ. *Queue Overflow*). У надійній прошивці факт переповнення обов'язково повинен викликати аварійний запис у журналі помилок ([NVS Crash Log](root:embedded/chorna-skrynka)) для коригування розмірів буферів або оптимізації швидкодії обробників.
5. **Небезпечна стратегія скидання сторожового таймера (Watchdog)**. Фатальний антипатерн — скидати сторожовий таймер (`watchdog_pet()`) усередині апаратного переривання системного таймера (SysTick). Якщо головний цикл диспетчеризації зависне через нескінченний цикл чи дедлок, апаратне переривання таймера продовжить скидати сторожа, маскуючи катастрофу від апаратного скидання. Правильний патерн — **токен життєздатності**: сторожовий таймер скидається лише тоді, коли всі активні автомати в системі успішно підтвердили проходження свого кванту RTC-диспетчеризації.

---
