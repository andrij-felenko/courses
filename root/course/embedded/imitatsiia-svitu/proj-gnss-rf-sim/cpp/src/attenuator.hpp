// attenuator.hpp — кроковий РЧ-атенюатор за SCPI через RS-232.
// Керування асинхронне: постановка команди не блокує потік вибірок.
#pragma once

#include <cstdint>
#include <expected>
#include <span>
#include <string>
#include <string_view>

namespace gnss {

inline constexpr double kMaxAttenuationDb = 95.0;
inline constexpr double kAttenuationStepDb = 0.25;

// Дескриптор порту живе рівно стільки, скільки об'єкт: жодного close() руками.
class SerialPort {
public:
    static std::expected<SerialPort, std::string> open(std::string_view device);

    SerialPort(const SerialPort&) = delete;
    SerialPort& operator=(const SerialPort&) = delete;
    SerialPort(SerialPort&& other) noexcept;
    SerialPort& operator=(SerialPort&& other) noexcept;
    ~SerialPort();

    // Неблокуючі: 0 означає «зараз не можна», помилка — реальний збій.
    [[nodiscard]] std::expected<std::size_t, std::string> write_some(std::span<const char> data) noexcept;
    [[nodiscard]] std::expected<std::size_t, std::string> read_some(std::span<char> buffer) noexcept;

    void flush_input() noexcept;

private:
    explicit SerialPort(int fd) noexcept : fd_{fd} {}
    int fd_{-1};
};

class Attenuator {
public:
    enum class State { Idle, Sending, WaitingAck, Failed };

    static std::expected<Attenuator, std::string> connect(std::string_view device);

    Attenuator(const Attenuator&) = delete;
    Attenuator& operator=(const Attenuator&) = delete;
    Attenuator(Attenuator&&) noexcept = default;
    Attenuator& operator=(Attenuator&&) noexcept = default;
    ~Attenuator();

    // Ставить нове загасання в роботу; помилка — автомат зайнятий або зламався.
    std::expected<void, std::string> request(double db);

    // Рухає автомат уперед. Викликається щокроку циклу й ніколи не блокує.
    void poll();

    [[nodiscard]] bool   busy()       const noexcept { return state_ != State::Idle; }
    [[nodiscard]] bool   failed()     const noexcept { return state_ == State::Failed; }
    [[nodiscard]] double current_db() const noexcept { return current_db_; }
    [[nodiscard]] std::uint64_t commands() const noexcept { return commands_; }
    [[nodiscard]] std::uint64_t timeouts() const noexcept { return timeouts_; }

private:
    explicit Attenuator(SerialPort port) noexcept : port_{std::move(port)} {}
    void restart_command();

    SerialPort  port_;
    State       state_{State::Idle};
    std::string tx_;
    std::size_t tx_sent_{};
    std::string rx_;
    double      pending_db_{}, current_db_{kMaxAttenuationDb};
    int         retries_{};
    double      deadline_ms_{};
    std::uint64_t commands_{}, timeouts_{};
};

}  // namespace gnss
