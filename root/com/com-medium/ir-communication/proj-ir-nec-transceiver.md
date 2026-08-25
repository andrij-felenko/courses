# ⚙️ Програмний прийомопередавач протоколу NEC на мікроконтролері

Реалізація протоколу NEC на мікроконтролері вимагає прецизійного формування пачок тримальної частоти 38 кГц для передавача та вимірювання інтервалів між перепадами напруги за допомогою таймера вхідного захоплення (Input Capture) для приймача.

### 1. Архітектура апаратних таймерів та часові допуски

Протокол NEC використовує кодування довжиною паузи (Pulse Distance Modulation). Для стабільного декодування в умовах оптичних шумів і коливань тактової частоти внутрішнього RC-генератора мікроконтролера приймач повинен підтримувати допустимий коридор похибки `±20%`:

- **Преамбула (Leader code)**: пачка 9000 мкс (допуск 7500..10500 мкс) + пауза 4500 мкс (допуск 3800..5200 мкс).
- **Код повтору (Repeat code)**: пачка 9000 мкс + пауза 2250 мкс (допуск 1800..2700 мкс) + імпульс 560 мкс.
- **Логічний 0**: пачка 560 мкс + пауза 560 мкс (разом 1125 мкс; допуск інтервалу паузи 400..750 мкс).
- **Логічна 1**: пачка 560 мкс + пауза 1690 мкс (разом 2250 мкс; допуск інтервалу паузи 1400..2000 мкс).

Оскільки вихід інтегрованого фотоприймача TSOP є інверсним (*Active-Low*), під час передачі оптичної світлової пачки на виводі мікроконтролера утримується низький рівень `0` (LOW), а під час світлової паузи — високий рівень `1` (HIGH).

Для роботи приймача апаратний таймер налаштовується в режим підрахунку мікросекунд (тактування 1 МГц за допомогою подільника Prescaler). Кожен логічний перепад на піні запускає канал захоплення (Input Capture), який автоматично копіює поточне значення лічильника таймера (CNT) в регістр захоплення/порівняння (CCR, англ. *Capture/Compare Register*) та генерує апаратне переривання.

Застосування вхідного захоплення замість опитування піна в циклі (англ. *Polling*) критично важливе: затримка реакції процесора на переривання або затримки виконання інших підпрограм не спотворюють виміряну мітку часу `timestamp`, оскільки апаратний лічильник фіксує момент перепаду на кремнієвому рівні з точністю до одного такту.

### 2. Реалізація драйвера: C та C++

Нижче наведено заголовочні файли інтерфейсу драйвера.

:::tabs
```c
/* nec_transceiver.h - Драйвер протоколу NEC на мові C */
#ifndef NEC_TRANSCEIVER_H
#define NEC_TRANSCEIVER_H

#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t address;
    uint8_t address_inv;
    uint8_t command;
    uint8_t command_inv;
    bool is_repeat;
} nec_packet_t;

typedef enum {
    NEC_RX_STATE_IDLE,
    NEC_RX_STATE_LEADER_BURST,
    NEC_RX_STATE_LEADER_SPACE,
    NEC_RX_STATE_BIT_PULSE,
    NEC_RX_STATE_BIT_SPACE
} nec_rx_state_t;

typedef struct {
    nec_rx_state_t state;
    uint32_t last_capture_us;
    uint32_t raw_data;
    uint8_t bit_index;
    nec_packet_t packet;
    bool packet_ready;
} nec_receiver_t;

void nec_receiver_init(nec_receiver_t *rx);
void nec_receiver_on_edge(nec_receiver_t *rx, uint32_t timestamp_us, bool pin_state);
bool nec_receiver_get_packet(nec_receiver_t *rx, nec_packet_t *out_packet);

#endif /* NEC_TRANSCEIVER_H */
```
```cpp
// nec_transceiver.hpp - Драйвер протоколу NEC на мові C++
#pragma once

#include <cstdint>
#include <optional>
#include <span>

namespace ir {

struct NecPacket {
    uint8_t address{0};
    uint8_t address_inv{0};
    uint8_t command{0};
    uint8_t command_inv{0};
    bool is_repeat{false};

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return (address == static_cast<uint8_t>(~address_inv)) &&
               (command == static_cast<uint8_t>(~command_inv));
    }
};

class NecDecoder {
public:
    enum class State : uint8_t {
        Idle,
        LeaderBurst,
        LeaderSpace,
        BitPulse,
        BitSpace
    };

    constexpr NecDecoder() noexcept = default;

    // Викликається в обробнику переривання захоплення входу
    void handle_edge(uint32_t timestamp_us, bool pin_state) noexcept;

    // Опитування наявності декодованого пакета в головному циклі
    [[nodiscard]] std::optional<NecPacket> pop_packet() noexcept;

    void reset() noexcept {
        state_ = State::Idle;
        raw_data_ = 0;
        bit_index_ = 0;
        ready_packet_.reset();
    }

private:
    State state_{State::Idle};
    uint32_t last_timestamp_us_{0};
    uint32_t raw_data_{0};
    uint8_t bit_index_{0};
    std::optional<NecPacket> ready_packet_{};
};

} // namespace ir
```
:::

