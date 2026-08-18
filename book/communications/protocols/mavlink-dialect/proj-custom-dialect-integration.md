# Інтеграція власного діалекту MAVLink для корисного навантаження

Створення спеціалізованого обладнання для безпілотних авіаційних комплексів — мультиспектральних камер для агромоніторингу, лазерних далекомірів, модулів скидання вантажу чи підводних гідролокаторів — вимагає узгодженого та надійного каналу зв'язку з польотним контролером і наземною станцією керування. Стандартних повідомлень `common.xml` зазвичай недостатньо для передачі вузькоспеціалізованих даних сенсора, таких як відліки окремих фотодіодів, статус затвора чи калібрувальні коефіцієнти матриць. Цей практичний посібник описує повний інженерний цикл розробки та інтеграції власного діалекту: від декларативного опису в XML до генерації кодеків, написання відправника телеметрії, приймача команд на C/C++ та створення тестового стенда на Python.

---

### 1. Постановка інженерної задачі та архітектура системи

Розробляється бортовий модуль 4-канального мультиспектрального сенсора для оцінки індексу вегетації рослин (Normalized Difference Vegetation Index, NDVI) під час автономного польоту агродослідного квадрокоптера. Сенсор побудований на базі мікроконтролера STM32G4 і підключається до порту `TELEM2` автопілота Pixhawk / CubeOrange через інтерфейс UART зі швидкістю 115200 бод.

Бортовий контролер сенсора виконує три базові системні завдання:
1. **Періодична телеметрія (1 Гц):** Щосекунди транслює поточний час роботи від моменту подачі живлення, температуру оптичного блоку в градусах Цельсія, сирі 16-бітні відліки чотирьох спектральних каналів (Green 560 нм, Red 660 нм, RedEdge 705 нм, NIR 840 нм) та режим активного оптичного фільтра.
2. **Розширені дані (MAVLink 2):** За наявності встановленої карти пам'яті MicroSD сенсор додає до пакета лічильник збережених знімків та відсоток заповнення носія.
3. **Керування та зворотний зв'язок:** Приймає універсальні команди запуску зйомки з параметрами експозиції та повертає квитанцію підтвердження виконання `COMMAND_ACK`.

Використання MAVLink замість довільного двійкового протоколу дає критичну перевагу: польотний контролер виступає прозорим маршрутизатором пакетів між корисним навантаженням і радіомодемом, а оператор на наземній станції бачить телеметрію у стандартному інтерфейсі QGroundControl без зміни прошивки автопілота.

---

### 2. Створення схеми діалекту `smart_multispectral.xml`

Створимо файл визначення діалекту. Щоб не дублювати базові системні повідомлення (`HEARTBEAT`, `COMMAND_LONG`, `COMMAND_ACK`), обов'язково підключаємо базову схему `common.xml` за допомогою тегу `<include>`:

```xml
<?xml version="1.0"?>
<mavlink>
  <include>common.xml</include>
  <version>3</version>
  <dialect>42</dialect>

  <enums>
    <!-- Перелік оптичних фільтрів сенсора -->
    <enum name="MULTISPECTRAL_FILTER_MODE">
      <description>Режими роботи оптичного револьвера фільтрів.</description>
      <entry value="0" name="FILTER_MODE_OFF">
        <description>Затвор закрито, темнове калібрування сенсора.</description>
      </entry>
      <entry value="1" name="FILTER_MODE_4_CHANNEL">
        <description>Синхронне зчитування 4 каналів (RGB + NIR).</description>
      </entry>
      <entry value="2" name="FILTER_MODE_CUSTOM_BAND">
        <description>Окремий вузькосмуговий фільтр RedEdge (705 нм).</description>
      </entry>
    </enum>

    <!-- Розширення переліку команд MAV_CMD -->
    <enum name="MAV_CMD">
      <entry value="42050" name="MAV_CMD_DO_TRIGGER_SPECTRAL_CAPTURE">
        <description>Запустити синхронну експозицію спектральних матриць.</description>
        <param index="1" label="Експозиція (мс)" units="ms" minValue="1" maxValue="1000" default="50">
          Час накопичення заряду матриці.
        </param>
        <param index="2" label="Режим фільтра" enum="MULTISPECTRAL_FILTER_MODE" default="1">
          Номер оптичного фільтра.
        </param>
        <param index="3" label="Кількість знімків" minValue="1" maxValue="100" default="1">
          Кількість кадрів у серії.
        </param>
        <param index="4" label="Зарезервовано">Порожній слот (передавати 0).</param>
        <param index="5">Зарезервовано.</param>
        <param index="6">Зарезервовано.</param>
        <param index="7">Зарезервовано.</param>
      </entry>
    </enum>
  </enums>

  <messages>
    <!-- Телеметрія спектрального сенсора -->
    <message id="42001" name="MULTISPECTRAL_SURVEY_STATUS">
      <description>Періодичний звіт про стан спектрального сенсора.</description>
      <field type="uint32_t" name="time_boot_ms" units="ms">Час від запуску системи.</field>
      <field type="float"    name="sensor_temperature" units="degC">Температура оптичного блоку.</field>
      <field type="uint16_t" name="raw_channels[4]">Відліки 4 спектральних каналів (Green, Red, RedEdge, NIR).</field>
      <field type="uint8_t"  name="filter_mode" enum="MULTISPECTRAL_FILTER_MODE">Активний оптичний фільтр.</field>
      <field type="uint8_t"  name="status_flags">Бітові прапорці апаратного стану сенсора.</field>
      <extensions/>
      <field type="uint32_t" name="frame_counter" default="0">Лічильник збережених знімків на носії.</field>
      <field type="uint8_t"  name="sd_storage_pct" units="%" invalid="UINT8_MAX">Відсоток заповнення карти пам'яті.</field>
    </message>
  </messages>
</mavlink>
```

