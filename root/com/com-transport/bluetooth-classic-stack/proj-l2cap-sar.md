# ⚙️ Рушій сегментації та збирання кадрів L2CAP

Протокол логічного керування каналом та адаптації (англ. *Logical Link Control and Adaptation Protocol*, L2CAP) виконує ключову роль у стеку Bluetooth: він перетворює обмежені за розміром асинхронні пакети радіоконтролера Baseband на повнорозмірні пакети вищих рівнів (SDU) розміром до 64 кілобайтів. Ця функція називається **SAR** (англ. *Segmentation and Reassembly*, «сегментація та збирання»).

```
               ВХІДНИЙ ПОТІК ВІД КОНТРОЛЕРА (HCI ACL DATA)
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                ПЕРЕВІРКА ПРАПОРА PB FLAG                │
       └────────────┬───────────────────────────────┬────────────┘
                    │                               │
            PB = 0b10 (Початок)             PB = 0b01 (Продовження)
                    │                               │
                    ▼                               ▼
       ┌─────────────────────────┐     ┌─────────────────────────┐
       │ Читання Length + CID    │     │ Пошук контексту збирання│
       │ Виділення буфера SDU    │     │ Дописування байтів у SDU│
       └────────────┬────────────┘     └────────────┬────────────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │         ЧИ ЗІБРАНО ВСІ БАЙТИ (Отримано == Length)?      │
       └────────────┬───────────────────────────────┬────────────┘
                    │ ТАК                           │ НІ
                    ▼                               ▼
       ┌─────────────────────────┐     ┌─────────────────────────┐
       │ Маршрутизація на CID:   │     │ Очікування наступного   │
       │ 0x0001: Диспетчер SDP   │     │ фрагмента з ефіру       │
       │ 0x0002: Сигнальний L2CAP│     └─────────────────────────┘
       │ 0x0040+: Сесія RFCOMM   │
       └─────────────────────────┘
```

---

### Чому рівню L2CAP необхідний механізм SAR

Фізичний та канальний рівні Bluetooth Classic (Baseband) оперують дуже короткими квантами ефірного часу — слотами тривалістю 625 мкс. Максимальний обсяг корисних даних, який апаратний контролер здатен передати в межах одного найдовшого 5-слотового пакету базової швидкості (DH5), становить рівно 339 байтів. Навіть при використанні підвищеної швидкості EDR (пакет 3-DH5) межа одного пакету радіоконтролера обмежена 1021 байтом.

Водночас мережеві протоколи та прикладні служби проектувалися з розрахунку на значно більші блоки даних. Наприклад, передавання кадрів Ethernet через профіль BNEP вимагає MTU не менше 1500 байтів, передавання високоякісного аудіопотоку SBC/AAC через протокол AVDTP генерує аудіокадри по кілька кілобайтів, а протокол виявлення служб SDP може повертати списки атрибутів розміром до кількох десятків кілобайтів.

Якби протоколи верхнього рівня мали напряму враховувати обмеження поточної модуляції ефіру та розміру буферів радіочіпа, архітектура стека перетворилася б на монолітний клубок залежностей. Рівень L2CAP вирішує цю проблему, створюючи уніфіковану абстракцію:
1. **Зверху (для застосунків)** L2CAP надає інтерфейс передавання та приймання повнорозмірних блоків даних SDU (англ. *Service Data Unit*) розміром до 65 535 байтів із гарантією збереження меж повідомлень (Message-oriented channel).
2. **Знизу (для контролера)** L2CAP розбиває кожен SDU на послідовність дрібних блоків PDU (англ. *Protocol Data Unit*), розмір яких точно підігнано під можливості поточного з'єднання HCI ACL.

---

### Структура базового заголовка L2CAP та простору каналів (CID)

Кожен кадр L2CAP у базовому режимі (Basic Information Frame, B-frame) починається з фіксованого 4-байтового заголовка:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Length (16 бітів)       |     Channel ID (16 бітів)     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|             Корисне навантаження кадру (0 .. MTU байтів)      |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- **Length** (16 бітів): довжина поля корисного навантаження кадру в байтах. Значення не включає сам 4-байтовий заголовок L2CAP.
- **Channel ID (CID)** (16 бітів): числовий ідентифікатор логічного каналу. Простір ідентифікаторів розділено на фіксовані службові канали та динамічно виділені канали застосунків.