### 3. Алгоритм кінцевого автомата декодера (FSM)

Обробник переривання обчислює тривалість кожного інтервалу через різницю міток часу `Δt = timestamp - last_timestamp`. Вхідний фільтр ігнорує паразитні сплески тривалістю менше 150 мкс, які виникають при перемиканні потужних індуктивних навантажень у мережі.

Декодер обробляє кожну фазу протоколу відповідно до графу станів:
1. `Idle` → перехід у `LeaderBurst` при першому спаді напруги (початок світлового спалаху преамбули).
2. `LeaderBurst` → перевірка тривалості пачки (допуск `7.5..10.5 мс`). Якщо інтервал коректний, переходимо в `LeaderSpace`, інакше — скидання в `Idle`.
3. `LeaderSpace` → якщо пауза становить `3.8..5.2 мс`, починається прийом 32 бітів кадру. Якщо пауза становить `1.8..2.7 мс`, фіксується прийом коду повтору (Repeat).
4. `BitPulse` та `BitSpace` → почергове вимірювання спалаху (560 мкс) та паузи (560 мкс для нуля, 1690 мкс для одиниці). При накопиченні 32 бітів здійснюється верифікація інверсних полів.

:::tabs
```c
/* nec_transceiver.c - Реалізація автомата станів декодера */
#include "nec_transceiver.h"

void nec_receiver_init(nec_receiver_t *rx) {
    rx->state = NEC_RX_STATE_IDLE;
    rx->last_capture_us = 0;
    rx->raw_data = 0;
    rx->bit_index = 0;
    rx->packet_ready = false;
}

void nec_receiver_on_edge(nec_receiver_t *rx, uint32_t timestamp_us, bool pin_state) {
    uint32_t duration = timestamp_us - rx->last_capture_us;
    rx->last_capture_us = timestamp_us;

    switch (rx->state) {
        case NEC_RX_STATE_IDLE:
            if (!pin_state) { // Спад у LOW: початок світлової пачки
                rx->state = NEC_RX_STATE_LEADER_BURST;
            }
            break;

        case NEC_RX_STATE_LEADER_BURST:
            if (pin_state) { // Наростання у HIGH: кінець пачки 9 мс
                if (duration >= 7500 && duration <= 10500) {
                    rx->state = NEC_RX_STATE_LEADER_SPACE;
                } else {
                    rx->state = NEC_RX_STATE_IDLE;
                }
            }
            break;

        case NEC_RX_STATE_LEADER_SPACE:
            if (!pin_state) { // Спад у LOW: кінець паузи преамбули
                if (duration >= 3800 && duration <= 5200) {
                    // Стандартний кадр даних
                    rx->raw_data = 0;
                    rx->bit_index = 0;
                    rx->state = NEC_RX_STATE_BIT_PULSE;
                } else if (duration >= 1800 && duration <= 2700) {
                    // Код повтору (Repeat code)
                    rx->packet.is_repeat = true;
                    rx->packet_ready = true;
                    rx->state = NEC_RX_STATE_IDLE;
                } else {
                    rx->state = NEC_RX_STATE_IDLE;
                }
            }
            break;

        case NEC_RX_STATE_BIT_PULSE:
            if (pin_state) { // Наростання у HIGH: кінець бітового спалаху 560 мкс
                if (duration >= 350 && duration <= 750) {
                    rx->state = NEC_RX_STATE_BIT_SPACE;
                } else {
                    rx->state = NEC_RX_STATE_IDLE;
                }
            }
            break;

        case NEC_RX_STATE_BIT_SPACE:
            if (!pin_state) { // Спад у LOW: вимірювання тривалості паузи
                if (duration >= 400 && duration <= 750) {
                    // Логічний 0 (пауза ~560 мкс)
                    rx->bit_index++;
                } else if (duration >= 1400 && duration <= 2000) {
                    // Логічна 1 (пауза ~1690 мкс)
                    rx->raw_data |= ((uint32_t)1 << rx->bit_index);
                    rx->bit_index++;
                } else {
                    rx->state = NEC_RX_STATE_IDLE;
                    break;
                }

                if (rx->bit_index >= 32) {
                    // Прийнято всі 32 біти кадру
                    rx->packet.address     = (uint8_t)(rx->raw_data & 0xFF);
                    rx->packet.address_inv = (uint8_t)((rx->raw_data >> 8) & 0xFF);
                    rx->packet.command     = (uint8_t)((rx->raw_data >> 16) & 0xFF);
                    rx->packet.command_inv = (uint8_t)((rx->raw_data >> 24) & 0xFF);
                    rx->packet.is_repeat   = false;

                    // Валідація цілісності
                    if ((rx->packet.address == (uint8_t)~rx->packet.address_inv) &&
                        (rx->packet.command == (uint8_t)~rx->packet.command_inv)) {
                        rx->packet_ready = true;
                    }
                    rx->state = NEC_RX_STATE_IDLE;
                } else {
                    rx->state = NEC_RX_STATE_BIT_PULSE;
                }
            }
            break;
    }
}

bool nec_receiver_get_packet(nec_receiver_t *rx, nec_packet_t *out_packet) {
    if (rx->packet_ready) {
        *out_packet = rx->packet;
        rx->packet_ready = false;
        return true;
    }
    return false;
}
```
```cpp
// nec_transceiver.cpp - Реалізація C++ декодера
#include "nec_transceiver.hpp"

namespace ir {

void NecDecoder::handle_edge(uint32_t timestamp_us, bool pin_state) noexcept {
    const uint32_t duration = timestamp_us - last_timestamp_us_;
    last_timestamp_us_ = timestamp_us;

    switch (state_) {
        case State::Idle:
            if (!pin_state) {
                state_ = State::LeaderBurst;
            }
            break;

        case State::LeaderBurst:
            if (pin_state) {
                if (duration >= 7500 && duration <= 10500) {
                    state_ = State::LeaderSpace;
                } else {
                    state_ = State::Idle;
                }
            }
            break;

        case State::LeaderSpace:
            if (!pin_state) {
                if (duration >= 3800 && duration <= 5200) {
                    raw_data_ = 0;
                    bit_index_ = 0;
                    state_ = State::BitPulse;
                } else if (duration >= 1800 && duration <= 2700) {
                    ready_packet_ = NecPacket{.is_repeat = true};
                    state_ = State::Idle;
                } else {
                    state_ = State::Idle;
                }
            }
            break;

        case State::BitPulse:
            if (pin_state) {
                if (duration >= 350 && duration <= 750) {
                    state_ = State::BitSpace;
                } else {
                    state_ = State::Idle;
                }
            }
            break;

        case State::BitSpace:
            if (!pin_state) {
                if (duration >= 400 && duration <= 750) {
                    // Логічний 0
                    ++bit_index_;
                } else if (duration >= 1400 && duration <= 2000) {
                    // Логічна 1
                    raw_data_ |= (1UL << bit_index_);
                    ++bit_index_;
                } else {
                    state_ = State::Idle;
                    break;
                }

                if (bit_index_ >= 32) {
                    NecPacket pkt{
                        .address     = static_cast<uint8_t>(raw_data_ & 0xFF),
                        .address_inv = static_cast<uint8_t>((raw_data_ >> 8) & 0xFF),
                        .command     = static_cast<uint8_t>((raw_data_ >> 16) & 0xFF),
                        .command_inv = static_cast<uint8_t>((raw_data_ >> 24) & 0xFF),
                        .is_repeat   = false
                    };

                    if (pkt.is_valid()) {
                        ready_packet_ = pkt;
                    }
                    state_ = State::Idle;
                } else {
                    state_ = State::BitPulse;
                }
            }
            break;
    }
}

std::optional<NecPacket> NecDecoder::pop_packet() noexcept {
    if (ready_packet_.has_value()) {
        auto pkt = ready_packet_;
        ready_packet_.reset();
        return pkt;
    }
    return std::nullopt;
}

} // namespace ir
```
:::

