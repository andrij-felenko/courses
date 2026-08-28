#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <expected>
#include <functional>
#include <cstdint>
#include <cstring>

namespace messaging {

constexpr uint32_t MagicBatch = 0x53504C54; // "SPLT"
constexpr uint32_t MagicItem  = 0x4954454D; // "ITEM"

enum class SplitError {
    InvalidBatchHeader,
    CorruptedFrameMagic,
    ChecksumMismatch,
    IncompleteFrameBuffer,
    QueueShutdown
};

// Обчислення CRC32 у сучасному стилі C++
constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFF;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

// Конверт атомарного повідомлення з успадкованим контекстом
struct DiscreteMessage {
    uint64_t correlation_id{0};
    uint32_t sequence_number{0};
    uint32_t sequence_size{0};
    bool is_last{false};
    std::string payload;

    [[nodiscard]] std::string_view payload_view() const noexcept {
        return payload;
    }
};

// Потокобезпечна черга з механізмом високої та низької ватерлінії (Backpressure)
class BoundedChannel {
public:
    explicit BoundedChannel(size_t capacity = 128, size_t high_watermark = 100, size_t low_watermark = 20)
        : capacity_(capacity), high_watermark_(high_watermark), low_watermark_(low_watermark) {}

    ~BoundedChannel() {
        close();
    }

    BoundedChannel(const BoundedChannel&) = delete;
    BoundedChannel& operator=(const BoundedChannel&) = delete;

    bool push(DiscreteMessage&& msg) {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_not_full_.wait(lock, [this] {
            return queue_.size() < high_watermark_ || is_closed_;
        });

        if (is_closed_) return false;

        queue_.push(std::move(msg));
        cv_not_empty_.notify_one();
        return true;
    }

    std::expected<DiscreteMessage, SplitError> pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_not_empty_.wait(lock, [this] {
            return !queue_.empty() || is_closed_;
        });

        if (queue_.empty() && is_closed_) {
            return std::unexpected(SplitError::QueueShutdown);
        }

        DiscreteMessage msg = std::move(queue_.front());
        queue_.pop();

        if (queue_.size() <= low_watermark_) {
            cv_not_full_.notify_all();
        }

        return msg;
    }

    void close() noexcept {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            is_closed_ = true;
        }
        cv_not_full_.notify_all();
        cv_not_empty_.notify_all();
    }

    [[nodiscard]] size_t size() const noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }

private:
    const size_t capacity_;
    const size_t high_watermark_;
    const size_t low_watermark_;
    std::queue<DiscreteMessage> queue_;
    mutable std::mutex mutex_;
    std::condition_variable cv_not_full_;
    std::condition_variable cv_not_empty_;
    bool is_closed_{false};
};

// Потоковий розділювач повідомлень (Message Splitter)
class MessageSplitter {
public:
    using DlqHandler = std::function<void(uint64_t corr_id, uint32_t seq, std::string_view reason)>;

    explicit MessageSplitter(std::shared_ptr<BoundedChannel> channel, DlqHandler dlq_handler = nullptr)
        : channel_(std::move(channel)), dlq_handler_(std::move(dlq_handler)) {}

