#include "ew/monitor.hpp"

#include <array>
#include <optional>

#include "ew/detector.hpp"
#include "ew/sx126x.hpp"

#include "queue.h"

namespace ew {

// Контракти решти прошивки. Це наші ж рівні, тож інтерфейс лишається
// С++-ним: span і optional замість вихідних вказівників.
namespace rf {
void hopChannel() noexcept;
void setAttenuator(bool on) noexcept;
void setFecDenominator(std::uint8_t denominator) noexcept;
} // namespace rf

namespace nav {
// Складає кадр у наданий буфер і повертає span саме на заповнену частину.
std::optional<GnssFrame> snapshot(std::span<GnssSat> storage) noexcept;
void useGnss(bool allow) noexcept;
} // namespace nav

namespace fc {
std::uint8_t throttlePct() noexcept;
void reportThreat(const Verdict& verdict, const RfStats& stats, std::uint32_t dropped) noexcept;
} // namespace fc

namespace {

constexpr auto kPeriod = Millis{100}; // класифікатор працює 10 разів на секунду
constexpr auto kHold = Millis{200};   // вердикт мусить протриматися два цикли
constexpr std::size_t kQueueLen = 8;
constexpr std::size_t kMaxSats = 12;
constexpr configSTACK_DEPTH_TYPE kStackWords = 384;

// Статична черга й статичний потік: динамічної купи в польотній прошивці немає.
Detector       g_detector{};
Sx126x         g_radio{};
QueueHandle_t  g_queue{nullptr};
StaticQueue_t  g_queue_ctl{};
alignas(RfSample) std::array<std::uint8_t, kQueueLen * sizeof(RfSample)> g_queue_storage{};
StaticTask_t   g_task_ctl{};
std::array<StackType_t, kStackWords> g_task_stack{};
volatile std::uint32_t g_dropped{0};

[[nodiscard]] Millis nowMs() noexcept
{
    return Millis{static_cast<std::uint32_t>(xTaskGetTickCount()) * portTICK_PERIOD_MS};
}

void applyReaction(Threat threat) noexcept
{
    switch (threat) {
        case Threat::SpotJamming:
            // Прицільна б'є в одну частоту — тікаємо на інший канал.
            rf::hopChannel();
            break;
        case Threat::BarrageBlocking:
            // Спершу виводимо LNA з насичення, інакше новий канал теж буде глухим.
            rf::setAttenuator(true);
            rf::hopChannel();
            break;
        case Threat::PulseJamming:
            // Проти рідких сплесків рятує надлишковість FEC.
            rf::setFecDenominator(8);
            break;
        case Threat::GnssSpoofing:
            // Координатам більше не віримо: далі — інерціальне числення.
            nav::useGnss(false);
            break;
        case Threat::WeakSignal:
            // Просто далеко: стрибок каналом тут лише зашкодить.
            break;
        case Threat::None:
            // Ефір очистився — знімаємо все, що вмикали.
            rf::setAttenuator(false);
            rf::setFecDenominator(5);
            nav::useGnss(true);
            break;
    }
}

void monitorTask(void*) noexcept
{
    TickType_t last_wake = xTaskGetTickCount();
    Threat applied = Threat::None;
    std::array<GnssSat, kMaxSats> sat_storage{};

    for (;;) {
        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(kPeriod.count()));

        // Забираємо все, що встигло накопати переривання.
        RfSample sample{};
        unsigned taken = 0;
        while (xQueueReceive(g_queue, &sample, 0) == pdTRUE) {
            g_detector.push(sample);
            ++taken;
        }

        if (taken == 0) {
            // Тиша в ефірі — теж симптом. Під загороджувальною завадою пакетів
            // немає, переривань немає, і вікно б «замерзло» на старих добрих
            // вибірках. Тому знімаємо миттєвий RSSI самі: він і скаже, ефір
            // порожній чи забитий по вінця.
            if (auto s = g_radio.readSample()) {
                s->throttle_pct = fc::throttlePct();
                g_detector.push(*s);
            }
        }

        const auto verdict = g_detector.evaluate(nav::snapshot(sat_storage), nowMs());

        // Реагуємо лише на вердикт, що протримався два цикли: одиничний провал
        // у місті чи різкий крен не мусить перекидати канал.
        if (verdict.threat != applied && verdict.held >= kHold) {
            applyReaction(verdict.threat);
            applied = verdict.threat;
        }

        if (const auto stats = g_detector.stats()) {
            fc::reportThreat(verdict, *stats, g_dropped);
        }
    }
}

} // namespace

void startMonitor(UBaseType_t priority) noexcept
{
    g_dropped = 0;
    g_queue = xQueueCreateStatic(kQueueLen, sizeof(RfSample), g_queue_storage.data(),
                                 &g_queue_ctl);
    // Статичне створення не вміє провалитися через брак пам'яті, але вміє
    // через криво пораховані розміри — ловимо це на старті, а не в польоті.
    configASSERT(g_queue != nullptr);

    static_cast<void>(xTaskCreateStatic(monitorTask, "ew", kStackWords, nullptr, priority,
                                        g_task_stack.data(), &g_task_ctl));
}

std::uint32_t droppedSamples() noexcept
{
    return g_dropped;
}

} // namespace ew

extern "C" void ew_monitor_dio1_isr()
{
    // У перериванні дозволено рівно одне: короткий детермінований обмін по SPI
    // (десяток байтів статусу, одиниці мікросекунд). Жодних обчислень тут
    // немає — класифікація живе в потоці.
    auto sample = ew::g_radio.readSample();
    if (!sample) {
        return;
    }
    sample->throttle_pct = ew::fc::throttlePct();

    BaseType_t woken = pdFALSE;
    // Черга неблокуюча: якщо потік телеметрії відстав, вибірку свідомо
    // втрачаємо, але радіотракт не зупиняємо ні на такт.
    if (xQueueSendFromISR(ew::g_queue, &*sample, &woken) != pdTRUE) {
        ++ew::g_dropped;
    }
    portYIELD_FROM_ISR(woken);
}
