typedef struct {
    uint32_t guest_target_pc;
    uint8_t* patch_offset_addr; // Адреса 4-байтного зміщення rel32 для патчингу
    bool     is_conditional;    // true для je (довжина 6), false для jmp (довжина 5)
} JumpPatchInfo;

typedef struct {
    uint32_t      guest_pc;
    uint8_t*      host_addr;
    size_t        host_size;
    JumpPatchInfo exits[2];
    size_t        exit_count;
} TranslationBlock;

// Патчинг переходу: запис нової відносної адреси в машинний код
static void patch_jump(const JumpPatchInfo* patch, const uint8_t* target_host_addr) {
    size_t insn_len = patch->is_conditional ? 6 : 5;
    uint8_t* insn_start = patch->patch_offset_addr - (insn_len - 4);
    int32_t rel_offset = (int32_t)(target_host_addr - (insn_start + insn_len));

    memcpy(patch->patch_offset_addr, &rel_offset, sizeof(int32_t));

#if defined(_WIN32)
    FlushInstructionCache(GetCurrentProcess(), insn_start, insn_len);
#elif defined(__GNUC__) || defined(__clang__)
    __builtin___clear_cache((char*)insn_start, (char*)insn_start + insn_len);
#endif
}