#### Анатомія розкладки полів у повідомленні #42001
Зверніть увагу на структуру повідомлення `MULTISPECTRAL_SURVEY_STATUS`:
* **Базова частина:** Містить 18 байтів даних: `time_boot_ms` (4 байти) + `sensor_temperature` (4 байти) + `raw_channels[4]` (8 байтів) + `filter_mode` (1 байт) + `status_flags` (1 байт). Оскільки всі типи впорядковано за спаданням розміру (4 → 4 → 2 → 1 → 1), жоден байт пам'яті не втрачається на вирівнювальні заповнювачі.
* **Розширена частина (`<extensions/>`):** Містить 5 додаткових байтів: `frame_counter` (4 байти) + `sd_storage_pct` (1 байт). Ця частина не впливає на контрольний хеш `CRC_EXTRA` базової структури.

---

### 3. Автоматична генерація коду через `mavgen`

Для перетворення XML-опису у двійкові кодеки використовується утиліта `mavgen` із пакета `pymavlink`. Запустимо генерацію для C-заголовків та модуля Python:

```bash
# Встановлення офіційних інструментів генерації
pip install pymavlink future

# Генерація C/C++ header-only бібліотеки для мікроконтролера
python -m pymavlink.tools.mavgen \
    --lang=C \
    --wire-protocol=2.0 \
    --output=generated/c_mavlink \
    smart_multispectral.xml

# Генерація модуля Python для тестового стенда
python -m pymavlink.tools.mavgen \
    --lang=Python \
    --wire-protocol=2.0 \
    --output=generated/python/smart_multispectral.py \
    smart_multispectral.xml
```

У результаті роботи генератора в каталозі `generated/c_mavlink/smart_multispectral/` буде створено повний набір C-заголовків. Ключовим файлом є `mavlink_msg_multispectral_survey_status.h`, де оголошено константи довжини, макроси упаковки та структуру даних `mavlink_multispectral_survey_status_t`.

---

### 4. Реалізація передавача телеметрії (Transmitter)

Модуль сенсора опитує аналого-цифрові канали через DMA, заповнює службові поля, викликає функцію упаковки повідомлення та ініціює передачу байтового масиву в апаратний UART.

