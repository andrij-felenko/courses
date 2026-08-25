# ⚙️ Низькозатримковий канал телеметрії та керування через WebRTC DataChannel

Протокол RTCDataChannel у стеку WebRTC надає можливість двонаправленої передачі довільних двійкових та текстових повідомлень безпосередньо між двома кінцевими вузлами через інкапсуляцію протоколу SCTP (Stream Control Transmission Protocol, RFC 4960 та RFC 8831) усередині захищеного тунелю DTLS поверх UDP.

На відміну від стандартних сокетів TCP (де втрата одного байта блокує просування всього потоку через Head-of-Line Blocking) та класичних WebSockets (які працюють виключно за клієнт-серверною топологією через TCP), DataChannel дозволяє налаштовувати гарантії доставки індивідуально для кожного логічного каналу: від абсолютно надійного впорядкованого режиму (Reliable Ordered) до надшвидкого ненадійного без збереження черговості (Unreliable Unordered), що критично важливо для задач дистанційного пілотування робототехніки, безпілотних літальних апаратів (FPV) та хмарного геймінгу.

## Архітектура протоколу: SCTP поверх DTLS

У класичних телекомунікаційних мережах протокол SCTP функціонує безпосередньо над мережевим рівнем IP (номер протоколу IP 132). Проте переважна більшість домашніх маршрутизаторів, базових станцій стільникового зв'язку та корпоративних фаєрволів NAT не підтримують трансляцію стану для протоколу 132 і просто відкидають такі пакети як невідомі. Щоб зробити протокол універсально доступним у глобальному інтернеті, у WebRTC протокол SCTP адаптовано для роботи виключно в просторі користувача (User-Space SCTP). Усі керівні та користувацькі повідомлення інкапсулюються у корисний вантаж DTLS-датаграм і передаються через єдиний узгоджений UDP-порт BUNDLE.

```text
+-----------------------------------------------------------------+
|              Прикладні дані (Телеметрія / Команди)              |
+-----------------------------------------------------------------+
|  SCTP (Потоковий контроль, чанки DATA, SACK, прапори U/B/E)     |
+-----------------------------------------------------------------+
|  DTLS (Шифрування AEAD AES-GCM, взаємна автентифікація)        |
+-----------------------------------------------------------------+
|  UDP (Датаграми через узгоджений ICE-канал зв'язку)             |
+-----------------------------------------------------------------+
```

### Формат кадру SCTP та структура чанків (Chunks)

Кожен пакет SCTP складається з обов'язкового 12-байтового загального заголовка (Common Header) та одного або кількох блоків даних, які в термінології стандарту називаються **чанками** (Chunks).

Загальний заголовок містить:
- `Source Port` (16 біт) та `Destination Port` (16 біт): логічні порти асоціації SCTP (за замовчуванням `5000` у WebRTC).
- `Verification Tag` (32 біти): випадкове число, узгоджене під час ініціалізації сесії, яке захищає від підробки пакетів та застарілих датаграм від попередніх сесій.
- `Checksum` (32 біти): контрольна сума за алгоритмом CRC-32c (поліном Кастаньйолі), що обчислюється від усього пакета.

Після загального заголовка розміщуються чанки. Найважливішим для передачі телеметрії є чанк користувацьких даних `DATA` (тип `0x00`), який має наступну структуру полів:

1. `Type` (8 біт): код типу (`0x00` для `DATA`).
2. `Flags` (8 біт): бітові прапорці керування доставкою:
   - Біт `U` (Unordered): якщо встановлено в `1`, пакет вважається невпорядкованим і передається додатку негайно після прийому без очікування попередніх втрачених номерів.
   - Біт `B` (Beginning) та `E` (Ending): вказують на початок та кінець фрагментованого повідомлення, якщо розмір корисного вантажу перевищував MTU.
