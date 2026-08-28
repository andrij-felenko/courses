// mavtap.cpp — спостерігач за потоком MAVLink: рядки, частоти, поля, запис кривої.
//
// збірка (заголовки — з генерації mavgen для свого діалекту):
//   g++ -O2 -std=c++17 mavtap.cpp -I<тека згенерованих заголовків> -o mavtap
//
// БЕЗ ЦЬОГО ВИЗНАЧЕННЯ таблиць опису повідомлень у збірці не буде,
// і mavlink_get_message_info() просто не існуватиме.
#define MAVLINK_USE_MESSAGE_INFO
#include <common/mavlink.h>

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <string>
#include <unordered_map>
#include <vector>

#if !defined(_WIN32)
#  include <netinet/in.h>
#  include <sys/socket.h>
#  include <sys/time.h>
#  include <unistd.h>
#endif

// ── сталі ───────────────────────────────────────────────────────────────────
constexpr uint8_t kChannel   = MAVLINK_COMM_0;   // свій слот розбирача
constexpr int     kStampBytes = 8;               // мітка часу запису .tlog
constexpr double  kTickSec    = 1.0;             // такт оцінювача частоти
constexpr double  kAlphaNew   = 0.8;             // вага свіжого відліку
constexpr size_t  kMaxRows    = 4096;            // стеля рядків на систему

// ── значення розрізняльного поля: короткий текст без виділення пам'яті ──────
struct Inst {
    char    s[24] = {};
    uint8_t n     = 0;

    bool operator==(const Inst& o) const {
        return n == o.n && std::memcmp(s, o.s, n) == 0;
    }
    void set(const char* p, size_t k) {
        n = static_cast<uint8_t>(k < sizeof(s) ? k : sizeof(s));
        std::memcpy(s, p, n);
    }
};

struct RowKey {
    uint32_t msgid  = 0;
    uint8_t  compid = 0;
    Inst     inst;

    bool operator==(const RowKey& o) const {
        return msgid == o.msgid && compid == o.compid && inst == o.inst;
    }
};

struct RowKeyHash {
    size_t operator()(const RowKey& k) const noexcept {
        uint64_t h = 1469598103934665603ULL;                 // FNV-1a, 64 біти
        auto mix = [&h](uint8_t b) { h ^= b; h *= 1099511628211ULL; };
        for (int i = 0; i < 4; ++i) mix(static_cast<uint8_t>(k.msgid >> (8 * i)));
        mix(k.compid);
        for (uint8_t i = 0; i < k.inst.n; ++i) mix(static_cast<uint8_t>(k.inst.s[i]));
        return static_cast<size_t>(h);
    }
};

// ── читання поля з навантаження ─────────────────────────────────────────────
static unsigned typeSize(mavlink_message_type_t t) {
    switch (t) {
    case MAVLINK_TYPE_CHAR:
    case MAVLINK_TYPE_UINT8_T:
    case MAVLINK_TYPE_INT8_T:   return 1;
    case MAVLINK_TYPE_UINT16_T:
    case MAVLINK_TYPE_INT16_T:  return 2;
    case MAVLINK_TYPE_UINT32_T:
    case MAVLINK_TYPE_INT32_T:
    case MAVLINK_TYPE_FLOAT:    return 4;
    default:                    return 8;
    }
}

// ЗАВЖДИ memcpy. Початок навантаження кратний восьми, але поле стоїть на своєму
// wire_offset: uint16_t за зсувом 41 і uint32_t за зсувом 50 — звичайна річ.
template <typename T>
static T wireRead(const mavlink_message_t& m, unsigned off) {
    T v{};
    std::memcpy(&v, _MAV_PAYLOAD(&m) + off, sizeof(T));
    return v;
}

struct Scalar { char txt[32]; };

