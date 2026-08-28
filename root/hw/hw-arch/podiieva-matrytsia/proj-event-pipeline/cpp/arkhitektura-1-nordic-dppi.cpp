#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>

namespace hal::dppi {

/* Безпечна типізована обгортка над каналом DPPI */
class Channel {
public:
    explicit constexpr Channel(uint8_t id) : id_(id) {}

    [[nodiscard]] constexpr uint32_t publish_config() const noexcept {
        return (1UL << 31) | (id_ & 0x1F);
    }

    [[nodiscard]] constexpr uint32_t subscribe_config() const noexcept {
        return (1UL << 31) | (id_ & 0x1F);
    }

    [[nodiscard]] constexpr uint32_t mask() const noexcept {
        return (1UL << id_);
    }

    [[nodiscard]] constexpr uint8_t id() const noexcept { return id_; }

private:
    uint8_t id_;
};

struct HardwareRegisters {
    struct Comp {
        volatile uint32_t TASKS_START;
        volatile uint32_t TASKS_STOP;
        volatile uint32_t EVENTS_UP;
        volatile uint32_t PUBLISH_UP;
    };

    struct Timer {
        volatile uint32_t TASKS_START;
        volatile uint32_t TASKS_STOP;
        volatile uint32_t TASKS_CLEAR;
        volatile uint32_t EVENTS_COMPARE[4];
        volatile uint32_t CC[4];
        volatile uint32_t SHORTS;
        volatile uint32_t SUBSCRIBE_START;
        volatile uint32_t PUBLISH_COMPARE[4];
    };

    struct Saadc {
        volatile uint32_t TASKS_START;
        volatile uint32_t TASKS_SAMPLE;
        volatile uint32_t EVENTS_END;
        volatile uint32_t RESULT_PTR;
        volatile uint32_t RESULT_MAXCNT;
        volatile uint32_t SUBSCRIBE_SAMPLE;
    };

    struct Dppi {
        volatile uint32_t CHEN;
        volatile uint32_t CHENSET;
        volatile uint32_t CHENCLR;
    };
};

/* RAII-драйвер автономного вимірювального конвеєра */
template <typename Regs = HardwareRegisters>
class AutonomousAcquisitionPipeline {
public:
    AutonomousAcquisitionPipeline(
        typename Regs::Comp* comp,
        typename Regs::Timer* timer,
        typename Regs::Saadc* saadc,
        typename Regs::Dppi* dppi,
        Channel trigger_channel,
        Channel sample_channel
    ) noexcept
        : comp_(comp), timer_(timer), saadc_(saadc), dppi_(dppi),
          trig_ch_(trigger_channel), sample_ch_(sample_channel) {}

    void setup(std::span<uint16_t> destination_buffer, uint32_t settling_ticks = 160) noexcept {
        /* Конфігурація публікації та підписки без магічних чисел */
        comp_->PUBLISH_UP = trig_ch_.publish_config();

        timer_->SUBSCRIBE_START = trig_ch_.subscribe_config();
        timer_->CC[0] = settling_ticks;
        timer_->SHORTS = 1UL << 0; /* Автоматичне скидання лічильника */
        timer_->PUBLISH_COMPARE[0] = sample_ch_.publish_config();

        saadc_->SUBSCRIBE_SAMPLE = sample_ch_.subscribe_config();
        saadc_->RESULT_PTR = reinterpret_cast<uint32_t>(destination_buffer.data());
        saadc_->RESULT_MAXCNT = static_cast<uint32_t>(destination_buffer.size());

        /* Активація каналів у матриці */
        dppi_->CHENSET = trig_ch_.mask() | sample_ch_.mask();

        /* Переведення АЦП у стан готовності приймати EasyDMA-тригери */
        saadc_->TASKS_START = 1;
    }

    void stop() noexcept {
        dppi_->CHENCLR = trig_ch_.mask() | sample_ch_.mask();
        saadc_->TASKS_STOP = 1;
        timer_->TASKS_STOP = 1;
        comp_->TASKS_STOP = 1;
    }

private:
    typename Regs::Comp*  comp_;
    typename Regs::Timer* timer_;
    typename Regs::Saadc* saadc_;
    typename Regs::Dppi*  dppi_;
    Channel trig_ch_;
    Channel sample_ch_;
};

} // namespace hal::dppi
