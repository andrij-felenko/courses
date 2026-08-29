#pragma once

#include <chrono>
#include <cstdint>
#include <functional>
#include <span>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

// Офіційні згенеровані заголовки MAVLink v2, діалект common.
#include <mavlink/v2.0/common/mavlink.h>

// Стани первинного рукостискання станції з апаратом.
enum class HandshakeState {
    Disconnected,   // порт закрито, ресурсів немає
    WaitHeartbeat,  // слухаємо ефір, нічого не питаємо
    ParamSync,      // вивантаження таблиці параметрів
    StreamConfig,   // узгодження частот телеметрії
    MissionSync,    // транзакційна вичитка польотного плану
    Operational,    // усе зібрано, працює сторожовий таймер лінка
    Failed          // рукостискання не склалося
};

const char* stateName(HandshakeState state) noexcept;

struct VehicleIdentity {
    std::uint8_t sysid{0};
    std::uint8_t compid{0};
    std::uint8_t type{0};
    std::uint8_t autopilot{0};
    std::uint32_t custom_mode{0};
    bool armed{false};
};

struct MissionItem {
    std::uint16_t seq{0};
    std::uint16_t command{0};
    std::int32_t lat_e7{0};   // градуси × 1e7, як їх передає MISSION_ITEM_INT
    std::int32_t lon_e7{0};
    float alt_m{0.0f};
};

// Те, що комунікаційний потік віддає потоку інтерфейсу. Готові структури їдуть
// копією всередині події: після push у чергу автомат уже нікому не належить.
struct EngineEvent {
    enum class Kind {
        Log,           // рядок у журнал станції
        StateChanged,  // автомат перейшов у новий стан
        VehicleFound,  // упізнано апарат (перше серцебиття)
        ParamsReady,   // таблиця параметрів зібрана повністю
        MissionReady   // польотний план вичитано й підтверджено
    };

    Kind kind{Kind::Log};
    HandshakeState state{HandshakeState::Disconnected};
    std::string text;
    VehicleIdentity vehicle{};
    std::unordered_map<std::string, float> params;
    std::vector<MissionItem> mission;
};

// Кінцевий автомат рукостискання. Про транспорт не знає нічого: єдиний вихід
// назовні — віртуальний sendPacket(), тож той самий код працює й через UART,
// і через UDP, і через канал симулятора.
class GcsHandshakeEngine {
public:
    using Clock = std::chrono::steady_clock;  // монотонний: NTP не зсуне таймаути

    explicit GcsHandshakeEngine(std::uint8_t gcs_sysid = 255, std::uint8_t gcs_compid = 190);
    virtual ~GcsHandshakeEngine() = default;

    GcsHandshakeEngine(const GcsHandshakeEngine&) = delete;
    GcsHandshakeEngine& operator=(const GcsHandshakeEngine&) = delete;

    void setEventSink(std::function<void(EngineEvent)> sink);

    void start();                                          // Disconnected → WaitHeartbeat
    void onMavlinkMessage(const mavlink_message_t& msg);   // розібраний кадр із парсера
    void tick();                                           // таймерний тік, кожні 10–20 мс

    [[nodiscard]] HandshakeState state() const noexcept { return m_state; }
    [[nodiscard]] const VehicleIdentity& vehicle() const noexcept { return m_vehicle; }
    [[nodiscard]] const std::unordered_map<std::string, float>& params() const noexcept { return m_params; }
    [[nodiscard]] const std::vector<MissionItem>& mission() const noexcept { return m_mission; }

protected:
    // Готовий кадр у фізичний канал. Реалізує нащадок під конкретний транспорт.
    virtual void sendPacket(std::span<const std::uint8_t> frame) = 0;

private:
    void emit(EngineEvent event);
    void log(std::string text);
    void enterState(HandshakeState next);
    void fail(std::string reason);
    void dropLink(std::string reason);
    void resetSession();
    void send(const mavlink_message_t& msg);
    void sendGcsHeartbeat();

    void handleHeartbeat(const mavlink_message_t& msg);
    void handleParamValue(const mavlink_message_t& msg);
    void handleCommandAck(const mavlink_message_t& msg);
    void handleMissionCount(const mavlink_message_t& msg);
    void handleMissionItem(const mavlink_message_t& msg);

    void pollWaitHeartbeat(Clock::time_point now);
    void pollParamSync(Clock::time_point now);
    void pollStreamConfig(Clock::time_point now);
    void pollMissionSync(Clock::time_point now);

    void startParamSync();
    void sendParamRequestList();
    void requestMissingParams(Clock::time_point now);

    void startStreamConfig();
    void sendStreamRequest();

    void startMissionSync();
    void sendMissionRequestList();
    void requestMissionItem();
    void finishMissionSync();

    std::uint8_t m_gcs_sysid;
    std::uint8_t m_gcs_compid;

    HandshakeState m_state{HandshakeState::Disconnected};
    VehicleIdentity m_vehicle{};
    bool m_seen_vehicle{false};

    Clock::time_point m_state_since{};
    Clock::time_point m_last_rx{};        // будь-який кадр від апарата
    Clock::time_point m_last_req{};       // наш останній запит у поточному стані
    Clock::time_point m_last_gcs_hb{};
    Clock::time_point m_last_wait_log{};

    std::uint16_t m_param_total{0};
    std::size_t m_param_have{0};
    std::size_t m_param_cursor{0};        // по колу, щоб не довбати одну й ту саму дірку
    int m_param_rounds{0};
    int m_list_retries{0};
    Clock::time_point m_last_param_rx{};
    std::vector<bool> m_param_mask;
    std::unordered_map<std::string, float> m_params;

    std::vector<std::pair<std::uint16_t, std::uint32_t>> m_streams;
    std::size_t m_stream_idx{0};

    std::uint16_t m_mission_total{0};
    std::uint16_t m_mission_seq{0};
    bool m_mission_counted{false};
    std::vector<MissionItem> m_mission;

    int m_retry{0};
    std::function<void(EngineEvent)> m_sink;
};
