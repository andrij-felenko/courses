class SeqUnwrap {
public:
    // опору ставимо на перший побачений номер; повертає його розгорнутим
    uint64_t reset(uint16_t first) { ref_ = BIAS + first; return ref_; }

    uint64_t unwrap(uint16_t seq) {
        const uint16_t ref16 = static_cast<uint16_t>(ref_);         // молодші 16 біт опори
        const uint16_t raw   = static_cast<uint16_t>(seq - ref16);  // різниця за модулем 2¹⁶
        // коротша ЗНАКОВА відстань: до 32767 — уперед, решта кола — назад
        const int32_t  d = (raw < 0x8000u) ? static_cast<int32_t>(raw)
                                           : static_cast<int32_t>(raw) - 0x10000;
        const uint64_t ext = static_cast<uint64_t>(static_cast<int64_t>(ref_) + d);
        if (ext > ref_) ref_ = ext;   // опора рухається ЛИШЕ вперед
        return ext;
    }
private:
    static constexpr uint64_t BIAS = 0x10000;  // запас, щоб ранній безлад не пішов у мінус
    uint64_t ref_ = 0;
};
