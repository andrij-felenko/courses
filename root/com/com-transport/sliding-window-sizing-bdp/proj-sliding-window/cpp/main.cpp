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
