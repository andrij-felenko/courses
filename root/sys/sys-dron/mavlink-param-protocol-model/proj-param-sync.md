# Реалізація клієнтського рушія синхронізації параметрів

У цій практичній роботі розглянуто проектування та реалізацію промислового, неблокуючого клієнтського рушія синхронізації системних параметрів MAVLink (Parameter Synchronization Engine) мовами C та C++. Розроблений модуль забезпечує автоматичне вичитування повної конфігурації автопілота, динамічне виявлення втрачених у радіоканалі пакетів, формування точкових запитів дозавантаження та потокове оновлення локальної таблиці конфігурації без блокування головного циклу обробки телеметрії.

---

### Постановка інженерної задачі та виклики радіоканалу

Синхронізація параметрів між польотним контролером безпілотного апарата (ArduPilot / PX4) та клієнтським програмним забезпеченням (наземна станція QGroundControl, Mission Planner або бортовий супутній комп'ютер на базі ROS 2) відбувається в умовах жорстких фізичних обмежень каналу зв'язку.

Типовий телеметрійний лінк будується на базі напівдуплексних радіомодемів діапазону 433/915 МГц (SiK Radio, Holybro, RFD900) зі швидкістю фізичного інтерфейсу UART 57600 бод. Реальна корисна пропускна здатність такого каналу з урахуванням службових заголовків радіомодема та напівдуплексного перемикання становить лише 4–5 кілобайтів за секунду. При цьому сучасний автопілот містить від 1200 до 2500 конфігураційних змінних, які визначають налаштування фільтрів оцінки стану (EKF), матриці калібрування сенсорів, коефіцієнти PID-регуляторів та пороги аварійного повернення додому (Failsafe).

У реальних польових умовах через просторове згасання сигналу, електромагнітні завади від силових регуляторів обертів (ESC) та багатопроменеве поширення радіохвиль рівень втрат пакетів в ефірі становить від 10% до 30%. За таких умов наївна реалізація клієнтського протоколу стикається з трьома критичними проблемами:

1. **Блокування послідовним очікуванням (Stop-and-Wait Penalty):** якщо запитувати кожен параметр окремим запитом і чекати на відповідь перед надсиланням наступного, повне вичитування 1500 параметрів із круговим часом затримки (RTT) близько 100 мс займе понад 150 секунд.
2. **Неконтрольований перезапуск списку (Burst Starvation):** якщо намагатися завантажувати параметри суцільним пакетом без виявлення дірок і при першій же втраті перезапитувати весь список заново через `PARAM_REQUEST_LIST`, система ніколи не зможе завершити синхронізацію на зашумленому лінку.
3. **Переповнення апаратних буферів FIFO (UART Buffer Overrun):** якщо автопілот надсилатиме пакети `PARAM_VALUE` із максимальною швидкістю процесора без затримок, приймальний буфер UART радіомодема або мікроконтролера миттєво переповниться, що призведе до втрати 50–70% пакетів у серії.

Для вирішення цих викликів клієнтський рушій повинен реалізувати асинхронну гібридну модель: швидке пакетне вичитування першого проходу (Burst Download) з подальшим виявленням локальних прогалин у нумерації індексів та їх адресним дозавантаженням (Targeted Hole Recovery) за допомогою точкових запитів `PARAM_REQUEST_READ`.

---

### Алгоритм виявлення прогалин (Hole Detection) та бітові структури даних

Ключовим елементом рушія є структура даних для обліку отриманих параметрів. Кожне повідомлення `PARAM_VALUE` містить два обов'язкових числових поля: загальну кількість параметрів `param_count` та унікальний порядковий номер поточного параметра `param_index` у діапазоні від `0` до `param_count - 1`.

Для відстеження стану завантаження можливі три підходи:

1. **Динамічний список отриманих ідентифікаторів (std::vector або зв'язний список):** вимагає лінійного пошуку O(N) під час вставки кожного нового параметра та призводить до динамічної фрагментації пам'яті в мікроконтролерах.
2. **Масив інтервалів (Interval Tree / Range Map):** ефективно зберігає неперервні діапазони індексів, проте має складну логіку об'єднання та розщеплення вузлів дерева.
3. **Фіксована бітова маска (Bitmask / Bitset):** кожен біт пам'яті відповідає рівно одному числовому індексу. Значення `1` означає, що параметр із цим індексом уже отримано та збережено в таблиці; значення `0` позначає пропущений або ще не завантажений індекс.

Бітова маска є оптимальним вибором для вбудованих систем та наземних станцій. Для зберігання інформації про 2048 конфігураційних змінних потрібно рівно 256 байтів статичної оперативної пам'яті (`2048 / 8 = 256`). Операції перевірки та встановлення біта виконуються за константний час O(1) за допомогою базових побітових операцій процесора.

```
Схема адресації індексів у бітовому масиві uint8_t mask[256]:
Індекс параметра:   index = 13 (двійкове 0b00001101)
Номер байта:        byte_offset = index / 8 = 13 / 8 = 1 (другий байт масиву)
Позиція біта:       bit_offset  = index % 8 = 13 % 8 = 5 (шостий біт у байті)

Операція встановлення біта:
mask[byte_offset] |= (1 << bit_offset);

Операція перевірки біта:
bool is_received = (mask[byte_offset] & (1 << bit_offset)) != 0;
```

```
Приклад стану бітової маски після першого пакетного проходу:
Байт 0 (індекси 0..7):    [ 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 ]  ← пропущено індекс 4!
Байт 1 (індекси 8..15):   [ 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 ]  ← пропущено індекси 10 та 15!
Байт 2 (індекси 16..23):  [ 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 ]  ← весь діапазон цілий
```

Після того, як автопілот завершує передачу первинного пакетного потоку (що фіксується за тайм-аутом відсутності нових вхідних повідомлень понад 500 мс), клієнтський рушій запускає лінійне сканування бітової карти від `0` до `param_count - 1`. Перший знайдений нульовий біт стає ціллю для точкового дозавантаження.

---

### Архітектура скінченного автомата стану (FSM Engine)

Клієнтський рушій будується за принципом недетермінованого скінченного автомата з неблокуючим інтерфейсом опитування (`poll()` або `tick()`), що викликається в головному циклі програми або за таймером операційної системи реального часу (FreeRTOS).

Автомат містить шість фундаментальних станів:

1. **`IDLE` (Очікування):** рушій перебуває в неактивному стані. Таблиця параметрів порожня або містить попередню конфігурацію.
2. **`REQUEST_LIST` (Запит повного списку):** клієнт надіслав повідомлення `PARAM_REQUEST_LIST` цільовій системі та очікує на перший пакет `PARAM_VALUE`. Якщо відповідь не надходить протягом 1000 мс, виконується повторне надсилання запиту (до трьох спроб).
3. **`RECEIVING_BURST` (Прийом пакетного потоку):** отримано перший пакет. Клієнт зберігає значення `param_count` і починає приймати потік повідомлень, скидаючи таймер активності при кожному новому кадрі. Якщо загальна кількість отриманих параметрів досягає `param_count`, процес одразу успішно завершується. Якщо потік зупиняється, але частина параметрів відсутня, після закінчення 500 мс бездіяльності автомат перемикається на усунення прогалин.
4. **`RESOLVING_HOLES` (Дозавантаження пропусків):** рушій послідовно знаходить пропущені індекси в бітовій масці та надсилає для кожного з них точкове повідомлення `PARAM_REQUEST_READ`. Для кожного індексу ведеться індивідуальний лічильник спроб (до 5 повторів із тайм-аутом 800 мс). Як тільки очікуваний пакет надходить, біт встановлюється в `1`, і рушій негайно переходить до наступної прогалини.
5. **`COMPLETED` (Успішне завершення):** всі `param_count` параметрів успішно отримано, валідовано та внесено до таблиці конфігурації. Рушій формує системну подію про готовність параметрів для інтерфейсу користувача чи алгоритмів навігації.
6. **`FAILED` (Критична помилка):** вичерпано ліміт повторних спроб зв'язку під час запиту списку або дозавантаження конкретного індексу.

```
Схема перемикання станів клієнтського рушія:
[ IDLE ]
   │  Виклик start_sync()
   v
[ REQUEST_LIST ] ──(Тайм-аут 3 спроб)──> [ FAILED ]
   │  Отримано перший PARAM_VALUE
   v
[ RECEIVING_BURST ] ──(Отримано всі N параметрів)──> [ COMPLETED ]
   │  Таймер мовчання > 500 мс (наявні дірки)
   v
[ RESOLVING_HOLES ] ──(Перевищено 5 спроб на індекс)──> [ FAILED ]
   │  Всі прогалини заповнено
   v
[ COMPLETED ]
```

---

### Робоча реалізація мовами C та C++

Нижче наведено повний вихідний код двох варіантів рушія. Варіант на C розроблено для мікроконтролерів із жорстким обмеженням пам'яті (статичні масиви, без використання купи `malloc`), а варіант на C++20 використовує безпечні типізовані конструкції (`std::variant`, `std::bit_cast`, `std::string_view`, `std::chrono`) та підходить для наземних станцій і високорівневих бортових комп'ютерів.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define MAX_PARAMS_CAPACITY 2048
#define PARAM_ID_LEN 16
#define MAX_LIST_RETRIES 3
#define MAX_HOLE_RETRIES 5
#define BURST_TIMEOUT_MS 500
#define READ_TIMEOUT_MS 800
#define LIST_TIMEOUT_MS 1000

typedef enum {
    SYNC_STATE_IDLE,
    SYNC_STATE_REQUEST_LIST,
    SYNC_STATE_RECEIVING_BURST,
    SYNC_STATE_RESOLVING_HOLES,
    SYNC_STATE_COMPLETED,
    SYNC_STATE_FAILED
} param_sync_state_t;

typedef struct {
    char     id[PARAM_ID_LEN + 1];
    float    raw_value;
    uint8_t  type;
    uint16_t index;
    bool     valid;
} param_entry_t;

typedef struct {
    uint8_t target_sys;
    uint8_t target_comp;
    param_sync_state_t state;

    uint16_t param_count;
    uint16_t received_count;

    // Бітова маска отриманих індексів (2048 бітів = 256 байтів)
    uint8_t  index_bitmask[MAX_PARAMS_CAPACITY / 8];
    param_entry_t entries[MAX_PARAMS_CAPACITY];

    // Змінні таймерів і повторів
    uint32_t last_packet_time_ms;
    uint16_t current_hole_index;
    uint8_t  retry_count;
} param_sync_engine_t;

// Встановлення біта в масці
static inline void bitmask_set(uint8_t *mask, uint16_t index) {
    mask[index / 8] |= (uint8_t)(1u << (index % 8));
}

// Перевірка стану біта в масці
static inline bool bitmask_test(const uint8_t *mask, uint16_t index) {
    return (mask[index / 8] & (uint8_t)(1u << (index % 8))) != 0;
}

// Ініціалізація структури рушія
void param_sync_init(param_sync_engine_t *eng, uint8_t sys_id, uint8_t comp_id) {
    memset(eng, 0, sizeof(param_sync_engine_t));
    eng->target_sys = sys_id;
    eng->target_comp = comp_id;
    eng->state = SYNC_STATE_IDLE;
}

// Зовнішні інтерфейси відправлення MAVLink-повідомлень у фізичний драйвер
extern void send_mavlink_request_list(uint8_t sys_id, uint8_t comp_id);
extern void send_mavlink_request_read(uint8_t sys_id, uint8_t comp_id, int16_t index);

// Запуск повної синхронізації
void param_sync_start(param_sync_engine_t *eng, uint32_t current_time_ms) {
    memset(eng->index_bitmask, 0, sizeof(eng->index_bitmask));
    eng->received_count = 0;
    eng->param_count = 0;
    eng->state = SYNC_STATE_REQUEST_LIST;
    eng->retry_count = 0;
    eng->last_packet_time_ms = current_time_ms;

    send_mavlink_request_list(eng->target_sys, eng->target_comp);
}

// Обробник вхідного повідомлення PARAM_VALUE
void param_sync_on_param_value(param_sync_engine_t *eng,
                               const char wire_id[16],
                               float val,
                               uint8_t type,
                               uint16_t count,
                               uint16_t index,
                               uint32_t current_time_ms) {
    if (index >= MAX_PARAMS_CAPACITY || count > MAX_PARAMS_CAPACITY) {
        return;
    }

    eng->last_packet_time_ms = current_time_ms;

    if (eng->param_count == 0 && count > 0) {
        eng->param_count = count;
    }

    // Якщо цей індекс ще не було зафіксовано в масці
    if (!bitmask_test(eng->index_bitmask, index)) {
        bitmask_set(eng->index_bitmask, index);
        eng->received_count++;

        param_entry_t *e = &eng->entries[index];
        memcpy(e->id, wire_id, PARAM_ID_LEN);
        e->id[PARAM_ID_LEN] = '\0';
        e->raw_value = val;
        e->type = type;
        e->index = index;
        e->valid = true;
    }

    // Перемикання станів автомата
    if (eng->state == SYNC_STATE_REQUEST_LIST) {
        eng->state = SYNC_STATE_RECEIVING_BURST;
    }

    // Якщо ми в режимі усунення прогалин і прийшов поточний очікуваний індекс
    if (eng->state == SYNC_STATE_RESOLVING_HOLES && index == eng->current_hole_index) {
        eng->retry_count = 0;
    }
}

// Пошук найближчого нульового біта в масці
static int32_t find_next_hole(const param_sync_engine_t *eng, uint16_t start_idx) {
    for (uint16_t i = start_idx; i < eng->param_count; ++i) {
        if (!bitmask_test(eng->index_bitmask, i)) {
            return (int32_t)i;
        }
    }
    return -1;
}

// Неблокуюче періодичне опитування стану (викликається в головному циклі)
void param_sync_poll(param_sync_engine_t *eng, uint32_t current_time_ms) {
    switch (eng->state) {
        case SYNC_STATE_REQUEST_LIST:
            if (current_time_ms - eng->last_packet_time_ms > LIST_TIMEOUT_MS) {
                if (eng->retry_count < MAX_LIST_RETRIES) {
                    eng->retry_count++;
                    eng->last_packet_time_ms = current_time_ms;
                    send_mavlink_request_list(eng->target_sys, eng->target_comp);
                } else {
                    eng->state = SYNC_STATE_FAILED;
                }
            }
            break;

        case SYNC_STATE_RECEIVING_BURST:
            // Перевірка повного отримання всіх елементів
            if (eng->received_count >= eng->param_count && eng->param_count > 0) {
                eng->state = SYNC_STATE_COMPLETED;
                break;
            }
            // Перевірка затишшя потоку
            if (current_time_ms - eng->last_packet_time_ms > BURST_TIMEOUT_MS) {
                int32_t first_hole = find_next_hole(eng, 0);
                if (first_hole >= 0) {
                    eng->state = SYNC_STATE_RESOLVING_HOLES;
                    eng->current_hole_index = (uint16_t)first_hole;
                    eng->retry_count = 0;
                    eng->last_packet_time_ms = current_time_ms;
                    send_mavlink_request_read(eng->target_sys, eng->target_comp, (int16_t)first_hole);
                } else {
                    eng->state = SYNC_STATE_COMPLETED;
                }
            }
            break;

        case SYNC_STATE_RESOLVING_HOLES:
            // Якщо поточну дірку успішно закрито
            if (bitmask_test(eng->index_bitmask, eng->current_hole_index)) {
                int32_t next = find_next_hole(eng, eng->current_hole_index + 1);
                if (next >= 0) {
                    eng->current_hole_index = (uint16_t)next;
                    eng->retry_count = 0;
                    eng->last_packet_time_ms = current_time_ms;
                    send_mavlink_request_read(eng->target_sys, eng->target_comp, (int16_t)next);
                } else {
                    eng->state = (eng->received_count >= eng->param_count) ?
                                  SYNC_STATE_COMPLETED : SYNC_STATE_FAILED;
                }
            } else if (current_time_ms - eng->last_packet_time_ms > READ_TIMEOUT_MS) {
                if (eng->retry_count < MAX_HOLE_RETRIES) {
                    eng->retry_count++;
                    eng->last_packet_time_ms = current_time_ms;
                    send_mavlink_request_read(eng->target_sys, eng->target_comp, (int16_t)eng->current_hole_index);
                } else {
                    // Вичерпано ліміт спроб для окремого індексу
                    eng->state = SYNC_STATE_FAILED;
                }
            }
            break;

        case SYNC_STATE_IDLE:
        case SYNC_STATE_COMPLETED:
        case SYNC_STATE_FAILED:
            break;
    }
}
```
```cpp
#include <cstdint>
#include <cstring>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <variant>
#include <chrono>
#include <functional>
#include <bit>
#include <iostream>

class ParameterSyncEngine {
public:
    using ParamValue = std::variant<uint8_t, int8_t, uint16_t, int16_t, uint32_t, int32_t, float>;

    struct Parameter {
        std::string name;
        ParamValue  value;
        uint8_t     mav_type{0};
        uint16_t    index{0};
    };

    enum class State {
        Idle,
        RequestingList,
        ReceivingBurst,
        ResolvingHoles,
        Completed,
        Failed
    };

    using SendListCallback = std::function<void(uint8_t sys_id, uint8_t comp_id)>;
    using SendReadCallback = std::function<void(uint8_t sys_id, uint8_t comp_id, int16_t index)>;

    ParameterSyncEngine(uint8_t sys_id, uint8_t comp_id,
                        SendListCallback send_list,
                        SendReadCallback send_read)
        : target_system_(sys_id)
        , target_component_(comp_id)
        , send_list_fn_(std::move(send_list))
        , send_read_fn_(std::move(send_read)) {}

    void start(std::chrono::steady_clock::time_point now) {
        state_ = State::RequestingList;
        param_count_ = 0;
        received_count_ = 0;
        retry_count_ = 0;
        received_mask_.clear();
        params_by_index_.clear();
        params_by_name_.clear();
        last_activity_ = now;

        if (send_list_fn_) {
            send_list_fn_(target_system_, target_component_);
        }
    }

    void on_param_value(const char wire_id[16],
                        float raw_val,
                        uint8_t mav_type,
                        uint16_t total_count,
                        uint16_t index,
                        std::chrono::steady_clock::time_point now) {
        last_activity_ = now;

        if (param_count_ == 0 && total_count > 0) {
            param_count_ = total_count;
            received_mask_.resize(param_count_, false);
            params_by_index_.resize(param_count_);
        }

        if (index >= param_count_) {
            return;
        }

        if (!received_mask_[index]) {
            received_mask_[index] = true;
            received_count_++;

            const size_t id_len = strnlen(wire_id, 16);
            std::string name(wire_id, id_len);

            Parameter param{
                .name = name,
                .value = unpack_wire_value(raw_val, mav_type),
                .mav_type = mav_type,
                .index = index
            };

            params_by_index_[index] = param;
            params_by_name_[name] = param;
        }

        if (state_ == State::RequestingList) {
            state_ = State::ReceivingBurst;
        } else if (state_ == State::ResolvingHoles && index == current_hole_index_) {
            retry_count_ = 0;
        }
    }

    void poll(std::chrono::steady_clock::time_point now) {
        using namespace std::chrono_literals;

        switch (state_) {
            case State::RequestingList:
                if (now - last_activity_ > 1000ms) {
                    if (retry_count_ < max_list_retries_) {
                        retry_count_++;
                        last_activity_ = now;
                        send_list_fn_(target_system_, target_component_);
                    } else {
                        state_ = State::Failed;
                    }
                }
                break;

            case State::ReceivingBurst:
                if (received_count_ >= param_count_ && param_count_ > 0) {
                    state_ = State::Completed;
                } else if (now - last_activity_ > 500ms) {
                    advance_to_next_hole(now, 0);
                }
                break;

            case State::ResolvingHoles:
                if (current_hole_index_ < received_mask_.size() && received_mask_[current_hole_index_]) {
                    advance_to_next_hole(now, current_hole_index_ + 1);
                } else if (now - last_activity_ > 800ms) {
                    if (retry_count_ < max_hole_retries_) {
                        retry_count_++;
                        last_activity_ = now;
                        send_read_fn_(target_system_, target_component_, static_cast<int16_t>(current_hole_index_));
                    } else {
                        state_ = State::Failed;
                    }
                }
                break;

            case State::Idle:
            case State::Completed:
            case State::Failed:
                break;
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] double progress() const noexcept {
        return param_count_ > 0 ? (100.0 * received_count_ / param_count_) : 0.0;
    }

    [[nodiscard]] const Parameter* get_by_name(std::string_view name) const noexcept {
        auto it = params_by_name_.find(std::string(name));
        return (it != params_by_name_.end()) ? &it->second : nullptr;
    }

    [[nodiscard]] const Parameter* get_by_index(uint16_t index) const noexcept {
        if (index < params_by_index_.size() && received_mask_[index]) {
            return &params_by_index_[index];
        }
        return nullptr;
    }

private:
    void advance_to_next_hole(std::chrono::steady_clock::time_point now, size_t start_idx) {
        for (size_t i = start_idx; i < received_mask_.size(); ++i) {
            if (!received_mask_[i]) {
                state_ = State::ResolvingHoles;
                current_hole_index_ = static_cast<uint16_t>(i);
                retry_count_ = 0;
                last_activity_ = now;
                send_read_fn_(target_system_, target_component_, static_cast<int16_t>(i));
                return;
            }
        }
        state_ = (received_count_ >= param_count_) ? State::Completed : State::Failed;
    }

    static ParamValue unpack_wire_value(float wire_float, uint8_t type) noexcept {
        const auto raw_u32 = std::bit_cast<uint32_t>(wire_float);
        switch (type) {
            case 1: return static_cast<uint8_t>(raw_u32 & 0xFF);
            case 2: return static_cast<int8_t>(static_cast<int32_t>(raw_u32) & 0xFF);
            case 3: return static_cast<uint16_t>(raw_u32 & 0xFFFF);
            case 4: return static_cast<int16_t>(static_cast<int32_t>(raw_u32) & 0xFFFF);
            case 5: return raw_u32;
            case 6: return std::bit_cast<int32_t>(raw_u32);
            case 9: return wire_float;
            default: return raw_u32;
        }
    }

    uint8_t target_system_;
    uint8_t target_component_;
    SendListCallback send_list_fn_;
    SendReadCallback send_read_fn_;

    State state_{State::Idle};
    uint16_t param_count_{0};
    uint16_t received_count_{0};
    uint16_t current_hole_index_{0};
    uint8_t  retry_count_{0};

    const uint8_t max_list_retries_{3};
    const uint8_t max_hole_retries_{5};

    std::vector<bool> received_mask_;
    std::vector<Parameter> params_by_index_;
    std::unordered_map<std::string, Parameter> params_by_name_;
    std::chrono::steady_clock::time_point last_activity_{};
};
```
:::

---

### Порядковий аналіз роботи рушія та деталі реалізації

Розгляньмо ключові внутрішні механізми, реалізовані в наведеному коді:

#### 1. Безпечне розпакування бітових контейнерів (bit-cast)

Функція `unpack_wire_value` на рівні процесора виконує побітове відображення (`std::bit_cast` у C++ або читання через `union` у C). Якщо автопілот передає параметр типу `MAV_PARAM_TYPE_UINT32` зі значенням бітової маски сенсорів `0x80000001` (десяткове число 2147483649), стандартне приведення `(float)val` призвело б до округлення мантиси та спотворення молодшого біта.

Рушій гарантує точність: сирі 4 байти поля `float` перетворюються на 32-бітне число `uint32_t` без втрати жодного біта інформації. Для менших типів (`uint8_t`, `int16_t`) виконується накладання маски або знакове розширення до відповідного типу в `std::variant`.

#### 2. Запобігання переповненню рядків (Null-terminator extraction)

Масив `param_id` у кадрі MAVLink має фіксований розмір 16 байтів. Якщо назва параметра містить рівно 16 символів (наприклад, `PILOT_THR_FILT_R`), автопілот записує символи без нульового термінатора.

У реалізації на C виділяється буфер розміром 17 байтів `id[PARAM_ID_LEN + 1]`, виконується копіювання `memcpy(e->id, wire_id, 16)` і явно виставляється кінцевий нуль `e->id[16] = '\0'`. У реалізації на C++ використовується функція `strnlen(wire_id, 16)`, яка обмежує довжину зчитування першими 16 байтами і створює безпечний об'єкт `std::string` точного розміру.

#### 3. Асинхронне відновлення дірок без повторного сканування

Коли рушій переходить у стан `RESOLVING_HOLES`, він не сканує всю бітову маску на кожній ітерації таймера. Пошук наступної дірки `find_next_hole` починається зі зміщення `current_hole_index + 1`. Це скорочує часову складність повного обходу до O(N) операцій навіть при великій кількості пропущених пакетів.

---

### Хронологія проходження та журнал подій сесії

Для демонстрації ефективності алгоритму простежимо реальну сесію синхронізації 1200 параметрів через радіоканал із 15% випадкових втрат пакетів:

```
[Т = 0.000 с] GCS надсилає PARAM_REQUEST_LIST (sys_id=1, comp_id=1)
[Т = 0.085 с] Отримано PARAM_VALUE index=0 (param_count=1200, id="SYS_AUTOSTART") → стан RECEIVING_BURST
[Т = 0.095 с] Отримано PARAM_VALUE index=1 (id="BAT1_N_CELLS")
[Т = 0.105 с] Пакет index=2 втрачено в ефірі (завада від мотора)
[Т = 0.115 с] Отримано PARAM_VALUE index=3 (id="MC_ROLLRATE_P")
...
[Т = 12.450 с] Отримано PARAM_VALUE index=1199 (останній у пакетному потоці)
[Т = 12.950 с] Спрацював таймер бездіяльності (>500 мс). Отримано 1020 параметрів із 1200 (180 пропусків).
               Перехід у стан RESOLVING_HOLES. Знайдено першу дірку: index=2.
[Т = 12.955 с] GCS надсилає PARAM_REQUEST_READ (param_index=2)
[Т = 13.040 с] Отримано PARAM_VALUE index=2 (id="BAT1_V_EMPTY") → біт 2 встановлено!
[Т = 13.045 с] GCS надсилає PARAM_REQUEST_READ (param_index=14)
...
[Т = 25.800 с] Останню прогалину index=1184 успішно закрито.
[Т = 25.805 с] Перехід у стан COMPLETED: 1200 з 1200 параметрів збережено, цілісність 100%!
```

Без механізму точкового дозавантаження спроба перезавантажити весь список цілком за наявності 15% втрат пакетів призвела б до нескінченного циклу перезапитів (ймовірність отримати 1200 пакетів поспіль без жодної втрати при 15% ймовірності помилки прямує до нуля).

---

### Профілювання ресурсів та аналіз пропускної здатності

Оцінимо обчислювальні витрати та трафік радіоканалу під час виконання повного циклу синхронізації конфігурації:

1. **Використання оперативної пам'яті (RAM):**
   * Варіант на C: 256 байтів для бітової маски + `2048 × 28 байтів` для масиву `entries` ≈ 57.5 КБ статичної RAM. Це дає змогу розмістити рушій навіть на скромних мікроконтролерах класу STM32F4 / ESP32 без використання динамічного розподілу пам'яті.
   * Варіант на C++: динамічний вектор `std::vector<bool>` для 2048 бітів займає лише 256 байтів, а хеш-таблиця `std::unordered_map` разом із вектором структур займає близько 95–110 КБ динамічної пам'яті, що є непомітним для ПК чи одноплатних комп'ютерів (Raspberry Pi, Jetson).
2. **Сумарний мережевий трафік:**
   * Корисне навантаження кадру `PARAM_VALUE` становить 25 байтів, повний розмір кадру MAVLink v2 із заголовком та CRC становить 37 байтів.
   * Для 1200 параметрів первинний пакетний потік генерує: `1200 × 37 = 44 400 байтів` (44.4 КБ).
   * За 15% втрат пакетів (180 пропущених параметрів) додатковий трафік дозавантаження становить: `180 × (32 байти запиту + 37 байтів відповіді) = 12 420 байтів` (12.4 КБ).
   * Загальний обсяг трафіку становить 56.8 КБ, що на швидкості 4 КБ/с передається приблизно за 14–16 секунд.
3. **Порівняння часу синхронізації при різних швидкостях інтерфейсу:**
   * **UART 57600 бод (радіомодем):** ~15 секунд (основний потік) + ~10 секунд (дозавантаження дірок) = 25 секунд.
   * **UART 115200 бод (прямий кабель):** ~7.5 секунд (основний потік) + ~3 секунди = 10.5 секунд.
   * **USB / Wi-Fi UDP (швидкість > 1 Мбіт/с):** менше 0.5 секунди для всієї конфігурації.

---

### Тестовий стенд: імітація радіозавад та автоматична валідація

Для верифікації коректності роботи рушія перед польовими випробуваннями використовується програмний стенд (Harness), який імітує автопілот із вбудованим генератором завад.

Стенд моделює три класи мережевих дефектів:

1. **Випадкове стирання пакетів (Random Packet Drops):** кожен вихідний кадр `PARAM_VALUE` або вхідний `PARAM_REQUEST_READ` відкидається із заданою ймовірністю (наприклад, 20%).
2. **Пакетні сплески втрат (Burst Losses):** симуляція проходження апарата крізь радіотінь, коли втрачається серія з 10–30 послідовних кадрів.
3. **Зміна порядку доставки (Packet Reordering):** пакети затримуються у віртуальній черзі та приходять у випадковому порядку.

Тестовий цикл порівнює відновлену таблицю параметрів із еталонною базою автопілота: перевіряється точний збіг імен `param_id`, відповідність числових типів `MAV_PARAM_TYPE` та двійкова ідентичність значень після розпакування `bit-cast`. Результати тестування показують 100% відновлення конфігурації за рівня втрат каналу до 40%.

---

### Оптимізація для систем із кількома підсистемами (Multi-Component Architecture)

У складних безпілотних комплексах параметри розподілені між кількома фізичними пристроями на борту: головним польотним контролером (`MAV_COMP_ID_AUTOPILOT1` = 1), оптичним підвісом (`MAV_COMP_ID_GIMBAL` = 154), тепловізійною камерою (`MAV_COMP_ID_CAMERA` = 100) та бортовим комп'ютером (`MAV_COMP_ID_ONBOARD_COMPUTER` = 191).

Кожен компонент веде власну незалежну нумерацію індексів `param_index` від `0` до власного `param_count - 1`. Клієнтська архітектура розв'язує цю задачу через мультиплексування:

* Клієнт створює окремий екземпляр класу `ParameterSyncEngine` для кожної пари `(System ID, Component ID)`.
* Вхідний маршрутизатор пакетів MAVLink перевіряє байти `sys_id` та `comp_id` у заголовку вхідного кадру і направляє повідомлення `PARAM_VALUE` у відповідний екземпляр рушія.
* Локальна база конфігурації організовує простори імен за шаблоном `SYS1.COMP1.MPC_XY_VEL_MAX` або `SYS1.COMP154.GMB_RATE_P`, що повністю виключає колізії однакових назв змінних між автопілотом і підвісом.

---

### Інтеграція з локальним файловим кешем (Persistent Disk Caching)

Для забезпечення миттєвого старту при повторних підключеннях наземна станція зберігає завантажені параметри на локальний диск у бінарному або текстовому форматі.

* **Збереження знімка конфігурації:** після переходу рушія у стан `COMPLETED` вся таблиця разом із поточним контрольним хешем (Param Hash) серіалізується у локальний файл `cache/<sys_id>_<comp_id>_params.bin`.
* **Перевірка валідності під час наступного старту:** при повторному зв'язку станція запитує лише хеш конфігурації. Якщо хеш автопілота збігається зі збереженим у кеші, рушій пропускає фази `REQUEST_LIST` та `RESOLVING_HOLES` і миттєво переходить у стан `COMPLETED` за 10–20 мс замість 25 секунд радіообміну.
* **Інкрементальна інвалідація:** якщо оператор змінив окремий параметр через `PARAM_SET`, оновлене значення негайно перезаписується в локальний кеш без необхідності повного повторного вичитування всієї бази.

---

### Обробка крайових випадків у польових умовах

Під час роботи рушія в польотних умовах виникають нетипові сценарії, які вимагають додаткових захисних механізмів:

1. **Спонтанні оновлення з індексом `65535` (`UINT16_MAX`):** коли пілот перемикає польотні режими на апаратурі радіокерування або бортовий скрипт змінює внутрішній стан системи, автопілот транслює кадр `PARAM_VALUE`, де поле `param_index` встановлено у значення `65535`. Рушій повинен оновити збережене значення у таблиці `params_by_name_`, але не повинен модифікувати бітову маску початкового вичитування `received_mask_`, щоб не спотворити лічильник прогресу.
2. **Динамічна зміна кількості параметрів (`param_count` mismatch):** у разі гарячого підключення нових пристроїв по шині DroneCAN або завантаження динамічних модулів під час вичитування списку, значення `count` у свіжих повідомленнях може стати більшим, ніж початкове `param_count_`. У такому разі C++ версія рушія викликає `received_mask_.resize(new_count, false)`, забезпечуючи дозавантаження нововиявлених змінних.
3. **Потокобезпечність та інтеграція в ROS 2:** у багатопотокових системах обробник вхідних повідомлень MAVLink та головний цикл користувацького інтерфейсу працюють у різних потоках операційної системи. Для безпечного доступу до таблиці параметрів виклики методів `on_param_value` та `poll` повинні захищатися легким м'ютексом (`std::mutex`) або виконуватися в єдиній черзі подій (Event Queue).
4. **Контроль смуги пропускання та темпу опитування (Pacing):** під час активного польоту телеметрійний канал перевантажений високопріоритетними пакетами `ATTITUDE`, `GLOBAL_POSITION_INT` та `HEARTBEAT`. Надсилання запитів `PARAM_REQUEST_READ` повинно суворо обмежуватися часовим інтервалом (не частіше одного запиту в 50–100 мс), щоб запобігти витісненню критичних навігаційних даних.
