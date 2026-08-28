#include <mavlink/common/mavlink.h>

#include <chrono>
#include <cstring>
#include <map>
#include <set>
#include <string>
#include <utility>

using Clock = std::chrono::steady_clock;
using Ms    = std::chrono::milliseconds;

// Куди складаємо готові кадри: у справжній станції це черга каналу.
struct MavlinkOut { void send(const mavlink_message_t& msg); };

constexpr uint8_t kGcsSysId  = 255;                          // звичний номер станції
constexpr uint8_t kGcsCompId = MAV_COMP_ID_MISSIONPLANNER;   // 190

constexpr int kListSilenceMs   = 5000;  // тиша у відповідь на запит списку
constexpr int kStreamSilenceMs = 3000;  // тиша посеред потоку = борт замовк
constexpr int kReadAckMs       = 1000;  // тиша у відповідь на точковий запит
constexpr int kListRetries     = 4;     // повторів запиту всього списку
constexpr int kTriesPerIndex   = 5;     // спроб на ОДИН номер, далі здаємось
constexpr int kBatchSize       = 10;    // точкових запитів у польоті одночасно

struct Param { float value; uint8_t type; };

// Усе, що ведемо на ОДИН компонент: під одним апаратом їх кілька (автопілот,
// підвіс, камера), і в кожного свій param_count і своя незалежна нумерація.
struct Comp {
    bool     seen  = false;               // чи прийшло хоч одне значення
    uint16_t total = 0;                   // param_count із першого повідомлення
    std::map<uint16_t, uint8_t>  waiting; // номер → скільки разів просили
    std::set<uint16_t>           failed;  // номери, на яких здалися
    std::map<std::string, Param> got;     // ім'я → значення
};

using Key = std::pair<uint8_t, uint16_t>;   // компонент + номер

class ParamFetcher {
public:
    ParamFetcher(MavlinkOut& out, uint8_t sysId, uint8_t defaultComp)
        : _out(out), _sysId(sysId), _defaultComp(defaultComp) {}

    void   start(Clock::time_point now) {
        _sendRequestList();
        _listAttempts = 1;
        _awaitingList = true;
        _listDeadline = now + Ms(kListSilenceMs);
    }

    void   onParamValue(uint8_t compId, const mavlink_param_value_t& pv,
                        Clock::time_point now);
    void   tick(Clock::time_point now);
    bool   complete() const;
    double progress() const;

    bool aborted() const { return _giveUp; }    // борт не озвався жодного разу
    // Назовні віддаємо все разом: і зібрані значення, і номери, на яких здалися.
    const std::map<uint8_t, Comp>& components() const { return _comps; }

private:
    void _ask(uint8_t compId, uint16_t idx, Clock::time_point now);
    void _refill(Clock::time_point now);
    void _sendRequestList();
    void _sendRequestRead(uint8_t compId, uint16_t idx);

    MavlinkOut& _out;
    uint8_t     _sysId, _defaultComp;

    std::map<uint8_t, Comp>          _comps;
    std::map<Key, Clock::time_point> _inFlight;  // що в польоті й доки чекаємо

    bool _awaitingList = false;   // чекаємо першої відповіді на запит списку
    bool _batchOn      = false;   // потік вичерпався, працює добір
    bool _giveUp       = false;   // борт не озвався зовсім
    int  _listAttempts = 0;
    Clock::time_point _listDeadline{}, _silenceDeadline{};
};
