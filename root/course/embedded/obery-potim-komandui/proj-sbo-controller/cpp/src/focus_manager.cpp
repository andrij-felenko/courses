// focus_manager.cpp — контекст оператора: селекція, квитанції, втрата звʼязку.
#include "gcs/focus_manager.hpp"

#include <algorithm>

namespace gcs {
namespace {
constexpr std::uint32_t kRed   = 0xD0342Cu;
constexpr std::uint32_t kGreen = 0x2E9E4Fu;
constexpr std::uint32_t kAmber = 0xE0A800u;
constexpr std::uint32_t kGrey  = 0x6E6E6Eu;
}  // namespace

FocusManager::FocusManager(sbo::NodeId self) noexcept : self_(self) {}

sbo::Frame FocusManager::request(sbo::MessageType type) noexcept {
    sbo::Frame tx{};
    tx.seq       = ++seq_;
    tx.type      = type;
    tx.source    = self_;
    tx.target    = target_;
    tx.component = component_;
    tx.command   = pending_cmd_;
    return tx;
}

std::expected<sbo::Frame, sbo::Error>
FocusManager::select(sbo::NodeId target, std::uint8_t component, std::string_view name,
                     sbo::CommandCode cmd, std::chrono::milliseconds window,
                     TimePoint now) noexcept {
    // Відсікаємо широкомовну селекцію вже на пульті: борт її теж відкине, але
    // оператор не мусить бачити на екрані «вибрано всіх».
    if (target.is_broadcast() || target == self_ || target.value == 0) {
        last_error_ = sbo::Error::BroadcastForbidden;
        return std::unexpected(sbo::Error::BroadcastForbidden);
    }

    target_      = target;
    component_   = component;
    name_.fill('\0');
    std::copy_n(name.begin(), std::min(name.size(), kNameLen - 1), name_.begin());
    pending_cmd_ = cmd;
    window_      = std::clamp(window.count() > 0 ? window : sbo::kDefaultWindow,
                              std::chrono::milliseconds{1}, sbo::kMaxWindow);
    token_       = sbo::Token{};              // старий токен нової селекції не переживає
    status_      = Status::WaitAck;
    last_error_  = sbo::Error::InternalFault;
    sent_at_     = now;
    ack_deadline_    = now + kAckTimeout;
    select_deadline_ = TimePoint{};

    sbo::Frame tx = request(sbo::MessageType::SelectReq);
    tx.timeout    = window_;
    return tx;
}

void FocusManager::tick(TimePoint now) noexcept {
    switch (status_) {
    case Status::WaitAck:
    case Status::WaitOp:
        if (now >= ack_deadline_) {
            // Канал мовчить: картка червоніє, кнопка дії гасне. Оператор не має
            // права вважати апарат готовим, поки квитанції немає.
            status_     = Status::LinkLost;
            token_      = sbo::Token{};
            last_error_ = sbo::Error::TimeoutExpired;
        }
        break;
    case Status::Armed:
        if (now >= select_deadline_) {
            status_ = Status::Expired;
            token_  = sbo::Token{};
        }
        break;
    default:
        break;
    }
}

void FocusManager::on_response(const sbo::Frame& rx, TimePoint now) noexcept {
    if (rx.source != target_ || rx.target != self_) {
        return;   // відповідь не від того апарата або не нам
    }

    switch (rx.type) {
    case sbo::MessageType::SelectAck: {
        if (status_ != Status::WaitAck) {
            return;   // запізніла квитанція після втрати звʼязку
        }
        if (rx.command != pending_cmd_) {
            status_     = Status::Rejected;
            last_error_ = sbo::Error::CommandMismatch;
            return;
        }
        token_  = rx.token;
        status_ = Status::Armed;
        // Вікно рахуємо від МОМЕНТУ ВІДПРАВКИ (борт відлічує своє від прийому)
        // і забираємо запас на політ команди назад.
        const auto window = rx.timeout.count() > 0 ? rx.timeout : window_;
        const auto usable = window > kGuard ? window - kGuard : window / 2;
        select_deadline_  = sent_at_ + usable;
        break;
    }

    case sbo::MessageType::SelectNack:
    case sbo::MessageType::OperateNack:
    case sbo::MessageType::CancelNack:
        status_     = Status::Rejected;
        last_error_ = rx.payload_len > 0 ? static_cast<sbo::Error>(rx.payload[0])
                                         : sbo::Error::InternalFault;
        token_      = sbo::Token{};
        break;

    case sbo::MessageType::OperateAck:
        status_ = Status::Done;
        token_  = sbo::Token{};
        break;

    case sbo::MessageType::CancelAck:
        status_ = Status::None;
        token_  = sbo::Token{};
        break;

    default:
        break;
    }
    (void)now;
}

std::expected<sbo::Frame, sbo::Error>
FocusManager::build_operate(std::span<const std::uint8_t> payload, TimePoint now) noexcept {
    if (payload.size() > sbo::kMaxPayload) {
        return std::unexpected(sbo::Error::BadLength);
    }
    tick(now);   // стан міг протухнути між перемальовуваннями
    if (status_ != Status::Armed || !token_.valid()) {
        return std::unexpected(status_ == Status::Expired ? sbo::Error::TimeoutExpired
                                                          : sbo::Error::NotArmed);
    }

    sbo::Frame tx = request(sbo::MessageType::OperateReq);
    tx.token      = token_;
    tx.set_data(payload);

    // Локальний замок теж одноразовий: другий клік вимагатиме нової селекції.
    token_        = sbo::Token{};
    status_       = Status::WaitOp;
    sent_at_      = now;
    ack_deadline_ = now + kAckTimeout;
    return tx;
}

std::expected<sbo::Frame, sbo::Error> FocusManager::build_cancel(TimePoint now) noexcept {
    if (status_ == Status::None || target_.value == 0) {
        return std::unexpected(sbo::Error::NotArmed);
    }
    sbo::Frame tx = request(sbo::MessageType::CancelReq);
    token_        = sbo::Token{};
    status_       = Status::WaitOp;
    sent_at_      = now;
    ack_deadline_ = now + kAckTimeout;
    return tx;
}

bool FocusManager::button_enabled(TimePoint now) const noexcept {
    return status_ == Status::Armed && token_.valid() && now < select_deadline_;
}

std::string_view FocusManager::target_name() const noexcept {
    const auto end = std::find(name_.begin(), name_.end(), '\0');
    return std::string_view{name_.data(), static_cast<std::size_t>(end - name_.begin())};
}

std::string_view FocusManager::badge() const noexcept {
    switch (status_) {
    case Status::None:     return "Апарат не обрано";
    case Status::WaitAck:  return "Очікування квитанції…";
    case Status::Armed:    return "Замок зведено";
    case Status::WaitOp:   return "Команду надіслано…";
    case Status::Done:     return "Виконано";
    case Status::LinkLost: return "Втрата зв'язку";
    case Status::Rejected: return sbo::to_string(last_error_);
    case Status::Expired:  return "Вікно вибору спливло";
    default:               return "";
    }
}

std::uint32_t FocusManager::frame_color() const noexcept {
    switch (status_) {
    case Status::Armed:
    case Status::Done:     return kGreen;
    case Status::WaitAck:
    case Status::WaitOp:   return kAmber;
    case Status::LinkLost:
    case Status::Rejected: return kRed;
    default:               return kGrey;
    }
}

}  // namespace gcs