3. `Length` (16 біт): повна довжина чанка в байтах включно із заголовком.
4. `TSN` (Transmission Sequence Number, 32 біти): наскрізний монотонно зростаючий лічильник послідовності передачі на рівні всього з'єднання. Використовується транспортним рівнем SCTP для підтвердження отримання байтів (через чанки `SACK`).
5. `Stream Identifier` (16 біт): числовий ідентифікатор логічного потоку (Stream ID), до якого прив'язано конкретний об'єкт `RTCDataChannel`.
6. `Stream Sequence Number` (16 біт): порядковий номер повідомлення *всередині даного конкретного потоку*. Якщо біт `U=1`, це поле ігнорується приймачем.
7. `Payload Protocol Identifier` (PPID, 32 біти): ідентифікатор типу прикладних даних, стандартизований IETF для WebRTC.

### Реєстр ідентифікаторів PPID у WebRTC

Протокол SCTP використовує поле PPID для того, щоб браузерний рушій знав, як саме інтерпретувати байти корисного вантажу без необхідності розбирати прикладні заголовки:

| Значення PPID | Стандарт | Опис типу даних | Поведінка рушія WebRTC |
| :--- | :--- | :--- | :--- |
| `50` | RFC 8831 | WebRTC DCEP | Керуючі пакети встановлення та підтвердження каналу (`DATA_CHANNEL_OPEN` / `ACK`). |
| `51` | RFC 8831 | WebRTC String (UTF-8) | Текстове повідомлення JavaScript (генерує рядок у `event.data`). |
| `52` | RFC 8831 | WebRTC Binary Partial | Застарілий бінарний фрагмент (зараз не використовується). |
| `53` | RFC 8831 | WebRTC Binary | Бінарні дані (передаються як `ArrayBuffer` або `Blob` у JavaScript). |
| `54` | RFC 8831 | WebRTC String Empty | Спеціальний маркер порожнього текстового рядка довжиною 0 байтів. |
| `55` | RFC 8831 | WebRTC Binary Empty | Спеціальний маркер порожнього бінарного буфера довжиною 0 байтів. |

### Механізм часткової надійності (PR-SCTP, RFC 3758)

Ключовою перевагою SCTP над класичним TCP є підтримка часткової надійності (Partial Reliability Extension, PR-SCTP). У стандартному TCP протокол зобов'язаний повторювати спроби доставки втраченого сегмента нескінченно, доки не буде отримано підтвердження або доки не спливе глобальний тайм-аут з'єднання (зазвичай кілька хвилин).

У WebRTC DataChannel розробник може тонко налаштувати політику скидання застарілих даних:

1. **Режим обмеження за часом життя (`maxPacketLifeTime`)**:
   Відправник фіксує мітку часу створення кадру `t_create`. Якщо пакет було втрачено в радіоканалі, і таймер повторної передачі перевищив значення `maxPacketLifeTime` (наприклад, 50 мс для телеметрії), відправник припиняє повторні спроби відправки цього чанка. Замість цього він генерує спеціальний керівний чанк **`FORWARD-TSN`**, який повідомляє приймачу: «Пропусти очікування послідовного номера `TSN_k`, цей пакет скасовано, пересунь вікно прийому вперед». Приймач негайно зміщує межу підтверджених даних, не блокуючи роботу наступних повідомлень.
2. **Режим обмеження за кількістю спроб (`maxRetransmits`)**:
   Для кожного чанка ведеться окремий лічильник відправок `retransmit_count`. Якщо пакет втрачено, відправник робить повторні спроби лише до досягнення ліміту `maxRetransmits` (для каналу керування джойстиком — `0`, тобто жодної повторної спроби). У разі невдачі відправник надсилає `FORWARD-TSN` і миттєво переходить до свіжого кадру.

## Багатопотокова архітектура бортового C++ агента

Для забезпечення суб-10-мілісекундної реакції при керуванні роботом програмний комплекс на бортовому комп'ютері поділяється на кілька ізольованих потоків виконання (Threads) з використанням неблокуючих кільцевих буферів (Lock-Free Ring Buffers):

