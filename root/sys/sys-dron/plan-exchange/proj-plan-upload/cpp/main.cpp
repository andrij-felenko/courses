#include <mavlink/common/mavlink.h>   // згенеровані заголовки MAVLink 2

#include <chrono>
#include <cmath>
#include <cstdint>
#include <functional>
#include <set>
#include <string>
#include <vector>

using Clock = std::chrono::steady_clock;

// Пункт у тому вигляді, у якому його тримає редактор.
struct Item {
    uint16_t command      = MAV_CMD_NAV_WAYPOINT;
    uint8_t  frame        = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    float    param[4]     = {0, 0, 0, 0};
    int32_t  x = 0, y = 0;          // широта й довгота, градуси · 10⁷
    float    z = 0;                 // висота, метри
    bool     autocontinue = true;
};

class MissionUploader {
public:
    using Sender = std::function<void(const uint8_t*, uint16_t)>;
    using Logger = std::function<void(const std::string&)>;

    MissionUploader(uint8_t sysId, uint8_t compId, Sender send, Logger log)
        : _sysId(sysId), _compId(compId),
          _send(std::move(send)), _log(std::move(log)) {}

    bool busy() const { return _tx != Tx::None; }

    // home != nullptr — прошивка чекає домашню точку нульовим пунктом.
    bool begin(std::vector<Item> items, uint8_t tgtSys, uint8_t tgtComp,
               const Item* home, Clock::time_point now)
    {
        if (_tx != Tx::None) {              // друга розмова на ту саму тему
            _log("транзакція вже йде");     // протокол не вміє їх розрізняти
            return false;
        }

        // Підготовка списку: дім і зсув цілей — РАЗ, до першого відправлення.
        _items.clear();
        _items.reserve(items.size() + 1);
        if (home) {
            _items.push_back(*home);
            for (Item it : items) {
                if (it.command == MAV_CMD_DO_JUMP)
                    it.param[0] += 1.0f;    // ціль поїхала разом з усіма
                _items.push_back(it);
            }
        } else {
            _items = std::move(items);
        }
        if (_items.empty() || _items.size() > 0xFFFF) {
            _log("порожня або задовга місія");
            return false;
        }
        for (size_t i = 0; i < _items.size(); ++i) {
            if (_items[i].command != MAV_CMD_DO_JUMP) continue;
            const long tgt = std::lroundf(_items[i].param[0]);
            if (tgt < 0 || size_t(tgt) >= _items.size()) {
                _log("DO_JUMP у пункті " + std::to_string(i) +
                     " цілить у неіснуючий " + std::to_string(tgt));
                return false;
            }
        }

        _tgtSys = tgtSys;
        _tgtComp = tgtComp;
        _pending.clear();
        for (uint16_t i = 0; i < uint16_t(_items.size()); ++i)
            _pending.insert(i);             // черга ще не відданих номерів
        _tx = Tx::Write;
        _retry = 0;
        _lastSent = -1;
        _sendCount(now);
        return true;
    }

    // Байти з каналу: розбираємо в кадри й годуємо машину.
    void feed(const uint8_t* data, size_t n, Clock::time_point now) {
        mavlink_message_t msg;
        mavlink_status_t  st;
        for (size_t i = 0; i < n; ++i)
            if (mavlink_parse_char(MAVLINK_COMM_0, data[i], &msg, &st))
                onMessage(msg, now);
    }

    void onMessage(const mavlink_message_t& msg, Clock::time_point now) {
        if (_tx != Tx::Write)     return;   // нас це не стосується
        if (msg.sysid != _tgtSys) return;   // інший апарат у тій самій мережі

        switch (msg.msgid) {
        case MAVLINK_MSG_ID_MISSION_REQUEST_INT: {
            mavlink_mission_request_int_t r;
            mavlink_msg_mission_request_int_decode(&msg, &r);
            _onRequest(r.seq, r.mission_type, now);
            break;
        }
        case MAVLINK_MSG_ID_MISSION_REQUEST: {   // застарілий варіант запиту
            mavlink_mission_request_t r;
            mavlink_msg_mission_request_decode(&msg, &r);
            _onRequest(r.seq, r.mission_type, now);   // відповідь однакова
            break;
        }
        case MAVLINK_MSG_ID_MISSION_ACK: {
            mavlink_mission_ack_t a;
            mavlink_msg_mission_ack_decode(&msg, &a);
            _onAck(a.type, a.mission_type);
            break;
        }
        default: break;
        }
    }

