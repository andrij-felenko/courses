# ⚙️ Реалізація транзакційного завантажувача місій: скінченний автомат у коді

Завантаження польотної місії з наземної станції або бортового комп'ютера на автопілот — це не проста передача масиву байтів через сокет чи послідовний порт, а сувора транзакційна взаємодія за моделлю Stop-and-Wait з покроковим підтвердженням кожного елемента. Радіоканал телеметрії на частотах 433 МГц, 868 МГц чи 915 МГц постійно зазнає завад: окремі кадри губляться, затримуються в чергах радіомодемів або спотворюються шумом в ефірі. Якщо відправити всі точки маршруту одним суцільним потоком без очікування квитанцій, втрата хоча б одного пункту спричинить критичну дірку в польотному плані, а переповнення вхідного буфера мікроконтролера викличе збій обробки завдань реального часу.

Розберімо повну інженерну архітектуру завантажувача місій, реалізуймо асинхронний неблокуючий скінченний автомат на C, C++ та Python, розгляньмо взаємодію з низькорівневими буферами MAVLink, таймерами та проаналізуймо типові аварійні сценарії.

## Чому необхідний неблокуючий скінченний автомат

У вбудованих системах керування дроном (як у прошивках польотних контролерів ArduPilot чи PX4, так і в коді бортових комп'ютерів на базі Linux) мережева взаємодія виконується всередині головного циклу обробки подій (англ. *event loop*). Використання блокуючих функцій очікування на зразок `sleep()` або синхронних циклів очікування квитанції `while(!got_ack)` категорично неприпустиме з кількох критичних причин:

1. **Блокування потоків стабілізації:** На польотному контролері цикл стабілізації та оцінки орієнтації (EKF) працює з фіксованою частотою 400 Гц або 1000 Гц. Будь-яка синхронна затримка на очікування відповіді з радіоканалу призведе до пропуску тактів керування моторами та неминучого падіння апарата.
2. **Параліч супутніх протоколів:** Навіть на наземній станції керування (QGroundControl, Mission Planner) блокування потоку зв'язку зупинить прийом критичної телеметрії (`HEARTBEAT`, `ATTITUDE`, `GLOBAL_POSITION_INT`), заморозить інтерфейс оператора та заблокує обробку аварійних команд примусового переривання місії.
3. **Недетермінованість радіоканалу:** Час кругового обігу пакета (англ. *round-trip time*, RTT) на радіомодемах SiK Telemetry або ELRS коливається від 20 мілісекунд до 1.5 секунди залежно від відстані, рівня шуму та завантаженості каналу. Автомат повинен працювати виключно за подіями: спливання таймера або надходження чергового байта в приймальний буфер.

Тому завантажувач місій проектується як асинхронний скінченний автомат (англ. *finite-state machine*, FSM), керований двома основними входами:
- **Події таймера (Time Ticks):** функція `tick()`, яка викликається на кожній ітерації головного циклу, вимірює інтервал від останньої активності та ініціює повторну передачу пакетів у разі перевищення таймауту (`TIMEOUT_MS`).
- **Події прийому повідомлень (Message Ingress):** функція `handle_message()`, яка отримує розпарсені структури повідомлень MAVLink (`MISSION_REQUEST_INT` та `MISSION_ACK`) і виконує валідацію послідовності та перемикання станів.

## Детальний аналіз станів автомата завантаження

Кінцевий автомат завантажувача містить шість дискретних станів:

```
[IDLE] ────────────────────────────────────────────────────────┐
  │                                                            │
  │ start_upload(items)                                        │
  │ → надсилаємо MISSION_COUNT(N)                              │
  ▼                                                            │
[SEND_COUNT] ──(очікуємо перший запит seq=0)──► [WAIT_REQUEST] │
                                                    │ ▲        │
                   отримано REQUEST(seq < N-1)      │ │        │
                   надсилаємо ITEM(seq)             │ │        │
                   ─────────────────────────────────┘ │        │
                                                      │        │
                   отримано REQUEST(N-1)              │        │
                   надсилаємо останній ITEM(N-1)      │        │
                   ───────────────────────────────────┼────┐   │
                                                           │   │   │
                                                           ▼   │   │
                                                      [WAIT_ACK]│   │
                                                           │   │   │
                             отримано MISSION_ACK(ACCEPTED)│   │   │
                             ──────────────────────────────┼───┼───┤
                                                           │   │   │
                                                           ▼   ▼   ▼
                                                        [DONE] [FAILED]
```

Розгляньмо інваріанти кожного стану та правила переходів між ними:

1. **`IDLE` (Спокій):**
   - **Умова перебування:** Транзакція відсутня. Черга елементів порожня або скинута.
   - **Вхідна подія:** Виклик `start(items)`.
   - **Дії при переході:** Збереження масиву точок, перевірка ненульової довжини, ініціалізація індексу `expected_seq = 0`, скидання лічильника спроб `retry_count = 0`, фіксація поточного часу `last_action_ms`, надсилання пакету `MISSION_COUNT` у радіоканал.
   - **Цільовий стан:** `SEND_COUNT`.

2. **`SEND_COUNT` (Очікування старту транзакції автопілотом):**
   - **Умова перебування:** Автопілот отримав `MISSION_COUNT`, перевіряє наявність вільного місця в EEPROM/Flash і готує свій внутрішній буфер.
   - **Очікувана подія:** Надходження `MISSION_REQUEST_INT` із номером `seq = 0`.
   - **Дії при отриманні:** Відправлення `MISSION_ITEM_INT` для нульової точки, оновлення таймера, перехід у стан очікування наступних запитів.
   - **Таймаут:** Якщо автопілот не відповів за 1000 мс, `MISSION_COUNT` надсилається повторно (до 5 разів). При перевищенні ліміту — перехід у `FAILED`.

3. **`WAIT_REQUEST` (Почергова передача елементів місії):**
   - **Умова перебування:** Транзакція в процесі. Станція очікує від автопілота запиту на черговий елемент `seq`.
   - **Дії при отриманні `MISSION_REQUEST_INT(seq)`:**
     - Якщо `seq` збігається з очікуваним індексом або є повтором щойно відправленого (через втрату попереднього `ITEM`): надсилається структура `MISSION_ITEM_INT(seq)`, скидається лічильник спроб, оновлюється таймер.
     - Якщо передано передостанній елемент (`seq < N - 1`), автомат залишається у стані `WAIT_REQUEST`.
     - Якщо надіслано останній елемент (`seq == N - 1`), автомат переходить у стан `WAIT_ACK`.
     - Якщо `seq >= N` (некоректний індекс поза межами масиву): надсилається `MISSION_ACK` із кодом помилки `MAV_MISSION_INVALID_SEQUENCE`, транзакція скасовується, перехід у `FAILED`.

4. **`WAIT_ACK` (Очікування фінальної фіксації місії):**
   - **Умова перебування:** Усі елементи успішно відправлені. Автопілот перевіряє цілісність отриманого графа місії, валідує параметри кожної команди (наприклад, допустимість висот, наявність точок зльоту й посадки) та записує їх у постійну Flash-пам'ять.
   - **Очікувана подія:** Надходження фінального пакета `MISSION_ACK`.
   - **Дії при отриманні:**
     - Якщо код результату `result == MAV_MISSION_ACCEPTED`: транзакція успішна, перехід у `DONE`.
     - Якщо код результату містить помилку (`MAV_MISSION_ERROR`, `MAV_MISSION_DENIED`, `MAV_MISSION_INVALID_PARAM` тощо): фіксація збою, перехід у `FAILED`.

5. **`DONE` (Успішне завершення):**
   - **Умова перебування:** Термінальний стан успіху. Станція може повідомити користувача та перейти назад у `IDLE` для нових завдань.

6. **`FAILED` (Аварійне скасування):**
   - **Умова перебування:** Термінальний стан помилки (таймаут вичерпано, зв'язок втрачено, автопілот повернув NACK/Error).
   - **Дії при переході:** Надсилання пакета `MISSION_ACK` із результатом `MAV_MISSION_OPERATION_CANCELLED` для гарантованого звільнення транзакційного буфера автопілота.

## Структури даних протоколу

Опишемо структури даних для представлення елемента місії та стану автомата. Координати задаються цілими числами `int32_t` (градуси `× 10⁷`), висота — у метрах (`float`), система координат — `MAV_FRAME_GLOBAL_RELATIVE_ALT_INT` (висота відносно точки старту):

:::tabs
```cpp
#include <cstdint>
#include <vector>
#include <string>
#include <chrono>
#include <functional>

// Константи протоколу MAVLink
constexpr uint8_t MAV_MISSION_TYPE_MISSION = 0;
constexpr uint8_t MAV_FRAME_GLOBAL_RELATIVE_ALT_INT = 3;
constexpr uint16_t MAV_CMD_NAV_WAYPOINT = 16;
constexpr uint16_t MAV_CMD_NAV_TAKEOFF = 22;

// Коди результату транзакції MAV_MISSION_RESULT
enum class MissionResult : uint8_t {
    Accepted = 0,
    Error = 1,
    UnsupportedFrame = 2,
    Unsupported = 3,
    NoSpace = 4,
    Invalid = 5,
    InvalidParam1 = 6,
    InvalidParam2 = 7,
    InvalidParam3 = 8,
    InvalidParam4 = 9,
    InvalidParam5 = 10,
    InvalidParam6 = 11,
    InvalidParam7 = 12,
    InvalidSequence = 13,
    Denied = 14,
    OperationCancelled = 15
};

// Елемент місії з цілочисловими координатами
struct MissionItem {
    uint16_t seq{0};
    uint16_t command{MAV_CMD_NAV_WAYPOINT};
    uint8_t frame{MAV_FRAME_GLOBAL_RELATIVE_ALT_INT};
    float param1{0.0f}; // Час очікування / кут
    float param2{0.0f}; // Радіус прийняття точки (м)
    float param3{0.0f}; // Радіус прольоту траєкторії (м)
    float param4{0.0f}; // Азимут рискання (град)
    int32_t x{0};       // Широта (deg * 1e7)
    int32_t y{0};       // Довгота (deg * 1e7)
    float z{0.0f};      // Висота (м)
    uint8_t autocontinue{1};
};

// Стани FSM
enum class FsmState {
    Idle,
    SendCount,
    WaitRequest,
    WaitAck,
    Done,
    Failed
};
```
```c
#include <stdint.h>
#include <stdbool.h>

#define MAV_MISSION_TYPE_MISSION 0
#define MAV_FRAME_GLOBAL_RELATIVE_ALT_INT 3
#define MAV_CMD_NAV_WAYPOINT 16
#define MAV_CMD_NAV_TAKEOFF 22

typedef enum {
    MAV_MISSION_ACCEPTED = 0,
    MAV_MISSION_ERROR = 1,
    MAV_MISSION_UNSUPPORTED_FRAME = 2,
    MAV_MISSION_UNSUPPORTED = 3,
    MAV_MISSION_NO_SPACE = 4,
    MAV_MISSION_INVALID = 5,
    MAV_MISSION_INVALID_PARAM1 = 6,
    MAV_MISSION_INVALID_PARAM2 = 7,
    MAV_MISSION_INVALID_PARAM3 = 8,
    MAV_MISSION_INVALID_PARAM4 = 9,
    MAV_MISSION_INVALID_PARAM5 = 10,
    MAV_MISSION_INVALID_PARAM6 = 11,
    MAV_MISSION_INVALID_PARAM7 = 12,
    MAV_MISSION_INVALID_SEQUENCE = 13,
    MAV_MISSION_DENIED = 14,
    MAV_MISSION_OPERATION_CANCELLED = 15
} MAV_MISSION_RESULT;

typedef struct {
    uint16_t seq;
    uint16_t command;
    uint8_t frame;
    float param1;
    float param2;
    float param3;
    float param4;
    int32_t x;
    int32_t y;
    float z;
    uint8_t autocontinue;
} mission_item_t;

typedef enum {
    FSM_IDLE,
    FSM_SEND_COUNT,
    FSM_WAIT_REQUEST,
    FSM_WAIT_ACK,
    FSM_DONE,
    FSM_FAILED
} fsm_state_t;
```
```python
from enum import IntEnum
from dataclasses import dataclass
from typing import List, Optional, Callable
import time

class MissionResult(IntEnum):
    ACCEPTED = 0
    ERROR = 1
    UNSUPPORTED_FRAME = 2
    UNSUPPORTED = 3
    NO_SPACE = 4
    INVALID = 5
    INVALID_PARAM1 = 6
    INVALID_PARAM2 = 7
    INVALID_PARAM3 = 8
    INVALID_PARAM4 = 9
    INVALID_PARAM5 = 10
    INVALID_PARAM6 = 11
    INVALID_PARAM7 = 12
    INVALID_SEQUENCE = 13
    DENIED = 14
    OPERATION_CANCELLED = 15

class FsmState(IntEnum):
    IDLE = 0
    SEND_COUNT = 1
    WAIT_REQUEST = 2
    WAIT_ACK = 3
    DONE = 4
    FAILED = 5

@dataclass
class MissionItem:
    seq: int
    command: int = 16  # MAV_CMD_NAV_WAYPOINT
    frame: int = 3     # MAV_FRAME_GLOBAL_RELATIVE_ALT_INT
    param1: float = 0.0
    param2: float = 0.0
    param3: float = 0.0
    param4: float = 0.0
    x: int = 0         # Lat * 1e7
    y: int = 0         # Lon * 1e7
    z: float = 0.0     # Alt in meters
    autocontinue: int = 1
```
:::

## Повна реалізація завантажувача

Реалізуємо клас автомата з неблокуючою логікою, підтримкою повторів пакетів через таймаут (1000 мс) та лімітом спроб (до 5 повторів на кожен крок транзакції):

:::tabs
```cpp
class MissionUploader {
public:
    using SendCountFn  = std::function<void(uint16_t count, uint8_t mission_type)>;
    using SendItemFn   = std::function<void(const MissionItem& item, uint8_t mission_type)>;
    using SendCancelFn = std::function<void(uint8_t mission_type)>;

    MissionUploader(SendCountFn send_cnt, SendItemFn send_itm, SendCancelFn send_cnl)
        : send_count_(std::move(send_cnt)),
          send_item_(std::move(send_itm)),
          send_cancel_(std::move(send_cnl)) {}

    bool start(std::vector<MissionItem> items, uint32_t now_ms) {
        if (state_ != FsmState::Idle && state_ != FsmState::Done && state_ != FsmState::Failed) {
            return false; // Транзакція вже триває
        }
        if (items.empty()) return false;

        items_ = std::move(items);
        for (size_t i = 0; i < items_.size(); ++i) {
            items_[i].seq = static_cast<uint16_t>(i);
        }

        expected_seq_ = 0;
        retry_count_ = 0;
        last_action_ms_ = now_ms;
        state_ = FsmState::SendCount;

        send_count_(static_cast<uint16_t>(items_.size()), MAV_MISSION_TYPE_MISSION);
        return true;
    }

    void handle_mission_request(uint16_t seq, uint8_t mission_type, uint32_t now_ms) {
        if (mission_type != MAV_MISSION_TYPE_MISSION) return;
        if (state_ != FsmState::SendCount && state_ != FsmState::WaitRequest) return;

        if (seq >= items_.size()) {
            // Запит номера за межами списку: аварійне скасування
            fail_transaction(MissionResult::InvalidSequence);
            return;
        }

        // Надсилаємо запитаний елемент місії
        expected_seq_ = seq;
        send_item_(items_[seq], MAV_MISSION_TYPE_MISSION);
        last_action_ms_ = now_ms;
        retry_count_ = 0;

        if (seq == items_.size() - 1) {
            // Передано останній пункт, очікуємо фінальний ACK
            state_ = FsmState::WaitAck;
        } else {
            state_ = FsmState::WaitRequest;
        }
    }

    void handle_mission_ack(MissionResult result) {
        if (state_ != FsmState::WaitAck && state_ != FsmState::WaitRequest && state_ != FsmState::SendCount) {
            return;
        }

        if (result == MissionResult::Accepted) {
            state_ = FsmState::Done;
        } else {
            state_ = FsmState::Failed;
        }
    }

    void tick(uint32_t now_ms) {
        if (state_ == FsmState::Idle || state_ == FsmState::Done || state_ == FsmState::Failed) {
            return;
        }

        if (now_ms - last_action_ms_ >= TIMEOUT_MS) {
            if (retry_count_ >= MAX_RETRIES) {
                fail_transaction(MissionResult::OperationCancelled);
                return;
            }

            retry_count_++;
            last_action_ms_ = now_ms;

            if (state_ == FsmState::SendCount) {
                send_count_(static_cast<uint16_t>(items_.size()), MAV_MISSION_TYPE_MISSION);
            } else if (state_ == FsmState::WaitRequest || state_ == FsmState::WaitAck) {
                // Повторюємо передачу останнього запитаного пункту
                if (expected_seq_ < items_.size()) {
                    send_item_(items_[expected_seq_], MAV_MISSION_TYPE_MISSION);
                }
            }
        }
    }

    FsmState state() const { return state_; }

private:
    void fail_transaction(MissionResult reason) {
        state_ = FsmState::Failed;
        send_cancel_(MAV_MISSION_TYPE_MISSION);
    }

    static constexpr uint32_t TIMEOUT_MS = 1000;
    static constexpr uint8_t MAX_RETRIES = 5;

    SendCountFn send_count_;
    SendItemFn send_item_;
    SendCancelFn send_cancel_;

    std::vector<MissionItem> items_;
    FsmState state_{FsmState::Idle};
    uint16_t expected_seq_{0};
    uint8_t retry_count_{0};
    uint32_t last_action_ms_{0};
};
```
```c
#include <string.h>

#define TIMEOUT_MS 1000
#define MAX_RETRIES 5
#define MAX_ITEMS 64

typedef void (*send_count_fn)(uint16_t count, uint8_t mission_type);
typedef void (*send_item_fn)(const mission_item_t* item, uint8_t mission_type);
typedef void (*send_cancel_fn)(uint8_t mission_type);

typedef struct {
    fsm_state_t state;
    mission_item_t items[MAX_ITEMS];
    uint16_t item_count;
    uint16_t expected_seq;
    uint8_t retry_count;
    uint32_t last_action_ms;

    send_count_fn send_count;
    send_item_fn send_item;
    send_cancel_fn send_cancel;
} mission_uploader_t;

void mission_uploader_init(mission_uploader_t* uploader,
                           send_count_fn s_cnt,
                           send_item_fn s_itm,
                           send_cancel_fn s_cnl) {
    uploader->state = FSM_IDLE;
    uploader->item_count = 0;
    uploader->expected_seq = 0;
    uploader->retry_count = 0;
    uploader->last_action_ms = 0;
    uploader->send_count = s_cnt;
    uploader->send_item = s_itm;
    uploader->send_cancel = s_cnl;
}

bool mission_uploader_start(mission_uploader_t* uploader,
                            const mission_item_t* items,
                            uint16_t count,
                            uint32_t now_ms) {
    if (uploader->state != FSM_IDLE &&
        uploader->state != FSM_DONE &&
        uploader->state != FSM_FAILED) {
        return false;
    }
    if (count == 0 || count > MAX_ITEMS) return false;

    memcpy(uploader->items, items, sizeof(mission_item_t) * count);
    uploader->item_count = count;
    for (uint16_t i = 0; i < count; i++) {
        uploader->items[i].seq = i;
    }

    uploader->expected_seq = 0;
    uploader->retry_count = 0;
    uploader->last_action_ms = now_ms;
    uploader->state = FSM_SEND_COUNT;

    uploader->send_count(count, MAV_MISSION_TYPE_MISSION);
    return true;
}

void mission_uploader_handle_request(mission_uploader_t* uploader,
                                     uint16_t seq,
                                     uint8_t mission_type,
                                     uint32_t now_ms) {
    if (mission_type != MAV_MISSION_TYPE_MISSION) return;
    if (uploader->state != FSM_SEND_COUNT && uploader->state != FSM_WAIT_REQUEST) return;

    if (seq >= uploader->item_count) {
        uploader->state = FSM_FAILED;
        uploader->send_cancel(MAV_MISSION_TYPE_MISSION);
        return;
    }

    uploader->expected_seq = seq;
    uploader->send_item(&uploader->items[seq], MAV_MISSION_TYPE_MISSION);
    uploader->last_action_ms = now_ms;
    uploader->retry_count = 0;

    if (seq == uploader->item_count - 1) {
        uploader->state = FSM_WAIT_ACK;
    } else {
        uploader->state = FSM_WAIT_REQUEST;
    }
}

void mission_uploader_handle_ack(mission_uploader_t* uploader, MAV_MISSION_RESULT result) {
    if (uploader->state != FSM_WAIT_ACK &&
        uploader->state != FSM_WAIT_REQUEST &&
        uploader->state != FSM_SEND_COUNT) {
        return;
    }

    if (result == MAV_MISSION_ACCEPTED) {
        uploader->state = FSM_DONE;
    } else {
        uploader->state = FSM_FAILED;
    }
}

void mission_uploader_tick(mission_uploader_t* uploader, uint32_t now_ms) {
    if (uploader->state == FSM_IDLE ||
        uploader->state == FSM_DONE ||
        uploader->state == FSM_FAILED) {
        return;
    }

    if (now_ms - uploader->last_action_ms >= TIMEOUT_MS) {
        if (uploader->retry_count >= MAX_RETRIES) {
            uploader->state = FSM_FAILED;
            uploader->send_cancel(MAV_MISSION_TYPE_MISSION);
            return;
        }

        uploader->retry_count++;
        uploader->last_action_ms = now_ms;

        if (uploader->state == FSM_SEND_COUNT) {
            uploader->send_count(uploader->item_count, MAV_MISSION_TYPE_MISSION);
        } else if (uploader->state == FSM_WAIT_REQUEST || uploader->state == FSM_WAIT_ACK) {
            if (uploader->expected_seq < uploader->item_count) {
                uploader->send_item(&uploader->items[uploader->expected_seq], MAV_MISSION_TYPE_MISSION);
            }
        }
    }
}
```
```python
class MissionUploader:
    TIMEOUT_SEC = 1.0
    MAX_RETRIES = 5

    def __init__(self,
                 send_count_fn: Callable[[int, int], None],
                 send_item_fn: Callable[[MissionItem, int], None],
                 send_cancel_fn: Callable[[int], None]):
        self.send_count = send_count_fn
        self.send_item = send_item_fn
        self.send_cancel = send_cancel_fn

        self.state = FsmState.IDLE
        self.items: List[MissionItem] = []
        self.expected_seq = 0
        self.retry_count = 0
        self.last_action_time = 0.0

    def start(self, items: List[MissionItem], now: float) -> bool:
        if self.state not in (FsmState.IDLE, FsmState.DONE, FsmState.FAILED):
            return False
        if not items:
            return False

        self.items = list(items)
        for idx, item in enumerate(self.items):
            item.seq = idx

        self.expected_seq = 0
        self.retry_count = 0
        self.last_action_time = now
        self.state = FsmState.SEND_COUNT

        self.send_count(len(self.items), int(MissionResult.ACCEPTED))
        return True

    def handle_mission_request(self, seq: int, mission_type: int, now: float):
        if mission_type != 0:  # MAV_MISSION_TYPE_MISSION
            return
        if self.state not in (FsmState.SEND_COUNT, FsmState.WAIT_REQUEST):
            return

        if seq >= len(self.items):
            self.state = FsmState.FAILED
            self.send_cancel(0)
            return

        self.expected_seq = seq
        self.send_item(self.items[seq], 0)
        self.last_action_time = now
        self.retry_count = 0

        if seq == len(self.items) - 1:
            self.state = FsmState.WAIT_ACK
        else:
            self.state = FsmState.WAIT_REQUEST

    def handle_mission_ack(self, result: MissionResult):
        if self.state not in (FsmState.WAIT_ACK, FsmState.WAIT_REQUEST, FsmState.SEND_COUNT):
            return

        if result == MissionResult.ACCEPTED:
            self.state = FsmState.DONE
        else:
            self.state = FsmState.FAILED

    def tick(self, now: float):
        if self.state in (FsmState.IDLE, FsmState.DONE, FsmState.FAILED):
            return

        if now - self.last_action_time >= self.TIMEOUT_SEC:
            if self.retry_count >= self.MAX_RETRIES:
                self.state = FsmState.FAILED
                self.send_cancel(0)
                return

            self.retry_count += 1
            self.last_action_time = now

            if self.state == FsmState.SEND_COUNT:
                self.send_count(len(self.items), 0)
            elif self.state in (FsmState.WAIT_REQUEST, FsmState.WAIT_ACK):
                if self.expected_seq < len(self.items):
                    self.send_item(self.items[self.expected_seq], 0)
```
:::

## Інтеграція з транспортним рівнем MAVLink

Для перетворення абстрактних викликів `send_count` та `send_item` у двійкові байти каналу зв'язку використовується офіційна C-бібліотека кодогенерації MAVLink (`mavlink_helpers.h`).

Розгляньмо, як формуються реальні кадри MAVLink v2 для відправлення на UART/UDP сокет:

:::tabs
```cpp
#include <mavlink.h>
#include <vector>
#include <iostream>

// Приклад відправки MISSION_COUNT через C-бібліотеку MAVLink
void send_mavlink_mission_count(int uart_fd, uint8_t system_id, uint8_t component_id,
                                uint8_t target_sys, uint8_t target_comp,
                                uint16_t count, uint8_t mission_type) {
    mavlink_message_t msg;
    mavlink_mission_count_t payload{};
    payload.count = count;
    payload.target_system = target_sys;
    payload.target_component = target_comp;
    payload.mission_type = mission_type;

    mavlink_msg_mission_count_encode(system_id, component_id, &msg, &payload);

    uint8_t buffer[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buffer, &msg);
    // write(uart_fd, buffer, len);
}

// Приклад відправки MISSION_ITEM_INT
void send_mavlink_mission_item_int(int uart_fd, uint8_t system_id, uint8_t component_id,
                                   uint8_t target_sys, uint8_t target_comp,
                                   const MissionItem& item, uint8_t mission_type) {
    mavlink_message_t msg;
    mavlink_mission_item_int_t payload{};
    payload.param1 = item.param1;
    payload.param2 = item.param2;
    payload.param3 = item.param3;
    payload.param4 = item.param4;
    payload.x = item.x;
    payload.y = item.y;
    payload.z = item.z;
    payload.seq = item.seq;
    payload.command = item.command;
    payload.target_system = target_sys;
    payload.target_component = target_comp;
    payload.frame = item.frame;
    payload.current = (item.seq == 0) ? 1 : 0;
    payload.autocontinue = item.autocontinue;
    payload.mission_type = mission_type;

    mavlink_msg_mission_item_int_encode(system_id, component_id, &msg, &payload);

    uint8_t buffer[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buffer, &msg);
    // write(uart_fd, buffer, len);
}
```
```c
#include <mavlink.h>

void send_mavlink_mission_count_c(int uart_fd, uint8_t system_id, uint8_t component_id,
                                  uint8_t target_sys, uint8_t target_comp,
                                  uint16_t count, uint8_t mission_type) {
    mavlink_message_t msg;
    mavlink_mission_count_t payload;
    payload.count = count;
    payload.target_system = target_sys;
    payload.target_component = target_comp;
    payload.mission_type = mission_type;

    mavlink_msg_mission_count_encode(system_id, component_id, &msg, &payload);

    uint8_t buffer[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buffer, &msg);
    // write(uart_fd, buffer, len);
}

void send_mavlink_mission_item_int_c(int uart_fd, uint8_t system_id, uint8_t component_id,
                                     uint8_t target_sys, uint8_t target_comp,
                                     const mission_item_t* item, uint8_t mission_type) {
    mavlink_message_t msg;
    mavlink_mission_item_int_t payload;
    payload.param1 = item->param1;
    payload.param2 = item->param2;
    payload.param3 = item->param3;
    payload.param4 = item->param4;
    payload.x = item->x;
    payload.y = item->y;
    payload.z = item->z;
    payload.seq = item->seq;
    payload.command = item->command;
    payload.target_system = target_sys;
    payload.target_component = target_comp;
    payload.frame = item->frame;
    payload.current = (item->seq == 0) ? 1 : 0;
    payload.autocontinue = item->autocontinue;
    payload.mission_type = mission_type;

    mavlink_msg_mission_item_int_encode(system_id, component_id, &msg, &payload);

    uint8_t buffer[MAVLINK_MAX_PACKET_LEN];
    uint16_t len = mavlink_msg_to_send_buffer(buffer, &msg);
    // write(uart_fd, buffer, len);
}
```
:::

## Симетричний автомат вивантаження місії (Downloader FSM)

Протокол місій розроблений симетричним: процедура зчитування польотного завдання з автопілота на наземну станцію (вивантаження, англ. *mission download*) використовує той самий набір повідомлень, але ініціатором запиту виступає станція, а відправником елементів — автопілот.

Граф станів автомата зчитування містить такі кроки:

```
[IDLE]
  │
  │ start_download() → надсилаємо MISSION_REQUEST_LIST
  ▼
[WAIT_COUNT] ──(отримано MISSION_COUNT = N)──► [REQUEST_ITEMS]
                                                    │ ▲
                   надсилаємо REQUEST_INT(seq)      │ │
                   отримано ITEM_INT(seq)           │ │
                   зберігаємо точку seq             │ │
                   ─────────────────────────────────┘ │
                                                      │
                   отримано останній ITEM(N-1)        │
                   надсилаємо MISSION_ACK(ACCEPTED)   │
                   ───────────────────────────────────┼──────────┐
                                                      │          │
                                                      ▼          ▼
                                                   [DONE]     [FAILED]
```

Розгляньмо роботу автомата зчитування:
1. **Ініціалізація (`WAIT_COUNT`):** Станція надсилає повідомлення `MISSION_REQUEST_LIST` автопілоту й запускає таймер очікування.
2. **Отримання кількості пунктів:** Автопілот відповідає повідомленням `MISSION_COUNT` із загальною кількістю точок `N`. Якщо `N == 0` (місія порожня), станція негайно надсилає `MISSION_ACK(ACCEPTED)` і переходить у стан `DONE`.
3. **Послідовне опитування (`REQUEST_ITEMS`):** Станція відправляє `MISSION_REQUEST_INT(seq = 0)` і чекає на `MISSION_ITEM_INT(0)`. Отримавши елемент, станція зберігає його в локальний масив і запитує наступний індекс `seq = 1`.
4. **Фіксація транзакції:** Після успішного отримання останньої точки `seq = N - 1` станція перевіряє цілісність отриманого списку (відсутність пропущених номерів) і надсилає автопілоту повідомлення `MISSION_ACK(MAV_MISSION_ACCEPTED)`. Лише після отримання цього ACK автопілот вважає сеанс читання завершеним і звільняє пам'ять.

:::tabs
```cpp
class MissionDownloader {
public:
    using SendReqListFn = std::function<void(uint8_t mission_type)>;
    using SendReqItemFn = std::function<void(uint16_t seq, uint8_t mission_type)>;
    using SendAckFn     = std::function<void(MissionResult result, uint8_t mission_type)>;

    MissionDownloader(SendReqListFn s_list, SendReqItemFn s_item, SendAckFn s_ack)
        : send_req_list_(std::move(s_list)),
          send_req_item_(std::move(s_item)),
          send_ack_(std::move(s_ack)) {}

    bool start(uint32_t now_ms) {
        if (state_ != FsmState::Idle && state_ != FsmState::Done && state_ != FsmState::Failed) {
            return false;
        }

        items_.clear();
        expected_count_ = 0;
        current_seq_ = 0;
        retry_count_ = 0;
        last_action_ms_ = now_ms;
        state_ = FsmState::SendCount; // Стан очікування MISSION_COUNT

        send_req_list_(MAV_MISSION_TYPE_MISSION);
        return true;
    }

    void handle_mission_count(uint16_t count, uint8_t mission_type, uint32_t now_ms) {
        if (mission_type != MAV_MISSION_TYPE_MISSION) return;
        if (state_ != FsmState::SendCount) return;

        expected_count_ = count;
        items_.clear();
        last_action_ms_ = now_ms;
        retry_count_ = 0;

        if (count == 0) {
            send_ack_(MissionResult::Accepted, MAV_MISSION_TYPE_MISSION);
            state_ = FsmState::Done;
            return;
        }

        items_.reserve(count);
        current_seq_ = 0;
        state_ = FsmState::WaitRequest; // Стан послідовного опитування
        send_req_item_(current_seq_, MAV_MISSION_TYPE_MISSION);
    }

    void handle_mission_item(const MissionItem& item, uint8_t mission_type, uint32_t now_ms) {
        if (mission_type != MAV_MISSION_TYPE_MISSION) return;
        if (state_ != FsmState::WaitRequest) return;

        if (item.seq != current_seq_) {
            if (item.seq < current_seq_) {
                send_req_item_(current_seq_, MAV_MISSION_TYPE_MISSION);
            } else {
                fail_transaction(MissionResult::InvalidSequence);
            }
            return;
        }

        items_.push_back(item);
        last_action_ms_ = now_ms;
        retry_count_ = 0;
        current_seq_++;

        if (current_seq_ == expected_count_) {
            send_ack_(MissionResult::Accepted, MAV_MISSION_TYPE_MISSION);
            state_ = FsmState::Done;
        } else {
            send_req_item_(current_seq_, MAV_MISSION_TYPE_MISSION);
        }
    }

    void tick(uint32_t now_ms) {
        if (state_ == FsmState::Idle || state_ == FsmState::Done || state_ == FsmState::Failed) {
            return;
        }

        if (now_ms - last_action_ms_ >= TIMEOUT_MS) {
            if (retry_count_ >= MAX_RETRIES) {
                fail_transaction(MissionResult::OperationCancelled);
                return;
            }

            retry_count_++;
            last_action_ms_ = now_ms;

            if (state_ == FsmState::SendCount) {
                send_req_list_(MAV_MISSION_TYPE_MISSION);
            } else if (state_ == FsmState::WaitRequest) {
                send_req_item_(current_seq_, MAV_MISSION_TYPE_MISSION);
            }
        }
    }

    const std::vector<MissionItem>& items() const { return items_; }
    FsmState state() const { return state_; }

private:
    void fail_transaction(MissionResult reason) {
        state_ = FsmState::Failed;
        send_ack_(reason, MAV_MISSION_TYPE_MISSION);
    }

    static constexpr uint32_t TIMEOUT_MS = 1000;
    static constexpr uint8_t MAX_RETRIES = 5;

    SendReqListFn send_req_list_;
    SendReqItemFn send_req_item_;
    SendAckFn     send_ack_;

    std::vector<MissionItem> items_;
    FsmState state_{FsmState::Idle};
    uint16_t expected_count_{0};
    uint16_t current_seq_{0};
    uint8_t retry_count_{0};
    uint32_t last_action_ms_{0};
};
```
```c
typedef struct {
    fsm_state_t state;
    mission_item_t items[MAX_ITEMS];
    uint16_t expected_count;
    uint16_t current_seq;
    uint8_t retry_count;
    uint32_t last_action_ms;

    send_cancel_fn send_req_list;
    send_count_fn send_req_item;
    send_cancel_fn send_ack;
} mission_downloader_t;

void mission_downloader_init(mission_downloader_t* dnl,
                             send_cancel_fn s_list,
                             send_count_fn s_item,
                             send_cancel_fn s_ack) {
    dnl->state = FSM_IDLE;
    dnl->expected_count = 0;
    dnl->current_seq = 0;
    dnl->retry_count = 0;
    dnl->last_action_ms = 0;
    dnl->send_req_list = s_list;
    dnl->send_req_item = s_item;
    dnl->send_ack = s_ack;
}

bool mission_downloader_start(mission_downloader_t* dnl, uint32_t now_ms) {
    if (dnl->state != FSM_IDLE && dnl->state != FSM_DONE && dnl->state != FSM_FAILED) {
        return false;
    }

    dnl->expected_count = 0;
    dnl->current_seq = 0;
    dnl->retry_count = 0;
    dnl->last_action_ms = now_ms;
    dnl->state = FSM_SEND_COUNT;

    dnl->send_req_list(MAV_MISSION_TYPE_MISSION);
    return true;
}

void mission_downloader_handle_count(mission_downloader_t* dnl,
                                     uint16_t count,
                                     uint8_t mission_type,
                                     uint32_t now_ms) {
    if (mission_type != MAV_MISSION_TYPE_MISSION) return;
    if (dnl->state != FSM_SEND_COUNT) return;

    dnl->expected_count = count;
    dnl->last_action_ms = now_ms;
    dnl->retry_count = 0;

    if (count == 0 || count > MAX_ITEMS) {
        dnl->state = (count == 0) ? FSM_DONE : FSM_FAILED;
        dnl->send_ack(MAV_MISSION_TYPE_MISSION);
        return;
    }

    dnl->current_seq = 0;
    dnl->state = FSM_WAIT_REQUEST;
    dnl->send_req_item(0, MAV_MISSION_TYPE_MISSION);
}

void mission_downloader_handle_item(mission_downloader_t* dnl,
                                    const mission_item_t* item,
                                    uint8_t mission_type,
                                    uint32_t now_ms) {
    if (mission_type != MAV_MISSION_TYPE_MISSION) return;
    if (dnl->state != FSM_WAIT_REQUEST) return;

    if (item->seq != dnl->current_seq) {
        dnl->send_req_item(dnl->current_seq, MAV_MISSION_TYPE_MISSION);
        return;
    }

    memcpy(&dnl->items[dnl->current_seq], item, sizeof(mission_item_t));
    dnl->last_action_ms = now_ms;
    dnl->retry_count = 0;
    dnl->current_seq++;

    if (dnl->current_seq == dnl->expected_count) {
        dnl->state = FSM_DONE;
        dnl->send_ack(MAV_MISSION_TYPE_MISSION);
    } else {
        dnl->send_req_item(dnl->current_seq, MAV_MISSION_TYPE_MISSION);
    }
}

void mission_downloader_tick(mission_downloader_t* dnl, uint32_t now_ms) {
    if (dnl->state == FSM_IDLE || dnl->state == FSM_DONE || dnl->state == FSM_FAILED) {
        return;
    }

    if (now_ms - dnl->last_action_ms >= TIMEOUT_MS) {
        if (dnl->retry_count >= MAX_RETRIES) {
            dnl->state = FSM_FAILED;
            dnl->send_ack(MAV_MISSION_TYPE_MISSION);
            return;
        }

        dnl->retry_count++;
        dnl->last_action_ms = now_ms;

        if (dnl->state == FSM_SEND_COUNT) {
            dnl->send_req_list(MAV_MISSION_TYPE_MISSION);
        } else if (dnl->state == FSM_WAIT_REQUEST) {
            dnl->send_req_item(dnl->current_seq, MAV_MISSION_TYPE_MISSION);
        }
    }
}
```
```python
class MissionDownloader:
    TIMEOUT_SEC = 1.0
    MAX_RETRIES = 5

    def __init__(self,
                 send_req_list_fn: Callable[[int], None],
                 send_req_item_fn: Callable[[int, int], None],
                 send_ack_fn: Callable[[MissionResult, int], None]):
        self.send_req_list = send_req_list_fn
        self.send_req_item = send_req_item_fn
        self.send_ack = send_ack_fn

        self.state = FsmState.IDLE
        self.items: List[MissionItem] = []
        self.expected_count = 0
        self.current_seq = 0
        self.retry_count = 0
        self.last_action_time = 0.0

    def start(self, now: float) -> bool:
        if self.state not in (FsmState.IDLE, FsmState.DONE, FsmState.FAILED):
            return False

        self.items.clear()
        self.expected_count = 0
        self.current_seq = 0
        self.retry_count = 0
        self.last_action_time = now
        self.state = FsmState.SEND_COUNT

        self.send_req_list(0)
        return True

    def handle_mission_count(self, count: int, mission_type: int, now: float):
        if mission_type != 0:
            return
        if self.state != FsmState.SEND_COUNT:
            return

        self.expected_count = count
        self.items.clear()
        self.last_action_time = now
        self.retry_count = 0

        if count == 0:
            self.send_ack(MissionResult.ACCEPTED, 0)
            self.state = FsmState.DONE
            return

        self.current_seq = 0
        self.state = FsmState.WAIT_REQUEST
        self.send_req_item(0, 0)

    def handle_mission_item(self, item: MissionItem, mission_type: int, now: float):
        if mission_type != 0:
            return
        if self.state != FsmState.WAIT_REQUEST:
            return

        if item.seq != self.current_seq:
            if item.seq < self.current_seq:
                self.send_req_item(self.current_seq, 0)
            else:
                self.state = FsmState.FAILED
                self.send_ack(MissionResult.INVALID_SEQUENCE, 0)
            return

        self.items.append(item)
        self.last_action_time = now
        self.retry_count = 0
        self.current_seq += 1

        if self.current_seq == self.expected_count:
            self.send_ack(MissionResult.ACCEPTED, 0)
            self.state = FsmState.DONE
        else:
            self.send_req_item(self.current_seq, 0)

    def tick(self, now: float):
        if self.state in (FsmState.IDLE, FsmState.DONE, FsmState.FAILED):
            return

        if now - self.last_action_time >= self.TIMEOUT_SEC:
            if self.retry_count >= self.MAX_RETRIES:
                self.state = FsmState.FAILED
                self.send_ack(MissionResult.OPERATION_CANCELLED, 0)
                return

            self.retry_count += 1
            self.last_action_time = now

            if self.state == FsmState.SEND_COUNT:
                self.send_req_list(0)
            elif self.state == FsmState.WAIT_REQUEST:
                self.send_req_item(self.current_seq, 0)
```
:::

## Фізичні обмеження каналу, MTU та оптимізація буферизації

Для ефективної роботи завантажувача місій у реальних польотних умовах необхідно враховувати фізичні параметри радіоканалу:

1. **Розмір корисного навантаження кадру (MTU):**
   Повідомлення `MISSION_ITEM_INT` має довжину корисного навантаження 38 байтів. Разом із заголовком MAVLink v2 (10 байтів), початковим маркером `0xFD`, адресацією та 2-байтовою контрольною сумою CRC-16 сумарний розмір кадру на дроті становить рівно `50 байтів` (або `63 байти` у разі використання криптографічного підпису MAVLink v2 Signature). Більшість апаратних радіомодемів (SiK Telemetry на чіпах Si1000/HM-TRP) мають внутрішній розмір пакета бездротового рівня (англ. *over-the-air packet*) від 64 до 128 байтів. Це означає, що кадр `MISSION_ITEM_INT` гарантовано вміщується в один радіопакет без внутрішньої апаратної фрагментації, що мінімізує ймовірність часткової втрати байтів.

2. **Розрахунок пропускної здатності та таймаутів:**
   Типова швидкість послідовного порту телеметрії становить `57 600 біт/с` (близько `5.76 КБ/с`). Передача одного кадру `MISSION_ITEM_INT` (50 байтів) займає всього:

   ```
   T_tx = 50 байтів · 10 біт / 57 600 біт/с ≈ 8.68 мс
   ```

   Проте час обробки на мікроконтролері складається не лише з передачі байтів через UART. Автопілот повинен:
   - Прийняти та перевірити CRC кадру в RTOS-потоці MAVLink.
   - Перевірити доступність вільного сектора у внутрішній Flash-пам'яті STM32 (або зовнішній SPI NOR Flash типу W25Q128).
   - Виконати запис 38-байтової структури у Flash (запис сторінки SPI Flash триває від 0.5 до 3 мс, а операція стирання сектора 4 КБ перед записом може блокувати SPI шину на 20–50 мс).
   - Сформувати наступний пакет `MISSION_REQUEST_INT` і поставити його у вихідну чергу DMA UART.

   Сумарний час відгуку автопілота на запит становить від `40 до 150 мс` за умов стабільного зв'язку. Тому вибір таймауту очікування `TIMEOUT_MS = 1000 мс` забезпечує 6-кратний запас надійності для компенсації затримок запису Flash та джиттеру радіолінії.

3. **Скидання сесії при зміні режиму польоту:**
   Якщо під час завантаження місії оператор перемикає дрон у режим ручного керування (Manual) або активує аварійний режим RTL, автопілот PX4/ArduPilot може тимчасово заблокувати запис Flash. У такому разі FSM отримає `MAV_MISSION_DENIED` і зобов'язаний коректно завершити транзакцію, перейшовши у стан `FAILED` без зависання вихідних черг повідомлень.

## Повний розбір кодів помилок MAV_MISSION_RESULT

Коли автопілот або станція перериває транзакцію, повідомлення `MISSION_ACK` містить один із кодів переліку `MAV_MISSION_RESULT`. Правильна реакція клієнтської програми на кожен із цих кодів є критичною для запобігання втраті зв'язку:

| Код результату | Число | Причина виникнення | Необхідна дія клієнта |
| :--- | :--- | :--- | :--- |
| `MAV_MISSION_ACCEPTED` | 0 | Усі пункти прийняті, валідовані та збережені у Flash. | Завершити транзакцію успіхом, активувати інтерфейс. |
| `MAV_MISSION_ERROR` | 1 | Загальний внутрішній збій автопілота (помилка ОС, тайм-аут Flash). | Повідомити оператора, повторити завантаження з нуля. |
| `MAV_MISSION_UNSUPPORTED_FRAME` | 2 | Задана система координат `frame` не підтримується прошивкою. | Перевірити налаштування `frame` (наприклад, замінити локальний фрейм на глобальний `GLOBAL_RELATIVE_ALT_INT`). |
| `MAV_MISSION_UNSUPPORTED` | 3 | Команда `command` (наприклад, специфічна дія `MAV_CMD`) не реалізована в автопілоті. | Вилучити непідтримувану команду з маршруту або оновити прошивку. |
| `MAV_MISSION_NO_SPACE` | 4 | Переповнено енергонезалежну пам'ять EEPROM/Flash польотного контролера. | Зменшити кількість точок місії (розбити складний маршрут на кілька частин). |
| `MAV_MISSION_INVALID` | 5 | Загальна невалідність структури елемента. | Перевірити діапазони всіх параметрів. |
| `MAV_MISSION_INVALID_PARAM1..7` | 6..12 | Конкретний числовий параметр (`param1`…`param7`) виходить за межі фізично допустимих значень (наприклад, від'ємний радіус повороту чи нульова швидкість). | Підсвітити оператору некоректний пункт і конкретне поле для виправлення. |
| `MAV_MISSION_INVALID_SEQUENCE` | 13 | Отримано повідомлення з неочікуваним індексом `seq` (порушено послідовність). | Скинути сесію та перезапустити завантаження з `seq = 0`. |
| `MAV_MISSION_DENIED` | 14 | Автопілот забороняє зміну місії в поточному режимі (наприклад, апарат у польоті в режимі AUTO без дозволу на динамічне редагування). | Переключити режим польоту або зачекати посадки. |
| `MAV_MISSION_OPERATION_CANCELLED` | 15 | Транзакцію скасовано через таймаут зв'язку або дію користувача. | Очистити тимчасові буфери, перейти в `IDLE`. |

## Трасування транзакції завантаження в реальному часі

Розгляньмо типовий життєвий цикл передачі місії з 3 точок (зліт, проліт вейпоінта, посадка) із симуляцією втрати пакета на кроці 1:

```
[0.000 с] GCS -> AP:  MISSION_COUNT (count=3, type=0)
                      GCS переходить у SEND_COUNT, запускає таймер 1000 мс.

[0.045 с] AP -> GCS:  MISSION_REQUEST_INT (seq=0, type=0)
                      GCS скидає таймер, переходить у WAIT_REQUEST.

[0.050 с] GCS -> AP:  MISSION_ITEM_INT (seq=0, cmd=NAV_TAKEOFF, alt=30m)
                      GCS запускає таймер 1000 мс.

[0.095 с] AP -> GCS:  MISSION_REQUEST_INT (seq=1, type=0)
                      [Неявний ACK для seq=0 + запит seq=1]
                      GCS скидає таймер.

[0.100 с] GCS -> AP:  MISSION_ITEM_INT (seq=1, cmd=NAV_WAYPOINT, lat=..., lon=...)
                      *** ПАКЕТ ВТРАЧЕНО В ЕФІРІ ЧЕРЕЗ ЗАВАДУ ***

[1.100 с] GCS:        ТАЙМАУТ очікування (1000 мс вичерпано).
                      retry_count збільшується до 1.
                      GCS повторно надсилає MISSION_ITEM_INT (seq=1).

[1.145 с] AP -> GCS:  MISSION_REQUEST_INT (seq=2, type=0)
                      [Автопілот отримав повтор seq=1 і тепер запитує seq=2]
                      GCS скидає retry_count до 0, переходить у WAIT_ACK (оскільки seq=2 — останній).

[1.150 с] GCS -> AP:  MISSION_ITEM_INT (seq=2, cmd=NAV_LAND)

[1.210 с] AP -> GCS:  MISSION_ACK (type=0, result=MAV_MISSION_ACCEPTED)
                      Автопілот записав 3 точки у Flash.
                      GCS переходить у стан DONE. Транзакція успішно завершена!
```

Завдяки моделі Stop-and-Wait втрата окремого пакета даних на позначці 0.100 с не призвела до розриву сесії чи порушення структури даних: протокол автоматично відновив передачу після спливання таймауту.

## Атомарне очищення проти застарілого часткового редагування

У ранніх версіях протоколу місій MAVLink існувало повідомлення `MISSION_WRITE_PARTIAL_LIST` (#38), яке дозволяло перезаписати діапазон точок `[start_index … end_index]` посеред уже завантаженого маршруту без передачі всього списку. Проте інженерна практика експлуатації автономних дронів виявила критичні вразливості такого підходу:

1. **Неузгодженість навігаційного графа (Split Graph):** Якщо оператор замінював відрізок маршруту під час польоту в режимі AUTO, а один із пакетів оновлення втрачався, дрон отримував розірваний маршрут, де новий поворотний пункт міг посилатися на несумісну висоту чи радіус розвороту попереднього сегмента.
2. **Порушення інваріантів послідовності:** Номери кроків `seq` у складних польотних завданнях із циклами (`MAV_CMD_DO_JUMP`) жорстко прив'язані до абсолютних індексів. Часткова заміна призводила до того, що команда переходу `DO_JUMP` починала вказувати на іншу навігаційну команду або виходити за межі масиву.

Через це сучасний канон протоколу місій вимагає **виключно повної атомарної заміни**:
- Якщо потрібно очистити всі завдання певного типу, станція надсилає повідомлення `MISSION_CLEAR_ALL` (#45), вказуючи тип місії `mission_type` (0 — місія, 1 — геозона, 2 — точки збору). Автопілот очищає відповідний сектор Flash і повертає `MISSION_ACK(ACCEPTED)`.
- Якщо потрібно змінити хоча б одну точку, станція формує новий повний масив точок і завантажує його через стандартну транзакцію `MISSION_COUNT` → `MISSION_REQUEST_INT` → `MISSION_ACK`. Автопілот тримає діючу місію активною доти, доки не отримає фінальний елемент нової транзакції, після чого атомарно підміняє вказівник на новий список.

## Передпольотна валідація місії клієнтом

Перед тим як викликати функцію `start()` завантажувача, клієнтський додаток (GCS або бортовий планувальник) зобов'язаний виконати комплекс статичних перевірок сформованого списку `MissionItem`:

1. **Наявність точки старту та зльоту:** Першим навігаційним пунктом для літака або коптера має бути команда `MAV_CMD_NAV_TAKEOFF` із позитивною висотою або відповідна точка Home. Завантаження місії, що починається з команди посадки `NAV_LAND` або безпосереднього руху `NAV_WAYPOINT` на висоті 0 метрів, має блокуватися ще на землі.
2. **Перевірка абсолютних висот:** Усі висоти точок маршруту у системі координат `GLOBAL_RELATIVE_ALT_INT` повинні перевірятися на відповідність висоті безпечного польоту (англ. *minimum safe altitude*) над рельєфом місцевості та стелі дозволеного повітряного простору.
3. **Контроль довжини полігону:** Сумарна кількість точок не повинна перевищувати ліміт внутрішньої пам'яті автопілота (зазвичай 500–2000 точок для контролерів на базі STM32F7/H7).

Виконання цих перевірок на боці клієнта усуває ситуації, коли автопілот перериває транзакцію кодами `MAV_MISSION_INVALID_PARAM` або `MAV_MISSION_NO_SPACE` посеред передачі даних на злітній смузі.

## Інженерні граблі та захист від збоїв

При практичній реалізації протоколу місій виникає низка специфічних ситуацій, на яких найчастіше спотикаються розробники:

1. **Пастка дубліката запиту (Duplicate Request Handling):**
   Якщо станція надіслала `MISSION_ITEM_INT(seq=2)`, але цей пакет затримався в буфері радіомодема, автопілот через внутрішній таймаут повторно надішле `MISSION_REQUEST_INT(seq=2)`. FSM станції не повинен розцінювати повтор як помилку протоколу. Станція зобов'язана надіслати збережений пункт `seq=2` повторно та скинути лічильник спроб.

2. **Захист від нелінійних стрибків послідовності (Sequence Jump Attack / Corruption):**
   Якщо через збій лічильника автопілот запитує `seq = 8`, коли станція передала `seq = 1`, станція не має права надсилати точку з пропуском номерів. Завантажувач повинен надіслати `MISSION_ACK(MAV_MISSION_INVALID_SEQUENCE)` та перевести автомат у `FAILED`.

3. **Колізія з нульовою точкою Home Position:**
   В екосистемі ArduPilot нульовий пункт місії (`seq = 0`) завжди зарезервований під координати точки старту та повернення додому (англ. *Home location*). Безпосередній політ починається з точки `seq = 1` (наприклад, команди `MAV_CMD_NAV_TAKEOFF`). У PX4 нульова точка може бути безпосередньо першою навігаційною командою. При проектуванні універсального завантажувача необхідно враховувати діалектні особливості цільового автопілота при формуванні масиву `items`.

4. **Пастка розширеного поля `mission_type` у MAVLink 1 проти MAVLink 2:**
   У першій версії протоколу MAVLink поле `mission_type` було відсутнє, а протокол підтримував лише маршрутні точки. У MAVLink 2 це поле додано в кінець структури. Якщо відправник формує кадр MAVLink 1 або якщо проміжний радіомодем обрізає розширені байти, поле `mission_type` за замовчуванням заповнюється нулями. Якщо станція намагається завантажити геозону (`type = 1`), а борт отримує `0`, автопілот повністю затре діючу польотну місію замість оновлення геозони. Тому при роботі з геозонами та точками збору необхідно програмно форсувати використання виключно протоколу MAVLink 2.
