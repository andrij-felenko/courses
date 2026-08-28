#include <string.h>

#define REG_OFFSET(idx) ((uint8_t)((idx) * sizeof(uint32_t)))
#define PC_OFFSET       ((uint8_t)(offsetof(GuestContext, pc)))
#define ZF_OFFSET       ((uint8_t)(offsetof(GuestContext, zf)))
#define HALT_OFFSET     ((uint8_t)(offsetof(GuestContext, halted)))

typedef struct {
    uint8_t* code;
    size_t   size;
} CodeEmitter;

static void emit_byte(CodeEmitter* e, uint8_t b) {
    e->code[e->size++] = b;
}

static void emit_u32(CodeEmitter* e, uint32_t val) {
    memcpy(e->code + e->size, &val, sizeof(uint32_t));
    e->size += sizeof(uint32_t);
}

// Запис константи: mov [rdi + reg_off], imm32
static void emit_mov_imm(CodeEmitter* e, uint8_t reg_idx, uint32_t imm) {
    emit_byte(e, 0xC7); // MOV r/m32, imm32
    emit_byte(e, 0x47); // ModR/M: [rdi + disp8]
    emit_byte(e, REG_OFFSET(reg_idx));
    emit_u32(e, imm);
}

// Додавання: mov eax, [rdi + rs]; add [rdi + rd], eax
static void emit_add(CodeEmitter* e, uint8_t rd, uint8_t rs) {
    emit_byte(e, 0x8B); emit_byte(e, 0x47); emit_byte(e, REG_OFFSET(rs));
    emit_byte(e, 0x01); emit_byte(e, 0x47); emit_byte(e, REG_OFFSET(rd));
    emit_byte(e, 0x0F); emit_byte(e, 0x94); emit_byte(e, 0xC0); // sete al
    emit_byte(e, 0x0F); emit_byte(e, 0xB6); emit_byte(e, 0xC0); // movzx eax, al
    emit_byte(e, 0x89); emit_byte(e, 0x47); emit_byte(e, ZF_OFFSET);
}

// Віднімання: mov eax, [rdi + rs]; sub [rdi + rd], eax
static void emit_sub(CodeEmitter* e, uint8_t rd, uint8_t rs) {
    emit_byte(e, 0x8B); emit_byte(e, 0x47); emit_byte(e, REG_OFFSET(rs));
    emit_byte(e, 0x29); emit_byte(e, 0x47); emit_byte(e, REG_OFFSET(rd));
    emit_byte(e, 0x0F); emit_byte(e, 0x94); emit_byte(e, 0xC0); // sete al
    emit_byte(e, 0x0F); emit_byte(e, 0xB6); emit_byte(e, 0xC0); // movzx eax, al
    emit_byte(e, 0x89); emit_byte(e, 0x47); emit_byte(e, ZF_OFFSET);
}

// Порівняння: cmp [rdi + rd], imm32
static void emit_cmp_imm(CodeEmitter* e, uint8_t rd, uint32_t imm) {
    emit_byte(e, 0x81); emit_byte(e, 0x7F); emit_byte(e, REG_OFFSET(rd));
    emit_u32(e, imm);
    emit_byte(e, 0x0F); emit_byte(e, 0x94); emit_byte(e, 0xC0); // sete al
    emit_byte(e, 0x0F); emit_byte(e, 0xB6); emit_byte(e, 0xC0); // movzx eax, al
    emit_byte(e, 0x89); emit_byte(e, 0x47); emit_byte(e, ZF_OFFSET);
}

// Завершення: mov byte ptr [rdi + HALT_OFFSET], 1; ret
static void emit_halt(CodeEmitter* e) {
    emit_byte(e, 0xC6); emit_byte(e, 0x47); emit_byte(e, HALT_OFFSET); emit_byte(e, 0x01);
    emit_byte(e, 0xC3); // ret
}
