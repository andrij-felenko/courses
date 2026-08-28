#include <iostream>
#include <span>
#include <string_view>

int main(int argc, char* argv[]) {
    const std::span<char*> args(argv, argc);
    std::string_view target_chip = "m328p";
    bool allow_hvpp = false;
    bool output_json = false;

    avr::tool::FuseBuilder builder;
    builder.set_clock(avr::tool::ClockSource::ExternalCrystalHigh, avr::tool::StartupTime::MaxDelayCeramic, false)
           .set_bod(avr::tool::BodLevel::V2_7)
           .set_bootloader(avr::tool::BootSize::Words256, true)
           .set_isp_enabled(true);

    for (size_t i = 1; i < args.size(); ++i) {
        const std::string_view arg = args[i];
        if (arg == "--chip" && i + 1 < args.size()) {
            target_chip = args[++i];
        } else if (arg == "--allow-hvpp") {
            allow_hvpp = true;
        } else if (arg == "--json") {
            output_json = true;
        }
    }

    const auto raw = builder.build();
    auto validation_result = avr::tool::FuseValidator::validate(raw, allow_hvpp);

    if (output_json) {
        std::cout << std::format("{{\n  \"chip\": \"{}\",\n  \"lfuse\": \"0x{:02X}\",\n  \"hfuse\": \"0x{:02X}\",\n  \"efuse\": \"0x{:02X}\",\n  \"lock\": \"0x{:02X}\",\n  \"is_safe\": {}\n}}\n",
                                 target_chip, raw.low, raw.high, raw.extended, raw.lock, validation_result.has_value());
    } else {
        std::cout << std::format("=== Результати розрахунку фьюзів для {} ===\n", target_chip);
        std::cout << std::format(" LFUSE: 0x{:02X}, HFUSE: 0x{:02X}, EFUSE: 0x{:02X}, LOCK: 0x{:02X}\n\n",
                                 raw.low, raw.high, raw.extended, raw.lock);
        std::cout << std::format("Команда AVRDUDE:\n  {}\n\n",
                                 avr::tool::FuseValidator::to_avrdude_args(raw, target_chip));

        if (validation_result.has_value()) {
            std::cout << "Статус: БЕЗПЕЧНО ДО ПРОШИВКИ.\n";
            for (const auto& msg : validation_result.value()) {
                std::cout << std::format(" [ПОПЕРЕДЖЕННЯ] {}\n", msg.text);
            }
        } else {
            std::cerr << std::format("Статус: ПОМИЛКА БЕЗПЕКИ — {}\n", validation_result.error());
            return EXIT_FAILURE;
        }
    }

    return EXIT_SUCCESS;
}
