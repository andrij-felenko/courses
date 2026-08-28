void run_cpp_unit_tests() {
    std::cout << "=== Запуск модульних тестів валідатора (C++20) ===\n";

    // 1. Перевірка Factory Profile
    constexpr auto factory_bytes = avr::tool::FuseBuilder{}
        .set_clock(avr::tool::ClockSource::InternalRc8MHz, avr::tool::StartupTime::MaxDelayCeramic, true)
        .set_isp_enabled(true)
        .set_bootloader(avr::tool::BootSize::Words2048, false)
        .set_bod(avr::tool::BodLevel::Disabled)
        .build();

    static_assert(factory_bytes.low == 0x62U, "Factory Low Fuse має бути 0x62");
    static_assert(factory_bytes.high == 0xD9U, "Factory High Fuse має бути 0xD9");
    static_assert(factory_bytes.extended == 0xFFU, "Factory Extended Fuse має бути 0xFF");
    std::cout << " [PASS] Compile-time constexpr валідацію Factory Profile виконано успішно.\n";

    // 2. Перевірка перехоплення критичної помилки RSTDISBL
    constexpr auto brick_bytes = avr::tool::FuseBuilder{}
        .set_reset_as_gpio(true) // Спроба вимкнути Reset
        .build();

    auto audit_res = avr::tool::FuseValidator::validate(brick_bytes, false);
    if (!audit_res.has_value()) {
        std::cout << " [PASS] Рушій валідації успішно заблокував небезпечну конфігурацію: " 
                  << audit_res.error() << "\n";
    } else {
        std::cerr << " [FAIL] Валідатор пропустив небезпечний RSTDISBL!\n";
    }
}
