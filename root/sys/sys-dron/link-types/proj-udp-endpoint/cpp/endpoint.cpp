// збірка: g++ -std=c++17 -I/usr/include/mavlink/v2.0 endpoint.cpp -o endpoint
#include <common/mavlink.h>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <poll.h>
#include <sys/socket.h>

#include <chrono>
#include <cstdint>
#include <cstdio>
#include <map>
#include <vector>

using Clock = std::chrono::steady_clock;

// ── кому слати: те, що ми вивчили з вхідних датаграм ─────────────────────
struct Target {
    sockaddr_in       addr{};
    Clock::time_point heard{};
};
static uint64_t targetKey(const sockaddr_in& a) {   // адреса й порт в одне число
    return (static_cast<uint64_t>(a.sin_addr.s_addr) << 16) | ntohs(a.sin_port);
}

// ── скільки загубилося: свій відлік на кожного, хто говорить ─────────────
struct SeqState { uint8_t next = 0; bool primed = false; };

int main() {
    const int fd = ::socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) { ::perror("socket"); return 1; }

    int on = 1;
    ::setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));

    sockaddr_in local{};
    local.sin_family      = AF_INET;
    local.sin_addr.s_addr = htonl(INADDR_ANY);
    local.sin_port        = htons(14550);
    if (::bind(fd, reinterpret_cast<sockaddr*>(&local), sizeof(local)) < 0) {
        ::perror("bind");        // порт зайнято — це ЄДИНА помилка, можлива тут;
        return 1;                // мовчання апарата помилкою не є
    }

    std::vector<uint8_t>         rx(64 * 1024);   // датаграма може везти багато кадрів
    std::map<uint64_t, Target>   targets;
    std::map<uint16_t, SeqState> seq;             // ключ: sysid<<8 | compid
    uint64_t got = 0, lost = 0;

    mavlink_message_t msg{};
    mavlink_status_t  st{};
    auto beatAt = Clock::now();

    for (;;) {
        pollfd p{fd, POLLIN, 0};
        const int ready = ::poll(&p, 1, 50);      // 50 мс — щоб не проспати серцебиття

        if (ready > 0 && (p.revents & POLLIN)) {
            sockaddr_in from{};
            socklen_t   fromLen = sizeof(from);
            const ssize_t n = ::recvfrom(fd, rx.data(), rx.size(), 0,
                                         reinterpret_cast<sockaddr*>(&from), &fromLen);
            if (n > 0) {
                // 1. ВИВЧАЄМО ВІДПРАВНИКА: адресу приніс сам пакет
                Target& t = targets[targetKey(from)];
                t.addr  = from;
                t.heard = Clock::now();

                // 2. КОЖЕН байт крізь розбирач: межі датаграми йому не потрібні
                for (ssize_t i = 0; i < n; ++i) {
                    if (mavlink_parse_char(MAVLINK_COMM_0, rx[i], &msg, &st)
                        != MAVLINK_FRAMING_OK) continue;

                    // 3. РОЗРИВ У НОМЕРАХ — свій відлік на кожного відправника
                    SeqState& s = seq[(static_cast<uint16_t>(msg.sysid) << 8) | msg.compid];
                    if (s.primed) lost += static_cast<uint8_t>(msg.seq - s.next);
                    s.primed = true;
                    s.next   = static_cast<uint8_t>(msg.seq + 1);
                    ++got;

                    if (msg.msgid == MAVLINK_MSG_ID_HEARTBEAT) {
                        mavlink_heartbeat_t hb;
                        mavlink_msg_heartbeat_decode(&msg, &hb);
                        std::printf("серцебиття від sys %u comp %u (тип %u); "
                                    "прийнято %llu, утрачено %llu\n",
                                    msg.sysid, msg.compid, hb.type,
                                    static_cast<unsigned long long>(got),
                                    static_cast<unsigned long long>(lost));
                    }
                }
            }
        }

        const auto now = Clock::now();
        if (now < beatAt) continue;
        beatAt = now + std::chrono::seconds(1);

        mavlink_message_t out{};
        mavlink_msg_heartbeat_pack(255, MAV_COMP_ID_MISSIONPLANNER, &out,
                                   MAV_TYPE_GCS, MAV_AUTOPILOT_INVALID,
                                   0, 0, MAV_STATE_ACTIVE);
        uint8_t        wire[MAVLINK_MAX_PACKET_LEN];
        const uint16_t len = mavlink_msg_to_send_buffer(wire, &out);

        // 4. ШЛЕМО В УСІ ВІДОМІ ЦІЛІ — і забуваємо тих, хто давно мовчить
        for (auto it = targets.begin(); it != targets.end(); ) {
            if (now - it->second.heard > std::chrono::seconds(10)) {
                it = targets.erase(it);
                continue;
            }
            ::sendto(fd, wire, len, 0,
                     reinterpret_cast<sockaddr*>(&it->second.addr), sizeof(sockaddr_in));
            ++it;
        }
    }
}
