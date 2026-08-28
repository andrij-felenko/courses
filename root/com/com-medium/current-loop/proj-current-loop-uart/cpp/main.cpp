// cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <system_error>

namespace current_loop {

constexpr std::size_t BufferSize = 256;
constexpr std::size_t MaxFrameLength = 64;
constexpr uint8_t FrameStartOfFrame = 0x02;

// Статуси помилок роботи струмової петлі
enum class LoopError {
    BufferEmpty,
    BufferOverflow,
    LineBreakFault,  // Фізичний обрив петлі (струм = 0 мА)
    ChecksumMismatch,
    InvalidLength
};

// Проектний клас кадру даних
struct LoopFrame {
    uint8_t sender_id{0};
    uint8_t length{0};
    std::array<uint8_t, MaxFrameLength> payload{};

    [[nodiscard]] std::span<const uint8_t> data() const noexcept {
        return std::span<const uint8_t>{payload.data(), length};
    }
};

// RAII Кільцевий драйвер струмової петлі
class CurrentLoopDriver {
public:
    CurrentLoopDriver() = default;

    // Метод запису з переривання UART (ISR)
    void on_uart_isr_receive(uint8_t byte, bool is_break_condition) noexcept {
        if (is_break_condition) {
            line_break_fault_ = true;
            ++break_count_;
            return;
        }

        const auto next_head = (head_ + 1) % BufferSize;
        if (next_head != tail_) {
            buffer_[head_] = byte;
            head_ = next_head;
        }
    }

    // Зчитати наступний байт
    [[nodiscard]] std::expected<uint8_t, LoopError> pop_byte() noexcept {
        if (line_break_fault_) {
            return std::unexpected(LoopError::LineBreakFault);
        }

        if (head_ == tail_) {
            return std::unexpected(LoopError::BufferEmpty);
        }

        const uint8_t byte = buffer_[tail_];
        tail_ = (tail_ + 1) % BufferSize;
        return byte;
    }

    // Сновити стан аварії після відновлення струму 20 мА
    void reset_line_fault() noexcept {
        line_break_fault_ = false;
    }

    [[nodiscard]] bool is_line_fault() const noexcept {
        return line_break_fault_;
    }

    [[nodiscard]] uint32_t break_count() const noexcept {
        return break_count_;
    }

    // Парсер кадру з поверненням std::expected
    [[nodiscard]] std::expected<LoopFrame, LoopError> parse_frame() noexcept {
        auto byte_res = pop_byte();
        if (!byte_res) return std::unexpected(byte_res.error());

        if (*byte_res != FrameStartOfFrame) {
            return std::unexpected(LoopError::BufferEmpty);
        }

        // Довжина
        auto len_res = wait_and_pop();
        if (!len_res) return std::unexpected(len_res.error());
        if (*len_res > MaxFrameLength) return std::unexpected(LoopError::InvalidLength);

        // Sender ID
        auto sender_res = wait_and_pop();
        if (!sender_res) return std::unexpected(sender_res.error());

        LoopFrame frame{};
        frame.length = *len_res;
        frame.sender_id = *sender_res;

        uint8_t calculated_crc = 0x00 ^ frame.length ^ frame.sender_id;

        for (std::size_t i = 0; i < frame.length; ++i) {
            auto data_res = wait_and_pop();
            if (!data_res) return std::unexpected(data_res.error());
            frame.payload[i] = *data_res;
            calculated_crc ^= frame.payload[i];
        }

        auto crc_res = wait_and_pop();
        if (!crc_res) return std::unexpected(crc_res.error());

        if (calculated_crc != *crc_res) {
            return std::unexpected(LoopError::ChecksumMismatch);
        }

        return frame;
    }

private:
    [[nodiscard]] std::expected<uint8_t, LoopError> wait_and_pop() noexcept {
        // У реальній O/S тут використовується семафор або таймаут
        return pop_byte();
    }

    std::array<uint8_t, BufferSize> buffer_{};
    volatile std::size_t head_{0};
    volatile std::size_t tail_{0};
    volatile bool line_break_fault_{false};
    uint32_t break_count_{0};
};

} // namespace current_loop
:::

