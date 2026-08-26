# ⚙️ Реалізація автономного контролера та рушія реконсиліації стану

При розробці автономного вбудованого вузла ключове інженерне завдання полягає у створенні детермінованого контуру керування, який не блокується операціями вводу/виводу мережевого стека, гарантовано зберігає критичні події під час аварійного вимкнення зв'язку та безконфліктно узгоджує стан із хмарним сервером після відновлення каналу.

Будь-яка спроба використати стандартні високорівневі бібліотеки з динамічним виділенням пам'яті (`malloc`, `new`, динамічні черги `std::queue` на базі зв'язних списків) у вбудованому контурі призводить до непередбачуваної фрагментації оперативної пам'яті (SRAM) і ризику відмови через вичерпання купи (англ. *heap exhaustion*) якраз під час тривалого офлайну, коли кількість накопичених подій досягає максимуму. Тому автономний контролер будується на принципі суворо статичного розподілу пам'яті з фіксованими розмірами структур і гарантованими часовими рамками виконання кожної операції `O(1)`.

### Архітектура та функціональні модулі

Реалізація автономної системи розбивається на три ізольовані підсистеми:
1. **Пріоритезований кільцевий буфер подій (Multi-Priority Ring Buffer):** 
   Керує збереженням інформації з різними політиками витіснення. Аварійні події рівня 0 (Alarm) ніколи не перезаписуються старими записами: якщо виділений буфер аварій заповнено, нові аварії відхиляються з фіксацією апаратного прапорця переповнення, але наявні критичні записи гарантовано доходять до оператора. Події аудиту рівня 1 (Audit) та телеметрії рівня 2 (Telemetry) працюють за принципом кільцевого буфера FIFO з витісненням найстаріших елементів та обов'язковою інкрементацією лічильника втрат `dropped_count`.
2. **Локальний рушій правил і розкладів (Local Rule Engine):** 
   Автономний автомат станів, що працює на кожному кроці квантування таймера (наприклад, кожні 100 мс). Він виконує фільтрацію шумів сенсора, розраховує гістерезисні межі увімкнення та вимкнення силових реле, контролює захисні інтервали часу (запобігання занадто частій комутації навантаження) та фіксує перехід у стан аварійного блокування (E-Stop).
3. **Рушій семантичної реконсиліації станів (State Reconciler):** 
   Відповідає за безпечний перехід між режимами `Offline` та `Online`. Після відновлення зв'язку він виконує рукостискання з бекендом, зіставляє локальне покоління стану `state_generation` із хмарною версією, відхиляє небезпечні дистанційні команди при активній локальній аварії та поетапно викачує буферизовані журнали за пріоритетом.

Нижче наведено повний вихідний код автономного контролера двома мовами: на чистому C99 без динамічної пам'яті та на ідіоматичному сучасному C++20 із суворою типізацією, семантикою `std::expected` та шаблонними кільцевими буферами.

