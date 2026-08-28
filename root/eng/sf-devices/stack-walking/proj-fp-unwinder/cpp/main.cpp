#include <array>
#include <span>
#include <string_view>
#include <cstdint>
#include <cstddef>
#include <unistd.h>
#include <sys/syscall.h>

namespace diagnostic {

struct alignas(sizeof(void*)) StackFrame {
    const StackFrame* saved_fp{nullptr};
    const void* return_address{nullptr};
};

class AsyncSignalSafePrinter {
public:
    static void write_literal(std::string_view msg) noexcept {
        (void)::syscall(SYS_write, STDERR_FILENO, msg.data(), msg.size());
    }

    static void write_address(std::uintptr_t addr) noexcept {
        constexpr std::string_view hex_chars = "0123456789abcdef";
        std::array<char, 20> buf{"0x0000000000000000\n"};

        for (int i = 15; i >= 0; --i) {
            buf[2 + (15 - i)] = hex_chars[(addr >> (i * 4)) & 0x0f];
        }
        (void)::syscall(SYS_write, STDERR_FILENO, buf.data(), buf.size());
    }
};

class StackWalker {
public:
    static constexpr std::size_t DefaultMaxDepth = 64;

    template <std::size_t Capacity>
    static std::size_t walk(std::span<const void*, Capacity> destination) noexcept {
        auto current_fp = reinterpret_cast<std::uintptr_t>(__builtin_frame_address(0));
        std::size_t collected = 0;
        const auto stack_limit = current_fp + (8 * 1024 * 1024);

        while (current_fp != 0 && collected < destination.size()) {
            if ((current_fp & (sizeof(void*) - 1)) != 0) {
                break;
            }

            const auto* frame = reinterpret_cast<const StackFrame*>(current_fp);
            destination[collected++] = frame->return_address;

            const auto next_fp = reinterpret_cast<std::uintptr_t>(frame->saved_fp);
            if (next_fp <= current_fp || next_fp >= stack_limit) {
                break;
            }

            current_fp = next_fp;
        }

        return collected;
    }

    static void dump_to_stderr(std::span<const void*> trace) noexcept {
        AsyncSignalSafePrinter::write_literal("=== C++ Stack Backtrace ===\n");
        for (const auto* addr : trace) {
            AsyncSignalSafePrinter::write_literal("  [frame] ");
            AsyncSignalSafePrinter::write_address(reinterpret_cast<std::uintptr_t>(addr));
        }
    }
};

} // namespace diagnostic
