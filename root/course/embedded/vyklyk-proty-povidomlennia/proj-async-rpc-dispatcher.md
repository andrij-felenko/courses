# ⚙️ Неблокуючий корелятор запитів і відповідей (Async RPC Correlator)

Практична реалізація гібридного комунікаційного рушія для вбудованих систем: клієнтський код отримує зручність семантики «запит–відповідь», але потік виконання ніколи не блокується в очікуванні повільного або нестабільного каналу зв'язку.

Уся пам'ять для збереження стану транзакцій виділяється статично під час компіляції (Zero-Allocation), що повністю виключає фрагментацію оперативної пам'яті (RAM) та усуває ризик раптового вичерпання купи (`heap exhaustion`) під час пікових навантажень.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   АРХІТЕКТУРА НЕБЛОКУЮЧОГО ДИСПЕТЧЕРА                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [Прикладна задача] ── async_request() ──> [ Статична таблиця слотів ]     │
│        ▲                                      • trans_id = 42               │
│        │                                      • timeout_ms = 200            │
│        │ on_complete(result)                  • callback / token            │
│        │                                                  │                 │
│        ▼                                                  ▼                 │
│  [Вхідний потік RX] ── dispatch_rx(frame) ──> [ Зіставлення за ID ]         │
│                                                           │                 │
│  [Системний таймер] ── correlator_tick() ───> [ Очищення таймаутів ]        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Інженерний задум та життєвий цикл транзакції

Класичний синхронний RPC заморожує потік задачі на час очікування відповіді. У неблокуючому кореляторі операція «запит–відповідь» розбивається на три повністю незалежні в часі фази:

1. **Фаза реєстрації (`Register`)**:
   Прикладна задача (наприклад, алгоритм навігації або контролер живлення) формує корисне навантаження команди. Корелятор знаходить перший вільний слот у статичному масиві, генерує новий унікальний ідентифікатор транзакції `trans_id`, фіксує дедлайн виконання і зберігає вказівник на функцію зворотного виклику (*callback*) разом із контекстом користувача. Запит укладається у вихідний буфер передавача (TX Queue / DMA), а функція негайно повертає присвоєний `trans_id`. Стек задачі звільняється менш ніж за 5 мікросекунд.

2. **Фаза диспетчеризації відповіді (`Dispatch`)**:
   Коли віддалений мікроконтролер завершує обробку і надсилає назад пакет-відповідь, приймальний обробник переривання (ISR) або фонова задача розбору кадрів витягує з заголовка поле `trans_id`. Корелятор виконує лінійний пошук серед активних слотів. Якщо збіг знайдено:
   - стан слота скидається у `SLOT_FREE` **до** виклику користувацького коду (це критично для запобігання дедлоку, якщо callback захоче відправити наступний запит);
   - викликається зареєстрований callback, куди передаються статус операції та спан отриманих байтів.

3. **Фаза контролю дедлайнів (`Tick / Sweep`)**:
   Періодичний таймер RTOS або системний тік (SysTick) раз на 10 мс викликає функцію `correlator_tick()`. Вона зменшує лічильники часу активних транзакцій. Якщо віддалений вузол не відповів у межах встановленого таймауту, корелятор примусово звільняє слот і викликає callback із кодом помилки `CORR_STATUS_TIMEOUT`. Завдяки цьому завислі запити ніколи не витікають і не блокують ресурси системи.

---

## Реалізація на C та C++

У лістингах нижче наведено виробничу реалізацію корелятора:
- версія для C орієнтована на мінімальний footprint у прошивках для FreeRTOS, Zephyr або bare-metal систем без ОС;
- версія для C++ використовує сучасні безпечні абстракції: `std::span` для уникнення копіювання буферів, `std::expected` для явної обробки помилок та статичний контейнер `std::array` без динамічної пам'яті.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CORRELATOR_MAX_PENDING 8
#define CORRELATOR_INVALID_ID  0

typedef enum {
    CORR_STATUS_OK = 0,
    CORR_STATUS_TIMEOUT,
    CORR_STATUS_ERROR_REMOTE,
    CORR_STATUS_BUSY,
    CORR_STATUS_INVALID_ARG
} CorrStatus_t;

