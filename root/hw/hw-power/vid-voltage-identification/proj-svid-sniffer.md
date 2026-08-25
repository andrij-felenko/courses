# ⚙️ Програмний декодер протоколу SVID та монітор телеметрії VRM

Під час налагодження материнських плат, діагностики силових ліній процесора та дослідження динамічної поведінки алгоритмів керування живленням (DVFS) інженеру необхідно в реальному часі реєструвати пакети шини SVID (Serial Voltage Identification). Оскільки шина функціонує на тактовій частоті до 25 МГц із рівнем логіки 1.05 В, звичайні повільні інтерфейсні логери I2C/UART не здатні зафіксувати ці швидкісні транзакції.

Цей проєкт розбирає архітектуру апаратного декодера шини SVID на базі швидкісного мікроконтролера або блоку захоплення сигналів логічного аналізатора. Програма реалізує повний автомат скінченних станів (FSM) для розпізнавання старт-біта, декодування адреси регулятора, команди, байта даних VID, перевірки непарного паритету, обробки перемикання напрямку шини та вимірювання телеметрії струму (IMON) і температури (TMON).

---

### Архітектурні виклики захоплення сигналів на частоті 25 МГц

Реєстрація та аналіз транзакцій шини SVID ставить жорсткі вимоги до апаратної частини цифрового знифера. На відміну від стандартних послідовних протоколів (I2C, SPI чи UART), інтерфейс SVID має низку специфічних властивостей, які унеможливлюють використання стандартних вбудованих апаратних периферійних модулів мікроконтролерів:

1. **Некратна довжина полів пакета:** Стандартний апаратний контролер SPI орієнтований на передачу слів, кратних 8 або 16 бітам. Кадр команди SVID складається з 1 біта старту, 4 бітів адреси, 5 бітів коду команди, 8 бітів корисних даних та 1 біта паритету (сумарно 19 бітів до фази відповіді). Жоден апаратний SPI-модуль не здатний змінити межі полів на льоту без втрати синхронізації.
2. **Динамічна зміна напрямку шини посеред транзакції:** Лінія `SDATA` є строго двоспрямованою. Ведучий процесор керує лінією під час перших 19 тактів, після чого слідує інтервал перемикання (Turn-Around) тривалістю 2 такти, і на наступні 11 тактів керування лінією перехоплює контролер VRM. Апаратний знифер повинен безперервно слухати лінію, не перериваючи захоплення бітів під час зміни активного драйвера.
3. **Висока тактова частота:** При частоті `SCLK = 25.0 МГц` період тактового імпульсу становить рівно 40.0 наносекунд. Тривалість стабільного логічного рівня становить лише 20 нс. Це означає, що типовий програмний опит виводів (GPIO bit-banging) на звичайних мікроконтролерах із тактовою частотою 100–200 МГц не залишає процесорного часу навіть на базові умовні переходи, якщо код не оптимізовано на рівні асемблерних інструкцій або апаратних автоматів захоплення.

