void Downloader::onLogData(uint16_t id, uint32_t ofs, uint8_t count,
                           const uint8_t* data, Ms now)
{
    now_ = now;
    if (state_ != State::Running) return;
    if (id != id_)      { ++stat_.foreign;   return; }   // відповідь про інший запис
    if (ofs % kChunk)   { ++stat_.unaligned; return; }   // зсув не з нашої сітки
    if (count > kChunk) { ++stat_.malformed; return; }   // поле зіпсоване

    if (count == 0) {                                    // за цим зсувом уже нічого немає
        shrinkTo(ofs);
        requestGap();
        return;
    }
    if (count < kChunk) shrinkTo(uint64_t(ofs) + count); // короткий пакет буває лише в кінці

    const uint64_t win = uint64_t(ofs) / kWindow;
    if (win != window_) { ++stat_.stale; return; }       // чуже вікно
    const uint32_t bin = uint32_t((uint64_t(ofs) - window_ * kWindow) / kChunk);
    if (bin >= bins_)   { ++stat_.stale; return; }       // за кінцем цього вікна

    lastData_ = now_;                                    // черга йде — навіть якщо це дублікат
    if (table_.test(bin)) { ++stat_.dup; return; }
    if (!out_.writeAt(ofs, data, count)) { finish(goodPrefix(), State::Failed); return; }

    table_.set(bin);
    ++stat_.written;
    retries_ = 0;                                        // поступ є
    if (bin >= reqStart_ && bin < reqEnd_ && --pending_ == 0)
        requestGap();                                    // прогін добито
}
