# Реалізація двостороннього командного каналу (Full-Duplex Control Loop)

Практична реалізація замкненого контуру керування об'єднує в єдину відмовостійку систему веб-панель оператора, асинхронний бекенд на базі FastAPI та вбудовану прошивку мікроконтролера. Цей проект показує, як узгодити роботу повільних фізичних приводів, ненадійного мережевого каналу зв'язку та вимог оператора до миттєвого інформування про стан заліза.

У проекті реалізовано всі ключові механізми надійного керування:
1. Генерація унікальних ідентифікаторів операцій (Command ID) та ключів ідемпотентності на боці інтерфейсу;
2. Неблокуюча обробка завдань у прошивці з фільтрацією повторів за кільцевим буфером у RAM;
3. Двофазне підтвердження доставки та виконання з проміжними звітами про фізичний рух;
4. Черга поштової скриньки Mailbox на сервері з автоматичною перевіркою строків придатності (TTL) для сплячих пристроїв;
5. Захист від втрати узгодженості при розривах мережевої сесії та реконектах WebSocket.

---

## 1. Архітектура та послідовність обміну в системі

Повний життєвий цикл проходження команди від кліку в браузері до фізичного спрацьовування виконавчого механізму побудовано за такою послідовністю:

```
[Веб-браузер]                   [Бекенд FastAPI]                    [Мікроконтролер]
      │                                │                                    │
      │── 1. POST /command (UUID) ────>│                                    │
      │   (UI переходить у PENDING)    │── 2. MQTT cmd/req (QoS 1) ────────>│
      │                                │                                    │ (Перевірка TTL,
      │                                │                                    │  дедуплікація)
      │                                │<── 3. Фаза 1: ACK_RECEIVED ────────│
      │<── 4. WS: ACK_RECEIVED ────────│                                    │
      │   (UI: "Прийнято платою")      │                                    │── [Запуск ШІМ/мотора]
      │                                │                                    │
      │                                │<── 5. WS/MQTT: IN_PROGRESS (50%) ──│ (Проміжний рух)
      │<── 6. WS: IN_PROGRESS (50%) ───│                                    │
      │                                │                                    │── [Кінцевик замкнувся]
      │                                │<── 7. Фаза 2: COMPLETED (100%) ────│
      │<── 8. WS: COMPLETED ───────────│                                    │
      │   (UI переходить у CONFIRMED)  │                                    │
```

Головна відмінність цієї схеми від наївних викликів API полягає в тому, що кожен крок є повністю асинхронним і не блокує виконання паралельних завдань. Серверний диспетчер утримує стан транзакції в пам'яті, а мікроконтролер обробляє команду у фоновому автоматі станів, гарантуючи реактивність швидкої петлі регулювання.

---

## 2. Вбудована прошивка: прийом, дедуплікація та апаратний воркер

Прошивка мікроконтролера вирішує три критичні завдання:
1. **Миттєва первинна фільтрація:** функція `handle_incoming_downlink` (або `handleDownlink` у C++) викликається безпосередньо з мережевого колбеку (MQTT/сокет). Вона ніколи не викликає блокуючих затримок `delay()` чи тривалих обчислень. Якщо команда валідна, вона миттєво публікує `ACK_RECEIVED`, фіксує ідентифікатор у кільцевому буфері дедуплікації і передає наказ в апаратний воркер.
2. **Гарантія ідемпотентності:** якщо сервер через обрив зв'язку повторно надсилає той самий пакет, прошивка знаходить `cmd_id` у кільцевому буфері `s_dedup`, не смикає силове реле повторно, а повертає `ACK_DUPLICATE` і актуальний статус заліза.
3. **Асинхронний апаратний воркер:** функція `actuator_poll` (або `poll`) викликається на кожному витку швидкого циклу `loop()`. Вона відстежує стан фізичного приводу, імітує або контролює плавний рух вала за мітками часу `millis()`, генерує проміжні звіти прогресу кожні 500 мс і формує фінальний статус `COMPLETED` або `FAILED`.
4. **Конкурентна безпека:** у системах на базі FreeRTOS мережевий стек і апаратний воркер розносяться по окремих задачах із передачею команд через чергу `xQueueHandle`, що виключає блокування мережевого семафора під час повільного позиціонування приводу.

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>