#### Карта простору ідентифікаторів каналів (CID)

| Діапазон CID | Тип каналу | Призначення та протокол |
| :--- | :--- | :--- |
| `0x0000` | **Null Identifier** | Зарезервовано; неприпустимий ідентифікатор (ознака помилки) |
| `0x0001` | **L2CAP Signaling (BR/EDR)** | Обмін командами встановлення, конфігурації та закриття каналів |
| `0x0002` | **Connectionless Reception** | Приймання широкомовних пакетів без встановлення з'єднання |
| `0x0003` | **AMP Manager Protocol** | Керування контролерами альтернативних MAC/PHY (Wi-Fi / UWB) |
| `0x0004` | **Attribute Protocol (ATT)** | Канал передавання атрибутів BLE GATT |
| `0x0005` | **LE L2CAP Signaling** | Сигнальний канал для пристроїв Bluetooth Low Energy |
| `0x0006` | **Security Manager Protocol (SMP)** | Протокол безпеки та спарювання BLE |
| `0x0007` | **LE APF** | Зарезервовано для кадрування безпеки BLE |
| `0x0008`–`0x003F` | **Reserved** | Зарезервовано Bluetooth SIG для майбутніх стандартних служб |
| `0x0040`–`0xFFFF` | **Dynamically Allocated** | Динамічні канали застосунків: SDP (`PSM=0x0001`), RFCOMM (`PSM=0x0003`), BNEP (`PSM=0x000F`), AVDTP (`PSM=0x0019`) |

---

### Сигнальний канал L2CAP Signaling (`CID = 0x0001`)

Усі процедури узгодження динамічних каналів виконуються шляхом обміну транзакційними командами через фіксований сигнальний канал `CID = 0x0001`. Сигнальний пакет складається з заголовка команди та її параметрів:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Code      |   Identifier  |            Length             |
|   (8 бітів)   |   (8 бітів)   |          (16 бітів)           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|                  Дані команди (Length байтів)                 |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

1. **`Code`** (8 бітів): тип операції.
   - `0x01` — `L2CAP_COMMAND_REJECT`: відхилення команди через невідомий код або переповнення довжини.
   - `0x02` / `0x03` — `L2CAP_CONNECTION_REQ` / `L2CAP_CONNECTION_RSP`: запит та відповідь на відкриття каналу для заданого коду служби PSM (англ. *Protocol/Service Multiplexer*).
   - `0x04` / `0x05` — `L2CAP_CONFIGURATION_REQ` / `L2CAP_CONFIGURATION_RSP`: двостороннє узгодження параметрів каналу (розмір MTU, Flush Timeout, специфікація якості обслуговування QoS).
   - `0x06` / `0x07` — `L2CAP_DISCONNECTION_REQ` / `L2CAP_DISCONNECTION_RSP`: штатне закриття логічного каналу.
   - `0x08` / `0x09` — `L2CAP_ECHO_REQ` / `L2CAP_ECHO_RSP`: діагностична перевірка зв'язку (L2CAP Ping).
   - `0x0A` / `0x0B` — `L2CAP_INFORMATION_REQ` / `L2CAP_INFORMATION_RSP`: запит списку підтримуваних розширених функцій (Extended Features Mask) та маски фіксованих каналів.
2. **`Identifier`** (8 бітів): числовий ідентифікатор транзакції. Відповідь (`Response`) зобов'язана містити той самий `Identifier`, що й відповідний запит (`Request`), що дозволяє хосту зіставляти паралельні асинхронні транзакції.
3. **`Length`** (16 бітів): довжина тіла параметрів конкретної сигнальної команди.

---

### Покрокове встановлення динамічного каналу зв'язку

Перед тим як прикладні протоколи (наприклад, [RFCOMM](topic:com-transport/bluetooth-classic-stack)) зможуть надсилати корисні SDU, стек L2CAP виконує обов'язковий протокольний діалог через сигнальний канал `CID = 0x0001`:

