#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <exception>
#include <print>
#include <stop_token>
#include <string>
#include <thread>

#include <csignal>
#include <pthread.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/timerfd.h>
#include <sys/un.h>
#include <unistd.h>

#include "controller.hpp"
#include "detection_channel.hpp"
#include "mavlink_link.hpp"
#include "posix_fd.hpp"

/* Бортовий контролер візуального наведення.
 *
 * Потік зору      — блокувальне читання детекцій із UNIX-сокета: нейромережа
 *                   крутиться окремим процесом на NPU й шле центр рамки та
 *                   апаратну мітку початку експозиції;
 * контур керування — головний потік, SCHED_FIFO, timerfd на 100 Гц.
 *
 * Між ними — канал без замків, спільної пам'яті більше немає жодної. */

namespace {

using namespace servo;
using namespace std::chrono_literals;

constexpr auto kControlPeriod = 10ms;    /* 100 Гц */
constexpr float kHoverThrust = 0.55f;

std::atomic<bool> g_stop{false};

void on_signal(int) { g_stop.store(true, std::memory_order_relaxed); }

/* Дротовий формат детектора: сталий розмір, без вирівнювальних дір. */
struct [[gnu::packed]] DetectionWire {
    std::uint64_t t_capture_us;   /* CLOCK_MONOTONIC тієї самої машини */
    float u;
    float v;
    float width;
    float height;
    std::uint8_t valid;
};

/* Приймач детекцій. Сокет прив'язується до шляху у файловій системі, тож
 * і зняти його при виході — теж обов'язок цього класу. */
class DetectorFeed {
public:
    explicit DetectorFeed(std::string path) : path_{std::move(path)} {
        fd_ = PosixFd{::socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0)};
        if (!fd_) {
            throw_errno("socket(AF_UNIX)");
        }
        ::unlink(path_.c_str());     /* залишок від попереднього запуску */

        sockaddr_un addr{};
        addr.sun_family = AF_UNIX;
        if (path_.size() >= sizeof(addr.sun_path)) {
            throw std::invalid_argument("задовгий шлях сокета детектора");
        }
        std::memcpy(addr.sun_path, path_.c_str(), path_.size());
        if (::bind(fd_.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0) {
            throw_errno("bind(" + path_ + ")");
        }

        /* Таймаут читання — єдиний спосіб розбудити потік на зупинці. */
        timeval tv{.tv_sec = 0, .tv_usec = 200000};
        ::setsockopt(fd_.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    }

    ~DetectorFeed() {
        fd_.reset();
        ::unlink(path_.c_str());
    }

    DetectorFeed(const DetectorFeed&) = delete;
    DetectorFeed& operator=(const DetectorFeed&) = delete;

    /* nullopt = минув таймаут очікування або кадр без цілі. */
    [[nodiscard]] std::optional<TargetDetection> receive() const {
        DetectionWire wire{};
        const ssize_t n = ::recv(fd_.get(), &wire, sizeof(wire), 0);
        if (n < 0) {
            if (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK) {
                return std::nullopt;
            }
            throw_errno("recv(detector)");
        }
        if (n != static_cast<ssize_t>(sizeof(wire))) {
            std::println(stderr, "детектор: пакет {} Б замість {}", n, sizeof(wire));
            return std::nullopt;
        }
        if (wire.valid == 0) {
            return std::nullopt;     /* кадр без цілі: таймаут розбереться */
        }
        /* steady_clock на Linux — це CLOCK_MONOTONIC, той самий годинник,
         * що ним детектор мітить початок експозиції. */
        return TargetDetection{
            .u = wire.u,
            .v = wire.v,
            .width = wire.width,
            .height = wire.height,
            .captured = TimePoint{std::chrono::microseconds{wire.t_capture_us}},
        };
    }

private:
    std::string path_;
    PosixFd fd_;
};

void promote_to_realtime() {
    sched_param param{.sched_priority = 80};
    if (::pthread_setschedparam(::pthread_self(), SCHED_FIFO, &param) != 0) {
        /* Без CAP_SYS_NICE це звичайна ситуація на столі розробника. */
        std::println(stderr, "увага: SCHED_FIFO недоступний, контур піде як SCHED_OTHER");
    }
    if (::mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        std::println(stderr, "увага: mlockall не вдався, можливі затримки на сторінкових збоях");
    }
}

PosixFd make_tick_timer(std::chrono::nanoseconds period) {
    PosixFd timer{::timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC)};
    if (!timer) {
        throw_errno("timerfd_create");
    }
    itimerspec its{};
    its.it_interval.tv_nsec = period.count();
    its.it_value.tv_nsec = period.count();
    if (::timerfd_settime(timer.get(), 0, &its, nullptr) != 0) {
        throw_errno("timerfd_settime");
    }
    return timer;
}

}  // namespace