    void tick(Clock::time_point now) {
        if (_expect == Expect::Nothing || now < _deadline) return;

        if (_expect == Expect::Ack) {
            // Усі пункти віддано, а підтвердження немає. Повторювати останній
            // пункт не можна: борт міг уже закрити транзакцію й вважатиме його
            // позаплановим. Чесна відповідь — «невідомо».
            _fail("борт не надіслав завершального підтвердження; що зараз "
                  "на борту — невідомо, перечитай кількість пунктів", true);
            return;
        }
        if (++_retry > MAX_RETRY) {
            _fail("немає відповіді після " + std::to_string(MAX_RETRY) +
                  " спроб", true);
            return;
        }
        if (_lastSent < 0) _sendCount(now);                 // не озвався на лічильник
        else               _sendItem(uint16_t(_lastSent), now);  // та сама відповідь
    }

    void cancel() {
        if (_tx == Tx::None) return;
        _fail("скасовано користувачем", true);
    }

private:
    enum class Tx     : uint8_t { None, Write };   // місце й для Read, Clear
    enum class Expect : uint8_t { Nothing, Request, Ack };

    static constexpr int ACK_MS    = 1500;  // борт зайнятий: пам'ять, запис
    static constexpr int ITEM_MS   =  250;  // борт вільний: тиша = втрата
    static constexpr int MAX_RETRY =    5;

    void _emit(const mavlink_message_t& msg) {
        uint8_t buf[MAVLINK_MAX_PACKET_LEN];   // 280 Б для v2 — менше не можна
        const uint16_t n = mavlink_msg_to_send_buffer(buf, &msg);
        _send(buf, n);
    }

    void _arm(Clock::time_point now, int ms) {
        _deadline = now + std::chrono::milliseconds(ms);
    }

    void _sendCount(Clock::time_point now) {
        mavlink_message_t msg;
        mavlink_msg_mission_count_pack(_sysId, _compId, &msg,
            _tgtSys, _tgtComp, uint16_t(_items.size()),
            _missionType, /*opaque_id*/ 0);
        _emit(msg);
        _expect = Expect::Request;
        _arm(now, ACK_MS);
    }

    void _sendItem(uint16_t seq, Clock::time_point now) {
        const Item& it = _items[seq];
        mavlink_message_t msg;
        mavlink_msg_mission_item_int_pack(_sysId, _compId, &msg,
            _tgtSys, _tgtComp, seq, it.frame, it.command,
            /*current*/ 0, it.autocontinue ? 1 : 0,
            it.param[0], it.param[1], it.param[2], it.param[3],
            it.x, it.y, it.z, _missionType);
        _emit(msg);
        _lastSent = int32_t(seq);
        _pending.erase(seq);                   // повторне викреслення нешкідливе
        if (_pending.empty()) { _expect = Expect::Ack;     _arm(now, ACK_MS); }
        else                  { _expect = Expect::Request; _arm(now, ITEM_MS); }
    }

    void _sendAck(uint8_t code) {
        mavlink_message_t msg;
        mavlink_msg_mission_ack_pack(_sysId, _compId, &msg,
            _tgtSys, _tgtComp, code, _missionType, /*opaque_id*/ 0);
        _emit(msg);
    }

    void _onRequest(uint16_t seq, uint8_t type, Clock::time_point now) {
        if (type != _missionType) return;      // запит на інший тип плану
        if (_expect != Expect::Request && _expect != Expect::Ack) {
            _log("запит поза чергою — викидаємо");   // хвіст старої розмови
            return;
        }
        if (seq >= _items.size()) {            // межа масиву — з мережевих даних!
            _fail("борт просить пункт " + std::to_string(seq) +
                  ", а їх усього " + std::to_string(_items.size()), true);
            return;
        }
        _retry = 0;                            // рух є — спроби обнуляємо
        _sendItem(seq, now);
    }

    void _onAck(uint8_t code, uint8_t type) {
        if (type != _missionType || _expect == Expect::Nothing) return;

        if (code == MAV_MISSION_ACCEPTED) {
            if (!_pending.empty()) {
                _fail("борт підтвердив місію, не забравши " +
                      std::to_string(_pending.size()) + " пунктів", false);
                return;
            }
            _log("готово: на борту " + std::to_string(_items.size()) + " пунктів");
            _reset();
            return;
        }
        _fail(_explain(code), false);   // борт уже закрив розмову
    }

    static const char* _blamedField(uint8_t code) {
        switch (code) {
        case MAV_MISSION_INVALID_PARAM1:   return "param1";
        case MAV_MISSION_INVALID_PARAM2:   return "param2";
        case MAV_MISSION_INVALID_PARAM3:   return "param3";
        case MAV_MISSION_INVALID_PARAM4:   return "param4";
        case MAV_MISSION_INVALID_PARAM5_X: return "x (широта)";
        case MAV_MISSION_INVALID_PARAM6_Y: return "y (довгота)";
        case MAV_MISSION_INVALID_PARAM7:   return "z (висота)";
        default:                           return nullptr;
        }
    }

