# ⚙️ Реалізація надійного завантажувача місій MAVLink

Надійна передача польотного плану на безпілотник вимагає побудови асинхронного кінцевого автомата (FSM), який керує послідовністю транзакцій за протоколом Stop-and-Wait ARQ. Клієнт не може надсилати точки суцільним масивом: він зобов'язаний очікувати явного запиту кожного пункту від автопілота, відстежувати часові інтервали очікування, обробляти повторні запити при втраті пакетів у радіоефірі та аналізувати фінальний код підтвердження `MISSION_ACK`.

---

## Архітектура кінцевого автомата завантажувача

Клієнтський автомат завантаження місії на дрон оперує шістьма внутрішніми станами, які забезпечують повну детермінованість поведінки в умовах нестабільного радіозв'язку:

```
Стани FSM клієнта:
  [IDLE] ─── (Start Upload) ───► [SENDING_COUNT]
                                       │
                                (MISSION_REQUEST_INT received)
                                       ▼
  [ERROR] ◄─── (Timeout / Retries > 5) ── [WAITING_REQUEST]
                                       │
                                (seq == count-1)
                                       ▼
  [COMPLETED] ◄─── (ACK: ACCEPTED) ─── [WAITING_ACK]
```

1. **`IDLE` (Очікування):** Клієнт вільний, транзакція не ініціалізована. Мережевий потік обробляє фонову телеметрію.
2. **`SENDING_COUNT` (Оголошення місії):** Клієнт надіслав пакет `MISSION_COUNT` і очікує перший запит `MISSION_REQUEST_INT(seq=0)` від автопілота.
3. **`WAITING_REQUEST` (Покрокова передача):** Клієнт надіслав черговий пункт `MISSION_ITEM_INT(seq=i)` і очікує запит на наступний елемент `MISSION_REQUEST_INT(seq=i+1)` або повторний запит поточного номера.
4. **`WAITING_ACK` (Очікування фіксації):** Усі елементи місії передано на борт; клієнт очікує фінальний пакет підтвердження `MISSION_ACK` із кодом результату запису у Flash-пам'ять.
5. **`COMPLETED` (Успішне завершення):** Термінальний стан. План польоту верифіковано та зафіксовано автопілотом.
6. **`FAILED` (Аварійне скасування):** Термінальний стан помилки. Виникає при вичерпанні ліміту повторних спроб або отриманні коду відхилення від польотного контролера.

---

## Покроковий опис логіки обробки подій та станів

Розгляньмо, як кінцевий автомат реагує на ключові мережеві та часові події під час сесії завантаження:

### 1. Ініціалізація транзакції (`startUpload`)
При виклику методу завантаження клієнт перевіряє непорожність переданого масиву навігаційних точок. Якщо список містить `N` елементів, автомат переходить у стан `SENDING_COUNT`, формує повідомлення `MISSION_COUNT` із параметром `count = N`, скидає внутрішній лічильник повторів `retry_count = 0` і фіксує поточну мітку часу таймера `last_action_time = now()`.

Початкова відправка `MISSION_COUNT` змушує польотний контролер виділити тимчасовий буфер у RAM і перейти у стан готовності до прийому даних. Якщо зв'язок відсутній, спрацьовує таймаут, і пакет відправляється повторно.

### 2. Прийом запиту елемента (`handleMissionRequestInt`)
Коли від польотного контролера надходить кадр `MISSION_REQUEST_INT`:
- Автомат перевіряє, чи перебуває він у стані `SENDING_COUNT` або `WAITING_REQUEST`. Якщо повідомлення прийшло в іншому стані, воно вважається запізнілим або некоректним і ігнорується.
- Перевіряється значення запитаного індексу `seq`. Якщо `seq ≥ N`, автопілот вийшов за межі виділеного діапазону — транзакція аварійно переривається з переходом у стан `FAILED`.
- Якщо `seq` валідний, клієнт формує повідомлення `MISSION_ITEM_INT` для відповідного пункту, відправляє його в радіоканал і оновлює таймер.
- Якщо запитаний пункт є останнім у списку (`seq == N - 1`), клієнт перемикає стан на `WAITING_ACK`. В іншому разі встановлюється стан `WAITING_REQUEST`.

