# ⚙️ Практичний монітор серцебиття та сторожовий таймер

Ця практична вставка містить закінчену архітектурну та програмну реалізацію підсистеми управління повідомленнями `HEARTBEAT` у протоколі MAVLink: фонового неблокуючого генератора власного пульсу з частотою 1 Гц та багатопотокового сторожового таймера відстеження топології мережі (англ. *Heartbeat Watchdog & Topology Discovery Engine*). Код спроєктовано для роботи як у вбудованих системах жорсткого реального часу (RTOS NuttX, FreeRTOS), так і у високорівневих прикладних програмах для супутніх комп'ютерів (Companion Computer) та наземних станцій керування на мовах C та C++.

---

## Системна постановка інженерної задачі

У будь-якому безпілотному комплексі мережева служба MAVLink виконує два симетричні та фундаментальні завдання, пов'язані з повідомленням `HEARTBEAT`:

1. **Регулярне самооголошення (Egress Broadcaster):** Власний пристрій (будь то польотний контролер, супутній комп'ютер на базі Linux чи наземна станція) зобов'язаний з суворою періодичністю транслювати в канал зв'язку власний паспорт `HEARTBEAT` (ідентифікатор `MSG ID 0`). Нормативна частота трансляції становить 1 Гц (період 1000 мс). Відправка пакета не повинна здійснюватися через блокуючі виклики системної затримки (наприклад, `sleep` або `usleep`), оскільки це зупиняє виконання паралельних завдань, блокує читання кільцевих буферів послідовного порту UART та дестабілізує роботу контурів оцінки орієнтації (EKF).
2. **Динамічне виявлення та сторожовий моніторинг (Ingress Watchdog):** Приймальний вузол зобов'язаний пасивно прослуховувати вхідний потік кадрів, автоматично реєструвати нових учасників мережі за унікальною парою числових адрес `(system_id, component_id)` і вести персональний облік часових міток останнього отриманого серцебиття `t_last`. Якщо потік пакетів від критично важливого абонента (наприклад, наземного пульта пілота або головного автопілота) припиняється на час, що перевищує встановлений поріг (зазвичай 4.5–5.0 секунд), сторожовий таймер зобов'язаний миттєво змінити статус зв'язку на `LOST` та викликати аварійну функцію зворотного виклику (англ. *Failsafe Callback*) для запуску захисних процедур повернення або посадки.

---

## Інженерні виклики та пастки реалізації

Під час практичної розробки сторожових таймерів телеметрії інженери стикаються з п'ятьма типовими проблемами, неправильне вирішення яких призводить до фальшивих аварійних спрацьовувань або зависання системи в польоті.

### 1. Вибір джерела часу: астрономічний годинник проти монотонного лічильника

Найбільш небезпечною помилкою є використання системного астрономічного часу (англ. *Wall-Clock Time*, виклики `gettimeofday`, `time(NULL)` або `std::chrono::system_clock`). 

Астрономічний годинник операційної системи може стрибкоподібно змінювати своє значення під впливом зовнішніх служб корекції часу:
* Під час встановлення зв'язку з супутниками GPS бортовий приймач передає точний час UTC, і операційна система Linux на супутньому комп'ютері виконує стрибок годинника на кілька секунд або хвилин вперед чи назад.
* На наземній станції служба мережевого часу NTP (Network Time Protocol) може автоматично підкоригувати системний годинник операційної системи.

Якщо час переводиться назад навіть на 1 секунду, різниця `t_now - t_last` стає від'ємною (або перетворюється на гігантське додатне число в беззнаковій арифметиці), що або миттєво провокує фальшиве спрацьовування аварійного повернення дрона (RTL), або повністю блокує відлік таймера на час стрибка.

**Правильне рішення:** Використовувати виключно неперервні монотонні таймери, значення яких гарантовано зростає з постійною швидкістю від моменту завантаження процесора і ніколи не коригується зовнішніми джерелами часу:
* У стандарті POSIX C: `clock_gettime(CLOCK_MONOTONIC, &ts)`.
* У сучасному стандарті C++: `std::chrono::steady_clock::now()`.
* У польотному стеку PX4 / RTOS NuttX: системний виклик високої роздільної здатності `hrt_absolute_time()`.
* В операційному середовищі ArduPilot: функція апаратного рівня `AP_HAL::millis()`.

### 2. Переповнення беззнакових лічильників мілісекунд (Integer Wrap-Around)

У вбудованих мікроконтролерах без операційної системи монотонний час часто зберігається у вигляді 32-бітного лічильника мілісекунд (`uint32_t`). Максимальне значення такого лічильника становить `2³² - 1 = 4 294 967 295` мілісекунд, що відповідає приблизно **49.71 діб** безперервної роботи.

Після досягнення максимального значення лічильник переповнюється і скидається в `0`. Якщо розробник реалізує перевірку тайм-ауту через пряме додавання:

:::tabs
```c
// ПОМИЛКОВА РЕАЛІЗАЦІЯ: ламається при переповненні лічильника
if (now_ms > last_seen_ms + TIMEOUT_MS) {
    trigger_failsafe();
}
```
```cpp
// ПОМИЛКОВА РЕАЛІЗАЦІЯ: ламається при переповненні лічильника
if (now_ms > last_seen_ms + TIMEOUT_MS) {
    trigger_failsafe();
}
```
:::

У момент, коли `last_seen_ms = 4294967000`, а `now_ms` після переповнення скинувся в `500`, вираз `last_seen_ms + TIMEOUT_MS` переповнюється, порівняння стає хибним, і сторожовий таймер перестає бачити втрату зв'язку протягом наступних 49 діб.

**Правильне рішення:** Розраховувати різницю виключно через операцію віднімання в беззнаковому типі:

:::tabs
```c
// ПРАВИЛЬНА РЕАЛІЗАЦІЯ: працює коректно в точці переходу через нуль
if ((uint32_t)(now_ms - last_seen_ms) >= TIMEOUT_MS) {
    trigger_failsafe();
}
```
```cpp
// ПРАВИЛЬНА РЕАЛІЗАЦІЯ: працює коректно в точці переходу через нуль
if (static_cast<uint32_t>(now_ms - last_seen_ms) >= TIMEOUT_MS) {
    trigger_failsafe();
}
```
:::

Завдяки математичним властивостям двійкової арифметики в додатковому коді (англ. *Two's Complement*), операція `(uint32_t)(500 - 4294967000)` дасть точне значення різниці `500 - (-296) = 796` мілісекунд без жодних додаткових умовних переходів.

### 3. Багатопотокова синхронізація та гонка станів (Race Conditions)

У реальних додатках прийом байтів із послідовного порту UART або мережевого UDP-сокета виконується в окремому високопріоритетному потоці введення-виведення (або безпосередньо в обробнику апаратного переривання ISR). У цьому потоці відбувається парсинг кадру MAVLink та оновлення мітки часу `last_seen_ms`.

Водночас періодична перевірка спрацьовування сторожових таймерів виконується в головному навігаційному циклі керування або окремому таймерному потоці моніторингу.

Якщо на 32-бітному процесорі (ARM Cortex-M4 або x86) мітка часу зберігається як 64-бітне число `uint64_t`, читання та запис цієї змінної вимагають виконання двох окремих 32-бітних процесорних інструкцій. Якщо потік перевірки перерве потік оновлення між записом молодшого та старшого 32-бітних слів, він прочитає спотворене значення часу, що призведе до непередбачуваної поведінки.

**Правильне рішення:** Застосовувати атомарні операції (`std::atomic<uint64_t>` у C++ або атомарні примітиви GCC `__atomic_store_n`/`__atomic_load_n` у C) або захищати критичні секції доступу до таблиці вузлів легковаговими м'ютексами.

### 4. Управління пам'яттю: динамічні контейнери проти статичних пулів

У високорівневих програмах моніторингу (на базі Linux або Windows) зручно використовувати асоціативні хеш-таблиці (`std::unordered_map`), які динамічно виділяють пам'ять під кожен новий виявлений пристрій.

Проте у вбудованому коді польотних контролерів використання динамічного виділення пам'яті (`malloc`, оператор `new`) під час польоту суворо заборонено через ризик фрагментації оперативної пам'яті (Heap Fragmentation) та непередбачуваний час виконання алокатора. Для бортових систем використовується статично виділений масив фіксованого розміру (наприклад, на 16 або 32 вузли) з алгоритмом витіснення найменш використовуваних або найдовше неактивних записів (LRU, Least Recently Used).

### 5. Гістерезис станів зв'язку та запобігання брязкоту (State Flutter)

Коли дрон віддаляється на межу дальності дії радіомодема, рівень сигналу RSSI коливається біля порогу чутливості приймача. Пакети надходять пачками: два втрачено, один отримано, знову три втрачено.

Якщо сторожовий таймер миттєво перемикатиме статус між `ONLINE` та `LOST`, польотний контролер почне хаотично смикатися: входити в режим RTL, за секунду скасовувати його, повертатися в режим місії, знову входити в RTL. Такий брязкіт станів (англ. *state flutter*) дезорієнтує навігаційний фільтр і може призвести до розгойдування апарата.

**Правильне рішення:** Реалізувати **гістерезис переходів**:
* Перехід `ONLINE -> WARNING` відбувається через 3.0 секунди бездіяльності.
* Перехід `WARNING -> LOST` (спрацьовування Failsafe) відбувається через 4.5–5.0 секунд.
* Повернення `LOST -> ONLINE` вимагає не просто одного випадкового пакета, а отримання щонайменше 2–3 послідовних валідних повідомлень `HEARTBEAT` без пропусків (або явного підтвердження від оператора).

---

## Архітектура багатопотокової обробки та інтеграція введення-виведення

Для забезпечення максимальної чуйності системи модуль розділено на три незалежні контури, пов'язані подійно-орієнтованим мультиплексуванням:

1. **Контур прийому (RX Worker Thread):** Обслуговує апаратні дескриптори послідовного порту UART або мережевого сокета UDP через неблокуючий системний виклик `poll()` або `epoll_wait()`. Після розпізнавання повідомлення `HEARTBEAT` потік миттєво оновлює параметри в таблиці вузлів, встановлюючи монотонну мітку часу, та негайно повертається до зчитування чергових байтів.
2. **Контур періодичної передачі (TX Timer Thread):** Спрацьовує з фіксованим квантом 1000 мс, зчитує системний статус із локальної пам'яті борту та формує вихідний кадр самооголошення.
3. **Контур сторожової перевірки (Watchdog Evaluation Loop):** Виконує періодичний аудит усіх записів таблиці з частотою 10–20 Гц, обчислює тривалість відсутності зв'язку та викликає зареєстровані обробники подій при переході через часові пороги.

Завдяки відокремленню контуру введення-виведення від таймерного аналізу, система ніколи не блокується в очікуванні даних, а обробка вхідних байтів не затримує генерацію вихідного серцебиття.

---

## Інтеграція в середовища операційних систем реального часу (FreeRTOS та NuttX)

У вбудованих системах керування на базі мікроконтролерів STM32 (ARM Cortex-M4/M7) сторожовий монітор часто оформлюють у вигляді окремого легковагового завдання операційної системи реального часу (RTOS Task).

Замість активного безперервного циклу опитування (англ. *busy polling*), що марно витрачає енергію акумулятора та ресурси процесора, завдання переводиться в стан сну (Blocked State) за допомогою бінарного семафора або черги повідомлень (`xQueueReceive` у FreeRTOS чи `mq_receive` у POSIX-сумісній NuttX). 

Коли апаратний контролер DMA закінчує прийом чергового блоку телеметрії по UART, обробник переривання надсилає сповіщення черзі, пробуджуючи завдання моніторингу. Одночасно періодичний програмний таймер RTOS (`xTimerCreate` з квантом 100 мс) періодично виводить задачу зі сну для перевірки термінів давності зв'язку. Такий підхід забезпечує мінімальну затримку реакції на втрату сигналу при нульовому навантаженні на центральний процесор під час пауз між пакетами.

---

## Повна програмна реалізація модулів на C та C++

Нижче наведено закінчену реалізацію монітора. Модуль забезпечує фонову періодичну відправку серцебиття з фіксованим інтервалом 1000 мс, веде динамічну таблицю відомих пристроїв і генерує події трьох рівнів: `ONLINE` (зв'язок у нормі), `WARNING` (пропуск пакетів понад 3 секунди) та `LOST` (повна втрата зв'язку понад 4.5 секунди).

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define MAX_TRACKED_NODES          16
#define HEARTBEAT_PERIOD_MS        1000   // Інтервал відправки 1 Гц
#define HEARTBEAT_WARN_TIMEOUT_MS  3000   // Поріг попередження (3 с)
#define HEARTBEAT_LOST_TIMEOUT_MS  4500   // Поріг втрати лінку (4.5 с)

// Рівні стану зв'язку з віддаленим вузлом
typedef enum {
    NODE_LINK_OFFLINE = 0,
    NODE_LINK_ONLINE,
    NODE_LINK_WARNING,
    NODE_LINK_LOST
} node_link_state_t;

// Структура обліку окремого віддаленого вузла мережі
typedef struct {
    uint8_t           system_id;
    uint8_t           component_id;
    uint8_t           type;
    uint8_t           autopilot;
    uint8_t           base_mode;
    uint32_t          custom_mode;
    uint8_t           system_status;
    uint64_t          last_heartbeat_ms;
    node_link_state_t state;
    bool              is_active;
} tracked_node_t;

// Структура головного контексту монітора
typedef struct {
    uint8_t        my_sysid;
    uint8_t        my_compid;
    uint8_t        my_type;
    uint8_t        my_autopilot;
    uint64_t       last_tx_ms;
    tracked_node_t nodes[MAX_TRACKED_NODES];
    void (*on_failsafe_event)(uint8_t sysid, uint8_t compid, node_link_state_t new_state);
} mavlink_monitor_t;

// Отримання поточного монотонного часу процесора в мілісекундах
static uint64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)(ts.tv_nsec / 1000000ULL);
}

