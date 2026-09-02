#include "gcs_session.hpp"

#include <variant>

namespace manual_control {
namespace {

template <class... Ts>
struct Overloaded : Ts... { using Ts::operator()...; };
template <class... Ts>
Overloaded(Ts...) -> Overloaded<Ts...>;

[[nodiscard]] mavlink::Result toMavResult(ArmVerdict v) noexcept
{
    switch (v) {
    case ArmVerdict::Accepted:
    case ArmVerdict::Disarmed:          return mavlink::Result::Accepted;
    case ArmVerdict::NeedsConfirmation: return mavlink::Result::TemporarilyRejected;
    case ArmVerdict::NoLink:
    case ArmVerdict::StickNotNeutral:
    case ArmVerdict::InFailsafe:        return mavlink::Result::Denied;
    }
    return mavlink::Result::Failed;
}

}  // namespace

void GcsSession::queueAck(std::uint16_t command, mavlink::Result result) noexcept
{
    const mavlink::Message msg{mavlink::CommandAck{.command = command, .result = result}};
    ackLen_ = mavlink::encode(ack_, msg, ourSysid_, ourCompid_, txSeq_++);
}

std::span<const std::byte> GcsSession::takeAck() noexcept
{
    const std::span<const std::byte> out{ack_.data(), ackLen_};
    ackLen_ = 0;
    return out;
}

void GcsSession::onHeartbeat(const mavlink::Frame& f, Millis now) noexcept
{
    // Серцебиття доводить, що жива станція, а не вікно джойстика.
    if (gcsSysid_ == 0 || fromOurGcs(f)) {
        lastHeartbeat_ = now;
        ++stats_.heartbeats;
    }
}

void GcsSession::onManualControl(const mavlink::ManualControl& mc, const mavlink::Frame& f,
                                 Millis now) noexcept
{
    if (mc.target != ourSysid_) {  // кадр адресований іншому апарату
        ++stats_.wrongTarget;
        return;
    }

    if (gcsSysid_ == 0 || (now - lastGcsFrame_) > kGcsRelatch) {
        // Перша авторизована станція фіксується тут; інша перебере керування
        // лише після повної тиші зафіксованої.
        gcsSysid_  = f.sysid;
        gcsCompid_ = f.compid;
    } else if (f.sysid != gcsSysid_) {
        ++stats_.foreign;  // друга станція на тому ж модемі — ігноруємо
        return;
    }

    lastGcsFrame_ = now;
    ++stats_.manual;
    arbiter_.feedManualControl(mc.x, mc.y, mc.z, mc.r, mc.buttons, now);
}

void GcsSession::onCommandLong(const mavlink::CommandLong& cl, const mavlink::Frame& f,
                               Millis now) noexcept
{
    if (cl.targetSystem != ourSysid_ ||
        (cl.targetComponent != ourCompid_ && cl.targetComponent != mavlink::kCompAll)) {
        ++stats_.wrongTarget;
        return;
    }
    if (!fromOurGcs(f)) {
        ++stats_.foreign;
        return;
    }
    if (cl.command != mavlink::kCmdComponentArmDisarm) {
        queueAck(cl.command, mavlink::Result::Unsupported);
        return;
    }

    ++stats_.armCommands;
    const bool arm = cl.param[0] > 0.5F;
    // Поле confirmation: 0 — перша спроба, ≥1 — підтвердження оператора.
    // Арм по одному натисканню кнопки не проходить свідомо.
    const bool confirmed = cl.confirmation >= 1;

    queueAck(cl.command, toMavResult(arbiter_.requestArm(arm, confirmed, now)));
}

void GcsSession::consume(std::span<const std::byte> bytes, Millis now) noexcept
{
    for (const std::byte b : bytes) {
        const auto frame = parser_.push(b);
        if (!frame)
            continue;
        const auto msg = mavlink::decode(*frame);
        if (!msg)
            continue;

        std::visit(Overloaded{
            [&](const mavlink::Heartbeat&) { onHeartbeat(*frame, now); },
            [&](const mavlink::ManualControl& mc) { onManualControl(mc, *frame, now); },
            [&](const mavlink::CommandLong& cl) { onCommandLong(cl, *frame, now); },
            [](const mavlink::CommandAck&) {}  // квитанції борт не приймає
        }, *msg);
    }
}

}  // namespace manual_control
