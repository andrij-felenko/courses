#include <iostream>
#include <vector>
#include <unordered_map>
#include <functional>

using JitFunction = void (*)(GuestContext*);

struct GuestInsn {
    uint8_t  op{0};
    uint8_t  rd{0};
    uint8_t  rs{0};
    uint16_t imm16{0};
};

class DbtEngine {
public:
    explicit DbtEngine(std::size_t cache_size = 1024 * 1024)
        : exec_mem_(cache_size) {}

    void load_program(std::vector<GuestInsn> prog) {
        program_ = std::move(prog);
        blocks_.clear();
        block_map_.clear();
    }

    void run(GuestContext& ctx) {
        while (!ctx.halted) {
            TranslationBlock* tb = get_or_compile_block(ctx.pc);
            if (!tb) {
                std::cerr << "Compilation failed for PC " << ctx.pc << '\n';
                break;
            }

            auto fn = reinterpret_cast<JitFunction>(tb->host_addr);
            fn(&ctx);
        }
    }

private:
    TranslationBlock* get_or_compile_block(uint32_t gpc) {
        auto it = block_map_.find(gpc);
        if (it != block_map_.end()) {
            return &blocks_[it->second];
        }
        return compile_block(gpc);
    }

    TranslationBlock* compile_block(uint32_t start_pc) {
        uint8_t* code_mem = exec_mem_.allocate_block(256);
        CodeEmitter e(code_mem);

        TranslationBlock tb;
        tb.guest_pc = start_pc;
        tb.host_addr = code_mem;
        tb.exit_count = 0;

        uint32_t pc = start_pc;
        bool block_ended = false;

        while (pc < program_.size() && !block_ended) {
            const auto& insn = program_[pc];
            switch (insn.op) {
                case 0x01: e.emit_mov_imm(insn.rd, insn.imm16); break;
                case 0x02: e.emit_add(insn.rd, insn.rs); break;
                case 0x03: e.emit_sub(insn.rd, insn.rs); break;
                case 0x04: e.emit_cmp_imm(insn.rd, insn.imm16); break;
                case 0x05: { // JMP target
                    const uint32_t target = insn.imm16;
                    e.emit_byte(0xE9); // jmp rel32
                    uint8_t* patch_site = e.buffer() + e.size();
                    e.emit_u32(0);

                    uint8_t* tramp_addr = e.buffer() + e.size();
                    auto tramp_offset = static_cast<int32_t>(tramp_addr - (patch_site + 4));
                    std::memcpy(patch_site, &tramp_offset, sizeof(int32_t));

                    e.emit_byte(0xC7); e.emit_byte(0x47); 
                    e.emit_byte(OffsetHelper::pc()); e.emit_u32(target);
                    e.emit_byte(0xC3); // ret

                    tb.exits[tb.exit_count++] = JumpPatchInfo{ target, patch_site, false };
                    block_ended = true;
                    break;
                }
                case 0x06: { // JZ target
                    const uint32_t target_taken = insn.imm16;
                    const uint32_t target_fall = pc + 1;

                    // cmp [rdi + zf], 1
                    e.emit_byte(0x83); e.emit_byte(0x7F); 
                    e.emit_byte(OffsetHelper::zf()); e.emit_byte(0x01);

                    // je trampoline_taken
                    e.emit_byte(0x0F); e.emit_byte(0x84);
                    uint8_t* patch_taken = e.buffer() + e.size();
                    e.emit_u32(0);

                    // jmp trampoline_fall
                    e.emit_byte(0xE9);
                    uint8_t* patch_fall = e.buffer() + e.size();
                    e.emit_u32(0);

                    // Трамплін Taken:
                    uint8_t* tramp_taken = e.buffer() + e.size();
                    auto off_taken = static_cast<int32_t>(tramp_taken - (patch_taken + 4));
                    std::memcpy(patch_taken, &off_taken, sizeof(int32_t));
                    e.emit_byte(0xC7); e.emit_byte(0x47); 
                    e.emit_byte(OffsetHelper::pc()); e.emit_u32(target_taken);
                    e.emit_byte(0xC3);

                    // Трамплін Fallthrough:
                    uint8_t* tramp_fall = e.buffer() + e.size();
                    auto off_fall = static_cast<int32_t>(tramp_fall - (patch_fall + 4));
                    std::memcpy(patch_fall, &off_fall, sizeof(int32_t));
                    e.emit_byte(0xC7); e.emit_byte(0x47); 
                    e.emit_byte(OffsetHelper::pc()); e.emit_u32(target_fall);
                    e.emit_byte(0xC3);

                    tb.exits[tb.exit_count++] = JumpPatchInfo{ target_taken, patch_taken, true };
                    tb.exits[tb.exit_count++] = JumpPatchInfo{ target_fall, patch_fall, false };
                    block_ended = true;
                    break;
                }
                case 0xFF: // HALT
                    e.emit_halt();
                    block_ended = true;
                    break;
            }
            pc++;
        }

        tb.host_size = e.size();
        const std::size_t new_idx = blocks_.size();
        blocks_.push_back(tb);
        block_map_[start_pc] = new_idx;

        TranslationBlock* current_tb = &blocks_[new_idx];

        // Патчимо попередні блоки, що чекали на цей Guest PC
        for (std::size_t i = 0; i < new_idx; ++i) {
            for (std::size_t k = 0; k < blocks_[i].exit_count; ++k) {
                if (blocks_[i].exits[k].guest_target_pc == start_pc) {
                    blocks_[i].exits[k].apply_patch(current_tb->host_addr);
                }
            }
        }

        // Патчимо виходи щойно створеного блоку, якщо їхні цілі вже скомпільовані
        for (std::size_t k = 0; k < current_tb->exit_count; ++k) {
            auto it = block_map_.find(current_tb->exits[k].guest_target_pc);
            if (it != block_map_.end()) {
                current_tb->exits[k].apply_patch(blocks_[it->second].host_addr);
            }
        }

        return current_tb;
    }

    std::vector<GuestInsn>               program_;
    ExecutableBuffer                     exec_mem_;
    std::vector<TranslationBlock>        blocks_;
    std::unordered_map<uint32_t, size_t> block_map_;
};
