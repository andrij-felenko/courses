void probe_state_duplication() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 2: Подвоєння стану в невіртуальному ромбі\n";
    std::cout << "=========================================================\n";

    AudioDuplexNV duplex;

    // Пряме звернення duplex.device_id було б неоднозначним (помилка компілятора).
    // Записуємо різні значення у дві незалежні копії:
    duplex.AudioIn::device_id  = 0xAAAA1111;
    duplex.AudioOut::device_id = 0xBBBB2222;

    std::cout << "Значення duplex.AudioIn::device_id  = 0x" << std::hex << duplex.AudioIn::device_id << '\n';
    std::cout << "Значення duplex.AudioOut::device_id = 0x" << std::hex << duplex.AudioOut::device_id << '\n\n';

    const auto* dev_in_ptr  = static_cast<Device*>(static_cast<AudioIn*>(&duplex));
    const auto* dev_out_ptr = static_cast<Device*>(static_cast<AudioOut*>(&duplex));

    const auto addr_dev_in  = reinterpret_cast<std::uintptr_t>(dev_in_ptr);
    const auto addr_dev_out = reinterpret_cast<std::uintptr_t>(dev_out_ptr);

    std::cout << "Адреса підоб'єкта Device (через AudioIn) : 0x" << std::hex << addr_dev_in << '\n';
    std::cout << "Адреса підоб'єкта Device (через AudioOut): 0x" << std::hex << addr_dev_out << '\n';
    std::cout << "Відстань між двома підоб'єктами Device    : " << std::dec
              << (addr_dev_out - addr_dev_in) << " байтів\n\n";

    std::cout << "Виклик віртуальних методів через різні інтерфейси:\n";
    std::cout << "1. Через AudioIn*:\n";
    AudioIn* in_ptr = &duplex;
    in_ptr->ping();

    std::cout << "2. Через AudioOut*:\n";
    AudioOut* out_ptr = &duplex;
    out_ptr->ping();
    std::cout << '\n';
}