/* Опис відповіді віддаленого вузла */
typedef struct {
    uint16_t trans_id;
    CorrStatus_t status;
    const uint8_t *payload;
    size_t payload_len;
} CorrResponse_t;

/* Сигнатура функції зворотного виклику */
typedef void (*CorrCallback_t)(const CorrResponse_t *response, void *user_arg);

typedef enum {
    SLOT_FREE = 0,
    SLOT_PENDING
} SlotState_t;

typedef struct {
    SlotState_t state;
    uint16_t trans_id;
    uint32_t timeout_remaining_ms;
    CorrCallback_t callback;
    void *user_arg;
} PendingSlot_t;

typedef struct {
    PendingSlot_t slots[CORRELATOR_MAX_PENDING];
    uint16_t next_trans_id;
} AsyncCorrelator_t;

/* Ініціалізація структури корелятора */
void correlator_init(AsyncCorrelator_t *corr) {
    if (!corr) return;
    memset(corr, 0, sizeof(AsyncCorrelator_t));
    corr->next_trans_id = 1;
}

/* Генерація унікального ненульового Transaction ID з перевіркою зайнятості */
static uint16_t generate_unique_id(AsyncCorrelator_t *corr) {
    for (size_t attempts = 0; attempts < 65535; ++attempts) {
        uint16_t candidate = corr->next_trans_id++;
        if (corr->next_trans_id == CORRELATOR_INVALID_ID) {
            corr->next_trans_id = 1;
        }

        /* Перевіряємо, чи цей ID вже не зайнятий іншою довгою транзакцією */
        bool in_use = false;
        for (size_t i = 0; i < CORRELATOR_MAX_PENDING; ++i) {
            if (corr->slots[i].state == SLOT_PENDING && 
                corr->slots[i].trans_id == candidate) {
                in_use = true;
                break;
            }
        }

        if (!in_use) {
            return candidate;
        }
    }
    return CORRELATOR_INVALID_ID;
}

/* Реєстрація нового асинхронного запиту */
CorrStatus_t correlator_register_request(AsyncCorrelator_t *corr,
                                        uint32_t timeout_ms,
                                        CorrCallback_t callback,
                                        void *user_arg,
                                        uint16_t *out_trans_id) {
    if (!corr || !callback || !out_trans_id || timeout_ms == 0) {
        return CORR_STATUS_INVALID_ARG;
    }

    /* Пошук вільного слота у статичному масиві */
    for (size_t i = 0; i < CORRELATOR_MAX_PENDING; ++i) {
        if (corr->slots[i].state == SLOT_FREE) {
            uint16_t id = generate_unique_id(corr);
            if (id == CORRELATOR_INVALID_ID) {
                return CORR_STATUS_BUSY;
            }

            corr->slots[i].state = SLOT_PENDING;
            corr->slots[i].trans_id = id;
            corr->slots[i].timeout_remaining_ms = timeout_ms;
            corr->slots[i].callback = callback;
            corr->slots[i].user_arg = user_arg;

            *out_trans_id = id;
            return CORR_STATUS_OK;
        }
    }

    /* Всі слоти зайняті: зворотний тиск (Backpressure) */
    return CORR_STATUS_BUSY;
}

/* Маршрутизація вхідного кадру відповіді */
bool correlator_dispatch_response(AsyncCorrelator_t *corr,
                                  uint16_t trans_id,
                                  CorrStatus_t status,
                                  const uint8_t *payload,
                                  size_t payload_len) {
    if (!corr || trans_id == CORRELATOR_INVALID_ID) {
        return false;
    }

    for (size_t i = 0; i < CORRELATOR_MAX_PENDING; ++i) {
        if (corr->slots[i].state == SLOT_PENDING && 
            corr->slots[i].trans_id == trans_id) {
            
            CorrResponse_t resp = {
                .trans_id = trans_id,
                .status = status,
                .payload = payload,
                .payload_len = payload_len
            };

            CorrCallback_t cb = corr->slots[i].callback;
            void *arg = corr->slots[i].user_arg;

            /* Звільняємо слот ДО виклику callback */
            corr->slots[i].state = SLOT_FREE;

            if (cb) {
                cb(&resp, arg);
            }
            return true;
        }
    }

    /* Відповідь для невідомого або вже скасованого за таймаутом запиту */
    return false;
}

