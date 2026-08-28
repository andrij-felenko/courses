#include <cstdint>
#include <cstddef>
#include <span>

enum class SyscallId : uint8_t {
    Yield      = 0x01,
    UartWrite  = 0x02,
    TaskExit   = 0xFF
};

extern "C" void SVC_Handler_Cpp(uint32_t *svc_args) noexcept {
    auto svc_id = static_cast<SyscallId>(((reinterpret_cast<const uint8_t*>(svc_args[6]))[-2]));

    if (svc_id == SyscallId::Yield) {
        SCB->ICSR |= SCB_ICSR_PENDSVSET_Msk;
        svc_args[0] = 0;
    } else if (svc_id == SyscallId::UartWrite) {
        auto buf = reinterpret_cast<const uint8_t*>(svc_args[0]);
        auto len = static_cast<std::size_t>(svc_args[1]);

        if (mpu_validate_buffer(buf, len, false)) {
            svc_args[0] = uart_transmit_blocking(buf, len);
        } else {
            svc_args[0] = static_cast<uint32_t>(-13); // -EACCES
        }
    }
}
