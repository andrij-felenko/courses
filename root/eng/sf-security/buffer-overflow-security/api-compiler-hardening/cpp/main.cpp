#include <sys/prctl.h>
#include <iostream>
#include <expected>
#include <system_error>

#ifndef PR_SET_SHADOW_STACK_STATUS
#define PR_SET_SHADOW_STACK_STATUS 75
#define PR_GET_SHADOW_STACK_STATUS 74
#define PR_LOCK_SHADOW_STACK_STATUS 76
#define PR_SHADOW_STACK_ENABLE     (1UL << 0)
#define PR_SHADOW_STACK_WRITE      (1UL << 1)
#endif

enum class ShadowStackError {
    NotSupported,
    LockFailed
};

// Ідіоматична обгортка C++23 з поверненням типізованого результату
std::expected<void, ShadowStackError> configure_shadow_stack() noexcept {
    if (prctl(PR_SET_SHADOW_STACK_STATUS, PR_SHADOW_STACK_ENABLE, 0, 0, 0) != 0) {
        return std::unexpected(ShadowStackError::NotSupported);
    }
    if (prctl(PR_LOCK_SHADOW_STACK_STATUS, PR_SHADOW_STACK_ENABLE, 0, 0, 0) != 0) {
        return std::unexpected(ShadowStackError::LockFailed);
    }
    return {};
}