1. **Потік апаратного захвату (Hardware I/O Thread)**: Працює з найвищим пріоритетом реального часу (`SCHED_FIFO` в Linux), опитує шини SPI/UART/CAN польотного контролера або давачів IMU з частотою 500–1000 Гц. Він формує структури `FlightTelemetryFrame` і записує їх у кільцевий буфер без динамічного виділення пам'яті (Zero Heap Allocation).
2. **Мережевий потік WebRTC (Network / Worker Thread)**: Вичитує найсвіжіший кадр із кільцевого буфера, виконує перевірку завантаженості каналу (`buffered_amount`), інкапсулює байти у чанк SCTP `DATA` з PPID 53 та передає криптографічному рушію DTLS (OpenSSL або BoringSSL) для шифрування AES-GCM.
3. **Сокетний рівень ядра**: Передає зашифровані UDP-датаграми в бездротовий мережевий інтерфейс (Wi-Fi, 4G/5G модем) за допомогою системних викликів `sendto()` або сучасного інтерфейсу `io_uring` для мінімізації накладних витрат перемикання контексту ядра.

## Конфігурація надійності під різні типи трафіку

Для керування роботом чи FPV-дроном створюються два паралельні незалежні DataChannel із різними профілями надійності:

| Назва каналу | Режим надійності | `ordered` | Параметр надійності | Призначення та поведінка |
| :--- | :--- | :--- | :--- | :--- |
| `controls` | **Unreliable Unordered** | `false` | `maxRetransmits: 0` | Керуючі сигнали джойстика (частота 100 Гц). Втрачений пакет ігнорується, оскільки наступний кадр (через 10 мс) несе актуальніші координати. |
| `telemetry` | **Unreliable Timed** | `false` | `maxPacketLifeTime: 50` | Високочастотна телеметрія польотного контролера (50 Гц: крен, тангаж, кутова швидкість). Пакет живе максимум 50 мс, запобігаючи затримкам. |
| `mission` | **Reliable Ordered** | `true` | За замовчуванням (необмежено) | Завантаження польотного завдання, зміна конфігураційних параметрів PID, перемикання режимів польоту (FailSafe/RTL). |

## Реалізація на бортовому комп'ютері (C++)

Бортовий агент робота (на базі Raspberry Pi або NVIDIA Jetson під керуванням Linux) виконує захват телеметрії з польотного контролера по шині UART/CAN, серіалізує її у двійковий формат та транслює через WebRTC DataChannel.

Нижче наведено ідіоматичну реалізацію C++ агента телеметрії, що використовує сучасний стандарт C++20, RAII-обгортки сокетів, безпечну роботу з пам'яттю через `std::span` та неблокуюче відправлення двійкових кадрів:

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <chrono>
#include <cstring>
#include <cstdint>
#include <expected>
#include <system_error>

// Двійкова структура кадру польотної телеметрії (фіксований розмір 32 байти)
#pragma pack(push, 1)
struct FlightTelemetryFrame {
    uint32_t timestamp_ms; // Час від старту контролера
    float roll_deg;        // Крен (-180.0 .. +180.0)
    float pitch_deg;       // Тангаж (-90.0 .. +90.0)
    float yaw_deg;         // Рискання (0.0 .. 360.0)
    float altitude_m;      // Висота барометрична/GPS
    float battery_voltage; // Напруга акумулятора (В)
    uint8_t arm_state;     // 0 = Disarmed, 1 = Armed
    uint8_t flight_mode;   // 0 = Manual, 1 = AltHold, 2 = Auto, 3 = RTL
    uint16_t crc16;        // Контрольна сума CRC-16-CCITT
};
#pragma pack(pop)

// Інтерфейс сокета DataChannel (RAII-абстракція над SCTP/DTLS тунелем)
class DataChannelSession {
public:
    virtual ~DataChannelSession() = default;
    virtual bool is_open() const noexcept = 0;
    virtual size_t buffered_amount() const noexcept = 0;
    virtual std::expected<void, std::error_code> send(std::span<const std::byte> data) = 0;
};