```
       КЛІЄНТ (Ініціатор)                                СЕРВЕР (Відповідач)
               │                                                  │
               │── L2CAP_CONNECTION_REQ (PSM=0x0003, SCID=0x0040) ─▶│
               │◀─ L2CAP_CONNECTION_RSP (DCID=0x0045, Status=OK) ──│
               │                                                  │
               │── L2CAP_CONFIGURATION_REQ (DCID=0x0045, MTU=1024) ─▶│
               │◀─ L2CAP_CONFIGURATION_RSP (SCID=0x0040, Result=OK) ─│
               │                                                  │
               │◀─ L2CAP_CONFIGURATION_REQ (DCID=0x0040, MTU=1024) ─│
               │── L2CAP_CONFIGURATION_RSP (SCID=0x0045, Result=OK) ─▶│
               │                                                  │
               │ ══════════ КАНАЛ ВІДКРИТО (СТАН OPEN) ══════════ │
               │── L2CAP Data PDU (CID 0x0045, SDU payload) ─────▶│
```

1. **Фаза підключення (Connection Phase)**:
   - Клієнт надсилає команду `L2CAP_CONNECTION_REQ`, вказуючи цільовий код протоколу `PSM` (`0x0001` для SDP, `0x0003` для RFCOMM, `0x000F` для BNEP) та виділений локальний дескриптор `SCID` (Source CID, наприклад `0x0040`).
   - Сервер перевіряє наявність зареєстрованого обробника для заданого PSM. Якщо службу знайдено, сервер виділяє власний дескриптор `DCID` (Destination CID, наприклад `0x0045`) і повертає `L2CAP_CONNECTION_RSP` із кодом результату `0x0000` (Connection Successful).
2. **Фаза двосторонньої конфігурації (Configuration Phase)**:
   - Обидві сторони незалежно одна від одної надсилають запит `L2CAP_CONFIGURATION_REQ`.
   - У параметрах конфігурації передається бажаний розмір вхідного буфера `MTU` (наприклад, 1024 байти), значення `Flush Timeout` (`0xFFFF` — без автоматичного скидання), а також параметри якості обслуговування `QoS Flow Specification` (тип трафіку, гарантована пропускна здатність, допустима затримка).
   - Кожна сторона відповідає пакетом `L2CAP_CONFIGURATION_RSP` із кодом `0x0000` (Success).
   - Лише після успішного підтвердження конфігурації в обох напрямках логічний канал переходить у робочий стан `OPEN`.

---

### Специфікації MTU та параметри QoS для стандартних профілів

Розмір узгодженого MTU та параметри політики обслуговування (QoS) визначають поведінку черги передавача та характеристики затримки:

| Профіль або протокол | Мінімальне обов'язкове MTU | Рекомендоване типове MTU | Тип QoS та параметри потоку |
| :--- | :--- | :--- | :--- |
| **SDP (Service Discovery)** | 48 байтів | 672 байти | Best Effort (без гарантій смуги, максимальна надійність) |
| **RFCOMM (Serial Port)** | 48 байтів | 1024–2048 байтів | Best Effort / Token Bucket (підтримка рівномірного потоку байтів) |
| **AVDTP (Audio Streaming)** | 672 байти | 1024–4096 байтів | Guaranteed QoS: фіксована швидкість токенів, Flush Timeout 10–50 мс |
| **BNEP (Ethernet Encapsulation)** | 1691 байт | 1691 байт | Best Effort (1500 байтів IP + 14 байтів Ethernet + заголовок BNEP) |

Алгоритм маркерного кошика (Token Bucket) у планувальнику L2CAP накопичує токени із заданою швидкістю `Token Rate`. Передавання фрагмента дозволяється лише за наявності достатньої кількості токенів у кошику, що запобігає перевантаженню радіоефіру монопольним трафіком однієї сесії.

---

### Взаємодія з механізмом Flush Timeout та скиданням пакетів

