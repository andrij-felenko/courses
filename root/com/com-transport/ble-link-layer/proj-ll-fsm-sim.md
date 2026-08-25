# ⚙️ Симуляція канального рівня BLE: кінцевий автомат, таймінги та протокол ARQ

Канальний рівень (Link Layer) бездротового стека Bluetooth Low Energy виконує синхронізацію в мікросекундному масштабі часу, керує перемиканням станів радіомодуля та забезпечує гарантовану доставку даних поверх фізично ненадійного ефіру. На відміну від протоколів вищих рівнів (L2CAP, ATT, GATT), які працюють із абстрактними буферами та дескрипторами пам'яті, код канального рівня безпосередньо взаємодіє з апаратними таймерами захоплення/порівняння, регістрами радіотрансивера та обчислювачем контрольної суми CRC.

Розглянемо практичну програмну модель ключових механізмів Link Layer: кінцевого автомата станів, розрахунку часового вікна розширення прийому (*Window Widening*) через температурний дрейф кварцового генератора та апаратного протоколу підтвердження й повторної передачі Stop-and-Wait ARQ із бітами `SN` та `NESN`.

---

## 1. Архітектурна модель симулятора та апаратний контекст

У реальних мікроконтролерах із підтримкою BLE (наприклад, лінійках Nordic Semiconductor nRF52/nRF53, Texas Instruments CC26xx або Espressif ESP32-C3/S3) канальний рівень Link Layer виконується з найвищим пріоритетом переривань апаратного контролера NVIC (*Nested Vectored Interrupt Controller*) або реалізується на окремому виділеному апаратному процесорі зв'язку (Cortex-M0+ / RISC-V).

Така архітектура обумовлена жорсткими вимогами реального часу:
* Міжкадровий інтервал `T_IFS = 150 ± 1 мкс` не залишає часу на виклик диспетчера операційної системи (RTOS) чи повільну обробку черг.
* Будь-яка затримка ввімкнення передавача чи приймача призводить до втрати синхронізації та аварійного розірвання зв'язку за таймаутом нагляду (*Supervision Timeout*).

На реальному кристалі зв'язок між подіями радіотракту та таймерами здійснюється апаратними каналами прямого зв'язку периферії (наприклад, система PPI/DPPI у чіпах Nordic). Подія готовності радіотрансивера `EVENTS_READY` автоматично через апаратну шину запускає завдання відправки `TASKS_START`, а подія завершення передачі `EVENTS_END` запускає апаратний таймер для точного відліку 150 мкс до моменту ввімкнення приймача `TASKS_RXEN`.

Розроблена симуляція моделює поведінку цього апаратного радіотракту та логіки Link Layer на чотирьох функціональних рівнях:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      Архітектурні шари симулятора                        │
├──────────────────────────────────────────────────────────────────────────┤
│ 1. Кінцевий автомат (FSM): перемикання Standby, Adv, Scan, Init, Conn   │
├──────────────────────────────────────────────────────────────────────────┤
│ 2. Модуль таймінгів: розрахунок Anchor Points та Window Widening         │
├──────────────────────────────────────────────────────────────────────────┤
│ 3. Протокол контролю потоку: Stop-and-Wait ARQ (біти SN, NESN, MD)       │
├──────────────────────────────────────────────────────────────────────────┤
│ 4. Апаратна верифікація цілісності: 24-бітний LFSR обчислювач CRC        │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Кінцевий автомат та інваріанти станів

Кінцевий автомат Link Layer відстежує життєвий цикл радіовузла. Стан визначає, які апаратні ресурси активні в поточний момент:

* `STANDBY`: радіотрансивер вимкнений, енергоспоживання мінімальне, працює лише таймер сну RTC (32.768 кГц).
* `ADVERTISING`: трансивер періодично прокидається для передачі пакетів `ADV_IND` на каналах 37, 38, 39 і короткочасно слухає відповіді.
* `SCANNING`: приймач увімкнений на рекламних каналах у пасивному чи активному режимі.
* `INITIATING`: приймач шукає конкретну адресу для надсилання кадру `CONNECT_IND`.
* `CONNECTION_MASTER`: вузол є ведучим сесії, задає часову сітку Anchor Points, першим передає дані на каналі зв'язку.
* `CONNECTION_SLAVE`: вузол є веденим, прокидається перед очікуваним приходом сигналу від Master і відповідає через `T_IFS = 150 мкс`.

---

## 3. Математика дрейфу годинника та розширення вікна прийому

У стані глибокого сну між подіями зв'язку мікроконтролери обох пристроїв синхронізуються за низькочастотними кварцовими генераторами 32.768 кГц. Похибка частоти таких кристалів задається параметром точності сну **SCA** (*Sleep Clock Accuracy*) у частинах на мільйон (**ppm**, $10^{-6}$).

Коли ведений засинає на час `t_sleep` (який із урахуванням дозволеної затримки `connSlaveLatency` може становити кілька секунд), різниця ходу кварців Master та Slave призводить до накопичення невизначеності моменту початку наступної події зв'язку.