// Контролер відправки високочастотної телеметрії
class TelemetryBroadcaster {
public:
    explicit TelemetryBroadcaster(std::shared_ptr<DataChannelSession> channel)
        : channel_(std::move(channel)) {}

    // Обчислення простої контрольної суми CRC-16 для захисту цілісності
    static uint16_t compute_crc16(std::span<const std::byte> bytes) noexcept {
        uint16_t crc = 0xFFFF;
        for (std::byte b : bytes) {
            crc ^= static_cast<uint8_t>(b);
            for (int i = 0; i < 8; ++i) {
                if (crc & 0x0001) {
                    crc = (crc >> 1) ^ 0x8408; // Поліном CCITT reverse
                } else {
                    crc >>= 1;
                }
            }
        }
        return crc;
    }

    // Відправка одного телеметричного кадру з контролем черги сокета (Backpressure)
    std::expected<void, std::string> broadcast_frame(float roll, float pitch, float yaw,
                                                    float alt, float vbat, uint8_t mode) {
        if (!channel_ || !channel_->is_open()) {
            return std::unexpected("Канал зв'язку DataChannel не відкритий");
        }

        // Захист від переповнення системного буфера SCTP (Backpressure)
        // Якщо в буфері відправки вже накопичилося понад 64 КіБ, скидаємо застарілий кадр
        if (channel_->buffered_amount() > 65536) {
            return std::unexpected("Черга відправки переповнена: кадр телеметрії пропущено");
        }

        auto now = std::chrono::steady_clock::now();
        uint32_t now_ms = static_cast<uint32_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count()
        );

        FlightTelemetryFrame frame{
            .timestamp_ms = now_ms,
            .roll_deg = roll,
            .pitch_deg = pitch,
            .yaw_deg = yaw,
            .altitude_m = alt,
            .battery_voltage = vbat,
            .arm_state = 1,
            .flight_mode = mode,
            .crc16 = 0
        };

        // Обчислюємо CRC-16 від усіх полів крім самого поля crc16
        auto payload_bytes = std::as_bytes(std::span{&frame, 1});
        auto data_to_hash = payload_bytes.subspan(0, sizeof(FlightTelemetryFrame) - sizeof(uint16_t));
        frame.crc16 = compute_crc16(data_to_hash);

        // Відправляємо бінарний буфер через SCTP без блокування
        auto result = channel_->send(payload_bytes);
        if (!result) {
            return std::unexpected("Помилка сокета при надсиланні кадру");
        }

        return {};
    }

private:
    std::shared_ptr<DataChannelSession> channel_;
};
```
```ts
// TypeScript клієнт станції керування в браузері (GCS)

interface FlightTelemetry {
    timestampMs: number;
    rollDeg: number;
    pitchDeg: number;
    yawDeg: number;
    altitudeM: number;
    batteryVoltage: number;
    armState: number;
    flightMode: number;
}

export class TelemetryReceiver {
    private channel: RTCDataChannel | null = null;
    private onTelemetryCallback: ((data: FlightTelemetry) => void) | null = null;

    constructor(peerConnection: RTCPeerConnection) {
        // Прослуховуємо подію створення каналу віддаленим C++ агентом
        peerConnection.ondatachannel = (event: RTCDataChannelEvent) => {
            if (event.channel.label === "telemetry") {
                this.setupChannel(event.channel);
            }
        };
    }

