#include <cstdint>
#include <cstring>

void chain_blocks_x86(TranslationBlock& src_tb, size_t branch_idx, const TranslationBlock& dst_tb) noexcept {
    uint8_t* patch_site = src_tb.jmp_patch_addr[branch_idx];
    auto* target_addr = static_cast<uint8_t*>(dst_tb.host_code_ptr);
    
    // Відносне 32-бітне зміщення для інструкції JMP rel32 (опкод 0xE9)
    int32_t rel_offset = static_cast<int32_t>(target_addr - (patch_site + 5));
    
    patch_site[0] = 0xE9;
    std::memcpy(patch_site + 1, &rel_offset, sizeof(int32_t));
    
    src_tb.jmp_dest[branch_idx] = const_cast<TranslationBlock*>(&dst_tb);
}
