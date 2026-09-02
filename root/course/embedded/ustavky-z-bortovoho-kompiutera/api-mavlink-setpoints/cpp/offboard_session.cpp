#include "offboard_session.hpp"

#include <arpa/inet.h>
#include <fcntl.h>
#include <poll.h>
#include <unistd.h>

#include <cerrno>
#include <cstring>
#include <stdexcept>
#include <system_error>
#include <thread>

namespace px4 {
namespace {

constexpr std::uint8_t kPx4MainOffboard = 6;
constexpr std::uint8_t kPx4MainAuto = 4;
constexpr std::uint8_t kPx4SubAutoLoiter = 3;

constexpr auto kStreamPeriod = std::chrono::milliseconds{50};   // 20 Гц
constexpr auto kOwnHeartbeat = std::chrono::seconds{1};

[[noreturn]] void throw_errno(const char* what)
{
    throw std::system_error(errno, std::generic_category(), what);
}

}  // namespace

void UniqueFd::reset(int fd) noexcept
{
    if (fd_ >= 0) ::close(fd_);
    fd_ = fd;
}

std::string_view result_name(std::uint8_t result) noexcept
{
    switch (result) {
    case MAV_RESULT_ACCEPTED:             return "ACCEPTED";
    case MAV_RESULT_TEMPORARILY_REJECTED: return "TEMPORARILY_REJECTED";
    case MAV_RESULT_DENIED:               return "DENIED";
    case MAV_RESULT_UNSUPPORTED:          return "UNSUPPORTED";
    case MAV_RESULT_FAILED:               return "FAILED";
    default:                              return "невідомий код";
    }
}

OffboardSession::OffboardSession(std::uint16_t local_port)
{
    UniqueFd fd{::socket(AF_INET, SOCK_DGRAM, 0)};
    if (!fd) throw_errno("socket");

    const int flags = ::fcntl(fd.get(), F_GETFL, 0);
    if (flags < 0 || ::fcntl(fd.get(), F_SETFL, flags | O_NONBLOCK) < 0) throw_errno("fcntl");

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(local_port);
    if (::bind(fd.get(), reinterpret_cast<const sockaddr*>(&addr), sizeof(addr)) < 0)
        throw_errno("bind");

    fd_ = std::move(fd);
}

OffboardSession::~OffboardSession()
{
    /* Кинути offboard мовчки означає віддати апарат у failsafe. Якщо ми
       звідси виходимо аварійно — самі переводимо його в режим утримання. */
    if (engaged_ && peer_known_) leave_offboard();
}

void OffboardSession::leave_offboard() noexcept
{
    try {
        mavlink_command_long_t cmd{};
        cmd.target_system = ids_.target_sys;
        cmd.target_component = ids_.target_comp;
        cmd.command = MAV_CMD_DO_SET_MODE;
        cmd.param1 = static_cast<float>(MAV_MODE_FLAG_CUSTOM_MODE_ENABLED);
        cmd.param2 = static_cast<float>(kPx4MainAuto);
        cmd.param3 = static_cast<float>(kPx4SubAutoLoiter);

        mavlink_message_t msg{};
        mavlink_msg_command_long_encode(ids_.self_sys, ids_.self_comp, &msg, &cmd);
        send(msg);   // без очікування ACK: ми вже виходимо
    } catch (...) {
        // деструктор не має права кидати далі
    }
}

void OffboardSession::send(const mavlink_message_t& msg)
{
    if (!fd_ || !peer_known_) return;

    std::uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    const std::uint16_t len = mavlink_msg_to_send_buffer(buf, &msg);

    for (;;) {
        const ssize_t n = ::sendto(fd_.get(), buf, len, 0,
                                   reinterpret_cast<const sockaddr*>(&peer_), peer_len_);
        if (n == static_cast<ssize_t>(len)) return;
        if (n < 0 && errno == EINTR) continue;
        /* Переповнену чергу сокета пропускаємо: наступна уставка за 50 мс,
           блокувати цикл заради однієї втраченої не можна. */
        return;
    }
}

void OffboardSession::handle(const mavlink_message_t& msg)
{
    switch (msg.msgid) {
    case MAVLINK_MSG_ID_HEARTBEAT: {
        if (msg.compid != MAV_COMP_ID_AUTOPILOT1) return;   // камери й гімбали теж б'ються серцем
        mavlink_heartbeat_t hb{};
        mavlink_msg_heartbeat_decode(&msg, &hb);
        ids_.target_sys = msg.sysid;
        tlm_.base_mode = hb.base_mode;
        tlm_.custom_mode = hb.custom_mode;
        tlm_.system_status = hb.system_status;
        tlm_.heartbeat_at = Clock::now();
        break;
    }
    case MAVLINK_MSG_ID_COMMAND_ACK: {
        mavlink_command_ack_t ack{};
        mavlink_msg_command_ack_decode(&msg, &ack);
        ack_ = std::pair{ack.command, ack.result};
        break;
    }
    case MAVLINK_MSG_ID_LOCAL_POSITION_NED: {
        mavlink_local_position_ned_t p{};
        mavlink_msg_local_position_ned_decode(&msg, &p);
        tlm_.position = sp::Vec3{p.x, p.y, p.z};
        tlm_.velocity = sp::Vec3{p.vx, p.vy, p.vz};
        break;
    }
    case MAVLINK_MSG_ID_ATTITUDE: {
        mavlink_attitude_t a{};
        mavlink_msg_attitude_decode(&msg, &a);
        tlm_.yaw = a.yaw;
        break;
    }
    case MAVLINK_MSG_ID_ESTIMATOR_STATUS: {
        mavlink_estimator_status_t e{};
        mavlink_msg_estimator_status_decode(&msg, &e);
        tlm_.estimator_flags = e.flags;
        break;
    }
    default:
        break;
    }
}

void OffboardSession::pump(std::chrono::milliseconds timeout)
{
    bool waited = false;

    for (;;) {
        pollfd pfd{fd_.get(), POLLIN, 0};
        const int rc = ::poll(&pfd, 1, waited ? 0 : static_cast<int>(timeout.count()));
        if (rc < 0) {
            if (errno == EINTR) continue;
            throw_errno("poll");
        }
        waited = true;
        if (rc == 0) return;

        std::uint8_t buf[2048];
        sockaddr_in from{};
        socklen_t from_len = sizeof(from);
        const ssize_t n = ::recvfrom(fd_.get(), buf, sizeof(buf), 0,
                                     reinterpret_cast<sockaddr*>(&from), &from_len);
        if (n < 0) {
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) return;
            throw_errno("recvfrom");
        }

        if (!peer_known_) {
            /* Адресу автопілота беремо з першого ж кадру — так само поводиться
               udp://:14540 у наземних станціях. */
            peer_ = from;
            peer_len_ = from_len;
            peer_known_ = true;
        }

        for (ssize_t i = 0; i < n; ++i) {
            mavlink_message_t msg{};
            mavlink_status_t status{};
            if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status) == 1) handle(msg);
        }
    }
}