Сумарна невизначеність часу `windowWidening` обчислюється як:

```
windowWidening = (SCA_master + SCA_slave) · t_sleep + 16 мкс
```

де додаткові 16 мкс враховують апаратний фазовий джиттер низькочастотного таймера та затримку виходу мікроконтролера з режиму глибокого сну.

Ведений пристрій зобов'язаний відкрити свій радіоприймач на `windowWidening` мікросекунд раніше розрахункового часу `Anchor Point` і тримати його відкритим довше. Якщо знехтувати цим розрахунком, ведений запізниться з увімкненням приймача і пропустить преамбулу кадру Master, що призведе до розриву зв'язку.

---

## 4. Логіка протоколу Stop-and-Wait ARQ та інваріанти бітів SN / NESN

Контроль надійної доставки та усунення дублікатів реалізовано через однобітний прапорець чергування:

```
                                 Діаграма станів ARQ
                                          │
       Відправник                                                Приймач
       ──────────                                                ───────
       1. Формує пакет:                                          2. Очікує пакет:
          SN = transmitSeqNum                                       Очікуваний номер = nextExpectedSeqNum
          NESN = nextExpectedSeqNum                                 │
          │                                                         ▼
          ▼                                              CRC валідна та SN == expected?
       Випромінює в ефір ───────────────────────────────► ┌─────────┴─────────┐
                                                          │                   │
                                                          ▼ ТАК               ▼ НІ (CRC помилка або дублікат)
                                                    Приймає дані        Відкидає тіло кадру
                                                    nextExpectedSeqNum  nextExpectedSeqNum
                                                      = 1 - nextExpected  НЕ змінюється
                                                          │                   │
                                                          └─────────┬─────────┘
                                                                    │
                                                                    ▼
       Отримує відповідь: ◄────────────────────────────── Відправляє ACK/NACK:
       Перевіряє NESN                                        NESN = nextExpectedSeqNum
       │
       ▼
    Отриманий NESN != transmitSeqNum?
    ┌─────────┴─────────┐
    │                   │
    ▼ ТАК (ACK)         ▼ НІ (NACK / таймаут)
  Пакет доставлено    Повторна відправка
  transmitSeqNum        того самого пакета
    = 1 - transmit      з тим самим SN
```

### Інваріанти поведінки:
1. **Підтвердження успіху (ACK):** Приймач інвертує свій біт `nextExpectedSeqNum` лише тоді, коли прийняв непошкоджений пакет із правильним `SN`. Отримавши відповідь із новим `NESN`, відправник інвертує свій `transmitSeqNum`, дозволяючи перехід до наступного блоку даних.
2. **Негативна квитанція (NACK):** У разі пошкодження CRC приймач залишає свій `nextExpectedSeqNum` незмінним. У відповіді він надсилає старий `NESN`, що сигналізує відправнику про необхідність ретрансмісії.
3. **Захист від дублікатів:** Якщо підтвердження ACK втрачено в ефірі, відправник повторно надішле старий пакет із тим самим `SN`. Приймач помітить, що `SN != nextExpectedSeqNum`, відкине дублікат, але повторно надішле актуальний `NESN`, щоб вивести відправника зі стану блокування.

---

## 5. Програмна реалізація симулятора

Нижче наведено повний вихідний код симулятора двома мовами програмування: стандартною мовою C (C99/C11) та сучасним стандартом C++20 з використанням безпечних типів даних, RAII та `std::span`.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Константи специфікації BLE Core 5.4 */
#define BLE_CRC24_POLY        0x00065Bu
#define BLE_CRC24_INIT        0x555555u
#define BLE_T_IFS_US          150u
#define BLE_MAX_PAYLOAD_LEN   251u

/* Стани кінцевого автомата Link Layer */
typedef enum {
    LL_STATE_STANDBY = 0,
    LL_STATE_ADVERTISING,
    LL_STATE_SCANNING,
    LL_STATE_INITIATING,
    LL_STATE_CONNECTION_MASTER,
    LL_STATE_CONNECTION_SLAVE
} ll_state_t;

/* Структура пакету каналу даних Data Channel PDU */
typedef struct {
    uint8_t llid : 2;
    uint8_t nesn : 1;
    uint8_t sn   : 1;
    uint8_t md   : 1;
    uint8_t rfu  : 3;
    uint8_t length;
    uint8_t payload[BLE_MAX_PAYLOAD_LEN];
    uint32_t crc;
} ll_data_pdu_t;

/* Стан вузла зв'язку */
typedef struct {
    ll_state_t state;
    uint8_t transmit_sn;     /* Останній надісланий Sequence Number */
    uint8_t next_expected_sn;/* Очікуваний наступний Sequence Number */
    uint16_t sca_ppm;        /* Точність кварцу сну в ppm */
    uint32_t conn_interval_us;
    uint16_t slave_latency;
    uint32_t supervision_timeout_ms;
} ll_node_t;

