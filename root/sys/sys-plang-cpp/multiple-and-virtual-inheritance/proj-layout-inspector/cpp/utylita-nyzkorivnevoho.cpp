void dump_memory(const void* ptr, std::size_t size, std::string_view label) {
    std::cout << "=== Розкладка пам'яті: " << label << " (" << std::dec << size << " байтів) ===\n";
    const auto* bytes = static_cast<const std::uint8_t*>(ptr);
    const auto base_addr = reinterpret_cast<std::uintptr_t>(ptr);

    for (std::size_t i = 0; i < size; i += 8) {
        std::cout << "  +" << std::setw(2) << std::setfill('0') << std::dec << i << " B [0x"
                  << std::hex << (base_addr + i) << "]: ";

        for (std::size_t j = 0; j < 8 && (i + j) < size; ++j) {
            std::cout << std::setw(2) << std::setfill('0') << std::hex
                      << static_cast<int>(bytes[i + j]) << ' ';
        }

        // Відображаємо значення як 64-бітне беззнакове слово для швидкої ідентифікації vptr
        if (i + 8 <= size) {
            std::uint64_t word = 0;
            std::memcpy(&word, bytes + i, sizeof(word));
            std::cout << " | слово: 0x" << std::setw(16) << std::setfill('0') << std::hex << word;
        }
        std::cout << '\n';
    }
    std::cout << '\n';
}