void OffboardSession::heartbeat_tick()
{
    const auto now = Clock::now();
    if (last_heartbeat_sent_ != Clock::time_point{} && now - last_heartbeat_sent_ < kOwnHeartbeat)
        return;

    mavlink_message_t msg{};
    mavlink_msg_heartbeat_pack(ids_.self_sys, ids_.self_comp, &msg,
                               MAV_TYPE_ONBOARD_CONTROLLER, MAV_AUTOPILOT_INVALID,
                               0, 0, MAV_STATE_ACTIVE);
    last_heartbeat_sent_ = now;
    send(msg);
}

void OffboardSession::wait_for_heartbeat(std::chrono::milliseconds timeout)
{
    const auto deadline = Clock::now() + timeout;
    while (Clock::now() < deadline) {
        pump(std::chrono::milliseconds{100});
        if (tlm_.heartbeat_at) return;
    }
    throw std::runtime_error("автопілот не надіслав HEARTBEAT");
}

std::expected<void, std::string> OffboardSession::stream(std::chrono::milliseconds duration,
                                                         const Builder& build,
                                                         bool require_offboard)
{
    const auto start = Clock::now();
    const auto deadline = start + duration;
    auto next = start;

    while (Clock::now() < deadline) {
        const double t = std::chrono::duration<double>(Clock::now() - start).count();
        const auto msg = build(t);
        if (!msg) return std::unexpected(std::string{sp::describe(msg.error())});

        send(*msg);
        heartbeat_tick();
        pump(std::chrono::milliseconds{0});

        const auto now = Clock::now();
        if (!tlm_.alive(now)) return std::unexpected("HEARTBEAT автопілота зник — канал утрачено");
        if (require_offboard && !tlm_.offboard())
            return std::unexpected("автопілот покинув offboard: спрацював failsafe");
        if (require_offboard && tlm_.estimator_flags &&
            (*tlm_.estimator_flags & ESTIMATOR_POS_HORIZ_REL) == 0)
            return std::unexpected("EKF утратив горизонтальну позицію");

        next += kStreamPeriod;
        std::this_thread::sleep_until(next);
    }
    return {};
}