### 3. Прийом підтвердження (`handleMissionAck`)
Отримавши повідомлення `MISSION_ACK`:
- Клієнт перевіряє поле `type` (код результату `MAV_MISSION_RESULT`).
- Якщо `type == MAV_MISSION_ACCEPTED` (значення 0), місію повністю зафіксовано у постійній пам'яті автопілота. Автомат переходить у стан `COMPLETED`.
- Якщо код результату відмінний від нуля (наприклад, `MAV_MISSION_UNSUPPORTED` або `MAV_MISSION_INVALID_PARAM2`), автопілот відхилив місію. Автомат реєструє помилку та переходить у стан `FAILED`.

### 4. Періодичний моніторинг таймаутів (`update`)
Головний цикл програми регулярно викликає функцію `update()`. Якщо з моменту останньої дії минуло більше ніж `timeout_duration` (типово 500 мс):
- Клієнт перевіряє лічильник повторів. Якщо `retry_count ≥ max_retries` (типово 5 спроб), канал вважається розірваним, і FSM переходить у `FAILED`.
- Якщо ліміт спроб не вичерпано, лічильник збільшується на 1, і клієнт повторно відправляє останній надісланий пакет (`MISSION_COUNT` або відповідний `MISSION_ITEM_INT`), після чого перезапускає таймер.

---

## Декомпозиція мережевого шару та обробка буферів

У реальних додатках на C++ або Python обробку транзакцій місій рекомендовано відокремлювати від низькорівневого вводу-виводу сокетів або послідовних портів UART за патерном Reactor. Мережевий потік безперервно зчитує байти з дескриптора, парсить кадри MAVLink за допомогою парсера кінцевого автомата `mavlink_parse_char()` та передає розпаковані структури у чергу повідомлень менеджера місій.

Такий підхід запобігає блокуванню транзакційного автомата під час повільних системних викликів запису у порт або при тимчасових затримках планувальника операційної системи.

### Динамічне регулювання частоти телеметрії (Stream Throttling)
Перед початком завантаження великих польотних завдань професійні наземні станції надсилають команду `MAV_CMD_SET_MESSAGE_INTERVAL` для тимчасового зменшення частоти потоків високошвидкісної телеметрії (наприклад, знижують частоту повідомлень `ATTITUDE` та `GLOBAL_POSITION_INT` з 50 Гц до 2 Гц). Це звільняє до 85% корисного часу радіолінії 57.6 кбіт/с, що практично виключає взаємні колізії пакетів у напівдуплексному каналі під час завантаження. Після отримання фінального `MISSION_ACK` наземна станція відновлює початкові інтервали трансляції телеметрії.

---

## Низькорівневий драйвер прийому UART та побайтовий парсинг

Надійний клієнт для мікроконтролерів або бортових комп'ютерів Linux реалізує побайтову обробку вхідного потоку через кільцевий буфер (*Ring Buffer*):

```
Структура обробки байтів UART:
[UART Rx DMA] ──► [Ring Buffer (1024 B)] ──► [mavlink_parse_char()] ──► [FSM Handler]
```

1. **Прийом за допомогою DMA:** Апаратний контролер DMA мікроконтролера записує вхідні байти безпосередньо в циклічний масив пам'яті без залучення процесора на кожне переривання байта.
2. **Пошук стартового маркера:** Парсер MAVLink сканує буфер у пошуках магічного байта `0xFD` (MAVLink v2) або `0xFE` (MAVLink v1). Будь-яке випадкове радіосміття в ефірі ігнорується до виявлення коректного маркера.
3. **Перевірка довжини та CRC-EXTRA:** Парсер зчитує поле довжини `len`, накопичує рівно `len + 12` байтів кадру та обчислює контрольну суму CRC-16 із домішуванням байта `CRC-EXTRA`. Лише кадри з валідною контрольною сумою передаються обробнику станів завантажувача.

---

## Багатопотокова синхронізація з графічним інтерфейсом користувача (GUI)

У сучасних наземних станціях керування (побудованих на базі Qt/C++, ImGui або Electron) мережевий транзакційний автомат і графічний інтерфейс користувача функціонують у різних операційних потоках:

- **Потік мережевого обміну (Telemetry & Protocol Thread):** Виконує неблокуюче опитування сокетів або послідовного порту через `epoll`/`poll` на Linux або `select` на Windows, керує таймерами Stop-and-Wait та обробляє кадрові квитанції.
- **Потік відображення (GUI Thread):** Відображає поточний статус завантаження для оператора на екрані.

