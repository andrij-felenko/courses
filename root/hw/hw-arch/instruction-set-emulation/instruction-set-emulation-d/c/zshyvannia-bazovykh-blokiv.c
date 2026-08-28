#include <stdint.h>
#include <string.h>

// Приклад патчингу 32-бітного відносного стрибка JMP на архітектурі x86-64
void tb_chain_blocks_x86(TranslationBlock *src_tb, int branch_idx, const TranslationBlock *dst_tb) {
    uint8_t *patch_site = src_tb->jmp_patch_addr[branch_idx];
    uint8_t *target_addr = (uint8_t *)dst_tb->host_code_ptr;
    
    // Обчислення відносного зміщення: Target - (PatchSite + 5 байтів розміру інструкції JMP)
    int32_t rel_offset = (int32_t)(target_addr - (patch_site + 5));
    
    // Формування коду інструкції: E9 <4 байти зміщення> (JMP rel32)
    patch_site[0] = 0xE9;
    memcpy(patch_site + 1, &rel_offset, sizeof(int32_t));
    
    // Запам'ятовуємо зв'язок для можливої подальшої розшивки
    src_tb->jmp_dest[branch_idx] = (TranslationBlock *)dst_tb;
}
