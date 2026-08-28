// Придушення для компілятора MSVC
[[gsl::suppress(bounds.1)]]
void write_hardware_register(uintptr_t base_addr, size_t offset, uint32_t val) {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(base_addr + offset);
    *reg = val;
}

// Придушення для аналізатора Clang-Tidy
void process_legacy_raw_packet(char* buffer) // NOLINT(cppcoreguidelines-pro-bounds-pointer-arithmetic)
{
    buffer[0] = '\0';
}
