# ⚙️ Реалізація автоматів станів Go-Back-N та Selective Repeat

Неможливо повністю осягнути динаміку протоколів ковзного вікна, спираючись лише на теоретичні часові діаграми. Практична реалізація вимагає побудови дискретного асинхронного автомата станів, який керує кільцевими буферами відправника й одержувача, відстежує стан кожного байта в умовах непередбачуваної втрати пакетів і коректно обробляє таймаути в багатопотоковому або подійно-орієнтованому середовищі.

Ця практична вставка містить детальний розбір архітектури симулятора мережевого каналу, закінчені та повністю робочі реалізації протоколів Go-Back-N і Selective Repeat мовами C (стандарт C99) та C++ (сучасний стандарт C++20), покрокове трасування станів автоматів під час виникнення завад, опис високоефективних таймерних коліс (Timing Wheels), механіку дескрипторних кілець мережевих адаптерів (DMA Ring Buffers), алгоритм швидкого відновлення (Fast Retransmit) за трьома дубльованими ACK, вичерпну тестову матрицю валідації станів, детальний розбір інваріантів пам'яті, проектування асинхронних рушіїв на базі `io_uring`, оптимізацію кешу процесора (Data Locality & False Sharing) та аналіз типових інженерних пасток системного програмування.

---

## 1. Архітектурна модель симулятора та диспетчеризація подій

Для перевірки коректності протоколів ARQ у контрольованих умовах використовується модель дискретно-подійного симулятора (англ. *Discrete Event Simulator*). Замість використання реальних мережевих сокетів операційної системи, які вносять недетерміновані затримки планувальника ОС, симулятор оперує віртуальним системним часом (дискретними квантами — тіками).

Фізичний канал зв'язку моделюється як двонапрямлена черга з фіксованою затримкою поширення `T_prop` та ймовірністю спотворення або втрати пакета `p`.

```
   +-------------------------------------------------------------+
   |                Мережеве середовище (Channel)                 |
   |   - Черга пакетів у польоті (In-flight Queue)               |
   |   - Моделювання затримки поширення (Propagation Delay T_p)  |
   |   - Генератор псевдовипадкових втрат (Loss Rate p)          |
   +-------------------------------------------------------------+
               ▲                                   │
      TX Кадри │                                   ▼ RX Кадри
   +-----------+-------------+       +-------------+-----------+
   |  Передавач (Sender)     |       |  Приймач (Receiver)     |
   | - Кільцевий буфер вікна |       | - Буфер прийому (SR)    |
   | - Таймери очікування    |       | - Контроль очікування   |
   | - S_base, S_next        |       | - Віддача у стек додатку|
   +-------------------------+       +-------------------------+
```

### Основні типи повідомлень

1. **`FRAME_DATA`:** Інформаційний кадр, що містить порядковий номер `seq`, корисне навантаження та довжину даних.
2. **`FRAME_ACK`:** Службовий пакет позитивного підтвердження. У протоколі Go-Back-N номер `ack` означає найвищий послідовно отриманий номер (кумулятивне підтвердження), тоді як у Selective Repeat `ack` підтверджує отримання виключно зазначеного кадру (індивідуальний або селективний ACK).
3. **`FRAME_NACK`:** Службовий пакет негативного підтвердження для негайного запиту повторної передачі без очікування тайм-ауту.

---

## 2. Повна реалізація автоматів станів мовами C та C++

Нижче наведено паралельні реалізації симулятора та алгоритмів ковзного вікна. У вкладці C реалізовано процедурний підхід на статичних структурах даних без динамічного виділення пам'яті, що є стандартом для розробки прошивок мікроконтролерів (bare-metal). У вкладці C++ реалізовано об'єктно-орієнтовану модель із суворою типізацією, безпечними неволодіючими зрізами `std::span` та `std::string_view`, інкапсульованими класами передавача та приймача і автоматичним керуванням ресурсами (RAII).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_WINDOW_SIZE  16
#define SEQ_SPACE        32   /* M = 2^5 = 32, W <= 16 для SR */
#define PAYLOAD_SIZE     32
#define MAX_EVENTS       128

typedef enum {
    FRAME_DATA = 0,
    FRAME_ACK,
    FRAME_NACK
} FrameType;

typedef struct {
    FrameType type;
    uint8_t seq;
    uint8_t ack;
    uint8_t payload[PAYLOAD_SIZE];
    size_t length;
} Frame;

/* Кільцевий буфер передавача */
typedef struct {
    Frame frame;
    bool in_flight;
    bool acked;
    uint32_t sent_time;
    uint32_t timeout_time;
} TxSlot;

typedef struct {
    uint8_t window_size;
    uint8_t s_base;
    uint8_t s_next;
    uint32_t rto_ticks;
    TxSlot buffer[SEQ_SPACE];
} SenderGBN;

typedef struct {
    uint8_t r_expected;
    uint32_t packets_received;
} ReceiverGBN;

