class CtrKeystream {
public:
    CtrKeystream(const Aes128& aes, const uint8_t* iv, size_t iv_size)
        : aes_(aes), pos_(16) {                 // pos_ == 16 → блок гами ще не породжено
        counter_.fill(0);
        std::memcpy(counter_.data(), iv, iv_size);   // 8 Б лягають у СТАРШІ вісім байтів
    }

    // Накладає гаму на n байтів. Стан живе МІЖ викликами — і номер блока, і позиція в ньому.
    void apply(uint8_t* data, size_t n) {
        for (size_t i = 0; i < n; ++i) {
            if (pos_ == 16) {
                aes_.encrypt_block(counter_.data(), pad_.data());
                bump();
                pos_ = 0;
            }
            data[i] ^= pad_[pos_++];
        }
    }

private:
    void bump() {                               // +1 до молодших восьми байтів
        for (int i = 15; i >= 8; --i)           // старший байт — лівіший, як усюди в ISO BMFF
            if (++counter_[i] != 0) break;      // далі йдемо лише тоді, коли байт перекотився через нуль
    }
    const Aes128& aes_;
    Block  counter_{}, pad_{};
    size_t pos_;
};

void decrypt_cenc(const Aes128& aes, const SampleEnc& s, uint8_t* sample, size_t size) {
    CtrKeystream ks(aes, s.iv.data(), s.iv.size());   // ОДИН на весь семпл

    if (s.subsamples.empty()) { ks.apply(sample, size); return; }

    size_t off = 0;
    for (const Subsample& ss : s.subsamples) {
        off += ss.clear_bytes;                  // чисті байти просто перестрибуємо
        ks.apply(sample + off, ss.enc_bytes);   // потік продовжується з того місця, де спинився
        off += ss.enc_bytes;
    }
}