static Scalar readScalar(const mavlink_message_t& m, mavlink_message_type_t t, unsigned off) {
    Scalar r{{0}};
    switch (t) {
    case MAVLINK_TYPE_UINT8_T:
        std::snprintf(r.txt, sizeof(r.txt), "%u",
                      unsigned(wireRead<uint8_t>(m, off))); break;
    case MAVLINK_TYPE_INT8_T:
        std::snprintf(r.txt, sizeof(r.txt), "%d",
                      int(wireRead<int8_t>(m, off))); break;
    case MAVLINK_TYPE_UINT16_T:
        std::snprintf(r.txt, sizeof(r.txt), "%u",
                      unsigned(wireRead<uint16_t>(m, off))); break;
    case MAVLINK_TYPE_INT16_T:
        std::snprintf(r.txt, sizeof(r.txt), "%d",
                      int(wireRead<int16_t>(m, off))); break;
    case MAVLINK_TYPE_UINT32_T:
        std::snprintf(r.txt, sizeof(r.txt), "%lu",
                      (unsigned long)wireRead<uint32_t>(m, off)); break;
    case MAVLINK_TYPE_INT32_T:
        std::snprintf(r.txt, sizeof(r.txt), "%ld",
                      (long)wireRead<int32_t>(m, off)); break;
    case MAVLINK_TYPE_UINT64_T:
        std::snprintf(r.txt, sizeof(r.txt), "%llu",
                      (unsigned long long)wireRead<uint64_t>(m, off)); break;
    case MAVLINK_TYPE_INT64_T:
        std::snprintf(r.txt, sizeof(r.txt), "%lld",
                      (long long)wireRead<int64_t>(m, off)); break;
    case MAVLINK_TYPE_FLOAT:
        std::snprintf(r.txt, sizeof(r.txt), "%.6g",
                      double(wireRead<float>(m, off))); break;
    case MAVLINK_TYPE_DOUBLE:
        std::snprintf(r.txt, sizeof(r.txt), "%.10g",
                      wireRead<double>(m, off)); break;
    default:
        r.txt[0] = '?'; r.txt[1] = '\0'; break;
    }
    return r;
}

// ── правила розрізнення примірників: ДАНІ, не код ───────────────────────────
static std::unordered_map<uint32_t, unsigned> g_instField;   // msgid → номер поля

static bool addInstanceRule(const char* msgName, const char* fieldName, bool quiet = false) {
    const mavlink_message_info_t* info = mavlink_get_message_info_by_name(msgName);
    if (!info) {
        if (!quiet) std::fprintf(stderr, "діалект не знає повідомлення %s\n", msgName);
        return false;
    }
    for (unsigned i = 0; i < info->num_fields; ++i) {
        if (std::strcmp(info->fields[i].name, fieldName) != 0) continue;
        const mavlink_message_type_t t = info->fields[i].type;
        if (t == MAVLINK_TYPE_FLOAT || t == MAVLINK_TYPE_DOUBLE) {
            std::fprintf(stderr, "%s.%s дробове — розрізняти таким не можна\n", msgName, fieldName);
            return false;
        }
        g_instField[info->msgid] = i;
        return true;
    }
    if (!quiet) std::fprintf(stderr, "у %s немає поля %s\n", msgName, fieldName);
    return false;
}

static void defaultInstanceRules() {
    static const char* kRules[][2] = {
        {"BATTERY_STATUS",    "id"},     {"ESC_INFO",   "index"},
        {"ESC_STATUS",        "index"},  {"DEBUG",      "ind"},
        {"NAMED_VALUE_FLOAT", "name"},   {"NAMED_VALUE_INT", "name"},
        {"DEBUG_VECT",        "name"},
        {"GIMBAL_DEVICE_ATTITUDE_STATUS", "gimbal_device_id"},
    };
    for (const auto& r : kRules) addInstanceRule(r[0], r[1], true);   // чого немає — мовчки повз
}

// Одне правило працює і для числа, і для рядка: NAMED_VALUE_FLOAT.name — char[10].
static Inst instanceOf(const mavlink_message_t& m, const mavlink_message_info_t* info) {
    Inst inst;
    const auto it = g_instField.find(m.msgid);
    if (it == g_instField.end()) return inst;              // повідомлення без примірників

    const mavlink_field_info_t& fi = info->fields[it->second];
    if (fi.type == MAVLINK_TYPE_CHAR) {
        const unsigned lim = fi.array_length ? fi.array_length : 1u;
        const char* p = _MAV_PAYLOAD(&m) + fi.wire_offset;
        size_t k = 0;
        while (k < lim && k < sizeof(inst.s) && p[k]) ++k;
        inst.set(p, k);
        return inst;
    }
    const Scalar sc = readScalar(m, fi.type, fi.wire_offset);
    inst.set(sc.txt, std::strlen(sc.txt));
    return inst;
}