Оптимальною апаратною платформою для створення снифера є швидкодіючі мікроконтролери з блоками програмованого введення-виведення (наприклад, State Machines PIO у мікроконтролерах Raspberry Pi RP2040/RP2350, гнучкі таймери Timer Capture з прямим доступом до пам'яті DMA в сімействах STM32H7 / NXP i.MX RT) або програмовані логічні інтегральні схеми (FPGA / CPLD).

---

### Апаратний прискорювач захоплення на базі Raspberry Pi Pico PIO

Для надійної фіксації кожного такту 25 МГц без завантаження основного процесорного ядра можна використати блок програмованого вводу-виводу (PIO — Programmable I/O). Автомат PIO тактується на системній частоті 150–200 МГц (що дає дискретність 5.0–6.6 нс на інструкцію) і здійснює стробування лінії `SDATA` строго по наростаючому фронту `SCLK`.

Мікропрограма PIO чекає спадного фронту старт-біта, після чого послідовно зчитує біти в зсувний регістр вводу (ISR — Input Shift Register) і через прямий доступ до пам'яті (DMA) пересилає упаковані 32-бітні слова у кільцевий буфер оперативної пам'яті:

```
; svid_capture.pio - Асемблерна програма блоку PIO для захоплення SVID 25 МГц
.program svid_capture
.side_set 0

; Очікування високого рівня SCLK перед початком
public entry_point:
    wait 1 gpio 0        ; Очікуємо SCLK = 1 (стан спокою)
    wait 0 gpio 1        ; Очікуємо спадний фронт SDATA = 0 (Start bit)

capture_loop:
    wait 1 gpio 0        ; Очікуємо наростаючий фронт такту SCLK (0 -> 1)
    in pins, 1           ; Зчитуємо 1 біт з лінії SDATA в регістр ISR
    wait 0 gpio 0        ; Очікуємо спадний фронт SCLK (1 -> 0)
    jmp capture_loop     ; Повторюємо цикл для наступного біта
```

Ця мікропрограма виконується повністю автономно в апаратному блоці PIO. Основні ядра мікроконтролера ARM Cortex-M0+/M33 звільняються від рутинного побітового опитування і займаються виключно високорівневим розбором пакетів, розрахунком потужності та передачею журналу на комп'ютер інженера через швидкісний інтерфейс USB High-Speed (480 Мбіт/с) або мережевий міст Ethernet.

---

### Двоядерна архітектура з безблокувальним кільцевим буфером (Lock-Free Ring Buffer)

Щоб запобігти втраті транзакцій під час масивних стрибків напруги (коли процесор генерує сотні пакетів `SetVID_Fast` за кілька мілісекунд), обробка розділяється між двома ядрами мікроконтролера:

1. **Ядро 0 (Capture Core):** Працює виключно в режимі обробки переривань DMA від блоку захоплення. Воно викликає функцію автомата `svid_decoder_step()` і записує декодовані структури `svid_packet_t` у безблокувальний кільцевий буфер (Lock-Free Single-Producer Single-Consumer Queue).
2. **Ядро 1 (Logger Core):** Працює у фоновому потоці з низьким пріоритетом. Воно вичитує готові пакети з кільцевого буфера, перетворює їх на текстовий формат JSON або двійковий лог Protocol Buffers і передає на робочу станцію.

```
Архітектура обробки даних без блокувань (SPSC Queue):
┌────────────────────┐     DMA IRQ      ┌─────────────────────────┐
│ Блок захоплення    ├─────────────────►│ ЯДРО 0 (Producer):     │
│ (PIO / FPGA)       │   25 МГц біти   │ Автомат станів FSM      │
└────────────────────┘                  └───────────┬─────────────┘
                                                    │ Запис у буфер (Write Head)
                                                    ▼
                                        ┌─────────────────────────┐
                                        │ КІЛЬЦЕВИЙ БУФЕР (SPSC)  │
                                        │ Пакети svid_packet_t[N] │
                                        └───────────┬─────────────┘
                                                    │ Читання з буфера (Read Tail)
                                                    ▼
┌────────────────────┐     USB / UART   ┌─────────────────────────┐
│ Хост-комп'ютер     │◄─────────────────┤ ЯДРО 1 (Consumer):      │
│ (Wireshark / GUI)  │   Лог телеметрії │ Форматування та експорт │
└────────────────────┘                  └─────────────────────────┘
```

Така конвеєризація гарантує, що навіть при тривалих затримках виводу через USB-інтерфейс (до 10–20 мс) жоден пакет шини SVID не буде втрачений.

---

### Апаратне підключення та узгодження рівнів

Шина SVID працює при низькій напрузі живлення логіки `1.05 В` (специфікації VR12.0/VR12.5) або `1.00–1.20 В` (специфікації VR13/VR14). Якщо мікроконтролер моніторингу працює з логічними рівнями 3.3 В або 1.8 В, пряме підключення до ліній `SCLK`, `SDATA` та `ALERT#` неприпустиме через ризик пробою транзисторів процесора.

```
Схема підключення апаратного снифера:
┌─────────────────────┐                                ┌─────────────────────┐
│  МАТЕРИНСЬКА ПЛАТА  │                                │  МІКРОКОНТРОЛЕР     │
│                     │       Швидкісний буфер-        │  (ARM Cortex-M7 /   │
│  Лінія SCLK (1.05 В)├──────►транслятор рівнів ──────►│  FPGA Capture)      │
│                     │       (SN74AXC4T774, <2 нс)    │  Вхід таймера SPI/  │
│  Лінія SDATA(1.05 В)├──────►────────────────────────►│  GPIO Fast Capture  │
│                     │                                │                     │
│  Лінія ALERT#(1.05В)├──────►────────────────────────►│  Вхід EXTINT (IRQ)  │
└─────────────────────┘                                └─────────────────────┘
```

#### Вимоги до фізичного тракту узгодження:

1. **Трансляція логічних рівнів:** Використовуються надшвидкісні спеціалізовані транслятори логічних рівнів (наприклад, `SN74AXC4T774` або `TXU0304`) із власною затримкою поширення сигналу менше 2.0 нс. Первинний каскад мікросхеми живиться безпосередньо від шини напруги системного агента сокета `VCCIO`/`VTT` (1.05 В), а вторинний каскад — від внутрішнього джерела живлення аналізатора 3.3 В. Це виключає затікання зворотного струму в чутливі ланцюги процесора.
2. **Паразитарна ємність щупів:** Сумарна вхідна ємність кожного вимірювального каналу знифера (разом із друкованими доріжками плати перехідника та захисними діодами ESD) не повинна перевищувати 3.0–4.0 пФ. Перевищення цього порогу спотворює прямокутну форму тактових імпульсів 25 МГц, викликаючи завал фронтів і провокуючи збої паритету в штатному обміні між процесором та VRM.
3. **Екранування та земляний контакт:** Дріт заземлення знифера повинен мати довжину не більше 10–15 мм і під'єднуватися до найближчого полігону GND сокета процесора. Довгий земляний провідник через власну паразитну індуктивність формує контур, що вловлює високочастотні завади від перемикання силових фаз VRM із струмами у сотні амперів.

---

### Автомат станів програмного декодера (FSM)

Декодування послідовного потоку бітів базується на автоматі скінченних станів, що тактується наростаючими фронтами сигналу `SCLK`:

```
┌───────────┐    Start Bit = 0    ┌──────────────┐   4 такти    ┌──────────────┐
│ IDLE_BUS  ├────────────────────►│ READ_ADDRESS ├────────────►│ READ_COMMAND │
└─────▲─────┘                     └──────────────┘              └──────┬───────┘
      │                                                                │ 5 тактів
      │                                                                ▼
┌─────┴─────┐    TA / Response    ┌──────────────┐   8 тактів   ┌──────────────┐
│ EMIT_LOG  │◄────────────────────┤ READ_PARITY  │◄─────────────┤  READ_DATA   │
└───────────┘                     └──────────────┘   + 1 такт   └──────────────┘
```

* **`IDLE_BUS`:** Лінія `SDATA` перебуває у стані високого рівня (1.05 В). Очікується спадний фронт стартового біта.
* **`READ_ADDRESS`:** Зчитування 4 бітів адреси підпорядкованого каналу VRM (MSB first).
* **`READ_COMMAND`:** Зчитування 5 бітів коду операції (SetVID, GetReg, SetReg).
* **`READ_DATA`:** Зчитування 8 бітів корисного навантаження (код вольтажу або номер регістра).
* **`READ_PARITY`:** Зчитування біта паритету та перевірка умови непарності `(odd_parity == 1)`.
* **`READ_SLAVE_RESPONSE`:** Пропуск двох тактів Turn-Around (TA), фіксація 2 бітів підтвердження `ACK/NACK` та зчитування 8 бітів телеметрії при командах `GetReg`.

---

### Реалізація декодера та монітора

Нижче наведено модульну бібліотеку декодування пакетів шини SVID з автоматичним перетворенням кодів напруги VR12.0/VR13, розрахунком потужності та детектуванням аварійних статусів.

:::tabs
```c
/* svid_sniffer.h - Декодер шини SVID для вбудованих систем (C99/C11) */
#ifndef SVID_SNIFFER_H
#define SVID_SNIFFER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    SVID_CMD_SETVID_FAST  = 0x00,
    SVID_CMD_SETVID_SLOW  = 0x01,
    SVID_CMD_SETVID_DECAY = 0x02,
    SVID_CMD_SET_REG      = 0x03,
    SVID_CMD_GET_REG      = 0x04,
    SVID_CMD_SET_OFFSET   = 0x07,
    SVID_CMD_UNKNOWN      = 0x1F
} svid_cmd_t;

typedef enum {
    SVID_ACK_OK   = 0x00,
    SVID_ACK_NACK = 0x01,
    SVID_ACK_BUSY = 0x02
} svid_ack_t;

typedef enum {
    SVID_STATE_IDLE,
    SVID_STATE_ADDR,
    SVID_STATE_CMD,
    SVID_STATE_DATA,
    SVID_STATE_PARITY,
    SVID_STATE_TURN_AROUND,
    SVID_STATE_ACK,
    SVID_STATE_SLAVE_DATA,
    SVID_STATE_SLAVE_PARITY,
    SVID_STATE_COMPLETE
} svid_fsm_state_t;

typedef struct {
    uint8_t address;          /* 4 біти адреси VRM (0x0..0xF) */
    svid_cmd_t command;       /* 5 бітів команди */
    uint8_t master_data;      /* 8 бітів даних від процесора */
    bool master_parity_ok;    /* Результат перевірки непарності */
    svid_ack_t slave_ack;     /* Відповідь підпорядкованого пристрою */
    uint8_t slave_data;       /* Байт телеметрії від VRM */
    bool slave_parity_ok;     /* Паритет телеметрії */
    uint32_t timestamp_us;    /* Часова мітка захоплення пакету */
} svid_packet_t;

typedef struct {
    svid_fsm_state_t state;
    uint8_t bit_index;
    uint16_t shift_reg;
    uint8_t ones_count;
    svid_packet_t current_packet;
} svid_decoder_t;

/* Ініціалізація структури декодера */
void svid_decoder_init(svid_decoder_t *dec);

/* Обробка одного тактового імпульсу SCLK та стану лінії SDATA */
bool svid_decoder_step(svid_decoder_t *dec, bool sdata_bit, uint32_t timestamp_us, svid_packet_t *out_pkt);

/* Допоміжні функції перерахунку фізичних величин */
double svid_decode_voltage_vr12(uint8_t vid_code);
double svid_decode_current_imon(uint8_t imon_code, double max_current_a);
double svid_decode_temperature_tmon(uint8_t tmon_code);

#ifdef __cplusplus
}
#endif

#endif /* SVID_SNIFFER_H */

/* svid_sniffer.c - Реалізація логіки автомата станів */
#include "svid_sniffer.h"

void svid_decoder_init(svid_decoder_t *dec) {
    if (!dec) return;
    dec->state = SVID_STATE_IDLE;
    dec->bit_index = 0;
    dec->shift_reg = 0;
    dec->ones_count = 0;
}

static bool check_odd_parity(uint8_t count) {
    return (count & 1) == 1;
}

bool svid_decoder_step(svid_decoder_t *dec, bool sdata, uint32_t timestamp_us, svid_packet_t *out_pkt) {
    if (!dec) return false;

    switch (dec->state) {
    case SVID_STATE_IDLE:
        if (!sdata) { /* Виявлено стартовий біт (перехід у нуль) */
            dec->state = SVID_STATE_ADDR;
            dec->bit_index = 0;
            dec->shift_reg = 0;
            dec->ones_count = 0;
            dec->current_packet.timestamp_us = timestamp_us;
        }
        break;

    case SVID_STATE_ADDR:
        dec->shift_reg = (uint16_t)((dec->shift_reg << 1) | (sdata ? 1 : 0));
        if (sdata) dec->ones_count++;
        dec->bit_index++;
        if (dec->bit_index == 4) {
            dec->current_packet.address = (uint8_t)(dec->shift_reg & 0x0F);
            dec->state = SVID_STATE_CMD;
            dec->bit_index = 0;
            dec->shift_reg = 0;
        }
        break;

    case SVID_STATE_CMD:
        dec->shift_reg = (uint16_t)((dec->shift_reg << 1) | (sdata ? 1 : 0));
        if (sdata) dec->ones_count++;
        dec->bit_index++;
        if (dec->bit_index == 5) {
            dec->current_packet.command = (svid_cmd_t)(dec->shift_reg & 0x1F);
            dec->state = SVID_STATE_DATA;
            dec->bit_index = 0;
            dec->shift_reg = 0;
        }
        break;

    case SVID_STATE_DATA:
        dec->shift_reg = (uint16_t)((dec->shift_reg << 1) | (sdata ? 1 : 0));
        if (sdata) dec->ones_count++;
        dec->bit_index++;
        if (dec->bit_index == 8) {
            dec->current_packet.master_data = (uint8_t)(dec->shift_reg & 0xFF);
            dec->state = SVID_STATE_PARITY;
        }
        break;

    case SVID_STATE_PARITY:
        if (sdata) dec->ones_count++;
        dec->current_packet.master_parity_ok = check_odd_parity(dec->ones_count);
        dec->state = SVID_STATE_TURN_AROUND;
        dec->bit_index = 0;
        break;

    case SVID_STATE_TURN_AROUND:
        dec->bit_index++;
        if (dec->bit_index == 2) { /* 2 такти перемикання напрямку шини */
            dec->state = SVID_STATE_ACK;
            dec->bit_index = 0;
            dec->shift_reg = 0;
            dec->ones_count = 0;
        }
        break;

    case SVID_STATE_ACK:
        dec->shift_reg = (uint16_t)((dec->shift_reg << 1) | (sdata ? 1 : 0));
        dec->bit_index++;
        if (dec->bit_index == 2) {
            dec->current_packet.slave_ack = (svid_ack_t)(dec->shift_reg & 0x03);
            if (dec->current_packet.command == SVID_CMD_GET_REG) {
                dec->state = SVID_STATE_SLAVE_DATA;
                dec->bit_index = 0;
                dec->shift_reg = 0;
                dec->ones_count = 0;
            } else {
                /* Для команд запису транзакція завершена */
                dec->state = SVID_STATE_IDLE;
                if (out_pkt) *out_pkt = dec->current_packet;
                return true;
            }
        }
        break;

    case SVID_STATE_SLAVE_DATA:
        dec->shift_reg = (uint16_t)((dec->shift_reg << 1) | (sdata ? 1 : 0));
        if (sdata) dec->ones_count++;
        dec->bit_index++;
        if (dec->bit_index == 8) {
            dec->current_packet.slave_data = (uint8_t)(dec->shift_reg & 0xFF);
            dec->state = SVID_STATE_SLAVE_PARITY;
        }
        break;

    case SVID_STATE_SLAVE_PARITY:
        if (sdata) dec->ones_count++;
        dec->current_packet.slave_parity_ok = check_odd_parity(dec->ones_count);
        dec->state = SVID_STATE_IDLE;
        if (out_pkt) *out_pkt = dec->current_packet;
        return true;

    default:
        dec->state = SVID_STATE_IDLE;
        break;
    }

    return false;
}

double svid_decode_voltage_vr12(uint8_t vid_code) {
    if (vid_code == 0x00) return 0.0; /* Вихід вимкнено */
    if (vid_code == 0xFF) return 0.0; /* Зарезервовано */
    return 0.245 + ((double)vid_code * 0.005);
}

double svid_decode_current_imon(uint8_t imon_code, double max_current_a) {
    return ((double)imon_code / 255.0) * max_current_a;
}

double svid_decode_temperature_tmon(uint8_t tmon_code) {
    return (double)tmon_code; /* 1 °C на крок квантування */
}
```
```cpp
// svid_sniffer.hpp - Ідіоматичний C++20 декодер протоколу SVID
#pragma once

#include <cstdint>
#include <cstddef>
#include <optional>
#include <span>
#include <string_view>

namespace svid {

enum class Command : uint8_t {
    SetVidFast  = 0x00,
    SetVidSlow  = 0x01,
    SetVidDecay = 0x02,
    SetReg      = 0x03,
    GetReg      = 0x04,
    SetOffset   = 0x07,
    Unknown     = 0x1F
};

enum class AckStatus : uint8_t {
    Ok   = 0x00,
    Nack = 0x01,
    Busy = 0x02
};

enum class State : uint8_t {
    Idle,
    Address,
    Command,
    Data,
    Parity,
    TurnAround,
    Ack,
    SlaveData,
    SlaveParity
};

struct Packet {
    uint8_t address{0};
    Command command{Command::Unknown};
    uint8_t masterData{0};
    bool masterParityOk{false};
    AckStatus slaveAck{AckStatus::Nack};
    uint8_t slaveData{0};
    bool slaveParityOk{false};
    uint32_t timestampUs{0};

    [[nodiscard]] double voltageVr12() const noexcept {
        if (masterData == 0x00 || masterData == 0xFF) return 0.0;
        return 0.245 + (static_cast<double>(masterData) * 0.005);
    }

    [[nodiscard]] double currentImon(double maxCurrentA) const noexcept {
        return (static_cast<double>(slaveData) / 255.0) * maxCurrentA;
    }

    [[nodiscard]] double temperatureTmon() const noexcept {
        return static_cast<double>(slaveData);
    }

    [[nodiscard]] double powerWatts(double maxCurrentA) const noexcept {
        return voltageVr12() * currentImon(maxCurrentA);
    }
};

class Decoder {
public:
    constexpr Decoder() noexcept = default;

    void reset() noexcept {
        state_ = State::Idle;
        bitIndex_ = 0;
        shiftReg_ = 0;
        onesCount_ = 0;
    }

    // Обробка одного такту SCLK/SDATA. Повертає декодований пакет при завершенні транзакції.
    [[nodiscard]] std::optional<Packet> step(bool sdata, uint32_t timestampUs) noexcept {
        switch (state_) {
        case State::Idle:
            if (!sdata) {
                state_ = State::Address;
                bitIndex_ = 0;
                shiftReg_ = 0;
                onesCount_ = 0;
                currentPkt_.timestampUs = timestampUs;
            }
            break;

        case State::Address:
            shiftReg_ = static_cast<uint16_t>((shiftReg_ << 1) | (sdata ? 1 : 0));
            if (sdata) ++onesCount_;
            if (++bitIndex_ == 4) {
                currentPkt_.address = static_cast<uint8_t>(shiftReg_ & 0x0F);
                state_ = State::Command;
                bitIndex_ = 0;
                shiftReg_ = 0;
            }
            break;

        case State::Command:
            shiftReg_ = static_cast<uint16_t>((shiftReg_ << 1) | (sdata ? 1 : 0));
            if (sdata) ++onesCount_;
            if (++bitIndex_ == 5) {
                currentPkt_.command = static_cast<Command>(shiftReg_ & 0x1F);
                state_ = State::Data;
                bitIndex_ = 0;
                shiftReg_ = 0;
            }
            break;

        case State::Data:
            shiftReg_ = static_cast<uint16_t>((shiftReg_ << 1) | (sdata ? 1 : 0));
            if (sdata) ++onesCount_;
            if (++bitIndex_ == 8) {
                currentPkt_.masterData = static_cast<uint8_t>(shiftReg_ & 0xFF);
                state_ = State::Parity;
            }
            break;

        case State::Parity:
            if (sdata) ++onesCount_;
            currentPkt_.masterParityOk = ((onesCount_ & 1) == 1);
            state_ = State::TurnAround;
            bitIndex_ = 0;
            break;

        case State::TurnAround:
            if (++bitIndex_ == 2) {
                state_ = State::Ack;
                bitIndex_ = 0;
                shiftReg_ = 0;
                onesCount_ = 0;
            }
            break;

        case State::Ack:
            shiftReg_ = static_cast<uint16_t>((shiftReg_ << 1) | (sdata ? 1 : 0));
            if (++bitIndex_ == 2) {
                currentPkt_.slaveAck = static_cast<AckStatus>(shiftReg_ & 0x03);
                if (currentPkt_.command == Command::GetReg) {
                    state_ = State::SlaveData;
                    bitIndex_ = 0;
                    shiftReg_ = 0;
                    onesCount_ = 0;
                } else {
                    state_ = State::Idle;
                    return currentPkt_;
                }
            }
            break;

        case State::SlaveData:
            shiftReg_ = static_cast<uint16_t>((shiftReg_ << 1) | (sdata ? 1 : 0));
            if (sdata) ++onesCount_;
            if (++bitIndex_ == 8) {
                currentPkt_.slaveData = static_cast<uint8_t>(shiftReg_ & 0xFF);
                state_ = State::SlaveParity;
            }
            break;

        case State::SlaveParity:
            if (sdata) ++onesCount_;
            currentPkt_.slaveParityOk = ((onesCount_ & 1) == 1);
            state_ = State::Idle;
            return currentPkt_;
        }

        return std::nullopt;
    }

private:
    State state_{State::Idle};
    uint8_t bitIndex_{0};
    uint16_t shiftReg_{0};
    uint8_t onesCount_{0};
    Packet currentPkt_{};
};

} // namespace svid
```
:::

---

### Детальний розбір програмної архітектури

Реалізація декодера побудована з дотриманням жорстких вимог до системного програмування реального часу:

1. **Повна відсутність динамічного виділення пам'яті (`Zero Dynamic Allocation`):**
   Усі структури даних мають фіксований детермінований розмір і розміщуються або на стеку, або в статичній пам'яті BSS. Функція кроку автомата `svid_decoder_step()` у C та метод `Decoder::step()` у C++ не викликають `malloc()`, `new` чи стандартні динамічні контейнери. Це повністю усуває недетерміновані затримки збирача пам'яті та фрагментацію купи під час обробки мільйонів пакетів на секунду.

2. **Ідіоматичне вираження безпеки типів у C++:**
   * Версія на C++ використовує строго типізовані перечислення `enum class Command` та `enum class AckStatus`, що виключає випадкове передавання числових констант інших підсистем.
   * Для передачі опціонального результату завершення транзакції застосовано стандартний тип `std::optional<Packet>` замість передачі вказівника на результат через аргументи функції.
   * Методи конвертації фізичних величин (`voltageVr12()`, `currentImon()`, `temperatureTmon()`, `powerWatts()`) позначені атрибутом `[[nodiscard]] noexcept`, що змушує компілятор оптимізувати математичні обчислення в кілька асемблерних інструкцій без накладних витрат на обробку винятків.

3. **Бітовий контроль та обчислення паритету:**
   * Накопичення бітів здійснюється через зсувний регістр `shiftReg_ = (shiftReg_ << 1) | bit`.
   * Кількість одиничних бітів підраховується простим інкрементом лічильника `onesCount_` на кожному кроці, що вимагає лише однієї операції `(onesCount_ & 1) == 1` для миттєвої перевірки умови непарності наприкінці кадру.

---

### Практичний сценарій моніторингу: аналіз журналу телеметрії

При підключенні розробленого снифера до працюючої материнської плати під час запуску стрес-тесту обчислювальних ядер (наприклад, пакету матричного множення AVX-512) логер фіксує наступну типову послідовність пакетів SVID:

```
[00:01:24.102340] SVID MASTER -> ADDR:0x0 (Vcore) CMD:SetVID_Fast DATA:0x65 (0.750 В) [Parity:OK]
                   SLAVE RESPONSE <- ACK:OK [Parity:OK]
                   СТАТУС: Процесор перебуває в енергоощадному стані C-State (800 МГц)

[00:01:24.105120] SVID MASTER -> ADDR:0x0 (Vcore) CMD:GetReg DATA:0x15 (Reg: IOUT/IMON) [Parity:OK]
                   SLAVE RESPONSE <- ACK:OK DATA:0x0A (10d -> 9.8 А) [Parity:OK]
                   ПОТУЖНІСТЬ: P = 0.750 В · 9.8 А = 7.35 Вт

[00:01:24.500010] >>> СТАРТ НАВАНТАЖЕННЯ: Запуск 16 потоків AVX-512 <<<
[00:01:24.500012] SVID MASTER -> ADDR:0x0 (Vcore) CMD:SetVID_Fast DATA:0xC9 (1.250 В) [Parity:OK]
                   SLAVE RESPONSE <- ACK:OK [Parity:OK]
                   СТАТУС: Активація Turbo Boost (5.2 ГГц), наростання SR = 30 мВ/мкс (Δt = 16.7 мкс)

[00:01:24.500100] SVID MASTER -> ADDR:0x0 (Vcore) CMD:GetReg DATA:0x15 (Reg: IOUT/IMON) [Parity:OK]
                   SLAVE RESPONSE <- ACK:OK DATA:0xBA (186d -> 182.3 А) [Parity:OK]
                   ПОТУЖНІСТЬ: P = 1.250 В · 182.3 А = 227.88 Вт

[00:01:24.500200] SVID MASTER -> ADDR:0x0 (Vcore) CMD:GetReg DATA:0x16 (Reg: Temp/TMON) [Parity:OK]
                   SLAVE RESPONSE <- ACK:OK DATA:0x55 (85 °C) [Parity:OK]

[00:01:28.120450] !!! АПАРТНЕ ПЕРЕРИВАННЯ: Спад лінії ALERT# -> 0 !!!
[00:01:28.120452] SVID MASTER -> ADDR:0x0 (Vcore) CMD:GetReg DATA:0x10 (Reg: Status1) [Parity:OK]
                   SLAVE RESPONSE <- ACK:OK DATA:0x01 (Біт 0: VR_HOT = 1) [Parity:OK]
                   ДІЯ: Температура VRM перевищила +105 °C, процесор активує тротлінг PROCHOT#
```

---

### Інтеграція з екосистемою Sigrok та PulseView

Для візуального аналізу сигналів захоплені пакети знифера можна транслювати у формат відкритого фреймворку аналізу логіки **Sigrok / PulseView**. Протокольний декодер (Protocol Decoder) на мові Python перетворює сирі рівні ліній `SCLK`, `SDATA` та `ALERT#` на інформативні кольорові графічні блоки поверх осцилограми:

1. **Рівень 0 (Physical Framing):** Відображає старт-біт (зелений маркер), біти адреси, коду команди, дані та статус біта непарності (червоний колір у разі помилки).
2. **Рівень 1 (Command Translation):** Розгортає двійкові коди у зрозумілі інженерні назви операцій: `SetVID_Fast(1.250 В)`, `GetReg(IOUT) -> 182.3 A`, `SetReg(SlewRate) -> 30 mV/us`.
3. **Рівень 2 (Power & Telemetry Overlay):** Будує синхронний графік миттєвої електричної потужності `P(t) = V(t) · I(t)` та температурної кривої `TMON(t)` у загальному вікні часових діаграм поруч із сигналами керування тактовими генераторами процесора.

---

### Розрахунок метрик якості та надійності шини (Bus Health Metrics)

У промислових стендах автоматизованого тестування (Automated Test Equipment — ATE) програмний декодер веде безперервний статистичний підрахунок параметрів надійності передачі даних:

* **Коефіцієнт помилок паритету (Parity Error Rate — PER):**
  ```
  PER = N_parity_errors / N_total_packets
  ```
  У нормальних умовах на відлагодженій материнській платі значення `PER` має бути строго рівним `0` на вибірці з понад `10⁸` транзакцій. Поява навіть поодиноких помилок паритету свідчить про наявність перехресних наведень (Crosstalk) від сусідніх високошвидкісних ліній пам'яті DDR5 або недостатню якість розв'язки заземлювальних полігонів під сокетом.

* **Коефіцієнт завантаження шини (Bus Utilization):**
  ```
  U_bus = (N_packets · T_packet_avg) / T_measurement
  ```
  Середня тривалість транзакції SVID при тактуванні 25 МГц становить приблизно `32 такти · 40 нс = 1.28 мкс`. Якщо процесор опитує телеметрію струму та температури з частотою 100 кГц, завантаження шини становить `100 000 · 1.28·10⁻⁶ = 12.8 %`, що залишає понад 87 % смуги пропускання для миттєвої передачі термінових команд зміни вольтажу `SetVID_Fast`.

---

### Подвійна буферизація DMA та фільтрація надлишкових пакетів

Коли комп'ютер працює під статичним навантаженням, блок керування живленням генерує тисячі однакових запитів `GetReg(IOUT)` та `GetReg(Temp)` на секунду, повертаючи незмінні числові значення. Запис кожного такого пакета у флеш-пам'ять або передача по USB створює надмірний трафік.

Для вирішення цієї проблеми програмний модуль знифера реалізує дворівневу оптимізацію:

1. **Подвійна буферизація DMA (Ping-Pong Buffering):** Контролер DMA налаштовується на два чергові буфери пам'яті по 512 байтів. Поки блок PIO наповнює буфер `Ping`, ядро мікроконтролера паралельно аналізує щойно заповнений буфер `Pong`. Перемикання дескрипторів DMA відбувається апаратно без жодної наносекунди простою.
2. **Дедуплікація та компресія телеметрії (Delta Compression):** Якщо поспіль надходить серія однакових телеметричних відповідей, логер зберігає лише перший пакет і лічильник повторень `repeat_count`. Запис нового кадру виконується лише у випадках, коли:
   * Змінився код напруги VID (будь-яка команда `SetVID`);
   * Струм `IMON` змінився більше ніж на заданий поріг чутливості (наприклад, `|ΔI| > 2.0 А`);
   * Температура `TMON` змінилася на `≥ 1 °C`;
   * Зафіксовано падіння сигнальної лінії апаратного переривання `ALERT#`.

Це стискає обсяг вихідного журналу в 15–20 разів без втрати жодної фізично важливої аномалії перехідного процесу.

---

### Пастки реалізації та діагностика

Під час захоплення та аналізу шини SVID інженери стикаються з чотирма характерними апаратними проблемами:

1. **Дзвін на лінії SDATA під час перемикання напрямку (Turn-Around Glitches):**
   Коли процесор відпускає лінію `SDATA`, а контролер VRM ще не відкрив свій драйвер, лінія підтягується до 1.05 В через резистор `R_pullup`. Якщо на платі є паразитарна індуктивність доріжок, на лінії виникає короткий імпульсний завадний дзвін тривалістю 2–3 нс. Програмний декодер повинен здійснювати стробування даних строго по наростаючому фронту `SCLK` із затримкою вибірки `t_sample = 20 нс` (рівно посередині тактового імпульсу), щоб повністю ігнорувати крайові перехідні процеси.

2. **Хибне визначення біта паритету:**
   Паритет SVID завжди є **непарним** (Odd Parity). Якщо кількість одиниць у полях `ADDR + CMD + DATA` дорівнює парному числу (наприклад, 4), біт `PARITY` повинен дорівнювати `1`, роблячи суму рівною 5. Якщо сума бітів уже непарна (наприклад, 3), біт `PARITY` дорівнює `0`. Плутанина між парним (Even) та непарним (Odd) паритетом — найчастіша помилка у саморобних аналізаторах протоколу.

3. **Обробка асинхронного переривання ALERT#:**
   Лінія `ALERT#` не є синхронізованою з тактовим сигналом `SCLK`. Вона падає в нуль у довільний момент часу. Для коректної діагностики мікроконтролер повинен налаштувати лінію `ALERT#` на окремий вхід зовнішнього апаратного переривання (EXTI / IRQ) з фіксацією спадного фронту, реєструючи точний момент настання аварії `VR_HOT` або `OCP` із субмікросекундною дискретністю.

4. **Зависання автомата станів при обриві пакета:**
   Якщо ведучий процесор через збій скидає тактування `SCLK` посеред передачі байта даних, автомат FSM може назавжди застрягнути в проміжному стані `SVID_STATE_DATA`. Щоб запобігти блокуванню аналізатора, у функцію обробки додають апаратний або програмний тайм-аут бездіяльності шини (Bus Inactivity Timeout): якщо на лінії `SCLK` відсутні перепади довше ніж 1.0 мкс при високому рівні `SDATA`, стан автомата примусово скидається в `SVID_STATE_IDLE`.
