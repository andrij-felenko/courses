/* Типобезпечна перевірка ревізії кремнію (C++) */
#include <cstdint>
#include <expected>

namespace driver {

enum class SiliconRev : uint8_t {
    RevA = 0x01,
    RevB = 0x02
};

void apply_workaround_if_needed(BusInterface& bus, uint8_t dev_addr) noexcept {
    uint8_t rev_raw = 0;
    if (bus.read_register(dev_addr, Reg::RevisionId, std::span<uint8_t, 1>{&rev_raw, 1})) {
        if (static_cast<SiliconRev>(rev_raw) == SiliconRev::RevA) {
            apply_errata_workaround_es042();
        }
    }
}

} // namespace driver
