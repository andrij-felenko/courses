# ⚙️ Кредитний протокол і буфер із пороговим зворотним тиском

Коли мікроконтролер із частотою 48 МГц приймає потік пакетів від швидкого радіомодуля або промислового інтерфейсу зі швидкістю 1 Мбіт/с, програмний обробник не встигає парсити та записувати дані у Flash-пам'ять із такою самою швидкістю. Звичайне відкидання пакетів змушує відправника перезапускати таймаути й повторювати передачу, що лише посилює затор на шині. Щоб зв'язок працював без втрат і без повторних пересилань, системі потрібні дві узгоджені ланки: кільцевий буфер приймача з гістерезисними порогами заповнення (High/Low Watermark) та кредитний автомат відправника, який зупиняє видачу кадрів до вичерпання виділених слотів пам'яті.

Нижче наведено робочу реалізацію обох механізмів. Перша частина — це драйвер кільцевого буфера приймача, який автоматично керує апаратною лінією `/RTS` (або формує програмний сигнал паузи), коли об'єм вільного місця падає нижче запасу на «байти в польоті». Друга частина — це кінцевий автомат протокольного обміну на основі явних кредитів (Credit-Based Flow Control), де передавач відправляє кадри лише за наявності доступного балансу, а приймач повертає кредити в міру звільнення пам'яті споживачем.

## Архітектура буфера з порогами заповнення

Кільцевий буфер приймача містить фіксований масив у статичній пам'яті (без динамічного виділення) та два покажчики: запису (`head`) та читання (`tail`). Головна відмінність від звичайного FIFO — наявність двох контрольних рівнів заповнення:
- **High Watermark (HWM)**: поріг спрацьовування паузи (наприклад, 75% місткості буфера, тобто 192 байти для буфера на 256 байтів). Щойно рівень досягає HWM, лінія `/RTS` піднімається у високий рівень (стан Busy), сигналізуючи передавачу про необхідність негайної зупинки. Решта 25% простору (64 байти) залишається суворим запасом безпеки: вона поглинає байти, які передавач уже завантажив у свій апаратний зсувний регістр, байти в кабелі або байти, надіслані до моменту обробки сигналу переривання.
- **Low Watermark (LWM)**: поріг відновлення прийому (наприклад, 25% місткості буфера, тобто 64 байти). Лінія `/RTS` опускається в нуль (стан Ready) лише тоді, коли обробник суттєво розвантажив буфер.

Зона між HWM та LWM утворює смугу гістерезису шириною 128 байтів. Якби поріг був один (наприклад, зняття RTS на рівні 192 і відновлення на рівні 191), кожен вичитаний програмою байт спричиняв би миттєве короткочасне відновлення RTS і надсилання рівно одного байта передавачем. Це призводило б до високочастотного тремтіння лінії керування на кожному символі та значного падіння ефективності шини.

:::tabs
@tab c
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define RING_BUF_SIZE 256
#define HIGH_WATERMARK (RING_BUF_SIZE * 3 / 4) // 192 байти: зняти RTS
#define LOW_WATERMARK  (RING_BUF_SIZE * 1 / 4) // 64 байти: відновити RTS

typedef void (*rts_set_fn)(bool active_low_ready);

typedef struct {
    uint8_t storage[RING_BUF_SIZE];
    volatile size_t head;
    volatile size_t tail;
    volatile size_t count;
    rts_set_fn set_rts;
    bool rts_asserted;
} FlowRingBuffer;

void flow_ring_init(FlowRingBuffer *rb, rts_set_fn rts_cb) {
    rb->head = 0;
    rb->tail = 0;
    rb->count = 0;
    rb->set_rts = rts_cb;
    rb->rts_asserted = true;
    if (rb->set_rts) {
        rb->set_rts(true); // Готовий до прийому (лінія /RTS = 0 В)
    }
}

