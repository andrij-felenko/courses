#include <cstdint>
#include <string_view>
#include <span>
#include <optional>

namespace symbols {

struct SymbolInfo {
    std::string_view name;
    std::uint32_t address;
    std::uint32_t size;
    std::uint8_t type;
};

[[nodiscard]] std::optional<SymbolInfo> find_symbol(
    std::span<const std::uint8_t> buffer,
    const elf::SectionHeader32& symtab_hdr,
    const elf::SectionHeader32& strtab_hdr,
    std::string_view target_name) noexcept {
    if (strtab_hdr.offset + strtab_hdr.size > buffer.size()) return std::nullopt;
    const char* strtab = reinterpret_cast<const char*>(buffer.data() + strtab_hdr.offset);

    const auto num_symbols = symtab_hdr.size / sizeof(Elf32_Sym);
    for (std::size_t i = 0; i < num_symbols; ++i) {
        const auto sym_off = symtab_hdr.offset + (i * sizeof(Elf32_Sym));
        if (sym_off + sizeof(Elf32_Sym) > buffer.size()) break;

        const auto* sym = reinterpret_cast<const Elf32_Sym*>(buffer.data() + sym_off);
        if (sym->st_name < strtab_hdr.size) {
            std::string_view name(strtab + sym->st_name);
            if (name == target_name) {
                return SymbolInfo{
                    .name = name,
                    .address = sym->st_value,
                    .size = sym->st_size,
                    .type = static_cast<std::uint8_t>(sym->st_info & 0x0FU)
                };
            }
        }
    }
    return std::nullopt;
}

} // namespace symbols
