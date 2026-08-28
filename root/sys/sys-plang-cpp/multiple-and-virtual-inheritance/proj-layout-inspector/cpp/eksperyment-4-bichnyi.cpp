void probe_side_casting() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 4: Side-cast через dynamic_cast\n";
    std::cout << "=========================================================\n";

    auto duplex = std::make_unique<AudioDuplexV>();
    VirtualAudioIn* in_branch = duplex.get();

    std::cout << "Початковий покажчик VirtualAudioIn*: 0x" << std::hex
              << reinterpret_cast<std::uintptr_t>(in_branch) << '\n';

    // Спроба static_cast призвела б до помилки компіляції:
    // VirtualAudioOut* out = static_cast<VirtualAudioOut*>(in_branch);

    // dynamic_cast успішно виконує бічний перехід за допомогою RTTI:
    VirtualAudioOut* out_branch = dynamic_cast<VirtualAudioOut*>(in_branch);

    if (out_branch != nullptr) {
        const auto addr_in  = reinterpret_cast<std::uintptr_t>(in_branch);
        const auto addr_out = reinterpret_cast<std::uintptr_t>(out_branch);
        std::cout << "Side-cast успішно виконано:\n";
        std::cout << "  Адреса VirtualAudioIn*  : 0x" << std::hex << addr_in << '\n';
        std::cout << "  Адреса VirtualAudioOut* : 0x" << std::hex << addr_out << '\n';
        std::cout << "  Різниця адрес           : +" << std::dec << (addr_out - addr_in) << " байтів\n";
    } else {
        std::cout << "Помилка: dynamic_cast повернув nullptr!\n";
    }
    std::cout << '\n';
}