std::expected<std::uint8_t, std::string>
OffboardSession::send_command(std::uint16_t command, std::array<float, 7> params,
                              std::uint8_t confirmation, const Builder& keepalive,
                              std::chrono::milliseconds timeout)
{
    ack_.reset();

    mavlink_command_long_t cmd{};
    cmd.target_system = ids_.target_sys;
    cmd.target_component = ids_.target_comp;
    cmd.command = command;
    cmd.confirmation = confirmation;
    cmd.param1 = params[0];
    cmd.param2 = params[1];
    cmd.param3 = params[2];
    cmd.param4 = params[3];
    cmd.param5 = params[4];
    cmd.param6 = params[5];
    cmd.param7 = params[6];

    mavlink_message_t msg{};
    mavlink_msg_command_long_encode(ids_.self_sys, ids_.self_comp, &msg, &cmd);
    send(msg);

    /* Чекаючи підтвердження, потік уставок не переривають: пауза довша за
       500 мс сама вибиває апарат з offboard. */
    const auto deadline = Clock::now() + timeout;
    auto next = Clock::now();
    while (Clock::now() < deadline) {
        if (const auto sp_msg = keepalive(0.0); sp_msg) send(*sp_msg);
        heartbeat_tick();
        pump(std::chrono::milliseconds{0});

        if (ack_ && ack_->first == command) return ack_->second;

        next += kStreamPeriod;
        std::this_thread::sleep_until(next);
    }
    return std::unexpected("COMMAND_ACK не прийшов");
}

std::expected<void, std::string> OffboardSession::enable_offboard(const Builder& keepalive)
{
    std::string last = "offboard не увімкнувся";

    for (int attempt = 0; attempt < 3; ++attempt) {
        /* param1 — base_mode з увімкненим власним режимом, param2 — головний
           режим PX4. Для ArduPilot Copter тут стояло б COPTER_MODE_GUIDED = 4. */
        const std::array<float, 7> params{static_cast<float>(MAV_MODE_FLAG_CUSTOM_MODE_ENABLED),
                                          static_cast<float>(kPx4MainOffboard),
                                          0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
        const auto result = send_command(MAV_CMD_DO_SET_MODE, params,
                                         static_cast<std::uint8_t>(attempt), keepalive,
                                         std::chrono::seconds{1});
        if (!result) {
            last = result.error();
            continue;
        }

        if (*result == MAV_RESULT_ACCEPTED) {
            /* Прийняти команду не означає ввійти в режим: підтвердженням
               є HEARTBEAT із потрібним custom_mode. */
            const auto deadline = Clock::now() + std::chrono::seconds{2};
            auto next = Clock::now();
            while (Clock::now() < deadline) {
                if (const auto msg = keepalive(0.0); msg) send(*msg);
                pump(std::chrono::milliseconds{0});
                if (tlm_.offboard()) {
                    engaged_ = true;
                    return {};
                }
                next += kStreamPeriod;
                std::this_thread::sleep_until(next);
            }
            return std::unexpected("режим не підтверджено в HEARTBEAT");
        }

        /* DENIED, UNSUPPORTED і FAILED повторювати марно: причина не в часі. */
        if (*result != MAV_RESULT_TEMPORARILY_REJECTED)
            return std::unexpected("DO_SET_MODE: " + std::string{result_name(*result)});

        /* Потік уставок ще молодий або EKF не готовий — стрічимо далі. */
        last = "DO_SET_MODE: TEMPORARILY_REJECTED";
        if (auto s = stream(std::chrono::seconds{1}, keepalive, false); !s) return s;
    }
    return std::unexpected(last);
}

std::expected<void, std::string> OffboardSession::arm(bool on, const Builder& keepalive)
{
    const std::array<float, 7> params{on ? 1.0f : 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
    const auto result = send_command(MAV_CMD_COMPONENT_ARM_DISARM, params, 0, keepalive,
                                     std::chrono::seconds{2});
    if (!result) return std::unexpected(result.error());
    if (*result != MAV_RESULT_ACCEPTED)
        return std::unexpected(std::string{on ? "ARM: " : "DISARM: "} +
                               std::string{result_name(*result)});

    /* Роззброїлися на землі — сесію завершено штатно, деструктору вже нема
       чого рятувати. */
    if (!on) engaged_ = false;
    return {};
}

}  // namespace px4
