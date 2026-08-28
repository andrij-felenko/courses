class SsrcGuard {
public:
    enum Verdict { First, Same, Foreign, Switched };

    Verdict check(uint32_t ssrc, uint16_t seq) {
        if (!have_)       { cur_ = ssrc; have_ = true; return First; }
        if (ssrc == cur_) { probation_ = 0; return Same; }

        // чужий SSRC беремо на випробування: одиничний пакет нічого не доводить
        if (ssrc != cand_ || static_cast<uint16_t>(cand_seq_ + 1) != seq) {
            cand_ = ssrc; cand_seq_ = seq; probation_ = MIN_SEQUENTIAL - 1;
            return Foreign;
        }
        cand_seq_ = seq;
        if (--probation_ > 0) return Foreign;

        cur_ = ssrc;         // два номери поспіль — джерело справді змінилося
        return Switched;
    }

private:
    static constexpr int MIN_SEQUENTIAL = 2;   // за RFC 3550 A.1
    uint32_t cur_ = 0, cand_ = 0;
    uint16_t cand_seq_ = 0;
    int      probation_ = 0;
    bool     have_ = false;
};