Для безпечної передачі інформації про хід завантаження без виникнення стану гонитви (*Race Condition*) застосовується патерн атомарного стану або черга повідомлень з блокуванням м'ютексом:

```
Схема міжпотокової передачі статусу:
[Protocol Thread] ──► std::atomic<float> progress_percent ──► [GUI Progress Bar]
                  ──► Lock-free Event Queue ──────────────► [User Notification Dialog]
```

Прогрес завантаження розраховується як частка успішно переданих пунктів:

```
progress = (current_seq / (float)total_count) * 100.0f
```

Якщо транзакція переривається через таймаут або повернення помилки, мережевий потік надсилає у графічний потік подію скасування з розшифровкою коду `MAV_MISSION_RESULT`, що дозволяє інтерфейсу миттєво підсвітити помилковий пункт на карті червоним кольором і пояснити причину збою оператору без зависання віконної системи.

---

## Програмна реалізація

Нижче наведено повну реалізацію клієнта завантаження місії двома мовами: на сучасному ідіоматичному C++ (з використанням типізованих станів, структури `std::chrono` та суворої перевірки меж) та мовою Python (з використанням бібліотеки `pymavlink`).

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <chrono>
#include <optional>
#include <cstdint>
#include <cstring>
#include <stdexcept>

// Перелік станів кінцевого автомата завантажувача
enum class UploadState {
    Idle,
    SendingCount,
    WaitingRequest,
    WaitingAck,
    Completed,
    Failed
};

// Структура навігаційного пункту місії
struct MissionItem {
    uint16_t seq{0};
    uint16_t command{16}; // MAV_CMD_NAV_WAYPOINT (16)
    uint8_t frame{6};     // MAV_FRAME_GLOBAL_RELATIVE_ALT_INT (6)
    float param1{0.0f};   // Час зависання (Hold time), с
    float param2{2.0f};   // Радіус прийняття точки, м
    float param3{0.0f};   // Проліт через точку (Pass radius)
    float param4{0.0f};   // Бажаний курс (Yaw angle), град
    int32_t latitude_e7{0};  // Широта * 10^7
    int32_t longitude_e7{0}; // Довгота * 10^7
    float altitude{10.0f};   // Висота відносно точки старту, м
    bool autocontinue{true};
};

// Клас транзакційного завантажувача місії
class MissionUploader {
public:
    MissionUploader(uint8_t target_sys, uint8_t target_comp, 
                    std::chrono::milliseconds timeout = std::chrono::milliseconds(500),
                    uint32_t max_retries = 5)
        : target_system_(target_sys),
          target_component_(target_comp),
          timeout_duration_(timeout),
          max_retries_(max_retries),
          state_(UploadState::Idle) {}

    // Ініціалізація нової транзакції завантаження списку пунктів
    void startUpload(const std::vector<MissionItem>& items) {
        if (items.empty()) {
            throw std::invalid_argument("Список місії не може бути порожнім.");
        }
        mission_items_ = items;
        current_seq_ = 0;
        retry_count_ = 0;
        state_ = UploadState::SendingCount;

        // Оголошуємо кількість пунктів автопілоту
        sendMissionCount(static_cast<uint16_t>(mission_items_.size()));
        last_action_time_ = std::chrono::steady_clock::now();
        std::cout << "[FSM] Старт транзакції: оголошено " << mission_items_.size() << " пунктів.\n";
    }

    // Обробка вхідного повідомлення MISSION_REQUEST_INT від автопілота
    void handleMissionRequestInt(uint16_t requested_seq) {
        if (state_ != UploadState::SendingCount && state_ != UploadState::WaitingRequest) {
            std::cout << "[FSM] Отримано неочікуваний запит seq=" << requested_seq << " у неактивному стані.\n";
            return;
        }

        if (requested_seq >= mission_items_.size()) {
            std::cerr << "[FSM] Помилка: автопілот запросив seq=" << requested_seq 
                      << ", що перевищує розмір місії (" << mission_items_.size() << ").\n";
            state_ = UploadState::Failed;
            return;
        }

        // Автопілот запросив черговий або повторний пункт
        current_seq_ = requested_seq;
        retry_count_ = 0; // Успішний рух скидає лічильник повторів

        sendMissionItem(mission_items_[current_seq_]);
        last_action_time_ = std::chrono::steady_clock::now();

        // Якщо це останній пункт — переходимо до очікування фінального ACK
        if (current_seq_ + 1 == mission_items_.size()) {
            state_ = UploadState::WaitingAck;
            std::cout << "[FSM] Передано фінальний пункт seq=" << current_seq_ << ". Очікування ACK...\n";
        } else {
            state_ = UploadState::WaitingRequest;
            std::cout << "[FSM] Надіслано пункт seq=" << current_seq_ << ". Очікування наступного запиту...\n";
        }
    }