// Викликається з ISR прийому UART або DMA half-transfer callback
bool flow_ring_push_isr(FlowRingBuffer *rb, uint8_t byte) {
    if (rb->count >= RING_BUF_SIZE) {
        return false; // Фатальне переповнення (буфер вичерпано повністю)
    }

    rb->storage[rb->head] = byte;
    rb->head = (rb->head + 1) % RING_BUF_SIZE;
    rb->count++;

    // Перевірка верхнього порогу: піднімаємо RTS у High (стан Busy)
    if (rb->rts_asserted && rb->count >= HIGH_WATERMARK) {
        rb->rts_asserted = false;
        if (rb->set_rts) {
            rb->set_rts(false); // /RTS = 3.3 В (заборона передачі)
        }
    }
    return true;
}

// Викликається з основного циклу або фонового завдання RTOS
bool flow_ring_pop(FlowRingBuffer *rb, uint8_t *out_byte) {
    if (rb->count == 0) {
        return false; // Буфер порожній
    }

    *out_byte = rb->storage[rb->tail];
    rb->tail = (rb->tail + 1) % RING_BUF_SIZE;
    rb->count--;

    // Перевірка нижнього порогу: опускаємо RTS у Low (стан Ready)
    if (!rb->rts_asserted && rb->count <= LOW_WATERMARK) {
        rb->rts_asserted = true;
        if (rb->set_rts) {
            rb->set_rts(true); // /RTS = 0 В (дозвіл передачі)
        }
    }
    return true;
}
```
@tab cpp
```cpp
#include <array>
#include <span>
#include <optional>
#include <concepts>
#include <cstdint>
#include <cstddef>

template <std::size_t Capacity = 256>
class FlowControlRingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two");
    static constexpr std::size_t HighWatermark = Capacity * 3 / 4;
    static constexpr std::size_t LowWatermark  = Capacity * 1 / 4;

public:
    using RtsCallback = void (*)(bool is_ready);

    explicit FlowControlRingBuffer(RtsCallback rts_cb) noexcept
        : set_rts_{rts_cb}, rts_asserted_{true} {
        if (set_rts_) {
            set_rts_(true);
        }
    }

    // Виклик із контексту переривання UART
    [[nodiscard]] bool push_from_isr(uint8_t byte) noexcept {
        if (count_ >= Capacity) {
            return false;
        }

        storage_[head_] = byte;
        head_ = (head_ + 1) & (Capacity - 1);
        ++count_;

        if (rts_asserted_ && count_ >= HighWatermark) {
            rts_asserted_ = false;
            if (set_rts_) {
                set_rts_(false);
            }
        }
        return true;
    }

    // Виклик із контексту споживача
    [[nodiscard]] std::optional<uint8_t> pop() noexcept {
        if (count_ == 0) {
            return std::nullopt;
        }

        const uint8_t byte = storage_[tail_];
        tail_ = (tail_ + 1) & (Capacity - 1);
        --count_;

        if (!rts_asserted_ && count_ <= LowWatermark) {
            rts_asserted_ = true;
            if (set_rts_) {
                set_rts_(true);
            }
        }
        return byte;
    }

    [[nodiscard]] std::size_t size() const noexcept { return count_; }
    [[nodiscard]] bool is_ready() const noexcept { return rts_asserted_; }