/* Обчислення контрольної суми CRC-24 по бітах (LFSR) */
static uint32_t ble_crc24_calc(const uint8_t *data, size_len_t len, uint32_t crc_init) {
    uint32_t state = crc_init & 0x00FFFFFFu;
    for (size_t i = 0; i < len; ++i) {
        uint8_t byte = data[i];
        for (int bit = 0; bit < 8; ++bit) {
            uint8_t data_bit = (byte >> bit) & 1u;
            uint8_t state_bit23 = (state >> 23) & 1u;
            state = ((state << 1) & 0x00FFFFFFu);
            if (data_bit ^ state_bit23) {
                state ^= BLE_CRC24_POLY;
            }
        }
    }
    return state & 0x00FFFFFFu;
}

/* Розрахунок розширення вікна прийому через дрейф кварцу (Window Widening) */
static uint32_t calc_window_widening_us(uint16_t master_sca_ppm, uint16_t slave_sca_ppm, uint32_t sleep_time_us) {
    uint64_t total_drift_ppm = (uint64_t)master_sca_ppm + (uint64_t)slave_sca_ppm;
    /* window_widening = (master_drift + slave_drift) * sleep_time + 16 мкс (jitter) */
    uint32_t drift_us = (uint32_t)((total_drift_ppm * sleep_time_us) / 1000000ULL);
    return drift_us + 16u;
}

/* Формування кадру для передачі */
static void ll_build_pdu(ll_node_t *node, ll_data_pdu_t *pdu, const uint8_t *payload, uint8_t len, bool more_data) {
    pdu->llid = 0x02; /* 10b: Start of L2CAP message */
    pdu->sn = node->transmit_sn;
    pdu->nesn = node->next_expected_sn;
    pdu->md = more_data ? 1 : 0;
    pdu->rfu = 0;
    pdu->length = len;
    memcpy(pdu->payload, payload, len);

    /* Серіалізація заголовка та розрахунок CRC */
    uint8_t raw[BLE_MAX_PAYLOAD_LEN + 2];
    raw[0] = (uint8_t)(pdu->llid | (pdu->nesn << 2) | (pdu->sn << 3) | (pdu->md << 4));
    raw[1] = pdu->length;
    memcpy(&raw[2], pdu->payload, len);

    pdu->crc = ble_crc24_calc(raw, (size_t)(len + 2), BLE_CRC24_INIT);
}

/* Обробка отриманого кадру на приймачі */
static bool ll_receive_pdu(ll_node_t *receiver, const ll_data_pdu_t *pdu, bool simulate_crc_error) {
    uint8_t raw[BLE_MAX_PAYLOAD_LEN + 2];
    raw[0] = (uint8_t)(pdu->llid | (pdu->nesn << 2) | (pdu->sn << 3) | (pdu->md << 4));
    raw[1] = pdu->length;
    memcpy(&raw[2], pdu->payload, pdu->length);

    uint32_t expected_crc = ble_crc24_calc(raw, (size_t)(pdu->length + 2), BLE_CRC24_INIT);
    if (simulate_crc_error || pdu->crc != expected_crc) {
        printf("  [Rx] Помилка CRC! Пакет відкинуто. Очікуваний NESN лишається %u\n", receiver->next_expected_sn);
        return false;
    }

    /* Якщо SN збігається з очікуваним — це новий пакет */
    if (pdu->sn == receiver->next_expected_sn) {
        printf("  [Rx] Прийнято НОВИЙ пакет [SN=%u, NESN=%u, len=%u]: \"%.*s\"\n",
               pdu->sn, pdu->nesn, pdu->length, pdu->length, pdu->payload);
        /* Змінюємо NESN для підтвердження успішного прийому */
        receiver->next_expected_sn = (uint8_t)(1u - receiver->next_expected_sn);
    } else {
        printf("  [Rx] Прийнято ДУБЛІКАТ [SN=%u]. Повторно підтверджуємо поточний стан.\n", pdu->sn);
    }

    /* Перевіряємо підтвердження наших переданих даних (ACK від сусіда) */
    if (pdu->nesn != receiver->transmit_sn) {
        receiver->transmit_sn = (uint8_t)(1u - receiver->transmit_sn);
    }
    return true;
}