    static const char* _resultName(uint8_t code) {
        switch (code) {
        case MAV_MISSION_ERROR:
            return "MAV_MISSION_ERROR — борт зараз не приймає місій";
        case MAV_MISSION_UNSUPPORTED_FRAME:
            return "MAV_MISSION_UNSUPPORTED_FRAME — невідома рамка координат";
        case MAV_MISSION_UNSUPPORTED:
            return "MAV_MISSION_UNSUPPORTED — невідома команда";
        case MAV_MISSION_NO_SPACE:
            return "MAV_MISSION_NO_SPACE — пунктів більше, ніж уміщає пам'ять";
        case MAV_MISSION_INVALID:
            return "MAV_MISSION_INVALID — недозволене значення в пункті";
        case MAV_MISSION_INVALID_SEQUENCE:
            return "MAV_MISSION_INVALID_SEQUENCE — номер приїхав не в тому порядку";
        case MAV_MISSION_DENIED:
            return "MAV_MISSION_DENIED — від цього відправника місій не беруть";
        case MAV_MISSION_OPERATION_CANCELLED:
            return "MAV_MISSION_OPERATION_CANCELLED — борт перервав обмін";
        default:
            return "невідомий код завершення";
        }
    }

    // Головне тут — прив'язка коду до конкретного пункту.
    std::string _explain(uint8_t code) const {
        std::string s = "борт відмовив: ";
        if (const char* f = _blamedField(code))
            s += std::string("недозволене значення в полі ") + f;
        else
            s += _resultName(code);

        if (_lastSent < 0)
            return s + "; жодного пункту ще не віддано — причина стосується "
                       "самого лічильника (" + std::to_string(_items.size()) +
                       " пунктів)";

        const Item& it = _items[size_t(_lastSent)];
        return s + "; останній відданий пункт " + std::to_string(_lastSent) +
               ": команда " + std::to_string(it.command) +
               ", рамка "   + std::to_string(int(it.frame)) +
               ", param1 "  + std::to_string(it.param[0]) +
               ", x "       + std::to_string(it.x) +
               ", y "       + std::to_string(it.y) +
               ", z "       + std::to_string(it.z);
    }

    void _fail(const std::string& why, bool tellVehicle) {
        // Своє скасування — теж повідомлення: інакше борт чекатиме решти
        // пунктів до власного таймауту й не прийме нової спроби.
        if (tellVehicle) _sendAck(MAV_MISSION_OPERATION_CANCELLED);
        _log("зірвалося: " + why);
        _reset();
    }

    void _reset() {
        _tx = Tx::None;
        _expect = Expect::Nothing;    // усе, що прийде далі, вже не наше
        _pending.clear();
        _items.clear();
        _lastSent = -1;
        _retry = 0;
    }

    uint8_t _sysId, _compId;
    Sender  _send;
    Logger  _log;

    uint8_t _tgtSys = 0, _tgtComp = 0;
    uint8_t _missionType = MAV_MISSION_TYPE_MISSION;

    Tx      _tx     = Tx::None;
    Expect  _expect = Expect::Nothing;
    std::vector<Item>  _items;
    std::set<uint16_t> _pending;
    int32_t _lastSent = -1;
    int     _retry    = 0;
    Clock::time_point _deadline{};
};

// ── застосування ───────────────────────────────────────────────────────────
void run(Link& link, const std::vector<Item>& mission, bool homeAsItemZero)
{
    MissionUploader up(255, MAV_COMP_ID_MISSIONPLANNER,
        [&link](const uint8_t* b, uint16_t n) { link.write(b, n); },
        [](const std::string& s) { std::puts(s.c_str()); });

    Item home;
    home.command = MAV_CMD_NAV_WAYPOINT;
    home.frame   = MAV_FRAME_GLOBAL;              // дім — абсолютна висота
    home.x = 504500000; home.y = 305230000; home.z = 148.0f;

    up.begin(mission, /*tgtSys*/ 1, MAV_COMP_ID_AUTOPILOT1,
             homeAsItemZero ? &home : nullptr, Clock::now());

    uint8_t rx[512];
    while (up.busy()) {
        const auto now = Clock::now();
        up.feed(rx, link.read(rx, sizeof rx, /*timeout_ms*/ 20), now);
        up.tick(now);
    }
}