/* Періодичний тік таймера дедлайнів (наприклад, раз на 10 мс) */
void correlator_tick(AsyncCorrelator_t *corr, uint32_t elapsed_ms) {
    if (!corr || elapsed_ms == 0) return;

    for (size_t i = 0; i < CORRELATOR_MAX_PENDING; ++i) {
        if (corr->slots[i].state == SLOT_PENDING) {
            if (corr->slots[i].timeout_remaining_ms <= elapsed_ms) {
                CorrResponse_t timeout_resp = {
                    .trans_id = corr->slots[i].trans_id,
                    .status = CORR_STATUS_TIMEOUT,
                    .payload = NULL,
                    .payload_len = 0
                };

                CorrCallback_t cb = corr->slots[i].callback;
                void *arg = corr->slots[i].user_arg;

                corr->slots[i].state = SLOT_FREE;

                if (cb) {
                    cb(&timeout_resp, arg);
                }
            } else {
                corr->slots[i].timeout_remaining_ms -= elapsed_ms;
            }
        }
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <expected>
#include <functional>

enum class CorrStatus : uint8_t {
    Ok = 0,
    Timeout,
    RemoteError,
    Busy,
    InvalidArg
};

struct Response {
    uint16_t trans_id{0};
    CorrStatus status{CorrStatus::Ok};
    std::span<const uint8_t> payload{};
};

using ResponseCallback = std::function<void(const Response&)>;

template <size_t MaxPending = 8>
class AsyncCorrelator {
public:
    constexpr AsyncCorrelator() = default;

    // Реєстрація запиту з неблокуючим зворотним викликом
    std::expected<uint16_t, CorrStatus> registerRequest(
        uint32_t timeout_ms,
        ResponseCallback callback) 
    {
        if (!callback || timeout_ms == 0) {
            return std::unexpected(CorrStatus::InvalidArg);
        }

        for (auto& slot : slots_) {
            if (!slot.is_active) {
                uint16_t id = generateUniqueId();
                if (id == 0) {
                    return std::unexpected(CorrStatus::Busy);
                }

                slot.is_active = true;
                slot.trans_id = id;
                slot.timeout_remaining_ms = timeout_ms;
                slot.callback = std::move(callback);

                return id;
            }
        }
        return std::unexpected(CorrStatus::Busy);
    }

    // Маршрутизація вхідної відповіді
    bool dispatchResponse(uint16_t trans_id, CorrStatus status, std::span<const uint8_t> payload) {
        if (trans_id == 0) return false;

        for (auto& slot : slots_) {
            if (slot.is_active && slot.trans_id == trans_id) {
                Response resp{trans_id, status, payload};
                auto cb = std::move(slot.callback);
                slot.is_active = false;

                if (cb) {
                    cb(resp);
                }
                return true;
            }
        }
        return false;
    }

    // Періодичне обслуговування таймерів дедлайнів
    void tick(uint32_t elapsed_ms) {
        if (elapsed_ms == 0) return;

        for (auto& slot : slots_) {
            if (slot.is_active) {
                if (slot.timeout_remaining_ms <= elapsed_ms) {
                    Response timeout_resp{slot.trans_id, CorrStatus::Timeout, {}};
                    auto cb = std::move(slot.callback);
                    slot.is_active = false;

                    if (cb) {
                        cb(timeout_resp);
                    }
                } else {
                    slot.timeout_remaining_ms -= elapsed_ms;
                }
            }
        }
    }

private:
    uint16_t generateUniqueId() {
        for (size_t attempt = 0; attempt < 65535; ++attempt) {
            uint16_t candidate = next_id_++;
            if (next_id_ == 0) next_id_ = 1;

            bool in_use = false;
            for (const auto& slot : slots_) {
                if (slot.is_active && slot.trans_id == candidate) {
                    in_use = true;
                    break;
                }
            }

            if (!in_use) {
                return candidate;
            }
        }
        return 0;
    }

    struct Slot {
        bool is_active{false};
        uint16_t trans_id{0};
        uint32_t timeout_remaining_ms{0};
        ResponseCallback callback{};
    };

    std::array<Slot, MaxPending> slots_{};
    uint16_t next_id_{1};
};
```
:::

---

## Порівняльний аналіз пам'яті та швидкодії

Оцінімо реальні апаратні витрати цього патерну на 32-бітному ядрі ARM Cortex-M4 (STM32 або NXP i.MX RT):

```
+-----------------------------------------------------------------------------+
|                      БЮДЖЕТ ПАМ'ЯТІ ТА ПРОДУКТИВНОСТІ                       |
+--------------------------+-----------------------+--------------------------+
| Параметр                 | Синхронний RPC        | Неблокуючий корелятор    |
+--------------------------+-----------------------+--------------------------+
| Кількість задач RTOS     | 8 задач (по одній     | 1 фонова задача обробки  |
| на 8 паралельних запитів | на кожне очікування)  | на всю комунікацію       |
| Обсяг RAM під стеки RTOS | 8 × 2048 Б = 16384 Б  | 1 × 1536 Б = 1536 Б      |
| Статична таблиця слотів  | 0 Б                   | 8 × 24 Б = 192 Б         |
| Сумарна пам'ять RAM      | 16.4 КБ               | 1.7 КБ (економія 90 %)   |
| Час виклику (TX latency) | 10–200 мс (зависання) | 2.4 мкс (280 тактів CPU) |
| Перемикання контексту    | 4 на кожну транзакцію | 0 під час відправки      |
+--------------------------+-----------------------+--------------------------+
```

Таблиця наочно ілюструє, чому заміна синхронних потоків на статичну таблицю кореляції є ключовим інженерним прийомом у мікроконтролерах із суворим лімітом RAM: при тій самій функціональності витрати пам'яті зменшуються на порядок.

---

## Інженерні тонкощі експлуатації в польових умовах

Під час впровадження неблокуючого корелятора у високошвидкісні польові протоколи (CAN, RS-485, радіомодеми) необхідно враховувати чотири апаратні пастки:

### 1. Потокобезпека та виклики з обробників переривань (ISR Safety)
У реальній прошивці функція `correlator_register_request()` викликається з контексту прикладної задачі RTOS, `correlator_tick()` — з періодичного таймера операційної системи, а `correlator_dispatch_response()` часто смикається безпосередньо з обробника переривання UART RX або шини CAN.
Щоб запобігти стану гонитви (*race condition*) під час одночасного модифікування масиву `slots`, доступ до таблиці слотів необхідно захищати:
- у FreeRTOS на рівні задач — м'ютексом або двійковим семафором;
- між задачею та перериванням — критичною секцією (`taskENTER_CRITICAL()` / `taskEXIT_CRITICAL()`) або передачею кадру з ISR у фонову задачу через безблокуючу чергу `xQueueSendFromISR()`.

### 2. Запобігання колізіям під час переповнення лічильника (`wrap-around`)
16-бітний лічильник `trans_id` скидається в 1 кожні 65535 викликів. Якщо в системі є завислий запит із великим дедлайном (наприклад, стирання Flash-пам'яті тривалістю 10 секунд), а потік дрібних швидких транзакцій встигне пройти повне коло лічильника, новий запит може випадково отримати той самий числовий ID. Функція `generate_unique_id()` гарантує відсутність колізій, перевіряючи згенерований номер по всій таблиці перед видачею.

### 3. Захист від запізнілих відповідей (Stale Responses)
Якщо зв'язок пропав на 300 мс, корелятор переведе запит у статус `TIMEOUT` і звільнить слот. Через 500 мс лінія відновлюється, і сервер нарешті надсилає стару відповідь. Оскільки слот уже вільний (або повторно зайнятий новим запитом із іншим ID), функція `correlator_dispatch_response()` просто повертає `false` і безпечно відкидає запізнілий пакет, не порушуючи логіку поточної транзакції.

### 4. Інваріант очищення слота перед виконанням зворотного виклику
Звільнення слота (`state = SLOT_FREE`) **суворо зобов'язане передувати** виконанню `cb(&resp, arg)`. Якщо користувацька функція callback є частиною ланцюжка послідовних кроків (наприклад, крок 1 завершився успішно і треба негайно відправити запит кроку 2), вона викликає `correlator_register_request()`. Якби слот не був очищений завчасно, при повністю заповненій таблиці новий запит зазнав би помилки `CORR_STATUS_BUSY`.