У реальному часі передавання мультимедійних даних (профіль A2DP) затримка важливіша за абсолютну надійність: аудіокадр, який запізнився на 200 мс через завади в ефірі, вже не має сенсу відтворювати, оскільки буфер декодера спустошиться і виникне клацання звуку.

Для керування цим процесом протокол L2CAP узгоджує параметр **Flush Timeout**:
1. **Необмежений тайм-аут (`Flush Timeout = 0xFFFF`)**: контролер зобов'язаний повторювати передавання пакету нескінченно, доки не отримає підтвердження або доки не розірветься з'єднання за `Link Supervision Timeout`. Використовується для надійних каналів керування (SDP, RFCOMM). Пакети HCI позначаються прапором `PB = 0b00` (Non-automatically-flushable).
2. **Обмежений тайм-аут (`Flush Timeout < 0xFFFF`)**: контролер запускає таймер для кожного пакету Baseband. Якщо таймер спливає до отримання ACK, контролер автоматично скидає пакет із черги та починає передавання наступного кадру. Пакети HCI маркуються прапором `PB = 0b10` (Automatically-flushable). Якщо рушій SAR на стороні приймача отримує новий початковий фрагмент `PB = 0b10` до того, як попередній SDU був повністю зібраний, це служить апаратним сигналом про те, що залишок попереднього кадру був скинутий передавачем, і незавершений буфер негайно анулюється.

---

### Режими роботи каналу L2CAP

Специфікація Bluetooth визначає п'ять режимів функціонування логічного каналу L2CAP:

1. **Базовий режим (Basic Information Frame, Basic Mode)**:
   Кадри не містять внутрішніх номерів послідовності та контрольних сум. Надійність доставки повністю делегується нижчележачому апаратному механізму підтверджень Baseband ARQ. Використовується за замовчуванням для служб SDP та RFCOMM.
2. **Режим контролю потоку (Flow Control Mode)**:
   Кадри нумеруються, що дозволяє приймачу обмежувати швидкість надсилання даних передавачем за допомогою ковзного вікна, проте втрачені кадри не надсилаються повторно.
3. **Режим повторного передавання (Retransmission Mode)**:
   Забезпечує гарантовану доставку та збереження порядку шляхом відстеження тайм-аутів і повторного надсилання непідтверджених кадрів L2CAP, якщо вони були скинуті контролером.
4. **Розширений режим повторного передавання (Enhanced Retransmission Mode, ERTM)**:
   Сучасний повноцінний протокол із ковзним вікном, підтримкою кадрів інформації (I-frames), супервізорних кадрів (S-frames: `RR` Receiver Ready, `REJ` Reject, `RNR` Receiver Not Ready, `SREJ` Selective Reject) та обов'язковою 16-бітною контрольною сумою FCS (англ. *Frame Check Sequence*). Дозволяє вибірково перевідправляти лише пошкоджені фрагменти великого SDU.
5. **Потоковий режим (Streaming Mode, SM)**:
   Орієнтований на ізохронне аудіо та відео. Кадри отримують порядкові номери для виявлення пропусків, але підтвердження та повторне передавання повністю вимкнені: якщо пакет спізнився до моменту відтворення, він негайно відкидається.

---

### Детальна структура розширеного режиму ERTM та розрахунок FCS

У режимі ERTM кожен кадр L2CAP доповнюється двобайтовим полем керування (Control Field) та завершується двобайтовою контрольною сумою `FCS` (CRC-16-CCITT):

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Length (16 бітів)       |     Channel ID (16 бітів)     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Enhanced Control Field    |   SDU Length (Лише для SAR)   |
|           (16 бітів)          |           (16 бітів)          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|                 Корисні дані інформаційного кадру             |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       FCS (CRC-16, 16 бітів)  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

1. **Інформаційні кадри (I-frames)**:
   - Біт 0 поля Control встановлено в `0`.
   - Поле `TxSeq` (6 бітів): порядковий номер переданого кадру (від 0 до 63).
   - Поле `ReqSeq` (6 бітів): номер наступного очікуваного кадру від протилежної сторони (вбудоване підтвердження зворотного каналу / Piggybacked ACK).
   - Біт `SAR` (2 біти): позначає стан сегментації SDU на рівні ERTM (`0b00` — нефрагментований SDU, `0b01` — початковий фрагмент, `0b10` — завершальний фрагмент, `0b11` — проміжний фрагмент).
