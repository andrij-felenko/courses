// service_engine.hpp — скінченний автомат сервісної консолі.
// Купи немає: увесь стан лежить в об'єкті, буфери — std::array.
#pragma once

#include <array>
#include <atomic>
#include <cstdint>
#include <expected>
#include <format>
#include <optional>
#include <string_view>
#include <utility>

#include "hw_port.hpp"

class ServiceEngine {
public:
    enum class State : std::uint8_t {
        Locked,
        ChallengeIssued,
        Unlocked,
        ActuationActive,
        Emergency,
    };

    enum class Error : std::uint16_t {
        Locked            = 0x4000,
        AccessDenied      = 0x4001,
        InvalidChannel    = 0x4002,
        TimeoutOutOfRange = 0x4003,
        AuthFailed        = 0x4004,
        BadArguments      = 0x4005,
        UnknownCommand    = 0x4006,
        ActuationBusy     = 0x4007,
        LineTooLong       = 0x4008,
        HardwareFault     = 0x4009,
        EepromWriteFailed = 0x400A,
        BusBusy           = 0x400B,
        InputOverrun      = 0x400C,
    };

    static constexpr std::size_t BufferSize = 128;
    static constexpr std::size_t CalSlots   = 4;

    ServiceEngine() noexcept = default;
    ServiceEngine(const ServiceEngine&)            = delete;
    ServiceEngine& operator=(const ServiceEngine&) = delete;

    // Конструктор навмисно не чіпає заліза: глобальний об'єкт будується
    // до main(), коли тактування й GPIO ще не підняті. Усе апаратне — тут.
    void begin() noexcept;

    void feedByte(char c) noexcept; // контекст ISR приймача UART
    void poll() noexcept;           // контекст сервісної задачі

    void emergencyAllOff() noexcept;
    void faultTrip(hw::Fault flags) noexcept; // контекст ISR захисту

    State        state() const noexcept { return state_; }
    std::int32_t calibration(std::size_t slot) const noexcept
    {
        return slot < CalSlots ? cal_[slot] : 0;
    }

private:
    using Result = std::expected<void, Error>;

    // Реле ввімкнене рівно доти, доки живий цей об'єкт. Іншого способу
    // подати напругу в класі немає, тож «забув вимкнути» не трапляється:
    // будь-який вихід — reset(), перезапис, аварія — гасить канал.
    class Actuation {
    public:
        Actuation(std::uint8_t channel, hw::Millis deadline) noexcept;
        ~Actuation();
        Actuation(Actuation&& other) noexcept;
        Actuation& operator=(Actuation&&)      = delete;
        Actuation(const Actuation&)            = delete;
        Actuation& operator=(const Actuation&) = delete;

        std::uint8_t channel() const noexcept { return channel_; }
        hw::Millis   deadline() const noexcept { return deadline_; }

    private:
        std::uint8_t channel_;
        hw::Millis   deadline_;
    };

    struct Command {
        std::string_view name;
        Result (ServiceEngine::*handler)(std::string_view args);
        bool needsSession;      // потрібна відкрита сесія
        bool duringActuation;   // дозволена, поки навантаження під напругою
        bool duringEmergency;   // дозволена після аварійної зупинки
    };

    static const std::array<Command, 10> kCommands;

    Result dispatch(std::string_view line) noexcept;
    Result cmdSysInfo(std::string_view args);
    Result cmdAuthChallenge(std::string_view args);
    Result cmdAuthKey(std::string_view args);
    Result cmdLock(std::string_view args);
    Result cmdActuateOff(std::string_view args);
    Result cmdActuateRelay(std::string_view args);
    Result cmdSelfTest(std::string_view args);
    Result cmdAdc(std::string_view args);
    Result cmdCalGet(std::string_view args);
    Result cmdCalSet(std::string_view args);

    void report(Result result) noexcept;
    void enterLocked() noexcept;
    void refreshSession() noexcept;
    void prompt() noexcept;
    void emit(std::string_view text) noexcept;

    // Форматування без купи: std::format_to_n пише в буфер на стеку.
    template <class... Args>
    void emitf(std::format_string<Args...> fmt, Args&&... args) noexcept
    {
        std::array<char, 160> buf{};
        auto result = std::format_to_n(buf.data(), buf.size(), fmt, std::forward<Args>(args)...);
        emit(std::string_view(buf.data(), static_cast<std::size_t>(result.out - buf.data())));
    }

    static constexpr auto ChallengeTimeout = std::chrono::seconds(30);
    static constexpr auto SessionTimeout   = std::chrono::minutes(15);
    static constexpr auto MaxActuation     = std::chrono::seconds(15);
    static constexpr std::uint8_t  MaxErrors     = 8;
    static constexpr std::uint16_t CalEepromBase = 0x0040;

    State         state_{State::Locked};
    hw::Millis    stateDeadline_{};
    std::optional<Actuation> actuation_{};
    std::uint32_t nonce_{0};
    hw::Fault     faults_{hw::Fault::None};
    bool          emergencyAnnounced_{false};
    std::uint8_t  errorCount_{0};
    std::array<std::int32_t, CalSlots> cal_{};

    // rx_ заповнює ISR, line_ читає задача. Передача прапорцем через
    // std::atomic з release/acquire — а не volatile, як у C.
    std::array<char, BufferSize> rx_{};
    std::size_t                  rxIdx_{0};
    bool                         rxOverflow_{false};
    std::array<char, BufferSize> line_{};
    std::size_t                  lineLen_{0};
    bool                         lineOverflow_{false};
    std::atomic<bool>            lineReady_{false};
    std::atomic<bool>            lineLost_{false};
};
