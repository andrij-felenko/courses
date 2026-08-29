#include <format>
#include <iostream>
#include <string_view>

#include "video/budget.hpp"
#include "video/platform.hpp"

namespace {

void printPlatformFit(const video::Budget& budget)
{
    std::cout << "   Придатність платформ:\n";
    for (const auto& platform : video::catalogue()) {
        const auto fit = video::check(platform, budget);
        std::cout << std::format("     {:<36} шина {:6.1f} %, пам'ять {:6.1f} % — {}\n",
                                 platform.name, fit.busLoadPercent, fit.ramLoadPercent,
                                 video::describe(fit.verdict));
    }
}

void report(std::string_view title, const video::Config& cfg)
{
    std::cout << std::format("\n=== {} ===\n", title);

    const auto result = video::evaluate(cfg);
    if (!result) {
        std::cout << std::format("   Конфігурацію відхилено: {}\n", video::describe(result.error()));
        return;
    }
    const video::Budget& budget = *result;

    std::cout << std::format("   Кодек: {}, {}x{} @ {} fps, {}-біт RAW\n",
                             video::name(cfg.codec), cfg.width, cfg.height, cfg.fps,
                             static_cast<unsigned>(cfg.rawDepthBits));
    std::cout << std::format("1. Сирий піксельний потік сенсора:      {:8.2f} Мбіт/с\n", budget.rawSensorMbps);
    std::cout << std::format("2. Бітрейт стисненого потоку:           {:8.2f} Мбіт/с\n", budget.codecMbps);
    std::cout << std::format("3. Навантаження на шину пам'яті:        {:8.1f} МБ/с\n",   budget.dramMBps);
    std::cout << std::format("4. Пул буферів ({} шт. по {:.2f} МБ):     {:8.2f} МБ\n",
                             budget.frameBuffers, budget.yuvFrameMB, budget.ramPoolMB);
    std::cout << std::format("5. Споживання вдень:                    {:8.2f} Вт\n",     budget.powerDayW);
    std::cout << std::format("6. Споживання вночі (ІЧ бере {:.2f} Вт):  {:8.2f} Вт\n",
                             budget.irElectricalW, budget.powerNightW);
    std::cout << std::format("7. Автономність, безперервний стрімінг: {:8.1f} годин\n",
                             budget.streamingAutonomy.count());
    std::cout << std::format("8. Автономність, Edge AI ({:.2f} % часу): {:8.1f} діб\n",
                             cfg.edgeDutyCycle * 100.0, budget.edgeAutonomy.count());
    std::cout << std::format("   Виграш подійного режиму:             {:8.0f} разів\n",
                             video::Hours{budget.edgeAutonomy} / budget.streamingAutonomy);

    printPlatformFit(budget);
}

}  // namespace

int main()
{
    // Профіль 1: типова автономна камера спостереження з нічним підсвічуванням.
    const video::Config cam1080p{
        .width = 1920,
        .height = 1080,
        .fps = 30,
        .rawDepthBits = 10,
        .codec = video::Codec::H264Avc,
        .refFrames = 4,
        .irOpticalW = 1.0,        // 1 Вт світла на дистанцію ~15 м
        .irLedEfficiency = 0.30,  // ККД ІЧ-світлодіода 940 нм
        .socBaseW = 0.50,
        .vpuW = 0.30,
        .sensorW = 0.20,
        .radioTxW = 1.10,
        .standbyW = 0.030,        // PIR + RTC + домен утримання
        .batteryWh = 37.0,        // Li-ion 10 А·год при 3.7 В
        .edgeDutyCycle = 0.005    // прокидаємось на 0.5 % часу
    };
    report("1080p @ 30 fps, H.264, нічний режим", cam1080p);

    // Профіль 2: та сама плата, але 4K — саме тут ламається шина.
    video::Config cam4k = cam1080p;
    cam4k.width = 3840;
    cam4k.height = 2160;
    cam4k.codec = video::Codec::H265Hevc;
    cam4k.vpuW = 0.90;  // кодування 4K дорожче для VPU
    report("4K @ 30 fps, H.265, нічний режим", cam4k);

    // Профіль 3: сирий Bayer без кодека — множник шини менший, зате бітрейт
    // нічим не збити.
    video::Config camRaw = cam1080p;
    camRaw.codec = video::Codec::RawBayer;
    report("1080p @ 30 fps, RAW Bayer без стиснення", camRaw);

    // Профіль 4: типова помилка в специфікації — прожектор є, ККД забули.
    // Без валідації тут вийшло б ділення на нуль і «нескінченна» автономність.
    video::Config broken = cam1080p;
    broken.irLedEfficiency = 0.0;
    report("1080p, ІЧ без указаного ККД", broken);

    return 0;
}