    private setupChannel(channel: RTCDataChannel): void {
        this.channel = channel;
        this.channel.binaryType = "arraybuffer";

        this.channel.onopen = () => {
            console.log("Канал телеметрії WebRTC DataChannel успішно відкрито");
        };

        this.channel.onmessage = (event: MessageEvent) => {
            if (!(event.data instanceof ArrayBuffer)) return;

            const buffer = event.data;
            if (buffer.byteLength !== 32) {
                console.warn(`Некоректний розмір кадру: очікувалося 32 байти, отримано ${buffer.byteLength}`);
                return;
            }

            const view = new DataView(buffer);

            // Перевірка контрольної суми CRC-16
            const receivedCrc = view.getUint16(30, true);
            const computedCrc = this.computeCrc16(new Uint8Array(buffer, 0, 30));

            if (receivedCrc !== computedCrc) {
                console.error("Помилка перевірки CRC-16: пакет пошкоджено при передачі");
                return;
            }

            const telemetry: FlightTelemetry = {
                timestampMs: view.getUint32(0, true),
                rollDeg: view.getFloat32(4, true),
                pitchDeg: view.getFloat32(8, true),
                yawDeg: view.getFloat32(12, true),
                altitudeM: view.getFloat32(16, true),
                batteryVoltage: view.getFloat32(20, true),
                armState: view.getUint8(24),
                flightMode: view.getUint8(25)
            };

            if (this.onTelemetryCallback) {
                this.onTelemetryCallback(telemetry);
            }
        };
    }

    private computeCrc16(bytes: Uint8Array): number {
        let crc = 0xFFFF;
        for (let i = 0; i < bytes.length; ++i) {
            crc ^= bytes[i];
            for (let j = 0; j < 8; ++j) {
                if (crc & 0x0001) {
                    crc = (crc >> 1) ^ 0x8408;
                } else {
                    crc >>= 1;
                }
            }
        }
        return crc;
    }

    public onTelemetry(callback: (data: FlightTelemetry) => void): void {
        this.onTelemetryCallback = callback;
    }
}
```
:::

## Реалізація каналу керування джойстиком (TypeScript та C++)

Канал керування `controls` вимагає наднизької затримки. Браузер опитує підключений USB-геймпад через Gamepad API з частотою 100 Гц (кожні 10 мс) і надсилає стиснутий 8-байтовий бінарний кадр `[Throttle, Roll, Pitch, Yaw, Switches]`.

:::tabs
```ts
// Модуль опитування геймпада та передачі команд керування
export class FlightControllerInput {
    private controlChannel: RTCDataChannel;
    private timerId: number | null = null;

    constructor(peerConnection: RTCPeerConnection) {
        // Створюємо ненадійний невпорядкований канал без повторів
        this.controlChannel = peerConnection.createDataChannel("controls", {
            ordered: false,
            maxRetransmits: 0
        });
        this.controlChannel.binaryType = "arraybuffer";

        this.controlChannel.onopen = () => {
            this.startControlLoop();
        };

        this.controlChannel.onclose = () => {
            this.stopControlLoop();
        };
    }

    private startControlLoop(): void {
        // Цикл опитування кожні 10 мс (100 Гц)
        this.timerId = window.setInterval(() => {
            this.pollAndSendStickCommands();
        }, 10);
    }

    private stopControlLoop(): void {
        if (this.timerId !== null) {
            clearInterval(this.timerId);
            this.timerId = null;
        }
    }

    private pollAndSendStickCommands(): void {
        if (this.controlChannel.readyState !== "open") return;

        const gamepads = navigator.getGamepads();
        const gp = gamepads[0];
        if (!gp) return;

        // Нормалізація стіків (-1.0 .. +1.0) у 16-бітові цілі числа (1000 .. 2000 мкс ШІМ)
        const throttlePwm = Math.round(1500 + (-gp.axes[1]) * 500); // Лівий стік Y (інвертований)
        const rollPwm     = Math.round(1500 + (gp.axes[2]) * 500);  // Правий стік X
        const pitchPwm    = Math.round(1500 + (-gp.axes[3]) * 500); // Правий стік Y
        const yawPwm      = Math.round(1500 + (gp.axes[0]) * 500);  // Лівий стік X

        const buffer = new ArrayBuffer(10);
        const view = new DataView(buffer);

        view.setUint16(0, throttlePwm, true);
        view.setUint16(2, rollPwm, true);
        view.setUint16(4, pitchPwm, true);
        view.setUint16(6, yawPwm, true);
        view.setUint8(8, gp.buttons[0].pressed ? 1 : 0); // Тумблер Arm
        view.setUint8(9, gp.buttons[1].pressed ? 1 : 0); // Тумблер Mode

        // Відправка без буферизації
        this.controlChannel.send(buffer);
    }
}
```
```cpp
// C++ обробник команд польоту на стороні бортового комп'ютера