:::tabs
```c
/* =========================================================================
 * C99 Реалізація автономного контролера для вбудованих систем (No Heap)
 * ========================================================================= */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_RULES            8
#define TELEMETRY_QUEUE_SIZE 32
#define AUDIT_QUEUE_SIZE     16
#define ALARM_QUEUE_SIZE     8

/* Рівні критичності подій */
typedef enum {
    EVENT_PRIO_ALARM = 0,    /* Аварія: жорстке збереження, найвищий пріоритет */
    EVENT_PRIO_AUDIT = 1,    /* Аудит: зміна режиму, відкриття замка */
    EVENT_PRIO_TELEMETRY = 2 /* Телеметрія: періодичні дані, проріджування */
} event_prio_t;

/* Структура збереженої події */
typedef struct {
    uint32_t timestamp_s;    /* Локальний час RTC (Unix секунди) */
    uint32_t sequence_id;    /* Монотонний лічильник події */
    uint16_t event_code;     /* Код події (наприклад, 0xE001 - Overheat) */
    int16_t  payload_val;    /* Значення датчика або аргумент */
    uint8_t  priority;       /* event_prio_t */
    uint8_t  acknowledged;   /* Прапорець підтвердження бекендом */
} offline_event_t;

/* Структура кільцевого буфера подій одного пріоритету */
typedef struct {
    offline_event_t buffer[TELEMETRY_QUEUE_SIZE];
    uint16_t head;
    uint16_t tail;
    uint16_t count;
    uint16_t capacity;
    uint32_t dropped_count;  /* Лічильник витіснених записів при переповненні */
} event_ring_t;

/* Правило локального автомата */
typedef struct {
    int16_t  temp_threshold_c_x10; /* Поріг увімкнення (наприклад, 22.0 C -> 220) */
    int16_t  temp_hysteresis_c_x10;/* Гістерезис (наприклад, 1.5 C -> 15) */
    uint32_t safe_mode_timeout_s;  /* Час без зв'язку до переходу у Fail-Safe */
    bool     heater_forced_off;    /* Захисне блокування */
} local_rules_t;

/* Актуальний та бажаний стан пристрою */
typedef struct {
    uint32_t state_version;        /* Локальний лічильник мутацій */
    uint32_t cloud_known_version;  /* Остання версія, підтверджена хмарою */
    bool     heater_active;        /* Поточний фізичний стан нагрівача */
    bool     alarm_latched;        /* Стан аварійного блокування */
    int16_t  last_temperature;     /* Останній вимір температури */
} device_state_t;

/* Головний контекст автономного вузла */
typedef struct {
    local_rules_t   rules;
    device_state_t  state;
    event_ring_t    q_alarm;
    event_ring_t    q_audit;
    event_ring_t    q_telemetry;
    uint32_t        global_seq;
    uint32_t        offline_duration_s;
    bool            network_online;
} offline_controller_t;

/* Ініціалізація кільцевого буфера */
static void ring_init(event_ring_t *ring, uint16_t capacity) {
    memset(ring->buffer, 0, sizeof(ring->buffer));
    ring->head = 0;
    ring->tail = 0;
    ring->count = 0;
    ring->capacity = capacity;
    ring->dropped_count = 0;
}

/* Запис події в буфер відповідного пріоритету */
static bool ring_push(event_ring_t *ring, const offline_event_t *ev, bool allow_overwrite) {
    if (ring->count >= ring->capacity) {
        if (!allow_overwrite) {
            /* Для критичних аварій: відхиляємо, якщо немає права перезапису */
            ring->dropped_count++;
            return false;
        }
        /* Для телеметрії та аудиту: зсуваємо хвіст (витісняємо найстаріший елемент) */
        ring->tail = (ring->tail + 1) % ring->capacity;
        ring->count--;
        ring->dropped_count++;
    }
    ring->buffer[ring->head] = *ev;
    ring->head = (ring->head + 1) % ring->capacity;
    ring->count++;
    return true;
}

/* Вичитування події з черги без видалення */
static bool ring_peek(event_ring_t *ring, offline_event_t *out_ev) {
    if (ring->count == 0) {
        return false;
    }
    *out_ev = ring->buffer[ring->tail];
    return true;
}

/* Підтвердження передачі та видалення з черги */
static void ring_pop(event_ring_t *ring) {
    if (ring->count > 0) {
        ring->tail = (ring->tail + 1) % ring->capacity;
        ring->count--;
    }
}

/* Ініціалізація контролера */
void offline_controller_init(offline_controller_t *ctrl) {
    memset(ctrl, 0, sizeof(*ctrl));
    ctrl->rules.temp_threshold_c_x10 = 220;  /* 22.0 °C */
    ctrl->rules.temp_hysteresis_c_x10 = 15;  /* 1.5 °C */
    ctrl->rules.safe_mode_timeout_s = 3600;  /* 1 година */
    ctrl->rules.heater_forced_off = false;

    ctrl->state.state_version = 1;
    ctrl->state.cloud_known_version = 0;
    ctrl->state.heater_active = false;
    ctrl->state.alarm_latched = false;

    ring_init(&ctrl->q_alarm, ALARM_QUEUE_SIZE);
    ring_init(&ctrl->q_audit, AUDIT_QUEUE_SIZE);
    ring_init(&ctrl->q_telemetry, TELEMETRY_QUEUE_SIZE);
}

/* Локальний контур керування (виклик у RTOS-задачі або головному циклі раз на 100 мс) */
void offline_controller_process_loop(offline_controller_t *ctrl,
                                     int16_t current_temp_x10,
                                     uint32_t rtc_now_s,
                                     uint32_t dt_ms) {
    ctrl->state.last_temperature = current_temp_x10;

    if (!ctrl->network_online) {
        ctrl->offline_duration_s += (dt_ms / 1000);
    } else {
        ctrl->offline_duration_s = 0;
    }

    /* 1. Захисна перевірка на критичний перегрів (> 50.0 °C) */
    if (current_temp_x10 > 500 && !ctrl->state.alarm_latched) {
        ctrl->state.alarm_latched = true;
        ctrl->state.heater_active = false;
        ctrl->state.state_version++;

        offline_event_t ev = {
            .timestamp_s = rtc_now_s,
            .sequence_id = ++ctrl->global_seq,
            .event_code = 0xE001, /* Emergency Overheat */
            .payload_val = current_temp_x10,
            .priority = EVENT_PRIO_ALARM,
            .acknowledged = 0
        };
        ring_push(&ctrl->q_alarm, &ev, false);
        return;
    }

    /* 2. Якщо зафіксовано аварію або захисне блокування — актуатор вимкнено */
    if (ctrl->state.alarm_latched || ctrl->rules.heater_forced_off) {
        ctrl->state.heater_active = false;
        return;
    }

    /* 3. Автономний гістерезисний терморегулятор */
    int16_t target = ctrl->rules.temp_threshold_c_x10;
    int16_t hyst = ctrl->rules.temp_hysteresis_c_x10;

    bool prev_heater = ctrl->state.heater_active;
    if (current_temp_x10 < (target - hyst)) {
        ctrl->state.heater_active = true;
    } else if (current_temp_x10 > (target + hyst)) {
        ctrl->state.heater_active = false;
    }

    /* Фіксація зміни стану в аудит-лозі */
    if (prev_heater != ctrl->state.heater_active) {
        ctrl->state.state_version++;
        offline_event_t audit_ev = {
            .timestamp_s = rtc_now_s,
            .sequence_id = ++ctrl->global_seq,
            .event_code = 0xA010, /* State Transition */
            .payload_val = (int16_t)ctrl->state.heater_active,
            .priority = EVENT_PRIO_AUDIT,
            .acknowledged = 0
        };
        ring_push(&ctrl->q_audit, &audit_ev, true);
    }
}

/* Періодичне збереження телеметрії з фільтрацією Deadband */
void offline_controller_log_telemetry(offline_controller_t *ctrl,
                                      uint32_t rtc_now_s,
                                      int16_t current_temp_x10) {
    static int16_t last_logged_temp = -9999;
    int16_t diff = current_temp_x10 - last_logged_temp;
    if (diff < 0) diff = -diff;

    /* Зберігаємо лише якщо температура змінилася більш ніж на 0.5 °C (5 одиниць) */
    if (diff >= 5 || last_logged_temp == -9999) {
        last_logged_temp = current_temp_x10;
        offline_event_t telem_ev = {
            .timestamp_s = rtc_now_s,
            .sequence_id = ++ctrl->global_seq,
            .event_code = 0x1001, /* Telemetry sample */
            .payload_val = current_temp_x10,
            .priority = EVENT_PRIO_TELEMETRY,
            .acknowledged = 0
        };
        ring_push(&ctrl->q_telemetry, &telem_ev, true);
    }
}

/* Процедура реконсиліації: обробка отриманого від хмари бажаного стану (Desired State) */
bool offline_controller_reconcile_cloud_command(offline_controller_t *ctrl,
                                                uint32_t cloud_version,
                                                int16_t new_temp_target_x10,
                                                bool force_heater_off) {
    /* ПРАВИЛО БЕЗПЕКИ 1: Якщо на пристрої активна апаратна аварія (Overheat),
     * хмара не може скинути її звичайною зміною уставки без прямого скидання тривоги */
    if (ctrl->state.alarm_latched && !force_heater_off) {
        return false; /* Конфлікт: локальна безпека має абсолютний пріоритет */
    }

    /* ПРАВИЛО УСТАВОК 2: Якщо версія конфігурації з хмари новіша — застосовуємо */
    if (cloud_version > ctrl->state.cloud_known_version) {
        ctrl->rules.temp_threshold_c_x10 = new_temp_target_x10;
        ctrl->rules.heater_forced_off = force_heater_off;
        ctrl->state.cloud_known_version = cloud_version;
        ctrl->state.state_version = cloud_version + 1;
        return true;
    }

    return false;
}

/* Дренаж черг після відновлення зв'язку: вибирає наступну найпріоритетнішу подію */
bool offline_controller_get_next_event_to_sync(offline_controller_t *ctrl,
                                               offline_event_t *out_ev,
                                               event_ring_t **out_source_ring) {
    /* Спершу аварії */
    if (ring_peek(&ctrl->q_alarm, out_ev)) {
        *out_source_ring = &ctrl->q_alarm;
        return true;
    }
    /* Потім аудит */
    if (ring_peek(&ctrl->q_audit, out_ev)) {
        *out_source_ring = &ctrl->q_audit;
        return true;
    }
    /* Насамкінець телеметрія */
    if (ring_peek(&ctrl->q_telemetry, out_ev)) {
        *out_source_ring = &ctrl->q_telemetry;
        return true;
    }
    return false;
}
```
```cpp
/* =========================================================================
 * C++20/C++23 Ідіоматична реалізація автономного контролера
 * ========================================================================= */
#include <array>
#include <span>
#include <cstdint>
#include <optional>
#include <chrono>
#include <algorithm>
#include <concepts>
#include <expected>

namespace embedded::edge {

enum class EventPriority : uint8_t {
    Alarm = 0,     // Жорстке збереження без переповнення
    Audit = 1,     // Журнал операцій, кільцевий FIFO
    Telemetry = 2  // Періодичні виміри, витіснення та деградація
};

enum class ReconcileError {
    SafetyConflict,
    StaleVersion,
    StorageFull
};

struct OfflineEvent {
    std::chrono::seconds timestamp{0};
    uint32_t             sequence_id{0};
    uint16_t             event_code{0};
    int16_t              payload_val{0};
    EventPriority        priority{EventPriority::Telemetry};
    bool                 acknowledged{false};
};

template <size_t Capacity, bool AllowOverwrite>
class FixedRingBuffer {
public:
    constexpr FixedRingBuffer() = default;

    [[nodiscard]] bool push(const OfflineEvent& ev) noexcept {
        if (m_count >= Capacity) {
            if constexpr (!AllowOverwrite) {
                m_dropped_count++;
                return false;
            } else {
                m_tail = (m_tail + 1) % Capacity;
                m_count--;
                m_dropped_count++;
            }
        }
        m_storage[m_head] = ev;
        m_head = (m_head + 1) % Capacity;
        m_count++;
        return true;
    }

    [[nodiscard]] std::optional<OfflineEvent> peek() const noexcept {
        if (m_count == 0) return std::nullopt;
        return m_storage[m_tail];
    }

    void pop() noexcept {
        if (m_count > 0) {
            m_tail = (m_tail + 1) % Capacity;
            m_count--;
        }
    }

    [[nodiscard]] size_t size() const noexcept { return m_count; }
    [[nodiscard]] bool empty() const noexcept { return m_count == 0; }
    [[nodiscard]] uint32_t dropped_count() const noexcept { return m_dropped_count; }

private:
    std::array<OfflineEvent, Capacity> m_storage{};
    size_t m_head{0};
    size_t m_tail{0};
    size_t m_count{0};
    uint32_t m_dropped_count{0};
};

struct LocalRules {
    int16_t temp_threshold_c_x10{220};  // 22.0 °C
    int16_t temp_hysteresis_c_x10{15};  // 1.5 °C
    std::chrono::seconds safe_timeout{3600};
    bool heater_forced_off{false};
};

struct DeviceState {
    uint32_t state_version{1};
    uint32_t cloud_known_version{0};
    bool     heater_active{false};
    bool     alarm_latched{false};
    int16_t  last_temperature{0};
};

class SovereignOfflineController {
public:
    static constexpr size_t AlarmQueueCap     = 8;
    static constexpr size_t AuditQueueCap     = 16;
    static constexpr size_t TelemetryQueueCap = 32;

    SovereignOfflineController() = default;

    // Циклічна обробка фізичного процесу
    void process_control_loop(int16_t current_temp_x10,
                              std::chrono::seconds rtc_now,
                              std::chrono::milliseconds dt) noexcept {
        m_state.last_temperature = current_temp_x10;

        if (!m_network_online) {
            m_offline_duration += std::chrono::duration_cast<std::chrono::seconds>(dt);
        } else {
            m_offline_duration = std::chrono::seconds{0};
        }

        // 1. Перевірка на критичний перегрів
        if (current_temp_x10 > 500 && !m_state.alarm_latched) {
            m_state.alarm_latched = true;
            m_state.heater_active = false;
            m_state.state_version++;

            m_alarms.push(OfflineEvent{
                .timestamp = rtc_now,
                .sequence_id = ++m_global_seq,
                .event_code = 0xE001,
                .payload_val = current_temp_x10,
                .priority = EventPriority::Alarm,
                .acknowledged = false
            });
            return;
        }

        if (m_state.alarm_latched || m_rules.heater_forced_off) {
            m_state.heater_active = false;
            return;
        }

        // 2. Локальний гістерезисний регулятор
        const auto target = m_rules.temp_threshold_c_x10;
        const auto hyst   = m_rules.temp_hysteresis_c_x10;
        const bool prev_heater = m_state.heater_active;

        if (current_temp_x10 < (target - hyst)) {
            m_state.heater_active = true;
        } else if (current_temp_x10 > (target + hyst)) {
            m_state.heater_active = false;
        }

        if (prev_heater != m_state.heater_active) {
            m_state.state_version++;
            m_audits.push(OfflineEvent{
                .timestamp = rtc_now,
                .sequence_id = ++m_global_seq,
                .event_code = 0xA010,
                .payload_val = static_cast<int16_t>(m_state.heater_active),
                .priority = EventPriority::Audit,
                .acknowledged = false
            });
        }
    }

    // Періодична телеметрія з дельта-фільтром
    void log_telemetry(std::chrono::seconds rtc_now, int16_t current_temp_x10) noexcept {
        const int16_t diff = std::abs(current_temp_x10 - m_last_logged_temp);
        if (diff >= 5 || m_last_logged_temp == -9999) {
            m_last_logged_temp = current_temp_x10;
            m_telemetry.push(OfflineEvent{
                .timestamp = rtc_now,
                .sequence_id = ++m_global_seq,
                .event_code = 0x1001,
                .payload_val = current_temp_x10,
                .priority = EventPriority::Telemetry,
                .acknowledged = false
            });
        }
    }

    // Семантична реконсиліація стану при отриманні наказу з бекенду
    [[nodiscard]] std::expected<void, ReconcileError> reconcile_cloud_state(
        uint32_t cloud_version,
        int16_t new_temp_target_x10,
        bool force_heater_off) noexcept {
        
        // Локальна аварія переважає дистанційне керування
        if (m_state.alarm_latched && !force_heater_off) {
            return std::unexpected(ReconcileError::SafetyConflict);
        }

        if (cloud_version <= m_state.cloud_known_version) {
            return std::unexpected(ReconcileError::StaleVersion);
        }

        m_rules.temp_threshold_c_x10 = new_temp_target_x10;
        m_rules.heater_forced_off = force_heater_off;
        m_state.cloud_known_version = cloud_version;
        m_state.state_version = cloud_version + 1;

        return {};
    }

    // Отримання чергової події для вивантаження
    [[nodiscard]] std::optional<OfflineEvent> fetch_next_sync_event() const noexcept {
        if (auto ev = m_alarms.peek()) return ev;
        if (auto ev = m_audits.peek()) return ev;
        if (auto ev = m_telemetry.peek()) return ev;
        return std::nullopt;
    }

    // Підтвердження збереження подією бекендом
    void acknowledge_top_event() noexcept {
        if (!m_alarms.empty()) {
            m_alarms.pop();
        } else if (!m_audits.empty()) {
            m_audits.pop();
        } else if (!m_telemetry.empty()) {
            m_telemetry.pop();
        }
    }

    void set_network_status(bool online) noexcept { m_network_online = online; }
    [[nodiscard]] const DeviceState& state() const noexcept { return m_state; }

private:
    LocalRules   m_rules{};
    DeviceState  m_state{};
    FixedRingBuffer<AlarmQueueCap, false>     m_alarms{};     // Без перезапису
    FixedRingBuffer<AuditQueueCap, true>      m_audits{};     // FIFO з витісненням
    FixedRingBuffer<TelemetryQueueCap, true>  m_telemetry{};  // FIFO з деградацією

    uint32_t             m_global_seq{0};
    int16_t              m_last_logged_temp{-9999};
    std::chrono::seconds m_offline_duration{0};
    bool                 m_network_online{false};
};

} // namespace embedded::edge
```
:::

