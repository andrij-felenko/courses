// Рушій набору: таблиця дескрипторів, бюджет часу на кожен тест і зупинка
// після провалу блокувального тесту.

#include <array>
#include <cstdint>

#include "bus_probe.hpp"
#include "fct.hpp"
#include "hal.hpp"
#include "platform_probe.hpp"
#include "ram_march.hpp"
#include "report.hpp"
#include "rf_calibration.hpp"

namespace {

constexpr std::array<fct::Case, 7> kSuite{{
    {"POWER_RAILS", &fct::test_power_rails, 50'000, true},
    {"CLOCK_PLL", &fct::test_clock_pll, 20'000, true},
    {"RAM_MARCH_C", &fct::test_ram_march, 60'000, false},
    {"I2C_DEVICES", &fct::test_i2c_devices, 40'000, false},
    {"SPI_FLASH_ID", &fct::test_spi_flash, 20'000, false},
    {"RF_CW", &fct::test_rf_cw, 4'000'000, false},
    {"OTP_TRIM", &fct::test_otp_trim, 100'000, false}
}};

fct::JsonReport g_report;

void run_suite() noexcept
{
    bool overall_pass = true;
    bool halted = false;
    const fct::Deadline total{0};

    g_report.begin();

    for (const auto& test : kSuite) {
        fct::Outcome outcome = fct::fail(fct::Error::Skipped,
                                         "Набір зупинено попереднім провалом");
        std::uint32_t spent = 0;

        if (!halted) {
            hal::watchdog_kick();
            const fct::Deadline slot{test.budget_us};
            outcome = test.run();
            spent = slot.elapsed_us();

            // Тест не переривають ззовні: його час сторожать дедлайни
            // всередині. Перевищення означає, що якийсь із них прогавили.
            if (outcome && spent > test.budget_us) {
                outcome = fct::fail(fct::Error::Timeout, "Перевищено бюджет часу",
                                    static_cast<std::int32_t>(spent), "us");
            }
        }

        if (!outcome) {
            overall_pass = false;
            if (test.blocking) {
                // Живлення чи тактування не в нормі — далі не йдемо: радіо
                // й пропалювання OTP на битій платі лише шкодять.
                halted = true;
            }
        }

        g_report.add(test.name, outcome, spent);
    }

    g_report.finish(overall_pass, total.elapsed_us());
    hal::result_indicate(overall_pass);
}

}  // namespace

int main()
{
    hal::board_init();
    run_suite();

    // Стенд сам зніме живлення після зчитування звіту; до того моменту
    // лише годуємо сторожовий таймер.
    for (;;) {
        hal::watchdog_kick();
    }
}