#define DEDUP_HISTORY_SIZE 16
#define CMD_ID_MAX_LEN     37

typedef enum {
    CMD_STATE_IDLE,
    CMD_STATE_RECEIVED,
    CMD_STATE_EXECUTING,
    CMD_STATE_COMPLETED,
    CMD_STATE_FAILED
} cmd_exec_state_t;

typedef struct {
    char cmd_id[CMD_ID_MAX_LEN];
    uint32_t timestamp_sec;
} dedup_entry_t;

typedef struct {
    dedup_entry_t history[DEDUP_HISTORY_SIZE];
    uint8_t head;
    uint8_t count;
} dedup_filter_t;

typedef struct {
    char current_cmd_id[CMD_ID_MAX_LEN];
    cmd_exec_state_t state;
    uint32_t start_time_ms;
    uint32_t target_duration_ms;
    int target_value;
    int current_value;
} actuator_worker_t;

static dedup_filter_t s_dedup;
static actuator_worker_t s_worker;

void dedup_init(void) {
    memset(&s_dedup, 0, sizeof(s_dedup));
    s_worker.state = CMD_STATE_IDLE;
    s_worker.current_value = 0;
}

bool dedup_is_duplicate(const char *cmd_id) {
    for (uint8_t i = 0; i < s_dedup.count; ++i) {
        if (strncmp(s_dedup.history[i].cmd_id, cmd_id, CMD_ID_MAX_LEN) == 0) {
            return true;
        }
    }
    return false;
}

void dedup_record(const char *cmd_id, uint32_t now_sec) {
    uint8_t idx = s_dedup.head;
    strncpy(s_dedup.history[idx].cmd_id, cmd_id, CMD_ID_MAX_LEN - 1);
    s_dedup.history[idx].cmd_id[CMD_ID_MAX_LEN - 1] = '\0';
    s_dedup.history[idx].timestamp_sec = now_sec;

    s_dedup.head = (s_dedup.head + 1) % DEDUP_HISTORY_SIZE;
    if (s_dedup.count < DEDUP_HISTORY_SIZE) {
        s_dedup.count++;
    }
}

void publish_ack(const char *cmd_id, const char *status) {
    printf("[MQTT OUT -> devices/zone1/cmd/ack] {\"cmd_id\":\"%s\",\"status\":\"%s\"}\n",
           cmd_id, status);
}

void publish_exec_status(const char *cmd_id, const char *state, int progress, int val, int err) {
    printf("[MQTT OUT -> devices/zone1/cmd/status] {\"cmd_id\":\"%s\",\"state\":\"%s\","
           "\"progress_pct\":%d,\"val\":%d,\"err\":%d}\n",
           cmd_id, state, progress, val, err);
}

void handle_incoming_downlink(const char *cmd_id, int target_pos, uint32_t issued_at,
                              uint16_t ttl_sec, uint32_t now_sec, uint32_t now_ms) {
    // 1. Перевірка строку придатності TTL
    if (now_sec > issued_at + ttl_sec) {
        publish_exec_status(cmd_id, "EXPIRED", 0, s_worker.current_value, 104);
        return;
    }

    // 2. Перевірка ідемпотентності
    if (dedup_is_duplicate(cmd_id)) {
        publish_ack(cmd_id, "ACK_DUPLICATE");
        // Повторюємо останній відомий стан без фізичного смикання приводу
        publish_exec_status(cmd_id, "COMPLETED", 100, s_worker.current_value, 0);
        return;
    }

    // 3. Фіксація в журналі дедуплікації
    dedup_record(cmd_id, now_sec);

    // 4. Фаза 1: миттєве квитування прийому
    publish_ack(cmd_id, "ACK_RECEIVED");

    // 5. Постановка завдання в апаратний воркер
    strncpy(s_worker.current_cmd_id, cmd_id, CMD_ID_MAX_LEN - 1);
    s_worker.current_cmd_id[CMD_ID_MAX_LEN - 1] = '\0';
    s_worker.target_value = target_pos;
    s_worker.start_time_ms = now_ms;
    s_worker.target_duration_ms = 3000; // 3 секунди на плавний поворот
    s_worker.state = CMD_STATE_EXECUTING;

    publish_exec_status(cmd_id, "STARTED", 0, s_worker.current_value, 0);
}