### Інженерний розбір ключових механізмів коду

Розгляньмо тонкощі представлених реалізацій, що забезпечують детермінізм і стійкість системи в реальних польових умовах:

#### 1. Безпека типів і шаблонна семантика в C++
У варіанті на C++ клас `FixedRingBuffer` параметризується не лише розміром `Capacity`, а й поведінкою при переповненні: `bool AllowOverwrite`.
- Для черги аварій `m_alarms` значення прапорця скомпільовано як `false`. Завдяки конструкції `if constexpr (!AllowOverwrite)` компілятор генерує код, який при заповненні черги збільшує лічильник `m_dropped_count` і повертає `false`, не чіпаючи наявні аварійні записи.
- Для черги аудиту та телеметрії значення дорівнює `true`, що розгортається у витіснення найстарішого елемента шляхом інкременту покажчика хвоста `m_tail = (m_tail + 1) % Capacity`.

Це виключає необхідність тримати динамічні перевірки режимів у пам'яті під час виконання і гарантує, що розробник не помилиться з політикою переповнення для критичних аварій на етапі компіляції.

#### 2. Обробка помилок без винятків: `std::expected`
У вбудованих системах використання винятків C++ (`try / catch / throw`) зазвичай заборонене через непередбачуваний розмір таблиць розгортання стека (англ. *stack unwinding tables*) та оверхед на пам'ять. 
Метод `reconcile_cloud_state` повертає `std::expected<void, ReconcileError>`. Це дозволяє явно декларувати можливі відмови:
- `ReconcileError::SafetyConflict` — пристрій заблоковано через фізичну аварію перегріву, і команда хмари на примусовий запуск відхилена.
- `ReconcileError::StaleVersion` — повідомлення з хмари прийшло із застарілим номером покоління (наприклад, через затримку в чергах брокера) і не повинно перезаписувати свіжішу локальну конфігурацію.