### 4. Генератор передавача 38 кГц (PWM Carrier Gating)

Для формування вихідного сигналу передавача апаратний таймер мікроконтролера налаштовується на частоту ШІМ `38 кГц` (період `T = 26.32 мкс`) зі шпаруватістю `33%` (час відкритого стану ключа `8.77 мкс`). Керування пачками здійснюється вмиканням/вимиканням вихідного каналу таймера (Timer Output Enable).

Під час вимкнення передавача вихідний пін переводиться в пасивний низький рівень (LOW), що закриває транзисторний ключ і повністю знеструмлює світлодіод.

:::tabs
```c
/* nec_tx.c - Генерація пачок передавача */
#include <stdint.h>
#include <stdbool.h>

// Апаратні функції керування ШІМ таймера
extern void timer_pwm_carrier_enable(void);
extern void timer_pwm_carrier_disable(void);
extern void delay_us(uint32_t us);

void nec_tx_send_burst(uint32_t burst_us, uint32_t space_us) {
    timer_pwm_carrier_enable();
    delay_us(burst_us);
    timer_pwm_carrier_disable();
    if (space_us > 0) {
        delay_us(space_us);
    }
}

void nec_tx_send_frame(uint8_t address, uint8_t command) {
    uint32_t raw = (uint32_t)address |
                   ((uint32_t)(~address & 0xFF) << 8) |
                   ((uint32_t)command << 16) |
                   ((uint32_t)(~command & 0xFF) << 24);

    // 1. Преамбула (Leader)
    nec_tx_send_burst(9000, 4500);

    // 2. Передача 32 бітів даних (LSB first)
    for (uint8_t i = 0; i < 32; i++) {
        if (raw & ((uint32_t)1 << i)) {
            // Біт '1': 560 мкс пачка + 1690 мкс пауза
            nec_tx_send_burst(560, 1690);
        } else {
            // Біт '0': 560 мкс пачка + 560 мкс пауза
            nec_tx_send_burst(560, 560);
        }
    }

    // 3. Завершальний стоп-імпульс
    nec_tx_send_burst(560, 0);
}
```
```cpp
// nec_tx.hpp - Генератор кадру C++ з RAII контролем носія
#pragma once

#include <cstdint>

namespace ir {

class NecTransmitter {
public:
    explicit NecTransmitter(void (*enable_carrier)(), void (*disable_carrier)(), void (*delay_func)(uint32_t))
        : enable_carrier_{enable_carrier}, disable_carrier_{disable_carrier}, delay_us_{delay_func} {}

    void send_frame(uint8_t address, uint8_t command) const {
        const uint32_t raw = static_cast<uint32_t>(address) |
                            (static_cast<uint32_t>(static_cast<uint8_t>(~address)) << 8) |
                            (static_cast<uint32_t>(command) << 16) |
                            (static_cast<uint32_t>(static_cast<uint8_t>(~command)) << 24);

        // Преамбула
        send_burst(9000, 4500);

        // 32 біти даних
        for (uint8_t i = 0; i < 32; ++i) {
            if (raw & (1UL << i)) {
                send_burst(560, 1690); // Біт '1'
            } else {
                send_burst(560, 560);  // Біт '0'
            }
        }

        // Кінцевий маркер
        send_burst(560, 0);
    }

    void send_repeat() const {
        send_burst(9000, 2250);
        send_burst(560, 0);
    }

private:
    void send_burst(uint32_t burst_us, uint32_t space_us) const {
        enable_carrier_();
        delay_us_(burst_us);
        disable_carrier_();
        if (space_us > 0) {
            delay_us_(space_us);
        }
    }

    void (*enable_carrier_)();
    void (*disable_carrier_)();
    void (*delay_us_)(uint32_t);
};

} // namespace ir
```
:::

