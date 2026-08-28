#include <iostream>
#include <fstream>
#include <iomanip>
#include <array>
#include <cstdint>
#include <string_view>
#include <span>

namespace {

constexpr uint32_t generate_crc32_entry(uint32_t byte_val, uint32_t polynomial) noexcept {
    uint32_t crc = byte_val;
    for (int bit = 0; bit < 8; ++bit) {
        crc = (crc & 1U) ? ((crc >> 1U) ^ polynomial) : (crc >> 1U);
    }
    return crc;
}

constexpr auto make_crc_table(uint32_t polynomial) noexcept {
    std::array<uint32_t, 256> table{};
    for (uint32_t i = 0; i < 256; ++i) {
        table[i] = generate_crc32_entry(i, polynomial);
    }
    return table;
}

} // namespace

int main(int argc, char* argv[]) {
    const std::span<char*> args(argv, static_cast<size_t>(argc));
    if (args.size() < 2) {
        std::cerr << "Використання: " << args[0] << " <шлях_до_вихідного_файлу>\n";
        return 1;
    }

    std::ofstream out(args[1], std::ios::trunc);
    if (!out.is_open()) {
        std::cerr << "Помилка відкриття файлу для запису: " << args[1] << '\n';
        return 1;
    }

    constexpr uint32_t ieee_poly = 0xEDB88320U;
    constexpr auto table = make_crc_table(ieee_poly);

    out << "/* Автоматично згенеровано утилітою table_gen на хості. Не редагувати! */\n";
    out << "#include <stdint.h>\n\n";
    out << "extern const uint32_t g_crc32_lookup[256] = {\n";

    for (size_t i = 0; i < table.size(); ++i) {
        if (i % 8 == 0) out << "    ";
        out << "0x" << std::hex << std::uppercase << std::setfill('0') << std::setw(8) << table[i] << "U";
        if (i + 1 < table.size()) out << ", ";
        if (i % 8 == 7) out << '\n';
    }

    out << "};\n";
    return 0;
}
