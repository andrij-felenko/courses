typedef struct {
    const char* name;
    uint32_t address;
    uint32_t size;
    uint8_t type;
} ResolvedSymbol;

bool find_symbol_by_name(const SafeBuffer* buf, 
                          const Elf32_Shdr* symtab_hdr, 
                          const Elf32_Shdr* strtab_hdr, 
                          const char* target_name, 
                          ResolvedSymbol* out_sym) {
    if (!buf || !symtab_hdr || !strtab_hdr || !target_name || !out_sym) return false;

    size_t num_symbols = symtab_hdr->sh_size / sizeof(Elf32_Sym);
    for (size_t i = 0; i < num_symbols; ++i) {
        size_t sym_offset = symtab_hdr->sh_offset + (i * sizeof(Elf32_Sym));
        Elf32_Sym sym;
        if (safe_read(buf, sym_offset, &sym, sizeof(Elf32_Sym))) {
            const char* name = get_string(buf, strtab_hdr->sh_offset, strtab_hdr->sh_size, sym.st_name);
            if (strcmp(name, target_name) == 0) {
                out_sym->name = name;
                out_sym->address = sym.st_value;
                out_sym->size = sym.st_size;
                out_sym->type = sym.st_info & 0x0F;
                return true;
            }
        }
    }
    return false;
}