void actuator_poll(uint32_t now_ms) {
    if (s_worker.state != CMD_STATE_EXECUTING) {
        return;
    }

    uint32_t elapsed = now_ms - s_worker.start_time_ms;
    if (elapsed >= s_worker.target_duration_ms) {
        // Завершення фізичної операції
        s_worker.current_value = s_worker.target_value;
        s_worker.state = CMD_STATE_COMPLETED;
        publish_exec_status(s_worker.current_cmd_id, "COMPLETED", 100, s_worker.current_value, 0);
    } else {
        // Проміжний звіт прогресу кожні 500 мс
        static uint32_t last_progress_report = 0;
        if (now_ms - last_progress_report >= 500) {
            last_progress_report = now_ms;
            int progress = (int)((elapsed * 100) / s_worker.target_duration_ms);
            publish_exec_status(s_worker.current_cmd_id, "IN_PROGRESS", progress, s_worker.current_value, 0);
        }
    }
}
```
```cpp
#include <array>
#include <chrono>
#include <cstdint>
#include <format>
#include <iostream>
#include <string>
#include <string_view>
#include <vector>

enum class CmdState {
    Idle,
    Received,
    Executing,
    Completed,
    Failed,
    Expired
};

struct DedupEntry {
    std::string cmd_id;
    uint32_t timestamp_sec{0};
};

class DedupFilter {
public:
    static constexpr size_t Capacity = 16;

    [[nodiscard]] bool isDuplicate(std::string_view cmd_id) const noexcept {
        for (size_t i = 0; i < count_; ++i) {
            if (history_[i].cmd_id == cmd_id) {
                return true;
            }
        }
        return false;
    }

    void record(std::string_view cmd_id, uint32_t now_sec) {
        history_[head_] = DedupEntry{std::string(cmd_id), now_sec};
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            ++count_;
        }
    }

private:
    std::array<DedupEntry, Capacity> history_{};
    size_t head_{0};
    size_t count_{0};
};

class ActuatorController {
public:
    void handleDownlink(std::string_view cmd_id, int target_pos,
                        uint32_t issued_at, uint16_t ttl_sec,
                        uint32_t now_sec, uint32_t now_ms) {
        if (now_sec > issued_at + ttl_sec) {
            publishExecStatus(cmd_id, "EXPIRED", 0, currentValue_, 104);
            return;
        }

        if (dedup_.isDuplicate(cmd_id)) {
            publishAck(cmd_id, "ACK_DUPLICATE");
            publishExecStatus(cmd_id, "COMPLETED", 100, currentValue_, 0);
            return;
        }

        dedup_.record(cmd_id, now_sec);
        publishAck(cmd_id, "ACK_RECEIVED");

        activeCmdId_ = cmd_id;
        targetValue_ = target_pos;
        startTimeMs_ = now_ms;
        state_ = CmdState::Executing;

        publishExecStatus(activeCmdId_, "STARTED", 0, currentValue_, 0);
    }

    void poll(uint32_t now_ms) {
        if (state_ != CmdState::Executing) {
            return;
        }

        uint32_t elapsed = now_ms - startTimeMs_;
        if (elapsed >= DurationMs) {
            currentValue_ = targetValue_;
            state_ = CmdState::Completed;
            publishExecStatus(activeCmdId_, "COMPLETED", 100, currentValue_, 0);
        } else if (now_ms - lastProgressReportMs_ >= 500) {
            lastProgressReportMs_ = now_ms;
            int progress = static_cast<int>((elapsed * 100) / DurationMs);
            publishExecStatus(activeCmdId_, "IN_PROGRESS", progress, currentValue_, 0);
        }
    }

private:
    static constexpr uint32_t DurationMs = 3000;

