// Інтерпретатор байткоду правил плюралізації CLDR на C++20
[[nodiscard]] constexpr PluralCategory eval_plural_bytecode(std::span<const uint8_t> bytecode, int32_t n) noexcept {
    if (bytecode.empty()) return PluralCategory::Other;
    
    std::array<int32_t, 8> stack{};
    size_t sp = 0;
    int32_t abs_n = n < 0 ? -n : n;
    size_t ip = 0;
    
    while (ip < bytecode.size() && bytecode[ip] != 0x00) {
        uint8_t op = bytecode[ip++];
        switch (op) {
            case 0x01: stack[sp++] = abs_n; break;
            case 0x04: stack[sp++] = bytecode[ip++]; break;
            case 0x05: {
                int32_t b = stack[--sp];
                int32_t a = stack[--sp];
                stack[sp++] = (b != 0) ? (a % b) : 0;
                break;
            }
            case 0x06: {
                int32_t b = stack[--sp];
                int32_t a = stack[--sp];
                stack[sp++] = (a == b) ? 1 : 0;
                break;
            }
            case 0x07: {
                int32_t b = stack[--sp];
                int32_t a = stack[--sp];
                stack[sp++] = (a != b) ? 1 : 0;
                break;
            }
            case 0x08: {
                uint8_t low = bytecode[ip++];
                uint8_t high = bytecode[ip++];
                int32_t val = stack[--sp];
                stack[sp++] = (val >= low && val <= high) ? 1 : 0;
                break;
            }
            case 0x09: {
                int32_t b = stack[--sp];
                int32_t a = stack[--sp];
                stack[sp++] = (a && b) ? 1 : 0;
                break;
            }
            case 0x0B: {
                uint8_t target = bytecode[ip++];
                if (!stack[--sp]) ip = target;
                break;
            }
            case 0x0C: return static_cast<PluralCategory>(bytecode[ip]);
            default: return PluralCategory::Other;
        }
    }
    return PluralCategory::Other;
}
