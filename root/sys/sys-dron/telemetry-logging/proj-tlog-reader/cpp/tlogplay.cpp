// tlogplay.cpp — читач логу телеметрії .tlog
// збірка: g++ -O2 -std=c++17 tlogplay.cpp -I<тека згенерованого MAVLink> -o tlogplay
#include <common/mavlink.h>

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <thread>
#include <vector>

// ── сталі ───────────────────────────────────────────────────────────────────
constexpr int      kStampBytes    = 8;
constexpr uint64_t kUsecPerSec    = 1000000ULL;
constexpr uint64_t kIndexStepUsec = 1 * kUsecPerSec;  // крок таблиці «час → зсув»
constexpr size_t   kProbeRecords  = 64;               // на скількох мітках вирішуємо порядок
constexpr int64_t  kResyncLimit   = 1 << 16;          // стеля скану межі кадру, байтів
constexpr int      kBatchWindowMs = 3;                // ближче за це — однією пачкою
constexpr uint8_t  kChannel       = MAVLINK_COMM_1;   // НЕ той канал, де живий лінк

constexpr uint64_t kStampFloorUsec = 1104537600ULL * kUsecPerSec;  // 2005-01-01

uint64_t beToU64(const uint8_t* p) {
    uint64_t v = 0;
    for (int i = 0; i < kStampBytes; ++i) v = (v << 8) | p[i];
    return v;
}

uint64_t swap64(uint64_t v) {
    uint64_t r = 0;
    for (int i = 0; i < kStampBytes; ++i) { r = (r << 8) | (v & 0xFFu); v >>= 8; }
    return r;
}

int frameLength(const uint8_t* h) {
    if (h[0] == MAVLINK_STX)              // 0xFD — MAVLink 2
        return MAVLINK_NUM_NON_PAYLOAD_BYTES + h[1] +
               ((h[2] & MAVLINK_IFLAG_SIGNED) ? MAVLINK_SIGNATURE_BLOCK_LEN : 0);
    if (h[0] == MAVLINK_STX_MAVLINK1)     // 0xFE — MAVLink 1
        return MAVLINK_CORE_HEADER_MAVLINK1_LEN + 1 + 2 + h[1];
    return -1;
}

// ── буферизоване читання з довільним позиціюванням ──────────────────────────
class FileBytes {
public:
    ~FileBytes() { if (_f) std::fclose(_f); }

    bool open(const char* path) {
        _f = std::fopen(path, "rb");
        if (!_f) return false;
        if (!seekRaw(0, SEEK_END)) return false;
        _size = tellRaw();
        return seek(0);
    }

    int64_t size() const { return _size; }
    int64_t tell() const { return _bufStart + static_cast<int64_t>(_bufPos); }

    bool seek(int64_t off) {
        if (off < 0 || off > _size || !seekRaw(off, SEEK_SET)) return false;
        _bufStart = off;
        _bufPos = _bufLen = 0;
        return true;
    }

    bool getByte(uint8_t& b) {
        if (_bufPos == _bufLen && !refill()) return false;
        b = _buf[_bufPos++];
        return true;
    }

    bool read(uint8_t* dst, size_t n) {
        for (size_t i = 0; i < n; ++i) if (!getByte(dst[i])) return false;
        return true;
    }

    bool skip(int64_t n) {                       // перескочити, не копіюючи
        if (n < 0 || tell() + n > _size) return false;
        const int64_t inBuf = static_cast<int64_t>(_bufLen - _bufPos);
        if (n <= inBuf) { _bufPos += static_cast<size_t>(n); return true; }
        return seek(tell() + n);
    }

private:
    bool refill() {
        _bufStart += static_cast<int64_t>(_bufLen);
        _bufPos = 0;
        _bufLen = std::fread(_buf, 1, sizeof(_buf), _f);
        return _bufLen > 0;
    }
    bool seekRaw(int64_t off, int whence) {
#if defined(_WIN32)
        return _fseeki64(_f, off, whence) == 0;
#else
        return fseeko(_f, static_cast<off_t>(off), whence) == 0;
#endif
    }
    int64_t tellRaw() {
#if defined(_WIN32)
        return _ftelli64(_f);
#else
        return static_cast<int64_t>(ftello(_f));
#endif
    }

    std::FILE* _f = nullptr;
    int64_t    _size = 0, _bufStart = 0;
    size_t     _bufLen = 0, _bufPos = 0;
    uint8_t    _buf[64 * 1024];
};

// ── читач ───────────────────────────────────────────────────────────────────
struct IndexEntry { uint64_t tUsec; int64_t offset; };
struct RawStamp   { uint64_t raw;   int64_t off;    };