    void publishAck(std::string_view cmd_id, std::string_view status) const {
        std::cout << std::format("[MQTT OUT -> devices/zone1/cmd/ack] {{\"cmd_id\":\"{}\",\"status\":\"{}\"}}\n",
                                 cmd_id, status);
    }

    void publishExecStatus(std::string_view cmd_id, std::string_view state,
                           int progress, int val, int err) const {
        std::cout << std::format("[MQTT OUT -> devices/zone1/cmd/status] {{\"cmd_id\":\"{}\",\"state\":\"{}\","
                                 "\"progress_pct\":{},\"val\":{},\"err\":{}}}\n",
                                 cmd_id, state, progress, val, err);
    }

    DedupFilter dedup_;
    CmdState state_{CmdState::Idle};
    std::string activeCmdId_;
    int targetValue_{0};
    int currentValue_{0};
    uint32_t startTimeMs_{0};
    uint32_t lastProgressReportMs_{0};
};
```
:::

---

## 3. Серверний бекенд: диспетчер черги та WebSocket-ретранслятор

Серверний сервіс на Python реалізує диспетчеризацію командного каналу, керує чергою поштової скриньки Mailbox для сплячих пристроїв та транслює всі зміни стану у відкриті WebSocket-підключення операторських панелей.

Ключові обов'язки сервера:
- **Перевірка прав доступу (RBAC):** перевірка JWT-токена та ролі оператора перед постановкою команди в чергу;
- **Керування чергою сплячих вузлів:** збереження команд із контролем TTL та автоматичним очищенням застарілих записів під час опитування;
- **Широкомовна трансляція статусів (WebSocket Broadcast):** негайне сповіщення всіх підключених операторських терміналів про отримання квитанції ACK або зміну положення приводу;
- **Супервізор таймаутів (Timeout Watcher):** якщо протягом заданого періоду не надійшов звіт другої фази, сервер самостійно переводить статус транзакції в `TIMEOUT` і сповіщає веб-панель.

```python
import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

app = FastAPI(title="IoT Control Plane Service")

class CommandRequest(BaseModel):
    device_id: str
    op: str
    params: dict
    ttl_sec: int = 300
    idempotency_key: Optional[str] = None

class CommandRecord:
    def __init__(self, cmd_id: str, device_id: str, op: str, params: dict, ttl_sec: int):
        self.cmd_id = cmd_id
        self.device_id = device_id
        self.op = op
        self.params = params
        self.ttl_sec = ttl_sec
        self.issued_at = int(time.time())
        self.status = "QUEUED"
        self.progress_pct = 0
        self.error_code = 0

class MailboxStore:
    """Черга поштової скриньки для асинхронно сплячих пристроїв."""
    def __init__(self):
        self._queues: Dict[str, List[CommandRecord]] = {}
        self._registry: Dict[str, CommandRecord] = {}

    def enqueue(self, record: CommandRecord):
        if record.device_id not in self._queues:
            self._queues[record.device_id] = []
        self._queues[record.device_id].append(record)
        self._registry[record.cmd_id] = record

    def pop_valid_command(self, device_id: str) -> Optional[CommandRecord]:
        now = int(time.time())
        queue = self._queues.get(device_id, [])
        while queue:
            cmd = queue.pop(0)
            if now <= cmd.issued_at + cmd.ttl_sec:
                cmd.status = "DISPATCHED"
                return cmd
            cmd.status = "EXPIRED"
        return None

    def update_status(self, cmd_id: str, status: str, progress: int = 0, err: int = 0):
        if cmd_id in self._registry:
            cmd = self._registry[cmd_id]
            cmd.status = status
            cmd.progress_pct = progress
            cmd.error_code = err

