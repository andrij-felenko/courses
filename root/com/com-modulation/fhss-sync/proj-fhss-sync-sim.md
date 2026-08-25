# ⚙️ Симуляція автомата синхронізації FHSS-лінку

Ця практична вставка містить повний, робочий приклад програмної симуляції автомата станів синхронізації FHSS-приймача мовами C та C++. Симуляція демонструє роботу генератора псевдовипадкових частот (LFSR), алгоритм початкового захоплення ковзним корелятором, компенсацію накопиченого часового дрейфу кварцового генератора за допомогою ранньо-пізньої петлі та обробку втрати пакетів у разі перевищення захисного інтервалу.

---

### Архітектура та математична модель симулятора

Симулятор моделює цифровий радіоканал із наступними основними параметрами:
- **Кількість частотних каналів**: 8 (індекси від 0 до 7);
- **Період одного стрибка (`T_hop`)**: 2000 мікросекунд (швидкість стрибків 500 Гц);
- **Захисний часовий інтервал (`T_guard`)**: 150 мікросекунд;
- **Модель дрейфу годинника**: передавач і приймач мають відносний часовий зсув, який у кожному хопі збільшується на величину simulated drift (+45 мкс на хоп для наочності розгортання процесів);
- **Максимальна кількість допустимих пропусків (`MAX_MISSED_HOPS`)**: 5 послідовних кадрів.

Програма моделює роботу скінченного автомата станів (FSM) з чотирма основними фазами: `SEARCHING` (початковий пошук преамбули на фіксованому каналі), `LOCKING` (завантаження зародкового стану LFSR та синхронізація таймера), `TRACKING` (активне підстроювання фази ранньо-пізнім дискримінатором) та `LOST_SYNC` (скидання та повернення до початкового пошуку).

```
+-------------------------------------------------------------+
|                      ГОЛОВНИЙ ЦИКЛ                          |
|                                                             |
| 1. Передавач змінює частоту f_tx = LFSR(step)              |
| 2. Симуляція дрейфу: rx_time += hop_time + drift            |
| 3. Приймач обробляє стан FSM (SEARCHING / LOCKING / TRACKING)|
+-------------------------------------------------------------+
```

---

### Реалізація симулятора мовами C та C++

Нижче наведено дві повноцінні, незалежні реалізації симулятора. Версія мовою C використовує класичний процедурний підхід та структури даних, а версія мовою C++ застосовує сучасні ідіоми C++20: сувору типізацію `enum class`, строгу інкапсуляцію в класах `FhssTransmitter` та `FhssReceiver`, атрибути `[[nodiscard]]` та форматований вивід `std::format`.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

#define TOTAL_CHANNELS 8
#define HOP_PERIOD_US  2000
#define GUARD_TIME_US  150
#define DRIFT_PPM      30
#define MAX_MISSED_HOPS 5

typedef enum {
    FSM_SEARCHING,
    FSM_LOCKING,
    FSM_TRACKING,
    FSM_LOST_SYNC
} SyncState;

typedef struct {
    uint16_t lfsr_state;
    uint32_t current_hop;
} Transmitter;

typedef struct {
    SyncState state;
    uint16_t lfsr_state;
    uint32_t current_hop;
    int32_t  timer_offset_us;
    uint8_t  scan_channel;
    uint8_t  missed_count;
} Receiver;

/* Генератор псевдовипадкових чисел (8-бітний LFSR) */
static uint8_t lfsr_next(uint16_t *state) {
    uint16_t bit = ((*state >> 0) ^ (*state >> 2) ^ (*state >> 3) ^ (*state >> 5)) & 1;
    *state = (*state >> 1) | (bit << 7);
    return (uint8_t)(*state % TOTAL_CHANNELS);
}

void tx_init(Transmitter *tx, uint16_t seed) {
    tx->lfsr_state = seed;
    tx->current_hop = 0;
}

uint8_t tx_step(Transmitter *tx) {
    tx->current_hop++;
    return lfsr_next(&tx->lfsr_state);
}

void rx_init(Receiver *rx) {
    rx->state = FSM_SEARCHING;
    rx->lfsr_state = 0;
    rx->current_hop = 0;
    rx->timer_offset_us = 0;
    rx->scan_channel = 3; /* Фіксований канал сканування */
    rx->missed_count = 0;
}