### 5. Крайові випадки та типові апаратні пастки

1. **Переповнення лічильника таймера мікросекунд**. При використанні 16-бітного лічильника таймера з частотою тактування 1 МГц переповнення настає кожні `65535 мкс = 65.535 мс`. Завдяки властивостям беззнакової модульної арифметики (доповнення до двійки `uint16_t`) обчислення різниці `(uint16_t)(current_time - last_time)` дає математично точний результат навіть при переході через нуль (наприклад, `0x0010 - 0xFFF0 = 0x0020 = 32 мкс`). Проте якщо між імпульсами минає більше одного повного періоду переповнення (стан простою лінії), лічильник встигає обернутися кілька разів. Для захисту від хибних спрацьовувань програмний автомат повинен контролювати тайм-аут: якщо лінія утримується в стані `HIGH` понад `20..30 мс`, автомат FSM безумовно скидається в стан `Idle`.

2. **Розтягування імпульсів у TSOP (Pulse Stretching)**. Внутрішній смуговий фільтр та інтегратор фотоприймача мають кінцевий час перехідного процесу. Через добротність фільтра (`Q ≈ 15`) перший імпульс пачки з'являється на виході TSOP із запізненням на `3..5 періодів` (близько 100 мкс), а після зникнення оптичного сигналу коливання в контурі згасають ще протягом `2..4 періодів`. У результаті вихідний імпульс низького рівня (LOW) на виході TSOP завжди довший за номінальний на `50..120 мкс`. Алгоритм декодера повинен вимірювати повний інтервал між спадними перепадами (*Falling-to-Falling edge*) або закладати широкий асиметричний допуск на тривалість спалаху.

3. **Хибні повтори при «деренчанні» пульта**. При утриманні клавіші пульт NEC надсилає код повтору кожні `110 мс`. Якщо користувач швидко відпустив клавішу, але наклався оптичний шум, прапорець `is_repeat` запобігає хибному багаторазовому виконанню критичних команд (наприклад, перемикання каналів або зміни гучності).

4. **Діагностика через логічний аналізатор**. Під час налагодження протоколу на лінію `OUT` приймача підключають цифровий логічний аналізатор. Якщо тривалість паузи логічної одиниці плаває в межах `1300..1800 мкс`, це свідчить про зміщення тактової частоти передавача (наприклад, використання неточного внутрішнього RC-генератора замість кварцового резонатора). Відхилення частоти ШІМ передавача понад `±5%` (тобто вихід за діапазон `36.1..39.9 кГц`) призводить до падіння амплітуди на виході смугового фільтра TSOP більш ніж на `6 дБ`, що скорочує дальність прийому вдвічі.