:::tabs
```c
/* transmitter_c.c — Реалізація відправника чистою мовою C */
#include <stdint.h>
#include <string.h>
#include "smart_multispectral/mavlink.h"

#define SENSOR_SYSID  1      /* System ID нашого безпілотного апарата */
#define SENSOR_COMPID 100    /* Component ID корисного навантаження (MAV_COMP_ID_PAYLOAD) */

/* Зовнішня низькорівнева функція передачі буфера через UART DMA */
extern void uart_dma_transmit(const uint8_t *data, uint16_t length);

void send_multispectral_telemetry(uint32_t boot_time_ms, float temp_c,
                                  const uint16_t channels[4], uint8_t filter,
                                  uint32_t photo_count, uint8_t sd_pct)
{
    mavlink_message_t msg;
    uint8_t tx_buffer[MAVLINK_MAX_PACKET_LEN];

    /* Пакування структури повідомлення з урахуванням полів розширення */
    mavlink_msg_multispectral_survey_status_pack(
        SENSOR_SYSID,
        SENSOR_COMPID,
        &msg,
        boot_time_ms,
        temp_c,
        channels,
        filter,
        0x01,         /* Прапорець: калібрування сенсора валідне */
        photo_count,  /* Поле розширення: лічильник знімків */
        sd_pct        /* Поле розширення: відсоток заповнення карти пам'яті */
    );

    /* Серіалізація кадру в плоский бінарний буфер (з відтинанням кінцевих нулів) */
    uint16_t len = mavlink_msg_to_send_buffer(tx_buffer, &msg);

    /* Відправка готового кадру в апаратний UART */
    uart_dma_transmit(tx_buffer, len);
}
```
```cpp
// transmitter_cpp.hpp — Ідіоматична обгортка мовою C++
#pragma once
#include <array>
#include <cstdint>
#include <span>
#include "smart_multispectral/mavlink.h"

class MultispectralTransmitter {
public:
    enum class FilterMode : uint8_t {
        Off = 0,
        FourChannel = 1,
        CustomBand = 2
    };

    struct SensorTelemetry {
        uint32_t time_boot_ms;
        float temperature_c;
        std::array<uint16_t, 4> raw_channels;
        FilterMode filter;
        uint8_t status_flags;
        uint32_t frame_counter;
        uint8_t sd_storage_pct;
    };

    MultispectralTransmitter(uint8_t sys_id, uint8_t comp_id)
        : sys_id_(sys_id), comp_id_(comp_id) {}

    template <typename TransmitFn>
    void send_telemetry(const SensorTelemetry& data, TransmitFn&& transmit_fn) {
        mavlink_message_t msg;
        std::array<uint8_t, MAVLINK_MAX_PACKET_LEN> buffer;

        mavlink_msg_multispectral_survey_status_pack(
            sys_id_,
            comp_id_,
            &msg,
            data.time_boot_ms,
            data.temperature_c,
            data.raw_channels.data(),
            static_cast<uint8_t>(data.filter),
            data.status_flags,
            data.frame_counter,
            data.sd_storage_pct
        );

        const uint16_t len = mavlink_msg_to_send_buffer(buffer.data(), &msg);
        transmit_fn(std::span<const uint8_t>(buffer.data(), len));
    }

private:
    uint8_t sys_id_;
    uint8_t comp_id_;
};
```
:::

#### Пояснення відмінностей реалізацій C та C++
* У версії на C функції приймають плоскі покажчики на сирі масиви `channels` і використовують глобальні статичні буфери, що є типовим підходом для простих проєктів безпосередньо на регістрах мікроконтролера.
* У версії на C++ застосовано безпечні абстракції сучасного стандарту: типізований перелік `enum class FilterMode` захищає від передачі невалідного індексу фільтра під час компіляції, контейнер `std::array` гарантує передачу рівно 4 спектральних каналів, а використання `std::span` унеможливлює вихід за межі вихідного буфера пам'яті.

---

### 5. Реалізація приймача та диспетчера команд (Receiver)

Приймач повинен безперервно зчитувати потік байтів з кільцевого буфера UART, виділяти валідні кадри MAVLink 2, перевіряти контрольну суму та адресувати вхідні команди `COMMAND_LONG` відповідному обробнику апаратного затвора.

