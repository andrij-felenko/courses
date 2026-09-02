#include "mavlink_link.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <memory>
#include <string>

#include <fcntl.h>
#include <termios.h>
#include <unistd.h>

/* Збірка: -I<mavlink>/v2.0 — каталог, згенерований mavgenerate. */
#include <common/mavlink.h>

namespace servo {
namespace {

speed_t baud_to_speed(int baud) {
    switch (baud) {
        case 57600:  return B57600;
        case 115200: return B115200;
        case 230400: return B230400;
        case 460800: return B460800;
        case 921600: return B921600;
        default:     return 0;
    }
}

}  // namespace

/* Стан розбору живе тут, щоб заголовок лишався чистим. */
struct MavlinkLink::Parser {
    mavlink_message_t msg{};
    mavlink_status_t status{};
};

MavlinkLink::MavlinkLink(std::string_view device, int baud)
    : parser_{std::make_unique<Parser>()} {
    compid_ = MAV_COMP_ID_ONBOARD_COMPUTER;
    target_compid_ = MAV_COMP_ID_AUTOPILOT1;

    const speed_t speed = baud_to_speed(baud);
    if (speed == 0) {
        throw std::invalid_argument("непідтримувана швидкість порту");
    }

    const std::string path{device};
    /* O_NONBLOCK: контур керування не має права зупинитися на read(). */
    PosixFd fd{::open(path.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK | O_CLOEXEC)};
    if (!fd) {
        throw_errno("open(" + path + ")");
    }

    termios tio{};
    if (::tcgetattr(fd.get(), &tio) != 0) {
        throw_errno("tcgetattr");
    }
    ::cfmakeraw(&tio);
    tio.c_cflag |= CLOCAL | CREAD;
    tio.c_cflag &= static_cast<tcflag_t>(~CRTSCTS);
    tio.c_cc[VMIN] = 0;
    tio.c_cc[VTIME] = 0;
    if (::cfsetispeed(&tio, speed) != 0 || ::cfsetospeed(&tio, speed) != 0 ||
        ::tcsetattr(fd.get(), TCSANOW, &tio) != 0) {
        throw_errno("tcsetattr");
    }
    ::tcflush(fd.get(), TCIOFLUSH);

    fd_ = std::move(fd);   /* до цього рядка дескриптор закриє деструктор PosixFd */
}

MavlinkLink::~MavlinkLink() = default;

std::optional<BodyRates> MavlinkLink::poll() {
    std::optional<BodyRates> latest;
    std::array<std::uint8_t, 512> buf{};

    while (true) {
        const ssize_t n = ::read(fd_.get(), buf.data(), buf.size());
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                break;      /* байтів більше немає — це норма */
            }
            throw_errno("read(serial)");
        }
        if (n == 0) {
            break;
        }

        for (ssize_t i = 0; i < n; ++i) {
            if (mavlink_parse_char(MAVLINK_COMM_1, buf[static_cast<std::size_t>(i)],
                                   &parser_->msg, &parser_->status) != 1) {
                continue;
            }
            if (parser_->msg.msgid != MAVLINK_MSG_ID_HIGHRES_IMU) {
                continue;
            }
            mavlink_highres_imu_t imu{};
            mavlink_msg_highres_imu_decode(&parser_->msg, &imu);
            /* Рамка тіла FRD: ygyro — тангаж, zgyro — рискання. */
            latest = BodyRates{.yaw = imu.zgyro, .pitch = imu.ygyro};
            ++imu_msgs_;
        }

        if (static_cast<std::size_t>(n) < buf.size()) {
            break;
        }
    }
    return latest;
}

bool MavlinkLink::send_rates(const GuidanceSetpoints& sp, float thrust, std::uint32_t boot_ms) {
    mavlink_set_attitude_target_t target{};
    target.time_boot_ms = boot_ms;
    target.target_system = target_sysid_;
    target.target_component = target_compid_;

    /* Керуємо виключно кутовими швидкостями, тому автопілоту наказано
     * ігнорувати орієнтацію. Біти 0..2 (ROLL/PITCH/YAW_RATE_IGNORE) лишаються
     * нульовими — інакше він викинув би саме те, що ми шлемо. */
    target.type_mask = ATTITUDE_TARGET_TYPEMASK_ATTITUDE_IGNORE;

    /* Кватерніон ігнорується, але має лишатися одиничним: автопілоти
     * перевіряють норму ще до розбору маски. */
    target.q[0] = 1.0f;

    target.body_roll_rate = 0.0f;   /* крен тримає контур стабілізації горизонту */
    target.body_pitch_rate = sp.pitch_rate_rad_s;
    target.body_yaw_rate = sp.yaw_rate_rad_s;
    target.thrust = std::clamp(thrust, 0.0f, 1.0f);

    mavlink_message_t msg{};
    mavlink_msg_set_attitude_target_encode(sysid_, compid_, &msg, &target);

    std::array<std::uint8_t, MAVLINK_MAX_PACKET_LEN> buf{};
    const std::uint16_t len = mavlink_msg_to_send_buffer(buf.data(), &msg);

    /* UART віддає не все одразу; недописаний пакет автопілот відкине
     * за контрольною сумою, тож дописуємо хвіст. */
    std::size_t sent = 0;
    while (sent < len) {
        const ssize_t n = ::write(fd_.get(), buf.data() + sent, len - sent);
        if (n > 0) {
            sent += static_cast<std::size_t>(n);
            continue;
        }
        if (n < 0 && errno == EINTR) {
            continue;
        }
        if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            /* Буфер драйвера забитий; ця уставка застаріє за 10 мс,
             * наступний такт надішле свіжу. */
            return false;
        }
        throw_errno("write(serial)");
    }
    return true;
}

}  // namespace servo
