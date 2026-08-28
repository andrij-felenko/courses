// Придушення для MSVC C++ Core Check
[[gsl::suppress(bounds.1)]]
void legacy_hardware_access(int* raw_io_port) {
    // Дозволено тимчасове використання адресної арифметики для регістрів MMIO
    *(raw_io_port + 0x10) = 0xFF;
}

// Придушення для Clang-Tidy
void parse_legacy_buffer(char* buf) // NOLINT(cppcoreguidelines-pro-bounds-pointer-arithmetic)
{
    buf[4] = '\0';
}