private:
    std::array<uint8_t, Capacity> storage_{};
    volatile std::size_t head_{0};
    volatile std::size_t tail_{0};
    volatile std::size_t count_{0};
    RtsCallback set_rts_{nullptr};
    bool rts_asserted_{false};
};
```
:::

## Кредитний автомат передавача й приймача

Для пакетного обміну через шини без окремих апаратних ліній керування (RS-485, CAN, бездротовий міст) використовується протокол на основі кредитів. Вузол-передавач зберігає цілочисельний баланс доступних слотів `available_credits`. Кожна відправка кадру декрементує цей лічильник. Якщо `available_credits == 0`, передавач переходить у режим очікування і не надсилає корисні дані. 

Вузол-приймач відправляє керівний кадр `CREDIT_GRANT` з числом звільнених слотів, коли його робоче завдання завершило обробку раніше отриманих пакетів. Для максимальної ефективності кількість повернених кредитів може накопичуватися і надсилатися пачкою або вбудовуватися в поле звичайного пакета підтвердження (Piggybacking).

:::tabs
@tab c
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PAYLOAD_SIZE 64
#define TOTAL_RX_SLOTS   4

typedef enum {
    FRAME_TYPE_DATA = 0x01,
    FRAME_TYPE_CREDIT_GRANT = 0x02
} FrameType;

typedef struct {
    uint8_t type;
    uint8_t seq_or_credit; // seq для DATA, кількість кредитів для GRANT
    uint8_t length;
    uint8_t payload[MAX_PAYLOAD_SIZE];
} PacketFrame;

// Передавач
typedef struct {
    int32_t available_credits;
    uint8_t next_seq;
} CreditSender;

void credit_sender_init(CreditSender *s, int32_t initial_credits) {
    s->available_credits = initial_credits;
    s->next_seq = 0;
}

bool credit_sender_can_send(const CreditSender *s) {
    return s->available_credits > 0;
}

bool credit_sender_send(CreditSender *s, const uint8_t *data, uint8_t len, PacketFrame *out_frame) {
    if (s->available_credits <= 0 || len > MAX_PAYLOAD_SIZE) {
        return false;
    }

    out_frame->type = FRAME_TYPE_DATA;
    out_frame->seq_or_credit = s->next_seq++;
    out_frame->length = len;
    memcpy(out_frame->payload, data, len);

    s->available_credits--;
    return true;
}

void credit_sender_on_grant(CreditSender *s, uint8_t returned_credits) {
    s->available_credits += returned_credits;
}

// Приймач
typedef struct {
    uint8_t pending_returns;
    uint8_t occupied_slots;
} CreditReceiver;

void credit_receiver_init(CreditReceiver *r) {
    r->pending_returns = 0;
    r->occupied_slots = 0;
}

bool credit_receiver_on_frame(CreditReceiver *r, const PacketFrame *frame) {
    if (frame->type != FRAME_TYPE_DATA) {
        return false;
    }
    if (r->occupied_slots >= TOTAL_RX_SLOTS) {
        return false; // Порушення протоколу: відправник перевищив квоту
    }
    r->occupied_slots++;
    return true;
}

// Викликається після того, як завдання вичитало пакет із пам'яті
void credit_receiver_release_slot(CreditReceiver *r) {
    if (r->occupied_slots > 0) {
        r->occupied_slots--;
        r->pending_returns++;
    }
}

bool credit_receiver_make_grant(CreditReceiver *r, PacketFrame *out_frame) {
    if (r->pending_returns == 0) {
        return false;
    }

    out_frame->type = FRAME_TYPE_CREDIT_GRANT;
    out_frame->seq_or_credit = r->pending_returns;
    out_frame->length = 0;

    r->pending_returns = 0;
    return true;
}
```
@tab cpp
```cpp
#include <array>
#include <span>
#include <optional>
#include <cstdint>
#include <algorithm>

enum class FrameType : uint8_t {
    Data = 0x01,
    CreditGrant = 0x02
};

struct PacketFrame {
    FrameType type{FrameType::Data};
    uint8_t seq_or_credit{0};
    uint8_t length{0};
    std::array<uint8_t, 64> payload{};
};

class CreditSender {
public:
    explicit constexpr CreditSender(int32_t initial_credits) noexcept
        : available_credits_{initial_credits} {}

    [[nodiscard]] bool can_send() const noexcept {
        return available_credits_ > 0;
    }

    [[nodiscard]] std::optional<PacketFrame> prepare_frame(std::span<const uint8_t> data) noexcept {
        if (available_credits_ <= 0 || data.size() > 64) {
            return std::nullopt;
        }

        PacketFrame frame;
        frame.type = FrameType::Data;
        frame.seq_or_credit = next_seq_++;
        frame.length = static_cast<uint8_t>(data.size());
        std::copy(data.begin(), data.end(), frame.payload.begin());

        --available_credits_;
        return frame;
    }

    void on_grant_received(uint8_t granted_credits) noexcept {
        available_credits_ += granted_credits;
    }

    [[nodiscard]] int32_t credits() const noexcept { return available_credits_; }

private:
    int32_t available_credits_{0};
    uint8_t next_seq_{0};
};

template <std::size_t MaxSlots = 4>
class CreditReceiver {
public:
    CreditReceiver() = default;

    [[nodiscard]] bool on_frame_received(const PacketFrame& frame) noexcept {
        if (frame.type != FrameType::Data) {
            return false;
        }
        if (occupied_slots_ >= MaxSlots) {
            return false; // Переповнення ліміту: помилка передавача
        }
        ++occupied_slots_;
        return true;
    }

    void release_slot() noexcept {
        if (occupied_slots_ > 0) {
            --occupied_slots_;
            ++pending_returns_;
        }
    }

    [[nodiscard]] std::optional<PacketFrame> make_grant_frame() noexcept {
        if (pending_returns_ == 0) {
            return std::nullopt;
        }

        PacketFrame frame;
        frame.type = FrameType::CreditGrant;
        frame.seq_or_credit = pending_returns_;
        frame.length = 0;

        pending_returns_ = 0;
        return frame;
    }

    [[nodiscard]] std::size_t occupied() const noexcept { return occupied_slots_; }

private:
    std::size_t occupied_slots_{0};
    uint8_t pending_returns_{0};
};
```
:::

