#include "sim_vehicle.h"

#include "command_client.h"

#include <iostream>

const char* mode_name(std::int32_t mode) {
    switch (mode) {
        case copter_mode::Stabilize: return "STABILIZE";
        case copter_mode::Auto:      return "AUTO";
        case copter_mode::Guided:    return "GUIDED";
        case copter_mode::Rtl:       return "RTL";
        default:                     return "CUSTOM";
    }
}

bool SimAutopilot::addressed_to_us(std::uint8_t sys, std::uint8_t comp) const {
    return sys == system_id_ && (comp == component_id_ || comp == 0);
}

std::optional<CommandAck> SimAutopilot::handle(TimePoint now, const CommandLong& frame) {
    if (!powered_) {
        return std::nullopt;  // тиша: борт знеструмлено або заблоковано
    }
    if (!addressed_to_us(frame.target_system, frame.target_component)) {
        return std::nullopt;  // кадр не нашому компоненту
    }

    const bool same_transaction = cache_.valid && cache_.command == frame.command &&
                                  cache_.target_system == frame.target_system &&
                                  cache_.target_component == frame.target_component &&
                                  (now - cache_.stamp) <= kTxWindow;

    if (dedup_ && frame.confirmation > 0 && same_transaction) {
        // Станція не почула ACK і повторює ту саму транзакцію. Виконавчий
        // механізм НЕ чіпаємо — просто віддаємо збережений результат ще раз.
        std::cout << "  [борт] повтор conf=" << static_cast<int>(frame.confirmation)
                  << " розпізнано кешем, дію не повторюємо\n";
        cache_.last_confirmation = frame.confirmation;
        return make_ack(frame, cache_.result, cache_.result_param2);
    }

    CommandAck ack = execute(now, frame);

    cache_.valid             = true;
    cache_.target_system     = frame.target_system;
    cache_.target_component  = frame.target_component;
    cache_.command           = frame.command;
    cache_.last_confirmation = frame.confirmation;
    cache_.result            = ack.result;
    cache_.result_param2     = ack.result_param2;
    cache_.stamp             = now;
    return ack;
}

std::optional<CommandAck> SimAutopilot::handle(TimePoint now, const CommandInt& frame) {
    (void)now;
    if (!powered_) {
        return std::nullopt;
    }
    if (!addressed_to_us(frame.target_system, frame.target_component)) {
        return std::nullopt;
    }
    // Дедуплікації тут немає: у COMMAND_INT немає поля confirmation, тому повтор
    // не відрізнити від нового наказу. Через цей контейнер шлють лише ідемпотентне.
    return execute(frame);
}

CommandAck SimAutopilot::execute(TimePoint now, const CommandLong& frame) {
    switch (frame.command) {
        case mav_cmd::ComponentArmDisarm: {
            const bool want_arm = frame.param[0] > 0.5f;
            if (want_arm) {
                if (!gps_fix_) {
                    return make_ack(frame, MavResult::Denied, deny_reason::NoGpsFix);
                }
                armed_ = true;  // ідемпотентно: повторний ARM нічого не змінює
                return make_ack(frame, MavResult::Accepted);
            }
            if (in_air_ && frame.param[1] != kForceDisarmMagic) {
                return make_ack(frame, MavResult::Denied, deny_reason::ArmedInAir);
            }
            armed_  = false;
            in_air_ = false;
            return make_ack(frame, MavResult::Accepted);
        }

        case mav_cmd::DoSetMode: {
            if (frame.param[0] != kCustomModeEnabled) {
                return make_ack(frame, MavResult::Unsupported);
            }
            const auto wanted = static_cast<std::int32_t>(frame.param[1]);
            if (wanted == copter_mode::Auto && !ekf_ready_) {
                // Динамічний стан заважає просто зараз — за кілька секунд варто повторити.
                return make_ack(frame, MavResult::TemporarilyRejected, deny_reason::EkfNotReady);
            }
            mode_ = wanted;  // абсолютний цільовий стан: ідемпотентно
            return make_ack(frame, MavResult::Accepted);
        }

        case mav_cmd::NavTakeoff: {
            if (!armed_) {
                return make_ack(frame, MavResult::TemporarilyRejected);
            }
            in_air_ = true;
            return make_ack(frame, MavResult::Accepted);
        }

        case mav_cmd::DoGripper: {
            // param2: 0 — відпустити, 1 — захопити, 2 — перемкнути (неідемпотентно).
            const auto action = static_cast<int>(frame.param[1]);
            if (action == 2) {
                gripper_closed_ = !gripper_closed_;
            } else if (action == 0 || action == 1) {
                gripper_closed_ = (action == 1);
            } else {
                return make_ack(frame, MavResult::Failed);
            }
            ++gripper_actuations_;  // сервопривід реально клацнув
            std::cout << "  [борт] замок спрацював, тепер "
                      << (gripper_closed_ ? "закрито" : "відкрито")
                      << " (усього спрацювань: " << gripper_actuations_ << ")\n";
            return make_ack(frame, MavResult::Accepted);
        }

        case mav_cmd::DoDigicamControl: {
            if (frame.param[4] > 0.5f) {
                ++photos_;  // затвор клацнув — теж неідемпотентна дія
            }
            return make_ack(frame, MavResult::Accepted);
        }

        case mav_cmd::DoStartMagCal: {
            // Довга операція: одразу IN_PROGRESS, далі періодичні звіти прогресу
            // й фінальний ACCEPTED. Кожен звіт скидає таймаут станції.
            reports_.clear();
            reports_.push_back({now + std::chrono::milliseconds(400),
                                make_ack(frame, MavResult::InProgress, 0, 25)});
            reports_.push_back({now + std::chrono::milliseconds(800),
                                make_ack(frame, MavResult::InProgress, 0, 50)});
            reports_.push_back({now + std::chrono::milliseconds(1200),
                                make_ack(frame, MavResult::InProgress, 0, 75)});
            reports_.push_back({now + std::chrono::milliseconds(1600),
                                make_ack(frame, MavResult::Accepted)});
            return make_ack(frame, MavResult::InProgress, 0, 0);
        }

        default:
            if (requires_command_int(frame.command)) {
                // Навігаційний наказ у неправильному контейнері: координати
                // у float32 втратили б понад 40 см ще до розбору.
                return make_ack(frame, MavResult::CommandIntOnly);
            }
            return make_ack(frame, MavResult::Unsupported);
    }
}

