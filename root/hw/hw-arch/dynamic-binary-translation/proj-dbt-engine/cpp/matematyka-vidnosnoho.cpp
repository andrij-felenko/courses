#include <cstdint>
#include <cstddef>
#include <vector>
#include <cstring>

struct OffsetHelper {
    static constexpr uint8_t reg(uint8_t idx) noexcept {
        return static_cast<uint8_t>(idx * sizeof(uint32_t));
    }
    static constexpr uint8_t pc() noexcept {
        return static_cast<uint8_t>(offsetof(GuestContext, pc));
    }
    static constexpr uint8_t zf() noexcept {
        return static_cast<uint8_t>(offsetof(GuestContext, zf));
    }
    static constexpr uint8_t halt() noexcept {
        return static_cast<uint8_t>(offsetof(GuestContext, halted));
    }
};

class CodeEmitter {
public:
    explicit CodeEmitter(uint8_t* output_buffer) 
        : buffer_(output_buffer), size_(0) {}

    void emit_byte(uint8_t b) {
        buffer_[size_++] = b;
    }

    void emit_u32(uint32_t val) {
        std::memcpy(buffer_ + size_, &val, sizeof(uint32_t));
        size_ += sizeof(uint32_t);
    }

    void emit_mov_imm(uint8_t reg_idx, uint32_t imm) {
        emit_byte(0xC7); // MOV r/m32, imm32
        emit_byte(0x47); // [rdi + disp8]
        emit_byte(OffsetHelper::reg(reg_idx));
        emit_u32(imm);
    }

    void emit_add(uint8_t rd, uint8_t rs) {
        emit_byte(0x8B); emit_byte(0x47); emit_byte(OffsetHelper::reg(rs)); // mov eax, [rdi + rs]
        emit_byte(0x01); emit_byte(0x47); emit_byte(OffsetHelper::reg(rd)); // add [rdi + rd], eax
        emit_update_zf();
    }

    void emit_sub(uint8_t rd, uint8_t rs) {
        emit_byte(0x8B); emit_byte(0x47); emit_byte(OffsetHelper::reg(rs)); // mov eax, [rdi + rs]
        emit_byte(0x29); emit_byte(0x47); emit_byte(OffsetHelper::reg(rd)); // sub [rdi + rd], eax
        emit_update_zf();
    }

    void emit_cmp_imm(uint8_t rd, uint32_t imm) {
        emit_byte(0x81); emit_byte(0x7F); emit_byte(OffsetHelper::reg(rd)); // cmp [rdi + rd], imm
        emit_u32(imm);
        emit_update_zf();
    }

    void emit_halt() {
        emit_byte(0xC6); emit_byte(0x47); emit_byte(OffsetHelper::halt()); emit_byte(0x01);
        emit_byte(0xC3); // ret
    }

    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] uint8_t* buffer() const noexcept { return buffer_; }

private:
    void emit_update_zf() {
        emit_byte(0x0F); emit_byte(0x94); emit_byte(0xC0); // sete al
        emit_byte(0x0F); emit_byte(0xB6); emit_byte(0xC0); // movzx eax, al
        emit_byte(0x89); emit_byte(0x47); emit_byte(OffsetHelper::zf()); // mov [rdi + zf], eax
    }

    uint8_t*    buffer_;
    std::size_t size_;
};