bool chooseSwapped(const std::vector<RawStamp>& head) {
    const uint64_t nowUsec  = static_cast<uint64_t>(std::time(nullptr)) * kUsecPerSec;
    const uint64_t ceilUsec = nowUsec + 365ULL * 86400ULL * kUsecPerSec;

    auto score = [&](bool swapped) {
        int      s = 0;
        uint64_t prev = 0;
        bool     havePrev = false;
        for (const RawStamp& h : head) {
            const uint64_t t = swapped ? swap64(h.raw) : h.raw;
            s += (t >= kStampFloorUsec && t <= ceilUsec) ? +1 : -1;
            if (havePrev) s += (t >= prev) ? +1 : -1;
            prev = t;
            havePrev = true;
        }
        return s;
    };
    return score(true) > score(false);    // рівність → старший-перший
}

class TlogReader {
public:
    bool open(const char* path) {
        if (!_f.open(path) || _f.size() < kStampBytes) return false;
        if (!scanFile()) return false;
        return positionAtRecord(0);
    }

    uint64_t firstUsec()    const { return _first; }
    uint64_t durationUsec() const { return _last > _first ? _last - _first : 0; }
    int      backSteps()    const { return _backSteps; }
    int      breaks()       const { return _breaks; }
    bool     truncated()    const { return _truncated; }

    bool pending(uint64_t& tUsec) const {
        if (!_hasPending) return false;
        tUsec = _pendingT;
        return true;
    }

    bool positionAtRecord(int64_t offset) {
        uint8_t stamp[kStampBytes];
        if (!_f.seek(offset) || !_f.read(stamp, kStampBytes)) { _hasPending = false; return false; }
        _pendingT   = decode(stamp);
        _hasPending = true;
        return true;
    }

    bool next(uint64_t& tUsec, std::vector<uint8_t>& frame) {
        if (!_hasPending) return false;
        tUsec = _pendingT;
        frame.clear();

        mavlink_reset_channel_status(kChannel);

        mavlink_message_t msg{};
        mavlink_status_t  st{};
        uint8_t b = 0;
        while (_f.getByte(b)) {
            frame.push_back(b);
            if (mavlink_parse_char(kChannel, b, &msg, &st)) {
                uint8_t stamp[kStampBytes];
                _hasPending = _f.read(stamp, kStampBytes);
                if (_hasPending) _pendingT = decode(stamp);
                return true;
            }
            if (frame.size() > MAVLINK_MAX_PACKET_LEN) break;
        }
        _hasPending = false;
        _truncated  = true;
        return false;
    }

    int64_t resyncFrom(int64_t byteOffset) {
        if (!_f.seek(byteOffset)) return -1;
        mavlink_reset_channel_status(kChannel);

        mavlink_message_t msg{};
        mavlink_status_t  st{};
        uint8_t b = 0;
        for (int64_t scanned = 0; scanned < kResyncLimit && _f.getByte(b); ++scanned) {
            if (!mavlink_parse_char(kChannel, b, &msg, &st)) continue;
            const int64_t frameEnd   = _f.tell();
            const int64_t frameStart = frameEnd - mavlink_msg_get_send_buffer_length(&msg);
            const int64_t recStart   = frameStart - kStampBytes;
            if (recStart >= 0) return recStart;
        }
        return -1;
    }

    bool seekToByte(int64_t byteOffset) {
        const int64_t rec = resyncFrom(byteOffset);
        if (rec < 0 || !positionAtRecord(rec)) return false;

        std::vector<uint8_t> probe;
        uint64_t t = 0;
        if (!next(t, probe)) return false;
        bool confirmed = !_hasPending;
        if (!confirmed) confirmed = next(t, probe);
        if (!confirmed) return false;
        return positionAtRecord(rec);
    }

    bool seekToTime(uint64_t tUsec) {
        if (_index.empty()) return false;
        auto it = std::upper_bound(_index.begin(), _index.end(), tUsec,
                                   [](uint64_t t, const IndexEntry& e) { return t < e.tUsec; });
        const IndexEntry& e = (it == _index.begin()) ? _index.front() : *(it - 1);
        if (!positionAtRecord(e.offset)) return false;

        std::vector<uint8_t> skip;
        uint64_t t = 0;
        while (_hasPending && _pendingT < tUsec) {
            if (!next(t, skip)) break;
        }
        return true;
    }

private:
    uint64_t decode(const uint8_t* p) const {
        const uint64_t v = beToU64(p);
        return _swapped ? swap64(v) : v;
    }