#pragma pack(push, 1)
struct ControlCommandPacket {
    uint16_t throttle_pwm; // 1000..2000 мкс
    uint16_t roll_pwm;     // 1000..2000 мкс
    uint16_t pitch_pwm;    // 1000..2000 мкс
    uint16_t yaw_pwm;      // 1000..2000 мкс
    uint8_t arm_switch;    // 0 = Off, 1 = On
    uint8_t mode_switch;   // 0 = PosHold, 1 = Manual
};
#pragma pack(pop)

class FlightCommandParser {
public:
    // Обробка вхідного пакету команд із сокета WebRTC
    void on_data_received(std::span<const std::byte> packet) {
        if (packet.size() != sizeof(ControlCommandPacket)) {
            // Ігноруємо некоректні розміри
            return;
        }

        ControlCommandPacket cmd{};
        std::memcpy(&cmd, packet.data(), sizeof(ControlCommandPacket));

        // Санітизація діапазонів сигналів ШІМ перед відправкою на польотний контролер
        cmd.throttle_pwm = std::clamp<uint16_t>(cmd.throttle_pwm, 1000, 2000);
        cmd.roll_pwm     = std::clamp<uint16_t>(cmd.roll_pwm, 1000, 2000);
        cmd.pitch_pwm    = std::clamp<uint16_t>(cmd.pitch_pwm, 1000, 2000);
        cmd.yaw_pwm      = std::clamp<uint16_t>(cmd.yaw_pwm, 1000, 2000);

        dispatch_to_flight_controller(cmd);
    }

private:
    void dispatch_to_flight_controller(const ControlCommandPacket& cmd) {
        // Передача структури по UART/MAVLink на польотний контролер (STM32/ArduPilot)
        // Обробка виконується в реальному часі без затримок черги
    }
};
```
:::

## Керування зворотним тиском (Backpressure) та фрагментація MTU

При роботі з DataChannel у високонавантажених системах виникають дві критичні пастки, пов'язані з фізикою транспортного рівня:

### 1. Переповнення черги відправника (`bufferedAmount`)
Виклик методу `send()` у WebRTC є асинхронним і не блокує виконання програми. Дані поміщаються у чергу буфера сокета SCTP. Якщо додаток генерує трафік швидше, ніж дозволяє пропускна здатність радіоканалу (наприклад, надсилає кадри телеметрії розміром 10 КіБ зі швидкістю 200 Гц через повільний зв'язок), значення властивості `bufferedAmount` починає неконтрольовано зростати.

Це призводить до накопичення гігантських затримок (десятків секунд) у пам'яті процесу, оскільки застарілі пакети стоять у черзі на відправку.

Правильне вирішення — використання механізму порогових повідомлень **`bufferedAmountLowThreshold`**:
```ts
channel.bufferedAmountLowThreshold = 32768; // 32 КіБ
channel.onbufferedamountlow = () => {
    // Відновлюємо відправку нових даних лише тоді, коли черга розвантажилася
    resumeSending();
};
```

### 2. Ліміти розміру повідомлень та уникнення фрагментації MTU
Максимальний розмір одного повідомлення SCTP, що передається через DataChannel, декларується в SDP атрибутом `a=max-message-size:` (зазвичай 256 КіБ). Проте надсилання великих бінарних блоків призводить до розбиття SCTP-повідомлення на десятки дрібних датаграм UDP на рівні MTU каналу (стандартно 1200–1280 байтів).

Втрата хоча б одного UDP-фрагмента у бездротовому середовищі вимагає повторної збірки всього великого повідомлення. Для систем реального часу рекомендується **тримати розмір окремого бінарного пакета DataChannel суворо меншим за 1150 байтів**. Це гарантує, що кожен пакет вміщується в єдину датаграму UDP без фрагментації на мережевому рівні, що мінімізує джиттер та забезпечує миттєву обробку даних.

## Вимірювання RTT та аварійне виявлення обриву зв'язку (FailSafe)

У системах дистанційного пілотування безпілотних апаратів затримка та зв'язність є факторами безпеки: якщо канал зв'язку переривається під час польоту на високій швидкості, дрон не повинен продовжувати виконувати останню отриману команду затиснутого стіка газу.

### Алгоритм розрахунку згладженого RTT (SRTT)

Для постійного моніторингу якості каналу браузер додає 32-бітовий мікросекундний таймстемп відправки `t_send` у кожен пакет команд. Бортовий агент робота повертає цей таймстемп у наступному кадрі телеметрії. Браузер фіксує поточний час прибуття `t_recv` та обчислює поточний вимір `RTT_sample = t_recv - t_send`.

Згладжене значення RTT (`SRTT`) та варіація затримки (`RTTVAR`) оновлюються за алгоритмом Якобсона–Карнса:

```text
SRTT    = (1 - 0.125) · SRTT + 0.125 · RTT_sample
RTTVAR  = (1 - 0.250) · RTTVAR + 0.250 · |SRTT - RTT_sample|
```

### Автоматичний аварійний захист (FailSafe Trigger)

На бортовому комп'ютері робота працює незалежний таймер сторожового пса (Watchdog Timer):
1. Щоразу, коли парсер успішно декодує новий пакет команд із каналу `controls`, таймер скидається в нуль.
2. Якщо внаслідок радіозавад або виходу за межі зони дії зв'язку свіжі команди не надходять протягом **250 мс** (що відповідає пропуску 25 послідовних пакетів при частоті 100 Гц), бортовий демон ініціює аварійний режим:
   - Вмикається аварійна зупинка двигунів (для наземних роботів) або перемикання польотного контролера в автономний режим повернення на точку зльоту (RTL — Return-to-Launch для дронів).
   - Сокет SCTP надсилає серію чанків `HEARTBEAT` для діагностики фізичного стану UDP-каналу.

## Налаштування системних сокетів Linux для низькозатримкового DataChannel

Для усунення прихованих буферних затримок у ядрі Linux на бортовому комп'ютері застосовується специфічна конфігурація мережевого сокета:

1. **Вимкнення алгоритмів затримки (`SCTP_NODELAY`)**: Подібно до сокетів TCP, стек SCTP за замовчуванням може застосовувати алгоритм Нагла для агрегації дрібних пакетів у більші блоки. Для каналів керування прапорець `SCTP_NODELAY` встановлюється в `1`, примушуючи сокет відправляти кожен кадр негайно.
2. **Пріоритезація трафіку (DSCP / ToS)**: UDP-пакетам, які інкапсулюють DataChannel керування, призначається поле типу обслуговування `IP_TOS` зі значенням `IPTOS_LOWDELAY` або міткою диференційованих послуг DSCP Expedited Forwarding (`EF`, значення `0xB8`). Це гарантує, що проміжні комутатори та стільникові модеми поміщають пакети керування у високопріоритетну апаратну чергу.

## Синхронізація відеопотоку та телеметрії (Data-Video Sync)

При відображенні пілотажного інтерфейсу HUD (штучного горизонту, швидкості, висоти) критично важливо, щоб показання приладів ідеально збігалися з відеокадром на екрані браузера.

Оскільки відеопотік RTP декодується апаратним декодером браузера (через WebCodecs або тег `<video>`), між моментом прибуття RTP-пакета та рендерингом пікселів на моніторі виникає буферна затримка декодера (20–40 мс).

Для бездоганної синхронізації вебклієнт використовує API **`requestVideoFrameCallback()`**:
- До кожного кадру відео прив'язується таймстемп захоплення камери (RTP Timestamp).
- Кадри телеметрії DataChannel зберігаються у короткочасному кільцевому буфері JavaScript.
## Узгодження Stream ID та запобігання колізіям (In-band vs Out-of-band)

Створення DataChannel може відбуватися за двома принципово різними сценаріями:

### 1. Динамічне узгодження через DCEP (`negotiated: false`)
За замовчуванням один вузол викликає `createDataChannel("telemetry")`, а віддалений вузол ловить подію `ondatachannel`. При цьому рушій автоматично виділяє номер `Stream ID`.

Щоб уникнути колізій, коли обидва вузли одночасно створюють канали з однаковими номерами, RFC 8831 встановлює суворе правило парності:
- **DTLS Client (активна роль)**: зобов'язаний виділяти лише **парні номери Stream ID** (`0, 2, 4, 6...`).
- **DTLS Server (пасивна роль)**: зобов'язаний виділяти лише **непарні номери Stream ID** (`1, 3, 5, 7...`).

Це повністю усуває конфлікти розподілу потоків SCTP навіть за умов одночасного створення сотень незалежних каналів.

### 2. Попередньо узгоджені канали (`negotiated: true`)
У вбудованих системах робототехніки та нативних C++ серверах часто застосовується режим `negotiated: true`:
```ts
const telemetryChannel = peerConnection.createDataChannel("telemetry", {
    negotiated: true,
    id: 1, // Фіксований Stream ID
    ordered: false,
    maxRetransmits: 0
});
```
У цьому режимі чанки DCEP `DATA_CHANNEL_OPEN` не надсилаються в мережу. Обидві сторони заздалегідь знають конфігурацію і призначають однаковий `id`. Це дозволяє передавати телеметрію та команди негайно після завершення DTLS-рукостискання без очікування додаткового RTT на DCEP-обмін.

## Архітектура неблокуючого буфера (Lock-Free Ring Buffer) у C++

Для передачі телеметрії між апаратним потоком читання IMU (500 Гц) та мережевим потоком WebRTC неприпустимо використовувати класичні блокуючі примітиви `std::mutex` або `std::condition_variable`. Блокування потоку реального часу на м'ютексі призводить до виникнення джиттера та зриву таймінгів ШІМ.

Замість цього застосовується неблокуюча черга з одним виробником та одним споживачем (Single Producer Single Consumer, SPSC):
- Індекси читання `head_` та запису `tail_` оголошуються як атомарні змінні `std::atomic<size_t>`.
- Операції синхронізуються за допомогою семантики пам'яті `std::memory_order_release` (під час публікації кадру) та `std::memory_order_acquire` (під час зчитування).
- Поля вирівнюються за межею лінії кешу процесора (`alignas(64)`), що запобігає ефекту хибного розділення пам'яті (False Sharing) між ядрами процесора ARM або x86_64.

## Безпека та ізоляція пісочника браузера

При інтеграції WebRTC DataChannel у вебдодатки діють строгі правила безпеки W3C:
- **Ізоляція за походженням (Same-Origin Policy & CORS)**: Браузер забороняє довільним стороннім скриптам перехоплювати дані відкритого `RTCDataChannel`. Доступ до сокета має лише той контекст виконання JavaScript (`Origin`), який ініціював створення сесії.
- **Обов'язкове шифрування DTLS**: На відміну від звичайних сокетів TCP або WebSocket (де можна відкрити незахищене з'єднання `ws://`), WebRTC взагалі не підтримує роботу без активного шифрування DTLS. Передача будь-яких відкритих незашифрованих чанків SCTP неможлива на рівні коду браузера.
- **Захист від атак виснаження пам'яті**: Браузерний рушій обмежує розмір черги повідомлень `bufferedAmount` та скидає з'єднання зі статусом помилки, якщо скомпрометований віддалений пір намагається затопити клієнт нескінченними пакетами без зчитування їх додатком.
