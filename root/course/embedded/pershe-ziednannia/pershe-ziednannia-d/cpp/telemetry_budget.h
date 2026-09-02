#pragma once
// Фаза 3: бюджет радіоканалу й індивідуальні інтервали потоків телеметрії.
#include <vector>

#include "serial_link.h"

struct StreamSpec {
    const char* name;
    std::uint32_t msgid;
    std::uint8_t legacy_stream;    // MAV_DATA_STREAM для відкату на застарілий #66
    float hz;                      // бажана частота
    std::uint16_t frame_bytes;     // кадр разом із заголовком і CRC
    bool reducible;                // чи можна різати частоту, коли бюджет не сходиться

    double bytesPerSecond() const { return hz * frame_bytes; }
};

class TelemetrySetup {
public:
    // 57600 бод на UART дають в ефірі SiK лише ~3.2–3.8 КБ/с корисних.
    static constexpr double kAirBytesPerSecond = 3500.0;
    static constexpr double kMaxShare = 0.40;  // телеметрії — не більше 40% смуги
    static constexpr auto kAckTimeout = std::chrono::milliseconds(600);
    static constexpr int kMaxAttempts = 3;

    TelemetrySetup(SerialLink& link, std::uint8_t gcs_sysid, std::uint8_t gcs_compid);

    void start(std::uint8_t tsys, std::uint8_t tcomp, bool supports_set_interval,
               Clock::time_point now);
    void onMessage(const mavlink_message_t& msg, Clock::time_point now);
    void tick(Clock::time_point now);
    bool done() const { return state_ == State::Done; }

private:
    enum class State { Idle, Sending, Done };

    void fitToBudget();
    void printBudget() const;
    void sendCurrent(Clock::time_point now);
    void legacyFallback();

    SerialLink& link_;
    std::uint8_t gcs_sysid_, gcs_compid_;
    std::uint8_t tsys_ = 0, tcomp_ = 0;

    State state_ = State::Idle;
    std::vector<StreamSpec> plan_;
    std::size_t index_ = 0;
    int attempts_ = 0;
    Clock::time_point last_tx_{};
};
