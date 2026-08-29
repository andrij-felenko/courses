// sender.hpp — автомат передавача Stop-and-Wait.
//
// Idle ──send──▶ WaitAck ──Ack──▶ Idle
//                   │  ▲
//         RTO/Nack  │  │ повтор
//                   ▼  │
//            (retries < kMaxRetries) ──ні──▶ Failed → доповідь → Idle
#pragma once

#include "frame.hpp"
#include "rto_estimator.hpp"

#include <array>
#include <chrono>
#include <cstdint>
#include <expected>
#include <functional>
#include <span>
#include <utility>

namespace arq {

enum class SenderState : std::uint8_t { Idle, WaitAck, Failed };
enum class SendError : std::uint8_t { Busy, PayloadTooBig };

class Sender {
public:
    using Ms      = std::chrono::milliseconds;
    using WireOut = std::function<void(std::span<const std::uint8_t>)>;
    using Report  = std::function<void(bool delivered, std::uint8_t seq)>;

    struct Stats {
        unsigned sent{};
        unsigned retransmitted{};
        unsigned acked{};
        unsigned failed{};
        unsigned stray{};
    };

    // На МК тут доречніший невеликий делегат без купи; std::function узято
    // заради читабельності прикладу, логіка автомата від цього не залежить.
    Sender(WireOut out, Report report)
        : out_{std::move(out)}, report_{std::move(report)} {}

    std::expected<void, SendError> send(std::span<const std::uint8_t> payload, Ms now)
    {
        if (state_ != SenderState::Idle) {
            return std::unexpected(SendError::Busy); // у польоті рівно один кадр
        }
        const auto frame = Frame::make(Type::Data, seq_, payload);
        if (!frame) {
            return std::unexpected(SendError::PayloadTooBig);
        }
        // Пакуємо один раз: повтор шле байт-у-байт ту саму копію.
        const auto wire = encode(*frame, wireBuf_);
        if (!wire) {
            return std::unexpected(SendError::PayloadTooBig);
        }

        wireLen_       = wire->size();
        retries_       = 0;
        retransmitted_ = false;
        state_         = SenderState::WaitAck;
        ++stats_.sent;
        emit(now);
        return {};
    }

    void poll(Ms now)
    {
        if (state_ != SenderState::WaitAck) {
            return;
        }
        if (now - sentAt_ < rto_.value()) {
            return;
        }
        retry(now, /*backoff=*/true);
    }

    void onWire(std::span<const std::uint8_t> wire, Ms now)
    {
        const auto frame = decode(wire);
        if (!frame) {
            ++stats_.stray; // биту квитанцію лікує таймаут
            return;
        }
        if (state_ != SenderState::WaitAck || frame->seq() != seq_) {
            ++stats_.stray; // квитанція з попереднього кола або не на часі
            return;
        }

        switch (frame->type()) {
        case Type::Ack:
            if (!retransmitted_) {
                rto_.addSample(now - sentAt_); // Карн №1
            }
            seq_ ^= 1u; // чергування біта: 0,1,0,1,…
            state_ = SenderState::Idle;
            ++stats_.acked;
            if (report_) {
                report_(true, frame->seq());
            }
            break;

        case Type::Nack:
            // Приймач явно сказав «кадр побитий» — повторюємо негайно.
            // RTO не подвоюємо: канал живий, це завада, а не перевантаження.
            retry(now, /*backoff=*/false);
            break;

        default:
            ++stats_.stray;
            break;
        }
    }

    [[nodiscard]] SenderState state() const noexcept { return state_; }
    [[nodiscard]] std::uint8_t seq() const noexcept { return seq_; }
    [[nodiscard]] const RtoEstimator& rto() const noexcept { return rto_; }
    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }

private:
    void emit(Ms now)
    {
        sentAt_ = now;
        if (out_) {
            out_(std::span<const std::uint8_t>{wireBuf_.data(), wireLen_});
        }
    }

    void retry(Ms now, bool backoff)
    {
        if (retries_ >= kMaxRetries) {
            state_ = SenderState::Failed;
            ++stats_.failed;
            if (report_) {
                report_(false, seq_);
            }
            // Номер НЕ чергуємо: якщо приймач насправді отримав дані, а до нас
            // не дійшла жодна квитанція, зміна номера змусила б його прийняти
            // наступний кадр за дублікат. Перевстановлення сесії — справа
            // прикладного рівня, протокол лише чесно доповів про відмову.
            state_ = SenderState::Idle;
            return;
        }

        ++retries_;
        retransmitted_ = true; // Карн №1: вимір RTT уже негодящий
        ++stats_.retransmitted;
        if (backoff) {
            rto_.backoff();
        }
        emit(now);
    }

    WireOut     out_;
    Report      report_;
    SenderState state_{SenderState::Idle};
    std::uint8_t seq_{0};
    unsigned     retries_{0};
    Ms           sentAt_{0};
    bool         retransmitted_{false};

    std::array<std::uint8_t, kMaxFrame> wireBuf_{};
    std::size_t  wireLen_{0};

    RtoEstimator rto_{};
    Stats        stats_{};
};

} // namespace arq
