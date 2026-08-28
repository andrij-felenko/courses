struct Frame { uint8_t seq, sys, comp, msg, len; uint8_t payload[255]; };

struct Parser {                       // ОДИН такий на кожне джерело байтів
    enum Stage { WaitStx, Len, Seq, Sys, Comp, Msg, Payload, CrcLo, CrcHi };
    Stage    stage = WaitStx;
    Frame    f{};
    uint8_t  idx = 0;
    uint16_t crc = 0, crc_rx = 0;
    uint32_t good = 0, bad = 0;       // лічильники для демонстрації
};

bool feed(Parser &p, uint8_t b, Frame &out) {
    switch (p.stage) {
    case Parser::WaitStx:
        if (b == STX) { p.crc = 0xFFFF; p.stage = Parser::Len; }
        return false;
    case Parser::Len:  p.f.len  = b; crc_step(b, p.crc); p.idx = 0; p.stage = Parser::Seq;  return false;
    case Parser::Seq:  p.f.seq  = b; crc_step(b, p.crc); p.stage = Parser::Sys;  return false;
    case Parser::Sys:  p.f.sys  = b; crc_step(b, p.crc); p.stage = Parser::Comp; return false;
    case Parser::Comp: p.f.comp = b; crc_step(b, p.crc); p.stage = Parser::Msg;  return false;
    case Parser::Msg:  p.f.msg  = b; crc_step(b, p.crc);
                       p.stage = p.f.len ? Parser::Payload : Parser::CrcLo;      return false;
    case Parser::Payload:
        p.f.payload[p.idx++] = b; crc_step(b, p.crc);
        if (p.idx == p.f.len) p.stage = Parser::CrcLo;
        return false;
    case Parser::CrcLo:
        p.crc_rx = b; p.stage = Parser::CrcHi;
        return false;
    case Parser::CrcHi:
        p.crc_rx = static_cast<uint16_t>(p.crc_rx | (b << 8));
        p.stage  = Parser::WaitStx;
        if (p.crc_rx == p.crc) { out = p.f; ++p.good; return true; }
        ++p.bad;                       // сума не зійшлася — кадру не було
        return false;
    }
    return false;
}