2. **Супервізорні кадри (S-frames)**:
   - Біт 0 поля Control встановлено в `1`.
   - Не містять поля даних і служать виключно для керування станом ковзного вікна та підтвердження прийому.
   - Поле `S-Type` (2 біти):
     - `0b00` (`RR` — Receiver Ready): підтверджує прийом усіх кадрів до номера `ReqSeq - 1` включно.
     - `0b01` (`REJ` — Reject): запит на повторне передавання всіх кадрів, починаючи з номера `ReqSeq` (груповий повтор Go-Back-N).
     - `0b10` (`RNR` — Receiver Not Ready): повідомляє про тимчасове переповнення буферів приймача та просить передавача призупинити надсилання I-кадрів.
     - `0b11` (`SREJ` — Selective Reject): запит на вибіркове повторне надсилання рівно одного конкретного кадру з номером `ReqSeq` без повтору всієї послідовності.
3. **Контрольна сума FCS (Frame Check Sequence)**:
   Обчислюється за стандартним поліномом [CRC-CCITT](topic:com-modulation/fec-codes) `G(x) = x^16 + x^12 + x^5 + 1` (шістнадцятковий вираз `0x1021`, початковий стан `0x0000`). Поле FCS охоплює всі байти кадру L2CAP, починаючи від поля `Length` і завершуючи останнім байтом корисних даних. Приймач обчислює контрольну суму над усім блоком включно з FCS: залишок ділення має дорівнювати нулю.

---

### Реалізація рушія L2CAP SAR

Нижче наведено робочу реалізацію рушія L2CAP SAR мовами C та C++, розраховану на роботу з асинхронним потоком транспортного інтерфейсу [HCI UART H4](topic:com-transport/bluetooth-classic-stack/api-hci-uart.md).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define L2CAP_MAX_MTU           1024
#define L2CAP_MAX_CONNECTIONS   4

#define L2CAP_CID_SDP           0x0001
#define L2CAP_CID_SIGNALING     0x0002
#define L2CAP_CID_DYNAMIC_START 0x0040

typedef enum {
    L2CAP_SAR_IDLE,
    L2CAP_SAR_ACCUMULATING,
    L2CAP_SAR_COMPLETE,
    L2CAP_SAR_ERROR_OVERFLOW,
    L2CAP_SAR_ERROR_CORRUPT
} l2cap_sar_state_t;

typedef struct {
    uint16_t length;
    uint16_t cid;
} __attribute__((packed)) l2cap_hdr_t;

typedef struct {
    uint16_t handle;
    l2cap_sar_state_t state;
    uint16_t expected_len;
    uint16_t received_len;
    uint16_t cid;
    uint8_t buffer[L2CAP_MAX_MTU];
} l2cap_channel_ctx_t;

typedef struct {
    l2cap_channel_ctx_t channels[L2CAP_MAX_CONNECTIONS];
} l2cap_engine_t;

void l2cap_engine_init(l2cap_engine_t *engine) {
    memset(engine, 0, sizeof(l2cap_engine_t));
}

static l2cap_channel_ctx_t* l2cap_find_or_alloc_channel(l2cap_engine_t *engine, uint16_t handle) {
    for (int i = 0; i < L2CAP_MAX_CONNECTIONS; i++) {
        if (engine->channels[i].handle == handle && engine->channels[i].state != L2CAP_SAR_IDLE) {
            return &engine->channels[i];
        }
    }
    for (int i = 0; i < L2CAP_MAX_CONNECTIONS; i++) {
        if (engine->channels[i].state == L2CAP_SAR_IDLE) {
            engine->channels[i].handle = handle;
            return &engine->channels[i];
        }
    }
    return NULL;
}

