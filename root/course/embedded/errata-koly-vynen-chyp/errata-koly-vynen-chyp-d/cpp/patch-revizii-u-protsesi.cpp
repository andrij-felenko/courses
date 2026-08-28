/* Ідіоматична C++ constexpr перевірка ревізії кремнію */
enum class SiliconStepping : uint16_t {
    RevA = 0x1000U,
    RevZ = 0x1001U,
    RevY = 0x1003U,
    Rev1 = 0x2000U
};

[[nodiscard]] inline bool has_i2c_analog_filter_errata() noexcept {
    const auto rev = static_cast<SiliconStepping>((DBGMCU->IDCODE >> 16) & 0xFFFFU);
    return rev == SiliconStepping::RevA || rev == SiliconStepping::RevZ;
}