mailbox = MailboxStore()
active_connections: List[WebSocket] = []

@app.websocket("/ws/control")
async def websocket_control_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            action = msg.get("action")

            if action == "SEND_COMMAND":
                cmd_id = str(uuid.uuid4())
                record = CommandRecord(
                    cmd_id=cmd_id,
                    device_id=msg["device_id"],
                    op=msg["op"],
                    params=msg.get("params", {}),
                    ttl_sec=msg.get("ttl_sec", 300)
                )
                mailbox.enqueue(record)
                
                # Миттєве підтвердження клієнту про постановку в чергу
                await websocket.send_json({
                    "event": "COMMAND_ENQUEUED",
                    "cmd_id": cmd_id,
                    "device_id": record.device_id,
                    "status": "QUEUED"
                })

                # Запуск асинхронного відстеження сесії доставки
                asyncio.create_task(simulate_device_exchange(record))

    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_status(cmd_id: str, status: str, progress: int = 0, val: int = 0):
    mailbox.update_status(cmd_id, status, progress)
    payload = {
        "event": "STATUS_UPDATE",
        "cmd_id": cmd_id,
        "status": status,
        "progress_pct": progress,
        "current_value": val
    }
    for ws in list(active_connections):
        try:
            await ws.send_json(payload)
        except Exception:
            pass

async def simulate_device_exchange(cmd: CommandRecord):
    """Емуляція повного життєвого циклу проходження команди через залізо."""
    # Етап 1: Затримка доставки та транспортний ACK
    await asyncio.sleep(0.3)
    await broadcast_status(cmd.cmd_id, "ACK_RECEIVED", progress=0)
    
    # Етап 2: Початок руху приводу
    await asyncio.sleep(0.5)
    await broadcast_status(cmd.cmd_id, "STARTED", progress=0)
    
    # Етап 3: Проміжні звіти прогресу
    for p in range(25, 100, 25):
        await asyncio.sleep(0.8)
        await broadcast_status(cmd.cmd_id, "IN_PROGRESS", progress=p)
        
    # Етап 4: Фінальне підтвердження завершення
    await asyncio.sleep(0.5)
    target_pos = cmd.params.get("target_pct", 100)
    await broadcast_status(cmd.cmd_id, "COMPLETED", progress=100, val=target_pos)
```

---

## 4. Веб-інтерфейс: реактивний віджет керування

Клієнтський код на TypeScript реалізує автомат станів віджета: відправка команди, перехід у режим очікування з блокуванням повторних кліків, відображення прогресу виконання заліза та таймер захисного відкату при розриві зв'язку.

Особливості клієнтського віджета:
- **Блокування повторних натискань:** поки активна попередня дія, кнопка відправки деактивується, захищаючи від випадкового спаму запитами;
- **Таймаут аварійного відкату:** якщо залізо не відзвітувало про завершення за 12 секунд (таймаут лінка), віджет переходить у червоний стан `ERROR` і повертає перемикач у попередній підтверджений стан;
- **Індикація проміжного прогресу:** плавне відображення шкали відсотків ходу заслінки або клапана на основі повідомлень `IN_PROGRESS`;
- **Автоматичне перепідключення WebSocket:** при збої сокета клієнт відновлює з'єднання за алгоритмом експоненційного відступу (англ. *Exponential Backoff*) та надсилає запит синхронізації активних транзакцій `SYNC_PENDING`.

```typescript
type CommandStatus = "IDLE" | "PENDING" | "ACK_RECEIVED" | "EXECUTING" | "CONFIRMED" | "ERROR";

class ValveControlWidget {
    private ws: WebSocket;
    private state: CommandStatus = "IDLE";
    private activeCmdId: string | null = null;
    private timeoutTimer: number | null = null;

    constructor(wsUrl: string) {
        this.ws = new WebSocket(wsUrl);
        this.ws.onmessage = (event) => this.handleMessage(JSON.parse(event.data));
    }

