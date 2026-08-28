/* Ідіоматичний C++ варіант з типізованими бітовими масками */
namespace driver {

enum class StatusFlag : uint8_t {
    DataReady     = (1 << 0),
    FifoWatermark = (1 << 1),
    FifoOverrun   = (1 << 2)
};

void clear_status_flag(BusInterface& bus, uint8_t dev_addr, StatusFlag flag) noexcept {
    const auto ack_byte = static_cast<uint8_t>(flag);
    bus.write_register(dev_addr, Reg::Status, std::span<const uint8_t, 1>{&ack_byte, 1});
}

} // namespace driver
