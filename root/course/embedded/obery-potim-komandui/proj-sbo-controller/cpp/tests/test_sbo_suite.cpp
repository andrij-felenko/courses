// test_sbo_suite.cpp — ті самі інваріанти безпеки, перевірені на C++-реалізації.
#include "gcs/focus_manager.hpp"
#include "sbo/target_engine.hpp"

#include <cstdio>

namespace {

int g_checks = 0;
int g_failed = 0;

#define CHECK(cond)                                                          \
    do {                                                                     \
        ++g_checks;                                                          \
        if (!(cond)) {                                                       \
            ++g_failed;                                                      \
            std::printf("  ПРОВАЛ %s:%d — %s\n", __FILE__, __LINE__, #cond); \
        }                                                                    \
    } while (false)

// Плата в тесті: замість реле й GPIO — лічильники.
class TestBoard final : public sbo::Board {
public:
    bool execute(sbo::CommandCode cmd, std::span<const std::uint8_t> payload) noexcept override {
        ++exec_calls;
        last_cmd     = cmd;
        last_payload = payload.size();
        if (fail_next) {
            fail_next = false;
            return false;   // привід відзвітував про відмову
        }
        return true;
    }
    void diag_level(sbo::DiagLine line, bool high) noexcept override {
        if (line == sbo::DiagLine::Armed) {
            armed_level = high;
        }
    }
    void diag_pulse(sbo::DiagLine line, std::chrono::microseconds) noexcept override {
        if (line == sbo::DiagLine::OperateExec) {
            ++exec_pulses;
        } else if (line == sbo::DiagLine::SecurityDrop) {
            ++drop_pulses;
        }
    }

    int              exec_calls{0};
    int              exec_pulses{0};
    int              drop_pulses{0};
    std::size_t      last_payload{0};
    sbo::CommandCode last_cmd{};
    bool             fail_next{false};
    bool             armed_level{false};
};

constexpr sbo::NodeId      kTarget{0x02};
constexpr sbo::NodeId      kGcs{0xFE};
constexpr sbo::NodeId      kOther{0xFD};
constexpr sbo::CommandCode kCmdArm{0x0101};

using Clock = sbo::TargetEngine::Clock;
const Clock::time_point kT0 = Clock::now();

sbo::Frame make_request(sbo::MessageType type, sbo::NodeId source, sbo::NodeId target,
                        sbo::CommandCode cmd, sbo::Token token = sbo::Token{},
                        std::chrono::milliseconds window = std::chrono::milliseconds{0}) {
    sbo::Frame f{};
    f.type    = type;
    f.source  = source;
    f.target  = target;
    f.command = cmd;
    f.token   = token;
    f.timeout = window;
    return f;
}

// 1. Пряма команда без фази вибору.
void test_operate_without_select() {
    TestBoard board;
    sbo::TargetEngine node{kTarget, board, 0x12345678u};

    const auto rx  = make_request(sbo::MessageType::OperateReq, kGcs, kTarget, kCmdArm,
                                  sbo::Token{0x9999});
    const auto res = node.process(rx, kT0);

    CHECK(res.has_value());
    CHECK(res->type == sbo::MessageType::OperateNack);
    CHECK(res->payload[0] == static_cast<std::uint8_t>(sbo::Error::NotArmed));
    CHECK(node.state() == sbo::State::Idle);
    CHECK(board.exec_calls == 0);
}

// 2. Номінальний цикл у межах вікна.
void test_nominal_cycle() {
    using namespace std::chrono_literals;
    TestBoard board;
    sbo::TargetEngine node{kTarget, board, 0x12345678u};

    const auto sel = node.process(
        make_request(sbo::MessageType::SelectReq, kGcs, kTarget, kCmdArm, sbo::Token{}, 5000ms), kT0);
    CHECK(sel.has_value());
    CHECK(sel->type == sbo::MessageType::SelectAck);
    CHECK(sel->token.valid());
    CHECK(node.state() == sbo::State::Armed);
    CHECK(board.armed_level);

    const auto op = node.process(
        make_request(sbo::MessageType::OperateReq, kGcs, kTarget, kCmdArm, sel->token), kT0 + 1500ms);
    CHECK(op.has_value());
    CHECK(op->type == sbo::MessageType::OperateAck);
    CHECK(node.state() == sbo::State::Idle);   // селектор одноразовий
    CHECK(board.exec_calls == 1);
    CHECK(board.last_cmd == kCmdArm);
    CHECK(board.exec_pulses == 1);
    CHECK(!board.armed_level);
}

// 3. Дія після спливання вікна: саме TimeoutExpired, а не «не зведено».
void test_timeout_expired() {
    using namespace std::chrono_literals;
    TestBoard board;
    sbo::TargetEngine node{kTarget, board, 0xA1B2C3D4u};

    const auto sel = node.process(
        make_request(sbo::MessageType::SelectReq, kGcs, kTarget, kCmdArm, sbo::Token{}, 5000ms), kT0);
    CHECK(sel.has_value());

    const auto late = node.process(
        make_request(sbo::MessageType::OperateReq, kGcs, kTarget, kCmdArm, sel->token), kT0 + 6000ms);
    CHECK(late.has_value());
    CHECK(late->type == sbo::MessageType::OperateNack);
    CHECK(late->payload[0] == static_cast<std::uint8_t>(sbo::Error::TimeoutExpired));
    CHECK(node.state() == sbo::State::Idle);
    CHECK(node.timeout_count() == 1);
    CHECK(board.exec_calls == 0);
}

// 4. Повтор кадру з уже використаним токеном.
void test_token_replay() {
    using namespace std::chrono_literals;
    TestBoard board;
    sbo::TargetEngine node{kTarget, board, 0x0BADF00Du};

    const auto sel = node.process(
        make_request(sbo::MessageType::SelectReq, kGcs, kTarget, kCmdArm, sbo::Token{}, 5000ms), kT0);
    const auto op  = make_request(sbo::MessageType::OperateReq, kGcs, kTarget, kCmdArm, sel->token);

    const auto first = node.process(op, kT0 + 500ms);
    CHECK(first.has_value());
    CHECK(first->type == sbo::MessageType::OperateAck);

    const auto echo = node.process(op, kT0 + 600ms);   // луна ефіру або зловмисник
    CHECK(echo.has_value());
    CHECK(echo->type == sbo::MessageType::OperateNack);
    CHECK(echo->payload[0] == static_cast<std::uint8_t>(sbo::Error::NotArmed));
    CHECK(board.exec_calls == 1);
}

// 5. Широкомовний і чужий кадри.
void test_broadcast_and_foreign() {
    TestBoard board;
    sbo::TargetEngine node{kTarget, board, 0x11112222u};

    const auto bcast = node.process(
        make_request(sbo::MessageType::OperateReq, kGcs, sbo::NodeId{0xFF}, kCmdArm,
                     sbo::Token{0x1234}), kT0);
    CHECK(!bcast.has_value());
    CHECK(bcast.error() == sbo::Error::BroadcastForbidden);
    CHECK(board.drop_pulses == 1);
    CHECK(board.exec_calls == 0);

    const auto foreign = node.process(
        make_request(sbo::MessageType::SelectReq, kGcs, sbo::NodeId{0x07}, kCmdArm), kT0);
    CHECK(!foreign.has_value());
    CHECK(foreign.error() == sbo::Error::ForeignTarget);
    CHECK(node.state() == sbo::State::Idle);
}

// 6. Другий оператор: ні перехоплення замка, ні підставленого токена.
void test_second_operator() {
    using namespace std::chrono_literals;
    TestBoard board;
    sbo::TargetEngine node{kTarget, board, 0x5A5A5A5Au};

    const auto sel = node.process(
        make_request(sbo::MessageType::SelectReq, kGcs, kTarget, kCmdArm, sbo::Token{}, 5000ms), kT0);

    const auto busy = node.process(
        make_request(sbo::MessageType::SelectReq, kOther, kTarget, kCmdArm, sbo::Token{}, 5000ms),
        kT0 + 100ms);
    CHECK(busy.has_value());
    CHECK(busy->type == sbo::MessageType::SelectNack);
    CHECK(busy->payload[0] == static_cast<std::uint8_t>(sbo::Error::Busy));
    CHECK(node.state() == sbo::State::Armed);   // чужий запит нашої селекції не зірвав

    const auto stolen = node.process(
        make_request(sbo::MessageType::OperateReq, kOther, kTarget, kCmdArm, sel->token),
        kT0 + 200ms);
    CHECK(stolen.has_value());
    CHECK(stolen->payload[0] == static_cast<std::uint8_t>(sbo::Error::SourceMismatch));
    CHECK(node.state() == sbo::State::Idle);
    CHECK(board.exec_calls == 0);
    CHECK(board.drop_pulses == 1);
}

// 7. Кадр на дроті: обіг туди-назад, повний тракт і зіпсований байт.
void test_frame_codec() {
    using namespace std::chrono_literals;
    TestBoard board;
    sbo::TargetEngine node{kTarget, board, 0x33445566u};

    auto req = make_request(sbo::MessageType::SelectReq, kGcs, kTarget, kCmdArm, sbo::Token{}, 5000ms);
    const std::array<std::uint8_t, 3> extra{0xDE, 0xAD, 0x01};
    req.set_data(extra);

    std::array<std::uint8_t, sbo::kMaxFrameLen> wire{};
    const auto encoded = sbo::encode(req, wire);
    CHECK(encoded.has_value());
    CHECK(encoded->size() == sbo::kHeaderLen + 3 + sbo::kCrcLen);

    const auto back = sbo::decode(*encoded);
    CHECK(back.has_value());
    CHECK(back->command == kCmdArm);
    CHECK(back->payload_len == 3);
    CHECK(back->data()[1] == 0xAD);

    std::array<std::uint8_t, sbo::kMaxFrameLen> answer{};
    const auto reply = node.handle_wire(*encoded, answer, kT0);
    CHECK(reply.has_value());
    const auto ack = sbo::decode(*reply);
    CHECK(ack.has_value());
    CHECK(ack->type == sbo::MessageType::SelectAck);
    CHECK(ack->token.valid());

    // Перешкода в ефірі перевернула біт у полі команди.
    const std::size_t len = encoded->size();
    wire[12] ^= 0x08u;
    CHECK(sbo::decode(std::span{wire.data(), len}).error() == sbo::Error::BadCrc);
    wire[12] ^= 0x08u;
    wire[0] = 0x00u;
    CHECK(sbo::decode(std::span{wire.data(), len}).error() == sbo::Error::BadMagic);
    CHECK(sbo::decode(std::span{wire.data(), sbo::kMinFrameLen - 1}).error() == sbo::Error::BadLength);
}

// 8. Пульт: мовчання борту гасить кнопку, квитанція її вмикає.
void test_gcs_link_loss() {
    using namespace std::chrono_literals;
    TestBoard board;
    sbo::TargetEngine node{kTarget, board, 0x77665544u};
    gcs::FocusManager focus{kGcs};

    CHECK(!focus.select(sbo::NodeId{0xFF}, 0, "ALL", kCmdArm, 5000ms, kT0).has_value());

    const auto sel = focus.select(kTarget, 1, "UAV-02", kCmdArm, 5000ms, kT0);
    CHECK(sel.has_value());
    CHECK(focus.status() == gcs::Status::WaitAck);
    CHECK(focus.target_name() == "UAV-02");
    CHECK(!focus.button_enabled(kT0));

    focus.tick(kT0 + 401ms);                       // квитанція не долетіла
    CHECK(focus.status() == gcs::Status::LinkLost);
    CHECK(focus.badge() == "Втрата зв'язку");
    CHECK(focus.frame_color() == 0xD0342Cu);
    CHECK(!focus.build_operate({}, kT0 + 401ms).has_value());

    // Друга спроба — цього разу борт відповів.
    const auto retry = focus.select(kTarget, 1, "UAV-02", kCmdArm, 5000ms, kT0 + 500ms);
    CHECK(retry.has_value());
    const auto ack = node.process(*retry, kT0 + 520ms);
    CHECK(ack.has_value());
    focus.on_response(*ack, kT0 + 540ms);
    CHECK(focus.status() == gcs::Status::Armed);
    CHECK(focus.button_enabled(kT0 + 600ms));

    const auto op = focus.build_operate({}, kT0 + 600ms);
    CHECK(op.has_value());
    CHECK(op->token.valid());
    CHECK(!focus.build_operate({}, kT0 + 601ms).has_value());   // другий клік — ні

    const auto done = node.process(*op, kT0 + 620ms);
    CHECK(done.has_value());
    CHECK(done->type == sbo::MessageType::OperateAck);
    focus.on_response(*done, kT0 + 640ms);
    CHECK(focus.status() == gcs::Status::Done);
    CHECK(board.exec_calls == 1);

    // Вікно селекції гасне саме, без жодного кадру ззовні.
    const auto again = focus.select(kTarget, 1, "UAV-02", kCmdArm, 1000ms, kT0 + 1000ms);
    const auto ack2  = node.process(*again, kT0 + 1010ms);
    focus.on_response(*ack2, kT0 + 1020ms);
    CHECK(focus.status() == gcs::Status::Armed);
    focus.tick(kT0 + 1900ms);
    CHECK(focus.status() == gcs::Status::Expired);
    CHECK(!focus.button_enabled(kT0 + 1900ms));
}

// 9. Відмова приводу доїжджає до оператора як NACK.
void test_actuator_failure() {
    using namespace std::chrono_literals;
    TestBoard board;
    sbo::TargetEngine node{kTarget, board, 0x24681357u};
    gcs::FocusManager focus{kGcs};

    const auto sel = node.process(
        make_request(sbo::MessageType::SelectReq, kGcs, kTarget, kCmdArm, sbo::Token{}, 5000ms), kT0);
    board.fail_next = true;
    const auto op = node.process(
        make_request(sbo::MessageType::OperateReq, kGcs, kTarget, kCmdArm, sel->token), kT0 + 200ms);

    CHECK(op.has_value());
    CHECK(op->type == sbo::MessageType::OperateNack);
    CHECK(op->payload[0] == static_cast<std::uint8_t>(sbo::Error::InternalFault));
    CHECK(node.state() == sbo::State::Idle);
    CHECK(board.exec_pulses == 0);

    // Пульт показує причину відмови текстом на картці.
    (void)focus.select(kTarget, 1, "UAV-02", kCmdArm, 5000ms, kT0);
    focus.on_response(*op, kT0 + 300ms);
    CHECK(focus.status() == gcs::Status::Rejected);
    CHECK(focus.frame_color() == 0xD0342Cu);
}

}  // namespace

int main() {
    test_operate_without_select();
    test_nominal_cycle();
    test_timeout_expired();
    test_token_replay();
    test_broadcast_and_foreign();
    test_second_operator();
    test_frame_codec();
    test_gcs_link_loss();
    test_actuator_failure();

    std::printf("перевірок: %d, провалів: %d\n", g_checks, g_failed);
    return g_failed == 0 ? 0 : 1;
}
