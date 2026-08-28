#include <cstdint>
#include <cstddef>
#include <cstring>
#include <array>

#if defined(_WIN32)
#include <windows.h>
#endif

struct JumpPatchInfo {
    uint32_t guest_target_pc{0};
    uint8_t* patch_offset_addr{nullptr};
    bool     is_conditional{false};

    void apply_patch(const uint8_t* target_host_addr) const noexcept {
        const std::size_t insn_len = is_conditional ? 6 : 5;
        uint8_t* insn_start = patch_offset_addr - (insn_len - 4);
        const auto rel_offset = static_cast<int32_t>(
            target_host_addr - (insn_start + insn_len));

        std::memcpy(patch_offset_addr, &rel_offset, sizeof(int32_t));

#if defined(_WIN32)
        FlushInstructionCache(GetCurrentProcess(), insn_start, insn_len);
#elif defined(__GNUC__) || defined(__clang__)
        __builtin___clear_cache(reinterpret_cast<char*>(insn_start), 
                                reinterpret_cast<char*>(insn_start + insn_len));
#endif
    }
};

struct TranslationBlock {
    uint32_t                      guest_pc{0};
    uint8_t*                      host_addr{nullptr};
    std::size_t                   host_size{0};
    std::array<JumpPatchInfo, 2>  exits{};
    std::size_t                   exit_count{0};
};