    bool scanFile() {
        if (!_f.seek(0)) return false;

        std::vector<RawStamp> head;
        head.reserve(kProbeRecords);

        bool     decided = false, haveFirst = false;
        uint64_t nextIndexT = 0, prevT = 0;

        auto accept = [&](uint64_t raw, int64_t off) {
            const uint64_t t = _swapped ? swap64(raw) : raw;
            if (!haveFirst) { _first = t; nextIndexT = t; haveFirst = true; }
            else if (t < prevT) ++_backSteps;
            prevT = t;
            _last = t;
            if (t >= nextIndexT) {
                _index.push_back({t, off});
                nextIndexT = t + kIndexStepUsec;
            }
        };

        while (true) {
            const int64_t recOffset = _f.tell();
            uint8_t stamp[kStampBytes];
            if (!_f.read(stamp, kStampBytes)) break;        // охайний кінець файлу

            uint8_t hdr[3];
            if (!_f.read(hdr, 3)) { _truncated = true; break; }
            const int flen = frameLength(hdr);
            if (flen < 0) {                                  // ланцюг зірвався
                const int64_t rec = resyncFrom(recOffset + 1);
                if (rec < 0) { _truncated = true; break; }
                ++_breaks;
                _f.seek(rec);
                continue;
            }
            if (!_f.skip(flen - 3)) { _truncated = true; break; }

            if (decided) {
                accept(beToU64(stamp), recOffset);
            } else {
                head.push_back({beToU64(stamp), recOffset});
                if (head.size() == kProbeRecords) {
                    _swapped = chooseSwapped(head);
                    decided  = true;
                    for (const RawStamp& h : head) accept(h.raw, h.off);
                }
            }
        }

        if (!decided) {                                      // файл коротший за пробу
            _swapped = chooseSwapped(head);
            for (const RawStamp& h : head) accept(h.raw, h.off);
        }
        return haveFirst;
    }

    FileBytes               _f;
    std::vector<IndexEntry> _index;
    uint64_t _first = 0, _last = 0, _pendingT = 0;
    bool     _hasPending = false, _swapped = false, _truncated = false;
    int      _backSteps = 0, _breaks = 0;
};

// ── видача ──────────────────────────────────────────────────────────────────
void emit(uint64_t /*tUsec*/, const std::vector<uint8_t>& frame) {
    std::fwrite(frame.data(), 1, frame.size(), stdout);   // кадр як є: далі — труба
}

void playback(TlogReader& log, double speed) {
    using Clock = std::chrono::steady_clock;

    uint64_t anchorLogUsec = 0;
    if (!log.pending(anchorLogUsec)) return;
    const Clock::time_point anchorTick = Clock::now();

    std::vector<uint8_t> frame;
    uint64_t t = 0;
    while (log.pending(t)) {
        const int64_t aheadUsec = static_cast<int64_t>(t) - static_cast<int64_t>(anchorLogUsec);
        const int64_t dueMs     = static_cast<int64_t>(aheadUsec / 1000.0 / speed);
        const auto    due       = anchorTick + std::chrono::milliseconds(dueMs);
        const int64_t waitMs    =
            std::chrono::duration_cast<std::chrono::milliseconds>(due - Clock::now()).count();

        if (waitMs >= kBatchWindowMs) {
            std::this_thread::sleep_for(std::chrono::milliseconds(waitMs));
            continue;
        }
        if (!log.next(t, frame)) break;
        emit(t, frame);
    }
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: tlogplay FILE [--seek PCT] [--speed X]\n");
        return 2;
    }
    double pct = 0.0, speed = 1.0;
    for (int i = 2; i + 1 < argc; i += 2) {
        if (!std::strcmp(argv[i], "--seek"))  pct   = std::atof(argv[i + 1]);
        if (!std::strcmp(argv[i], "--speed")) speed = std::atof(argv[i + 1]);
    }

    TlogReader log;
    if (!log.open(argv[1])) {
        std::fprintf(stderr, "не відкривається або порожній: %s\n", argv[1]);
        return 1;
    }

    const uint64_t dur = log.durationUsec();
    std::fprintf(stderr, "тривалість %.3f с · стрибків часу назад %d · розривів %d%s\n",
                 static_cast<double>(dur) / 1e6, log.backSteps(), log.breaks(),
                 log.truncated() ? " · хвіст обірваний" : "");

    if (pct > 0.0) {
        if (dur == 0) std::fprintf(stderr, "нульова тривалість: перемотувати нема куди\n");
        else log.seekToTime(log.firstUsec() + static_cast<uint64_t>(dur * (pct / 100.0)));
    }

    playback(log, speed);
    return 0;
}