int main(void) {
    ll_node_t master = {
        .state = LL_STATE_CONNECTION_MASTER,
        .transmit_sn = 0,
        .next_expected_sn = 0,
        .sca_ppm = 50,
        .conn_interval_us = 20000, /* 20.0 мс */
        .slave_latency = 4,
        .supervision_timeout_ms = 2000
    };

    ll_node_t slave = {
        .state = LL_STATE_CONNECTION_SLAVE,
        .transmit_sn = 0,
        .next_expected_sn = 0,
        .sca_ppm = 250,
        .conn_interval_us = 20000,
        .slave_latency = 4,
        .supervision_timeout_ms = 2000
    };

    printf("=== СИМУЛЯТОР BLE LINK LAYER (ARQ & TIMINGS) ===\n\n");

    /* 1. Розрахунок дрейфу вікна */
    uint32_t sleep_time_us = master.conn_interval_us * (master.slave_latency + 1);
    uint32_t widening_us = calc_window_widening_us(master.sca_ppm, slave.sca_ppm, sleep_time_us);
    printf("[1] Розрахунок вікна розширення (Window Widening):\n");
    printf("    connInterval = %u мкс, Slave Latency = %u\n", master.conn_interval_us, master.slave_latency);
    printf("    Час сну Slave = %u мкс\n", sleep_time_us);
    printf("    Спільний дрейф = %u ppm -> Розширення вікна прийому = %u мкс\n\n",
           master.sca_ppm + slave.sca_ppm, widening_us);

    /* 2. Передача пакету 1 (Успішно) */
    printf("[2] Подія 1: Master передає пакет 1 -> Slave:\n");
    ll_data_pdu_t pdu1;
    const char *msg1 = "Hello BLE";
    ll_build_pdu(&master, &pdu1, (const uint8_t *)msg1, (uint8_t)strlen(msg1), false);
    printf("  [Tx Master] Пакет відправлено: SN=%u, NESN=%u, CRC=0x%06X\n", pdu1.sn, pdu1.nesn, pdu1.crc);
    ll_receive_pdu(&slave, &pdu1, false);

    /* Відповідь Slave (ACK) */
    ll_data_pdu_t ack1;
    ll_build_pdu(&slave, &ack1, NULL, 0, false);
    printf("  [Tx Slave]  Відповідь ACK:     SN=%u, NESN=%u, CRC=0x%06X\n", ack1.sn, ack1.nesn, ack1.crc);
    ll_receive_pdu(&master, &ack1, false);
    printf("\n");

    /* 3. Передача пакету 2 (Зіпсовано завадою) */
    printf("[3] Подія 2: Master передає пакет 2 (симуляція завади в ефірі):\n");
    ll_data_pdu_t pdu2;
    const char *msg2 = "Data block 2";
    ll_build_pdu(&master, &pdu2, (const uint8_t *)msg2, (uint8_t)strlen(msg2), false);
    printf("  [Tx Master] Пакет відправлено: SN=%u, NESN=%u, CRC=0x%06X\n", pdu2.sn, pdu2.nesn, pdu2.crc);
    ll_receive_pdu(&slave, &pdu2, true); /* Симуляція пошкодження CRC */

    /* Slave надсилає старий NESN (NACK) */
    ll_data_pdu_t nack;
    ll_build_pdu(&slave, &nack, NULL, 0, false);
    printf("  [Tx Slave]  Відповідь NACK:    SN=%u, NESN=%u (NESN не перемкнуто)\n", nack.sn, nack.nesn);
    ll_receive_pdu(&master, &nack, false);
    printf("\n");

    /* 4. Повторна передача пакету 2 (Retransmit) */
    printf("[4] Подія 3: Master фіксує незмінний NESN та повторює пакет 2:\n");
    ll_build_pdu(&master, &pdu2, (const uint8_t *)msg2, (uint8_t)strlen(msg2), false);
    printf("  [Tx Master] Retransmit:        SN=%u, NESN=%u, CRC=0x%06X\n", pdu2.sn, pdu2.nesn, pdu2.crc);
    ll_receive_pdu(&slave, &pdu2, false);

    /* Slave підтверджує успіх */
    ll_build_pdu(&slave, &ack1, NULL, 0, false);
    printf("  [Tx Slave]  Відповідь ACK:     SN=%u, NESN=%u\n", ack1.sn, ack1.nesn);
    ll_receive_pdu(&master, &ack1, false);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <cstdint>
#include <optional>
#include <iomanip>

namespace ble::ll {

constexpr uint32_t Crc24Poly = 0x00065Bu;
constexpr uint32_t Crc24Init = 0x555555u;
constexpr uint32_t TIfsUs = 150u;
constexpr size_t MaxPayloadLen = 251;

enum class State {
    Standby,
    Advertising,
    Scanning,
    Initiating,
    ConnectionMaster,
    ConnectionSlave
};

struct DataPdu {
    uint8_t llid{0x02}; /* 10b: Start of L2CAP message */
    uint8_t nesn{0};
    uint8_t sn{0};
    uint8_t md{0};
    uint8_t length{0};
    std::vector<uint8_t> payload{};
    uint32_t crc{0};
};

/* Обчислення контрольної суми CRC-24 (LFSR) через std::span */
[[nodiscard]] constexpr uint32_t calculate_crc24(std::span<const uint8_t> data, uint32_t init = Crc24Init) noexcept {
    uint32_t state = init & 0x00FFFFFFu;
    for (uint8_t byte : data) {
        for (int bit = 0; bit < 8; ++bit) {
            uint8_t data_bit = (byte >> bit) & 1u;
            uint8_t state_bit23 = (state >> 23) & 1u;
            state = (state << 1) & 0x00FFFFFFu;
            if (data_bit ^ state_bit23) {
                state ^= Crc24Poly;
            }
        }
    }
    return state & 0x00FFFFFFu;
}

/* Розрахунок розширення вікна прийому */
[[nodiscard]] constexpr uint32_t calculate_window_widening(uint16_t master_ppm, uint16_t slave_ppm, uint32_t sleep_time_us) noexcept {
    const uint64_t total_ppm = static_cast<uint64_t>(master_ppm) + static_cast<uint64_t>(slave_ppm);
    const auto drift = static_cast<uint32_t>((total_ppm * sleep_time_us) / 1'000'000ULL);
    return drift + 16u; /* +16 мкс захисного джиттеру */
}

class LinkLayerNode {
public:
    explicit LinkLayerNode(State initial_state, uint16_t sca_ppm, uint32_t interval_us, uint16_t latency = 0)
        : state_{initial_state}, sca_ppm_{sca_ppm}, conn_interval_us_{interval_us}, slave_latency_{latency} {}

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] uint8_t transmit_sn() const noexcept { return transmit_sn_; }
    [[nodiscard]] uint8_t next_expected_sn() const noexcept { return next_expected_sn_; }
    [[nodiscard]] uint16_t sca_ppm() const noexcept { return sca_ppm_; }
    [[nodiscard]] uint32_t conn_interval_us() const noexcept { return conn_interval_us_; }
    [[nodiscard]] uint16_t slave_latency() const noexcept { return slave_latency_; }

    [[nodiscard]] DataPdu build_pdu(std::string_view payload_str, bool more_data = false) {
        DataPdu pdu{};
        pdu.llid = 0x02;
        pdu.sn = transmit_sn_;
        pdu.nesn = next_expected_sn_;
        pdu.md = more_data ? 1 : 0;
        pdu.length = static_cast<uint8_t>(payload_str.size());
        pdu.payload.assign(payload_str.begin(), payload_str.end());

        std::vector<uint8_t> raw_header_and_payload;
        raw_header_and_payload.reserve(2 + pdu.payload.size());
        raw_header_and_payload.push_back(static_cast<uint8_t>(pdu.llid | (pdu.nesn << 2) | (pdu.sn << 3) | (pdu.md << 4)));
        raw_header_and_payload.push_back(pdu.length);
        raw_header_and_payload.insert(raw_header_and_payload.end(), pdu.payload.begin(), pdu.payload.end());

        pdu.crc = calculate_crc24(raw_header_and_payload);
        return pdu;
    }

    bool receive_pdu(const DataPdu& pdu, bool simulate_crc_error = false) {
        std::vector<uint8_t> raw;
        raw.reserve(2 + pdu.payload.size());
        raw.push_back(static_cast<uint8_t>(pdu.llid | (pdu.nesn << 2) | (pdu.sn << 3) | (pdu.md << 4)));
        raw.push_back(pdu.length);
        raw.insert(raw.end(), pdu.payload.begin(), pdu.payload.end());

        const uint32_t expected_crc = calculate_crc24(raw);
        if (simulate_crc_error || pdu.crc != expected_crc) {
            std::cout << "  [Rx] Помилка CRC! Пакет відкинуто. Очікуваний NESN лишається "
                      << static_cast<int>(next_expected_sn_) << "\n";
            return false;
        }

        if (pdu.sn == next_expected_sn_) {
            std::string_view msg{reinterpret_cast<const char*>(pdu.payload.data()), pdu.payload.size()};
            std::cout << "  [Rx] Прийнято НОВИЙ пакет [SN=" << static_cast<int>(pdu.sn)
                      << ", NESN=" << static_cast<int>(pdu.nesn) << ", len=" << static_cast<int>(pdu.length)
                      << "]: \"" << msg << "\"\n";
            next_expected_sn_ = static_cast<uint8_t>(1u - next_expected_sn_);
        } else {
            std::cout << "  [Rx] Прийнято ДУБЛІКАТ [SN=" << static_cast<int>(pdu.sn)
                      << "]. Повторно підтверджуємо поточний стан.\n";
        }

        if (pdu.nesn != transmit_sn_) {
            transmit_sn_ = static_cast<uint8_t>(1u - transmit_sn_);
        }
        return true;
    }

private:
    State state_{State::Standby};
    uint8_t transmit_sn_{0};
    uint8_t next_expected_sn_{0};
    uint16_t sca_ppm_{50};
    uint32_t conn_interval_us_{20000};
    uint16_t slave_latency_{0};
};

} // namespace ble::ll