static void l2cap_dispatch_packet(uint16_t handle, uint16_t cid, const uint8_t *payload, uint16_t len) {
    if (cid == L2CAP_CID_SDP) {
        /* Передача у підсистему Service Discovery Protocol */
    } else if (cid == L2CAP_CID_SIGNALING) {
        /* Передача у внутрішній диспетчер команд L2CAP Signaling */
    } else if (cid >= L2CAP_CID_DYNAMIC_START) {
        /* Передача у підсистему емуляції послідовного порту RFCOMM */
    }
}

bool l2cap_process_acl_fragment(l2cap_engine_t *engine,
                                uint16_t handle,
                                uint8_t pb_flag,
                                const uint8_t *data,
                                uint16_t data_len) {
    if (!engine || !data || data_len == 0) {
        return false;
    }

    l2cap_channel_ctx_t *ctx = l2cap_find_or_alloc_channel(engine, handle);
    if (!ctx) {
        return false;
    }

    if (pb_flag == 0x02 || pb_flag == 0x00) {
        /* Перший фрагмент L2CAP кадру (Start Fragment) */
        if (data_len < sizeof(l2cap_hdr_t)) {
            ctx->state = L2CAP_SAR_ERROR_CORRUPT;
            return false;
        }

        const l2cap_hdr_t *hdr = (const l2cap_hdr_t*)data;
        ctx->expected_len = hdr->length;
        ctx->cid = hdr->cid;
        ctx->received_len = 0;

        if (ctx->expected_len > L2CAP_MAX_MTU) {
            ctx->state = L2CAP_SAR_ERROR_OVERFLOW;
            return false;
        }

        uint16_t payload_len = data_len - sizeof(l2cap_hdr_t);
        if (payload_len > ctx->expected_len) {
            ctx->state = L2CAP_SAR_ERROR_CORRUPT;
            return false;
        }

        if (payload_len > 0) {
            memcpy(ctx->buffer, data + sizeof(l2cap_hdr_t), payload_len);
            ctx->received_len = payload_len;
        }

        if (ctx->received_len == ctx->expected_len) {
            ctx->state = L2CAP_SAR_COMPLETE;
            l2cap_dispatch_packet(handle, ctx->cid, ctx->buffer, ctx->received_len);
            ctx->state = L2CAP_SAR_IDLE;
            return true;
        }

        ctx->state = L2CAP_SAR_ACCUMULATING;
        return true;

    } else if (pb_flag == 0x01) {
        /* Продовження кадру L2CAP (Continuation Fragment) */
        if (ctx->state != L2CAP_SAR_ACCUMULATING) {
            ctx->state = L2CAP_SAR_ERROR_CORRUPT;
            return false;
        }

        if (ctx->received_len + data_len > ctx->expected_len) {
            ctx->state = L2CAP_SAR_ERROR_OVERFLOW;
            return false;
        }

        memcpy(ctx->buffer + ctx->received_len, data, data_len);
        ctx->received_len += data_len;

        if (ctx->received_len == ctx->expected_len) {
            ctx->state = L2CAP_SAR_COMPLETE;
            l2cap_dispatch_packet(handle, ctx->cid, ctx->buffer, ctx->received_len);
            ctx->state = L2CAP_SAR_IDLE;
            return true;
        }

        return true;
    }

    return false;
}
```
```cpp
#include <cstdint>
#include <vector>
#include <span>
#include <unordered_map>
#include <optional>
#include <functional>

class L2capSarEngine {
public:
    static constexpr uint16_t kMaxMtu = 1024;
    static constexpr uint16_t kCidSdp = 0x0001;
    static constexpr uint16_t kCidSignaling = 0x0002;
    static constexpr uint16_t kCidDynamicStart = 0x0040;

    enum class SarState {
        Idle,
        Accumulating,
        Complete,
        ErrorOverflow,
        ErrorCorrupt
    };

    enum class PacketBoundary : uint8_t {
        StartNonFlushable = 0x00,
        Continuation      = 0x01,
        StartAutoFlushable= 0x02
    };

    struct ChannelContext {
        uint16_t handle{0};
        SarState state{SarState::Idle};
        uint16_t expected_len{0};
        uint16_t cid{0};
        std::vector<uint8_t> buffer{};

        void reset() {
            state = SarState::Idle;
            expected_len = 0;
            cid = 0;
            buffer.clear();
        }
    };

