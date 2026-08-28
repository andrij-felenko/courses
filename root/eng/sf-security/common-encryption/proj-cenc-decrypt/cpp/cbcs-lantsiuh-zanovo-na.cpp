void decrypt_cbcs(const Aes128& aes, const SampleEnc& s,
                  const TrackEnc& t, uint8_t* sample, size_t size) {
    const std::vector<uint8_t>& iv = s.iv.empty() ? t.constant_iv : s.iv;
    const unsigned crypt = t.crypt_byte_block ? t.crypt_byte_block : 1u;
    const unsigned skip  = t.skip_byte_block;          // 9 для відео, 0 — суцільно

    auto range = [&](uint8_t* p, size_t n) {
        Block chain{};
        std::memcpy(chain.data(), iv.data(), iv.size());   // ланцюг — З НУЛЯ, від сталого IV
        const size_t blocks = n / 16;                  // неповний хвіст лишається чистим
        for (size_t i = 0; i < blocks; ) {
            const size_t take = std::min<size_t>(crypt, blocks - i);
            for (size_t k = 0; k < take; ++k, ++i) {
                uint8_t* b = p + i * 16;
                Block cipher;
                std::memcpy(cipher.data(), b, 16);     // запам'ятати ДО розшифрування
                aes.decrypt_block(b, b);
                for (int j = 0; j < 16; ++j) b[j] ^= chain[j];
                chain = cipher;                        // наступна ланка — попередній ШИФРОТЕКСТ
            }
            if (skip == 0) break;                      // візерунка немає — шифруємо все
            i += skip;                                 // пропущені блоки ланцюг не рвуть
        }
    };

    if (s.subsamples.empty()) { range(sample, size); return; }

    size_t off = 0;
    for (const Subsample& ss : s.subsamples) {
        off += ss.clear_bytes;
        range(sample + off, ss.enc_bytes);             // IV і візерунок — заново на КОЖНІЙ
        off += ss.enc_bytes;
    }
}
