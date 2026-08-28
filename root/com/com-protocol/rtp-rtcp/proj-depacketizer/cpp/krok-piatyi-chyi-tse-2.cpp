class RtpReceiver {
public:
    explicit RtpReceiver(std::function<void(Frame&&)> sink)
        : asm_(std::move(sink)),
          ring_(/*depth*/ 32, /*hold*/ 40ull * 1000 * 1000,
                [this](const Packet& p)              { asm_.on_packet(p); },
                [this](uint64_t from, uint64_t count){ asm_.on_gap(from, count); }) {}

    void on_datagram(const uint8_t* buf, size_t n, uint64_t now_ns) {
        RtpHeader h;
        if (!parse_rtp(buf, n, h)) return;

        switch (guard_.check(h.ssrc, h.seq)) {
            case SsrcGuard::Foreign:  return;                    // не наш потік — мовчки геть
            case SsrcGuard::First:
            case SsrcGuard::Switched: ring_.reset(unwrap_.reset(h.seq)); break;
            case SsrcGuard::Same:     break;
        }

        Packet p;
        p.ext    = unwrap_.unwrap(h.seq);
        p.ts     = h.ts;
        p.marker = h.marker;
        p.payload.assign(h.payload, h.payload + h.payload_len);
        ring_.push(std::move(p), now_ns);
    }

    // ОБОВ'ЯЗКОВО кликати за таймером, інакше поріг часу ніколи не спрацює
    void tick(uint64_t now_ns) { ring_.drain(now_ns); }

private:
    SsrcGuard      guard_;
    SeqUnwrap      unwrap_;
    FrameAssembler asm_;
    Reorderer      ring_;
};
