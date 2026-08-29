#include "gcs.hpp"

namespace sbo {

Frame Gcs::skeleton(MsgType type, std::uint8_t target) {
    Frame f;
    f.seq = seq_++;
    f.type = type;
    f.source = source_;
    f.target = target;
    f.comp = comp_;
    f.state = armed_ ? State::Armed : State::Idle;
    f.cmd = cmd_;
    return f;
}

std::vector<std::uint8_t> Gcs::select(std::uint8_t target, Comp comp, Cmd cmd, Ms window) {
    // Намір запам'ятовуємо ще до квитанції: повтори за N_retry мусять нести
    // той самий вибір, інакше борт побачить два різні запити.
    target_ = target;
    comp_ = comp;
    cmd_ = cmd;
    window_ = window;
    token_ = 0;
    armed_ = false;

    Frame f = skeleton(MsgType::SelectReq, target);
    f.window = window;
    return encode(f);
}

std::vector<std::uint8_t> Gcs::operate(std::vector<std::uint8_t> params) {
    Frame f = skeleton(MsgType::OperateReq, target_);
    f.token = token_;
    f.payload = std::move(params);
    return encode(f);
}

std::vector<std::uint8_t> Gcs::cancel() {
    Frame f = skeleton(MsgType::CancelReq, target_);
    f.token = token_;
    return encode(f);
}

std::vector<std::uint8_t> Gcs::ping(std::uint8_t target) {
    Frame f = skeleton(MsgType::StatusPing, target);
    f.cmd = Cmd::None;
    return encode(f);
}

void Gcs::on_reply(const Frame& r) {
    switch (r.type) {
        case MsgType::SelectAck:
            token_ = r.token;
            window_ = r.window;          // борт міг підрізати вікно під межі
            armed_ = true;
            last_error_.reset();
            break;
        case MsgType::SelectNack:
        case MsgType::OperateNack:
            armed_ = false;
            token_ = 0;
            last_error_ = r.reason();
            break;
        case MsgType::OperateAck:
        case MsgType::CancelAck:
            armed_ = false;
            token_ = 0;
            last_error_ = r.reason();
            break;
        case MsgType::StatusPong:
            // Розділ 8: борт звітує ARMED, а пульт вважає замок вільним —
            // уявлення розійшлися, потрібен примусовий CANCEL_REQ.
            if (!r.payload.empty() && (r.payload.front() & kFlagArmed) && !armed_) {
                last_error_ = Error::Busy;
            }
            break;
        default:
            break;
    }
}

}  // namespace sbo
