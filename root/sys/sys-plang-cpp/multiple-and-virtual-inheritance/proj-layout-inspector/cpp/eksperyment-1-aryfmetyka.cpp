void probe_pointer_adjustments() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 1: Зсуви покажчиків у невіртуальному об'єкті\n";
    std::cout << "=========================================================\n";

    auto obj = std::make_unique<AudioDuplexNV>();
    auto* raw_duplex = obj.get();
    const auto addr_root = reinterpret_cast<std::uintptr_t>(raw_duplex);

    // Статичний upcast до першої бази (Primary Base)
    AudioIn* in_branch = raw_duplex;
    const auto addr_in = reinterpret_cast<std::uintptr_t>(in_branch);

    // Статичний upcast до другої бази (Secondary Base)
    AudioOut* out_branch = raw_duplex;
    const auto addr_out = reinterpret_cast<std::uintptr_t>(out_branch);

    std::cout << "Адреса AudioDuplexNV* : 0x" << std::hex << addr_root << " (базовий початок)\n";
    std::cout << "Адреса AudioIn*        : 0x" << std::hex << addr_in   << " (зсув +"
              << std::dec << (addr_in - addr_root) << " B)\n";
    std::cout << "Адреса AudioOut*       : 0x" << std::hex << addr_out  << " (зсув +"
              << std::dec << (addr_out - addr_root) << " B)\n\n";

    // Порівняння поведінки static_cast та reinterpret_cast
    auto* safe_out = static_cast<AudioOut*>(raw_duplex);
    auto* dangerous_out = reinterpret_cast<AudioOut*>(raw_duplex);

    std::cout << "Результат static_cast<AudioOut*>     : 0x" << std::hex << reinterpret_cast<std::uintptr_t>(safe_out)
              << " (коректно додано зсув)\n";
    std::cout << "Результат reinterpret_cast<AudioOut*>: 0x" << std::hex << reinterpret_cast<std::uintptr_t>(dangerous_out)
              << " (ПОМИЛКА: адреса не змінилася!)\n\n";

    std::cout << "Звернення через коректний static_cast:\n";
    std::cout << "  safe_out->buffer_size = " << std::dec << safe_out->buffer_size << " (очікувано 1024)\n";

    std::cout << "Звернення через некоректний reinterpret_cast:\n";
    std::cout << "  dangerous_out->buffer_size = " << std::dec << dangerous_out->buffer_size
              << " (прочитано sample_rate першої бази!)\n\n";

    // Крайовий випадок: поведінка при приведенні нульового вказівника
    AudioDuplexNV* null_duplex = nullptr;
    AudioOut* null_out = null_duplex; // Неявний static_cast над nullptr

    std::cout << "Приведення nullptr:\n";
    std::cout << "  null_duplex = " << static_cast<void*>(null_duplex) << '\n';
    std::cout << "  null_out    = " << static_cast<void*>(null_out)
              << " (компілятор перевірив на 0 перед додаванням зсуву!)\n\n";

    dump_memory(raw_duplex, sizeof(AudioDuplexNV), "AudioDuplexNV");
}
