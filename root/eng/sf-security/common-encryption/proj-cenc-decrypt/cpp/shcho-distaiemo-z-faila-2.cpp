struct Reader {
    const uint8_t* p;
    uint8_t  u8()  { return *p++; }
    uint16_t u16() { uint16_t v = uint16_t(p[0] << 8 | p[1]); p += 2; return v; }
    uint32_t u32() { uint32_t v = uint32_t(p[0]) << 24 | uint32_t(p[1]) << 16
                                | uint32_t(p[2]) << 8  | p[3];  p += 4; return v; }
    void skip(size_t n) { p += n; }
};

// tenc — типові параметри доріжки: moov → … → stsd → encv → sinf → schi → tenc
TrackEnc parse_tenc(Reader r) {
    TrackEnc t;
    const uint32_t vf = r.u32();               // FullBox: 1 Б версія + 3 Б прапорці
    r.u8();                                    // reserved
    if ((vf >> 24) == 0) {
        r.u8();                                // версія 0 — ще один reserved
    } else {
        const uint8_t b = r.u8();              // версія 1 — візерунок у двох півбайтах
        t.crypt_byte_block = b >> 4;           // скільки блоків шифрувати
        t.skip_byte_block  = b & 0x0F;         // скільки лишити чистими
    }
    t.is_protected       = r.u8();
    t.per_sample_iv_size = r.u8();             // 0, 8 або 16 — БЕЗ цього senc не розібрати
    for (uint8_t& b : t.kid) b = r.u8();       // номер ключа, а не сам ключ
    if (t.is_protected && t.per_sample_iv_size == 0) {
        const uint8_t n = r.u8();              // саме випадок cbcs
        t.constant_iv.assign(r.p, r.p + n);
        r.skip(n);
    }
    return t;
}

// senc — на кожен семпл: початкове значення й пари «чисто / захищено»
std::vector<SampleEnc> parse_senc(Reader r, const TrackEnc& t) {
    const uint32_t vf = r.u32();
    const bool has_subsamples = (vf & 0x000002) != 0;   // прапорець, не версія
    const uint32_t count = r.u32();

    std::vector<SampleEnc> out(count);
    for (SampleEnc& s : out) {
        s.iv.assign(r.p, r.p + t.per_sample_iv_size);
        r.skip(t.per_sample_iv_size);
        if (!has_subsamples) continue;                  // захищений увесь семпл
        const uint16_t m = r.u16();
        s.subsamples.resize(m);
        for (Subsample& ss : s.subsamples) {
            ss.clear_bytes = r.u16();                   // 16 бітів
            ss.enc_bytes   = r.u32();                   // а тут уже 32
        }
    }
    return out;
}
