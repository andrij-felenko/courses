#include <cstdint>

enum class DriverStatus : uint8_t {
    Ok = 0,
    InvalidParam,
    NackAddress,
    NackData,
    CrcMismatch,
    BusTimeout,
    BusStuck,
    WrongDeviceId
};

enum class ErrorAction : uint8_t {
    None = 0,
    RetryImmediate,
    RetryWithBackoff,
    BusRecover,
    CircuitBreakerHit
};

[[nodiscard]] constexpr ErrorAction classify_error(DriverStatus status) noexcept {
    switch (status) {
        case DriverStatus::Ok:
            return ErrorAction::None;

        case DriverStatus::CrcMismatch:
        case DriverStatus::NackData:
        case DriverStatus::NackAddress:
        case DriverStatus::BusTimeout:
            return ErrorAction::RetryWithBackoff;

        case DriverStatus::BusStuck:
            return ErrorAction::BusRecover;

        case DriverStatus::InvalidParam:
        case DriverStatus::WrongDeviceId:
        default:
            return ErrorAction::CircuitBreakerHit;
    }
}