    // Обробка фінального повідомлення MISSION_ACK
    void handleMissionAck(uint8_t result_code) {
        if (state_ != UploadState::WaitingAck && state_ != UploadState::WaitingRequest) {
            return;
        }

        if (result_code == 0) { // MAV_MISSION_ACCEPTED
            state_ = UploadState::Completed;
            std::cout << "[FSM] УСПІХ: Місію зафіксовано у Flash автопілота (MAV_MISSION_ACCEPTED).\n";
        } else {
            state_ = UploadState::Failed;
            std::cerr << "[FSM] ПОМИЛКА: Автопілот відхилив місію з кодом помилки: " 
                      << static_cast<int>(result_code) << "\n";
        }
    }

    // Періодична функція оновлення таймерів (має викликатися у головному циклі програми)
    void update(std::chrono::steady_clock::time_point now) {
        if (state_ == UploadState::Idle || state_ == UploadState::Completed || state_ == UploadState::Failed) {
            return;
        }

        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - last_action_time_);
        if (elapsed > timeout_duration_) {
            if (retry_count_ >= max_retries_) {
                std::cerr << "[FSM] ТАЙМАУТ: Перевищено ліміт спроб (" << max_retries_ 
                          << "). Транзакцію скасовано.\n";
                state_ = UploadState::Failed;
                return;
            }

            retry_count_++;
            std::cout << "[FSM] Таймаут відповіді. Повторна спроба " << retry_count_ 
                      << " з " << max_retries_ << "...\n";

            if (state_ == UploadState::SendingCount) {
                sendMissionCount(static_cast<uint16_t>(mission_items_.size()));
            } else if (state_ == UploadState::WaitingRequest || state_ == UploadState::WaitingAck) {
                sendMissionItem(mission_items_[current_seq_]);
            }
            last_action_time_ = now;
        }
    }

    UploadState getState() const { return state_; }

private:
    void sendMissionCount(uint16_t count) {
        // У реальній системі тут викликається mavlink_msg_mission_count_pack() та відправка у UART/UDP
        std::cout << "  -> TX: MISSION_COUNT (count=" << count 
                  << ", target_sys=" << static_cast<int>(target_system_) << ")\n";
    }

    void sendMissionItem(const MissionItem& item) {
        // У реальній системі тут викликається mavlink_msg_mission_item_int_pack()
        std::cout << "  -> TX: MISSION_ITEM_INT (seq=" << item.seq 
                  << ", cmd=" << item.command << ", lat=" << item.latitude_e7 
                  << ", lon=" << item.longitude_e7 << ", alt=" << item.altitude << "m)\n";
    }

    uint8_t target_system_;
    uint8_t target_component_;
    std::chrono::milliseconds timeout_duration_;
    uint32_t max_retries_;

    UploadState state_;
    std::vector<MissionItem> mission_items_;
    uint16_t current_seq_{0};
    uint32_t retry_count_{0};
    std::chrono::steady_clock::time_point last_action_time_;
};
```
```python
import time
from pymavlink import mavutil