int main(int argc, char** argv) {
    const std::string device = (argc > 1) ? argv[1] : "/dev/ttyUSB0";
    const int baud = (argc > 2) ? std::stoi(argv[2]) : 921600;
    const std::string sock_path = (argc > 3) ? argv[3] : "/run/vision/detections.sock";

    std::signal(SIGINT, on_signal);
    std::signal(SIGTERM, on_signal);
    std::signal(SIGPIPE, SIG_IGN);

    try {
        const CameraIntrinsics camera{
            .fx = 812.4f, .fy = 811.9f,
            .cx = 319.6f, .cy = 241.2f,
            .img_width = 640.0f, .img_height = 480.0f,
        };
        VisualServoingController controller{camera};
        SpscChannel<TargetDetection> channel;

        MavlinkLink link{device, baud};
        DetectorFeed feed{sock_path};
        const PosixFd timer = make_tick_timer(kControlPeriod);

        /* jthread сам виставить stop_token і приєднається в деструкторі —
         * навіть якщо нижче полетить виняток. */
        std::jthread vision{[&feed, &channel](std::stop_token stop) {
            while (!stop.stop_requested()) {
                try {
                    if (auto det = feed.receive()) {
                        channel.push(*det);
                    }
                } catch (const std::system_error& e) {
                    std::println(stderr, "потік зору: {}", e.what());
                    break;
                }
            }
        }};

        promote_to_realtime();

        const auto boot = Clock::now();
        auto last_report = boot;
        unsigned overruns = 0;
        unsigned tx_errors = 0;
        BodyRates gyro{};

        while (!g_stop.load(std::memory_order_relaxed)) {
            std::uint64_t ticks = 0;
            const ssize_t n = ::read(timer.get(), &ticks, sizeof(ticks));
            if (n < 0) {
                if (errno == EINTR) {
                    continue;
                }
                throw_errno("read(timerfd)");
            }
            if (ticks > 1) {
                /* Проґавлений такт — рівно те, чого не має бути в контурі
                 * реального часу, тож рахуємо й показуємо. */
                overruns += static_cast<unsigned>(ticks - 1);
            }

            const auto now = Clock::now();

            /* 1. Свіжі гіроскопи; коли нових немає — тримаємо попередні. */
            if (auto rates = link.poll()) {
                gyro = *rates;
            }

            /* 2. Усі детекції, що встигли накопичитися. */
            while (auto det = channel.pop()) {
                controller.on_detection(*det);
            }

            /* 3. Крок контуру. Утрату супроводу не ховаємо в нулях — з неї
             * видно, чи ми ще не бачили цілі, чи вже її загубили. */
            const auto result = controller.update(now, gyro);
            const GuidanceSetpoints sp = result.value_or(GuidanceSetpoints{});

            /* 4. Уставки шлемо КОЖЕН такт, зокрема й нульові: мовчання довше
             * за пів секунди автопілот трактує як зрив offboard. */
            const auto boot_ms = std::chrono::duration_cast<std::chrono::milliseconds>(now - boot);
            if (!link.send_rates(sp, kHoverThrust, static_cast<std::uint32_t>(boot_ms.count()))) {
                ++tx_errors;
            }

            /* 5. Телеметрія раз на секунду. Поздовжня уставка йде контуру
             * позиції апарата — це вже не наш модуль, тут вона лише в звіті. */
            if (now - last_report >= 1s) {
                last_report = now;
                const char* state = result ? "супровід"
                                   : (result.error() == TrackingLoss::stale_frame ? "втрачено"
                                                                                  : "пошук");
                std::println(stderr,
                             "{} кадрів={} відкинуто={} черга_втрат={} такти={} tx_err={} "
                             "| yaw={:+.3f} pitch={:+.3f} рад/с vf={:+.2f} м/с",
                             state, controller.frames_used(), controller.frames_rejected(),
                             channel.dropped(), overruns, tx_errors,
                             sp.yaw_rate_rad_s, sp.pitch_rate_rad_s, sp.forward_vel_m_s);
            }
        }

        vision.request_stop();
    } catch (const std::exception& e) {
        std::println(stderr, "фатально: {}", e.what());
        return 1;
    }

    return 0;
}