:::tabs
```c
/* receiver_c.c — Побайтовий парсер та диспетчер команд на C */
#include <stdint.h>
#include "smart_multispectral/mavlink.h"

#define SENSOR_SYSID  1
#define SENSOR_COMPID 100

extern void uart_send_bytes(const uint8_t *data, uint16_t length);
extern void trigger_hardware_capture(uint32_t exposure_ms, uint8_t filter);

static void handle_command_long(const mavlink_message_t *msg)
{
    mavlink_command_long_t cmd;
    mavlink_msg_command_long_decode(msg, &cmd);

    /* Перевіряємо адресність: команда призначена нашому модулю? */
    if (cmd.target_system != SENSOR_SYSID && cmd.target_system != 0) return;
    if (cmd.target_component != SENSOR_COMPID && cmd.target_component != 0) return;

    uint8_t result = MAV_RESULT_UNSUPPORTED;

    if (cmd.command == 42050 /* MAV_CMD_DO_TRIGGER_SPECTRAL_CAPTURE */) {
        uint32_t exposure_ms = (uint32_t)cmd.param1;
        uint8_t filter_mode = (uint8_t)cmd.param2;

        /* Запуск апаратного процесу зйомки */
        trigger_hardware_capture(exposure_ms, filter_mode);
        result = MAV_RESULT_ACCEPTED;
    }

    /* Надсилаємо підтвердження виконання команди (COMMAND_ACK) */
    mavlink_message_t ack_msg;
    uint8_t tx_buf[MAVLINK_MAX_PACKET_LEN];

    mavlink_msg_command_ack_pack(
        SENSOR_SYSID,
        SENSOR_COMPID,
        &ack_msg,
        cmd.command,
        result,
        0,     /* progress */
        0,     /* result_param2 */
        msg->sysid,
        msg->compid
    );

    uint16_t len = mavlink_msg_to_send_buffer(tx_buf, &ack_msg);
    uart_send_bytes(tx_buf, len);
}

void process_incoming_byte(uint8_t byte)
{
    mavlink_message_t msg;
    mavlink_status_t status;

    /* Побайтовий скінченний автомат розбору кадру MAVLink */
    if (mavlink_parse_char(MAVLINK_COMM_0, byte, &msg, &status)) {
        switch (msg.msgid) {
            case MAVLINK_MSG_ID_COMMAND_LONG:
                handle_command_long(&msg);
                break;
            default:
                break;
        }
    }
}
```
```cpp
// receiver_cpp.hpp — Ідіоматичний обробник та диспетчер на C++
#pragma once
#include <functional>
#include <span>
#include <array>
#include "smart_multispectral/mavlink.h"

class MavlinkCommandDispatcher {
public:
    using CaptureCallback = std::function<bool(uint32_t exposure_ms, uint8_t filter_mode)>;

    MavlinkCommandDispatcher(uint8_t sys_id, uint8_t comp_id)
        : sys_id_(sys_id), comp_id_(comp_id) {}

    void set_capture_handler(CaptureCallback handler) {
        capture_handler_ = std::move(handler);
    }

    template <typename TransmitFn>
    void feed_byte(uint8_t byte, TransmitFn&& transmit_fn) {
        mavlink_message_t msg;
        mavlink_status_t status;

        if (mavlink_parse_char(MAVLINK_COMM_0, byte, &msg, &status)) {
            dispatch_message(msg, transmit_fn);
        }
    }

private:
    template <typename TransmitFn>
    void dispatch_message(const mavlink_message_t& msg, TransmitFn&& transmit_fn) {
        if (msg.msgid == MAVLINK_MSG_ID_COMMAND_LONG) {
            mavlink_command_long_t cmd;
            mavlink_msg_command_long_decode(&msg, &cmd);

            if (cmd.target_system != sys_id_ && cmd.target_system != 0) return;
            if (cmd.target_component != comp_id_ && cmd.target_component != 0) return;

            uint8_t result = MAV_RESULT_UNSUPPORTED;
            if (cmd.command == 42050 && capture_handler_) {
                const bool ok = capture_handler_(
                    static_cast<uint32_t>(cmd.param1),
                    static_cast<uint8_t>(cmd.param2)
                );
                result = ok ? MAV_RESULT_ACCEPTED : MAV_RESULT_FAILED;
            }

            mavlink_message_t ack_msg;
            std::array<uint8_t, MAVLINK_MAX_PACKET_LEN> buffer;
            mavlink_msg_command_ack_pack(
                sys_id_, comp_id_, &ack_msg,
                cmd.command, result, 0, 0,
                msg.sysid, msg.compid
            );

            const uint16_t len = mavlink_msg_to_send_buffer(buffer.data(), &ack_msg);
            transmit_fn(std::span<const uint8_t>(buffer.data(), len));
        }
    }

    uint8_t sys_id_;
    uint8_t comp_id_;
    CaptureCallback capture_handler_;
};
```
:::

---

### 6. Архітектура кільцевого буфера UART DMA та обробка переривань

На реальному мікроконтролері (STM32G4/F4) побайтове опитування вхідного порту через блокуючі виклики або звичайні переривання `RXNE` призводить до значного навантаження на процесор і втрати байтів при сплесках трафіку. Для надійної обробки застосовується апаратний DMA у циклічному режимі (Circular Mode) у поєднанні з перериванням лінії очікування (UART Idle Line Detection):

```
Апаратний UART RX ───► Циклічний буфер DMA (512B) ───► IDLE / Half-Transfer IRQ
                                                             │
                                                             ▼
                                                    mavlink_parse_char()
                                                             │
                                                             ▼
                                                    Диспетчер подій сенсора
```

1. **Конфігурація DMA:** Канал DMA налаштовується на постійний запис вхідних байтів із регістра `USART_RDR` у масив пам'яті розміром 512 байтів.
2. **Переривання `USART_IT_IDLE`:** Коли передача пакета завершується і на лінії встановлюється високий рівень протягом часу одного кадру (10 бітових інтервалів), мікроконтролер генерує переривання IDLE.
3. **Обчислення зміщення:** Процесор зчитує поточний лічильник залишкових передач DMA (`DMA_CNDTR`), визначає кількість новоприбулих байтів і передає їх у функцію `mavlink_parse_char()`. Такий підхід забезпечує мінімальну затримку реакції (менше 100 мікросекунд) та нульове завантаження ядра CPU під час очікування кадру.

