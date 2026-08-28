// Прикладний виклик підтвердження прошивки на C++20
#include <expected>

namespace bootloader {

class ApplicationOtaClient {
public:
    explicit ApplicationOtaClient(MetadataManager& mgr, IFlashDriver& flash) noexcept
        : m_mgr(mgr), m_flash(flash) {}

    [[nodiscard]] std::expected<void, FlashError> confirmRunningImage() noexcept {
        BootRecord rec0{}, rec1{};
        m_flash.read(MetadataManager::Sector0Addr, {reinterpret_cast<uint8_t*>(&rec0), sizeof(BootRecord)});
        m_flash.read(MetadataManager::Sector1Addr, {reinterpret_cast<uint8_t*>(&rec1), sizeof(BootRecord)});

        const bool valid0 = m_mgr.isValid(rec0);
        const bool valid1 = m_mgr.isValid(rec1);

        BootRecord current{};
        if (valid0 && valid1) {
            current = (rec0.sequence >= rec1.sequence) ? rec0 : rec1;
        } else if (valid0) {
            current = rec0;
        } else if (valid1) {
            current = rec1;
        } else {
            return std::unexpected(FlashError::CorruptedRecord);
        }

        if (current.status == SlotStatus::PendingTest) {
            current.status = SlotStatus::ConfirmedOk;
            current.retriesLeft = 0;
            return m_mgr.writeRecord(current);
        }

        return {};
    }

private:
    MetadataManager& m_mgr;
    IFlashDriver&    m_flash;
};

} // namespace bootloader