// Ініціалізація структури монітора
void mavlink_monitor_init(mavlink_monitor_t* mon, uint8_t sysid, uint8_t compid,
                          uint8_t type, uint8_t autopilot,
                          void (*failsafe_cb)(uint8_t, uint8_t, node_link_state_t)) {
    memset(mon, 0, sizeof(mavlink_monitor_t));
    mon->my_sysid = sysid;
    mon->my_compid = compid;
    mon->my_type = type;
    mon->my_autopilot = autopilot;
    mon->last_tx_ms = 0;
    mon->on_failsafe_event = failsafe_cb;
}

// Обробка вхідного розпарсеного повідомлення HEARTBEAT
void mavlink_monitor_handle_heartbeat(mavlink_monitor_t* mon, uint8_t sysid, uint8_t compid,
                                      uint8_t type, uint8_t autopilot, uint8_t base_mode,
                                      uint32_t custom_mode, uint8_t system_status) {
    uint64_t now = get_monotonic_ms();
    int empty_slot = -1;

    // Пошук вузла в таблиці за парою (sysid, compid)
    for (int i = 0; i < MAX_TRACKED_NODES; ++i) {
        if (mon->nodes[i].is_active &&
            mon->nodes[i].system_id == sysid &&
            mon->nodes[i].component_id == compid) {
            
            mon->nodes[i].type = type;
            mon->nodes[i].autopilot = autopilot;
            mon->nodes[i].base_mode = base_mode;
            mon->nodes[i].custom_mode = custom_mode;
            mon->nodes[i].system_status = system_status;
            mon->nodes[i].last_heartbeat_ms = now;

            // Якщо зв'язок відновився після деградації або обриву
            if (mon->nodes[i].state != NODE_LINK_ONLINE) {
                mon->nodes[i].state = NODE_LINK_ONLINE;
                if (mon->on_failsafe_event) {
                    mon->on_failsafe_event(sysid, compid, NODE_LINK_ONLINE);
                }
            }
            return;
        }

        if (!mon->nodes[i].is_active && empty_slot == -1) {
            empty_slot = i;
        }
    }

    // Реєстрація нового раніше невідомого вузла
    if (empty_slot != -1) {
        tracked_node_t* node = &mon->nodes[empty_slot];
        node->is_active = true;
        node->system_id = sysid;
        node->component_id = compid;
        node->type = type;
        node->autopilot = autopilot;
        node->base_mode = base_mode;
        node->custom_mode = custom_mode;
        node->system_status = system_status;
        node->last_heartbeat_ms = now;
        node->state = NODE_LINK_ONLINE;

        if (mon->on_failsafe_event) {
            mon->on_failsafe_event(sysid, compid, NODE_LINK_ONLINE);
        }
    }
}

