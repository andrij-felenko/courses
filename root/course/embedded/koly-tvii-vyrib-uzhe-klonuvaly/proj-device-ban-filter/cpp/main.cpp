#include <array>
#include <span>
#include <optional>
#include <cstdint>
#include <cstring>

constexpr std::size_t ChallengeNonceSize = 32;
constexpr std::size_t EcdsaSignatureSize = 64;
constexpr std::size_t DeviceSerialSize = 16;

struct DeviceAuthPayload {
    std::array<std::uint8_t, DeviceSerialSize> serial{};
    std::array<std::uint8_t, EcdsaSignatureSize> signature{};
};

class ISecureElementDriver {
public:
    virtual ~ISecureElementDriver() = default;
    [[nodiscard]] virtual bool readSerial(std::span<std::uint8_t, DeviceSerialSize> outSerial) const noexcept = 0;
    [[nodiscard]] virtual bool signChallenge(std::span<const std::uint8_t, ChallengeNonceSize> nonce,
                                             std::span<std::uint8_t, EcdsaSignatureSize> outSignature) const noexcept = 0;
};

class AttestationClient {
public:
    explicit AttestationClient(const ISecureElementDriver& driver) noexcept
        : driver_(driver) {}

    [[nodiscard]] std::optional<DeviceAuthPayload> generateResponse(
        std::span<const std::uint8_t, ChallengeNonceSize> nonce) const noexcept {
        DeviceAuthPayload payload{};

        if (!driver_.readSerial(payload.serial)) {
            return std::nullopt;
        }

        if (!driver_.signChallenge(nonce, payload.signature)) {
            return std::nullopt;
        }

        return payload;
    }

private:
    const ISecureElementDriver& driver_;
};