/* Обчислення модульної відстані на кільці */
static inline uint8_t mod_dist(uint8_t from, uint8_t to, uint8_t mod) {
    return (to - from + mod) % mod;
}

/* ─── Ініціалізація та методи Go-Back-N ─── */
void gbn_sender_init(SenderGBN *snd, uint8_t win_size, uint32_t rto) {
    snd->window_size = win_size;
    snd->s_base = 0;
    snd->s_next = 0;
    snd->rto_ticks = rto;
    memset(snd->buffer, 0, sizeof(snd->buffer));
}

bool gbn_sender_send(SenderGBN *snd, const uint8_t *data, size_t len, uint32_t current_time, Frame *out_frame) {
    uint8_t used = mod_dist(snd->s_base, snd->s_next, SEQ_SPACE);
    if (used >= snd->window_size) {
        return false; /* Вікно заповнене, передача неможлива */
    }

    uint8_t seq = snd->s_next;
    TxSlot *slot = &snd->buffer[seq];
    slot->frame.type = FRAME_DATA;
    slot->frame.seq = seq;
    slot->frame.ack = 0;
    slot->frame.length = len < PAYLOAD_SIZE ? len : PAYLOAD_SIZE;
    memcpy(slot->frame.payload, data, slot->frame.length);
    
    slot->in_flight = true;
    slot->acked = false;
    slot->sent_time = current_time;
    slot->timeout_time = current_time + snd->rto_ticks;

    *out_frame = slot->frame;
    snd->s_next = (snd->s_next + 1) % SEQ_SPACE;
    return true;
}

void gbn_sender_on_ack(SenderGBN *snd, uint8_t ack_seq) {
    /* Кумулятивний ACK: підтверджує всі кадри від s_base до ack_seq */
    uint8_t advance = mod_dist(snd->s_base, (ack_seq + 1) % SEQ_SPACE, SEQ_SPACE);
    uint8_t max_advance = mod_dist(snd->s_base, snd->s_next, SEQ_SPACE);

    if (advance > 0 && advance <= max_advance) {
        while (snd->s_base != (ack_seq + 1) % SEQ_SPACE) {
            snd->buffer[snd->s_base].in_flight = false;
            snd->buffer[snd->s_base].acked = true;
            snd->s_base = (snd->s_base + 1) % SEQ_SPACE;
        }
    }
}

int gbn_sender_check_timeouts(SenderGBN *snd, uint32_t current_time, Frame out_frames[], int max_out) {
    /* Якщо для s_base сплив таймаут — повторюємо ВСІ кадри від s_base до s_next */
    if (snd->s_base == snd->s_next) return 0;

    TxSlot *base_slot = &snd->buffer[snd->s_base];
    if (base_slot->in_flight && current_time >= base_slot->timeout_time) {
        int count = 0;
        uint8_t curr = snd->s_base;
        while (curr != snd->s_next && count < max_out) {
            snd->buffer[curr].sent_time = current_time;
            snd->buffer[curr].timeout_time = current_time + snd->rto_ticks;
            out_frames[count++] = snd->buffer[curr].frame;
            curr = (curr + 1) % SEQ_SPACE;
        }
        return count;
    }
    return 0;
}

/* ─── Приймач Go-Back-N ─── */
void gbn_receiver_init(ReceiverGBN *rcv) {
    rcv->r_expected = 0;
    rcv->packets_received = 0;
}

bool gbn_receiver_on_frame(ReceiverGBN *rcv, const Frame *f, Frame *out_ack) {
    if (f->type != FRAME_DATA) return false;

    if (f->seq == rcv->r_expected) {
        /* Отримано очікуваний кадр */
        rcv->packets_received++;
        out_ack->type = FRAME_ACK;
        out_ack->seq = 0;
        out_ack->ack = rcv->r_expected;
        out_ack->length = 0;
        rcv->r_expected = (rcv->r_expected + 1) % SEQ_SPACE;
        return true;
    } else {
        /* Невпорядкований кадр — відкидаємо, повторюємо старий ACK */
        if (rcv->packets_received > 0) {
            out_ack->type = FRAME_ACK;
            out_ack->seq = 0;
            out_ack->ack = (rcv->r_expected + SEQ_SPACE - 1) % SEQ_SPACE;
            out_ack->length = 0;
            return true;
        }
        return false;
    }
}