#### 3. Атомарність та інваріанти послідовності (Sequence Tracking)
Кожна подія отримує монотонний ідентифікатор `sequence_id`, який інкрементується глобальним лічильником `global_seq`. 
При вивантаженні даних після відновлення зв'язку сервер відправляє підтвердження `ACK` із зазначенням саме цього ідентифікатора. Функція `acknowledge_top_event()` видаляє елемент із черги лише тоді, коли сервер підтвердив успішне збереження у своїй базі даних. Якщо під час дренажу черги зв'язок обривається вдруге, пристрій зберігає всі непідтверджені події і повторить їхню передачу під час наступного підключення без втрати хронології.

#### 4. Багатозадачна інтеграція в RTOS
У реальній операційній системі реального часу (FreeRTOS, Zephyr RTOS) цей модуль інтегрується двома задачами:
- **Task 1: `ControlTask` (High Priority, 100 Гц):** Викликає `process_control_loop()` та `log_telemetry()`. Ця задача має найвищий пріоритет і ніколи не викликає функцій блокування на мережевих сокетах.
- **Task 2: `SyncTask` (Low Priority, Background):** Працює в нескінченному циклі з очікуванням події мережевого лінка. Вона вичитує події через `fetch_next_sync_event()`, пакує їх у TCP/TLS пакет, надсилає на сервер і після отримання відповіді викликає `acknowledge_top_event()`.

Взаємодія між задачами захищається легким м'ютексом або lock-free атомарними покажчиками `head` і `tail`, що виключає стан гонитви (англ. *race condition*) між контуром фізичного контролю та мережевим стеком.