int main() {
    using namespace ble::ll;

    LinkLayerNode master{State::ConnectionMaster, 50, 20000, 4};
    LinkLayerNode slave{State::ConnectionSlave, 250, 20000, 4};

    std::cout << "=== СИМУЛЯТОР BLE LINK LAYER (C++20 RAII & ARQ) ===\n\n";

    const uint32_t sleep_time_us = master.conn_interval_us() * (master.slave_latency() + 1);
    const uint32_t widening_us = calculate_window_widening(master.sca_ppm(), slave.sca_ppm(), sleep_time_us);

    std::cout << "[1] Розрахунок вікна розширення (Window Widening):\n"
              << "    connInterval = " << master.conn_interval_us() << " мкс, Slave Latency = " << master.slave_latency() << "\n"
              << "    Час сну Slave = " << sleep_time_us << " мкс\n"
              << "    Спільний дрейф = " << (master.sca_ppm() + slave.sca_ppm())
              << " ppm -> Розширення вікна прийому = " << widening_us << " мкс\n\n";

    /* Подія 1: Успішна передача */
    std::cout << "[2] Подія 1: Master передає пакет 1 -> Slave:\n";
    auto pdu1 = master.build_pdu("Hello BLE C++");
    std::cout << "  [Tx Master] Пакет відправлено: SN=" << static_cast<int>(pdu1.sn)
              << ", NESN=" << static_cast<int>(pdu1.nesn) << ", CRC=0x"
              << std::hex << std::uppercase << std::setfill('0') << std::setw(6) << pdu1.crc << std::dec << "\n";
    slave.receive_pdu(pdu1, false);

    auto ack1 = slave.build_pdu("");
    std::cout << "  [Tx Slave]  Відповідь ACK:     SN=" << static_cast<int>(ack1.sn)
              << ", NESN=" << static_cast<int>(ack1.nesn) << "\n";
    master.receive_pdu(ack1, false);
    std::cout << "\n";

    /* Подія 2: Помилка CRC */
    std::cout << "[3] Подія 2: Master передає пакет 2 (симуляція завади в ефірі):\n";
    auto pdu2 = master.build_pdu("Data block 2");
    std::cout << "  [Tx Master] Пакет відправлено: SN=" << static_cast<int>(pdu2.sn)
              << ", NESN=" << static_cast<int>(pdu2.nesn) << "\n";
    slave.receive_pdu(pdu2, true);

    auto nack = slave.build_pdu("");
    std::cout << "  [Tx Slave]  Відповідь NACK:    SN=" << static_cast<int>(nack.sn)
              << ", NESN=" << static_cast<int>(nack.nesn) << " (NESN не перемкнуто)\n";
    master.receive_pdu(nack, false);
    std::cout << "\n";

    /* Подія 3: Повторна передача */
    std::cout << "[4] Подія 3: Master фіксує незмінний NESN та повторює пакет 2:\n";
    pdu2 = master.build_pdu("Data block 2");
    std::cout << "  [Tx Master] Retransmit:        SN=" << static_cast<int>(pdu2.sn)
              << ", NESN=" << static_cast<int>(pdu2.nesn) << "\n";
    slave.receive_pdu(pdu2, false);

    ack1 = slave.build_pdu("");
    std::cout << "  [Tx Slave]  Відповідь ACK:     SN=" << static_cast<int>(ack1.sn)
              << ", NESN=" << static_cast<int>(ack1.nesn) << "\n";
    master.receive_pdu(ack1, false);

    return 0;
}
```
:::

---

## 6. Покроковий розбір сценаріїв роботи симулятора

Програма симулює три типові послідовності обміну даними між вузлами зв'язку:

### Сценарій 1: Успішна пряма доставка (Подія 1)
1. Ведучий формує кадр із рядком `"Hello BLE"`: встановлює `SN = 0` та `NESN = 0` (підтверджуючи нульовий очікуваний кадр від Slave). Обчислюється контрольна сума `CRC-24`.
2. Ведений отримує пакет, перевіряє цілісність (успішно), бачить `SN == 0`, що збігається з його очікуваним `next_expected_sn = 0`. Він передає рядок прикладному рівню та інвертує свій лічильник: `next_expected_sn = 1`.
3. Ведений формує порожній пакет підтвердження `ACK`, де вказує `NESN = 1` (очікую наступний пакет із номером 1) та `SN = 0`.
4. Ведучий приймає `ACK`, бачить `NESN == 1 != transmit_sn (0)`, що свідчить про успішне підтвердження попередньої відправки, та інвертує свій `transmit_sn = 1`.

### Сценарій 2: Втрата кадру через спотворення CRC (Подія 2)
1. Ведучий надсилає новий блок даних `"Data block 2"` із оновленим номером `SN = 1` та `NESN = 0`.
2. У каналі зв'язку симулюється завада: на приймачі прапорець `simulate_crc_error = true` викликає невідповідність контрольної суми.
3. Ведений виявляє апаратну помилку CRC і негайно відкидає пакет: тіло кадру ігнорується, а лічильник очікування залишається незмінним (`next_expected_sn = 1`).
4. Ведений надсилає службову відповідь із старим значенням `NESN = 1` (неявний NACK).
5. Ведучий приймає відповідь, виявляє, що повернутий `NESN (1)` збігається з його `transmit_sn (1)`. Це означає, що кадр не був доставлений, тому ведучий залишає `transmit_sn = 1` і готує повторну передачу.

### Сценарій 3: Повторна передача (Retransmission, Подія 3)
1. На наступному Anchor Point ведучий повторно випромінює той самий блок `"Data block 2"` із збереженим `SN = 1`.
2. За відсутності завад ведений успішно валідує CRC, бачить очікуваний `SN == 1`, приймає корисні дані та перемикає лічильник очікування: `next_expected_sn = 0`.
3. Ведений надсилає підтвердження `NESN = 0`, розблоковуючи ведучого для передачі нових даних.

---

## 7. Порівняння C та C++ реалізацій та керування пам'яттю

Під час розробки сучасних стеків зв'язку для вбудованих систем вибір між C та C++ визначається архітектурними пріоритетами проекту:

1. **Керування пам'яттю та буферизація:**
   * У варіанті на C структура `ll_data_pdu_t` використовує фіксований статичний масив `uint8_t payload[BLE_MAX_PAYLOAD_LEN]`. Це унеможливлює динамічну фрагментацію пам'яті (*heap fragmentation*) у ядрі мікроконтролера, проте вимагає виділення максимального обсягу пам'яті (251 байт) під кожен буфер передавача та приймача.
   * У реалізації на C++20 клас `LinkLayerNode` оперує легковагими неволодіючими представленнями пам'яті `std::string_view` та `std::span<const uint8_t>`. Це дозволяє передавати дані у функцію формування кадру `build_pdu` без зайвого копіювання байтів із прикладних структур або буферів флеш-пам'яті (*zero-copy architecture*).

2. **Безпека типів та інкапсуляція:**
   * У коді на C++ стани автомата строго типізовані через `enum class State`, що запобігає випадковому неявному приведенню цілих чисел або змішуванню стану радіомодуля з числовими кодами помилок.
   * Модифікатор `[[nodiscard]]` для методів `calculate_crc24` та `build_pdu` на рівні компілятора гарантує, що розробник не проігнорує обчислений результат контрольної суми або сформований пакет.

---

## 8. Методологія апаратного налагодження та профілювання Link Layer

При перенесенні програмної логіки на реальні мікроконтролери розробники використовують спеціалізовані інструменти апаратного аналізу:

1. **Профілювання через GPIO та логічний аналізатор:**
   Найпростіший і найнадійніший спосіб перевірити дотримання міжкадрового інтервалу `T_IFS = 150 мкс` — перемикання апаратних ніжок GPIO на початку та в кінці обробників переривань радіомодуля (`RADIO_IRQHandler`). Підключивши 8-канальний логічний аналізатор із частотою дискретизації 24–100 МГц (Saleae Logic або аналог), інженер візуалізує:
   * Момент запуску високочастотного кварцу (HFXO).
   * Точний час переходу трансивера з Tx у Rx.
   * Тривалість виконання розрахунку CRC-24 та шифрування AES-CCM.

2. **Аналіз радіоефіру за допомогою BLE-сніфера:**
   Використання спеціалізованого апаратного USB-донгла з прошивкою сніфера (наприклад, Nordic nRF Sniffer або професійні комплекси Ellisys / Teledyne LeCroy) у поєднанні з аналізатором трафіку Wireshark дозволяє перехоплювати пакети на рівні радіоканалу. Сніфер показує:
   * Значення бітів `SN`, `NESN` та `MD` у кожному кадровому фреймі.
   * Помилки контрольної суми CRC та факт їхньої ретрансмісії.
   * Зсув точок прив'язки `Anchor Points` та динаміку зміни `connInterval`.

3. **Осцилографічний аналіз струму споживання:**
   Підключення прецизійного вимірювача струму (Power Profiler Kit II або аналогічний джерело-вимірювач SMU) дає змогу виміряти споживання струму під час події з'єднання. На осцилограмі чітко розрізняються фази: пробудження мікроконтролера (~3 мА), увімкнення приймача (~6–10 мА), імпульс випромінювання передавача (~8–15 мА) та повернення в режим сну Standby зі струмом менше 2 мкА.

---

## 9. Розрахунок енергетичного бюджету для автономного сенсора

Розглянемо практичний розрахунок середнього струму споживання та тривалості автономної роботи бездротового датчика від літієвого дискового елемента CR2032 номінальною ємністю `C_bat = 220 мА·год` при напрузі 3.0 В.

Нехай датчик налаштовано з параметрами:
* `connInterval = 1000 мс` (1.0 с).
* `connSlaveLatency = 4` (велений відповідає лише за наявності нових вимірювань або кожну 5-ту подію з'єднання, тобто раз на 5.0 с у стані спокою).
* Струм у режимі глибокого сну Standby: `I_sleep = 1.8 мкА`.
* Тривалість активної фази події з'єднання (пробудження, розширення вікна `windowWidening`, прийом кадру Master та передача 20-байтного звіту телеметрії): `t_active = 2.5 мс` при середньому струмі `I_active = 8.5 мА`.

Електричний заряд `Q_event`, що витрачається за одну подію зв'язку:

```
Q_event = I_active · t_active = 8.5 мА · 0.0025 с = 0.02125 мА·с (21.25 мкКл)
```

У стані спокою подія зв'язку відбувається раз на `T_period = connInterval · (1 + connSlaveLatency) = 5.0 с`. Середній струм споживання `I_avg` становить:

```
I_avg = (Q_event / T_period) + I_sleep
      = (0.02125 мА·с / 5.0 с) + 0.0018 мА
      = 0.00425 мА + 0.0018 мА = 0.00605 мА = 6.05 мкА
