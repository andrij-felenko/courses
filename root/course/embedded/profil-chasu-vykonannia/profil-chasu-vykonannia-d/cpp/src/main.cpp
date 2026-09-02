// Стенд часового профілю: обробник контуру струму на 20 кГц, який сам себе
// міряє. Осцилограф бачить строб, DWT рахує такти, фоновий код друкує
// смугу періоду, джитер і найгірший час виконання.
#include <array>
#include <atomic>
#include <charconv>
#include <cstdint>
#include <optional>
#include <span>
#include <string_view>

#include "dwt.hpp"
#include "fir.hpp"
#include "foc.hpp"
#include "inverter.hpp"
#include "strobe.hpp"

namespace {

using DebugPin = prof::GpioStrobe<GPIOB_BASE, 5U>;

constexpr std::uint32_t kCalibrationSamples = 2048U;
constexpr float kVdc = 24.0f;
// Демонстраційна електрична швидкість 50 Гц; у виробі кут дає давач положення.
constexpr auto kThetaStep = foc::Phase::step_for(50.0f, static_cast<float>(inverter::kPwmHz));
constexpr std::array<float, 4> kFirTaps{0.125f, 0.375f, 0.375f, 0.125f};

struct Profile {
    prof::CycleSpan period{};   // такти між сусідніми входами в обробник
    prof::CycleSpan exec{};     // BCET і WCET корисної роботи
    std::uint32_t overruns{0};
    bool tripped{false};
};

// Публікація структури з обробника у фоновий код без заборони переривань:
// __disable_irq() тут сам був би джерелом джитера, який ми міряємо.
// На одному ядрі досить бар'єрів рівня компілятора.
template <class T>
class SeqPublisher {
public:
    void publish(const T& value) noexcept   // тільки з обробника
    {
        seq_.store(seq_.load(std::memory_order_relaxed) + 1U, std::memory_order_relaxed);
        std::atomic_signal_fence(std::memory_order_release);
        value_ = value;
        std::atomic_signal_fence(std::memory_order_release);
        seq_.store(seq_.load(std::memory_order_relaxed) + 1U, std::memory_order_relaxed);
    }

    [[nodiscard]] std::optional<T> read() const noexcept   // тільки з фону
    {
        const std::uint32_t before = seq_.load(std::memory_order_relaxed);
        if ((before & 1U) != 0U) {
            return std::nullopt;   // обробник саме зараз пише
        }
        std::atomic_signal_fence(std::memory_order_acquire);
        T copy = value_;
        std::atomic_signal_fence(std::memory_order_acquire);
        if (seq_.load(std::memory_order_relaxed) != before) {
            return std::nullopt;
        }
        return copy;
    }

private:
    std::atomic<std::uint32_t> seq_{0};
    T value_{};
};

foc::CurrentLoop g_loop{};
prof::FirFilter<4> g_fir_a{kFirTaps};
prof::FirFilter<4> g_fir_b{kFirTaps};

Profile g_profile{};
SeqPublisher<Profile> g_published{};
std::atomic<std::uint32_t> g_isr_count{0};

foc::Phase g_theta{};
std::uint32_t g_prev_entry{0};
bool g_have_prev{false};
std::uint32_t g_overrun_run{0};

std::uint32_t g_cal_left{kCalibrationSamples};
std::uint32_t g_cal_acc_a{0};
std::uint32_t g_cal_acc_b{0};
float g_offset_a{0.0f};
float g_offset_b{0.0f};

void account(std::uint32_t entry, std::uint32_t exec) noexcept
{
    if (g_have_prev) {
        g_profile.period.add(entry - g_prev_entry);
    }
    g_prev_entry = entry;
    g_have_prev = true;
    g_profile.exec.add(exec);

    if (exec > inverter::kDeadlineCycles) {
        ++g_profile.overruns;
        if (++g_overrun_run >= 2U) {
            // Два прострочені такти поспіль — саме той сценарій, що палить
            // ключі. Міст знімаємо негайно, розбір лишаємо фоновому коду.
            inverter::trip();
            g_profile.tripped = true;
        }
    } else {
        g_overrun_run = 0U;
    }

    g_published.publish(g_profile);
}

// ---- друк у налагоджувальний порт ITM ------------------------------------

void itm_write(std::string_view text) noexcept
{
    for (const char ch : text) {
        ITM_SendChar(static_cast<std::uint32_t>(static_cast<unsigned char>(ch)));
    }
}

void itm_write(std::uint32_t value) noexcept
{
    std::array<char, 12> buffer{};
    const auto [end, ec] = std::to_chars(buffer.data(), buffer.data() + buffer.size(), value);
    if (ec == std::errc{}) {
        itm_write(std::string_view{buffer.data(), static_cast<std::size_t>(end - buffer.data())});
    }
}

void report() noexcept
{
    static std::uint32_t last = 0U;
    const std::uint32_t now = g_isr_count.load(std::memory_order_relaxed);
    if ((now - last) < inverter::kPwmHz) {
        return;   // раз на секунду; у контур фоновий код не втручається
    }
    last = now;

    const auto snapshot = g_published.read();
    if (!snapshot) {
        return;   // натрапили на оновлення — надрукуємо наступного разу
    }

    itm_write(std::string_view{"період "});
    itm_write(snapshot->period.min);
    itm_write(std::string_view{".."});
    itm_write(snapshot->period.max);
    itm_write(std::string_view{" т, джитер "});
    itm_write(snapshot->period.jitter());
    itm_write(std::string_view{" т; BCET "});
    itm_write(snapshot->exec.min);
    itm_write(std::string_view{" т, WCET "});
    itm_write(snapshot->exec.max);
    itm_write(std::string_view{" т ("});
    itm_write(prof::Dwt::micros_x100(snapshot->exec.max, inverter::kSysclkMhz));
    itm_write(std::string_view{" сотих мкс); прострочень "});
    itm_write(snapshot->overruns);
    itm_write(std::string_view{snapshot->tripped ? "; МІСТ ЗНЯТО\r\n" : "\r\n"});
}

[[noreturn]] void fault_stop(std::string_view why) noexcept
{
    inverter::trip();
    for (;;) {
        itm_write(why);
        itm_write(std::string_view{"\r\n"});
        for (volatile std::uint32_t i = 0U; i < 4000000U; ++i) {
        }
    }
}

}  // namespace