class PyMissionUploader:
    """Клієнт завантаження місії на автопілот через pymavlink."""

    def __init__(self, master: mavutil.mavfile, target_system: int = 1, 
                 target_component: int = 1, timeout: float = 0.5, max_retries: int = 5):
        self.master = master
        self.target_system = target_system
        self.target_component = target_component
        self.timeout = timeout
        self.max_retries = max_retries

    def upload_mission(self, mission_items: list) -> bool:
        """Транзакційне завантаження списку елементів місії."""
        count = len(mission_items)
        if count == 0:
            print("[PY-FSM] Помилка: список місії порожній.")
            return False

        print(f"[PY-FSM] Старт завантаження: {count} пунктів.")
        
        # Крок 1: Відправка MISSION_COUNT
        retries = 0
        seq = 0

        self._send_count(count)
        start_time = time.time()

        while True:
            # Очікуємо відповіді від автопілота
            msg = self.master.recv_match(
                type=["MISSION_REQUEST_INT", "MISSION_REQUEST", "MISSION_ACK"],
                blocking=False
            )

            current_time = time.time()

            if msg is not None:
                msg_type = msg.get_type()

                if msg_type in ["MISSION_REQUEST_INT", "MISSION_REQUEST"]:
                    req_seq = msg.seq
                    print(f"[PY-FSM] Отримано запит: seq={req_seq}")

                    if req_seq < count:
                        seq = req_seq
                        retries = 0
                        self._send_item(mission_items[seq])
                        start_time = time.time()
                    else:
                        print(f"[PY-FSM] Помилка: автопілот запросив неіснуючий seq={req_seq}")
                        return False

                elif msg_type == "MISSION_ACK":
                    ack_result = msg.type
                    if ack_result == mavutil.mavlink.MAV_MISSION_ACCEPTED:
                        print("[PY-FSM] УСПІХ: Місію прийнято та зафіксовано (MAV_MISSION_ACCEPTED).")
                        return True
                    else:
                        print(f"[PY-FSM] ВІДХИЛЕНО: Автопілот повернув код помилки {ack_result}.")
                        return False

            # Перевірка таймауту
            if current_time - start_time > self.timeout:
                if retries >= self.max_retries:
                    print(f"[PY-FSM] ТАЙМАУТ: Вичерпано ліміт спроб ({self.max_retries}). Відміна.")
                    return False

                retries += 1
                print(f"[PY-FSM] Таймаут. Повторна спроба {retries}/{self.max_retries}...")

                if seq == 0 and msg is None:
                    self._send_count(count)
                else:
                    self._send_item(mission_items[seq])

                start_time = time.time()

            time.sleep(0.01) # Запобігання 100% завантаженню CPU

    def _send_count(self, count: int):
        self.master.mav.mission_count_send(
            self.target_system,
            self.target_component,
            count,
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION
        )
        print(f"  -> TX: MISSION_COUNT(count={count})")

    def _send_item(self, item: dict):
        self.master.mav.mission_item_int_send(
            self.target_system,
            self.target_component,
            item["seq"],
            item.get("frame", mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT),
            item.get("command", mavutil.mavlink.MAV_CMD_NAV_WAYPOINT),
            item.get("current", 0),
            item.get("autocontinue", 1),
            item.get("param1", 0.0),
            item.get("param2", 2.0),
            item.get("param3", 0.0),
            item.get("param4", 0.0),
            int(item["lat"] * 1e7),
            int(item["lon"] * 1e7),
            float(item["alt"]),
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION
        )
        print(f"  -> TX: MISSION_ITEM_INT(seq={item['seq']}, alt={item['alt']}m)")