// ── поля рядка ──────────────────────────────────────────────────────────────
struct Field {
    std::string            name;                        // з індексом: voltages[3]
    unsigned               off   = 0;                   // зсув у навантаженні
    mavlink_message_type_t type  = MAVLINK_TYPE_CHAR;
    unsigned               chars = 0;                   // >0 — рядковий масив
    std::string            text;                        // останнє показане
    bool                   logged = false;
};

// Порядок полів в описі — порядок XML, а НЕ порядок у навантаженні.
// Місце в байтах питаємо лише в wire_offset.
static std::vector<Field> buildFields(const mavlink_message_info_t* info) {
    std::vector<Field> out;
    out.reserve(info->num_fields);
    for (unsigned i = 0; i < info->num_fields; ++i) {
        const mavlink_field_info_t& fi = info->fields[i];

        if (fi.type == MAVLINK_TYPE_CHAR) {              // ім'я лишається одним полем
            Field f;
            f.name  = fi.name;
            f.off   = fi.wire_offset;
            f.type  = fi.type;
            f.chars = fi.array_length ? fi.array_length : 1u;
            out.push_back(std::move(f));
            continue;
        }
        if (fi.array_length == 0) {                      // скаляр
            Field f;
            f.name = fi.name;
            f.off  = fi.wire_offset;
            f.type = fi.type;
            out.push_back(std::move(f));
            continue;
        }
        const unsigned esz = typeSize(fi.type);          // масив → окремі елементи
        for (unsigned j = 0; j < fi.array_length; ++j) {
            Field f;
            f.name = std::string(fi.name) + "[" + std::to_string(j) + "]";
            f.off  = fi.wire_offset + j * esz;
            f.type = fi.type;
            out.push_back(std::move(f));
        }
    }
    return out;
}

// ── рядок і система ─────────────────────────────────────────────────────────
struct Row {
    RowKey             key;
    std::string        title;              // BATTERY_STATUS[1]
    uint64_t           count = 0, lastCount = 0;
    double             rateHz = 0.0;
    mavlink_message_t  last{};             // копія ОСТАННЬОГО кадру
    bool               selected  = false;
    bool               anyLogged = false;
    std::vector<Field> fields;
};

struct SeqState { uint8_t last = 0; bool have = false; uint64_t dup = 0, gap = 0, back = 0; };

struct System {
    std::unordered_map<RowKey, Row, RowKeyHash> rows;
    std::unordered_map<uint8_t, SeqState>       seq;
    bool overflow = false;
};

static bool matches(const std::string& title, const std::string& pat) {
    if (pat.empty()) return false;
    if (title == pat) return true;
    const size_t br = title.find('[');                   // BATTERY_STATUS = усі примірники
    return br != std::string::npos && title.compare(0, br, pat) == 0;
}

class Tap {
public:
    void selectPattern(const std::string& p) { _selectPat = p; }

    bool logSpec(const std::string& spec) {              // ROW.FIELD
        const size_t dot = spec.find('.');
        if (dot == std::string::npos) return false;
        _logRow   = spec.substr(0, dot);
        _logField = spec.substr(dot + 1);
        const std::string path = "mavtap-" + _logField + ".csv";
        _logOut = std::fopen(path.c_str(), "w");
        if (_logOut) std::fprintf(_logOut, "t_s,%s\n", _logField.c_str());
        return _logOut != nullptr;
    }

    void onMessage(const mavlink_message_t& m, uint64_t tUsec) {
        System& sys = _systems[m.sysid];                 // система з'являється з байта заголовка
        trackSeq(sys, m);

        const mavlink_message_info_t* info = mavlink_get_message_info(&m);
        if (!info) return;

        RowKey key;
        key.msgid  = m.msgid;
        key.compid = m.compid;
        key.inst   = instanceOf(m, info);

        auto it = sys.rows.find(key);
        if (it == sys.rows.end()) {
            if (sys.rows.size() >= kMaxRows) { sys.overflow = true; return; }
            it = sys.rows.emplace(key, makeRow(key, info)).first;
        }

        Row& row = it->second;
        ++row.count;                                     // ДЕШЕВО
        row.last = m;                                    // ДЕШЕВО: 296 Б, без купи
        if (row.anyLogged) logSample(row, tUsec);        // дорого — але лише записуване поле
    }

    void tick(double elapsedSec) {
        if (elapsedSec <= 0.0) return;
        for (auto& sp : _systems)
            for (auto& rp : sp.second.rows) {
                Row& row = rp.second;
                const double instHz = double(row.count - row.lastCount) / elapsedSec;
                row.rateHz    = (1.0 - kAlphaNew) * row.rateHz + kAlphaNew * instHz;
                row.lastCount = row.count;
            }
        if (_logOut) std::fflush(_logOut);
    }