## Інженерні пастки та деталі реалізації

При практичному впровадженні наведених алгоритмів у прошивку реального часу розробник стикається з трьома критичними аспектами системного програмування:

1. **Гонка станів між ISR та потоком споживача**: Лічильник `count` кільцевого буфера модифікується як у перериванні UART (інкремент), так і в основному циклі або завданні RTOS (декремент). Операція `count--` на мікроконтролері складається з трьох машинних інструкцій (зчитування з пам'яті в регістр ядра, віднімання одиниці, збереження результату назад). Якщо під час цієї операції виникає переривання UART, яке виконує `count++`, результат збереження затре значення переривання. Для усунення цієї гонки в одноядерних системах операцію зменшення беруть у критичну секцію (коротке відключення переривань), або замінюють спільний лічильник `count` на незалежні індекси `head` і `tail`, які вирівнюються за розміром машинного слова і змінюються суворо одним потоком виконання.
2. **Бар'єри пам'яті на конвеєрних ядрах**: На сучасних ядрах із глибоким конвеєром і перевпорядкуванням пам'яті (Cortex-M7) компілятор або процесор може виконати оновлення індексу `head` раніше, ніж фактичні дані запишуться в масив `storage`. Щоб запобігти зчитуванню «сміття» споживачем, перед зміною індексу обов'язково викликають апаратний бар'єр даних (інструкція `__DMB()`).
3. **Втрата керуючого кадру повернення кредитів**: Якщо лінія зв'язку зашумлена і пакет `CREDIT_GRANT` пошкоджено, лічильник передавача ніколи не поповниться, що призведе до вічного зависання (deadlock). Для захисту від цієї пастки впроваджують два правила:
   - Передавач запускає таймер неактивності: якщо кредити вичерпані, а відповіді немає довше за інтервал `T_TIMEOUT`, передавач надсилає короткий запит стану `POLL_CREDITS`.
   - Приймач не просто надсилає відносний інкремент `+1`, а вказує в кожному кадрі абсолютний кумулятивний номер звільнених слотів або поточний залишок вільних блоків пам'яті.