CommandAck SimAutopilot::execute(const CommandInt& frame) {
    switch (frame.command) {
        case mav_cmd::NavLoiterUnlim: {
            if (frame.frame != MavFrame::GlobalRelativeAltInt && frame.frame != MavFrame::GlobalInt) {
                return make_ack(frame, MavResult::Unsupported);
            }
            loiter_lat_ = frame.x;
            loiter_lon_ = frame.y;
            loiter_alt_ = frame.z;
            std::cout << "  [борт] точка очікування: " << deg_from_1e7(loiter_lat_) << ", "
                      << deg_from_1e7(loiter_lon_) << " на " << loiter_alt_ << " м\n";
            return make_ack(frame, MavResult::Accepted);
        }
        case mav_cmd::DoGripper:
        case mav_cmd::DoDigicamControl:
        case mav_cmd::ComponentArmDisarm:
            // Ці накази несуть лічильник повторів, тож приймаються лише в COMMAND_LONG.
            return make_ack(frame, MavResult::CommandLongOnly);
        default:
            return make_ack(frame, MavResult::Unsupported);
    }
}

std::optional<CommandAck> SimAutopilot::poll(TimePoint now) {
    if (!powered_ || reports_.empty() || reports_.front().due > now) {
        return std::nullopt;
    }
    CommandAck ack = reports_.front().ack;
    reports_.pop_front();
    return ack;
}

void SimRadio::send(const CommandLong& frame) {
    std::cout << "  [TX] COMMAND_LONG cmd=" << frame.command << " ціль="
              << static_cast<int>(frame.target_system) << ":"
              << static_cast<int>(frame.target_component)
              << " conf=" << static_cast<int>(frame.confirmation) << "\n";
    enqueue_uplink(frame);
}

void SimRadio::send(const CommandInt& frame) {
    std::cout << "  [TX] COMMAND_INT cmd=" << frame.command << " ціль="
              << static_cast<int>(frame.target_system) << ":"
              << static_cast<int>(frame.target_component)
              << " x=" << frame.x << " y=" << frame.y << "\n";
    enqueue_uplink(frame);
}

void SimRadio::enqueue_uplink(std::variant<CommandLong, CommandInt> frame) {
    if (drop_up_ > 0) {
        --drop_up_;
        std::cout << "  [ефір] кадр Uplink спотворено шумом, CRC не зійшлася\n";
        return;
    }
    if (up_.size() >= kModemQueueDepth) {
        std::cout << "  [ефір] буфер UART модема переповнено — кадр відкинуто\n";
        return;
    }
    up_.push_back({now_ + uplink_delay_, std::move(frame)});
}

void SimRadio::enqueue_downlink(const CommandAck& ack) {
    if (drop_down_ > 0) {
        --drop_down_;
        std::cout << "  [ефір] квитанція Downlink загинула — дія на борту ВЖЕ виконана\n";
        return;
    }
    down_.push_back({now_ + downlink_delay_, ack});
}

void SimRadio::tick(TimePoint now) {
    now_ = now;

    // 1) кадри, що пролетіли вгору, потрапляють у обробник борту
    while (!up_.empty() && up_.front().due <= now) {
        auto frame = std::move(up_.front().frame);
        up_.pop_front();
        auto ack = std::visit([&](const auto& f) { return vehicle_.handle(now, f); }, frame);
        if (ack) {
            enqueue_downlink(*ack);
        }
    }

    // 2) проміжні звіти довгої операції
    while (auto report = vehicle_.poll(now)) {
        enqueue_downlink(*report);
    }

    // 3) квитанції, що дозріли на зворотному шляху
    while (!down_.empty() && down_.front().due <= now) {
        const CommandAck ack = down_.front().ack;
        down_.pop_front();
        if (client_) {
            client_->on_ack(now, ack);
        }
    }
}