```

Розрахуємо теоретичний термін служби батареї з урахуванням 15% запасу на саморозряд елемента за кілька років:

```
T_life = (0.85 · C_bat) / I_avg
       = (0.85 · 220 мА·год) / 0.00605 мА
       = 187 мА·год / 0.00605 мА ≈ 30909 годин ≈ 3.53 роки
```

Цей розрахунок наочно демонструє, як механізм Slave Latency у поєднанні з жорсткими мікросекундними таймінгами Link Layer дозволяє пристрою працювати понад три з половиною роки від мініатюрної батарейки.

---

## 10. Механізм Connection Subrating (Bluetooth 5.3+) та латентність доставки

У класичному BLE перехід між режимом енергозбереження (великий `connSlaveLatency`) та режимом активної передачі вимагав повноцінної процедури `LL_CONNECTION_UPDATE_IND`, яка займала від кількох сотень мілісекунд до секунд через необхідність безпечного призначення лічильника `Instant`.

Починаючи з версії Bluetooth 5.3, стандартизовано процедуру **Connection Subrating**, яка дозволяє динамічно змінювати кратність пропуску подій зв'язку за один міжкадровий обмін. Ведений може миттєво тимчасово вимкнути латентність (*subrate factor*) під час появи пакета в локальному буфері і передавати дані на кожному базовому `connInterval`, а після спустошення буфера — автоматично повернутися в енергозберігаючий ритм.

Математичне очікування затримки доставки кадру `E[T_delivery]` за наявності випадкових радіозавад із ймовірністю бітової помилки `p` розраховується за геометричним розподілом кількості ретрансмісій:

```
E[T_delivery] = connInterval / (1 - p)
```

При ймовірності втрати пакету `p = 0.1` (10% Packet Error Rate) середній час доставки зростає лише на 11%, тоді як при `p = 0.5` — подвоюється, що підкреслює критичну роль швидкої ретрансмісії в алгоритмі Stop-and-Wait ARQ.

---

## 11. Інженерні пастки реалізації таймінгів та протоколу ARQ

Під час практичної розробки вбудованого ПЗ та драйверів Link Layer для мікроконтролерів інженери часто припускаються типових помилок:

1. **Неправильний розрахунок `windowWidening`:** Якщо розробник ігнорує власний дрейф кварцу Slave або не враховує накопичений дрейф під час тривалого сну з увімкненим `Slave Latency`, приймач відкривається пізніше, ніж передає Master. Результат — регулярні пропуски перших пакетів та аварійне розірвання зв'язку за `connSupervisionTimeout`.
2. **Передчасне перемикання `SN` на відправнику:** Якщо передавач перемикає `SN` до того, як отримає пакет із інвертованим `NESN`, втрачений пакет замінюється новим. Це призводить до невиправної втрати байтів у потоці L2CAP без генерації апаратної помилки.
3. **Порушення міжкадрового інтервалу `T_IFS`:** Радіомодуль повинен перемкнутися з режиму передачі (Tx) у режим прийому (Rx) рівно за `150 ± 1` мкс. Якщо обробка переривання в мікроконтролері блокується іншими задачами з вищим пріоритетом і затримує ввімкнення приймача хоча б на 2 мкс, пакет буде пропущений.
4. **Некоректна ініціалізація `CRCInit`:** Якщо під час встановлення зв'язку початкове значення регістру CRC не синхронізоване між Master та Slave, кожен надісланий пакет відхилятиметься приймачем як пошкоджений, що призведе до розриву зв'язку одразу після отримання `CONNECT_IND`.
5. **Апаратні колізії прямого доступу до пам'яті (DMA):** Якщо мікроконтролер модифікує буфер передачі в той самий момент, коли апаратний блок радіотрансивера зчитує байти через DMA (регістр `PACKETPTR`), CRC-24 буде обчислено над частково зміненими даними. Буфери передачі повинні блокуватися подвійним буферизуванням (*ping-pong buffers*) до отримання позитивного підтвердження `ACK`.
6. **Блокування переривань іншими драйверами:** Виклик довгих критичних секцій (`__disable_irq()`) у драйверах Flash-пам'яті або дисплеїв блокує переривання радіомодуля. Будь-яка критична секція, що триває довше 50–100 мкс під час активної події зв'язку, зриває жорсткий розклад Link Layer.
7. **Тестування на рівні безперервної інтеграції (CI/CD):** Оскільки фізичний радіоефір важко автоматизувати у віртуальних середовищах, розробники вбудованих BLE-стеків запускають подібні симулятори у збірках unit-тестів на хост-машині. Це дозволяє симулювати мільйони циклів ARQ із заданими розподілами завад, перевіряючи відсутність взаємних блокувань і витоків пам'яті до прошивки коду в реальний кремній. Такий підхід скорочує цикл виправлення регресій та гарантує стабільність канального рівня перед сертифікацією виробу в Bluetooth SIG.