/* ─── Демонстраційний запуск симуляції ─── */
int main(void) {
    SenderGBN sender;
    ReceiverGBN receiver;
    gbn_sender_init(&sender, 4, 10); /* Вікно W = 4, RTO = 10 тіків */
    gbn_receiver_init(&receiver);

    printf("=== Симуляція протоколу Go-Back-N (C99) ===\n");
    for (int i = 0; i < 6; i++) {
        char msg[20];
        snprintf(msg, sizeof(msg), "DataBlock-%d", i);
        Frame f;
        if (gbn_sender_send(&sender, (uint8_t*)msg, strlen(msg), i * 2, &f)) {
            printf("[TX %u] Відправлено кадр Seq=%u (%s)\n", i * 2, f.seq, msg);
            
            /* Емуляція втрати кадру з Seq=1 */
            if (f.seq == 1) {
                printf("  [ВТРАТА] Кадр Seq=1 загубився в каналі зв'язку!\n");
                continue;
            }

            Frame ack;
            if (gbn_receiver_on_frame(&receiver, &f, &ack)) {
                printf("  [RX] Прийнято Seq=%u, надіслано ACK=%u\n", f.seq, ack.ack);
                gbn_sender_on_ack(&sender, ack.ack);
            }
        }
    }

    /* Симуляція спливання таймауту */
    printf("\n--- Спрацьовує таймаут RTO для кадру Seq=1 ---\n");
    Frame retrans[MAX_WINDOW_SIZE];
    int n = gbn_sender_check_timeouts(&sender, 25, retrans, MAX_WINDOW_SIZE);
    printf("Go-Back-N повторює %d кадрів починаючи з base=%u:\n", n, sender.s_base);
    for (int i = 0; i < n; i++) {
        printf("  [TX-RETRY] Повтор кадру Seq=%u\n", retrans[i].seq);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <optional>
#include <string>
#include <string_view>
#include <span>
#include <cstdint>
#include <algorithm>

namespace arq {

constexpr size_t kSeqSpace = 32;       // Потужність простору номерів M = 32
constexpr size_t kMaxPayload = 64;

enum class FrameType : uint8_t {
    Data,
    Ack,
    Nack
};

struct Frame {
    FrameType type{FrameType::Data};
    uint8_t seq{0};
    uint8_t ack{0};
    std::array<uint8_t, kMaxPayload> payload{};
    size_t length{0};

    [[nodiscard]] std::string_view AsStringView() const {
        return std::string_view(reinterpret_cast<const char*>(payload.data()), length);
    }
};

// Допоміжні функції модульної арифметики
[[nodiscard]] constexpr uint8_t ModDist(uint8_t from, uint8_t to, uint8_t mod = kSeqSpace) noexcept {
    return static_cast<uint8_t>((to - from + mod) % mod);
}

// ─────────────────────────────────────────────────────────────────────────────
// Selective Repeat Sender (Передавач із вибірковим повтором)
// ─────────────────────────────────────────────────────────────────────────────
class SelectiveRepeatSender {
public:
    struct Slot {
        Frame frame;
        bool in_flight{false};
        bool acked{false};
        uint32_t timeout_time{0};
    };

    explicit SelectiveRepeatSender(uint8_t window_size, uint32_t rto_ticks)
        : window_size_(window_size), rto_ticks_(rto_ticks) {
        if (window_size_ > kSeqSpace / 2) {
            throw std::invalid_argument("SR window size must not exceed M / 2");
        }
    }

    [[nodiscard]] bool CanSend() const noexcept {
        return ModDist(base_, next_seq_) < window_size_;
    }

    std::optional<Frame> Send(std::span<const uint8_t> data, uint32_t current_time) {
        if (!CanSend()) {
            return std::nullopt;
        }

        const uint8_t seq = next_seq_;
        auto& slot = buffer_[seq];
        slot.frame.type = FrameType::Data;
        slot.frame.seq = seq;
        slot.frame.ack = 0;
        slot.frame.length = std::min(data.size(), kMaxPayload);
        std::copy_n(data.data(), slot.frame.length, slot.frame.payload.begin());

        slot.in_flight = true;
        slot.acked = false;
        slot.timeout_time = current_time + rto_ticks_;

        next_seq_ = static_cast<uint8_t>((next_seq_ + 1) % kSeqSpace);
        return slot.frame;
    }

    void OnIndividualAck(uint8_t ack_seq) noexcept {
        // Індивідуальний ACK у Selective Repeat
        if (ModDist(base_, ack_seq) < window_size_) {
            buffer_[ack_seq].acked = true;
            buffer_[ack_seq].in_flight = false;

            // Зрушення лівої межі вікна, якщо підтверджено найстаріший кадр
            while (base_ != next_seq_ && buffer_[base_].acked) {
                buffer_[base_].acked = false; // Очищення для майбутнього кола
                base_ = static_cast<uint8_t>((base_ + 1) % kSeqSpace);
            }
        }
    }

    [[nodiscard]] std::vector<Frame> CheckTimeouts(uint32_t current_time) {
        std::vector<Frame> expired;
        uint8_t curr = base_;
        while (curr != next_seq_) {
            auto& slot = buffer_[curr];
            if (slot.in_flight && !slot.acked && current_time >= slot.timeout_time) {
                // Повторюємо ВИКЛЮЧНО прострочений кадр
                slot.timeout_time = current_time + rto_ticks_;
                expired.push_back(slot.frame);
            }
            curr = static_cast<uint8_t>((curr + 1) % kSeqSpace);
        }
        return expired;
    }

    [[nodiscard]] uint8_t GetBase() const noexcept { return base_; }
    [[nodiscard]] uint8_t GetNextSeq() const noexcept { return next_seq_; }

private:
    uint8_t window_size_;
    uint32_t rto_ticks_;
    uint8_t base_{0};
    uint8_t next_seq_{0};
    std::array<Slot, kSeqSpace> buffer_{};
};

// ─────────────────────────────────────────────────────────────────────────────
// Selective Repeat Receiver (Приймач із буфером перевпорядкування)
// ─────────────────────────────────────────────────────────────────────────────
class SelectiveRepeatReceiver {
public:
    struct RxSlot {
        Frame frame;
        bool received{false};
    };

    explicit SelectiveRepeatReceiver(uint8_t window_size)
        : window_size_(window_size) {}

    // Обробка вхідного кадру: повертає індивідуальний ACK та список даних для додатку
    std::pair<Frame, std::vector<std::string>> OnFrame(const Frame& f) {
        std::vector<std::string> delivered_data;
        Frame ack_frame;
        ack_frame.type = FrameType::Ack;
        ack_frame.seq = 0;
        ack_frame.ack = f.seq; // Індивідуальне підтвердження саме цього кадру

        if (f.type != FrameType::Data) {
            return {ack_frame, delivered_data};
        }

        const uint8_t dist = ModDist(base_, f.seq);
        if (dist < window_size_) {
            // Кадр потрапляє в активне приймальне вікно
            auto& slot = rx_buffer_[f.seq];
            slot.frame = f;
            slot.received = true;

            // Зрушення вікна прийому та передача даних стеку по порядку
            while (rx_buffer_[base_].received) {
                delivered_data.emplace_back(rx_buffer_[base_].frame.AsStringView());
                rx_buffer_[base_].received = false; // Звільнення слота
                base_ = static_cast<uint8_t>((base_ + 1) % kSeqSpace);
            }
        } else if (ModDist(static_cast<uint8_t>((base_ - window_size_ + kSeqSpace) % kSeqSpace), f.seq) < window_size_) {
            // Кадр із попереднього вікна (дублікат через втрату попереднього ACK)
            // Повторно надсилаємо ACK, щоб розблокувати передавач
        }

        return {ack_frame, delivered_data};
    }

    [[nodiscard]] uint8_t GetBase() const noexcept { return base_; }

private:
    uint8_t window_size_;
    uint8_t base_{0};
    std::array<RxSlot, kSeqSpace> rx_buffer_{};
};

} // namespace arq

// ─────────────────────────────────────────────────────────────────────────────
// Точка входу: демонстрація роботи Selective Repeat
// ─────────────────────────────────────────────────────────────────────────────
int main() {
    using namespace arq;
    std::cout << "=== Симуляція протоколу Selective Repeat (C++20) ===\n";

    SelectiveRepeatSender sender(4, 10);   // W_s = 4, RTO = 10
    SelectiveRepeatReceiver receiver(4); // W_r = 4

    const std::vector<std::string> messages = {
        "Packet-0", "Packet-1", "Packet-2", "Packet-3", "Packet-4"
    };

    // Відправляємо перші 4 пакети (повне вікно)
    for (size_t i = 0; i < 4; ++i) {
        std::span<const uint8_t> data(reinterpret_cast<const uint8_t*>(messages[i].data()), messages[i].size());
        if (auto f = sender.Send(data, i * 2)) {
            std::cout << "[TX] Відправлено кадр Seq=" << static_cast<int>(f->seq)
                      << " (\"" << f->AsStringView() << "\")\n";

            // Симулюємо втрату кадру з Seq=1
            if (f->seq == 1) {
                std::cout << "  [ВТРАТА] Кадр Seq=1 спотворено завадою в ефірі!\n";
                continue;
            }

            auto [ack, delivered] = receiver.OnFrame(*f);
            std::cout << "  [RX] Прийнято Seq=" << static_cast<int>(f->seq)
                      << ", надіслано індивідуальний ACK=" << static_cast<int>(ack.ack) << "\n";
            for (const auto& msg : delivered) {
                std::cout << "    [APP-DELIVER] Дані віддано додатку: \"" << msg << "\"\n";
            }
            sender.OnIndividualAck(ack.ack);
        }
    }

    std::cout << "\nСтан передавача: base=" << static_cast<int>(sender.GetBase())
              << ", next=" << static_cast<int>(sender.GetNextSeq()) << "\n";
    std::cout << "Стан приймача: base=" << static_cast<int>(receiver.GetBase()) << "\n";

    // Спливання таймауту для втраченого кадру 1
    std::cout << "\n--- Таймаут RTO на передавачі для кадру Seq=1 ---\n";
    auto expired = sender.CheckTimeouts(25);
    std::cout << "Selective Repeat повторює ТІЛЬКИ " << expired.size() << " кадр(и):\n";
    for (const auto& f : expired) {
        std::cout << "  [TX-RETRY] Вибірковий повтор кадру Seq=" << static_cast<int>(f.seq) << "\n";
        auto [ack, delivered] = receiver.OnFrame(f);
        std::cout << "  [RX] Отримано відсутній Seq=" << static_cast<int>(f.seq)
                  << ", надіслано ACK=" << static_cast<int>(ack.ack) << "\n";
        for (const auto& msg : delivered) {
            std::cout << "    [APP-DELIVER] Дані з буфера віддано додатку: \"" << msg << "\"\n";
        }
        sender.OnIndividualAck(ack.ack);
    }

    std::cout << "\nПісля відновлення: передавач base=" << static_cast<int>(sender.GetBase())
              << ", приймач base=" << static_cast<int>(receiver.GetBase()) << "\n";
    return 0;
}
```
:::

---

## 3. Покроковий розбір трасування станів та відновлення після втрат

Проаналізуємо роботу обох алгоритмів під час втрати другого за чергою пакета (`Seq = 1`).

### Траєкторія Go-Back-N

1. Передавач заповнює вікно `W = 4` і транслює кадри `0, 1, 2, 3`.
2. Кадр `0` доходить успішно. Приймач надсилає `ACK 0` і перемикається в очікування `R_expected = 1`.
3. Кадр `1` знищується шумом у каналі.
4. Кадри `2` та `3` досягають приймача. Приймач порівнює `seq = 2` та `seq = 3` зі своїм станом `R_expected = 1`. Оскільки рівність порушена, він **відкидає тіло обох кадрів**, але у відповідь відправляє дубльований `ACK 0`, сигналізуючи про розрив послідовності.
5. На передавачі спливає таймаут `RTO` для кадру `1` (оскільки `S_base` застряг на позиції `1`).
6. Автомат GBN викликає `gbn_sender_check_timeouts()` і **повторює передачу ВСІХ непідтверджених кадрів** `1, 2, 3`. Трафік каналу витрачається на повторну доставку блоків `2` та `3`, які вже були прийняті апаратурою приймача, але викинуті через відсутність буфера.

### Траєкторія Selective Repeat

1. Передавач відправляє повне вікно `0, 1, 2, 3`.
2. Кадр `0` приймається і негайно віддається стеку додатку (`delivered_data`).
3. Кадр `1` губиться.
4. Кадри `2` та `3` доходять до приймача. Автомат SR перевіряє потрапляння в діапазон вікна: `ModDist(base, seq) < W`. Обидва кадри записуються у відповідні слоти `rx_buffer_[2]` та `rx_buffer_[3]`. Приймач генерує індивідуальні підтвердження `ACK 2` та `ACK 3`.
5. Передавач отримує `ACK 2` і `ACK 3`, позначаючи відповідні слоти прапорцем `acked = true`. Вікно передавача не зрушується (бо `base_ = 1` не підтверджено), але таймери для слотів `2` і `3` зупиняються.
6. На передавачі спливає таймаут виключно для слота `1`. Метод `CheckTimeouts()` повертає вектор рівно з **одного кадру** `Seq = 1`.
7. Отримавши відсутній кадр `1`, приймач заповнює дірку в буфері. Цикл `while (rx_buffer_[base_].received)` моментально зшиває кадри `1, 2, 3` у єдиний потік і пакетом віддає їх додатку. Вікно приймача перестрибує відразу на `base_ = 4`.

---

## 4. Високопродуктивні таймери: ієрархічні таймерні колеса (Timing Wheels)

У базовій симуляції перевірка таймаутів здійснюється лінійним скануванням масиву слотів. Проте в ядрі Linux або високонавантажених серверах, де вікно передавача утримує десятки тисяч сегментів, лінійне сканування `O(W)` на кожному апаратному тіку таймера призводить до неприпустимих втрат процесорного часу.

Для досягнення константної складності `O(1)` операцій запуску, скасування та спливання таймерів застосовується структура даних **таймерного колеса** (англ. *Timing Wheel*, запропонована Джорджем Варгезе та Ентоні Лауком):

```
                   Поточний тік часу (Current Tick)
                                 │
                                 ▼
                     +-------+-------+-------+
                     | Слот0 | Слот1 | Слот2 | ...
                     +-------+-------+-------+
                         │
                         ▼ Двозв'язний список активних таймерів кадру
                     +---------------+       +---------------+
                     | Frame Seq=12  | ────► | Frame Seq=45  |
                     | Timeout = +10 |       | Timeout = +10 |
                     +---------------+       +---------------+
```

1. Колесо являє собою статичний кільцевий масив із `N` слотів, де кожен слот відповідає одному майбутньому тіку часу `t mod N`.
2. Кожен слот містить голову двозв'язного списку дескрипторів пакетів, для яких таймаут спливає саме в цей момент.
3. Додавання нового кадру в польоті розраховує цільовий слот `slot = (current_tick + RTO) mod N` і вставляє дескриптор у початок списку за `O(1)`.
4. Отримання `ACK` витягує дескриптор зі списку за `O(1)`, оскільки слот зберігає прямі вказівники на сусідні вузли списку.
5. На кожному системному перериванні таймера вказівник колеса просувається на одну позицію `current_tick = (current_tick + 1) mod N`, і всі таймери з поточного списку списуються як прострочені без необхідності сканування решти вікна.

---

## 5. Архітектура DMA-кілець у мережевих картах (NIC Ring Descriptors)

У сучасних високошвидкісних мережевих інтерфейсах (10/25/100 GbE) ядро операційної системи взаємодіє з апаратним контролером через кільцеві черги апаратних дескрипторів:

```
      Оперативна пам'ять (RAM)                     Мережевий адаптер (NIC)
   ┌─────────────────────────────┐               ┌─────────────────────────┐
   │ Ring Buffer:                │               │ Регістри дверного       │
   │ [Desc 0] -> sk_buff A (TX)  │ ◄── DMA Read ─│ дзвінка (Doorbell):     │
   │ [Desc 1] -> sk_buff B (TX)  │               │ - TX_HEAD (контролер)   │
   │ [Desc 2] -> Порожній слот   │               │ - TX_TAIL (драйвер ядра)│
   └─────────────────────────────┘               └─────────────────────────┘
```

1. Драйвер формує пакет у пам'яті (`sk_buff`), записує фізичну адресу буфера в черговий дескриптор `Desc N` і оновлює апаратний регістр `TX_TAIL` (Doorbell write).
2. Контролер через Direct Memory Access (DMA) самостійно вичитує біти з оперативної пам'яті, випромінює їх у фізичний трансивер та інкрементує регістр `TX_HEAD`.
3. Після отримання пакета `ACK` ядро звільняє структуру `sk_buff`, повертаючи слот у пул вільних дескрипторів.
4. Якщо швидкість передавача перевищує пропускну здатність лінії, черга дескрипторів заповнюється повністю (`TX_TAIL + 1 == TX_HEAD`), що викликає спрацьовування механізму апаратного зворотного тиску (Backpressure) і блокує сокетний виклик `send()`.

---

## 6. Алгоритм швидкого відновлення (Fast Retransmit)

Очікування повного спливання таймауту `RTO` (який зазвичай становить `200–1000` мс) вкрай негативно впливає на інтерактивні додатки. Для прискореного відновлення після втрат застосовується алгоритм **Fast Retransmit**:

1. При втраті кадру `k` усі наступні успішно прийняті кадри `k+1, k+2, k+3` змушують приймач генерувати повторні кумулятивні підтвердження `ACK k`.
2. Отримання **трьох дубльованих підтверджень** (Triple Duplicate ACK) є для передавача однозначним евристичним свідченням того, що кадр `k` дійсно втрачено (а не просто затримано в черзі), тоді як наступні кадри вже дійшли до одержувача.
3. Передавач не чекає спливання таймера `RTO`, а **негайно повторно надсилає відсутній кадр `k`** (Fast Retransmit) і переходить у фазу швидкого відновлення (Fast Recovery), підтримуючи потік конвеєра активним.

---

## 7. Тестова матриця валідації автоматів станів (Test Matrix)

Для всебічної перевірки стійкості реалізацій ARQ розробляється набір детермінованих стрес-тестів:

| Тестовий сценарій | Початковий стан | Подія у каналі | Очікувана реакція передавача | Очікувана реакція приймача | Інваріант коректності |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Одиночна втрата** | `W=4`, відправлено `0,1,2,3` | Кадр `1` втрачено | GBN: повтор `1,2,3`. SR: повтор `1` | GBN: дроп `2,3`, ACK 0. SR: буфер `2,3`, ACK 2,3 | Дані додатку: `0,1,2,3` без пропусків |
| **2. Масовий сплеск (Burst Loss)** | `W=8`, відправлено `0..7` | Втрачено кадри `1,2,3,4` | Таймаут на `1`, повтор непідтверджених | Буферизація кадрів `5,6,7` (SR) | Жоден кадр не дублюється в застосунку |
| **3. Втрата зворотних ACK** | `W=4`, кадри `0..3` дійшли | Усі `ACK 0..3` втрачено | Спливання RTO `S_base=0`, повтор `0` | Відкидання дубліката `0`, повтор ACK 3 | Вікно TX розблоковується після отримання ACK 3 |
| **4. Перевпорядкування (Reordering)** | `W=4`, порядок: `3,2,1,0` | Затримки в багатошляховому лінку | Ігнорування дублікатів ACK | Буферизація `3,2,1`, видача приходу `0` | Строго послідовний вихід: `0,1,2,3` |
| **5. Перехід через нуль (Wrap-around)** | `M=8, Base=6, W=4` | Відправлено `6,7,0,1` | Коректне зрушення `S_base` через 0 | Перевірка `ModDist(Base, seq) < 4` | Відсутність зациклення та переповнення типізації |

---

## 8. Покроковий розбір коду та інваріанти роботи з буферами

Проаналізуємо ключові методи реалізацій C та C++ з точки зору коректності керування пам'яттю та системних інваріантів:

1. **Функція модульної відстані `ModDist(from, to, mod)`:**
   Обчислює кількість кроків за годинниковою стрілкою від індексу `from` до індексу `to` на кільці розміру `mod`. Вираз `(to - from + mod) % mod` захищений від від'ємних результатів ділення в C (де оператор `%` для від'ємних чисел зберігає знак діленого) завдяки додаванню зміщення `+ mod`.
2. **Інваріант просування `S_base` у Go-Back-N:**
   При отриманні кумулятивного `ack_seq` передавач перевіряє умову `advance > 0 && advance <= max_advance`. Це унеможливлює атаку запізнілим дублікатом старого `ACK`, який міг би спричинити хибне циклічне зміщення бази на повний оберт.
3. **Метод `OnIndividualAck()` у Selective Repeat:**
   У C++20 кожне підтвердження позначає слот прапорцем `buffer_[ack_seq].acked = true`. Зрушення лівої межі `base_` виконується у циклі `while (buffer_[base_].acked)`. Слот обов'язково скидається в стан `acked = false`, очищаючи дескриптор для використання на наступному оберті циклічного буфера.
4. **Метод `OnFrame()` у приймачі Selective Repeat:**
   Повертає пару `std::pair<Frame, std::vector<std::string>>`: перший елемент — це сформований зворотний `ACK`, а другий — вектор із фрагментами даних, які вдалося послідовно зшити та віддати прикладному рівню. Якщо вхідний кадр потрапив у вікно попереднього циклу (`dist` у лівому півколі), приймач генерує повторний `ACK`, не зберігаючи застарілі дані в пам'яті.

---

## 9. Асинхронне масштабування: перехід до epoll та io_uring

У реальних високопродуктивних мережевих рушіях (наприклад, реалізаціях протоколу QUIC або користувацьких UDP-стеках UDT/SRT) робота зі ковзним вікном переноситься в асинхронні цикли подій (Event Loops):

1. **Подійно-орієнтований таймер через `timerfd`:**
   Замість опитування системного часу в циклі створюється файловий дескриптор `timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK)`. Найближчий таймаут зі списку активних слотів вікна записується в дескриптор через `timerfd_settime()`, після чого ядро операційної системи самостійно пробуджує потік через `epoll_wait()`.
2. **Нульове копіювання через `io_uring`:**
   При використанні підсистеми ядра Linux `io_uring` передавач заповнює чергу надсилання (Submission Queue, SQE) операціями `IORING_OP_SENDMSG` із прапорцем `MSG_ZEROCOPY`. Мережева карта читає дані прямо зі сторінок пам'яті користувача, а після підтвердження доставки через `ACK` ядро повертає подію в чергу завершення (Completion Queue, CQE), повідомляючи про безпеку повторного використання буфера.
3. **Lock-Free кільцеві буфери (SPSC Ring Buffers):**
   Для зв'язку між мережевим потоком (що вичитує сокети) та прикладним потоком (що обробляє корисні дані) використовуються безблокувальні кільцеві буфери з атомарними покажчиками `std::atomic<size_t>` та бар'єрами пам'яті `std::memory_order_acquire` / `std::memory_order_release`, що усуває блокування м'ютексів та забезпечує обробку десятків мільйонів пакетів за секунду на одне процесорне ядро.

---

## 10. Оптимізація кешу процесора та усунення False Sharing

При розробці багатопотокових ARQ-стеків на сучасних багатоядерних процесорах x86_64 та ARMv8 критично важливо враховувати архітектуру кеш-ліній (Cache Lines) та модель послідовної узгодженості пам'яті:

1. **Проблема хибного розділення пам'яті (False Sharing):**
   Якщо лічильник передавача `S_next` (який безперервно модифікується потоком надсилання) та лічильник `S_base` (який змінюється потоком обробки вхідних ACK) опиняються в межах однієї 64-байтової кеш-лінії L1, ядра процесора починають безперервно інвалідувати кеш одне одного через протокол когерентності MESI. Це знижує пропускну здатність у 5–10 разів.
2. **Вирівнювання пам'яті `alignas(64)` та атомарні операції:**
   Для усунення False Sharing критичні змінні стану розміщують на окремих кеш-лініях за допомогою специфікатора вирівнювання:
   ```cpp
   alignas(64) std::atomic<uint32_t> s_base_{0};
   alignas(64) std::atomic<uint32_t> s_next_{0};
   ```
   При читанні та оновленні використовують семантику звільнення-набуття (`std::memory_order_release` для публікації слота та `std::memory_order_acquire` для читання), що запобігає апаратному перевпорядкуванню інструкцій на процесорах із слабкою моделлю пам'яті (ARM, RISC-V).
3. **Побітові маски замість оператора ділення по модулю `%`:**
   Якщо розмір простору номерів є степенем двійки `M = 2^k`, обчислення `(seq + 1) % M` замінюють на побітове `(seq + 1) & (M - 1)`. Це дозволяє компілятору згенерувати інструкцію `AND` замість важкої інструкції цілочисельного ділення `DIV`, яка займає до 20–40 тактів процесора.
4. **Векторизована обробка вікна через SIMD:**
   Для швидкої перевірки статусу підтвердження масиву слотів у Selective Repeat застосовують бітові маски AVX2/NEON: 32 або 64 слоти пакуються в один регістр, що дозволяє за одну інструкцію `_mm256_testz_si256` перевірити, чи є хоча б один прострочений таймер у поточному вікні.

---

## 11. Інженерні пастки та тонкощі низькорівневої реалізації

Практична розробка драйверів мережевих карт, супутникових модемів та стеків протоколів на мікроконтролерах вимагає врахування таких критичних аспектів:

1. **Модульна арифметика замість лінійного порівняння:**
   Найчастіша помилка програміста-початківця — спроба перевірити коректність номера виразом `if (seq >= base && seq < base + W)`. При переході лічильника через нуль (наприклад, `base = 30`, `W = 4` на кільці `M = 32`, коли вікно охоплює `{30, 31, 0, 1}`), ця умова поверне `false` для абсолютно валідних номерів `0` та `1`. Єдиний правильний спосіб — обчислювати відстань `(seq - base + M) % M < W`.
2. **Алгоритм Карна та розрахунок таймауту RTO (Karn-Partridge Algorithm):**
   Якщо кадр було передано повторно, неможливо визначити, на яку саме спробу надійшов відповідний `ACK` — на первинну (що просто затрималася в черзі) чи на повторну. Якщо врахувати такий запізнілий `ACK` у згладжуванні RTT, оцінка затримки каналу катастрофічно спотвориться. Правило Карна стверджує: *ніколи не оновлювати RTT за вимірюваннями повторно переданих сегментів, а при кожному таймауті застосовувати експоненціальне відтермінування (Exponential Backoff, `RTO = 2 · RTO`)*.
3. **Гонка потоків при скасуванні таймерів (Timer Race Conditions):**
   У багатопотокових ОС обробник переривання таймера може почати виконуватися на одному ядрі процесора в той самий момент, коли мережевий потік на іншому ядрі отримує пакет `ACK` і зрушує `S_base`. Якщо обробник таймера не заблокує м'ютекс або не перевірить статус слота `in_flight == true`, він згенерує паразитного дубліката вже підтвердженого пакета.
4. **Вичерпання дескрипторів DMA та Zero-Copy буферизація:**
   У високопродуктивних мережевих адаптерах 10/40/100 GbE передавач не копіює байти з буфера програми в буфер протоколу. Кільцевий буфер ковзного вікна формується у вигляді масиву апаратних дескрипторів DMA (англ. *Direct Memory Access*). Розмір вікна `W_s` у таких системах жорстко обмежений довжиною фізичного DMA-кільця контролера, а звільнення пам'яті відбувається виключно після надходження підтвердження `ACK`.
5. **Синдром дурного вікна (Silly Window Syndrome):**
   У байт-орієнтованих протоколах (наприклад, TCP) швидкий передавач може надсилати крихітні пакети розміром у 1 байт щоразу, коли повільний приймач звільняє 1 байт у буфері. Для боротьби з цим явищем алгоритм Кларка забороняє приймачу анонсувати розширення вікна, доки воно не досягне принаймні половини максимального буфера або розміру одного повного кадру (MSS).
6. **Блокування початку черги (Head-of-Line Blocking) на транспортному рівні:**
   Хоча Selective Repeat успішно буферизує пакети `2, 3, 4` під час втрати пакета `1`, прикладний процес не може прочитати байти `2, 3, 4` доти, доки не надійде пакет `1`, якщо протокол гарантує суворий порядок потоку (як TCP). У сучасних мультиплексованих протоколах (QUIC) кожен потік даних має власне незалежне вікно, тому втрата пакета в одному потоці не блокує доставку незалежних даних іншим потокам.
7. **Коректне вивільнення неволодіючих дескрипторів (Span Lifetime Safety):**
   При передачі `std::span` у метод `Send()` розробник повинен гарантувати, що пам'ять корисного навантаження не буде звільнена доти, доки пакет перебуває в польоті або в черзі повтору. У C++20 копіювання в локальний масив слота `std::array<uint8_t, kMaxPayload>` ізолює внутрішній стан протоколу від життєвого циклу зовнішнього буфера додатку.