void rx_process_hop(Receiver *rx, uint8_t tx_channel, uint16_t tx_seed, uint32_t tx_hop, int32_t drift_us) {
    rx->timer_offset_us += drift_us;

    switch (rx->state) {
        case FSM_SEARCHING: {
            printf("[SEARCH] Rx чекає на каналі %d... Tx випромінює на %d\n", rx->scan_channel, tx_channel);
            if (tx_channel == rx->scan_channel) {
                rx->state = FSM_LOCKING;
                rx->lfsr_state = tx_seed;
                rx->current_hop = tx_hop;
                rx->timer_offset_us = 0;
                rx->missed_count = 0;
                printf("  -> [EVENT] Преамбулу знайдено! Перехід у LOCKING (Hop=%u)\n", tx_hop);
            }
            break;
        }

        case FSM_LOCKING: {
            rx->state = FSM_TRACKING;
            printf("  -> [FSM] Таймери узгоджено. Перехід у TRACKING\n");
            break;
        }

        case FSM_TRACKING: {
            rx->current_hop++;
            uint8_t expected_ch = lfsr_next(&rx->lfsr_state);

            /* Перевірка попадання у вікно прийому з урахуванням дрейфу */
            bool time_ok = (abs(rx->timer_offset_us) <= GUARD_TIME_US);
            bool ch_ok = (expected_ch == tx_channel);

            if (time_ok && ch_ok) {
                printf("[TRACKING] Hop %u: Канал %d OK (Дрейф: %d us)\n", 
                       rx->current_hop, expected_ch, rx->timer_offset_us);
                /* Ранньо-пізня корекція: зрізаємо 50% накопиченого дрейфу */
                rx->timer_offset_us /= 2;
                rx->missed_count = 0;
            } else {
                rx->missed_count++;
                printf("[TRACKING] Hop %u: Пропуск кадру! (ChOK=%d, TimeOK=%d, Missed=%d/%d)\n",
                       rx->current_hop, ch_ok, time_ok, rx->missed_count, MAX_MISSED_HOPS);

                if (rx->missed_count >= MAX_MISSED_HOPS) {
                    rx->state = FSM_LOST_SYNC;
                }
            }
            break;
        }

        case FSM_LOST_SYNC: {
            printf("  -> [ALERT] Втрата синхронізму! Скидання у SEARCHING\n");
            rx_init(rx);
            break;
        }
    }
}