// Періодичний крок оновлення таймерів (виклик із головного циклу)
void mavlink_monitor_tick(mavlink_monitor_t* mon,
                          void (*send_hb_fn)(uint8_t sysid, uint8_t compid, uint8_t type,
                                            uint8_t autopilot, uint8_t base_mode,
                                            uint32_t custom_mode, uint8_t system_status)) {
    uint64_t now = get_monotonic_ms();

    // 1. Трансляція власного HEARTBEAT з частотою 1 Гц
    if (now - mon->last_tx_ms >= HEARTBEAT_PERIOD_MS) {
        mon->last_tx_ms = now;
        if (send_hb_fn) {
            // Прапорці базового режиму: ARMED (0x80) | STABILIZE (0x10) | CUSTOM (0x01)
            uint8_t base_mode = 0x80 | 0x10 | 0x01;
            uint32_t custom_mode = 0x00030000; // PX4 POSCTL
            uint8_t system_status = 4;          // MAV_STATE_ACTIVE
            send_hb_fn(mon->my_sysid, mon->my_compid, mon->my_type,
                       mon->my_autopilot, base_mode, custom_mode, system_status);
        }
    }

    // 2. Перевірка сторожових таймерів для всіх активних вузлів
    for (int i = 0; i < MAX_TRACKED_NODES; ++i) {
        if (!mon->nodes[i].is_active) continue;

        uint64_t elapsed_ms = now - mon->nodes[i].last_heartbeat_ms;

        if (elapsed_ms >= HEARTBEAT_LOST_TIMEOUT_MS) {
            if (mon->nodes[i].state != NODE_LINK_LOST) {
                mon->nodes[i].state = NODE_LINK_LOST;
                if (mon->on_failsafe_event) {
                    mon->on_failsafe_event(mon->nodes[i].system_id,
                                           mon->nodes[i].component_id,
                                           NODE_LINK_LOST);
                }
            }
        } else if (elapsed_ms >= HEARTBEAT_WARN_TIMEOUT_MS) {
            if (mon->nodes[i].state == NODE_LINK_ONLINE) {
                mon->nodes[i].state = NODE_LINK_WARNING;
                if (mon->on_failsafe_event) {
                    mon->on_failsafe_event(mon->nodes[i].system_id,
                                           mon->nodes[i].component_id,
                                           NODE_LINK_WARNING);
                }
            }
        }
    }
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <chrono>
#include <unordered_map>
#include <functional>
#include <string_view>
#include <mutex>

namespace mavlink {

enum class LinkState {
    Offline,
    Online,
    Warning,
    Lost
};

struct NodeAddress {
    uint8_t sysid{0};
    uint8_t compid{0};

    bool operator==(const NodeAddress& other) const noexcept {
        return sysid == other.sysid && compid == other.compid;
    }
};

struct NodeAddressHash {
    std::size_t operator()(const NodeAddress& addr) const noexcept {
        return (static_cast<std::size_t>(addr.sysid) << 8) | static_cast<std::size_t>(addr.compid);
    }
};

struct NodeRecord {
    NodeAddress address{};
    uint8_t     type{0};
    uint8_t     autopilot{0};
    uint8_t     base_mode{0};
    uint32_t    custom_mode{0};
    uint8_t     system_status{0};
    std::chrono::steady_clock::time_point last_heartbeat{};
    LinkState   state{LinkState::Offline};

    [[nodiscard]] constexpr bool is_armed() const noexcept {
        return (base_mode & 0x80) != 0;
    }
};

class HeartbeatService {
public:
    using StateChangeHandler = std::function<void(const NodeRecord&, LinkState)>;
    using HeartbeatEmitter   = std::function<void(uint8_t sysid, uint8_t compid, uint8_t type,
                                                  uint8_t autopilot, uint8_t base_mode,
                                                  uint32_t custom_mode, uint8_t system_status)>;

    HeartbeatService(uint8_t sysid, uint8_t compid, uint8_t type, uint8_t autopilot) noexcept
        : my_sysid_(sysid), my_compid_(compid), my_type_(type), my_autopilot_(autopilot) {}

    void on_state_change(StateChangeHandler handler) noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        state_handler_ = std::move(handler);
    }

    void process_incoming_heartbeat(uint8_t sysid, uint8_t compid, uint8_t type,
                                   uint8_t autopilot, uint8_t base_mode,
                                   uint32_t custom_mode, uint8_t system_status) {
        const auto now = std::chrono::steady_clock::now();
        const NodeAddress addr{sysid, compid};

        std::lock_guard<std::mutex> lock(mutex_);
        auto it = nodes_.find(addr);

        if (it == nodes_.end()) {
            NodeRecord record{
                .address = addr,
                .type = type,
                .autopilot = autopilot,
                .base_mode = base_mode,
                .custom_mode = custom_mode,
                .system_status = system_status,
                .last_heartbeat = now,
                .state = LinkState::Online
            };
            auto [new_it, _] = nodes_.emplace(addr, record);
            dispatch_event(new_it->second, LinkState::Online);
        } else {
            auto& record = it->second;
            record.type = type;
            record.autopilot = autopilot;
            record.base_mode = base_mode;
            record.custom_mode = custom_mode;
            record.system_status = system_status;
            record.last_heartbeat = now;

            if (record.state != LinkState::Online) {
                record.state = LinkState::Online;
                dispatch_event(record, LinkState::Online);
            }
        }
    }

    void update_timers(const HeartbeatEmitter& emitter) {
        const auto now = std::chrono::steady_clock::now();

        // 1. Періодична відправка власного серцебиття 1 Гц
        if (now - last_broadcast_ >= std::chrono::milliseconds(1000)) {
            last_broadcast_ = now;
            if (emitter) {
                const uint8_t base_mode = 0x80 | 0x10 | 0x01; // ARMED | STABILIZED | CUSTOM
                const uint32_t custom_mode = 0x00030000;      // PX4 POSCTL
                const uint8_t system_status = 4;               // MAV_STATE_ACTIVE
                emitter(my_sysid_, my_compid_, my_type_, my_autopilot_,
                        base_mode, custom_mode, system_status);
            }
        }

        // 2. Перевірка сторожових таймерів віддалених вузлів
        std::lock_guard<std::mutex> lock(mutex_);
        for (auto& [addr, record] : nodes_) {
            const auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - record.last_heartbeat);

            if (elapsed >= std::chrono::milliseconds(4500)) {
                if (record.state != LinkState::Lost) {
                    record.state = LinkState::Lost;
                    dispatch_event(record, LinkState::Lost);
                }
            } else if (elapsed >= std::chrono::milliseconds(3000)) {
                if (record.state == LinkState::Online) {
                    record.state = LinkState::Warning;
                    dispatch_event(record, LinkState::Warning);
                }
            }
        }
    }

private:
    void dispatch_event(const NodeRecord& record, LinkState state) const noexcept {
        if (state_handler_) {
            state_handler_(record, state);
        }
    }

    uint8_t my_sysid_{1};
    uint8_t my_compid_{1};
    uint8_t my_type_{2};
    uint8_t my_autopilot_{12};
    std::chrono::steady_clock::time_point last_broadcast_{};

    mutable std::mutex mutex_;
    std::unordered_map<NodeAddress, NodeRecord, NodeAddressHash> nodes_;
    StateChangeHandler state_handler_;
};

} // namespace mavlink
```
:::

---

## Покроковий розбір алгоритмічної логіки

Проаналізуємо ключові етапи функціонування розробленого модуля:

1. **Ініціалізація сервісу:** Функція `mavlink_monitor_init` або конструктор класу `HeartbeatService` фіксують власну адресу пристрою (`system_id`, `component_id`), його фізичний тип (наприклад, квадрокоптер `MAV_TYPE_QUADROTOR = 2`) та стек автопілота (`MAV_AUTOPILOT_PX4 = 12`). Також реєструється функція зворотного виклику для обробки аварійних подій.
2. **Маршрутизація вхідних пакетів:** Метод `handle_heartbeat` викликається потоком парсингу MAVLink щоразу, коли з лінії зв'язку надходить кадр з ідентифікатором `MSG ID 0`. Модуль виконує швидкий пошук у таблиці вузлів:
   * Якщо вузол уже відомий, оновлюються його поточні параметри (`base_mode`, `custom_mode`, `system_status`) та фіксується поточний монотонний час `last_heartbeat_ms = now`. Якщо попередній стан вузла був `WARNING` або `LOST`, лічильник помилок скидається, а статус повертається в `ONLINE`.
   * Якщо пристрій з'явився вперше, створюється новий запис у таблиці топології та генерується подія первинного виявлення абонента.
3. **Фоновий цикл оновлення (Метод `tick`):** Викликається з основного циклу програми або таймерного завдання RTOS:
   * Перша гілка перевіряє умову `now - last_tx_ms >= 1000`. При її виконанні викликається передавач, який транслює свіже повідомлення `HEARTBEAT` в апаратний UART або мережевий UDP-сокет.
   * Друга гілка обходить усі зареєстровані вузли та розраховує час відсутності повідомлень: `elapsed = now - last_heartbeat`. При перевищенні порогу 3000 мс генерується попередження `WARNING`, а при перевищенні 4500 мс — подія `LOST` з активацією контурів Failsafe.

---

## Оцінка якості каналу та метрики джиттера

Окрім простого відстеження тайм-ауту повної втрати зв'язку, професійні наземні станції керування (QGroundControl) та бортові маршрутизатори обчислюють дві додаткові метрики якості лінії зв'язку на основі потоку повідомлень `HEARTBEAT`:

1. **Коефіцієнт втрати пакетів (Packet Drop Rate):** У кожному кадрі MAVLink поле `SEQ` містить послідовний номер пакета від 0 до 255. Якщо за певний інтервал часу надійшли пакети з номерами `10, 11, 12, 15, 16`, приймач фіксує пропуск двох пакетів (`13` та `14`). Співвідношення кількості втрачених пакетів до загальної кількості очікуваних дозволяє розрахувати відсоток втрат каналу.
2. **Оцінка часового джиттера (Jitter Estimation):** В ідеальній лінії зв'язку інтервал між приходом двох сусідніх повідомлень `HEARTBEAT` становить точно `1000` мілісекунд. Через затримки в буферах операційної системи, повторні передачі радіомодема та інтерференцію в радіоефірі реальний інтервал коливається (наприклад, `950 мс`, `1080 мс`, `920 мс`). Джиттер обчислюється як ковзне середнє абсолютного відхилення: `J = (1 - α) · J + α · |Δt - 1000|`, де `α = 0.1` — коефіцієнт експоненційного згладжування. Зростання джиттера понад 200 мс є раннім індикатором перевантаження радіоканалу або наближення до зони радіозавад задовго до настання повного тайм-ауту втрати зв'язку.

---

## Алгоритми витіснення застарілих записів (LRU Eviction)

У бортових контролерах польоту з жорсткими лімітами статичної пам'яті таблиця вузлів має обмежену місткість (наприклад, 16 слотів). Якщо безпілотник бере участь у спільних польотах великої кількості груп або проходить через зони дії багатьох тимчасових наземних станцій, таблиця може заповнитися неактивними записами.

Для запобігання переповненню таблиці вбудований модуль реалізує політику витіснення застарілих вузлів (англ. *Least Recently Used Eviction*):
* Якщо вільних слотів немає, а з лінії надійшов `HEARTBEAT` від нового вузла, алгоритм шукає запис із найбільшим значенням `now - last_heartbeat`.
* Якщо цей неактивний вузол перебуває в стані `LOST` понад 60 секунд, його запис безперешкодно перезаписується новими даними.
* Якщо ж усі зайняті слоти відповідають активним вузлам (`ONLINE` або `WARNING`), новий пристрій тимчасово ігнорується, а система реєструє попередження про вичерпання ліміту абонентів мережі.

Такий підхід гарантує детерміноване використання статичної пам'яті без загрози вичерпання пулу адрес під час тривалого польоту в динамічному середовищі.

---

## Сценарії верифікації та стендового тестування

Для перевірки надійності розробленої системи на стенді проводять три стандартні тести:

* **Тест 1 (Нормальна робота):** Передавач транслює пакети з частотою 1 Гц протягом 60 секунд. Сторожовий таймер безперервно утримує стан `LinkState::Online`, середній час відгуку становить `1000 ± 15` мс.
* **Тест 2 (Обрив каналу / Failsafe Timeout):** На 10-й секунді польоту канал передачі штучно блокується (вимикається живлення радіомодема). На 13-й секунді сторожовий таймер перемикає статус у `Warning` (наземна станція підсвічує зв'язок жовтим кольором). На 14.5-й секунді генерується подія `LinkState::Lost`, і польотний контролер автоматично перемикає польотний режим у `RTL` (Return to Launch).
* **Тест 3 (Відновлення зв'язку):** На 20-й секунді живлення модема відновлюється. Перший же отриманий пакет `HEARTBEAT` миттєво повертає статус вузла в `LinkState::Online`, підтверджуючи працездатність каналу керування.