    std::expected<size_t, SplitError> process_stream(std::span<const uint8_t> stream) {
        if (stream.size() < 24) {
            return std::unexpected(SplitError::IncompleteFrameBuffer);
        }

        // 1. Десеріалізація заголовка пакета без копіювання
        uint32_t magic_batch = *reinterpret_cast<const uint32_t*>(stream.data());
        if (magic_batch != MagicBatch) {
            report_dlq(0, 0, "Невірний сигнатурний заголовок пакета");
            return std::unexpected(SplitError::InvalidBatchHeader);
        }

        uint64_t correlation_id = *reinterpret_cast<const uint64_t*>(stream.data() + 4);
        uint32_t total_items = *reinterpret_cast<const uint32_t*>(stream.data() + 12);

        size_t offset = 24;
        size_t emitted_count = 0;

        // 2. Ітеративний розбір кадрів елементів
        while (offset + 16 <= stream.size()) {
            uint32_t item_magic = *reinterpret_cast<const uint32_t*>(stream.data() + offset);
            uint32_t seq_num = *reinterpret_cast<const uint32_t*>(stream.data() + offset + 4);
            uint32_t payload_len = *reinterpret_cast<const uint32_t*>(stream.data() + offset + 8);
            uint16_t item_flags = *reinterpret_cast<const uint16_t*>(stream.data() + offset + 12);

            if (item_magic != MagicItem) {
                report_dlq(correlation_id, seq_num, "Пошкоджено сигнатуру кадру елемента");
                break;
            }

            size_t total_frame_len = 16 + payload_len + 4;
            if (offset + total_frame_len > stream.size()) {
                break; // Буфер закінчився посеред кадру
            }

            std::span<const uint8_t> payload_span(stream.data() + offset + 16, payload_len);
            uint32_t expected_crc = *reinterpret_cast<const uint32_t*>(stream.data() + offset + 16 + payload_len);

            // 3. Валідація контрольної суми кадру
            if (calculate_crc32(payload_span) != expected_crc) {
                report_dlq(correlation_id, seq_num, "Незбіг контрольної суми CRC32");
                offset += total_frame_len;
                continue; // Ізоляція одиничного збою
            }

            // 4. Формування дискретного конверта з метаданими
            DiscreteMessage msg{
                .correlation_id = correlation_id,
                .sequence_number = seq_num,
                .sequence_size = total_items,
                .is_last = ((item_flags & 0x01) != 0) || (seq_num == total_items),
                .payload = std::string(reinterpret_cast<const char*>(payload_span.data()), payload_span.size())
            };

            // 5. Відправка в чергу з підтримкою протитиску
            if (!channel_->push(std::move(msg))) {
                return std::unexpected(SplitError::QueueShutdown);
            }

            emitted_count++;
            offset += total_frame_len;
        }

        return emitted_count;
    }

private:
    void report_dlq(uint64_t corr_id, uint32_t seq, std::string_view reason) const {
        if (dlq_handler_) {
            dlq_handler_(corr_id, seq, reason);
        }
    }

    std::shared_ptr<BoundedChannel> channel_;
    DlqHandler dlq_handler_;
};

} // namespace messaging

int main() {
    using namespace messaging;

    auto channel = std::make_shared<BoundedChannel>(128, 100, 20);
    MessageSplitter splitter(channel, [](uint64_t cid, uint32_t seq, std::string_view reason) {
        std::cout << "[DLQ C++] Пакет 0x" << std::hex << cid << ", Елемент #" << std::dec << seq
                  << " ізольовано. Причина: " << reason << '\n';
    });

    // Підготовка синтетичного двійкового кадру
    std::vector<uint8_t> buffer;
    auto append_val = [&buffer](const auto& val) {
        const auto* ptr = reinterpret_cast<const uint8_t*>(&val);
        buffer.insert(buffer.end(), ptr, ptr + sizeof(val));
    };

    uint32_t magic_b = MagicBatch;
    uint64_t corr_id = 0xFEEDBEEF00112233ULL;
    uint32_t total = 3;
    uint32_t flags = 0;
    uint32_t hcrc = 0;

    append_val(magic_b);
    append_val(corr_id);
    append_val(total);
    append_val(flags);
    append_val(hcrc);

    std::vector<std::string> payloads = {"Order-201:Monitor", "Order-202:CORRUPT", "Order-203:Keyboard"};

    for (uint32_t i = 1; i <= 3; ++i) {
        uint32_t i_magic = MagicItem;
        uint32_t seq = i;
        uint32_t p_len = static_cast<uint32_t>(payloads[i - 1].size());
        uint16_t i_flags = (i == 3) ? 1 : 0;
        uint16_t res = 0;

        append_val(i_magic);
        append_val(seq);
        append_val(p_len);
        append_val(i_flags);
        append_val(res);

        buffer.insert(buffer.end(), payloads[i - 1].begin(), payloads[i - 1].end());

        uint32_t crc = calculate_crc32(std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(payloads[i - 1].data()), p_len));
        if (i == 2) crc ^= 0xCAFEBABE; // Навмисне пошкодження другого елемента
        append_val(crc);
    }

    std::cout << "=== Запуск C++20 Message Splitter ===\n";
    auto result = splitter.process_stream(buffer);

    if (result) {
        std::cout << "Успішно емітовано елементів: " << *result << "\n\n";
    }

    // Зчитування результатів
    while (channel->size() > 0) {
        auto msg = channel->pop();
        if (msg) {
            std::cout << "[C++ Споживач] Елемент " << msg->sequence_number << '/' << msg->sequence_size
                      << " (CorrID: 0x" << std::hex << msg->correlation_id << std::dec
                      << ", Fin: " << std::boolalpha << msg->is_last << "): "
                      << msg->payload_view() << '\n';
        }
    }

    return 0;
}
