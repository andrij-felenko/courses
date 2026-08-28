struct Packet {
    uint64_t ext    = 0;   // розгорнутий номер
    uint32_t ts     = 0;   // мітка часу з заголовка
    bool     marker = false;
    std::vector<uint8_t> payload;
};

class Reorderer {
public:
    using OnPacket = std::function<void(const Packet&)>;
    using OnGap    = std::function<void(uint64_t from, uint64_t count)>;

    Reorderer(uint64_t depth, uint64_t hold_ns, OnPacket out, OnGap gap)
        : depth_(depth), hold_ns_(hold_ns), out_(std::move(out)), gap_(std::move(gap)) {}

    void reset(uint64_t first_ext) {
        for (size_t i = 0; i < N; ++i) { slot_[i].payload.clear(); full_[i] = false; }
        head_ = highest_ = first_ext;
        stalled_ = false;
    }

    void push(Packet&& p, uint64_t now_ns) {
        if (p.ext < head_) { ++late_; return; }        // місце цього пакета вже проїхало

        if (p.ext - head_ >= MAX_DROPOUT) {            // це вже не діра, а розрив потоку
            advance_to_(head_ + N);                    // випорожнюємо кільце по порядку
            gap_(head_, p.ext - head_);                // решту оголошуємо однією заявою
            lost_ += p.ext - head_;
            head_ = highest_ = p.ext;
            stalled_ = false;
        } else if (p.ext >= head_ + N) {               // вікно повне — звільняємо місце
            advance_to_(p.ext - N + 1);
        }

        const size_t i = idx(p.ext);
        if (full_[i]) { ++dup_; return; }              // той самий номер уже лежить — повтор
        if (p.ext > highest_) highest_ = p.ext;
        slot_[i] = std::move(p);
        full_[i] = true;

        drain(now_ns);
    }

    // кликати і за таймером теж: без нового пакета застигла голова сама не зрушить
    void drain(uint64_t now_ns) {
        for (;;) {
            const size_t i = idx(head_);
            if (full_[i]) {                            // голова на місці — віддаємо й ідемо далі
                out_(slot_[i]);
                release_(i);
                ++head_; stalled_ = false;
                continue;
            }
            if (highest_ < head_) break;               // попереду взагалі нічого — просто чекаємо потік

            if (!stalled_) { stalled_ = true; stall_since_ = now_ns; }
            const bool pressure = (highest_ - head_) >= depth_;          // поріг за глибиною
            const bool expired  = (now_ns - stall_since_) >= hold_ns_;   // поріг за часом
            if (!pressure && !expired) break;          // бюджет іще є — чекаємо

            gap_(head_, 1); ++lost_;                   // здаємось: цього пакета не буде
            ++head_; stalled_ = false;
        }
    }

    uint64_t late() const { return late_; }
    uint64_t dup()  const { return dup_;  }
    uint64_t lost() const { return lost_; }

private:
    static constexpr size_t   N           = 128;   // степінь двійки: модуль стає маскою
    static constexpr uint64_t MAX_DROPOUT = 3000;  // за RFC 3550 A.1: далі — це вже не діра

    static size_t idx(uint64_t ext) { return static_cast<size_t>(ext & (N - 1)); }
    void release_(size_t i) { slot_[i].payload.clear(); full_[i] = false; }

    // силоміць зрушити голову до target, нічого не загубивши мовчки
    void advance_to_(uint64_t target) {
        if (target <= head_) return;                   // важливо: інакше зб'ємо лічильник простою
        uint64_t miss = 0;
        while (head_ < target) {
            const size_t i = idx(head_);
            if (full_[i]) {
                if (miss) { gap_(head_ - miss, miss); lost_ += miss; miss = 0; }
                out_(slot_[i]); release_(i);
            } else {
                ++miss;                                // сусідні діри злипаються в одну заяву
            }
            ++head_;
        }
        if (miss) { gap_(head_ - miss, miss); lost_ += miss; }
        stalled_ = false;
    }

    std::array<Packet, N> slot_{};
    std::array<bool,   N> full_{};
    uint64_t head_ = 0, highest_ = 0, stall_since_ = 0;
    bool     stalled_ = false;
    uint64_t depth_, hold_ns_;
    OnPacket out_;
    OnGap    gap_;
    uint64_t late_ = 0, dup_ = 0, lost_ = 0;
};
