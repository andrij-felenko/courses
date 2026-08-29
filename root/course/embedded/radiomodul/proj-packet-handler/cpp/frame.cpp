#include "frame.hpp"

#include "crc16.hpp"
#include "whitening.hpp"

namespace radio {

std::string_view describe(BuildError error) noexcept
{
    switch (error) {
    case BuildError::EmptyPayload:
        return "порожній payload";
    case BuildError::PayloadTooLong:
        return "payload довший за 64 байти";
    }
    return "невідома помилка";
}

std::expected<std::vector<std::uint8_t>, BuildError>
buildFrame(std::span<const std::uint8_t> payload)
{
    if (payload.empty()) {
        return std::unexpected(BuildError::EmptyPayload);
    }
    if (payload.size() > kMaxPayload) {
        return std::unexpected(BuildError::PayloadTooLong);
    }

    std::vector<std::uint8_t> frame;
    frame.reserve(kPreambleBytes + 2 + 1 + payload.size() + 2);

    // 1. Преамбула. Її не скремблюють: приймач саме за нею ловить фазу біта,
    //    тож вона мусить лишитися рівним чергуванням 0 і 1.
    frame.insert(frame.end(), kPreambleBytes, kPreambleByte);

    // 2. Синхрослово, старший байт першим: корелятор шукає точний візерунок.
    frame.push_back(static_cast<std::uint8_t>(kSyncWord >> 8));
    frame.push_back(static_cast<std::uint8_t>(kSyncWord & 0xFF));

    // 3. Тіло кадру: байт довжини й корисні дані.
    const std::size_t bodyStart = frame.size();
    frame.push_back(static_cast<std::uint8_t>(payload.size()));
    frame.insert(frame.end(), payload.begin(), payload.end());

    // 4. CRC — по чистому тілу, ДО накладання маски: так рахує апаратний блок
    //    трансивера, і рівно так само його перевірить приймач.
    const std::uint16_t crc =
        crc16(std::span<const std::uint8_t>(frame).subspan(bodyStart));
    frame.push_back(static_cast<std::uint8_t>(crc >> 8));
    frame.push_back(static_cast<std::uint8_t>(crc & 0xFF));

    // 5. Тіло разом із контрольною сумою відбілюємо одним потоком LFSR —
    //    інакше довгий хвіст нулів лишив би передавач на одній частоті.
    Whitener whitener;
    whitener.apply(std::span<std::uint8_t>(frame).subspan(bodyStart));

    return frame;
}

} // namespace radio
