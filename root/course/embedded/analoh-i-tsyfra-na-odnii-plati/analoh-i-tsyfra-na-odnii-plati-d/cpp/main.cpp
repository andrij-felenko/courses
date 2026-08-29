// main.cpp — зчитування диференційного каналу з фільтрацією.
//
// Прошивка робить дві речі. Перша — тягне з ADS1220 сирі коди й проганяє їх
// крізь ковзне усереднення з відкиданням викидів. Друга, і для цієї теми
// головніша, — друкує в термінал розмах вікна в LSB та оцінку кількості
// чесних розрядів. Саме ці два числа кажуть, чи вдалося розведення: на
// правильно зонованій платі із суцільним полігоном розмах лишається в
// одиницях LSB, на розрізаній землі росте до сотень.
#include <chrono>
#include <cstdint>

#include "ads1220.hpp"
#include "board.hpp"
#include "robust_filter.hpp"

namespace {

using namespace std::chrono_literals;

// При 20 SPS звіт раз на 64 вибірки — це раз на три з гаком секунди,
// і термінал лишається читабельним.
constexpr std::uint32_t report_every = 64;

// Скільки збоїв обміну поспіль терпимо, перш ніж піднімати чип наново.
constexpr unsigned faults_before_reset = 3;

// Скидання, налаштування і запуск. Повертається лише тоді, коли чип справді
// налаштований: найчастіша причина невдачі на старті — аналогове живлення
// ще не вийшло на режим, бо LDO за феритовою бусиною підіймається повільніше
// за цифрову шину.
void bring_up(ads1220::Driver& adc)
{
    while (true) {
        const auto ready = adc.configure().and_then([&adc] { return adc.start(); });
        if (ready) {
            board::log("АЦП готовий: AIN0/AIN1, G = 32, Vref = 3.300 В, 20 SPS");
            return;
        }

        board::log("АЦП не піднявся: {}", ads1220::describe(ready.error()));
        board::sleep(200ms);
    }
}

}  // namespace

int main()
{
    board::init();

    board::SpiBus bus;
    ads1220::Driver adc{bus};
    RobustFilter<16> filter;

    bring_up(adc);

    std::uint32_t emitted = 0;
    unsigned faults = 0;

    while (true) {
        const auto sample = adc.read();

        if (!sample) {
            if (sample.error() == ads1220::Error::over_range) {
                // Не збій зв'язку, а стан входу: міст розбалансовано або
                // обірвано провід давача. Чип живий, перепідіймати нема чого.
                board::log("Вхід за межами шкали — перевірте баланс мосту");
                faults = 0;
                continue;
            }

            ++faults;
            board::log("Збій {}: {}", faults, ads1220::describe(sample.error()));

            if (faults >= faults_before_reset) {
                // Просідання живлення від кидка струму цифрової частини
                // здатне скинути чип у стандартну конфігурацію. Мовчки
                // читати з нього далі — гірше, ніж не читати зовсім.
                filter.reset();
                faults = 0;
                bring_up(adc);
            }
            continue;
        }

        faults = 0;

        const auto filtered = filter.push(sample->value);
        if (!filtered) {
            continue;  // вікно ще наповнюється
        }

        if (++emitted % report_every == 0) {
            const auto stats = filter.stats();

            board::log("U = {} нВ | розмах вікна = {} LSB | ENOB ~ {} біт | викидів {} з {}",
                       ads1220::Driver::to_nanovolts(ads1220::Code{*filtered}),
                       stats.spread,
                       stats.enob,
                       stats.rejected,
                       stats.accepted + stats.rejected);
        }
    }
}
