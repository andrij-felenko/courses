#include "offboard_streamer.hpp"

#include <cmath>
#include <cstring>
#include <format>
#include <iostream>

#include <pthread.h>
#include <sched.h>
#include <sys/timerfd.h>
#include <unistd.h>

PeriodicTimer::PeriodicTimer(std::chrono::nanoseconds period) {
    // Без TFD_NONBLOCK: read() спить до такту. З ним цикл перетворився б
    // на бездумне обертання процесора.
    fd_ = ::timerfd_create(CLOCK_MONOTONIC, 0);
    if (fd_ < 0) {
        throw std::system_error(errno, std::system_category(), "timerfd_create");
    }

    itimerspec spec{};
    spec.it_interval.tv_nsec = static_cast<long>(period.count());
    spec.it_value = spec.it_interval;
    if (::timerfd_settime(fd_, 0, &spec, nullptr) != 0) {
        const int saved = errno;
        ::close(fd_);
        fd_ = -1;
        throw std::system_error(saved, std::system_category(), "timerfd_settime");
    }
}

PeriodicTimer::~PeriodicTimer() {
    if (fd_ >= 0) {
        ::close(fd_);
    }
}

std::uint64_t PeriodicTimer::wait() {
    for (;;) {
        std::uint64_t expirations = 0;
        const ssize_t n = ::read(fd_, &expirations, sizeof(expirations));
        if (n == static_cast<ssize_t>(sizeof(expirations))) {
            return expirations;
        }
        if (n < 0 && errno == EINTR) {
            continue;
        }
        throw std::system_error(errno, std::system_category(), "read(timerfd)");
    }
}

namespace {

void apply_realtime_priority() {
    sched_param param{};
    param.sched_priority = 45;
    const int rc = ::pthread_setschedparam(::pthread_self(), SCHED_FIFO, &param);
    if (rc != 0) {
        // Найчастіше це EPERM без CAP_SYS_NICE. Летіти можна, але потік
        // тепер витісняє будь-який фоновий процес — джитер зросте.
        std::cerr << std::format("[streamer] SCHED_FIFO недоступний ({}): "
                                 "працюємо у звичайному SCHED_OTHER\n",
                                 std::strerror(rc));
    }
}

// Лінійний зріз: за такт швидкість падає щонайбільше на a_brake·Δt.
float ramp_to_zero(float v, float dv_max) {
    if (std::fabs(v) <= dv_max) {
        return 0.0f;
    }
    return v - std::copysign(dv_max, v);
}

}  // namespace

OffboardStreamer::OffboardStreamer(const std::string& port, speed_t baud,
                                   std::uint8_t sys_id, std::uint8_t comp_id)
    : link_(port, baud, sys_id, comp_id) {}

void OffboardStreamer::set_target(const VelocityCommand& cmd) {
    const std::lock_guard lock(mutex_);
    target_ = cmd;
    target_stamp_ = std::chrono::steady_clock::now();
    target_valid_ = true;
}

void OffboardStreamer::begin_mission() {
    mission_.store(true, std::memory_order_release);
}

void OffboardStreamer::request_shutdown() {
    shutdown_.store(true, std::memory_order_release);
}

bool OffboardStreamer::running() const noexcept {
    return running_.load(std::memory_order_acquire);
}

void OffboardStreamer::log_tx(const TxResult& result) {
    if (result) {
        return;
    }
    ++tx_errors_;
    // Скаржитись щотакту не можна: на 20 Гц журнал сам стане джерелом
    // затримки. Пишемо перший збій і далі раз на секунду.
    if (tx_errors_ % kStreamHz == 1) {
        std::cerr << std::format("[streamer] запис у UART не вдався: {} (усього {})\n",
                                 result.error().message(), tx_errors_);
    }
}

void OffboardStreamer::send_current() {
    log_tx(link_.send_setpoint(sent_));
}

void OffboardStreamer::brake_step() {
    const float dv = kBrakeAccel * kTickDt;
    sent_.vx = ramp_to_zero(sent_.vx, dv);
    sent_.vy = ramp_to_zero(sent_.vy, dv);
    sent_.vz = ramp_to_zero(sent_.vz, dv);
    // Курс не гальмуємо: тримаємо той, що був у момент втрати даних.
}

bool OffboardStreamer::stopped() const noexcept {
    return std::fabs(sent_.vx) < kZeroSpeedEps &&
           std::fabs(sent_.vy) < kZeroSpeedEps &&
           std::fabs(sent_.vz) < kZeroSpeedEps;
}

