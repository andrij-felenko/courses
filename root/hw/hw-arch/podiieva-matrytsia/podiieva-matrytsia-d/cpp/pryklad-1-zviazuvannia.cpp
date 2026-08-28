#include <cstdint>
#include <concepts>

namespace hal::nrf {

/* Безпечна RAII обгортка для каналу Nordic PPI */
class PpiChannel {
public:
    explicit constexpr PpiChannel(uint8_t channel_index) noexcept 
        : index_(channel_index) {}

    void bind_event_to_task(
        volatile const uint32_t* event_register,
        volatile uint32_t* task_register
    ) const noexcept {
        auto* ppi = reinterpret_cast<PpiHardwareMap*>(PPI_BASE_ADDR);
        ppi->CH[index_].EEP = reinterpret_cast<uint32_t>(event_register);
        ppi->CH[index_].TEP = reinterpret_cast<uint32_t>(task_register);
    }

    void set_fork_task(volatile uint32_t* fork_task_register) const noexcept {
        auto* ppi = reinterpret_cast<PpiHardwareMap*>(PPI_BASE_ADDR);
        ppi->FORK[index_].TEP = reinterpret_cast<uint32_t>(fork_task_register);
    }

    void enable() const noexcept {
        auto* ppi = reinterpret_cast<PpiHardwareMap*>(PPI_BASE_ADDR);
        ppi->CHENSET = (1UL << index_);
    }

    void disable() const noexcept {
        auto* ppi = reinterpret_cast<PpiHardwareMap*>(PPI_BASE_ADDR);
        ppi->CHENCLR = (1UL << index_);
    }

    [[nodiscard]] constexpr uint8_t index() const noexcept { return index_; }

private:
    static constexpr uintptr_t PPI_BASE_ADDR = 0x4001F000;

    struct PpiHardwareMap {
        struct {
            volatile uint32_t EEP;
            volatile uint32_t TEP;
        } CH[32];
        volatile uint32_t CHEN;
        volatile uint32_t CHENSET;
        volatile uint32_t CHENCLR;
        struct {
            volatile uint32_t TEP;
        } FORK[32];
    };

    uint8_t index_;
};

/* Модульний будівельник апаратних зв'язків */
struct HardwareLinker {
    static void setup_timer_gpiote_adc_pipeline(
        uint32_t period_ticks,
        uint8_t gpio_pin,
        const PpiChannel& channel
    ) noexcept {
        auto* timer = reinterpret_cast<volatile uint32_t*>(0x40009000);  // TIMER1
        auto* gpiote = reinterpret_cast<volatile uint32_t*>(0x40006000); // GPIOTE
        auto* saadc = reinterpret_cast<volatile uint32_t*>(0x40007000);  // SAADC

        // 1. Конфігурація TIMER1
        timer[21] = period_ticks; // CC[0]
        timer[1] = (1UL << 0);    // SHORTS (COMPARE0_CLEAR)

        // 2. Конфігурація GPIOTE
        gpiote[64] = (3UL << 0) | (static_cast<uint32_t>(gpio_pin) << 8) | (3UL << 16);

        // 3. Зв'язування через типізовану обгортку PPI
        channel.bind_event_to_task(&timer[16], &gpiote[0]); // EVENTS_COMPARE[0] -> TASKS_OUT[0]
        channel.set_fork_task(&saadc[1]);                   // FORK -> TASKS_SAMPLE
        channel.enable();

        // 4. Запуск лічильника
        timer[0] = 1; // TASKS_START
    }
};

} // namespace hal::nrf
