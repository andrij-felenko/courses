#pragma once
// Фаза 2: повна вичитка параметрів автопілота із закриттям дірок,
// що їх лишили втрачені в ефірі кадри PARAM_VALUE.
#include <map>
#include <string>
#include <vector>

#include "serial_link.h"

class ParamSync {
public:
    ParamSync(SerialLink& link, std::uint8_t gcs_sysid, std::uint8_t gcs_compid);

    void start(std::uint8_t tsys, std::uint8_t tcomp, Clock::time_point now);
    void onMessage(const mavlink_message_t& msg, Clock::time_point now);
    void tick(Clock::time_point now);

    bool done() const { return state_ == State::Done; }
    bool failed() const { return state_ == State::Failed; }
    // Пауза між пачками дозапитів: росте, коли лінк починає сипатись.
    void setPacing(std::chrono::milliseconds gap) { pacing_ = gap; }
    const std::map<std::string, float>& values() const { return values_; }

private:
    enum class State { Idle, WaitList, Recovering, Done, Failed };

    void sendRequestList(Clock::time_point now);
    void requestMissing(Clock::time_point now);
    void finish();
    void checkCache();

    static constexpr auto kSilence = std::chrono::milliseconds(800);
    static constexpr auto kListTimeout = std::chrono::milliseconds(3000);
    static constexpr std::size_t kBatch = 4;  // не більше чотирьох дозапитів за пачку
    static constexpr int kMaxRounds = 20;

    SerialLink& link_;
    std::uint8_t gcs_sysid_, gcs_compid_;
    std::uint8_t tsys_ = 0, tcomp_ = 0;

    State state_ = State::Idle;
    std::uint16_t count_ = 0;          // param_count, оголошений автопілотом
    std::size_t received_ = 0;         // одиниць у бітовій масці
    std::vector<bool> got_;            // бітова маска прийнятих індексів
    std::map<std::string, float> values_;
    std::size_t cursor_ = 0;           // звідки шукати наступну дірку
    int rounds_ = 0;
    int list_attempts_ = 0;
    Clock::time_point last_rx_{}, last_tx_{};
    std::chrono::milliseconds pacing_{100};
};