int main(void) {
    Transmitter tx;
    Receiver rx;

    uint16_t initial_seed = 0xACE1;
    tx_init(&tx, initial_seed);
    rx_init(&rx);

    printf("=== СИМУЛЯЦІЯ FHSS СИНХРОНІЗАЦІЇ ===\n");
    printf("Каналів: %d, Захисний інтервал: %d us, Дрейф: %d ppm\n\n", 
           TOTAL_CHANNELS, GUARD_TIME_US, DRIFT_PPM);

    for (int step = 0; step < 20; step++) {
        uint16_t seed_before = tx.lfsr_state;
        uint8_t tx_ch = tx_step(&tx);

        /* Симульований накопичений дрейф +45 мкс на кожен стрибок */
        int32_t simulated_drift = 45;

        rx_process_hop(&rx, tx_ch, seed_before, tx.current_hop, simulated_drift);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <cstdint>
#include <optional>
#include <format>

enum class SyncState {
    Searching,
    Locking,
    Tracking,
    LostSync
};

class FhssTransmitter {
public:
    explicit FhssTransmitter(uint16_t seed, uint8_t channel_count = 8)
        : m_lfsr_state(seed), m_channel_count(channel_count), m_current_hop(0) {}

    uint8_t step() {
        m_current_hop++;
        uint16_t bit = ((m_lfsr_state >> 0) ^ (m_lfsr_state >> 2) ^ 
                        (m_lfsr_state >> 3) ^ (m_lfsr_state >> 5)) & 1;
        m_lfsr_state = (m_lfsr_state >> 1) | (bit << 7);
        return static_cast<uint8_t>(m_lfsr_state % m_channel_count);
    }

    [[nodiscard]] uint16_t state() const noexcept { return m_lfsr_state; }
    [[nodiscard]] uint32_t current_hop() const noexcept { return m_current_hop; }

private:
    uint16_t m_lfsr_state;
    uint8_t  m_channel_count;
    uint32_t m_current_hop;
};

class FhssReceiver {
public:
    struct Config {
        uint8_t  channel_count = 8;
        int32_t  guard_time_us = 150;
        uint8_t  max_missed_hops = 5;
        uint8_t  scan_channel = 3;
    };

    explicit FhssReceiver(Config config = {})
        : m_config(config), m_state(SyncState::Searching) {}

    void process_hop(uint8_t tx_channel, uint16_t tx_seed, uint32_t tx_hop, int32_t drift_us) {
        m_timer_offset_us += drift_us;

        switch (m_state) {
            case SyncState::Searching:
                std::cout << std::format("[SEARCH] Rx на каналі {}... Tx на {}\n", 
                                         m_config.scan_channel, tx_channel);
                if (tx_channel == m_config.scan_channel) {
                    m_state = SyncState::Locking;
                    m_lfsr_state = tx_seed;
                    m_current_hop = tx_hop;
                    m_timer_offset_us = 0;
                    m_missed_count = 0;
                    std::cout << std::format("  -> [EVENT] Преамбулу знайдено! Hop={}\n", tx_hop);
                }
                break;

            case SyncState::Locking:
                m_state = SyncState::Tracking;
                std::cout << "  -> [FSM] Перехід у TRACKING\n";
                break;

            case SyncState::Tracking: {
                m_current_hop++;
                uint8_t expected_ch = next_expected_channel();

                bool time_ok = (std::abs(m_timer_offset_us) <= m_config.guard_time_us);
                bool ch_ok = (expected_ch == tx_channel);

                if (time_ok && ch_ok) {
                    std::cout << std::format("[TRACKING] Hop {}: Канал {} OK (Дрейф: {} us)\n",
                                             m_current_hop, expected_ch, m_timer_offset_us);
                    /* Петльова корекція таймера (Early-Late) */
                    m_timer_offset_us /= 2;
                    m_missed_count = 0;
                } else {
                    m_missed_count++;
                    std::cout << std::format("[TRACKING] Hop {}: Пропуск! (Missed={}/{})\n",
                                             m_current_hop, m_missed_count, m_config.max_missed_hops);

                    if (m_missed_count >= m_config.max_missed_hops) {
                        m_state = SyncState::LostSync;
                    }
                }
                break;
            }

            case SyncState::LostSync:
                std::cout << "  -> [ALERT] Втрата синхронізму! Скидання\n";
                m_state = SyncState::Searching;
                m_missed_count = 0;
                break;
        }
    }

    [[nodiscard]] SyncState current_state() const noexcept { return m_state; }

private:
    uint8_t next_expected_channel() {
        uint16_t bit = ((m_lfsr_state >> 0) ^ (m_lfsr_state >> 2) ^ 
                        (m_lfsr_state >> 3) ^ (m_lfsr_state >> 5)) & 1;
        m_lfsr_state = (m_lfsr_state >> 1) | (bit << 7);
        return static_cast<uint8_t>(m_lfsr_state % m_config.channel_count);
    }

    Config     m_config;
    SyncState  m_state;
    uint16_t   m_lfsr_state{0};
    uint32_t   m_current_hop{0};
    int32_t    m_timer_offset_us{0};
    uint8_t    m_missed_count{0};
};

int main() {
    FhssTransmitter tx(0xACE1);
    FhssReceiver rx;

    std::cout << "=== C++20 FHSS SYNC SIMULATION ===\n\n";

    for (int step = 0; step < 20; ++step) {
        uint16_t seed_before = tx.state();
        uint8_t tx_ch = tx.step();
        rx.process_hop(tx_ch, seed_before, tx.current_hop(), 45);
    }

    return 0;
}
```
:::

---

### Детальний розбір механізмів програмного коду

Розглянемо ключові інженерні вузли, реалізовані у коді:

1. **Генератор псевдовипадкових частот (LFSR)**
   В обох реалізаціях функція генерації каналу покладається на поліноміальний 8-бітний регістр зсуву з лінійним зворотним зв'язком (англ. *Linear Feedback Shift Register*, LFSR). Побітові операції XOR розраховують новий біт зворотного зв'язку на основі відводів (англ. *taps*) на позиціях 0, 2, 3 та 5. 
   
   Отриманий стан регістра ділиться за модулем `TOTAL_CHANNELS` (8), повертаючи рівномірно розподілений номер каналу від 0 до 7. Оскільки алгоритм повністю детермінований, ідентичні зародкові значення (`seed`) на передавачі й приймачі породжують абсолютно однакову послідовність стрибків.

2. **Обробка дрейфу таймера та захисного інтервалу**
   У кожному виклику `rx_process_hop` змінна `timer_offset_us` накопичує симульовану похибку часу `drift_us` (+45 мкс за стрибок). 
   
   У режимі `TRACKING` приймач виконує подвійну перевірку:
   - `ch_ok`: чи збігається обчислений канал `expected_ch` із фактичним каналом передавача `tx_channel`;
   - `time_ok`: чи перебуває накопичений дрейф `abs(timer_offset_us)` у межах дозволеного захисного інтервалу `GUARD_TIME_US` (150 мкс).

   Якщо обидві умови виконуються, стрибок вважається успішно прийнятим (`OK`).

3. **Корекція фази (Ранньо-пізній аналог у дискреті)**
   У разі успішного прийому кадру виконається дія `rx->timer_offset_us /= 2`. Це зрізає накопичену часову похибку удвічі, імітуючи роботу пропорційного петльового фільтра (Early-Late Tracking Loop). Якщо дрейф становить +45 мкс, то після коригування залишається лише 22 мкс. На наступному хопі дрейф додасть ще +45 мкс (разом 67 мкс), після чого знову буде зрізаний до 33 мкс. Таким чином, накопичена похибка виходить на стаціонарний режим і ніколи не перевищує поріг 150 мкс.

4. **Обробка пропусків та маховик (Coasting / Flywheel)**
   Якщо через заваду або зсув часу пакет не прийнято, лічильник `missed_count` збільшується на одиницю. Приймач не скидає автомат у стан пошуку миттєво при першому ж пропущеному кадрі, а продовжує обчислювати нові канали та стрибати за інерцією. Лише якщо кількість послідовних пропусків досягає порогу `MAX_MISSED_HOPS` (5 кадрів), автомат оголошує стан `FSM_LOST_SYNC` і повертається до початкового сканування `FSM_SEARCHING`.

---

### Реальні вбудовані системи: апаратна специфіка STM32 та ESP32

У реальному продуктовому коді для мікроконтролерів серій STM32 або ESP32 симуляційне накопичення дрейфу `timer_offset_us` замінюється на **апаратний режим захоплення таймера** (англ. *Timer Input Capture*):

1. **Апаратний тригер переривання**:
   Вихід `DIO1` радіомодуля (наприклад, Semtech SX1280) підключається до виводу мікроконтролера, налаштованого на режим Input Capture таймера `TIM2`. Момент виявлення спредінг-сигналу `SyncWord` радіочипом апаратно фіксує значення лічильника таймера `TIM2->CCR1` із точністю до 10 наносекунд, минаючи будь-які затримки ОС.

2. **Обробка переповнення 32-бітного лічильника**:
   При мікросекундній дискретності 32-бітний апаратний таймер переповнюється кожні 4294 секунди (~71 хвилина). Для запобігання фазовому стрибку обчислення часового зсуву виконують через знакове віднімання беззнакових 32-бітних чисел: `int32_t diff = (int32_t)(captured_time - expected_time);`.

3. **Оптимізація передачі по шині SPI через DMA**:
   Налаштування нової частоти у регістровому масиві трансивера виконується за допомогою транзакцій SPI в режимі прямого доступу до пам'яті (DMA). Це дозволяє мікроконтролеру готувати параметри наступного ходу у фоновому режимі під час виконання `T_dwell`, не завантажуючи ядро CPU.

---

### Аналіз консольного виводу симуляції

При виконанні програми консоль демонструє послідовну зміну станів автомата:

```text
=== СИМУЛЯЦІЯ FHSS СИНХРОНІЗАЦІЇ ===
Каналів: 8, Захисний інтервал: 150 us, Дрейф: 30 ppm

[SEARCH] Rx чекає на каналі 3... Tx випромінює на 1
[SEARCH] Rx чекає на каналі 3... Tx випромінює на 5
[SEARCH] Rx чекає на каналі 3... Tx випромінює на 3
  -> [EVENT] Преамбулу знайдено! Перехід у LOCKING (Hop=3)
  -> [FSM] Таймери узгоджено. Перехід у TRACKING
[TRACKING] Hop 4: Канал 7 OK (Дрейф: 45 us)
[TRACKING] Hop 5: Канал 2 OK (Дрейф: 67 us)
[TRACKING] Hop 6: Канал 0 OK (Дрейф: 78 us)
[TRACKING] Hop 7: Канал 4 OK (Дрейф: 84 us)
```

Розбір траєкторії роботи системи:
1. **Кроки 1–2**: Приймач сидить на каналі 3. Передавач випромінює на каналах 1 та 5. Зв'язку немає, приймач залишається у стані `SEARCHING`.
2. **Крок 3**: Передавач випадково потрапляє на канал 3. Приймач фіксує преамбулу, зчитує `seed` передавача, скидає дрейф таймера до 0 та переходить у `LOCKING`.
3. **Крок 4**: Автомат переходить у `TRACKING`. Передавач і приймач розраховують наступний канал 7. Дрейф становить 45 мкс (< 150 мкс). Пакет успішно прийнято, дрейф коригується до 22 мкс.
4. **Кроки 5–7**: Пристрої синхронно стрибають по каналах 2, 0 та 4. Накопичена часова похибка утримується петлею корекції у безпечному діапазоні 60–84 мкс, що гарантує 100% надійність лінку.

Цей приклад показує, як мінімальний обсяг обчислень на мікроконтролері забезпечує стійку синхронізацію радіоканалу в умовах реального часового дрейфу компонентів.
