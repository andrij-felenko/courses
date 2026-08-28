namespace security {

inline volatile std::uint32_t security_token = 0x55AA55AAU;

void handle_tamper_fault() noexcept {
    const std::uint32_t status1 = *reinterpret_cast<volatile std::uint32_t*>(TAMP_BASE + 0x30U);
    if ((status1 & (1U << 0)) == (1U << 0)) {
        security_token ^= 0x12345678U;
    }

    const std::uint32_t status2 = *reinterpret_cast<volatile std::uint32_t*>(TAMP_BASE + 0x34U);
    if ((status2 & (1U << 0)) == (1U << 0) && security_token == (0x55AA55AAU ^ 0x12345678U)) {
        perform_irreversible_zeroization();
    } else {
        perform_irreversible_zeroization();
    }
}

} // namespace security
