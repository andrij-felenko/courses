#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <exception>
#include <format>
#include <iostream>
#include <limits>
#include <tuple>

#include "screen.hpp"

namespace {

using namespace gcs;

// Модель польоту з зав'язки статті: 40 хвилин, батарея тихо сповзає з 22.2 В
// до 13.8 В — 3.7 мВ/с, тобто нижче будь-якого порогу чутливості сітківки.
constexpr std::uint32_t kFlightSeconds{2400};

float batteryVoltage(std::uint32_t t) {
    if (t < 120) {
        return 22.2f;
    }
    const float k = std::min(1.0f, static_cast<float>(t - 120) / (kFlightSeconds - 120));
    return 22.2f - 8.4f * k;
}

bool brownout(std::uint32_t t) {
    return batteryVoltage(t) < 14.5f;   // просідання DC-DC тягне за собою решту борту
}

float escTemp(std::uint32_t t) {
    return brownout(t) ? 128.0f : 46.0f + 0.004f * static_cast<float>(t);
}

float linkRssi(std::uint32_t t) {
    if (t >= 1500 && t <= 1506) {
        return std::numeric_limits<float>::quiet_NaN();   // побиті кадри телеметрії
    }
    if (brownout(t)) {
        return -97.0f;
    }
    return -62.0f + static_cast<float>((t * 37) % 7) * 0.3f;
}

float gpsHdop(std::uint32_t t) {
    return brownout(t) ? 6.4f : 0.9f + static_cast<float>((t * 13) % 5) * 0.05f;
}

void printFrame(std::uint32_t t, const Frame& f) {
    std::cout << std::format("\n== t={:02}:{:02}  екран: {} ==\n", t / 60, t % 60, stateName(f.state));
    for (const std::string& banner : f.banners) {
        std::cout << "   " << banner << '\n';
    }
    if (f.bannersSuppressed > 0) {
        std::cout << std::format("   ... ще {} тривог згорнуто{}\n", f.bannersSuppressed,
                                 f.flood ? "  [ЛАВИНА ТРИВОГ, EEMUA 191]" : "");
    }
    for (const Cell& cell : f.cells) {
        if (cell.draw == Draw::Hidden) {
            continue;
        }
        std::cout << std::format("   {:<7} {:<5} {}{}\n", cell.label, inkName(cell.ink), cell.text,
                                 cell.draw == Draw::Dim ? "   (приглушено)" : "");
    }
    if (f.hidden > 0) {
        std::cout << std::format("   [{} другорядних віджетів прибрано з екрана]\n", f.hidden);
    }
}

} // namespace

int main() try {
    Channel battery{"BATT", "V", Danger::Falling,
                    Limits{.warn = 18.0f, .crit = 14.0f, .maxDriftRate = 0.002f, .hysteresis = 0.4f}};
    Channel esc{"ESC T", "C", Danger::Rising,
                Limits{.warn = 80.0f, .crit = 95.0f, .maxDriftRate = 0.05f, .hysteresis = 3.0f}};
    Channel link{"LINK", "dBm", Danger::Falling,
                 Limits{.warn = -85.0f, .crit = -95.0f, .maxDriftRate = 0.0f, .hysteresis = 3.0f}};
    Channel hdop{"HDOP", "", Danger::Rising,
                 Limits{.warn = 2.0f, .crit = 4.0f, .maxDriftRate = 0.0f, .hysteresis = 0.3f}};

    Screen screen;
    screen.addMetric("BATT", Tier::Core, battery);
    screen.addMetric("LINK", Tier::Core, link);
    screen.addStatic("MODE", Tier::Core, "AUTO");
    screen.addMetric("ESC T", Tier::Secondary, esc);
    screen.addMetric("HDOP", Tier::Secondary, hdop);
    screen.addStatic("FW", Tier::Secondary, "v4.3.1-rc2");
    screen.addStatic("PKT RX", Tier::Secondary, "312481");

    State previous = State::Calm;
    for (std::uint32_t t = 0; t <= kFlightSeconds; ++t) {
        const Millis now{t * 1000};

        std::ignore = battery.update(batteryVoltage(t), now);
        std::ignore = esc.update(escTemp(t), now);
        if (auto taken = link.update(linkRssi(t), now); !taken) {
            // Вибірку відкинуто (NaN у кадрі) — канал сам постаріє й скаже про це.
        }
        if (t < 2000) {
            std::ignore = hdop.update(gpsHdop(t), now);   // далі GPS-модуль замовкає
        }

        battery.tick(now);
        esc.tick(now);
        link.tick(now);
        hdop.tick(now);

        const Frame frame = screen.render(now);
        if (frame.state != previous || t % 300 == 0) {
            printFrame(t, frame);
            previous = frame.state;
        }
    }
    return 0;
} catch (const std::exception& e) {
    std::cerr << "конфігурація HUD непослідовна: " << e.what() << '\n';
    return 1;
}