void OffboardStreamer::run(std::stop_token stop) {
    apply_realtime_priority();

    while (!stop.stop_requested() && running()) {
        const std::uint64_t ticks = timer_.wait();
        if (ticks > 1) {
            // Ядро повідомило про пропущені такти — ми не встигли.
            late_ticks_ += static_cast<std::uint32_t>(ticks - 1);
            std::cerr << std::format("[streamer] проспано {} тактів (усього {})\n",
                                     ticks - 1, late_ticks_);
        }
        ++tick_;

        const auto now = std::chrono::steady_clock::now();
        const FcuStatus& fcu = link_.poll();
        rx_drops_ = fcu.rx_drops;
        if (tick_ % kHeartbeatDivider == 0) {
            log_tx(link_.send_heartbeat());
        }

        // Знімок цілі планувальника разом з оцінкою свіжості.
        VelocityCommand target{};
        bool is_fresh = false;
        {
            const std::lock_guard lock(mutex_);
            target = target_;
            is_fresh = target_valid_ && (now - target_stamp_) <= kPlannerTimeout;
        }

        if (shutdown_.load(std::memory_order_acquire)) {
            // Зупинка: свіжі цілі більше не цікавлять, гальмуємо.
            is_fresh = false;
            if (state_ == State::PreStreaming || state_ == State::RequestMode) {
                state_ = State::Idle;
            } else if (state_ == State::ActiveStreaming) {
                state_ = State::HoldFallback;
            }
        }

        // Автопілот міг вийти з Offboard сам: пілот узяв керування,
        // спрацював failsafe або обірвався лінк. Тиснути далі уставками —
        // воювати з пілотом, тому просто замовкаємо.
        if (state_ == State::ActiveStreaming || state_ == State::HoldFallback) {
            const bool link_dead = !fcu.last_heartbeat.has_value() ||
                                   (now - *fcu.last_heartbeat) > kFcuLinkTimeout;
            if (link_dead) {
                std::cerr << "[streamer] автопілот мовчить понад 3 с — стоп\n";
                state_ = State::Idle;
            } else if (!fcu.offboard) {
                std::cerr << "[streamer] FCU вийшов з OFFBOARD (пілот або failsafe) — стоп\n";
                state_ = State::Idle;
            }
        }

        switch (state_) {
        case State::Idle:
            if (shutdown_.load(std::memory_order_acquire)) {
                running_.store(false, std::memory_order_release);
            } else if (mission_.load(std::memory_order_acquire) &&
                       fcu.last_heartbeat.has_value()) {
                // Без жодного HEARTBEAT просити режим марно.
                std::cerr << "[streamer] старт місії: розганяємо потік уставок\n";
                state_ = State::PreStreaming;
                prestream_count_ = 0;
                sent_ = VelocityCommand{0.0f, 0.0f, 0.0f, target.yaw};
                mission_.store(false, std::memory_order_release);
            }
            break;

        case State::PreStreaming:
            // FCU приймає перехід в Offboard, лише коли до запиту він
            // бачив стабільний потік уставок щонайменше 500 мс.
            sent_ = VelocityCommand{0.0f, 0.0f, 0.0f, target.yaw};
            send_current();
            if (++prestream_count_ >= kPreStreamFrames) {
                state_ = State::RequestMode;
                mode_attempts_ = 0;
                mode_tick_ = tick_ - kModeRetryTicks;  // перший запит одразу
            }
            break;

        case State::RequestMode: {
            // Потік НЕ переривається, поки триває узгодження режиму.
            sent_.yaw = target.yaw;
            send_current();

            if (fcu.offboard) {
                std::cerr << std::format("[streamer] OFFBOARD підтверджено ({} спроб)\n",
                                         mode_attempts_);
                state_ = State::ActiveStreaming;
                break;
            }
            if (const auto ack = link_.take_mode_ack(); ack && !ack->accepted) {
                std::cerr << std::format("[streamer] DO_SET_MODE відхилено, MAV_RESULT={}\n",
                                         ack->result);
            }
            if (tick_ - mode_tick_ >= kModeRetryTicks) {
                if (mode_attempts_ >= kModeMaxAttempts) {
                    std::cerr << "[streamer] автопілот не пускає в OFFBOARD — місію скасовано\n";
                    state_ = State::Idle;
                    break;
                }
                log_tx(link_.request_offboard());
                ++mode_attempts_;
                mode_tick_ = tick_;
            }
            break;
        }

        case State::ActiveStreaming:
            if (is_fresh) {
                sent_ = target;
                send_current();
            } else {
                std::cerr << "[streamer] ціль старша за 250 мс — гальмування\n";
                state_ = State::HoldFallback;
                brake_step();
                send_current();
            }
            break;

        case State::HoldFallback:
            if (is_fresh) {
                std::cerr << "[streamer] планувальник ожив — повертаємось у потік\n";
                state_ = State::ActiveStreaming;
                sent_ = target;
                send_current();
            } else {
                brake_step();
                send_current();
                if (shutdown_.load(std::memory_order_acquire) && stopped()) {
                    // Апарат стоїть. Припиняємо потік: через 500 мс FCU
                    // сам вибиває Offboard і йде в Hold — це і є штатна
                    // передача керування автопілоту.
                    std::cerr << "[streamer] зупинено, віддаємо керування FCU\n";
                    state_ = State::Idle;
                }
            }
            break;
        }
    }

    std::cerr << std::format("[streamer] вихід: тактів {}, проспано {}, збоїв TX {}, "
                             "втрачено пакетів {}\n",
                             tick_, late_ticks_, tx_errors_, rx_drops_);
    running_.store(false, std::memory_order_release);
}
