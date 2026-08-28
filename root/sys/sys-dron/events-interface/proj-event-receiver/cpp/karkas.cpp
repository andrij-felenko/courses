#include <common/mavlink.h>

#include <cstdint>
#include <cstdio>
#include <functional>
#include <utility>

#define RX_TRACE(...) printf(__VA_ARGS__)      // слід виконання; у бібліотеці — порожній

class EventReceiver
{
public:
    struct Callbacks {
        std::function<void(const mavlink_request_event_t &)> send_request;
        std::function<void(int timeout_ms)>                  timer;    // <0 — вимкнути
        std::function<void(const mavlink_event_t &)>         deliver;
        std::function<void(int num_lost)>                    lost;
    };

    struct Stats { unsigned requests, duplicates, lost_total, reboots; };

    EventReceiver(Callbacks cb, uint8_t our_sysid, uint8_t our_compid,
                  uint8_t sysid, uint8_t compid)
        : _cb(std::move(cb)),
          _our_sysid(our_sysid), _our_compid(our_compid),
          _sysid(sysid), _compid(compid) {}

    void processMessage(const mavlink_message_t &msg)
    {
        if (msg.sysid != _sysid || msg.compid != _compid) {
            return;                     // цей примірник обслуговує один компонент
        }
        switch (msg.msgid) {
        case MAVLINK_MSG_ID_EVENT:                  onEvent(msg);   break;
        case MAVLINK_MSG_ID_CURRENT_EVENT_SEQUENCE: onCurrent(msg); break;
        case MAVLINK_MSG_ID_RESPONSE_EVENT_ERROR:   onError(msg);   break;
        default: break;
        }
    }

    Stats stats() const { return { _requests, _duplicates, _lost_total, _reboots }; }

    /* onTimeout() — тут же, у тілі класу; його показано разом із request()  */

private:
    /* Cmp і compare() — з попереднього блоку; onEvent, onCurrent, onError,
       request, checkReboot — теж члени цього ж класу                       */

    const Callbacks _cb;
    unsigned _requests{0}, _duplicates{0}, _lost_total{0}, _reboots{0};
    /* решта стану — нижче */
};
