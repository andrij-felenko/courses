using Ms = uint64_t;                     // монотонний час у мілісекундах

constexpr Ms       kIdle     = 500;      // тиша, після якої вважаємо чергу обірваною
constexpr Ms       kIdleMax  = 3000;     // стеля очікування
constexpr uint32_t kRetryCap = 20;       // безплідних спроб поспіль до відмови
constexpr uint32_t kMerge    = 8;        // прийнятих кошиків, які дешевше перепросити

struct Transport {
    virtual ~Transport() = default;
    virtual void requestData(uint16_t id, uint32_t ofs, uint32_t count) = 0;
    virtual void requestEnd() = 0;
};

struct Stats {
    uint64_t written = 0, dup = 0, stale = 0, unaligned = 0, foreign = 0, malformed = 0;
    uint64_t requests = 0, repeats = 0;
};

class Downloader {
public:
    enum class State { Running, Done, Failed };

    Downloader(Transport& tx, LogFile& out, uint16_t id, uint64_t declared)
        : tx_(tx), out_(out), id_(id), size_(declared) {}

    State        state() const { return state_; }
    uint64_t     size()  const { return size_;  }
    const Stats& stats() const { return stat_;  }

    void start(Ms now) {
        now_ = lastData_ = now;
        window_ = 0;  bins_ = binsIn(0);  table_.clear();
        requestGap();
    }

    void onLogData(uint16_t id, uint32_t ofs, uint8_t count, const uint8_t* data, Ms now);
    void onTick(Ms now);

private:
    void requestGap();
    void shrinkTo(uint64_t realEnd);
    void finish(uint64_t realSize, State how) {
        state_ = how;
        tx_.requestEnd();                // звільняємо бортовий логер
        out_.finish(realSize);
    }
    uint32_t binsIn(uint64_t win) const {
        const uint64_t n = (size_ - win * kWindow + kChunk - 1) / kChunk;
        return uint32_t(n < kBins ? n : kBins);
    }
    uint64_t goodPrefix() const {        // скільки байтів з початку файлу справді суцільні
        const uint64_t p = window_ * kWindow + uint64_t(table_.firstZero(0, bins_)) * kChunk;
        return p < size_ ? p : size_;
    }

    Transport& tx_;
    LogFile&   out_;
    uint16_t   id_;
    uint64_t   size_;                    // оголошений, а далі — уточнений
    uint64_t   window_ = 0;
    uint32_t   bins_ = 0;
    Bits       table_;
    uint32_t   reqStart_ = 0, reqEnd_ = 0, pending_ = 0;
    uint32_t   retries_ = 0;
    Ms         now_ = 0, lastData_ = 0;
    State      state_ = State::Running;
    Stats      stat_;
};
