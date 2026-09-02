// Пульт: послідовність запуску й головна задача реального часу 1 кГц.
#include <atomic>
#include <chrono>
#include <cstdint>

#include "battery.hpp"
#include "gimbals.hpp"
#include "hal.hpp"
#include "hud.hpp"
#include "protocol.hpp"
#include "sx1280.hpp"

namespace console {
namespace {

using namespace std::chrono_literals;

constexpr auto kTxDeadline = 700us;   // кадр 14 Б на 1.3 Мбіт/с іде ~450 мкс
constexpr auto kRxWindow = 260us;
constexpr std::uint32_t kWatchdogMs = 15;
constexpr std::uint8_t kRadioFaultLimit = 3;
constexpr std::uint16_t kFailsafeLosses = 200;   // 200 мс мовчання борту

// Єдине, що переривання таймера робить із рештою прошивки. Ні пакування, ні
// SPI, ні скидання watchdog: watchdog, скинутий звідси, справно спрацьовував
// би й тоді, коли головна задача давно висить, і ховав би відмову.
std::atomic<std::uint32_t> g_ticks{0};

}   // namespace

extern "C" void console_timer_isr()
{
    g_ticks.fetch_add(1, std::memory_order_relaxed);
}

class Console {
public:
    [[nodiscard]] bool boot() noexcept
    {
        hal::init();
        if (!latch_.engage()) {
            return false;
        }
        if (!radio_.begin()) {
            return false;
        }

        // POST: двадцять мілісекунд живих відліків, щоб устоявся IIR, і аж
        // тоді маємо право судити про положення газу й справність осей.
        for (int i = 0; i < 20; ++i) {
            const auto raw = hal::axes();
            hal::invalidate(std::as_bytes(raw));
            (void)gimbals_.process(raw);
            battery_.sample();
            hal::delay(1ms);
        }
        return battery_.level() != BatteryMonitor::Level::Critical;
    }

    [[noreturn]] void run() noexcept
    {
        hal::hal_timer_start_1khz(&console_timer_isr);
        hal::hal_watchdog_start(kWatchdogMs);

        for (;;) {
            const auto ticks = g_ticks.load(std::memory_order_relaxed);
            if (ticks == served_) {
                continue;   // слот починає таймер, а не ми
            }
            if (ticks - served_ > 1) {
                ++overruns_;   // не вклалися в мілісекунду; лічильник видно в GDB
            }
            served_ = ticks;

            if (runSlot()) {
                // Єдине місце, де скидається watchdog: осі оцифровані, кадр
                // пішов у ефір, телеметрія перевірена за CRC.
                hal::hal_watchdog_kick();
            }
        }
    }

    // Відмова до старту watchdog: миготимо вібромотором і не йдемо далі, бо
    // відпускати апарат у ефір із несправним пультом гірше, ніж не злетіти.
    [[noreturn]] void halt(int pulses) noexcept
    {
        latch_.release();
        for (;;) {
            for (int i = 0; i < pulses; ++i) {
                hal::haptic(200);
                hal::delay(120ms);
                hal::haptic(0);
                hal::delay(180ms);
            }
            hal::delay(800ms);
        }
    }

private:
    bool radioFault() noexcept
    {
        if (++radioFaults_ >= kRadioFaultLimit) {
            radioFaults_ = 0;
            // Спроба підняти трансивер зірве кілька слотів — це свідомо:
            // гірший варіант лише мовчазний ефір.
            (void)radio_.begin();
        }
        return false;   // watchdog не скидаємо: 15 відмов підряд перезапустять пульт
    }