```
:::

---

## Тестування в симуляторі SITL та верифікація

Перед польовими випробуваннями клієнтський завантажувач місій обов'язково перевіряється у середовищі програмної симуляції Software-in-the-Loop (SITL):

1. **Запуск емулятора автопілота:**
   Для ArduPilot запуск здійснюється командою:
   `sim_vehicle.py -v ArduCopter --model quad --out 127.0.0.1:14550`
   Для PX4 запуск здійснюється командою:
   `make px4_sitl jmavsim`

2. **Емуляція втрати пакетів у каналі:**
   Для перевірки стійкості автомата до таймаутів утиліта посередник (`mavproxy.py` або власний проксі-скрипт) налаштовується на штучне відкидання 20–30% пакетів MAVLink. Коректно реалізований завантажувач повинен успішно завершити передачу місії через механізм повторних спроб без зриву транзакції.

3. **Верифікація цілісності місії після завантаження:**
   Після отримання підтвердження `MISSION_ACK` надійна наземна станція виконує автоматичне вивантаження маршруту назад на землю (`Download Flow`) і побайтово порівнює збережені у Flash координати із вихідним планом. Збіг усіх точок гарантує відсутність внутрішніх спотворень пам'яті автопілота.

---

## Діагностика через бортові журнали (ULog / DataFlash Binary Logs)

Коли під час польових випробувань виникають відхилення місії або збої валідації (`MAV_MISSION_UNSUPPORTED`, `MAV_MISSION_INVALID_PARAM`), точну причину відхилення можна визначити через аналіз бортових бінарних журналів автопілота:

1. **Журнали PX4 Autopilot (формат ULog `.ulg`):**
   - Утиліта аналізу: `ulog_info mission_flight.ulg` або веб-сервіс `Flight Review`.
   - Топік повідомлень: `mission` та `navigator_mission_item`. У цих топіках реєструються точні значення полів кожної прийнятої точки, стан тимчасового буфера `dataman` та системний код помилки валідації геометрії (наприклад, перевищення максимального ліміту допустимої дистанції між точками).
2. **Журнали ArduPilot (формат DataFlash `.bin`):**
   - Утиліта аналізу: `mavlogdump.py --types CMD,MSG flight.bin`.
   - Повідомлення `CMD`: Фіксує повну послідовність запису команд у віртуальний пул EEPROM із номерами параметрів та результатом парсингу. Якщо параметр команди порушує ліміти прошивки, у повідомленнях типу `MSG` з'являється текстове сповіщення підсистеми `AP_Mission` (наприклад, `Mission: Bad Command ID` або `Mission: Invalid Latitude`).

---

## Трасування дампа пакетів обміну (Hex Dump Analysis)

Для глибокого розуміння фізичного обміну розгляньмо трасування реальних байтів кадру MAVLink v2 під час передачі одного навігаційного пункту.

```
Трасування байтів кадру MISSION_ITEM_INT (38 байтів корисного навантаження):
[0xFD] [0x26] [0x00] [0x00] [0x14] [0xFF] [0xBE] [0x49] [0x00] [0x00] ... [CRC_LOW] [CRC_HIGH]
  │      │      │      │      │      │      │      │
  │      │      │      │      │      │      │      └─ Message ID: 0x000049 = 73 (MISSION_ITEM_INT)
  │      │      │      │      │      │      └─ CompID: 190 (GCS)
  │      │      │      │      │      └─ SysID: 255 (GCS Ground Station)
  │      │      │      │      └─ Sequence number: 20
  │      │      │      └─ Incompat/Compat flags
  │      │      └─ Length: 38 (0x26) байтів payload
  └─ Magic Byte MAVLink v2 (0xFD)