    void print(uint64_t tUsec) {
        std::printf("\x1b[H\x1b[2J");                    // очистити екран
        std::printf("t = %.1f с\n", double(tUsec) / 1e6);

        for (auto& sp : _systems) {
            System& sys = sp.second;
            std::printf("\n-- система %u --\n", unsigned(sp.first));
            std::printf("   %-30s comp    кадрів      Гц\n", "рядок");

            std::vector<Row*> ordered;                   // порядок будуємо на друці:
            ordered.reserve(sys.rows.size());            // сорок рядків сортуються задарма
            for (auto& rp : sys.rows) ordered.push_back(&rp.second);
            std::sort(ordered.begin(), ordered.end(), [](const Row* a, const Row* b) {
                if (a->key.compid != b->key.compid) return a->key.compid < b->key.compid;
                return a->title < b->title;
            });

            for (const Row* r : ordered)
                std::printf("   %-30s %4u %9llu %7.1f\n", r->title.c_str(),
                            unsigned(r->key.compid), (unsigned long long)r->count, r->rateHz);

            for (const auto& sq : sys.seq)
                std::printf("   comp %u: пропущено %llu · здубльовано %llu · назад %llu\n",
                            unsigned(sq.first), (unsigned long long)sq.second.gap,
                            (unsigned long long)sq.second.dup,
                            (unsigned long long)sq.second.back);
            if (sys.overflow)
                std::printf("   стеля рядків досягнута — нові примірники не заводяться\n");

            for (Row* r : ordered) {                     // розкладання — тут, на такті друку
                if (!r->selected) continue;
                decodeRow(*r);
                std::printf("\n   %s\n", r->title.c_str());
                for (const Field& f : r->fields)
                    std::printf("      %-24s %s\n", f.name.c_str(), f.text.c_str());
            }
        }
        std::fflush(stdout);
    }

private:
    Row makeRow(const RowKey& key, const mavlink_message_info_t* info) const {
        Row r;
        r.key   = key;
        r.title = info->name;
        if (key.inst.n) r.title += "[" + std::string(key.inst.s, key.inst.n) + "]";
        r.fields   = buildFields(info);
        r.selected = matches(r.title, _selectPat);
        if (_logOut && matches(r.title, _logRow))
            for (Field& f : r.fields)
                if (f.name == _logField) { f.logged = true; r.anyLogged = true; }
        return r;
    }

    static void trackSeq(System& sys, const mavlink_message_t& m) {
        SeqState& s = sys.seq[m.compid];
        if (!s.have) { s.last = m.seq; s.have = true; return; }

        const uint8_t d = static_cast<uint8_t>(m.seq - s.last);   // за модулем 256
        if      (d == 0)  ++s.dup;                  // той самий кадр удруге — дві дороги
        else if (d == 1)  { }                       // рівно наступний
        else if (d < 128) s.gap += (d - 1);         // стільки кадрів не долетіло
        else              ++s.back;                 // номер пішов назад

        if (d != 0 && d < 128) s.last = m.seq;      // назад позначку не рухаємо
    }

    void decodeRow(Row& row) const {
        for (Field& f : row.fields) {
            if (f.chars) {                          // символьний масив — як текст
                const char* p = _MAV_PAYLOAD(&row.last) + f.off;
                size_t k = 0;
                while (k < f.chars && p[k]) ++k;
                f.text.assign(p, k);
                continue;
            }
            f.text = readScalar(row.last, f.type, f.off).txt;
        }
    }

    void logSample(Row& row, uint64_t tUsec) {
        for (const Field& f : row.fields) {
            if (!f.logged) continue;
            const Scalar sc = readScalar(row.last, f.type, f.off);
            std::fprintf(_logOut, "%.6f,%s\n", double(tUsec) / 1e6, sc.txt);
        }
    }

    std::map<uint8_t, System> _systems;                  // впорядкована за sysid — для друку
    std::string _selectPat, _logRow, _logField;
    std::FILE*  _logOut = nullptr;
};

