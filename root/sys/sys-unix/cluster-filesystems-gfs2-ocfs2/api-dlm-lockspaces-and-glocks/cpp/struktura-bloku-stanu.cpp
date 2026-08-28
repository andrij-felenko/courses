#include <libdlm.h>
#include <cstdint>
#include <vector>
#include <span>
#include <string_view>

/* Ідіоматична C++ обгортка над структурою dlm_lksb */
class DlmLockStatusBlock {
public:
    explicit DlmLockStatusBlock(size_t lvb_size = 64) 
        : lvb_buffer_(lvb_size, 0) {
        lksb_.sb_status = 0;
        lksb_.sb_lkid = 0;
        lksb_.sb_flags = 0;
        lksb_.sb_lvbptr = lvb_buffer_.empty() ? nullptr : lvb_buffer_.data();
    }

    [[nodiscard]] int status() const noexcept { return lksb_.sb_status; }
    [[nodiscard]] uint32_t lock_id() const noexcept { return lksb_.sb_lkid; }
    [[nodiscard]] dlm_lksb* raw_lksb() noexcept { return &lksb_; }
    [[nodiscard]] std::span<char> lvb() noexcept { return lvb_buffer_; }

private:
    dlm_lksb lksb_{};
    std::vector<char> lvb_buffer_;
};