---

### 7. Скрипт верифікації та емулятор наземної станції на Python

Для тестування розробленого модуля підключимо мікроконтролер через USB-UART перехідник до комп'ютера та запустимо автоматизований скрипт на базі згенерованого модуля `pymavlink`:

```python
#!/usr/bin/env python3
"""
test_payload_client.py — Клієнт перевірки кастомного діалекту MAVLink.
Підключається до UART-порту сенсора, слухає телеметрію та надсилає команди.
"""
import time
import sys
from pymavlink import mavutil

# Імпортуємо згенерований модуль діалекту
import smart_multispectral as custom_mavlink

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = 115200

    print(f"Підключення до сенсора на {port} зі швидкістю {baud} бод...")
    # Створюємо MAVLink з'єднання із зазначенням нашого діалекту
    master = mavutil.mavlink_connection(port, baud=baud, dialect="smart_multispectral")
    master.wait_heartbeat(timeout=5)

    print("З'єднання встановлено. Очікування кастомної телеметрії #42001...")

    # Чекаємо 3 телеметричні повідомлення
    for _ in range(3):
        msg = master.recv_match(type='MULTISPECTRAL_SURVEY_STATUS', blocking=True, timeout=3)
        if msg:
            print(f"[ТЕЛЕМЕТРІЯ] Час: {msg.time_boot_ms} мс | "
                  f"Темп: {msg.sensor_temperature:.2f} °C | "
                  f"Канали: {msg.raw_channels} | "
                  f"Фото: {getattr(msg, 'frame_counter', 0)} | "
                  f"SD: {getattr(msg, 'sd_storage_pct', 0)}%")
        else:
            print("Попередження: таймаут очікування телеметрії!")

    print("\nНадсилання команди запуску зйомки MAV_CMD_DO_TRIGGER_SPECTRAL_CAPTURE (#42050)...")
    master.mav.command_long_send(
        1,                  # target_system (БПЛА)
        100,                # target_component (Мультиспектральний модуль)
        42050,              # command
        0,                  # confirmation
        75.0,               # param1: експозиція 75 мс
        1.0,                # param2: 4-канальний режим
        1.0,                # param3: 1 кадр
        0, 0, 0, 0          # param4..7: зарезервовано
    )

    # Очікування відповіді COMMAND_ACK
    ack = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
    if ack and ack.command == 42050:
        print(f"Отримано підтвердження COMMAND_ACK: результат = {ack.result} (0 = ACCEPTED)")
    else:
        print("Помилка: не отримано підтвердження команди!")

if __name__ == '__main__':
    main()
```

---

### 8. Трасування двійкового кадру на каналі передачі