    bool runSlot() noexcept
    {
        // 1. Осі. DMA поклав свіжі відліки повз кеш ядра — інвалідуємо рядки.
        const auto rawGimbals = hal::axes();
        hal::invalidate(std::as_bytes(rawGimbals));
        const auto scaled = gimbals_.process(rawGimbals);

        const std::uint16_t switches = hal::switches();
        const Fault faults = gimbals_.safety(scaled, switches);
        const std::uint8_t aux = gimbals_.auxUpdate(switches);

        hud_.update(HudSnapshot{.packMillivolts = battery_.millivolts(),
                                .batteryLevel = battery_.level(),
                                .linkQuality = stats_.quality(),
                                .lostFrames = lostFrames_,
                                .armed = (switches & hal::sw::Arm) != 0,
                                .faults = faults,
                                .air = air_});

        if (any(faults)) {
            // Блокування передачі: в ефір не йде нічого, поки оператор не
            // поверне газ у нуль і не зніме Arm. Вібро — короткими поштовхами
            // раз на пів секунди, щоб його чули крізь рукавицю.
            hal::haptic(served_ % 500 < 120 ? 180 : 0);
            hud_.servicePage();
            return true;   // задача відпрацювала штатно, watchdog скидаємо
        }
        hal::haptic(0);

        std::uint8_t flags = 0;
        if (switches & hal::sw::Arm) {
            flags |= flag::Armed;
        }
        if (switches & hal::sw::RateHigh) {
            flags |= flag::RateHigh;
        }
        if (switches & hal::sw::Payload) {
            flags |= flag::Payload;
        }
        if (lostFrames_ > kFailsafeLosses) {
            flags |= flag::Failsafe;
        }

        // 2. Кадр і передача.
        const Frame frame = UplinkFrame{.axes = scaled,
                                        .switches = switches,
                                        .flags = flags,
                                        .aux = aux,
                                        .sequence = sequence_++}
                                .serialize();
        if (!radio_.transmit(frame)) {
            return radioFault();
        }

        // 3. PA в ефірі близько 450 мкс, шина SPI при цьому вільна — саме
        //    сюди лягає фонова графіка.
        hud_.servicePage();

        if (!radio_.waitIrq(irq::TxDone, kTxDeadline)) {
            return radioFault();
        }

        // 4. Перемикання TDD у прийом і друга порція графіки.
        if (!radio_.listen(kRxWindow)) {
            return radioFault();
        }
        hud_.servicePage();

        const auto event = radio_.waitIrq(irq::RxDone | irq::RxTxTimeout | irq::CrcError,
                                          kRxWindow + 100us);
        if (!event) {
            // Чип не сказав навіть «таймаут» — це відмова трансивера, а не
            // втрачений пакет.
            return radioFault();
        }

        bool received = false;
        if (*event & irq::RxDone) {
            if (const auto packet = radio_.read()) {
                if (const auto telemetry = Telemetry::parse(packet->payload)) {
                    air_ = *telemetry;
                    air_.rssiDbm = static_cast<std::int8_t>(packet->rssiDbm);
                    received = true;
                    lostFrames_ = 0;
                }
            }
        }
        if (!received && lostFrames_ < 60000) {
            ++lostFrames_;
        }
        stats_.mark(received);
        radioFaults_ = 0;

        // 5. Вікно, у якому PA вже вимкнений, а наступна посилка ще не
        //    почалася: тільки тут напруга батареї не просаджена стрибком
        //    струму на 95 мА.
        if ((served_ & 0x07u) == 0) {
            battery_.sample();
        }
        return true;
    }

    PowerLatch latch_{};
    Sx1280 radio_{static_cast<std::uint8_t>(kFrameLength)};
    Gimbals gimbals_{};
    BatteryMonitor battery_{};
    Hud hud_{};
    LinkStats stats_{};
    Telemetry air_{};
    std::uint32_t served_{0};
    std::uint32_t overruns_{0};
    std::uint16_t lostFrames_{0};
    std::uint8_t sequence_{0};
    std::uint8_t radioFaults_{0};
};

}   // namespace console

int main()
{
    static console::Console pult;

    if (!pult.boot()) {
        pult.halt(2);
    }
    pult.run();
}