    using PacketHandler = std::function<void(uint16_t handle, uint16_t cid, std::span<const uint8_t> payload)>;

    explicit L2capSarEngine(PacketHandler handler = nullptr)
        : packet_handler_(std::move(handler)) {}

    void set_packet_handler(PacketHandler handler) {
        packet_handler_ = std::move(handler);
    }

    bool process_acl_fragment(uint16_t handle, PacketBoundary pb, std::span<const uint8_t> data) {
        if (data.empty()) {
            return false;
        }

        auto& ctx = channels_[handle];
        ctx.handle = handle;

        if (pb == PacketBoundary::StartAutoFlushable || pb == PacketBoundary::StartNonFlushable) {
            if (data.size() < sizeof(uint16_t) * 2) {
                ctx.state = SarState::ErrorCorrupt;
                return false;
            }

            uint16_t length = static_cast<uint16_t>(data[0]) | (static_cast<uint16_t>(data[1]) << 8);
            uint16_t cid = static_cast<uint16_t>(data[2]) | (static_cast<uint16_t>(data[3]) << 8);

            if (length > kMaxMtu) {
                ctx.state = SarState::ErrorOverflow;
                return false;
            }

            ctx.expected_len = length;
            ctx.cid = cid;
            ctx.buffer.clear();
            ctx.buffer.reserve(length);

            auto payload = data.subspan(4);
            if (payload.size() > ctx.expected_len) {
                ctx.state = SarState::ErrorCorrupt;
                return false;
            }

            ctx.buffer.insert(ctx.buffer.end(), payload.begin(), payload.end());

            if (ctx.buffer.size() == ctx.expected_len) {
                ctx.state = SarState::Complete;
                dispatch(ctx);
                ctx.reset();
                return true;
            }

            ctx.state = SarState::Accumulating;
            return true;

        } else if (pb == PacketBoundary::Continuation) {
            if (ctx.state != SarState::Accumulating) {
                ctx.state = SarState::ErrorCorrupt;
                return false;
            }

            if (ctx.buffer.size() + data.size() > ctx.expected_len) {
                ctx.state = SarState::ErrorOverflow;
                return false;
            }

            ctx.buffer.insert(ctx.buffer.end(), data.begin(), data.end());

            if (ctx.buffer.size() == ctx.expected_len) {
                ctx.state = SarState::Complete;
                dispatch(ctx);
                ctx.reset();
                return true;
            }

            return true;
        }

        return false;
    }

private:
    void dispatch(const ChannelContext& ctx) {
        if (packet_handler_) {
            packet_handler_(ctx.handle, ctx.cid, std::span<const uint8_t>(ctx.buffer));
        }
    }