Розглянемо побайтову структуру сформованого кадру MAVLink 2 для повідомлення `MULTISPECTRAL_SURVEY_STATUS` (#42001). Це допомагає діагностувати помилки під час налагодження протоколу за допомогою логічного аналізатора або Wireshark:

```
Зсув (байт)   Поле кадру              Значення (HEX)    Опис
─────────────────────────────────────────────────────────────────────────────
0             STX                     0xFD              Стартовий маркер кадру MAVLink 2
1             LEN                     0x17 (23 байти)   Довжина корисних даних (18 base + 5 ext)
2             INCOMPAT_FLAGS          0x00              Несумісні прапорці (підпис відсутній)
3             COMPAT_FLAGS            0x00              Сумісні прапорці
4             SEQ                     0x2A (42)         Порядковий номер кадру
5             SYSID                   0x01              System ID (БПЛА 1)
6             COMPID                  0x64 (100)        Component ID (Корисне навантаження)
7..9          MSGID                   0x41 0xA4 0x00    Message ID = 42001 (0x00A441, little-endian)
10..13        time_boot_ms            0xE8 0x03 0x00 0x00  1000 мс
14..17        sensor_temperature      0x00 0x00 0x20 0x41  25.0 °C (IEEE 754 float)
18..25        raw_channels[4]         0x00 0x04 ...     4 канали по 2 байти
26            filter_mode             0x01              FILTER_MODE_4_CHANNEL
27            status_flags            0x01              Сенсор готовий
28..31        frame_counter [ext]     0x0C 0x00 0x00 0x00  12 знімків
32            sd_storage_pct [ext]    0x1E              30% заповнення карти
33..34        CRC-16                  0x5B 0xD2         Контрольна сума кадру з урахуванням CRC_EXTRA
─────────────────────────────────────────────────────────────────────────────
Загальний розмір пакета: 35 байтів (10 байтів заголовок + 23 байти payload + 2 байти CRC)
```

Якщо на момент передачі поля розширення `frame_counter` та `sd_storage_pct` мають нульові значення (`0x00`), передавач MAVLink 2 автоматично відтинає ці 5 байтів з кінця корисних даних. Поле `LEN` у заголовку зменшується з 23 до 18 байтів, а розмір кадру скорочується до 30 байтів.

---

### 9. Розрахунок пропускної здатності та бюджету каналу зв'язку

Під час проєктування бортового комплексу критично важливо правильно узгодити частоту передачі кастомних повідомлень із фізичною пропускною здатністю каналу зв'язку.

У стандартному форматі UART 8N1 (1 стартовий біт, 8 бітів даних, 1 стоповий біт, без парності) кожен байт на фізичному рівні вимагає передачі 10 бітів. Розглянемо бюджет передачі нашого пакета довжиною 35 байтів (350 бітів на фізичній лінії):

* **При частоті 1 Гц:** Канал завантажується на 350 біт/с. Для швидкості 115200 бод (корисна ємність 11520 байт/с) це становить лише 0.3% пропускної здатності каналу.
* **При частоті 10 Гц:** Навантаження зростає до 3500 біт/с (3.0% ємності порту 115200 бод). Проте якщо цей потік пересилається через вузькосмуговий радіомодем на швидкості 57600 бод паралельно з основним навігаційним потоком автопілота (де сумарний трафік сягає 4000 байт/с), виникає ризик переповнення буфера радіоканалу та зростання джиттеру затримок.
* **Ефект нульового обтинання:** Коли поля розширення містять нулі, розмір кадру скорочується на 5 байтів (до 30 байтів). На частоті 10 Гц це економить 500 біт/с ефірного трафіку, що становить 14.3% загального обсягу пакета сенсора.

---

### 10. Інтеграція плагіна в консоль MAVProxy

Для польових випробувань та швидкого налагодження бортових систем розробники часто використовують модульний термінал керування `MAVProxy`. Створимо власний плагін `mavproxy_multispectral.py`, який додає зручні консольні команди для оператора:

```python
"""
mavproxy_multispectral.py — Розширення консолі MAVProxy для спектральної камери.
"""
from MAVProxy.modules.lib import mp_module

class MultispectralModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(MultispectralModule, self).__init__(mpstate, "multispectral", "Підтримка спектральної камери")
        self.add_command('spectral', self.cmd_spectral, "Команди спектрального сенсора", ['trigger', 'status'])

    def cmd_spectral(self, args):
        if len(args) < 1:
            print("Використання: spectral trigger <exposure_ms> <filter_id>")
            return

        if args[0] == 'trigger':
            exp = float(args[1]) if len(args) > 1 else 50.0
            flt = float(args[2]) if len(args) > 2 else 1.0
            print(f"Відправка команди зйомки: експозиція {exp} мс, фільтр {flt}")
            self.master.mav.command_long_send(
                self.settings.target_system,
                100,  # Component ID
                42050, 0, exp, flt, 1.0, 0, 0, 0, 0
            )

    def mavlink_packet(self, msg):
        if msg.get_type() == 'MULTISPECTRAL_SURVEY_STATUS':
            # Логування кастомної телеметрії у фоновому режимі
            self.console.writeln(f"[СЕНСОР] T={msg.sensor_temperature:.1f}C NIR={msg.raw_channels[3]}", bg='black')

def init(mpstate):
    return MultispectralModule(mpstate)
```

Оператор завантажує модуль у терміналі командою `module load multispectral` і може керувати сенсором простою командою `spectral trigger 100 1` безпосередньо під час польоту.

---

### 11. Автоматизоване тестування стійкості до бітових спотворень

Для верифікації надійності зв'язку в умовах радіозавад використовується тест ін'єкції штучних помилок. Скрипт емулює пошкодження випадкових бітів у кадрі та перевіряє, чи коректно парсер MAVLink відсіює спотворені пакети:

```python
"""
stress_test_crc.py — Стрес-тест стійкості до спотворення бітів у каналі зв'язку.
"""
import random
from pymavlink import mavutil
import smart_multispectral as custom_mavlink

def run_bitflip_test(iterations=1000):
    mav = custom_mavlink.MAVLink(None, srcSystem=1, srcComponent=100)
    rejected_corrupted = 0
    passed_clean = 0

    for i in range(iterations):
        # Генеруємо чистий тестовий пакет
        msg = mav.multispectral_survey_status_encode(
            time_boot_ms=i * 100,
            sensor_temperature=24.5,
            raw_channels=[1000, 2000, 3000, 4000],
            filter_mode=1,
            status_flags=0x01,
            frame_counter=i,
            sd_storage_pct=45
        )
        wire_data = bytearray(msg.pack(mav))

        # Спотворюємо один випадковий біт у середині корисного навантаження
        corrupt_idx = random.randint(10, len(wire_data) - 3)
        wire_data[corrupt_idx] ^= (1 << random.randint(0, 7))

        # Передаємо пошкоджений буфер парсеру
        test_parser = custom_mavlink.MAVLink(None)
        parsed = None
        for b in wire_data:
            m = test_parser.parse_char(bytes([b]))
            if m is not None:
                parsed = m

        if parsed is None:
            rejected_corrupted += 1

    print(f"Тест завершено: перевірено {iterations} спотворених пакетів.")
    print(f"Відсіяно контрольною сумою CRC-16/CRC_EXTRA: {rejected_corrupted} з {iterations} (100.0%)")

if __name__ == '__main__':
    run_bitflip_test(1000)
```

Завдяки суворому поєднанню CRC-16 та байта `CRC_EXTRA` жоден спотворений кадр не приймається диспетчером, що гарантує цілісність даних польотної телеметрії.

---

### 12. Маршрутизація кастомних повідомлень через польотний стек

Коли модуль підключається до послідовного порту `TELEM2` польотного контролера (наприклад, Pixhawk під керуванням ArduPilot або PX4), автопілот повинен пересилати кастомні повідомлення на наземну станцію керування (QGroundControl) через радіомодем на порту `TELEM1`.

#### Налаштування в ArduPilot
1. Встановіть параметр порту `SERIAL2_PROTOCOL = 2` (MAVLink 2).
2. За замовчуванням маршрутизатор ArduPilot автоматично транслює всі повідомлення з `CompID != 1` на всі активні порти, де виявлено наземну станцію (`SYSID_MYGCS`). Якщо швидкість радіоканалу обмежена (наприклад, 57600 бод на телеметрії SiK 915 MHz), переконайтеся, що частота передачі кастомної телеметрії не перевищує 2–4 Гц, щоб уникнути переповнення черги `mavlink_channel_t`.

#### Налаштування в PX4 Autopilot
У PX4 маршрутизація здійснюється через менеджер потоків `mavlink`. У файлі запуску або параметрах QGroundControl призначте екземпляр MAVLink для порту `TELEM2`:
* `MAV_2_CONFIG = TELEM 2`
* `MAV_2_MODE = Custom` або `Onboard`
* `MAV_2_RATE = 115200`

---

### 13. Інтеграція діалекту в QGroundControl

Щоб оператор на наземній станції міг бачити розширені параметри спектрального сенсора та викликати команду зйомки через графічний інтерфейс, виконайте такі кроки:

1. **Компіляція діалекту в QGC:** Скопіюйте файл `smart_multispectral.xml` у теку вихідного коду `qgroundcontrol/libs/mavlink/include/mavlink/v2.0/custom/`.
2. **Перекомпіляція кодеків:** Запустіть скрипт генерації MAVLink всередині дерева збірки QGroundControl, щоб створити C++ заголовки діалекту.
3. **Створення QML-віджета:** У дереві ресурсів QGroundControl додайте віджет панелі інструментів (Instrument Panel), який підписується на сигнал `vehicle->mavlinkMessageReceived` та оновлює графічні індикатори спектральних каналів при отриманні повідомлення з ID #42001.

---

### 14. Еволюція схеми та підтримка зворотної сумісності

Коли сенсор уже розгорнуто у складі серійних безпілотників, виникає потреба додавати нові датчики (наприклад, GPS-синхронізатор часу експозиції або акселерометр вібрацій). Для збереження сумісності з раніше випущеними наземними станціями дотримуйтеся правил:

1. **Додавання полів суворо після `<extensions/>`:** Якщо додати нове поле до базової секції, зміниться константа `CRC_EXTRA`, і всі старі наземні станції миттєво втратять зв'язок із новим модулем.
2. **Заборона зміни послідовності та типів наявних полів:** Поля в секції розширення не сортуються генератором і кодуються у порядку їх оголошення в XML.
3. **Інкремент номера версії:** Щоразу при додаванні нових параметрів збільшуйте числове значення у тегу `<version>` (наприклад, `<version>4</version>`), що сигналізує системі про розширені можливості апаратної ревізії.

---

### 15. Передпольотний чекліст верифікації інтеграції

Перед першим тестовим вильотом безпілотного апарата з інтегрованим кастомним модулем виконайте перевірку за інженерним чеклістом:

1. **Валідація схеми:** Файл XML успішно проходить перевірку `xmllint` без зауважень синтаксису.
2. **Унікальність Message ID:** Перевірено відсутність колізій із `common.xml` та `ardupilotmega.xml` (номер #42001 вільний).
3. **Збіг `CRC_EXTRA`:** Байт контрольної суми у прошивці мікроконтролера строго збігається з байтом у кодеку наземної станції QGC.
4. **Конфігурація `Component ID`:** Модулю присвоєно унікальний `CompID = 100`, що виключає конфлікти з автопілотом.
5. **Тест нульового обтинання:** Перевірено, що при нульових полях розширення пакет успішно декодується приймачем старої версії.
6. **Бюджет UART:** Виміряне навантаження порту при максимальній частоті зйомки не перевищує 35% ємності каналу.
7. **Обробка помилок `COMMAND_ACK`:** У разі некоректних параметрів команди модуль повертає `MAV_RESULT_DENIED` або `FAILED`.
8. **Ізоляція живлення:** Перевірено відсутність стрибків струму по лінії 5V під час спрацьовування електромагнітного затвора.

---

### 16. Запис кастомної телеметрії в бортовий журнал польоту

Під час виконання автономної місії зв'язок із наземною станцією керування може тимчасово втрачатися. Щоб зберегти всі зібрані мультиспектральні дані для подальшого аналізу та побудови ортофотоплану, автопілот повинен зберігати кастомні пакети MAVLink у бортовий чорний ящик (Dataflash на SD-карті):

* **Формат ArduPilot Dataflash (`.bin`):** Польотний контролер автоматично логує вхідні MAVLink-кадри у бінарну структуру `FMT` / `MAV_MSG`. Для перегляду таких журналів утиліта `mavlogdump.py` з бібліотеки `pymavlink` розпаковує повідомлення #42001 у форматі CSV або JSON:
  ```bash
  mavlogdump.py --dialect=smart_multispectral --types=MULTISPECTRAL_SURVEY_STATUS flight_log.bin > telemetry.csv
  ```
* **Формат PX4 ULog (`.ulg`):** Модуль `logger` у PX4 перехоплює всі кадри з MAVLink-порту та записує їх у топік `mavlink_log`. Під час постобробки в PlotJuggler або Flight Review користувач бачить графіки температури сенсора та криві відгуку фотодіодів, синхронізовані за часом із просторовими координатами GPS.
* **Відтворення в SITL-симуляторі:** Під час тестування у програмному симуляторі Software-In-The-Loop згенерований двійковий лог польоту можна відтворити командою `mavproxy.py --master=tcp:127.0.0.1:5760 --dialect=smart_multispectral`. Це дає змогу верифікувати обробку аварійних ситуацій та втрату пакетів на ідентичній копії польотного стека без ризику пошкодження реального обладнання.

---

### 17. Типові пастки та крайові випадки

Під час розробки та польотної інтеграції кастомних діалектів необхідно враховувати чотири типові апаратні та протокольні пастки:

1. **Колізія `Component ID` з автопілотом:**
   * Ніколи не призначайте модулю корисного навантаження `CompID = 1` (`MAV_COMP_ID_AUTOPILOT1`). Це призведе до того, що наземна станція сприйматиме телеметрію датчика як статус головного польотного контролера. Завжди використовуйте ідентифікатори з діапазону `100 .. 150` або стандартизовані константи (`MAV_COMP_ID_PAYLOAD`, `MAV_COMP_ID_GIMBAL`, `MAV_COMP_ID_CAMERA`).
2. **Обробка неініціалізованих полів розширення:**
   * Завдяки механізму нульового обтинання (Zero-Truncation) приймач автоматично заповнює відсутні поля нулями. Якщо число `0` є валідним показником фізичного датчика (наприклад, кут 0° чи температура 0 °C), використовуйте спеціальні сигнальні значення (наприклад, `invalid="NaN"` або `invalid="UINT8_MAX"` для позначення відсутності вимірювання).
3. **Переповнення буфера UART на мікроконтролері:**
   * Генерація MAVLink-кадрів з високою частотою (понад 20 Гц) при швидкості UART 57600 бод може викликати блокування або втрату байтів. Використовуйте DMA з подвійною буферизацією (Ping-Pong buffers) для безперервної передачі даних без завантаження ядра CPU.
4. **Контроль версій MAVLink 1 проти MAVLink 2:**
   * Пам'ятайте, що повідомлення з Message ID понад 255 фізично не можуть бути передані у форматі MAVLink 1. Якщо ваш радіомодем або ретранслятор сконфігуровано в режимі примусового MAVLink 1, кастомне повідомлення `#42001` буде скинуто на канальному рівні. Завжди вмикайте протокол версії 2.0 на обох кінцях лінії зв'язку.
