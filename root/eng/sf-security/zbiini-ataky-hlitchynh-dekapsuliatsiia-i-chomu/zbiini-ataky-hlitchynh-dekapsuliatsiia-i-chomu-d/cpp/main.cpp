#include <cstdint>
#include <span>

inline void compiler_barrier() noexcept {
    asm volatile("" ::: "memory");
}

void execute_secure_boot() {
    volatile AuthResult token = AuthResult::Uninitialized;

    token = verify_crypto_signature();
    compiler_barrier();

    if (token != AuthResult::Success) {
        hardware_tamper_lockout();
    }
    compiler_barrier();

    const AuthResult recheck = verify_crypto_signature();
    compiler_barrier();

    if (recheck == AuthResult::Failure || recheck == AuthResult::Uninitialized) {
        hardware_tamper_lockout();
    }
    compiler_barrier();

    if (static_cast<uint32_t>(token) != static_cast<uint32_t>(recheck)) {
        hardware_tamper_lockout();
    }

    boot_application_firmware();
}