// Обробник теж лежить у SRAM: інакше кожен його перехід коштував би п'яти
// тактів очікування Flash, а промах ART додавав би випадкові такти.
extern "C" [[gnu::section(".ramfunc")]] void ADC_IRQHandler()
{
    const std::uint32_t entry = prof::Dwt::now();
    // Строб гарантовано впаде на будь-якому виході, зокрема з гілки калібрування.
    const prof::ScopeStrobe<DebugPin> strobe{};
    inverter::ack_conversion();

    const auto raw = inverter::raw_currents();

    if (g_cal_left != 0U) {
        // Калібрування нуля датчиків: міст стоїть у нульовому векторі,
        // струму немає, тож середнє за 2048 вибірок і є зсув.
        g_cal_acc_a += raw.a;
        g_cal_acc_b += raw.b;
        if (--g_cal_left == 0U) {
            g_offset_a = static_cast<float>(g_cal_acc_a) / kCalibrationSamples;
            g_offset_b = static_cast<float>(g_cal_acc_b) / kCalibrationSamples;
        }
    } else {
        const float ia = g_fir_a.push((static_cast<float>(raw.a) - g_offset_a) * inverter::kAdcToAmp);
        const float ib = g_fir_b.push((static_cast<float>(raw.b) - g_offset_b) * inverter::kAdcToAmp);

        g_theta += kThetaStep;
        inverter::set_duties(g_loop.update(ia, ib, g_theta, kVdc));
    }

    account(entry, prof::Dwt::since(entry));
    g_isr_count.fetch_add(1U, std::memory_order_relaxed);

    // Прапорець знято на початку, але запис міг ще йти шиною APB: без DSB
    // ядро встигає вийти й одразу увійти в те саме переривання ще раз.
    __DSB();
}

int main()
{
    // Тактування порту строба потрібне ще до пуску інвертора: перші
    // імпульси на екрані мають з'явитися вже на етапі калібрування.
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;
    static_cast<void>(RCC->AHB1ENR);
    DebugPin::configure();

    g_loop.build_tables();
    g_loop.reset();
    g_loop.set_targets(foc::Dq{0.0f, 2.0f});   // id = 0, iq = 2 А
    g_fir_a.reset();
    g_fir_b.reset();

    // Лічильник тактів має вже рахувати, коли прийде перше переривання,
    // інакше в смугу періоду потрапить фальшивий нуль.
    if (!prof::Dwt::enable()) {
        itm_write(std::string_view{"DWT недоступний: лишається тільки осцилограф\r\n"});
    }

    if (const auto started = inverter::bring_up(); !started) {
        fault_stop(inverter::describe(started.error()));
    }

    for (;;) {
        report();
    }
}
