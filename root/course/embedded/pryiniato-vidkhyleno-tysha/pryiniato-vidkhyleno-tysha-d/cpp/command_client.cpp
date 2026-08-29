#include "command_client.h"

#include <type_traits>
#include <utility>

namespace {
// Повний обіг кадру в реальному ефірі — 120…250 мс. Коротший таймаут не лікує
// втрату, а породжує шторм повторів і забиває буфер UART модема.
constexpr std::chrono::milliseconds kMinRetryInterval{250};
}  // namespace

const char* state_name(TxState s) {
    switch (s) {
        case TxState::Idle:           return "IDLE";
        case TxState::WaitingAck:     return "WAITING_ACK";
        case TxState::InProgress:     return "IN_PROGRESS";
        case TxState::Success:        return "SUCCESS";
        case TxState::Rejected:       return "REJECTED";
        case TxState::TimeoutFailure: return "TIMEOUT_FAILURE";
    }
    return "?";
}

CommandClient::CommandClient(ILink& link,
                             std::uint8_t gcs_system,
                             std::uint8_t gcs_component,
                             std::chrono::milliseconds retry_interval,
                             std::uint8_t max_retries)
    : link_(link),
      gcs_system_(gcs_system),
      gcs_component_(gcs_component),
      retry_interval_(retry_interval),
      max_retries_(max_retries) {
    if (retry_interval < kMinRetryInterval) {
        throw std::invalid_argument(
            "інтервал повтору коротший за час обігу кадру в ефірі — це шторм повторів");
    }
    if (max_retries == 0 || max_retries > 10) {
        throw std::invalid_argument("MAX_RETRIES поза розумними межами 1…10");
    }
}

bool CommandClient::send(TimePoint now, CommandLong frame, DoneCb on_done, ProgressCb on_progress) {
    if (busy()) {
        return false;
    }
    if (frame.target_system == 0) {
        // Широкомовний кадр отримають усі борти, а квитанції не буде з ким зіставити.
        throw std::invalid_argument("широкомовна адреса 0 заборонена для командної транзакції");
    }
    frame.confirmation  = 0;  // нова окрема дія завжди починається з нуля
    frame.src_system    = gcs_system_;
    frame.src_component = gcs_component_;

    command_          = frame.command;
    target_system_    = frame.target_system;
    target_component_ = frame.target_component;
    pending_          = std::move(frame);

    start(now, std::move(on_done), std::move(on_progress));
    return true;
}

bool CommandClient::send(TimePoint now, CommandInt frame, DoneCb on_done, ProgressCb on_progress) {
    if (busy()) {
        return false;
    }
    if (frame.target_system == 0) {
        throw std::invalid_argument("широкомовна адреса 0 заборонена для командної транзакції");
    }
    frame.src_system    = gcs_system_;
    frame.src_component = gcs_component_;

    command_          = frame.command;
    target_system_    = frame.target_system;
    target_component_ = frame.target_component;
    pending_          = std::move(frame);

    start(now, std::move(on_done), std::move(on_progress));
    return true;
}

void CommandClient::start(TimePoint now, DoneCb on_done, ProgressCb on_progress) {
    on_done_     = std::move(on_done);
    on_progress_ = std::move(on_progress);
    retries_     = 0;
    state_       = TxState::WaitingAck;
    transmit();
    deadline_ = now + retry_interval_;
}

void CommandClient::transmit() {
    std::visit(
        [this](const auto& frame) {
            using T = std::decay_t<decltype(frame)>;
            if constexpr (!std::is_same_v<T, std::monostate>) {
                link_.send(frame);
            }
        },
        pending_);
}

void CommandClient::on_ack(TimePoint now, const CommandAck& ack) {
    if (!busy()) {
        return;  // активної транзакції немає — квитанція чужа або запізніла
    }
    if (ack.command != command_) {
        return;  // ACK на іншу команду з фонового потоку
    }
    if (ack.src_system != target_system_ || ack.src_component != target_component_) {
        return;  // відповів не той компонент, якому ми адресували наказ
    }
    if (ack.target_system != 0 &&
        (ack.target_system != gcs_system_ || ack.target_component != gcs_component_)) {
        return;  // квитанція адресована іншій станції в тій самій мережі
    }

    if (ack.result == MavResult::InProgress) {
        // Довга операція жива: таймаут відсуваємо, повтору не робимо.
        state_    = TxState::InProgress;
        deadline_ = now + retry_interval_;
        if (on_progress_ && ack.progress != 255) {
            on_progress_(ack.progress);
        }
        return;
    }

    if (ack.result == MavResult::Accepted) {
        finish(TxState::Success, ack.result, ack.result_param2, "команду виконано");
        return;
    }

    // Будь-яка інша квитанція — остаточний вердикт: пакет дійшов, борт відмовив.
    // Повторювати заборонено: справа не в радіозв'язку, а в стані системи.
    finish(TxState::Rejected, ack.result, ack.result_param2,
           std::string("борт відмовив: ") + result_name(ack.result));
}

void CommandClient::tick(TimePoint now) {
    if (!busy() || now < deadline_) {
        return;
    }

    if (retries_ >= max_retries_) {
        finish(TxState::TimeoutFailure, MavResult::Failed, 0,
               "тиша: борт не відповів, фізичний стан апарата НЕВІДОМИЙ");
        return;
    }

    ++retries_;
    if (auto* frame = std::get_if<CommandLong>(&pending_)) {
        // Лічильник повторів: борт із нього бачить, що це та сама транзакція,
        // і не виконує неідемпотентну дію вдруге.
        frame->confirmation = retries_;
    }
    // У COMMAND_INT поля confirmation немає — повтор іде байт-у-байт, тому цим
    // контейнером шлють лише ідемпотентні навігаційні накази.
    state_ = TxState::WaitingAck;
    transmit();
    deadline_ = now + retry_interval_;
}

void CommandClient::finish(TxState state, MavResult result, std::int32_t param2, std::string message) {
    last_ = Outcome{state, result, param2, static_cast<unsigned>(retries_) + 1u, std::move(message)};
    // Стан лишається термінальним, доки не почнеться наступна транзакція:
    // саме за ним інтерфейс розблоковує кнопку й показує причину.
    state_   = state;
    pending_ = std::monostate{};
    on_progress_ = nullptr;

    auto cb  = std::move(on_done_);
    on_done_ = nullptr;
    if (cb) {
        cb(last_);
    }
}