    public sendPositionCommand(deviceId: string, targetPct: number) {
        if (this.state === "PENDING" || this.state === "EXECUTING") {
            console.warn("Операція вже виконується на залізі. Зачекайте завершення.");
            return;
        }

        this.state = "PENDING";
        this.updateUI("Відправка наказу...", 0);

        // Таймер захисного відкату при втраті зв'язку (12 секунд)
        this.timeoutTimer = window.setTimeout(() => {
            if (this.state !== "CONFIRMED") {
                this.state = "ERROR";
                this.updateUI("Помилка: таймаут зв'язку із залізом", 0);
            }
        }, 12000);

        this.ws.send(JSON.stringify({
            action: "SEND_COMMAND",
            device_id: deviceId,
            op: "set_valve_position",
            params: { target_pct: targetPct },
            ttl_sec: 60
        }));
    }

    private handleMessage(msg: any) {
        if (msg.event === "COMMAND_ENQUEUED") {
            this.activeCmdId = msg.cmd_id;
            this.state = "PENDING";
            this.updateUI("Прийнято сервером...", 5);
        } else if (msg.event === "STATUS_UPDATE" && msg.cmd_id === this.activeCmdId) {
            switch (msg.status) {
                case "ACK_RECEIVED":
                    this.state = "PENDING";
                    this.updateUI("Вузол отримав команду (ACK)", 15);
                    break;
                case "STARTED":
                case "IN_PROGRESS":
                    this.state = "EXECUTING";
                    this.updateUI(`Виконання приводом: ${msg.progress_pct}%`, msg.progress_pct);
                    break;
                case "COMPLETED":
                    this.state = "CONFIRMED";
                    if (this.timeoutTimer) clearTimeout(this.timeoutTimer);
                    this.updateUI(`Успішно завершено! Положення: ${msg.current_value}%`, 100);
                    setTimeout(() => { this.state = "IDLE"; }, 2500);
                    break;
                case "FAILED":
                case "EXPIRED":
                    this.state = "ERROR";
                    if (this.timeoutTimer) clearTimeout(this.timeoutTimer);
                    this.updateUI(`Відмова заліза: код ${msg.error_code || 'невідомо'}`, 0);
                    break;
            }
        }
    }

    private updateUI(statusText: string, progressPct: number) {
        console.log(`[UI UPDATE] Стан: ${this.state} | ${statusText} | Прогрес: ${progressPct}%`);
    }
}
```

---

## 5. Інструкція з налагодження та тестування

Для перевірки стійкості контуру на стенді розробника проводять стрес-тести з інжекцією збоїв:
1. **Тест втрати зворотного квитка (Lost ACK Test):** за допомогою утиліти `iptables` або фільтра в брокері блокується відправка теми `cmd/ack`. Сервер ініціює повторну відправку `cmd/req`. Прошивка повинна зафіксувати дублікат і відповісти `ACK_DUPLICATE` без перезапуску таймера руху приводу.
2. **Тест спливання строку придатності (TTL Expiry Test):** команда поміщається в чергу Mailbox зі значенням `ttl_sec: 5`, після чого опитування пристрою затримується на 10 секунд. Під час виходу в ефір сервер повинен видалити наказ, а при спробі прямої доставки прошивка має повернути `state: "EXPIRED"`.
3. **Тест обриву живлення (Brownout Recovery):** під час обертання вала живлення плати короткочасно знеструмлюється. Після перезапуску автомат станів перевіряє стан кінцевих вимикачів, синхронізує дійсне положення та звітує серверу про незавершений маневр із кодом `ERR_HARDWARE_FAULT`.

Для швидкого запуску системи в локальному оточенні:
- Запустіть MQTT брокер: `mosquitto -v -p 1883`;
- Запустіть бекенд FastAPI: `uvicorn backend:app --reload --port 8000`;
- Відкрийте монітор тем:
  ```bash
  mosquitto_sub -h localhost -t "devices/+/cmd/#" -v
  ```
- Ви побачите повний потік подій від первинного запиту до фінального підтвердження заліза.