// ── джерело: файл телеметрії ────────────────────────────────────────────────
// Запис — вісім байтів часу (мікросекунди від епохи, старший байт першим) і
// кадр як прийшов. Розпізнавання чужого порядку байтів і перемотування тут
// свідомо опущено: це задача окремого читача логу.
static int runTlog(const char* path, Tap& tap) {
    std::FILE* f = std::fopen(path, "rb");
    if (!f) { std::perror(path); return 1; }

    mavlink_message_t msg{};
    mavlink_status_t  st{};
    uint8_t  stamp[kStampBytes];
    uint64_t firstUsec = 0, lastTickUsec = 0;
    bool     started = false;

    while (std::fread(stamp, 1, kStampBytes, f) == size_t(kStampBytes)) {
        uint64_t tUsec = 0;
        for (int i = 0; i < kStampBytes; ++i) tUsec = (tUsec << 8) | stamp[i];

        // Межа кадру у файлі відома точно, тож стан каналу скидаємо на кожному
        // записі: недобудований залишок попереднього не має продовжуватися.
        mavlink_reset_channel_status(kChannel);

        bool got = false;
        int  c   = 0;
        for (int k = 0; k < MAVLINK_MAX_PACKET_LEN && (c = std::fgetc(f)) != EOF; ++k)
            if (mavlink_parse_char(kChannel, uint8_t(c), &msg, &st)) { got = true; break; }
        if (!got) break;                         // обірваний хвіст — звичайний кінець

        if (!started) { firstUsec = lastTickUsec = tUsec; started = true; }
        tap.onMessage(msg, tUsec - firstUsec);

        // ТАКТ ВЕДЕ ЧАС ЛОГУ: таблиця однакова, хоч файл читається за секунду,
        // хоч відтворюється в темпі польоту.
        if (tUsec >= lastTickUsec + uint64_t(kTickSec * 1e6)) {
            tap.tick(double(tUsec - lastTickUsec) / 1e6);
            tap.print(tUsec - firstUsec);
            lastTickUsec = tUsec;
        }
    }
    std::fclose(f);
    return 0;
}

// ── джерело: UDP ────────────────────────────────────────────────────────────
#if !defined(_WIN32)
static int runUdp(int port, Tap& tap) {
    const int fd = ::socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) { std::perror("socket"); return 1; }

    sockaddr_in addr{};
    addr.sin_family      = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port        = htons(uint16_t(port));
    if (::bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        std::perror("bind");
        return 1;
    }

    timeval tv{};                                // щоб такт спрацьовував і в тиші
    tv.tv_usec = 200000;
    ::setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    mavlink_message_t msg{};
    mavlink_status_t  st{};
    uint8_t buf[2048];

    using Clock = std::chrono::steady_clock;     // МОНОТОННИЙ: міряємо проміжок
    const auto t0 = Clock::now();
    auto lastTick = t0;

    for (;;) {
        const ssize_t n   = ::recv(fd, buf, sizeof(buf), 0);
        const auto    now = Clock::now();
        const uint64_t tUsec =
            std::chrono::duration_cast<std::chrono::microseconds>(now - t0).count();

        for (ssize_t i = 0; i < n; ++i)
            if (mavlink_parse_char(kChannel, buf[i], &msg, &st)) tap.onMessage(msg, tUsec);

        const double elapsed = std::chrono::duration<double>(now - lastTick).count();
        if (elapsed >= kTickSec) {
            tap.tick(elapsed);
            tap.print(tUsec);
            lastTick = now;
        }
    }
}
#endif

int main(int argc, char** argv) {
    const char* tlog = nullptr;
    int         port = 0;
    Tap         tap;

    defaultInstanceRules();

    for (int i = 1; i + 1 < argc; i += 2) {
        const std::string k = argv[i], v = argv[i + 1];
        if      (k == "--tlog")   tlog = argv[i + 1];
        else if (k == "--udp")    port = std::atoi(argv[i + 1]);
        else if (k == "--select") tap.selectPattern(v);
        else if (k == "--log")    tap.logSpec(v);
        else if (k == "--instance") {
            const size_t eq = v.find('=');
            if (eq != std::string::npos)
                addInstanceRule(v.substr(0, eq).c_str(), v.substr(eq + 1).c_str());
        }
    }

    if (tlog) return runTlog(tlog, tap);
#if !defined(_WIN32)
    if (port) return runUdp(port, tap);
#endif
    std::fprintf(stderr,
        "usage: mavtap (--tlog FILE | --udp PORT) [--select ROW]\n"
        "              [--log ROW.FIELD] [--instance MSG=FIELD]\n");
    return 2;
}