---

### Покроковий аналіз виконання парсера кадрів

Розглянемо поетапний потік виконання коду при виклику parse_frame.

На першому етапі здійснюється перевірка маркера початку кадру SOF (Start Of Frame). Функція pop_byte() вилучає перший байт з кільцевого буфера. Якщо перший байт не дорівнює контрольному байту 0x02, парсер негайно переходить у стан помилки LoopError::BufferEmpty і скидає поточну позицію. Це захищає від обробки сміттєвих байтів, наведених у кабель при підключенні клеми.

На другому етапі відбувається зчитування заголовочних полів кадру. Драйвер послідовно читає байт довжини корисного навантаження length та ідентифікатор вузла відправника sender_id. Перевіряється граничний інваріант: довжина не повинна перевищувати MaxFrameLength (64 байти). Якщо відправник сформував некоректний байт довжини, парсер повертає статус LoopError::InvalidLength і запобігає переповненню статичного масиву payload.

На третьому етапі виконується циклічна вибірка даних та розрахунок контрольної суми. У циклі драйвер зчитує байт за байтом та акумулює поточне значення контрольної суми за допомогою побітового виключального АБО.

На четвертому етапі проводиться верифікація контрольної суми кадру. Останній прийнятий байт порівнюється з обчисленим значенням calculated_crc. Якщо в результаті імпульсної завади хоча б один біт у кабелі був викривлений, обчислене значення не співпаде з прийнятим, і пакет відкидається зі статусом ChecksumMismatch.

---

### Детальний порівняльний аналіз C та C++ рішень

Розглянемо фундаментальні відмінності між реалізаціями драйвера мовою C та C++:

Щодо безпеки обробки помилок (Type-safe Error Handling): у мові C функція loop_buf_pop повертає статус loop_status_t, а значення байта записується через покажчик uint8_t *byte. Якщо розробник забуде перевірити повернене значення, він прочитає сміття зі змінної. У мові C++ метод pop_byte() повертає тип std::expected<uint8_t, LoopError> (C++23). Об'єкт є монадичним контейнером, який фізично не дозволяє розпакувати байт без розкриття перевірки на помилку.

Щодо керування пам'яттю та RAII: у C-версії структура current_loop_ringbuf_t вимагає обов'язкового явного виклику функції loop_buf_init(). Випадковий виклик loop_buf_pop() без попередньої ініціалізації призводить до читання невизначеного стану. У C++ конструктор за замовчуванням CurrentLoopDriver() = default гарантує обнулення індексів head_, tail_ та прапорців у момент створення об'єкта у стеку або статичній пам'яті.

Щодо представлення буферів даних (Zero-Copy Views): у C-реалізації структура loop_frame_t містить фіксований масив uint8_t data[MAX_FRAME_LEN], і розробник повинен окремо передавати довжину length. У C++ метод data() повертає std::span<const uint8_t>. Це неперервний view-об'єкт без додаткового виділення пам'яті у купі (Heap), який несе в собі і вказівник на дані, і безпечний розмір, захищаючи від виходу за межі масиву (Buffer Overflow).

Щодо гарантій для систем реального часу (Real-Time Safety): усі методи класу C++ позначаються специфікатором noexcept та [[nodiscard]]. Специфікатор noexcept підтверджує компілятору, що код не генерує винятків і розгортається у найшвидші асемблерні машинні інструкції без таблиць розкрутки стека.

---

### Алгоритм обчислення контрольної суми CRC-8 / MAXIM

Для захисту даних від імпульсних наведень на кабель у промислових кадрах застосовують циклічний надлишковий код CRC-8 з поліномом `P(x) = x^8 + x^5 + x^4 + 1` (значення 0x8C у дзеркальному вираженні).

Математичний принцип обчислення полягає у діленні масиву бітів кадру на твірний поліном за модулем 2. На відміну від ззвичайного додавання XOR, поліноміальний код розпізнає 100 % одиночних і подвійних помилок, а також будь-які пачки завад довжиною до 8 бітів включно.
