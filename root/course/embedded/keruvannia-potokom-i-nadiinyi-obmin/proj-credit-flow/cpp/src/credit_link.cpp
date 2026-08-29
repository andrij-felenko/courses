#include "credit_link.hpp"

#include <algorithm>

namespace credit {

// --- Кадр -------------------------------------------------------------------

Frame Frame::make_data(std::uint8_t seq, std::span<const std::uint8_t> payload) noexcept
{
    Frame frame;
    frame.kind_ = FrameKind::Data;
    frame.seq_ = seq;
    frame.length_ = static_cast<std::uint8_t>(std::min(payload.size(), kMaxPayload));
    std::copy_n(payload.begin(), frame.length_, frame.payload_.begin());
    return frame;
}

Frame Frame::make_grant(std::uint16_t cumulative) noexcept
{
    Frame frame;
    frame.kind_ = FrameKind::Grant;
    frame.cumulative_ = cumulative;
    return frame;
}

Frame Frame::make_poll(std::uint16_t cumulative) noexcept
{
    Frame frame;
    frame.kind_ = FrameKind::Poll;
    frame.cumulative_ = cumulative;
    return frame;
}

std::string_view to_string(LinkState state) noexcept
{
    switch (state) {
    case LinkState::Ready: return "READY";
    case LinkState::Blocked: return "BLOCKED";
    case LinkState::Polling: return "POLLING";
    case LinkState::Dead: return "DEAD";
    }
    return "?";
}

// --- Передавач --------------------------------------------------------------

Sender::Sender(Millis now, std::uint16_t window) noexcept
    : window_{static_cast<std::int32_t>(window)},
      credits_{static_cast<std::int32_t>(window)}, // вікно узгоджене при встановленні зв'язку
      last_event_{now}
{
}

bool Sender::can_send() const noexcept
{
    return state_ != LinkState::Dead && credits_ > 0;
}

std::expected<Frame, SendError> Sender::encode(std::span<const std::uint8_t> payload,
                                               Millis now) noexcept
{
    if (state_ == LinkState::Dead) {
        return std::unexpected{SendError::LinkDown};
    }
    if (payload.size() > kMaxPayload) {
        return std::unexpected{SendError::PayloadTooLong};
    }
    if (credits_ <= 0) {
        return std::unexpected{SendError::NoCredit};
    }

    Frame frame = Frame::make_data(next_seq_++, payload);
    --credits_;
    ++stats_.frames_sent;

    if (credits_ == 0) {
        // Тишу міряємо від миті, коли витратили останній кредит: саме звідси
        // має сенс чекати повернення.
        state_ = LinkState::Blocked;
        last_event_ = now;
        polls_sent_ = 0;
    }
    return frame;
}

void Sender::on_frame(const Frame& frame, Millis now) noexcept
{
    if (state_ == LinkState::Dead) {
        return; // мертвий лінк піднімає лише повторне встановлення зв'язку
    }

    // Різниця беззнакових правильна й після переповнення 16-бітного лічильника.
    const auto delta = static_cast<std::uint16_t>(frame.cumulative_release() - last_cumulative_);

    if (delta > static_cast<std::uint16_t>(window_)) {
        // Приймач фізично не міг звільнити більше слотів, ніж вікно: кадр побито
        // або він від чужого сеансу. Стан не чіпаємо взагалі.
        ++stats_.suspect_grants;
        return;
    }

    if (delta == 0) {
        // Повторений або переставлений кадр. Кумулятивне число робить його
        // безпечним: нічого не додаємо й нічого не ламаємо.
        ++stats_.stale_grants;
    } else {
        last_cumulative_ = frame.cumulative_release();
        credits_ = std::min<std::int32_t>(credits_ + delta, window_); // вікно — тверда стеля
        stats_.credits_granted += delta;
    }

    last_event_ = now;
    if (credits_ > 0) {
        state_ = LinkState::Ready;
        polls_sent_ = 0;
    }
}

std::optional<Frame> Sender::tick(Millis now) noexcept
{
    if (state_ != LinkState::Blocked && state_ != LinkState::Polling) {
        return std::nullopt;
    }
    if (now - last_event_ < kPollTimeout) {
        return std::nullopt;
    }
    if (polls_sent_ >= kMaxPolls) {
        state_ = LinkState::Dead;
        return std::nullopt;
    }

    ++polls_sent_;
    last_event_ = now;
    state_ = LinkState::Polling;
    // Кажемо, що вже зараховано: приймачу видно, наскільки ми відстали.
    return Frame::make_poll(last_cumulative_);
}

// --- Приймач ----------------------------------------------------------------

std::expected<Receiver::Disposition, RxError> Receiver::accept(const Frame& frame) noexcept
{
    switch (frame.kind()) {
    case FrameKind::Poll:
        poll_pending_ = true;
        return Disposition::PollPending;
    case FrameKind::Data:
        break;
    case FrameKind::Grant:
    default:
        ++stats_.malformed; // GRANT у цей бік не ходить
        return std::unexpected{RxError::MalformedFrame};
    }

    if (occupied_ >= slots_.size()) {
        // Класти нікуди: передавач порахував кредити неправильно. Кадр гине,
        // але пам'ять уже прийнятих пакетів лишається цілою.
        ++stats_.over_quota;
        return std::unexpected{RxError::OverQuota};
    }

    if (seq_seen_ && frame.seq() != expected_seq_) {
        ++stats_.seq_gaps;
    }
    expected_seq_ = static_cast<std::uint8_t>(frame.seq() + 1);
    seq_seen_ = true;

    slots_[write_idx_] = frame;
    write_idx_ = (write_idx_ + 1) % slots_.size();
    ++occupied_;
    return Disposition::Stored;
}

std::optional<Frame> Receiver::take() noexcept
{
    if (occupied_ == 0) {
        return std::nullopt;
    }

    Frame frame = slots_[read_idx_];
    read_idx_ = (read_idx_ + 1) % slots_.size();
    --occupied_;
    ++cumulative_; // пам'ять звільнено — росте абсолютний лічильник
    return frame;
}

std::optional<Frame> Receiver::build_grant() noexcept
{
    const auto unreported = static_cast<std::uint16_t>(cumulative_ - last_reported_);

    // Копимо пачку: кожен окремий GRANT коштує стільки ж ефіру, скільки й кадр
    // даних. Але POLL відповідаємо негайно, хай навіть новини нема — саме ця
    // відповідь і виводить лінк зі стопора після втраченого повернення.
    if (!poll_pending_ && unreported < kGrantBatch) {
        return std::nullopt;
    }

    last_reported_ = cumulative_;
    poll_pending_ = false;
    return Frame::make_grant(cumulative_);
}

} // namespace credit
