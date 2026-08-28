// actuator_test.cpp — покрутити один вихід і коректно відпустити.
// g++ -std=c++17 -I<тека зі згенерованими заголовками> actuator_test.cpp -o actuator_test
#include <mavlink/common/mavlink.h>

#include <arpa/inet.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <unistd.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <limits>
#include <map>
#include <string>
#include <thread>
#include <vector>

static constexpr uint8_t GCS_SYSID  = 255;                        // не збігатися з бортом!
static constexpr uint8_t GCS_COMPID = MAV_COMP_ID_MISSIONPLANNER;

static int64_t nowMs()
{
    using namespace std::chrono;
    return duration_cast<milliseconds>(steady_clock::now().time_since_epoch()).count();
}

class Link {
public:
    Link(const char *addr, uint16_t port)
    {
        _fd = ::socket(AF_INET, SOCK_DGRAM, 0);
        sockaddr_in me{};
        me.sin_family = AF_INET;
        me.sin_addr.s_addr = ::inet_addr(addr);
        me.sin_port = htons(port);
        ::bind(_fd, reinterpret_cast<sockaddr *>(&me), sizeof me);
    }
    ~Link() { if (_fd >= 0) ::close(_fd); }

    bool recv(mavlink_message_t &out, int waitMs)
    {
        if (!_queue.empty()) {                       // спершу віддаємо вже розібране
            out = _queue.front();
            _queue.erase(_queue.begin());
            return true;
        }
        timeval tv{waitMs / 1000, (waitMs % 1000) * 1000};
        fd_set rd;
        FD_ZERO(&rd);
        FD_SET(_fd, &rd);
        if (::select(_fd + 1, &rd, nullptr, nullptr, &tv) <= 0) {
            return false;
        }
        uint8_t buf[2048];
        sockaddr_in from{};
        socklen_t len = sizeof from;
        ssize_t n = ::recvfrom(_fd, buf, sizeof buf, 0,
                               reinterpret_cast<sockaddr *>(&from), &len);
        _peer = from;
        _peerKnown = true;

        mavlink_message_t msg;
        for (ssize_t i = 0; i < n; ++i) {            // в одній датаграмі буває
            if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &_status)) {
                _queue.push_back(msg);               // кілька повідомлень
            }
        }
        if (_queue.empty()) return false;
        out = _queue.front();
        _queue.erase(_queue.begin());
        return true;
    }

    void send(const mavlink_message_t &msg)
    {
        if (!_peerKnown) return;                     // адресу впізнаємо з першої датаграми
        uint8_t buf[MAVLINK_MAX_PACKET_LEN];
        uint16_t n = mavlink_msg_to_send_buffer(buf, &msg);
        ::sendto(_fd, buf, n, 0, reinterpret_cast<const sockaddr *>(&_peer), sizeof _peer);
    }

    bool waitHeartbeat(int timeoutMs)
    {
        const int64_t deadline = nowMs() + timeoutMs;
        mavlink_message_t msg;
        while (nowMs() < deadline) {
            if (!recv(msg, 200) || msg.msgid != MAVLINK_MSG_ID_HEARTBEAT) continue;
            mavlink_heartbeat_t hb;
            mavlink_msg_heartbeat_decode(&msg, &hb);
            if (hb.autopilot == MAV_AUTOPILOT_INVALID) continue;   // камера чи інша станція
            _targetSystem = msg.sysid;
            return true;
        }
        return false;
    }

    uint8_t targetSystem() const { return _targetSystem; }

private:
    int _fd = -1;
    sockaddr_in _peer{};
    bool _peerKnown = false;
    uint8_t _targetSystem = 0;
    mavlink_status_t _status{};
    std::vector<mavlink_message_t> _queue;
};