    std::unordered_map<uint16_t, ChannelContext> channels_{};
    PacketHandler packet_handler_{};
};
```
:::

---

### Детальний аналіз алгоритму сегментації вихідного потоку

Коли вищий протокол генерує великий блок даних (наприклад, кадр протоколу [RFCOMM](topic:com-transport/bluetooth-classic-stack) розміром 2048 байтів), процес сегментації виконується за таким суворим покроковим алгоритмом:

1. **Визначення ліміту фрагмента контролера**:
   Хост звертається до раніше збереженого значення `HC_ACL_Data_Packet_Length`, отриманого під час опитування `HCI_Read_Buffer_Size`. Нехай це значення дорівнює 339 байтам (максимальний розмір корисного навантаження пакету DH5).
2. **Формування першого пакета HCI ACL (`PB = 0b10`)**:
   - Перший пакет обов'язково несе 4 байти заголовка L2CAP (`Length = 2048`, `CID = 0x0040`).
   - На дані протоколу вищого рівня у першому пакеті залишається рівно `339 - 4 = 335` байтів.
   - Загальний розмір першого пакету HCI ACL становить 339 байтів.
   - Пакет передається у чергу передавача HCI з дескриптором цільового з'єднання `Connection Handle` та зменшенням лічильника буферних кредитів на 1.
3. **Формування послідовності продовжувальних пакетів (`PB = 0b01`)**:
   - Наступні фрагменти не містять жодних заголовків L2CAP і цілком заповнюються корисними байтами вихідного повідомлення.
   - Другий фрагмент містить наступні 339 байтів (байти з 335 по 673).
   - Третій, четвертий, п'ятий та шостий фрагменти також передають по 339 байтів.
   - Сьомий фінальний фрагмент містить залишок: `2048 - 335 - (5 × 339) = 18` байтів.
4. **Завершення передачі**:
   - Усі 7 сформованих пакетів передаються через інтерфейс HCI у порядку їх формування.
   - Автомат стану приймача на віддаленому пристрої об'єднує 7 отриманих порцій даних у єдиний безперервний масив довжиною 2048 байтів і лише після отримання фінального 18-байтового шматка викликає обробник сесії RFCOMM.

---

### Багатопотоковість та синхронізація у вбудованих операційних системах

У реальних вбудованих середовищах (FreeRTOS, Zephyr RTOS, NuttX) обробник переривання UART або потік DMA працює асинхронно відносно прикладних потоків задач. Це вимагає дотримання суворих правил конкурентності:

1. **Ізоляція обробника переривань (ISR)**: безпосередньо в ISR UART виконується лише швидке копіювання сирих байтів у кільцевий буфер або чергу повідомлень (Message Queue). Важка логіка SAR та виклики зворотного зв'язку (Callbacks) виносяться в контекст окремого системного потоку стека Bluetooth (`bt_rx_task`).
2. **Захист контекстів каналів м'ютексами**: оскільки прикладний потік може ініціювати відправлення даних або закриття каналу `L2CAP_DISCONNECTION_REQ` одночасно з надходженням вхідних фрагментів від контролера, доступ до структур `l2cap_channel_ctx_t` захищається бінарними семафорами або м'ютексами з низьким часом блокування.

---

### Крайові випадки та обробка позаштатних ситуацій у рушії SAR

1. **Втрата проміжних фрагментів в ефірі (Incomplete Frame Recovery)**:
   Якщо через сильні радіозавади або тайм-аут контролер був змушений скинути фрагмент із прапором `PB = 0b01`, а згодом надійшов новий перший фрагмент `PB = 0b10`, рушій негайно очищує накопичений пошкоджений буфер попереднього пакету та починає збирання нового кадру. Це запобігає «залипанню» автомата стану в режимі накопичення та витоку оперативної пам'яті.
2. **Переповнення MTU (MTU Violation)**:
   Якщо віддалена сторона передала сумарну кількість байтів, більшу за оголошений розмір `expected_len`, або якщо `expected_len` перевищує погоджений під час конфігурації `MTU`, пакет бракується без виклику обробників вищих рівнів.
3. **Чергування фрагментів різних з'єднань (Interleaved Multi-Connection Traffic)**:
   При роботі у топології Scatternet або за наявності кількох активних ведених пристроїв пакети ACL від різних вузлів надходять упереміж. Поле `Connection Handle` у заголовку ACL однозначно адресує окремий контекст збирання, забезпечуючи повну ізоляцію паралельних потоків даних.
4. **Тайм-аут збирання кадру (SAR Assembly Timeout)**:
   Якщо перший фрагмент отримано, але наступні фрагменти не надходять протягом захисного інтервалу часу (зазвичай від 5 до 30 секунд залежно від профілю), рушій за таймером переводить контекст каналу у стан `IDLE`, запобігаючи довічному утриманню виділеної динамічної пам'яті.
5. **Організація пам'яті без динамічної алокації (Zero-Copy Memory Pools)**:
   У високопродуктивних мікроконтролерних системах (наприклад, на базі FreeRTOS або Zephyr) використання динамічного виділення пам'яті `malloc` усередині обробника переривань UART заборонено через ризик фрагментації купи та недетермінований час виконання. Замість цього пул пам'яті організується у вигляді масиву статично виділених блоків фіксованого розміру `net_buf` із лічильниками посилань. Збирання фрагментів виконується шляхом зв'язування таких блоків у двозв'язний список без копіювання байтів у пам'яті, що мінімізує навантаження на процесорне ядро.
