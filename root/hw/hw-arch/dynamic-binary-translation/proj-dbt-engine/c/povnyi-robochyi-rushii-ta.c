#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_GUEST_CODE 64
#define MAX_BLOCKS     64

typedef void (*JitFunction)(GuestContext* ctx);

typedef struct {
    uint8_t op;
    uint8_t rd;
    uint8_t rs;
    uint8_t imm8;
    uint16_t imm16;
} GuestInsn;

typedef struct {
    GuestInsn        program[MAX_GUEST_CODE];
    size_t           program_size;
    ExecutableBuffer* exec_mem;
    TranslationBlock blocks[MAX_BLOCKS];
    size_t           block_count;
} DbtEngine;

static TranslationBlock* find_block(DbtEngine* dbt, uint32_t gpc) {
    for (size_t i = 0; i < dbt->block_count; ++i) {
        if (dbt->blocks[i].guest_pc == gpc) return &dbt->blocks[i];
    }
    return NULL;
}

static TranslationBlock* compile_block(DbtEngine* dbt, uint32_t start_pc) {
    uint8_t* code_mem = exec_buffer_alloc_block(dbt->exec_mem, 256);
    if (!code_mem) return NULL;

    CodeEmitter e = { code_mem, 0 };
    TranslationBlock* tb = &dbt->blocks[dbt->block_count++];
    tb->guest_pc = start_pc;
    tb->host_addr = code_mem;
    tb->exit_count = 0;

    uint32_t pc = start_pc;
    bool block_ended = false;

    while (pc < dbt->program_size && !block_ended) {
        GuestInsn insn = dbt->program[pc];
        switch (insn.op) {
            case 0x01: emit_mov_imm(&e, insn.rd, insn.imm16); break;
            case 0x02: emit_add(&e, insn.rd, insn.rs); break;
            case 0x03: emit_sub(&e, insn.rd, insn.rs); break;
            case 0x04: emit_cmp_imm(&e, insn.rd, insn.imm16); break;
            case 0x05: { // JMP target
                uint32_t target = insn.imm16;
                emit_byte(&e, 0xE9); // jmp rel32
                uint8_t* patch_site = e.code + e.size;
                emit_u32(&e, 0);

                // Трамплін безумовного переходу:
                uint8_t* tramp_addr = e.code + e.size;
                int32_t tramp_offset = (int32_t)(tramp_addr - (patch_site + 4));
                memcpy(patch_site, &tramp_offset, sizeof(int32_t));

                emit_byte(&e, 0xC7); emit_byte(&e, 0x47); emit_byte(&e, PC_OFFSET); emit_u32(&e, target);
                emit_byte(&e, 0xC3); // ret

                tb->exits[tb->exit_count++] = (JumpPatchInfo){ target, patch_site, false };
                block_ended = true;
                break;
            }
            case 0x06: { // JZ target
                uint32_t target_taken = insn.imm16;
                uint32_t target_fall = pc + 1;

                // Перевірка прапорця: cmp dword ptr [rdi + ZF_OFFSET], 1
                emit_byte(&e, 0x83); emit_byte(&e, 0x7F); emit_byte(&e, ZF_OFFSET); emit_byte(&e, 0x01);

                // je trampoline_taken
                emit_byte(&e, 0x0F); emit_byte(&e, 0x84);
                uint8_t* patch_taken = e.code + e.size;
                emit_u32(&e, 0);

                // jmp trampoline_fall
                emit_byte(&e, 0xE9);
                uint8_t* patch_fall = e.code + e.size;
                emit_u32(&e, 0);

                // Трамплін Taken:
                uint8_t* tramp_taken = e.code + e.size;
                int32_t off_taken = (int32_t)(tramp_taken - (patch_taken + 4));
                memcpy(patch_taken, &off_taken, sizeof(int32_t));
                emit_byte(&e, 0xC7); emit_byte(&e, 0x47); emit_byte(&e, PC_OFFSET); emit_u32(&e, target_taken);
                emit_byte(&e, 0xC3);

                // Трамплін Fallthrough:
                uint8_t* tramp_fall = e.code + e.size;
                int32_t off_fall = (int32_t)(tramp_fall - (patch_fall + 4));
                memcpy(patch_fall, &off_fall, sizeof(int32_t));
                emit_byte(&e, 0xC7); emit_byte(&e, 0x47); emit_byte(&e, PC_OFFSET); emit_u32(&e, target_fall);
                emit_byte(&e, 0xC3);

                tb->exits[tb->exit_count++] = (JumpPatchInfo){ target_taken, patch_taken, true };
                tb->exits[tb->exit_count++] = (JumpPatchInfo){ target_fall, patch_fall, false };
                block_ended = true;
                break;
            }
            case 0xFF: // HALT
                emit_halt(&e);
                block_ended = true;
                break;
        }
        pc++;
    }

    tb->host_size = e.size;

    // Зшивання: якщо попередні блоки чекали на цей блок, патчимо їх
    for (size_t i = 0; i < dbt->block_count - 1; ++i) {
        for (size_t k = 0; k < dbt->blocks[i].exit_count; ++k) {
            if (dbt->blocks[i].exits[k].guest_target_pc == start_pc) {
                patch_jump(&dbt->blocks[i].exits[k], tb->host_addr);
            }
        }
    }

    // Зшивання виходів нового блоку, якщо цілі вже є в кеші
    for (size_t k = 0; k < tb->exit_count; ++k) {
        TranslationBlock* target_tb = find_block(dbt, tb->exits[k].guest_target_pc);
        if (target_tb) {
            patch_jump(&tb->exits[k], target_tb->host_addr);
        }
    }

    return tb;
}

void dbt_run(DbtEngine* dbt, GuestContext* ctx) {
    while (!ctx->halted) {
        TranslationBlock* tb = find_block(dbt, ctx->pc);
        if (!tb) {
            tb = compile_block(dbt, ctx->pc);
            if (!tb) {
                fprintf(stderr, "Помилка JIT-компіляції блоку\n");
                break;
            }
        }

        // Прямий виклик згенерованого нативного коду
        JitFunction fn = (JitFunction)tb->host_addr;
        fn(ctx);
    }
}