```

Коли приймач отримує цей двійковий масив:
1. Заголовок перевіряється на стартовий маркер `0xFD`.
2. Довжина корисного навантаження `0x26` (38 байтів) порівнюється з очікуваним розміром повідомлення ID #73.
3. Розраховується контрольна сума CRC-16 з урахуванням байта `CRC-EXTRA = 38`.
4. Якщо контрольна сума зійшлася, 38 байтів безпосередньо копіюються у структуру пам'яті автопілота без додаткового декодування.

---

## Адаптивний таймаут із експоненційним відступом (Exponential Backoff)

У каналах із сильним рівнем завад або при тимчасовому входженні безпілотника в радіотінь сталий таймаут 500 мс може створювати зайве навантаження на радіоефір повторними запитами, коли модем зайнятий переналаштуванням частоти (FHSS).

Для оптимізації обміну кінцевий автомат клієнта може використовувати експоненційний відступ:

```
T_retry(k) = min(T_base · 1.5ᵏ, T_max)
```

де:
- `T_base` — базовий таймаут очікування (500 мс);
- `k` — поточний номер невдалої спроби (0, 1, 2, ...);
- `T_max` — максимальний граничний таймаут (2500 мс).

Цей алгоритм дає радіоканалу час на стабілізацію та випорожнення апаратних черг радіомодему перед кожною наступною спробою повторного передавання кадру.

---

## Конфігурація апаратного зв'язку телеметрійних модемів

Для досягнення мінімальної кількості повторних транзакцій та виключення втрат пакетів через переповнення апаратних буферів, радіомодеми зв'язку (наприклад, модеми SiK Radio або RFD900) вимагають коректного узгодження швидкостей:

1. **Співвідношення швидкостей UART та ефіру:** Швидкість передачі в ефірі `AIR_SPEED` (наприклад, 64 кбіт/с) завжди повинна перевищувати або дорівнювати швидкості послідовного порту `SERIAL_SPEED` (57 600 біт/с). Якщо швидкість UART перевищує пропускну здатність радіоканалу, черга внутрішнього буфера модема швидко переповнюється, що призводить до відкидання пакетів на фізичному рівні.
2. **Апаратний контроль потоку RTS/CTS (Hardware Flow Control):** Використання ліній RTS/CTS між польотним контролером та радіомодемом дозволяє мікроконтролеру модема апаратно призупиняти видачу даних з UART, коли радіоканал зайнятий передачею або перебуває у фазі перемикання частоти FHSS.
3. **Кількість частотних каналів (Frequency Hopping Spread Spectrum):** При налаштуванні діапазону 915 МГц або 433 МГц рекомендується використовувати не менше ніж 24–50 псевдовипадкових каналів стрибків частоти. Це мінімізує тривалість пакетних колізій із сторонніми побутовими передавачами та забезпечує стабільний RTT для протоколу Stop-and-Wait.

---

## Моніторинг виконання та аварійні протоколи Failsafe

Після успішного завантаження місії клієнтська програма перемикається у режим пасивного моніторингу навігаційного процесу:

- **Обробка навігаційного зміщення (Cross-Track Error):** Повідомлення `NAV_CONTROLLER_OUTPUT` передає поточне лінійне відхилення апарата від прямої лінії між вейпоїнтами `xtrack_error` (метри) та похибку курсу `nav_bearing` (градуси). Якщо відхилення перевищує безпечний коридор польоту через сильний боковий вітер, наземна станція попереджає оператора про небезпеку зіткнення з перешкодами.
- **Поведінка при втраті радіозв'язку (Data Link Loss Failsafe):** Якщо безпілотник виходить за радіус дії наземної станції, параметр конфігурації `NAV_DLL_ACT` визначає дію автопілота: продовжувати виконання місії в автономному режимі (`Mission Continue`), негайно перейти до точки екстреного збору `RALLY` або розвернутися та повернутися на точку старту `RTL`.

## Автоматизоване тестування у конвеєрах CI/CD та віртуальні порти

Для забезпечення стабільної якості коду у процесі розробки наземних станцій, завантажувач місій тестується в автоматизованих конвеєрах CI/CD без підключення фізичного обладнання:

1. **Емуляція віртуального послідовного порту через `socat` (Linux):**
   Утиліта створює пару зв'язаних віртуальних терміналів:
   `socat -d -d pty,raw,echo=0 pty,raw,echo=0`
   Один кінець псевдотермінала підключається до тестованого клієнта на C++, а інший — до скрипта-імітатора автопілота на Python.
2. **Модульне тестування з імітацією втрат (Mock Fault Injection):**
   Тестовий стенд імітує різні класи збоїв:
   - Втрату кожного парного або непарного кадру `MISSION_ITEM_INT` для перевірки повторних запитів;
   - Затримку відповіді на 800 мс для перевірки спрацьовування таймауту;
   - Повернення кодів помилок `MAV_MISSION_NO_SPACE` та `MAV_MISSION_INVALID_PARAM5_X` для перевірки коректного аварійного завершення без зависання FSM;
   - Скидання віртуального з'єднання в середині транзакції для перевірки переходу у стан `FAILED`.

---

## Типові пастки реалізації та захист від збоїв

1. **Ігнорування `MISSION_REQUEST` старого формату:** Якщо клієнт надсилає `MISSION_COUNT` у форматі MAVLink v2, але підключається до старішої версії автопілота, пристрій може відповісти застарілим повідомленням `MISSION_REQUEST` (#40) замість `MISSION_REQUEST_INT` (#51). Клієнт повинен уміти приймати обидва типи повідомлень або автоматично транслювати координати в цілочисельний формат.
2. **Скидання лічильника спроб при отриманні того самого `seq`:** Якщо пакет `MISSION_ITEM_INT` загубився в радіоефірі, автопілот після власного внутрішнього таймауту повторно надішле `MISSION_REQUEST_INT` з тим самим значенням `seq`. Отримання дубліката запиту **не повинно** вважатися успішним просуванням уперед: таймер перезапускається, але лічильник спроб збільшується, щоб запобігти нескінченному зацикленню при односторонньому обриві радіозв'язку.
3. **Обробка розриву зв'язку під час запису Flash:** При переході до стану `WAITING_ACK` мікроконтролер автопілота записує тимчасовий буфер у енергонезалежну пам'ять (Flash/FRAM), що може тривати від 20 до 80 мілісекунд. У цей момент таймаут очікування фінального `ACK` на наземній станції рекомендовано збільшувати у 1.5–2 рази (`T_ack ≥ 1000 мс`) порівняно з міжелементними інтервалами.
4. **Використання часткового оновлення замість повного:** При зміні однієї точки в місії на 500 пунктів використання `MISSION_WRITE_PARTIAL_LIST` економить до 98% радіотрафіку та запобігає тривалому блокуванню каналу телеметрії.
